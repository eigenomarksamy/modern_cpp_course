---
title: `std::atomic`: indivisible operations
standard: C++17
objective: make single variables race-free with `std::atomic`, use read-modify-write operations and compare-and-swap loops, and recognize when atomics are not enough
prerequisites: data-races, mutexes
difficulty: 2
---

### the idea

the frame counter from [[data-races]] lost updates because `++frames` is three steps: load, add, store. a mutex fixed it by making the threads take turns. for a single integer, that is a lot of machinery: what you want is for the increment itself to be one indivisible step. `std::atomic` provides exactly that, and only that, which is both why it is fast and why it is so easy to misuse.

### understanding the concept

`std::atomic<T>` (for trivially copyable `T`) makes each operation on the object indivisible, and concurrent atomic operations on the same object are never a data race. every atomic object has a single *modification order* that all threads agree on, so no increment is ever lost.

read-modify-write operations (`exchange`, `fetch_add`, `compare_exchange_weak/strong`) are atomic as a whole. `compare_exchange` writes the new value only if the current value equals `expected` (compared byte for byte like `memcmp`, not with `operator==`, which matters for `float` and padding); on failure it loads the current value into `expected`. the `weak` form may fail spuriously (even when the values are equal), which is fine in a loop and can be cheaper on LL/SC architectures such as ARM.

atomicity covers *one operation on one object*. a sequence of atomic operations is not atomic as a whole, and an atomic variable says nothing by itself about other, non-atomic memory; how atomics order other memory is the subject of [[memory-model]].

### in code

the counter, a statistic, and a compare-and-swap loop for an operation the library does not provide:

```cpp complete
#include <atomic>
#include <cstdint>

std::atomic<std::uint64_t> frames_dropped{0};
std::atomic<float> peak_power{0.0f};

void on_drop() {
    ++frames_dropped;                 // one atomic read-modify-write: no lost updates
}

void record_power(float p) {
    float cur = peak_power.load();
    while (cur < p && !peak_power.compare_exchange_weak(cur, p)) {
        // failed: cur now holds the latest value; the loop re-checks cur < p
    }
}
```

there is no `fetch_max` in C++20, so the CAS loop is the standard way to build any read-modify-write the library lacks: read the current value, compute the new one, and publish it only if nobody changed the value in between, retrying otherwise.

### in practice

an atomic counter shared by eight worker threads is correct, and it can still be slow: every increment needs exclusive ownership of the cache line that holds it, so the line bounces between cores. when only the total matters, count in a local variable inside each worker and add it to the shared atomic once per batch or at the end. the same idea scales up: the cheapest synchronization is the one you avoid by not sharing. atomics are the right tool for genuinely shared single values (a stop flag, a sequence number, a statistic read by a monitoring thread), not a faster replacement for every mutex.

### watch out for

**two atomic operations are not one.**

```cpp
std::atomic<int> active{0};
constexpr int max_active = 4;

bool try_enter() {
    if (active.load() < max_active) {   // BUG: another thread can enter between the load...
        ++active;                       // ...and the increment: five threads get in
        return true;
    }
    return false;
}
```

each operation is atomic and there is no data race, but the check and the increment are separate steps: a race condition, as in [[data-races]]. make the decision and the update one read-modify-write with a CAS loop (`while (cur < max_active && !active.compare_exchange_weak(cur, cur + 1))`), or protect the compound state with a mutex.

### the takeaway

`std::atomic` makes each single operation on one variable indivisible and race-free; anything that spans two operations needs a compare-and-swap loop or a mutex.

### optional challenge

two threads each run `x = x + 1;` a thousand times on `std::atomic<int> x{0};`. is the program undefined? what values can `x` end with?

<details>
<summary>answer</summary>

it is not undefined: every access is atomic, so there is no data race. but `x = x + 1` is an atomic load followed by a separate atomic store, so two threads can both read the same value and both store the same increment, losing one update. the final value can be anything from 2 up to 2000 (2 is reachable in a pathological interleaving). `++x`, `x += 1`, or `x.fetch_add(1)` is a single read-modify-write and always ends at 2000.

</details>
