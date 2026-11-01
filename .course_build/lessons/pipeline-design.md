---
title: putting it together, part 1: values, messages, and the queue
standard: C++20
objective: see the course's ideas combine in one small program, starting with value types, a closed message set, and a closable bounded queue
prerequisites: blocking-queue, variant, defaulted-comparisons, architecture-decisions
difficulty: 2
---

### the idea

each lesson so far isolated one idea. real code is where the ideas meet and pull against each other: the queue wants ownership to move, the processing stage wants to borrow, the test wants seams, and shutdown wants all of it to unwind in the right order. the next three lessons build one small program, about 160 lines in four parts that compile together with `-std=c++20`, and review every decision in it.

### understanding the concept

the shape is a classic two-stage pipeline:

```text
 source (fake sensor)          bounded queue            consumer thread
 producer jthread  ---push--->  [ Message x 8 ]  ---pop--->  Processor<Sink>
                                                              gate(span) -> sink.on_frame(span)
```

a producer thread pulls `Message`s (a frame of detections or a sensor fault) from an injected source and pushes them into a bounded queue. a consumer thread pops them, gates each frame's detections (drop weak and distant returns, sort strongest first), and hands the result to an injected sink. ownership flows one way: a `Frame` is created by the source, moved through the queue, and owned by exactly one stage at a time. the sink only borrows the result.

### in code

part 1 defines the vocabulary: a value type and a closed set of messages.

```cpp group=pipeline
// part 1: values and messages
#include <algorithm>
#include <cassert>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <deque>
#include <functional>
#include <mutex>
#include <optional>
#include <ranges>
#include <span>
#include <stop_token>
#include <thread>
#include <utility>
#include <variant>
#include <vector>

struct Detection {
    double range_m{}, azimuth_rad{}, snr_db{};
    bool operator==(const Detection&) const = default;  // equality yes, ordering no
};
struct Frame { std::uint64_t seq{}; std::vector<Detection> detections; };
struct SensorFault { std::uint64_t seq{}; int code{}; };
using Message = std::variant<Frame, SensorFault>;

template <typename... Fs> struct overloaded : Fs... { using Fs::operator()...; };
```

part 2 is the queue from [[blocking-queue]], with close semantics so shutdown never leaves a thread blocked forever.

```cpp group=pipeline
// part 2: a bounded, closable queue
template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {}
    bool push(T item) {                      // blocks while full; false once closed
        std::unique_lock lock(m_);
        not_full_.wait(lock, [&] { return closed_ || q_.size() < capacity_; });
        if (closed_) return false;
        q_.push_back(std::move(item));
        not_empty_.notify_one();
        return true;
    }
    std::optional<T> pop() {                 // blocks while empty; nullopt once closed and drained
        std::unique_lock lock(m_);
        not_empty_.wait(lock, [&] { return closed_ || !q_.empty(); });
        std::optional<T> item;
        if (!q_.empty()) {
            item.emplace(std::move(q_.front()));
            q_.pop_front();
            not_full_.notify_one();
        }
        return item;
    }
    void close() {
        { std::lock_guard lock(m_); closed_ = true; }
        not_full_.notify_all(); not_empty_.notify_all();
    }
private:
    std::mutex m_;
    std::condition_variable not_full_, not_empty_;
    std::deque<T> q_;
    std::size_t capacity_;
    bool closed_ = false;
};
```

### in practice

the design review for these two parts. every row is a decision someone could reasonably have made differently:

| decision | alternative | why this one |
|---|---|---|
| `Detection` defaults `==` only | also default `<=>` | `double` members give only `partial_ordering`, and detections have no natural order; sort by an explicit projection instead ([[defaulted-comparisons]]) |
| `Message` is a `std::variant` | base class with virtual `handle()` | closed set, value semantics, no allocation per message; a missing case in the visitor fails to compile ([[variant]]) |
| bounded queue, producer blocks | unbounded queue, or drop-oldest | back-pressure bounds memory and latency; a sensor that cannot wait would need drop-oldest instead ([[blocking-queue]]) |

### watch out for

**`Detection` deliberately has no ordering.** it would be easy to default `operator<=>` along with `operator==`, and then `std::sort(detections)` would compile. but a detection has no natural order (by range? by strength? by azimuth?), and with `double` members the defaulted ordering is only partial, so NaN would make such a sort undefined. leaving `<=>` out forces every sort to name its key with a projection, which is both safer and clearer at the call site.

### the takeaway

start an integrated design from its values and its messages: small value types with only the operations that mean something, a closed variant for what flows between stages, and a queue whose policy for "full" and "closed" is explicit.

### optional challenge

`BoundedQueue::pop` here notifies `not_full_` while still holding the lock, while the version in [[blocking-queue]] unlocks first. is either one wrong?

<details>
<summary>answer</summary>

neither is wrong. notifying under the lock or right after releasing it are both correct, as long as the state change happened under the lock. notifying after unlocking can save a woken producer from immediately blocking on the mutex the consumer still holds; notifying under the lock is simpler to reason about and safe even if a woken thread might destroy the condition variable. here, `close()` and the queue's lifetime are controlled by the pipeline, so either choice is fine; consistency within one class matters more than the choice.

</details>
