---
title: happens-before and memory orders
standard: C++20
objective: explain happens-before and the synchronizes-with edge, publish data correctly with release and acquire, and choose a memory order deliberately
prerequisites: atomics
difficulty: 3
---

### the idea

a radar thread fills a frame buffer and then sets `bool ready = true;`. a processing thread spins on `ready`, then reads the frame. on your x86 workstation it seems to work. it is still UB: `ready` is accessed concurrently and is not atomic, so it is a data race ([[data-races]]); the optimizer may hoist the load out of the spin loop; and even with a correct flag, the question remains whether the *frame data* written before the flag is guaranteed to be visible after it. answering that precisely is what the memory model is for.

### understanding the concept

`std::atomic<T>` (for trivially copyable `T`) makes each operation on the object indivisible, and concurrent atomic operations on the same object are never a data race. every atomic object also has a single *modification order* that all threads agree on. what atomicity alone does not give you is any promise about *other* memory. compilers reorder independent loads and stores, and so do CPUs (store buffers, out-of-order execution). the memory model defines which reorderings other threads may observe, using three relations:

- **sequenced-before**: program order within one thread.
- **synchronizes-with**: a *release* store to an atomic synchronizes with an *acquire* load of the same atomic that reads the value written by that store (or by a later read-modify-write in its release sequence).
- **happens-before**: built from the two above, transitively. if a write happens before a read of the same location, with no other write in between, the read sees that write. if two conflicting accesses, one non-atomic, are not ordered by happens-before, you have a data race.

mutex unlock/lock, thread start and `join`, and future readiness, which the previous lessons relied on, are all defined in terms of this relation. atomics let you build the edges yourself, choosing a `std::memory_order` per operation:

| order | what it guarantees | typical use |
|---|---|---|
| `seq_cst` (default) | acquire/release, plus one total order of all `seq_cst` operations that every thread agrees on | the default; anything you have not proven needs less |
| `release` (stores) / `acquire` (loads) / `acq_rel` (read-modify-writes) | the synchronizes-with edge: writes before the release are visible after the acquire that reads it | publishing data through a flag or pointer |
| `relaxed` | atomicity and the per-object modification order, nothing else | counters and statistics that publish nothing |
| `consume` | intended as a cheaper acquire for dependent loads | do not use: its specification is under revision, and compilers implement it as `acquire` |

### in code

message passing, the pattern behind almost every correct use of acquire/release:

```cpp complete
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

weaken either side to `relaxed` and the edge disappears: the reads of `frame` then race with the writes, which is UB, even though `ready` itself is still race-free. using a plain `bool` makes `ready` itself a data race. note the asymmetry: the order protects the *non-atomic* data around the atomic.

relaxed operations build no edges at all, so they are only right for values that publish nothing. the statistics from [[atomics]] are the classic case: `frames_dropped.fetch_add(1, std::memory_order_relaxed)` still never loses an increment, and a monitoring thread that reads the counter sees *some* recent value, because nobody reads other data based on it.

### in practice

the engineering advice is conservative. use mutexes for compound state, `seq_cst` atomics for single flags and counters, and weaken orders only with a written justification and a benchmark showing it matters. lock-free does not mean faster: a contended atomic still bounces a cache line between cores, CAS loops can retry under contention, and a lock-free design's correctness argument is much harder to review. what lock-freedom does guarantee is progress (some thread always makes progress, no thread can block others by being descheduled while holding a lock), and that is the property to want it for, for example in a real-time thread that must never block on a lower-priority one.

### watch out for

mixing up "atomic" and "ordered". a `relaxed` flag is perfectly atomic and still publishes nothing: code that sets data, then `ready.store(true, std::memory_order_relaxed)`, then reads the data on the other side has a data race on the data. it may pass every test on x86, whose hardware ordering is strong enough to hide many such bugs, and then fail on ARM, or after a compiler upgrade reorders the stores. the memory model is a contract with the compiler and every CPU you will ever ship on, not a description of your test machine.

### the takeaway

atomicity makes a single variable race-free; memory orders decide what *other* memory becomes visible. release/acquire pairs build happens-before edges, `relaxed` builds none, and `seq_cst` is the right default until a measurement says otherwise.

### optional challenge

`x` and `y` are `std::atomic<int>` initialized to 0. thread `A` runs `x.store(1, release); r1 = y.load(acquire);` and thread `B` runs `y.store(1, release); r2 = x.load(acquire);`. after both finish, can `r1 == 0 && r2 == 0`? what if every operation is `seq_cst`?

<details>
<summary>answer</summary>

with release/acquire, yes. each acquire load synchronizes only with a release store *whose value it reads*; if both loads read 0, no synchronizes-with edge exists and nothing forbids the outcome. real hardware produces it: a store can sit in the core's store buffer while the subsequent load of a different address executes. with `seq_cst` on all four operations, no: there is a single total order of the four operations consistent with each thread's program order, so whichever store comes first in that order precedes the other thread's load, which must then read 1. this "store buffering" pattern (as in Dekker's mutual exclusion algorithm) is the classic case where `seq_cst` is required and acquire/release is not enough.

</details>
