<a id="day-52"></a>

## day 52: the cost of allocation

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 12, 15, 17, 50

### the idea

A 1 kHz joint controller meets its deadline in every lab test, then misses one every few minutes in the field. The profiler shows nothing hot. The culprit is a `std::string` built for a log line and a `std::vector` that grows inside the loop: allocation calls whose cost is usually small but occasionally very large. In real-time code the average does not matter; the worst case does, and the general-purpose heap has no useful worst-case bound.

### understanding the concept

`operator new` (and `malloc` beneath it) is a general-purpose allocator. On each call it may:

- find a free block of the right size class and update its bookkeeping (the cheap, common path, often served from a per-thread cache in modern allocators such as glibc's tcache, jemalloc, tcmalloc, or mimalloc);
- take a lock or touch shared structures when the thread cache is empty or memory was freed by another thread;
- ask the operating system for more memory (`brk`, `mmap`, `VirtualAlloc`), which is a system call, and the fresh pages are then page-faulted in on first touch.

So the cost distribution has a cheap mode and a long tail you cannot bound. Allocation also scatters data (each node or object lands wherever a block was free, which is day 51's locality problem), and long-running processes fragment the heap.

The expensive part is that allocations hide. Each of these allocates, or may:

| code | allocation |
|---|---|
| `std::string` longer than the small-string buffer | one per string (buffer size is implementation-defined: 15 chars in libstdc++ and MSVC, 22 in libc++, on 64-bit targets) |
| string concatenation `a + b + c` | possibly one per intermediate |
| `std::function` holding a large capture | one, beyond a small internal buffer (size implementation-specific) |
| `std::make_shared<T>()` | one (object and control block together); `shared_ptr<T>(new T)` makes two (day 12) |
| `std::map`, `std::set`, `std::list`, `std::unordered_map` | one per node |
| `push_back` without `reserve` | about log2(n) reallocations with geometric growth |
| `throw` | the runtime allocates the exception object |

The tools, roughly in order of how often you reach for them: `reserve` and reuse; avoiding node containers in hot paths; `std::pmr` resources for scoped, fast allocation; object pools for fixed-size objects; and the strongest pattern of all for real-time code, an allocation-free steady state: allocate everything at startup, then never again.

### in code

First, measure. Replacing the global allocation functions is a standard, supported mechanism. Put the replacement in its own file and link it only into test binaries:

```cpp
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

The array forms forward to these by default. With GCC 12 and libstdc++ on x86-64, `count_allocs` reported: a 6-character string 0, a 22-character string 1, a `std::function` capturing a `std::array<double, 8>` 1, `make_shared<int>` 1, 100 `std::map` inserts 100, and 1,000 `push_back` calls without `reserve` 11. These are implementation details, which is exactly why you count rather than guess. A complete counter also replaces the C++17 `std::align_val_t` overloads; libstdc++'s default `pmr` resource, for one, allocates through them.

Second, `std::pmr` (C++17). A `memory_resource` is a runtime-polymorphic allocator, and the `std::pmr::` containers hold a pointer to one. `monotonic_buffer_resource` is a bump allocator: allocation advances a pointer, deallocation is a no-op, and everything is released at once when the resource dies.

```cpp
#include <array>
#include <cstddef>
#include <memory_resource>
#include <vector>

struct Detection { float range_m, azimuth_rad, snr_db; };

std::size_t process_frame(const std::vector<Detection>& raw) {
    alignas(std::max_align_t) std::array<std::byte, 16 * 1024> buffer;   // scratch on the stack
    std::pmr::monotonic_buffer_resource arena(buffer.data(), buffer.size(),
                                              std::pmr::null_memory_resource());
    std::pmr::vector<Detection> gated(&arena);
    gated.reserve(raw.size());                   // a pointer bump, no heap
    for (const Detection& d : raw)
        if (d.snr_db > 10.0f) gated.push_back(d);
    return gated.size();
}                                                // everything released at once
```

The `null_memory_resource()` upstream is a deliberate choice: if a frame ever needs more than 16 KiB, allocation throws `std::bad_alloc` instead of silently falling back to the heap. In a test, that is a loud failure you want; in production you might prefer the default upstream plus a metric. Note `reserve`: with a monotonic resource, a growing vector leaves every outgrown buffer behind as dead space until the arena is released.

Third, the real-time pattern: preallocate, then reuse.

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

The test turns a performance property into a regression test: if someone adds a `std::string` to `cycle` next year, CI fails instead of the robot.

### in practice

A radar tracker processed each frame with a `std::map<TrackId, Track>` and built a fresh `std::vector` of candidate associations per track. A heap profiler (heaptrack on Linux, or Valgrind's massif) showed hundreds of thousands of allocations per second, and the tail of the frame time tracked them.

The fix came in layers, each verified with the counter and day 50's harness: tracks moved into a `std::vector` sorted by id (day 15), candidate lists became members cleared each frame, and per-frame temporaries moved to a `monotonic_buffer_resource` reset at frame boundaries. The steady state dropped to zero allocations, and the remaining frame-time variation came from the work itself.

Object pools fill the remaining gap: when objects of one type are created and destroyed at runtime (tracks born and dying), a fixed-capacity pool with a free list gives O(1) allocation with no system calls. `std::pmr::unsynchronized_pool_resource` is a general-purpose version for single-threaded use; `synchronized_pool_resource` adds locking.

### watch out for

`pmr` propagation surprises people. A pmr container does not propagate its resource on copy: `std::pmr::vector<int> copy = a;` gets the default resource (normally the heap), not `a`'s arena. Moving keeps the resource, but move-assigning between containers with different resources copies element by element. Uses-allocator construction passes the resource down only to elements that accept one: `pmr::vector<pmr::string>` puts the strings in the arena, `pmr::vector<std::string>` does not. And the resource must outlive every container using it; a container whose arena has been destroyed holds dangling memory, and touching it is undefined behavior.

Two measurement traps. The standard allows a new-expression to omit or merge its call to a replaceable allocation function, so an optimized build may count fewer allocations than the source suggests. And on Windows, a replacement in the executable does not intercept allocations made inside a DLL that has its own `operator new`: with MinGW's shared libstdc++, string allocations inside the library went uncounted until the program was linked with `-static`. Exceptions are separate again: the common Itanium ABI runtimes allocate the exception object with `malloc`, so an `operator new` counter never sees it.

### the takeaway

Count allocations instead of guessing, move them out of hot loops and into startup, and when a steady state must be allocation-free, write a test that says so.

### optional challenge

`std::pmr::vector<std::pmr::string> names(&arena); names.push_back("front_left_radar_long_name");` How many allocations come from the arena, and what changes if the element type is `std::string`?

<details>
<summary>answer</summary>

With `pmr::string` elements, uses-allocator construction gives the new string the vector's resource, so both the vector's buffer and the string's heap buffer (the name is longer than the small-string buffer) come from the arena. One subtlety: `push_back` first constructs a temporary `pmr::string` from the literal using the default resource, then moves it into the vector; because the resources differ, the move copies into arena memory, so the temporary's allocation hits the heap. `emplace_back("...")` constructs in place with the arena and avoids that. With `std::string` elements, only the vector's buffer is in the arena; every long string allocates from the global heap, defeating the point of the arena.

</details>
