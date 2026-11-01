---
title: a bounded producer-consumer queue
standard: C++17
objective: build a bounded blocking queue with clean shutdown, and choose a back-pressure policy deliberately
prerequisites: condition-variables, optional
difficulty: 2
---

### the idea

every pipeline whose stages run at different speeds needs a buffer between them, and the interesting part of that buffer is not where items go but what happens when it fills up. block the producer, drop the oldest item, drop the newest, or grow without limit: each is a decision about latency, memory, and data loss, and an unbounded queue is the one that makes the decision silently and fails in the field.

### understanding the concept

a bounded blocking queue has a small, complete contract: `push` waits while the queue is full, `pop` waits while it is empty, and `close` ends the conversation, waking every waiter so that producers stop and consumers drain what is left. two conditions are waited on ("not full" and "not empty"), so the queue uses two condition variables over one mutex. the class is the unit of synchronization: the mutex, both condition variables, and the state they guard are private, and every public operation is one complete transaction.

### in code

the queue: a bounded blocking queue with shutdown. `push` blocks when full, `pop` blocks when empty, and `close` wakes everyone:

```cpp complete
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

a consumer is just `while (auto d = queue.pop()) track(*d);`, and it exits cleanly after `close()` once the queue is drained. returning `std::optional` ([[optional]]) makes "no more items" part of the type instead of a sentinel. notice that the class is the unit of synchronization: the mutex, both condition variables, and the state they guard are private, and every public operation is one complete transaction ([[mutexes]]).

### in practice

back-pressure is a design decision, and the queue is where you make it explicit. in a radar chain, every detection matters for the tracker, so a bounded queue that blocks the detector is reasonable: when the tracker falls behind, the slowdown propagates upstream, and memory stays bounded. for a camera feeding a planner, a frame that is 200 ms old is worse than no frame, so drop-oldest (the `LatestSlot` above, or a ring buffer that overwrites) is the right policy. telemetry export sits in between: bounded, drop newest, and count what you dropped.

what you should almost never ship is an *unbounded* queue between stages with different throughput. it does not remove overload, it hides it until the process runs out of memory, usually in the field. whatever policy you pick, export the queue depth and drop counts as metrics: they are the first thing you will want when the pipeline misbehaves.

### watch out for

producers and consumers sharing one condition variable. if both "not full" and "not empty" waiters sleep on the same `cv`, a `notify_one()` intended for a consumer can wake a producer instead. that producer re-checks its predicate, finds it still false, and goes back to sleep; the notification is used up, and the consumer that should have run keeps sleeping. the program can stall with items in the queue. the fix is either one condition variable per condition (as in `BoundedQueue`) or `notify_all()` on a shared one, which is correct but wakes everyone. the same reasoning is why `close()` uses `notify_all()`: every waiter must observe `closed_`.

### the takeaway

decide deliberately what happens when the producer is faster than the consumer, make that policy explicit in the queue's type, and measure its depth and drops in production.

### optional challenge

after the wait in `pop()`, why does the code test `q_.empty()` rather than `closed_`? what would change if it returned `std::nullopt` whenever `closed_` is true?

<details>
<summary>answer</summary>

testing `q_.empty()` gives drain-on-close semantics: items pushed before `close()` are still delivered, and `pop()` reports the end only when the queue is both closed and empty. if it returned on `closed_`, any items still queued at shutdown would be silently discarded, so a final batch of detections or log records would be lost. sometimes that is what you want (a fast abort), but then it should be a separate, explicitly named operation, not an accident of the predicate.

</details>
