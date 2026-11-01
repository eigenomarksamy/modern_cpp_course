---
title: observability: logs, metrics, and traces
standard: C++20
objective: instrument production code with structured logs, cheap metrics, and spans, without letting the instrumentation disturb the code it observes
prerequisites: testing, atomics, raii
difficulty: 2
---

### the idea

tests tell you the code did what you expected on inputs you thought of. observability tells you what it did in production on inputs you did not think of. a team with only the first ships bugs it cannot diagnose; a team with only the second diagnoses the same bug every week. both are design concerns, and both are cheaper when the code was built for them.

### understanding the concept

**observability** has three complementary signals:

- **logs**: discrete events with context. make them structured (`key=value` or JSON) so machines can query them.
- **metrics**: cheap numeric aggregates (counters, gauges, histograms), exported periodically. they answer "how often" and "how slow" without storing every event.
- **traces**: timed spans with parent/child relationships, showing where one request or frame spent its time across stages and threads.

### in code

structured logging, where the interesting part is what a disabled log costs:

```cpp
#include <atomic>
#include <initializer_list>

enum class Level { debug, info, warn, error };
inline std::atomic<Level> g_level{Level::info};       // adjustable at runtime

struct Field { std::string_view key; double value; };

void log_event(Level lvl, std::string_view event, std::initializer_list<Field> fields,
               std::source_location loc = std::source_location::current()) {
    if (lvl < g_level.load(std::memory_order_relaxed)) return;
    std::fprintf(stderr, "level=%d event=%.*s", static_cast<int>(lvl),
                 static_cast<int>(event.size()), event.data());
    for (const Field& f : fields)
        std::fprintf(stderr, " %.*s=%g", static_cast<int>(f.key.size()), f.key.data(), f.value);
    std::fprintf(stderr, " src=%s:%u\n", loc.file_name(), static_cast<unsigned>(loc.line()));
}

// The arguments of a disabled log_event() call are still evaluated. The macro checks first.
#define LOG_DEBUG(event, ...)                                                   \
    do {                                                                        \
        if (g_level.load(std::memory_order_relaxed) <= Level::debug)            \
            log_event(Level::debug, event, __VA_ARGS__);                        \
    } while (0)

// LOG_DEBUG("cycle", {{"residual", compute_residual()}});
// prints nothing at level info, and compute_residual() is never called
```

this is one of the few places where a macro still earns its keep: a function cannot avoid evaluating its arguments. if debug logs must cost nothing at all in release builds, add a compile-time floor (`if constexpr (kMinCompiledLevel <= Level::debug)`) so the code is not even generated; the tradeoff is that you cannot turn those logs on in the field without a rebuild. in a C++20 codebase with a newer toolchain, you would format with `std::format` ([[format]]) rather than `printf`.

metrics and spans, built so they are safe to use inside a control loop:

```cpp
#include <algorithm>
#include <array>
#include <bit>

class LatencyHistogram {          // log2 buckets in microseconds: [0,1), [1,2), [2,4), ...
public:
    static constexpr std::size_t kBuckets = 24;
    void record(std::chrono::nanoseconds d) {
        const auto us = static_cast<std::uint64_t>(std::max<std::int64_t>(d.count(), 0) / 1000);
        const auto b = std::min<std::size_t>(std::bit_width(us), kBuckets - 1);
        counts_[b].fetch_add(1, std::memory_order_relaxed);   // no lock, no allocation
    }
    std::uint64_t count(std::size_t b) const { return counts_[b].load(std::memory_order_relaxed); }
private:
    std::array<std::atomic<std::uint64_t>, kBuckets> counts_{};
};

class ScopeTimer {                                    // a tracing span in miniature: RAII again
public:
    explicit ScopeTimer(LatencyHistogram& h) : h_(h), start_(std::chrono::steady_clock::now()) {}
    ~ScopeTimer() { h_.record(std::chrono::steady_clock::now() - start_); }
    ScopeTimer(const ScopeTimer&) = delete;
    ScopeTimer& operator=(const ScopeTimer&) = delete;
private:
    LatencyHistogram& h_;
    std::chrono::steady_clock::time_point start_;
};

// void control_cycle() { ScopeTimer span(g_cycle_latency); /* ... */ }
```

relaxed ordering is correct here because each counter is independent and nothing else is published through it ([[memory-model]]). a reporter thread reads the buckets periodically and exports them; the control loop only ever does one `fetch_add`.

### in practice

on the robot, each pipeline stage has a latency histogram, a dropped-frame counter, and a span per frame. when an operator reports "the arm hesitated at 14:02", the team pulls the spans for that minute and sees the planner stage at its p99.9 while a log shows a map reload: a diagnosis in minutes instead of a week of trying to reproduce it.

### watch out for

observability code runs in the paths you are trying to observe, so it can cause the problems it is meant to find. writing a log line can allocate ([[allocation-costs]]), take a lock inside the logging library, and block on I/O when the disk or the network is slow. inside a 1 kHz control loop, or while holding a mutex ([[deadlocks]]), that turns a diagnostic into a deadline miss or a convoy of blocked threads. keep hot paths to counters and fixed-size records: push events into a preallocated lock-free ring buffer and let a background thread format and write them, rate-limit repeated messages, and never log while holding a lock you share with a latency-critical thread.

### the takeaway

design for "what is it doing?" from the start: structured logs for events, counters and histograms for rates and latencies, spans for where time went, all built so that observing the system does not change it.

### optional challenge

with `LatencyHistogram`'s log2 buckets, which bucket does a 5 µs cycle land in, and which does a 1 ms cycle land in? what does that bucketing make easy, and what does it give up?

<details>
<summary>answer</summary>

5 µs: `std::bit_width(5)` is 3, so bucket 3, covering [4, 8) µs. 1 ms is 1000 µs: `std::bit_width(1000)` is 10, so bucket 10, covering [512, 1024) µs. log2 buckets cover microseconds to seconds with a couple of dozen counters and one cheap instruction per record, which is what makes them safe in a control loop, and percentiles such as p99 can be estimated from them. what they give up is resolution: within a bucket, 520 µs and 1000 µs are indistinguishable, so a regression from 600 to 900 µs is invisible. finer buckets (or several sub-buckets per power of two) trade memory for precision.

</details>
