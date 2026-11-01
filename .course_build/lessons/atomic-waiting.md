---
title: atomic waits, false sharing, and lock-freedom
standard: C++20
objective: block on an atomic value with C++20 wait and notify, avoid false sharing between hot atomics, and check whether an atomic is really lock-free
prerequisites: memory-model
difficulty: 2
---

### the idea

a consumer that spins on an atomic flag burns a core while it waits. two workers that each update their own counter, with no shared data at all, still slow each other down. and an `std::atomic` of a struct may quietly contain a lock. atomics are a low-level tool, and using them well means knowing how they interact with the operating system's scheduler and the CPU's caches, not just with the memory model.

### understanding the concept

not every atomic is lock-free. `std::atomic<T>::is_always_lock_free` (C++17, `constexpr`) and `is_lock_free()` tell you; a large `T` may be implemented with a hidden lock. the standard guarantees lock-freedom only for `std::atomic_flag` (and, in C++20, the `std::atomic_signed_lock_free` and `std::atomic_unsigned_lock_free` aliases). C++20 adds `wait`/`notify_one`/`notify_all` on atomics (block until the value changes, without a condition variable) and `std::atomic_ref<T>`, which applies atomic operations to an ordinary object; while any `atomic_ref` to an object exists, every access to it must go through an `atomic_ref`.

### in code

third, C++20 replaces the spin with a blocking wait, and keeps hot atomics on separate cache lines:

```cpp complete
#include <atomic>
#include <cstdint>

std::atomic<std::uint32_t> generation{0};

void publish_next() {                    // producer, after writing the new frame
    generation.fetch_add(1, std::memory_order_release);
    generation.notify_all();
}

void await_next(std::uint32_t& seen) {   // consumer
    generation.wait(seen, std::memory_order_acquire);   // blocks while value == seen
    seen = generation.load(std::memory_order_acquire);
}

struct alignas(64) WorkerStats {         // 64: a common cache-line size, not a guarantee
    std::atomic<std::uint64_t> processed{0};
};
WorkerStats stats[8];                    // one per worker: no false sharing between them
```

`wait(old)` returns only after observing a value different from `old`; it may wake spuriously internally, but it re-checks for you. it compares values, so if the counter changed and changed back before the waiter looked, the waiter keeps sleeping (the ABA problem), which is why a monotonically increasing generation counter is used rather than a toggling flag. note that this only signals. if the producer rewrites a single shared frame buffer while a consumer is still reading the previous frame, that is a data race again; pair the signal with double buffering or hand frames over through a queue ([[blocking-queue]]).

### in practice

the `alignas(64)` matters when several threads each update their own counter at high rates. if two such counters share a cache line, every write by one core invalidates the line in the other core's cache, and two logically independent threads end up contending: *false sharing*. C++17 added `std::hardware_destructive_interference_size` in `<new>` for this, but support varies: GCC provides it from version 12 (64 on x86-64 here) and warns (`-Winterference-size`) when it is used in a header, because the value can change with tuning flags and so becomes an ABI hazard. check `__cpp_lib_hardware_interference_size`, or use a named constant you control. [[cache-locality]] shows how to measure the effect with hardware counters.

### watch out for

**an atomic is not necessarily lock-free.**

```cpp complete
#include <atomic>

struct Pose { double x, y, z, qw, qx, qy, qz; };   // 56 bytes
std::atomic<Pose> latest_pose;                      // compiles; very likely uses a lock

static_assert(std::atomic<int>::is_always_lock_free);   // true on mainstream platforms
// static_assert(std::atomic<Pose>::is_always_lock_free);   // fails on typical 64-bit targets
```

`std::atomic<T>` works for any trivially copyable `T`, and for types too large for the hardware's atomic instructions the library falls back to a lock (libstdc++ uses a small table of mutexes and needs `-latomic` for some sizes). that is correct, but it defeats the usual reason for choosing an atomic in a real-time thread. assert `is_always_lock_free` where it matters, and for large data publish a pointer or use double buffering instead.

### the takeaway

use C++20 `wait`/`notify` instead of spinning, keep atomics that different threads update on separate cache lines, and assert lock-freedom wherever you rely on it.

### optional challenge

why does `await_next` wait on a generation counter that only ever increases, instead of a `bool` that the producer sets to `true` and the consumer resets to `false`?

<details>
<summary>answer</summary>

`wait(old)` compares values: it sleeps while the atomic still equals `old`. with a toggling flag, two quick publications can change the value and change it back before the waiter looks, so the waiter sees "unchanged" and keeps sleeping through two frames (the ABA problem). a monotonically increasing counter never returns to a previous value in practice, so any publication is visible as a change, and the consumer can also tell how many frames it missed.

</details>
