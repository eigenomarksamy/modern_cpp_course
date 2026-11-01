<a id="day-40"></a>

## day 40: atomics and the memory model

**reading time:** about 10 minutes · **standard:** C++20 · **builds on:** days 06, 36, 37

### the idea

A radar thread fills a frame buffer and then sets `bool ready = true;`. A processing thread spins on `ready`, then reads the frame. On your x86 workstation it seems to work. It is still UB: `ready` is accessed concurrently and is not atomic, so it is a data race (day 37); the optimizer may hoist the load out of the spin loop; and even with a correct flag, the question remains whether the *frame data* written before the flag is guaranteed to be visible after it. Answering that precisely is what the memory model is for.

### understanding the concept

`std::atomic<T>` (for trivially copyable `T`) makes each operation on the object indivisible, and concurrent atomic operations on the same object are never a data race. Every atomic object also has a single *modification order* that all threads agree on. What atomicity alone does not give you is any promise about *other* memory. Compilers reorder independent loads and stores, and so do CPUs (store buffers, out-of-order execution). The memory model defines which reorderings other threads may observe, using three relations:

- **sequenced-before**: program order within one thread.
- **synchronizes-with**: a *release* store to an atomic synchronizes with an *acquire* load of the same atomic that reads the value written by that store (or by a later read-modify-write in its release sequence).
- **happens-before**: built from the two above, transitively. If a write happens before a read of the same location, with no other write in between, the read sees that write. If two conflicting accesses, one non-atomic, are not ordered by happens-before, you have a data race.

Mutex unlock/lock, thread start and `join`, and future readiness, which you have used all week, are all defined in terms of this relation. Atomics let you build the edges yourself, choosing a `std::memory_order` per operation:

| order | what it guarantees | typical use |
|---|---|---|
| `seq_cst` (default) | acquire/release, plus one total order of all `seq_cst` operations that every thread agrees on | the default; anything you have not proven needs less |
| `release` (stores) / `acquire` (loads) / `acq_rel` (read-modify-writes) | the synchronizes-with edge: writes before the release are visible after the acquire that reads it | publishing data through a flag or pointer |
| `relaxed` | atomicity and the per-object modification order, nothing else | counters and statistics that publish nothing |
| `consume` | intended as a cheaper acquire for dependent loads | do not use: its specification is under revision, and compilers implement it as `acquire` |

Read-modify-write operations (`exchange`, `fetch_add`, `compare_exchange_weak/strong`) are atomic as a whole. `compare_exchange` writes the new value only if the current value equals `expected` (compared byte for byte like `memcmp`, not with `operator==`, which matters for `float` and padding); on failure it loads the current value into `expected`. The `weak` form may fail spuriously (even when the values are equal), which is fine in a loop and can be cheaper on LL/SC architectures such as ARM.

Not every atomic is lock-free. `std::atomic<T>::is_always_lock_free` (C++17, `constexpr`) and `is_lock_free()` tell you; a large `T` may be implemented with a hidden lock. The standard guarantees lock-freedom only for `std::atomic_flag` (and, in C++20, the `std::atomic_signed_lock_free` and `std::atomic_unsigned_lock_free` aliases). C++20 adds `wait`/`notify_one`/`notify_all` on atomics (block until the value changes, without a condition variable) and `std::atomic_ref<T>`, which applies atomic operations to an ordinary object; while any `atomic_ref` to an object exists, every access to it must go through an `atomic_ref`.

### in code

Message passing, the pattern behind almost every correct use of acquire/release:

```cpp
#include <array>
#include <atomic>
#include <cassert>
#include <cstdint>

struct Frame { std::array<float, 1024> samples; std::uint64_t seq; };

Frame frame;                          // plain, non-atomic data
std::atomic<bool> ready{false};

void producer() {
    frame.samples.fill(1.0f);
    frame.seq = 42;
    ready.store(true, std::memory_order_release);        // (1) publish
}

void consumer() {
    while (!ready.load(std::memory_order_acquire)) {}    // (2) spin until published
    assert(frame.seq == 42);                             // guaranteed, no data race
}
```

```text
producer                                consumer
frame.samples = ...   | sequenced
frame.seq = 42        | before
ready.store(release) ---synchronizes-with--> ready.load(acquire) reads true
                                             | sequenced before
                                             frame.seq == 42 (happens after the write)
```

Weaken either side to `relaxed` and the edge disappears: the reads of `frame` then race with the writes, which is UB, even though `ready` itself is still race-free. Using a plain `bool` makes `ready` itself a data race. Note the asymmetry: the order protects the *non-atomic* data around the atomic.

Relaxed operations and a compare-and-swap loop, for statistics that publish nothing:

```cpp
#include <atomic>
#include <cstdint>

std::atomic<std::uint64_t> frames_dropped{0};
std::atomic<float> peak_power{0.0f};

void on_drop() {
    frames_dropped.fetch_add(1, std::memory_order_relaxed);   // only the count matters
}

void record_power(float p) {
    float cur = peak_power.load(std::memory_order_relaxed);
    while (cur < p &&
           !peak_power.compare_exchange_weak(cur, p, std::memory_order_relaxed)) {
        // failed: cur now holds the latest value; the loop re-checks cur < p
    }
}
```

There is no `fetch_max` in C++20, so the CAS loop is the standard way to build any read-modify-write the library lacks. Relaxed is correct here because nobody reads other data based on these values; a monitoring thread that loads them sees *some* value from each modification order, and after `join` the final values are exact.

Third, C++20 replaces the spin with a blocking wait, and keeps hot atomics on separate cache lines:

```cpp
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

`wait(old)` returns only after observing a value different from `old`; it may wake spuriously internally, but it re-checks for you. It compares values, so if the counter changed and changed back before the waiter looked, the waiter keeps sleeping (the ABA problem), which is why a monotonically increasing generation counter is used rather than a toggling flag. Note that this only signals. If the producer rewrites a single shared frame buffer while a consumer is still reading the previous frame, that is a data race again; pair the signal with double buffering or hand frames over through a queue (day 38).

### in practice

The `alignas(64)` matters when several threads each update their own counter at high rates. If two such counters share a cache line, every write by one core invalidates the line in the other core's cache, and two logically independent threads end up contending: *false sharing*. C++17 added `std::hardware_destructive_interference_size` in `<new>` for this, but support varies: GCC provides it from version 12 (64 on x86-64 here) and warns (`-Winterference-size`) when it is used in a header, because the value can change with tuning flags and so becomes an ABI hazard. Check `__cpp_lib_hardware_interference_size`, or use a named constant you control. Day 51 shows how to measure the effect with hardware counters.

The engineering advice is conservative. Use mutexes for compound state, `seq_cst` atomics for single flags and counters, and weaken orders only with a written justification and a benchmark showing it matters. Lock-free does not mean faster: a contended atomic still bounces a cache line between cores, CAS loops can retry under contention, and a lock-free design's correctness argument is much harder to review. What lock-freedom does guarantee is progress (some thread always makes progress, no thread can block others by being descheduled while holding a lock), and that is the property to want it for, for example in a real-time thread that must never block on a lower-priority one.

### watch out for

Mixing up "atomic" and "ordered". A `relaxed` flag is perfectly atomic and still publishes nothing: code that sets data, then `ready.store(true, std::memory_order_relaxed)`, then reads the data on the other side has a data race on the data. It may pass every test on x86, whose hardware ordering is strong enough to hide many such bugs, and then fail on ARM, or after a compiler upgrade reorders the stores. The memory model is a contract with the compiler and every CPU you will ever ship on, not a description of your test machine.

### the takeaway

Atomicity makes a single variable race-free; memory orders decide what *other* memory becomes visible. Release/acquire pairs build happens-before edges, `relaxed` builds none, and `seq_cst` is the right default until a measurement says otherwise.

### optional challenge

`x` and `y` are `std::atomic<int>` initialized to 0. Thread A runs `x.store(1, release); r1 = y.load(acquire);` and thread B runs `y.store(1, release); r2 = x.load(acquire);`. After both finish, can `r1 == 0 && r2 == 0`? What if every operation is `seq_cst`?

<details>
<summary>answer</summary>

With release/acquire, yes. Each acquire load synchronizes only with a release store *whose value it reads*; if both loads read 0, no synchronizes-with edge exists and nothing forbids the outcome. Real hardware produces it: a store can sit in the core's store buffer while the subsequent load of a different address executes. With `seq_cst` on all four operations, no: there is a single total order of the four operations consistent with each thread's program order, so whichever store comes first in that order precedes the other thread's load, which must then read 1. This "store buffering" pattern (as in Dekker's mutual exclusion algorithm) is the classic case where `seq_cst` is required and acquire/release is not enough.

</details>
