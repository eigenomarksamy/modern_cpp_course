---
title: deadlocks: breaking the cycle
standard: C++17
objective: recognize the conditions for deadlock, take multiple locks safely, and keep unknown code and blocking waits out of critical sections
prerequisites: mutexes, condition-variables
difficulty: 2
---

### the idea

a tracker merges track stores: `merge(a, b)` locks `a`, then `b`. under rare timing, one thread runs `merge(left, right)` while another runs `merge(right, left)`. each holds one mutex and waits forever for the other. nothing crashes and nothing is logged; the robot simply stops publishing tracks after three days in the field. deadlocks are the concurrency bug that hides best in testing, so the defenses have to be structural.

### understanding the concept

a deadlock needs four conditions at once: mutual exclusion, hold-and-wait (holding one resource while waiting for another), no preemption (nobody can take a lock away), and a circular wait. mutexes give you the first three for free, so practical defenses break the cycle:

- **acquire several locks at once** with `std::scoped_lock(m1, m2)` (C++17). it uses the `std::lock` deadlock-avoidance algorithm, so argument order does not matter.
- **fixed lock ordering** when locks are taken at different times: every code path acquires them in the same global order. a *lock hierarchy* makes this checkable: give each mutex a level and assert, in debug builds, that a thread only acquires locks with a lower level than any it already holds.
- **never call unknown code while holding a lock.** a callback, a virtual function overridden elsewhere, or a user-supplied `std::function` can take other locks (creating a cycle you cannot see) or call back into your object and try to lock the same `std::mutex` again. locking a `std::mutex` the calling thread already owns is UB, and in practice usually a self-deadlock. `std::recursive_mutex` hides the symptom, but the callback then runs while your invariants may be half-updated.

two cousins are worth naming. in a *livelock*, threads keep reacting to each other (both back off with `try_lock`, both retry, forever) without progress. in *starvation*, one thread never gets its turn, for example a writer behind a constant stream of readers on a `std::shared_mutex`, whose fairness the standard does not specify.

### in code

the merge deadlock and its fix:

```cpp ub
#include <mutex>
#include <vector>

struct Track { int id; double range_m; };
struct TrackStore {
    std::mutex m;
    std::vector<Track> tracks;
};

void merge_buggy(TrackStore& into, TrackStore& from) {
    std::lock_guard a(into.m);
    std::lock_guard b(from.m);     // BUG: merge(x, y) || merge(y, x) can deadlock
    into.tracks.insert(into.tracks.end(), from.tracks.begin(), from.tracks.end());
    from.tracks.clear();
}

void merge(TrackStore& into, TrackStore& from) {
    if (&into == &from) return;               // locking one std::mutex twice would be UB
    std::scoped_lock lock(into.m, from.m);    // both or neither, in any argument order
    into.tracks.insert(into.tracks.end(), from.tracks.begin(), from.tracks.end());
    from.tracks.clear();
}
```

calling out of the lock. the tempting version runs handlers inside the critical section; if a handler calls `subscribe()`, the same thread locks `m_` twice:

```cpp complete
#include <functional>
#include <mutex>
#include <vector>

struct Detection { float range_m; };

class DetectionBus {
public:
    using Handler = std::function<void(const Detection&)>;
    void subscribe(Handler h) {
        std::lock_guard lock(m_);
        handlers_.push_back(std::move(h));
    }
    void publish(const Detection& d) {
        std::vector<Handler> snapshot;
        {
            std::lock_guard lock(m_);
            snapshot = handlers_;              // copy under the lock...
        }
        for (const auto& h : snapshot) h(d);   // ...call unknown code with no lock held
    }
private:
    std::mutex m_;
    std::vector<Handler> handlers_;
};
```

the copy costs allocations per publish; a `std::shared_ptr<const std::vector<Handler>>` snapshot ([[mutexes]]) avoids that. [[observer]] returns to this as the observer pattern, including unsubscription.

### in practice

the best way to avoid deadlocks is to need fewer locks. three designs do most of the work:

- **confinement**: each piece of mutable state is owned by exactly one thread. a lidar driver's parser state lives on the driver thread and is never shared.
- **message passing**: threads communicate by moving values through queues ([[blocking-queue]]). ownership transfers with the message, so nothing is shared at all.
- **immutable shared data**: configuration and calibration published as `std::shared_ptr<const T>` snapshots can be read by everyone without locks.

locks then remain only inside a few small, well-tested components (queues, snapshot holders), which is where they belong. test those components with stress tests: many iterations, more threads than cores, random small delays injected around the critical sections, and assertions on invariants. in a separate build on Linux or macOS, run them under ThreadSanitizer (`-fsanitize=thread` with GCC or Clang), which reports data races on the paths your tests execute and also lock-order inversions, the deadlock risk above, even in runs that did not actually deadlock.

### watch out for

**waiting while holding a lock.** a deadlock does not need two mutexes. any blocking wait performed under a lock can close a cycle:

```cpp
void Driver::stop() {
    std::lock_guard lock(m_);
    running_ = false;
    worker_.join();        // BUG: if the worker needs m_ to finish its iteration, both wait forever
}
```

the worker is blocked on `m_`, and the thread holding `m_` is blocked on the worker. the same shape appears with `future::get()`, a condition variable on a different mutex, or a synchronous call into another component. update the shared state under the lock, release it, and only then wait.

### the takeaway

deadlocks come from cycles, so break the cycle by design: take multiple locks with `std::scoped_lock`, never call unknown code under a lock, and prefer confinement, message passing, and immutable data so that few locks exist at all.

### optional challenge

in the fixed `merge`, why does the self-merge check matter? without it, what does `merge(store, store)` do?

<details>
<summary>answer</summary>

`std::scoped_lock lock(into.m, from.m)` would be asked to lock the same `std::mutex` twice. the standard leaves the deadlock-avoidance algorithm unspecified; typical implementations lock one mutex and then `try_lock` the others. either way, calling `lock` or `try_lock` on a `std::mutex` the calling thread already owns is UB. in practice the thread may hang, spin forever, or appear to succeed. even if locking worked, the function body would then insert a vector into itself through iterators that the insertion can invalidate. the early return turns an invalid call into a no-op; documenting `into != from` as a precondition (and asserting it) is a reasonable alternative.

</details>
