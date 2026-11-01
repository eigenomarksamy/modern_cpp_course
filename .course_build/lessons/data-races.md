---
title: data races and race conditions
standard: C++17
objective: define a data race precisely, explain why it is undefined behavior rather than an imprecise result, and tell it apart from a race condition
prerequisites: threads, undefined-behavior
difficulty: 3
---

### the idea

two radar worker threads each count processed frames into a shared `long`, a million frames each. on one machine with GCC 12, an `-O0` build printed totals between 1.0 and 1.5 million, different on every run. the `-O2` build printed exactly 2,000,000 every time. a colleague concludes the release build is fine and the debug build is "just losing a few counts." both conclusions are wrong. the program has a data race, and a data race is undefined behavior, not an imprecise number. the release build only looks right because the optimizer, assuming no race, collapsed each thread's loop into a single addition.

### understanding the concept

the standard's definition is precise, and worth knowing word for word in spirit:

- two expression evaluations **conflict** if they access the same memory location and at least one of them modifies it. (a memory location is a scalar object or a run of adjacent non-zero-width bit-fields; two different `char` members are different locations, which is why threads may safely write neighbouring struct members.)
- a program has a **data race** if it contains two potentially concurrent conflicting actions, at least one of which is not atomic, and neither happens before the other.
- any data race is **UB** ([[undefined-behavior]]).

why UB rather than "some interleaving of the two"? because the compiler is allowed to optimize single-threaded code as if no other thread could be watching. it may keep a variable in a register for a whole loop, merge or split stores, or hoist a load out of a loop entirely, which turns `while (!done) {}` into an infinite loop. on some targets a 64-bit store is two instructions, and a reader can see half of each value. `++count` is a read-modify-write: three steps, and even when it compiles to a single x86 instruction, it is not atomic without a `lock` prefix.

a **race condition** is different: a bug where the result depends on timing. you can have one with no data race at all, when every access is properly locked but the *sequence* of operations is not. locking each step separately does not make the sequence atomic.

### in code

the counter, broken and fixed:

```cpp ub
#include <mutex>
#include <thread>

long frames = 0;
void count_frames_racy() {
    for (int i = 0; i < 1'000'000; ++i) ++frames;   // BUG: data race, UB
}

std::mutex frames_mutex;
long frames_safe = 0;
void count_frames() {
    for (int i = 0; i < 1'000'000; ++i) {
        std::lock_guard lock(frames_mutex);          // CTAD: lock_guard<std::mutex>
        ++frames_safe;
    }
}

int main() {
    std::thread a(count_frames), b(count_frames);
    a.join();
    b.join();
    // frames_safe == 2'000'000, guaranteed
}
```

locking per increment is correct but makes the threads take turns on every iteration. better designs avoid sharing: count locally and add once at the end, or use an atomic counter ([[atomics]]). correct first, then reduce sharing.

### in practice

races hide from ordinary testing: they depend on timing, compiler, and hardware, and the code usually works. ThreadSanitizer finds them by instrumenting every memory access and tracking happens-before relationships at run time:

```sh
g++ -std=c++17 -O1 -g -fsanitize=thread tests.cpp -o tests_tsan && ./tests_tsan
# WARNING: ThreadSanitizer: data race ... Write of size 8 ... Previous write of size 8 ...
```

it reports the two conflicting accesses with stack traces, even when the run happened to produce the right answer. it needs its own build (it cannot be combined with AddressSanitizer), slows the program down considerably, and only sees the interleavings your tests actually execute. a CI job that runs the concurrent tests under TSan is the cheapest insurance against this whole class of bug.

### watch out for

**no data race, and still wrong.**

now a race condition with no data race. every method locks, and the code is still wrong:

```cpp ub
#include <map>
#include <mutex>

struct Track { double range_m; double velocity_mps; };

class TrackTable {
public:
    bool contains(int id) const {
        std::lock_guard lock(m_);
        return tracks_.count(id) != 0;
    }
    void insert(int id, Track t) {
        std::lock_guard lock(m_);
        tracks_[id] = t;
    }
    // Fix: make the operation callers need a single critical section.
    bool insert_if_absent(int id, Track t) {
        std::lock_guard lock(m_);
        return tracks_.try_emplace(id, t).second;
    }
private:
    mutable std::mutex m_;              // mutable: const readers must lock too
    std::map<int, Track> tracks_;
};

// BUG (race condition, not UB): another thread may insert between the two calls
// if (!table.contains(id)) table.insert(id, initial_track);
```

the lesson is about API design: the critical section is part of the interface. a thread-safe class must offer the *transactions* its callers need, not just thread-safe getters and setters.

### the takeaway

a data race is undefined behavior, not an imprecise result, and the optimizer is entitled to assume you never wrote one; race conditions are a separate, higher-level bug that locking each step does not fix.

### optional challenge

which of these are data races (assume no other synchronization)?

1. two threads write two different `char` members of the same struct object.
2. two threads read the same `int`.
3. one thread sets `bool done = true;` while another loops on `while (!done) {}`.
4. two threads call `++` on the same `std::atomic<int>`.
5. two threads write two adjacent bit-fields, `unsigned a : 4;` and `unsigned b : 4;`, of the same struct.

<details>
<summary>answer</summary>

3 and 5. distinct `char` members are distinct memory locations (1), and concurrent reads never conflict (2). (3) is the classic: a non-atomic write and read with no happens-before, so the compiler may hoist the load out of the loop and spin forever. atomic operations never race with each other (4). adjacent non-zero-width bit-fields form *one* memory location (5), so writing different fields is a conflicting access; a zero-width bit-field (`unsigned : 0;`) between them would separate the locations.

</details>
