<a id="day-42"></a>

## day 42: week 6 review: sharing safely

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 36 to 41

### recap

| day | idea in one line |
|---|---|
| [36](#day-36) | Own every thread with RAII: `std::jthread` joins in its destructor, `stop_token` makes cancellation cooperative, and `detach` needs a written justification. |
| [37](#day-37) | A data race is UB; bundle each mutex with the data it guards, make each method one transaction, and never let a reference to guarded data escape the lock. |
| [38](#day-38) | A condition variable lets you sleep until shared state changes: change that state under the mutex, wait with a predicate, and choose a back-pressure policy on purpose. |
| [39](#day-39) | A future is a one-shot channel for a value or an exception; name the launch policy and keep `std::async` futures alive while the work should run. |
| [40](#day-40) | Atomicity makes one variable race-free; memory orders decide what *other* memory becomes visible. Release/acquire publishes, `relaxed` publishes nothing, `seq_cst` is the default. |
| [41](#day-41) | Deadlocks are cycles: take several locks with `std::scoped_lock`, never call unknown code under a lock, and design so that few locks exist at all. |

The theme of the week: shared mutable state is the problem, and every tool this week is a different way of controlling it. Mutexes serialize it, atomics shrink it to one variable, futures and queues hand it over, and good design (confinement, message passing, immutable snapshots) removes it.

### review questions

1. A `Poller` class declares `std::jthread worker_;` first and `std::vector<float> buffer_;` second, and the thread function writes into `buffer_`. Every member is RAII. What can go wrong when a `Poller` is destroyed?

2. Two threads run this. Is it correct?

   ```cpp
   std::atomic<int> count{0};
   std::vector<int> data;

   void add(int x) {
       if (count.load() < 100) { data.push_back(x); ++count; }
   }
   ```

3. The producer never touches the mutex. Is there a data race? Can the consumer hang?

   ```cpp
   std::atomic<bool> ready{false};
   std::mutex m;
   std::condition_variable cv;

   void producer() { ready = true; cv.notify_one(); }
   void consumer() {
       std::unique_lock lock(m);
       cv.wait(lock, [] { return ready.load(); });
   }
   ```

4. This loop was meant to process chunks of a point cloud in parallel. A profile shows one core busy at a time. Why?

   ```cpp
   for (auto& chunk : chunks)
       std::async(std::launch::async, process, std::ref(chunk));
   ```

5. Pick a memory order for each: (a) a frames-processed counter that a statistics thread prints once a second; (b) a flag that tells a consumer a calibration struct has been fully written; (c) two threads that each set their own "I want to enter" flag and then read the other thread's flag.

6. **From week 5.** What is wrong here, and what are two fixes?

   ```cpp
   void start_fft(std::jthread& worker) {
       std::vector<float> samples = read_frame();
       worker = std::jthread([s = std::span<const float>(samples)] { fft(s); });
   }
   ```

7. **From week 2.** Threads A and B each hold their own copy of a `std::shared_ptr<const Config>` and reset it at the same time. Threads C and D share one global `std::shared_ptr<const Config> g_config`; C assigns a new config to it while D copies it. Which pair is safe?

### mini exercise

Find three concurrency bugs in this class, then fix them. Assume `on_change`, `set`, and `get` can each be called from any thread at any time.

```cpp
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
<summary>1. member order and jthread</summary>

Members are destroyed in reverse declaration order, so `buffer_` is destroyed first, while `worker_` is still running. The thread can write into a destroyed vector until `worker_`'s destructor requests stop and joins: UB. Declare the `std::jthread` last, after everything it touches (day 36). The same rule kept day 41's `ThreadPool` correct.

</details>

<details>
<summary>2. an atomic counter does not protect a vector</summary>

No, and for two separate reasons. `data.push_back` from two threads is a data race on the vector, which is UB; making `count` atomic says nothing about other memory (day 40). And even with the vector protected, check-then-act is a race condition: both threads can see 99 and both append (day 37). Fix both with one mutex guarding the vector, with the check and the push in one critical section; `data.size()` then replaces the counter.

</details>

<details>
<summary>3. lost wakeup</summary>

No data race, since `ready` is atomic. Yes, it can hang. The consumer checks the predicate under `m` and sees `false`. Before it blocks, the producer sets `ready` and calls `notify_one()`; nobody is waiting yet, so the notification is lost and the consumer sleeps forever (unless a spurious wakeup rescues it). Because the producer never takes `m`, nothing orders its store between the consumer's check and its sleep. Fix: `{ std::lock_guard lk(m); ready = true; } cv.notify_one();`. With the store under the mutex, `ready` can be a plain `bool` (day 38).

</details>

<details>
<summary>4. the accidentally sequential loop</summary>

Each returned `std::future` is a temporary destroyed at the end of the statement, and a future from `std::async` blocks in its destructor until its task finishes. Every iteration waits for its own chunk (day 39). Since C++20, `std::async` is `[[nodiscard]]`, so GCC warns about this line. Keep the futures in a `std::vector<std::future<void>>`, then call `get()` on each, which also rethrows any exception a chunk threw.

</details>

<details>
<summary>5. choosing memory orders</summary>

(a) `relaxed`: only the count matters, and nothing is published through it. (b) `release` on the store and `acquire` on the load: the edge makes the struct's non-atomic writes visible after the flag is seen. (c) `seq_cst`: this is the store-buffering pattern from day 40's challenge, where acquire/release allows both threads to read `false`. If you are unsure, the default `seq_cst` is never wrong, only sometimes slower.

</details>

<details>
<summary>6. from week 5: a span handed to a thread</summary>

`std::span` borrows (day 31). `samples` is destroyed when `start_fft` returns, while the new thread may still be reading it: a dangling span and UB. A span is only safe to borrow across threads when the owner provably outlives the thread. Fixes: move ownership into the thread (`[v = std::move(samples)] { fft(v); }`, with `fft` taking a span so the vector converts), or share immutable data with `std::shared_ptr<const std::vector<float>>` when several threads need it.

</details>

<details>
<summary>7. from week 2: shared_ptr and threads</summary>

A and B are safe: the reference count updates are atomic, so separate `shared_ptr` objects that share a control block may be copied and destroyed concurrently (day 12). C and D are a data race on the single `g_config` object, UB. Copy it under a mutex (day 37's snapshot pattern) or use C++20's `std::atomic<std::shared_ptr<const Config>>`. That specialization is not guaranteed to be lock-free, so measure before assuming it beats a mutex. Either way, the `Config` itself is safe to read because it is `const`.

</details>

<details>
<summary>mini exercise: one solution</summary>

The bugs: (1) `on_change` writes `listener_` without the lock while `set` reads it, a data race. (2) `set` calls the listener while holding `m_`; a listener that calls `get()` locks `m_` again on the same thread (UB, in practice a self-deadlock), and one that takes another lock can form a lock-order cycle (day 41). (3) `get` returns a reference into the map; reading it after the lock is released races with a concurrent `set` of the same key (day 37).

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

The fix has a price worth naming: listeners now run outside the lock, so two concurrent `set` calls on the same key can notify in the opposite order to their writes. If listeners need a consistent order, push the updates into a queue drained by one thread (day 38). Copying the `std::function` may allocate on every `set`; a `std::shared_ptr<const Listener>` snapshot avoids that if a profile says it matters.

</details>

### connections

- **Back to weeks 1 to 5.** A data race is the most common UB in concurrent code (day 06). RAII carries the week: `jthread`, `lock_guard`, `scoped_lock`, and day 41's semaphore guard are day 08's idea applied to threads and locks. Lambda captures (day 17) decide what a thread can touch and for how long. Futures carry exceptions with the guarantees from day 20, `std::optional` (day 24) is how a closed queue says "no more items", and `std::span` (day 31) is fine to hand to a thread only while its owner lives.
- **Ahead.** Week 7 is design. The thread-safe class as a unit of cohesion (day 37) returns with SOLID (day 43). Injecting a clock (day 44) makes timeouts and periodic threads testable. Day 41's `DetectionBus` becomes the observer pattern with RAII subscriptions (day 45), and coroutines (day 48) show asynchrony without a thread per task. Day 53 adds stress testing and sanitizers, and the day 55 capstone wires `BoundedQueue`, `std::jthread`, and `stop_token` into one pipeline.
