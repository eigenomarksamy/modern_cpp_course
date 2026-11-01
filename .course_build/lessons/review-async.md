---
title: review: futures, atomics, and concurrency design
kind: review
standard: C++20
objective: consolidate futures and async, atomics and memory orders, atomic waits, deadlock avoidance, and C++20 coordination primitives
prerequisites: futures, async, atomics, memory-model, atomic-waiting, deadlocks, sync-primitives
difficulty: 2
---

### recap

| lesson | key idea |
|---|---|
| [[futures]] | a one-shot channel for a value or an exception, synchronizing like `join`. |
| [[async]] | name the launch policy, and keep the futures alive: a discarded `std::async` future blocks. |
| [[atomics]] | single operations are indivisible; anything spanning two operations needs a CAS loop or a mutex. |
| [[memory-model]] | release/acquire pairs build happens-before edges for the surrounding data; `relaxed` builds none. |
| [[atomic-waiting]] | wait and notify instead of spinning, keep hot atomics on separate cache lines, assert lock-freedom. |
| [[deadlocks]] | break the cycle: `std::scoped_lock`, no unknown code or blocking waits under a lock. |
| [[sync-primitives]] | latch for startup, barrier for phases, semaphore for limits; prefer existing executors. |

### review questions

1. two threads run this. is it correct?

   ```cpp
   std::atomic<int> count{0};
   std::vector<int> data;

   void add(int x) {
       if (count.load() < 100) { data.push_back(x); ++count; }
   }
   ```
2. this loop was meant to process chunks of a point cloud in parallel. a profile shows one core busy at a time. why?

   ```cpp
   for (auto& chunk : chunks)
       std::async(std::launch::async, process, std::ref(chunk));
   ```
3. pick a memory order for each: (a) a frames-processed counter that a statistics thread prints once a second; (b) a flag that tells a consumer a calibration struct has been fully written; (c) two threads that each set their own "I want to enter" flag and then read the other thread's flag.
4. from [[mutexes]]: a component calls registered callbacks while holding its mutex, and one callback calls back into the component. what happens, and what is the fix?

### mini exercise

find three concurrency bugs in this class, then fix them. assume `on_change`, `set`, and `get` can each be called from any thread at any time.

```cpp complete
#include <functional>
#include <map>
#include <mutex>
#include <string>

class TelemetryHub {
public:
    using Listener = std::function<void(const std::string&, double)>;

    void on_change(Listener l) { listener_ = std::move(l); }

    void set(const std::string& key, double value) {
        std::lock_guard lock(m_);
        latest_[key] = value;
        if (listener_) listener_(key, value);
    }

    const double& get(const std::string& key) {
        std::lock_guard lock(m_);
        return latest_.at(key);
    }

private:
    std::mutex m_;
    std::map<std::string, double> latest_;
    Listener listener_;
};
```

### answers

<details>
<summary>answer 1: an atomic counter does not protect a vector</summary>

no, and for two separate reasons. `data.push_back` from two threads is a data race on the vector, which is UB; making `count` atomic says nothing about other memory ([[memory-model]]). and even with the vector protected, check-then-act is a race condition: both threads can see 99 and both append ([[mutexes]]). fix both with one mutex guarding the vector, with the check and the push in one critical section; `data.size()` then replaces the counter.

</details>

<details>
<summary>answer 2: the accidentally sequential loop</summary>

each returned `std::future` is a temporary destroyed at the end of the statement, and a future from `std::async` blocks in its destructor until its task finishes. every iteration waits for its own chunk ([[async]]). since C++20, `std::async` is `[[nodiscard]]`, so GCC warns about this line. keep the futures in a `std::vector<std::future<void>>`, then call `get()` on each, which also rethrows any exception a chunk threw.

</details>

<details>
<summary>answer 3: choosing memory orders</summary>

(a) `relaxed`: only the count matters, and nothing is published through it. (b) `release` on the store and `acquire` on the load: the edge makes the struct's non-atomic writes visible after the flag is seen. (c) `seq_cst`: this is the store-buffering pattern from [[memory-model]]'s challenge, where acquire/release allows both threads to read `false`. if you are unsure, the default `seq_cst` is never wrong, only sometimes slower.

</details>

<details>
<summary>answer 4: callbacks under a lock</summary>

the callback runs on the same thread that already holds the component's `std::mutex`, so its call back into the component tries to lock it again: undefined behavior, in practice usually a self-deadlock. `std::recursive_mutex` would hide the symptom and run the callback against half-updated state. copy what the callbacks need (including the list of callbacks) under the lock, release it, and then call them.

</details>

<details>
<summary>mini exercise answer</summary>

the bugs: (1) `on_change` writes `listener_` without the lock while `set` reads it, a data race. (2) `set` calls the listener while holding `m_`; a listener that calls `get()` locks `m_` again on the same thread (UB, in practice a self-deadlock), and one that takes another lock can form a lock-order cycle ([[deadlocks]]). (3) `get` returns a reference into the map; reading it after the lock is released races with a concurrent `set` of the same key ([[mutexes]]).

```cpp
class TelemetryHub {
public:
    using Listener = std::function<void(const std::string&, double)>;

    void on_change(Listener l) {
        std::lock_guard lock(m_);
        listener_ = std::move(l);
    }

    void set(const std::string& key, double value) {
        Listener listener;
        {
            std::lock_guard lock(m_);
            latest_[key] = value;
            listener = listener_;           // copy under the lock
        }
        if (listener) listener(key, value); // call unknown code with no lock held
    }

    double get(const std::string& key) const {
        std::lock_guard lock(m_);
        return latest_.at(key);             // a copy, not a reference
    }

private:
    mutable std::mutex m_;
    std::map<std::string, double> latest_;
    Listener listener_;
};
```

the fix has a price worth naming: listeners now run outside the lock, so two concurrent `set` calls on the same key can notify in the opposite order to their writes. if listeners need a consistent order, push the updates into a queue drained by one thread ([[condition-variables]]). copying the `std::function` may allocate on every `set`; a `std::shared_ptr<const Listener>` snapshot avoids that if a profile says it matters.

</details>

### connections

with this module, the concurrency toolbox is complete: threads and their ownership, mutexes and condition variables, futures, atomics and the memory model, and the C++20 coordination primitives. the recurring design lesson is that the best synchronization is the one you do not need: confinement, message passing, and immutable shared data. the next module steps back from mechanisms to design: SOLID, coupling and cohesion, dependency injection, and patterns, where ownership and lifetimes decide how components are wired together.
