---
title: latches, barriers, semaphores, and thread pools
standard: C++20
objective: coordinate threads with `std::latch`, `std::barrier`, and `std::counting_semaphore`, and understand what a minimal thread pool does and lacks
prerequisites: deadlocks, blocking-queue, futures
difficulty: 2
---

### the idea

"wait until every driver has initialized", "let all four simulation threads finish this step before anyone starts the next", "never run more than four uploads at once": these are common coordination needs, and before C++20 each one was a hand-written mix of a mutex, a condition variable, and a counter, with the usual opportunities for lost wakeups. C++20 standardized three small primitives for exactly these shapes, and they compose naturally with the queue you already have into the simplest kind of thread pool.

### understanding the concept

C++20 also added three coordination primitives that replace many hand-rolled condition variable patterns:

| primitive | semantics | typical use |
|---|---|---|
| `std::latch` | one-shot countdown; `wait()` until it reaches zero | startup: wait until every driver is initialized |
| `std::barrier` | reusable; all participants `arrive_and_wait()` per phase; an optional completion function runs once per phase | lock-step simulation or pipelines |
| `std::counting_semaphore<N>` | a counter of permits; `acquire()` blocks at zero; any thread may `release()` | limit concurrent access to a resource |

### in code

the C++20 primitives, one use each:

```cpp complete
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

the barrier's completion function must be `noexcept`-invocable; it runs after all participants arrive and before any is released, which makes it the safe place to swap double buffers. a semaphore has no owner, unlike a mutex, so nothing stops a missing `release()`: wrap it in RAII as shown.

finally, the minimal thread pool, built on [[blocking-queue]]'s `BoundedQueue`:

```cpp
#include <cstddef>
#include <functional>
#include <thread>
#include <vector>
// plus BoundedQueue<T> from the bounded queue lesson

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

it is about fifteen lines, and it is missing what production pools need: futures for results ([[futures]]'s `packaged_task`), exception handling, work stealing, priorities, and protection against the deadlock below. use an existing executor (Boost.Asio's `thread_pool`, oneTBB, or your framework's) unless you have a reason not to.

### in practice

how many threads should a pool have? for CPU-bound work, about one per core is the usual starting point, and `std::thread::hardware_concurrency()` is a hint for that (it may return 0). for work that blocks on I/O, more threads keep the cores busy while others wait, and the right number is found by measuring. two rules hold in either case. keep latency-critical threads, such as a control loop, out of general-purpose pools, so a burst of background work cannot delay them; give them their own dedicated thread. and prefer an existing executor in production: the hard parts (results, exceptions, fairness, nested tasks, shutdown) are already solved there.

### watch out for

thread-starvation deadlock in pools. a task running on a pool submits a subtask to the same pool and blocks on its future. if every worker does this at once, all workers are waiting for subtasks that no free worker can run. no mutex is involved, so lock ordering cannot save you. avoid blocking waits inside pool tasks; split the work so the waiting happens outside the pool, or use a framework that runs nested tasks while waiting (work-stealing schedulers do).

### the takeaway

use a latch for one-time startup synchronization, a barrier for lock-step phases, and a semaphore to bound concurrency, each wrapped so it cannot be left in the wrong state; and keep blocking waits out of pool tasks.

### optional challenge

in `start_drivers`, why must the latch be declared before the vector of `std::jthread`s? what could go wrong if the declarations were swapped?

<details>
<summary>answer</summary>

locals are destroyed in reverse order of declaration. with the latch declared first, the vector is destroyed first: every `jthread` requests stop and joins, so no driver thread can still be using the latch when it is destroyed. swapped, the latch would be destroyed before the threads are joined, and a driver that is slow to initialize could call `count_down()` on a destroyed object, which is undefined behavior. it is the same rule as declaring a `jthread` member last in [[jthread]].

</details>
