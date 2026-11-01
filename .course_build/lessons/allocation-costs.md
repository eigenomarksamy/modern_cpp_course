---
title: the cost of allocation
standard: C++17
objective: find hidden heap allocations, count them in tests, and move them out of hot paths into an allocation-free steady state
prerequisites: benchmarking, cache-locality, callbacks
difficulty: 2
---

### the idea

a 1 kHz joint controller meets its deadline in every lab test, then misses one every few minutes in the field. the profiler shows nothing hot. the culprit is a `std::string` built for a log line and a `std::vector` that grows inside the loop: allocation calls whose cost is usually small but occasionally very large. in real-time code the average does not matter; the worst case does, and the general-purpose heap has no useful worst-case bound.

### understanding the concept

`operator new` (and `malloc` beneath it) is a general-purpose allocator. on each call it may:

- find a free block of the right size class and update its bookkeeping (the cheap, common path, often served from a per-thread cache in modern allocators such as glibc's tcache, jemalloc, tcmalloc, or mimalloc);
- take a lock or touch shared structures when the thread cache is empty or memory was freed by another thread;
- ask the operating system for more memory (`brk`, `mmap`, `VirtualAlloc`), which is a system call, and the fresh pages are then page-faulted in on first touch.

so the cost distribution has a cheap mode and a long tail you cannot bound. allocation also scatters data (each node or object lands wherever a block was free, which is [[cache-locality]]'s locality problem), and long-running processes fragment the heap.

the expensive part is that allocations hide. each of these allocates, or may:

| code | allocation |
|---|---|
| `std::string` longer than the small-string buffer | one per string (buffer size is implementation-defined: 15 chars in libstdc++ and MSVC, 22 in libc++, on 64-bit targets) |
| string concatenation `a + b + c` | possibly one per intermediate |
| `std::function` holding a large capture | one, beyond a small internal buffer (size implementation-specific) |
| `std::make_shared<T>()` | one (object and control block together); `shared_ptr<T>(new T)` makes two ([[shared-ptr]]) |
| `std::map`, `std::set`, `std::list`, `std::unordered_map` | one per node |
| `push_back` without `reserve` | about log2(n) reallocations with geometric growth |
| `throw` | the runtime allocates the exception object |

the remedies, roughly in order of how often you reach for them: `reserve` and reuse; avoiding node containers in hot paths; scoped arenas and pools ([[pmr-pools]]); and the strongest pattern of all for real-time code, an allocation-free steady state: allocate everything at startup, then never again.

### in code

first, measure. replacing the global allocation functions is a standard, supported mechanism. put the replacement in its own file and link it only into test binaries:

```cpp complete
// alloc_counter.cpp: link into test binaries only
#include <atomic>
#include <cstddef>
#include <cstdlib>
#include <new>

std::atomic<std::size_t> g_allocs{0};

void* operator new(std::size_t n) {                  // replaces the global allocation function
    g_allocs.fetch_add(1, std::memory_order_relaxed);
    if (void* p = std::malloc(n ? n : 1)) return p;
    throw std::bad_alloc{};
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

// elsewhere:
template <typename F>
std::size_t count_allocs(F&& f) {
    const std::size_t before = g_allocs.load();
    f();
    return g_allocs.load() - before;
}
```

the array forms forward to these by default. with GCC 12 and libstdc++ on x86-64, `count_allocs` reported: a 6-character string 0, a 22-character string 1, a `std::function` capturing a `std::array<double, 8>` 1, `make_shared<int>` 1, 100 `std::map` inserts 100, and 1,000 `push_back` calls without `reserve` 11. these are implementation details, which is exactly why you count rather than guess. a complete counter also replaces the C++17 `std::align_val_t` overloads; libstdc++'s default `pmr` resource, for one, allocates through them.

the real-time pattern: preallocate, then reuse.

```cpp
class LocalPlanner {
public:
    explicit LocalPlanner(std::size_t max_obstacles) {
        nearby_.reserve(max_obstacles);           // pay once, at startup
    }
    std::size_t cycle(const std::vector<Obstacle>& scan) {
        nearby_.clear();                          // destroys elements, keeps capacity
        for (const Obstacle& o : scan)
            if (o.x * o.x + o.y * o.y < 25.0f) nearby_.push_back(o);
        return nearby_.size();
    }
private:
    std::vector<Obstacle> nearby_;                // reused every cycle
};

void test_planner_steady_state_is_allocation_free() {
    std::vector<Obstacle> scan(256, Obstacle{1.0f, 1.0f, 0.5f});
    LocalPlanner planner(512);
    planner.cycle(scan);                          // warm-up
    const std::size_t before = g_allocs.load();
    for (int i = 0; i < 1000; ++i) planner.cycle(scan);
    assert(g_allocs.load() == before);            // the steady state never touches the heap
}
```

the test turns a performance property into a regression test: if someone adds a `std::string` to `cycle` next year, CI fails instead of the robot.

### in practice

a radar tracker processed each frame with a `std::map<TrackId, Track>` and built a fresh `std::vector` of candidate associations per track. a heap profiler (heaptrack on Linux, or Valgrind's massif) showed hundreds of thousands of allocations per second, and the tail of the frame time tracked them.

the fix came in layers, each verified with the counter and [[benchmarking]]'s harness: tracks moved into a `std::vector` sorted by id ([[associative-containers]]), candidate lists became members cleared each frame, and per-frame temporaries moved to a `monotonic_buffer_resource` reset at frame boundaries. the steady state dropped to zero allocations, and the remaining frame-time variation came from the work itself.

### watch out for

**measurement traps.**

two measurement traps. the standard allows a new-expression to omit or merge its call to a replaceable allocation function, so an optimized build may count fewer allocations than the source suggests. and on Windows, a replacement in the executable does not intercept allocations made inside a DLL that has its own `operator new`: with MinGW's shared libstdc++, string allocations inside the library went uncounted until the program was linked with `-static`. exceptions are separate again: the common Itanium ABI runtimes allocate the exception object with `malloc`, so an `operator new` counter never sees it.

### the takeaway

count allocations instead of guessing, move them out of hot loops and into startup, and when a steady state must be allocation-free, write a test that says so.

### optional challenge

`LocalPlanner::cycle` calls `nearby_.clear()`. what happens to the allocation-free steady state if it instead calls `nearby_ = std::vector<Obstacle>{};` or `nearby_.clear(); nearby_.shrink_to_fit();`?

<details>
<summary>answer</summary>

both break it. `clear()` destroys the elements but keeps the capacity, so later `push_back` calls reuse the buffer. move-assigning an empty vector takes over the temporary's (empty) buffer and frees the old one, so the next cycle reallocates, about log2(n) times as it grows again. `shrink_to_fit()` is a non-binding request to drop unused capacity, and mainstream implementations honor it by reallocating, with the same result. the allocation test from this lesson would catch either change on the first CI run.

</details>
