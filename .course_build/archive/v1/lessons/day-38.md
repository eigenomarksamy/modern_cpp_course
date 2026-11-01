<a id="day-38"></a>

## day 38: condition variables and the producer-consumer queue

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 24, 36, 37

### the idea

A detection stage hands work to a tracker thread through a mutex-protected `std::deque`. The first version of the tracker loops on `if (q.empty()) continue;`, which burns a core doing nothing. The second sleeps 1 ms between checks, which adds up to a millisecond of latency to every frame and still wakes a thousand times a second. What you actually want is "sleep until there is something to do", and that is what a condition variable provides.

### understanding the concept

A `std::condition_variable` is a wait queue tied to a mutex. `cv.wait(lock)` does two things atomically: it releases the mutex and puts the thread to sleep. When woken, it reacquires the mutex before returning. That atomicity is the whole point: there is no window between "I checked the condition" and "I am asleep" in which another thread can change the condition and notify.

Two rules make it correct.

**Always wait with a predicate.** Waits may return without any notification (a *spurious wakeup*, explicitly allowed by the standard), and even a real notification may arrive after another thread has already consumed what you were woken for. So the condition is re-checked under the lock every time. The overload `cv.wait(lock, pred)` is exactly `while (!pred()) cv.wait(lock);`.

**Modify the predicate's state while holding the same mutex.** A notification has no memory: if nobody is waiting, `notify_one()` does nothing. If the producer changes the state without the mutex, it can do so after the consumer evaluated the predicate (false) but before the consumer went to sleep. The notify finds nobody waiting, and the consumer sleeps forever. This is the *lost wakeup*, and making the flag `std::atomic` does not fix it: it removes the data race, not the window.

`std::condition_variable` works only with `std::unique_lock<std::mutex>`, because `wait` must unlock and relock it. `std::condition_variable_any` works with any lockable type, at some cost in overhead, and in C++20 it gained stop-token-aware waits.

Notifying while holding the lock or right after releasing it are both correct, provided the state change happened under the lock. Notifying after unlocking can avoid waking a thread that immediately blocks on the mutex you still hold (some implementations mitigate this anyway). Notifying under the lock is the safer choice when a woken waiter might destroy the condition variable itself, for example by returning and ending the lifetime of the object that contains it; a notify on a destroyed condition variable is UB.

### in code

The lost wakeup, labelled:

```cpp
#include <atomic>
#include <condition_variable>
#include <mutex>

std::mutex m;
std::condition_variable cv;
std::atomic<bool> ready{false};

void producer_buggy() {
    ready = true;            // BUG: not under m; the consumer may be between
    cv.notify_one();         // its predicate check and its sleep: wakeup lost
}

void producer() {
    {
        std::lock_guard lock(m);
        ready = true;        // a plain bool would now be enough
    }
    cv.notify_one();
}

void consumer() {
    std::unique_lock lock(m);
    cv.wait(lock, [] { return ready.load(); });
    // ready is true here, and m is held again
}
```

Now the workhorse of this week, a bounded blocking queue with shutdown. `push` blocks when full, `pop` blocks when empty, and `close` wakes everyone:

```cpp
#include <condition_variable>
#include <cstddef>
#include <deque>
#include <mutex>
#include <optional>

template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {}  // capacity > 0

    bool push(T item) {                                  // false if closed
        std::unique_lock lock(m_);
        not_full_.wait(lock, [&] { return closed_ || q_.size() < capacity_; });
        if (closed_) return false;
        q_.push_back(std::move(item));
        lock.unlock();
        not_empty_.notify_one();
        return true;
    }

    std::optional<T> pop() {                             // nullopt: closed and drained
        std::unique_lock lock(m_);
        not_empty_.wait(lock, [&] { return closed_ || !q_.empty(); });
        if (q_.empty()) return std::nullopt;
        std::optional<T> item(std::move(q_.front()));
        q_.pop_front();
        lock.unlock();
        not_full_.notify_one();
        return item;
    }

    void close() {
        { std::lock_guard lock(m_); closed_ = true; }
        not_full_.notify_all();                          // every waiter must re-check
        not_empty_.notify_all();
    }

private:
    std::mutex m_;
    std::condition_variable not_full_, not_empty_;
    std::deque<T> q_;
    std::size_t capacity_;
    bool closed_ = false;
};
```

A consumer is just `while (auto d = queue.pop()) track(*d);`, and it exits cleanly after `close()` once the queue is drained. Returning `std::optional` (day 24) makes "no more items" part of the type instead of a sentinel. Notice that the class is the unit of synchronization: the mutex, both condition variables, and the state they guard are private, and every public operation is one complete transaction (day 37).

Not every stage should block the producer. For a planner that only cares about the newest camera frame, a single overwrite slot is the right policy. This one needs C++20 for the stop-token wait:

```cpp
// C++20: condition_variable_any::wait(lock, stop_token, pred)
#include <condition_variable>
#include <mutex>
#include <optional>
#include <stop_token>
#include <utility>

template <typename T>
class LatestSlot {                     // producer never blocks; stale values are dropped
public:
    void publish(T v) {
        { std::lock_guard lock(m_); value_ = std::move(v); }
        cv_.notify_one();
    }
    std::optional<T> wait_next(std::stop_token st) {
        std::unique_lock lock(m_);
        if (!cv_.wait(lock, st, [&] { return value_.has_value(); }))
            return std::nullopt;       // woken by a stop request, nothing to return
        return std::exchange(value_, std::nullopt);
    }
private:
    std::mutex m_;
    std::condition_variable_any cv_;
    std::optional<T> value_;
};
```

The token overload registers a stop callback that wakes the waiter, then returns the final value of the predicate. Inside a `std::jthread` (day 36), this makes the blocking wait respond to the jthread's destructor without any extra close flag.

### in practice

Back-pressure is a design decision, and the queue is where you make it explicit. In a radar chain, every detection matters for the tracker, so a bounded queue that blocks the detector is reasonable: when the tracker falls behind, the slowdown propagates upstream, and memory stays bounded. For a camera feeding a planner, a frame that is 200 ms old is worse than no frame, so drop-oldest (the `LatestSlot` above, or a ring buffer that overwrites) is the right policy. Telemetry export sits in between: bounded, drop newest, and count what you dropped.

What you should almost never ship is an *unbounded* queue between stages with different throughput. It does not remove overload, it hides it until the process runs out of memory, usually in the field. Whatever policy you pick, export the queue depth and drop counts as metrics: they are the first thing you will want when the pipeline misbehaves.

### watch out for

Producers and consumers sharing one condition variable. If both "not full" and "not empty" waiters sleep on the same `cv`, a `notify_one()` intended for a consumer can wake a producer instead. That producer re-checks its predicate, finds it still false, and goes back to sleep; the notification is used up, and the consumer that should have run keeps sleeping. The program can stall with items in the queue. The fix is either one condition variable per condition (as in `BoundedQueue`) or `notify_all()` on a shared one, which is correct but wakes everyone. The same reasoning is why `close()` uses `notify_all()`: every waiter must observe `closed_`.

### the takeaway

A condition variable is not a signal, it is a way to sleep until shared state changes. Guard that state with the mutex, wait with a predicate, and decide deliberately what happens when the producer is faster than the consumer.

### optional challenge

After the wait in `pop()`, why does the code test `q_.empty()` rather than `closed_`? What would change if it returned `std::nullopt` whenever `closed_` is true?

<details>
<summary>answer</summary>

Testing `q_.empty()` gives drain-on-close semantics: items pushed before `close()` are still delivered, and `pop()` reports the end only when the queue is both closed and empty. If it returned on `closed_`, any items still queued at shutdown would be silently discarded, so a final batch of detections or log records would be lost. Sometimes that is what you want (a fast abort), but then it should be a separate, explicitly named operation, not an accident of the predicate.

</details>
