---
title: review: threads and synchronization
kind: review
standard: C++20
objective: consolidate thread ownership, jthread and stop tokens, data races, mutexes, condition variables, and the bounded queue
prerequisites: threads, jthread, data-races, mutexes, condition-variables, blocking-queue
difficulty: 2
---

### recap

| lesson | key idea |
|---|---|
| [[threads]] | a joinable `std::thread` terminates the program on destruction; arguments are copied in, and references must outlive the thread. |
| [[jthread]] | `std::jthread` stops and joins in its destructor; cancellation is cooperative through stop tokens and callbacks. |
| [[data-races]] | conflicting non-atomic accesses without happens-before are undefined behavior; race conditions are a separate bug. |
| [[mutexes]] | bundle each mutex with its data, make each method one transaction, and never let guarded data escape the lock. |
| [[condition-variables]] | sleep until shared state changes: modify it under the mutex, and always wait with a predicate. |
| [[blocking-queue]] | a bounded queue with `close()` makes back-pressure and shutdown explicit. |

### review questions

1. a `Poller` class declares `std::jthread worker_;` first and `std::vector<float> buffer_;` second, and the thread function writes into `buffer_`. every member is RAII. what can go wrong when a `Poller` is destroyed?
2. a `TrackTable` offers a locked `contains(id)` and a locked `insert(id, track)`, and callers write `if (!t.contains(id)) t.insert(id, track);`. is there a data race? is the code correct?
3. the producer never touches the mutex. is there a data race? can the consumer hang?

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
4. from [[span]]: what is wrong here, and what are two fixes?

   ```cpp
   void start_fft(std::jthread& worker) {
       std::vector<float> samples = read_frame();
       worker = std::jthread([s = std::span<const float>(samples)] { fft(s); });
   }
   ```

5. from [[shared-ptr]]: threads `A` and `B` each hold their own copy of a `std::shared_ptr<const Config>` and reset it at the same time. threads `C` and `D` share one global `std::shared_ptr<const Config> g_config`; `C` assigns a new config to it while `D` copies it. which pair is safe?

### mini exercise

this class hands the latest reading from a sensor thread to a consumer. find two bugs, then fix them.

```cpp complete
#include <condition_variable>
#include <mutex>

class LatestReading {
public:
    void publish(double v) { value_ = v; ready_ = true; cv_.notify_one(); }
    double wait() {
        std::unique_lock lock(m_);
        cv_.wait(lock, [&] { return ready_; });
        ready_ = false;
        return value_;
    }
private:
    std::mutex m_;
    std::condition_variable cv_;
    double value_ = 0.0;
    bool ready_ = false;
};
```

### answers

<details>
<summary>answer 1: member order and jthread</summary>

members are destroyed in reverse declaration order, so `buffer_` is destroyed first, while `worker_` is still running. the thread can write into a destroyed vector until `worker_`'s destructor requests stop and joins: UB. declare the `std::jthread` last, after everything it touches ([[jthread]]). the same rule kept [[deadlocks]]'s `ThreadPool` correct.

</details>

<details>
<summary>answer 2: locked steps are not a transaction</summary>

there is no data race: every access to the table happens under its mutex. the code is still wrong: another thread can insert the same id between `contains` and `insert`, so two threads both see "absent" and one insertion overwrites the other. that is a race condition, and the fix is an API change: a single locked `insert_if_absent` (or `try_emplace`-style) operation that checks and inserts in one critical section.

</details>

<details>
<summary>answer 3: lost wakeup</summary>

no data race, since `ready` is atomic. yes, it can hang. the consumer checks the predicate under `m` and sees `false`. before it blocks, the producer sets `ready` and calls `notify_one()`; nobody is waiting yet, so the notification is lost and the consumer sleeps forever (unless a spurious wakeup rescues it). because the producer never takes `m`, nothing orders its store between the consumer's check and its sleep. fix: `{ std::lock_guard lk(m); ready = true; } cv.notify_one();`. with the store under the mutex, `ready` can be a plain `bool` ([[condition-variables]]).

</details>

<details>
<summary>answer 4: a span handed to a thread</summary>

`std::span` borrows ([[span]]). `samples` is destroyed when `start_fft` returns, while the new thread may still be reading it: a dangling span and UB. a span is only safe to borrow across threads when the owner provably outlives the thread. fixes: move ownership into the thread (`[v = std::move(samples)] { fft(v); }`, with `fft` taking a span so the vector converts), or share immutable data with `std::shared_ptr<const std::vector<float>>` when several threads need it.

</details>

<details>
<summary>answer 5: shared_ptr and threads</summary>

`A` and `B` are safe: the reference count updates are atomic, so separate `shared_ptr` objects that share a control block may be copied and destroyed concurrently ([[shared-ptr]]). `C` and `D` are a data race on the single `g_config` object, UB. copy it under a mutex ([[mutexes]]'s snapshot pattern) or use C++20's `std::atomic<std::shared_ptr<const Config>>`. that specialization is not guaranteed to be lock-free, so measure before assuming it beats a mutex. either way, the `Config` itself is safe to read because it is `const`.

</details>

<details>
<summary>mini exercise answer</summary>

`publish` writes `value_` and `ready_` without the mutex while `wait` reads them under it: a data race, which is undefined behavior. and because the state changes outside the mutex, the notification can arrive after the consumer checked the predicate but before it went to sleep: a lost wakeup. the fix makes the state change under the same mutex, then notifies:

```cpp
void publish(double v) {
    {
        std::lock_guard lock(m_);
        value_ = v;
        ready_ = true;
    }
    cv_.notify_one();
}
```

note the policy this class implements: a second `publish` before the consumer wakes overwrites the first value, which is right for "latest reading" and wrong for anything that must not be dropped; for that, use the bounded queue.

</details>

### connections

this module was about owning threads and protecting what they share. the next one covers the other tools: futures for one-shot results, atomics and the memory model that explains every "synchronizes with" used so far, and the design rules that keep deadlocks out. underneath all of it is the same idea as [[ownership-in-interfaces]]: decide who owns each piece of state, and the synchronization follows from that decision.
