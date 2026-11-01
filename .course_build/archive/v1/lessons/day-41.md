<a id="day-41"></a>

## day 41: deadlocks and concurrency design

**reading time:** about 10 minutes · **standard:** C++20 · **builds on:** days 36, 37, 38, 39, 40

### the idea

A tracker merges track stores: `merge(a, b)` locks `a`, then `b`. Under rare timing, one thread runs `merge(left, right)` while another runs `merge(right, left)`. Each holds one mutex and waits forever for the other. Nothing crashes and nothing is logged; the robot simply stops publishing tracks after three days in the field. Deadlocks are the concurrency bug that hides best in testing, so the defenses have to be structural.

### understanding the concept

A deadlock needs four conditions at once: mutual exclusion, hold-and-wait (holding one resource while waiting for another), no preemption (nobody can take a lock away), and a circular wait. Mutexes give you the first three for free, so practical defenses break the cycle:

- **Acquire several locks at once** with `std::scoped_lock(m1, m2)` (C++17). It uses the `std::lock` deadlock-avoidance algorithm, so argument order does not matter.
- **Fixed lock ordering** when locks are taken at different times: every code path acquires them in the same global order. A *lock hierarchy* makes this checkable: give each mutex a level and assert, in debug builds, that a thread only acquires locks with a lower level than any it already holds.
- **Never call unknown code while holding a lock.** A callback, a virtual function overridden elsewhere, or a user-supplied `std::function` can take other locks (creating a cycle you cannot see) or call back into your object and try to lock the same `std::mutex` again. Locking a `std::mutex` the calling thread already owns is UB, and in practice usually a self-deadlock. `std::recursive_mutex` hides the symptom, but the callback then runs while your invariants may be half-updated.

Two cousins are worth naming. In a *livelock*, threads keep reacting to each other (both back off with `try_lock`, both retry, forever) without progress. In *starvation*, one thread never gets its turn, for example a writer behind a constant stream of readers on a `std::shared_mutex`, whose fairness the standard does not specify.

C++20 also added three coordination primitives that replace many hand-rolled condition variable patterns:

| primitive | semantics | typical use |
|---|---|---|
| `std::latch` | one-shot countdown; `wait()` until it reaches zero | startup: wait until every driver is initialized |
| `std::barrier` | reusable; all participants `arrive_and_wait()` per phase; an optional completion function runs once per phase | lock-step simulation or pipelines |
| `std::counting_semaphore<N>` | a counter of permits; `acquire()` blocks at zero; any thread may `release()` | limit concurrent access to a resource |

### in code

The merge deadlock and its fix:

```cpp
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

Calling out of the lock. The tempting version runs handlers inside the critical section; if a handler calls `subscribe()`, the same thread locks `m_` twice:

```cpp
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

The copy costs allocations per publish; a `std::shared_ptr<const std::vector<Handler>>` snapshot (day 37) avoids that. Day 45 returns to this as the observer pattern, including unsubscription.

The C++20 primitives, one use each:

```cpp
#include <barrier>
#include <latch>
#include <semaphore>
#include <stop_token>
#include <thread>
#include <vector>

struct Blob;                                   // provided elsewhere:
void init_driver(int);  void run_driver(int, std::stop_token);  void run_until_shutdown();
void swap_buffers() noexcept;  void update_partition(int);  void send(const Blob&);

void start_drivers(int n) {
    std::latch initialized(n);                 // declared before the threads that use it
    std::vector<std::jthread> drivers;
    for (int i = 0; i < n; ++i)
        drivers.emplace_back([&initialized, i](std::stop_token st) {
            init_driver(i);
            initialized.count_down();
            run_driver(i, st);
        });
    initialized.wait();                        // every driver is initialized here
    run_until_shutdown();
}                                              // drivers stop and join, then the latch dies

std::barrier step_done(4, []() noexcept { swap_buffers(); });   // runs once per phase
void simulate(int part, int steps) {           // run by 4 threads
    for (int s = 0; s < steps; ++s) {
        update_partition(part);                // reads the old buffer, writes the new one
        step_done.arrive_and_wait();
    }
}

std::counting_semaphore<4> upload_slots(4);    // at most 4 concurrent uploads
void upload(const Blob& b) {
    upload_slots.acquire();
    struct Release { std::counting_semaphore<4>& s; ~Release() { s.release(); } } guard{upload_slots};
    send(b);                                   // released even if send throws
}
```

The barrier's completion function must be `noexcept`-invocable; it runs after all participants arrive and before any is released, which makes it the safe place to swap double buffers. A semaphore has no owner, unlike a mutex, so nothing stops a missing `release()`: wrap it in RAII as shown.

Finally, the minimal thread pool, built on day 38's `BoundedQueue`:

```cpp
#include <cstddef>
#include <functional>
#include <thread>
#include <vector>
// plus BoundedQueue<T> from day 38

class ThreadPool {
public:
    explicit ThreadPool(std::size_t n) : tasks_(1024) {
        for (std::size_t i = 0; i < n; ++i)
            workers_.emplace_back([this] {
                while (auto task = tasks_.pop()) (*task)();   // a throwing task terminates
            });
    }
    ~ThreadPool() { tasks_.close(); }     // workers drain the queue and exit, then join
    bool submit(std::function<void()> f) { return tasks_.push(std::move(f)); }
private:
    BoundedQueue<std::function<void()>> tasks_;
    std::vector<std::jthread> workers_;   // declared last: joined before tasks_ dies
};
```

It is about fifteen lines, and it is missing what production pools need: futures for results (day 39's `packaged_task`), exception handling, work stealing, priorities, and protection against the deadlock below. Use an existing executor (Boost.Asio's `thread_pool`, oneTBB, or your framework's) unless you have a reason not to.

### in practice

The best way to avoid deadlocks is to need fewer locks. Three designs do most of the work:

- **Confinement**: each piece of mutable state is owned by exactly one thread. A lidar driver's parser state lives on the driver thread and is never shared.
- **Message passing**: threads communicate by moving values through queues (day 38). Ownership transfers with the message, so nothing is shared at all.
- **Immutable shared data**: configuration and calibration published as `std::shared_ptr<const T>` snapshots can be read by everyone without locks.

Locks then remain only inside a few small, well-tested components (queues, snapshot holders), which is where they belong. Test those components with stress tests: many iterations, more threads than cores, random small delays injected around the critical sections, and assertions on invariants. In a separate build on Linux or macOS, run them under ThreadSanitizer (`-fsanitize=thread` with GCC or Clang), which reports data races on the paths your tests execute and also lock-order inversions, the deadlock risk above, even in runs that did not actually deadlock.

### watch out for

Thread-starvation deadlock in pools. A task running on a pool submits a subtask to the same pool and blocks on its future. If every worker does this at once, all workers are waiting for subtasks that no free worker can run. No mutex is involved, so lock ordering cannot save you. Avoid blocking waits inside pool tasks; split the work so the waiting happens outside the pool, or use a framework that runs nested tasks while waiting (work-stealing schedulers do).

### the takeaway

Deadlocks come from cycles, so break the cycle by design: take multiple locks with `std::scoped_lock`, never call unknown code under a lock, and prefer confinement, message passing, and immutable data so that few locks exist at all.

### optional challenge

In the fixed `merge`, why does the self-merge check matter? Without it, what does `merge(store, store)` do?

<details>
<summary>answer</summary>

`std::scoped_lock lock(into.m, from.m)` would be asked to lock the same `std::mutex` twice. The standard leaves the deadlock-avoidance algorithm unspecified; typical implementations lock one mutex and then `try_lock` the others. Either way, calling `lock` or `try_lock` on a `std::mutex` the calling thread already owns is UB. In practice the thread may hang, spin forever, or appear to succeed. Even if locking worked, the function body would then insert a vector into itself through iterators that the insertion can invalidate. The early return turns an invalid call into a no-op; documenting `into != from` as a precondition (and asserting it) is a reasonable alternative.

</details>
