---
title: condition variables: sleeping until state changes
standard: C++17
objective: wait for shared state with a condition variable, using a predicate and the same mutex, and avoid lost and spurious wakeups
prerequisites: mutexes, jthread
difficulty: 3
---

### the idea

a detection stage hands work to a tracker thread through a mutex-protected `std::deque`. the first version of the tracker loops on `if (q.empty()) continue;`, which burns a core doing nothing. the second sleeps 1 ms between checks, which adds up to a millisecond of latency to every frame and still wakes a thousand times a second. what you actually want is "sleep until there is something to do", and that is what a condition variable provides.

### understanding the concept

a `std::condition_variable` is a wait queue tied to a mutex. `cv.wait(lock)` does two things atomically: it releases the mutex and puts the thread to sleep. when woken, it reacquires the mutex before returning. that atomicity is the whole point: there is no window between "I checked the condition" and "I am asleep" in which another thread can change the condition and notify.

two rules make it correct.

**always wait with a predicate.** waits may return without any notification (a *spurious wakeup*, explicitly allowed by the standard), and even a real notification may arrive after another thread has already consumed what you were woken for. so the condition is re-checked under the lock every time. the overload `cv.wait(lock, pred)` is exactly `while (!pred()) cv.wait(lock);`.

**modify the predicate's state while holding the same mutex.** a notification has no memory: if nobody is waiting, `notify_one()` does nothing. if the producer changes the state without the mutex, it can do so after the consumer evaluated the predicate (false) but before the consumer went to sleep. the notify finds nobody waiting, and the consumer sleeps forever. this is the *lost wakeup*, and making the flag `std::atomic` does not fix it: it removes the data race, not the window.

`std::condition_variable` works only with `std::unique_lock<std::mutex>`, because `wait` must unlock and relock it. `std::condition_variable_any` works with any lockable type, at some cost in overhead, and in C++20 it gained stop-token-aware waits.

notifying while holding the lock or right after releasing it are both correct, provided the state change happened under the lock. notifying after unlocking can avoid waking a thread that immediately blocks on the mutex you still hold (some implementations mitigate this anyway). notifying under the lock is the safer choice when a woken waiter might destroy the condition variable itself, for example by returning and ending the lifetime of the object that contains it; a notify on a destroyed condition variable is UB.

### in code

the lost wakeup, labelled:

```cpp complete
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

### in practice

not every stage should block the producer. for a planner that only cares about the newest camera frame, a single overwrite slot is the right policy. this one needs C++20 for the stop-token wait:

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

the token overload registers a stop callback that wakes the waiter, then returns the final value of the predicate. inside a `std::jthread` ([[jthread]]), this makes the blocking wait respond to the jthread's destructor without any extra close flag.

### watch out for

**waiting with `if` instead of a predicate.**

```cpp
std::unique_lock lock(m);
if (!ready) cv.wait(lock);   // BUG: a spurious wakeup returns with ready still false
use_result();
```

the standard allows `wait` to return without any notification, and a real notification may be consumed by another waiter first. code that checks the condition once and then trusts the wakeup works in testing and fails rarely in production. the predicate overload, `cv.wait(lock, [&] { return ready; })`, loops for you, and there is no good reason to call the bare `wait` in new code.

### the takeaway

a condition variable is not a signal; it is a way to sleep until shared state changes. change that state under the mutex, and always wait with a predicate.

### optional challenge

`cv.wait(lock)` takes the lock as an argument and releases it internally. what would go wrong if the API instead asked you to unlock the mutex yourself and then call a `wait()` that only sleeps?

<details>
<summary>answer</summary>

there would be a window between your `unlock()` and the start of the sleep. a producer could take the mutex in that window, change the state, and notify, and the notification would find nobody waiting yet. the consumer would then go to sleep after the event it was waiting for: the lost wakeup, built into the API. `wait` releases the mutex and blocks as one atomic step with respect to notifications, which is the entire reason it needs the lock.

</details>
