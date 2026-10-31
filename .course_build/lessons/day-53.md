<a id="day-53"></a>

## day 53: testing and observability

**reading time:** about 10 minutes · **standard:** C++20 · **builds on:** days 06, 08, 34, 41, 44

### the idea

Tests tell you the code did what you expected on inputs you thought of. Observability tells you what it did in production on inputs you did not think of. A team with only the first ships bugs it cannot diagnose; a team with only the second diagnoses the same bug every week. Both are design concerns, and both are cheaper when the code was built for them.

### understanding the concept

**The test pyramid, in C++ terms.** At the base, many fast unit tests that run in milliseconds and need no hardware: pure functions, classes with injected dependencies (day 44). In the middle, integration tests: several real components wired together, perhaps over loopback sockets or by replaying recorded sensor data. At the top, few and expensive: hardware-in-the-loop (the real controller board driving a simulated plant) and field tests. Push each check as low as it can go; a bug found by a unit test costs seconds, one found on the robot costs a day.

**Test behavior, not implementation.** A test that asserts "the planner called `compute_cost` 14 times" breaks on every refactor and catches nothing. A test that asserts "the planned path never enters the keep-out zone" survives refactors and catches real bugs. Mocks that verify call sequences are right only when the call is the behavior (the actuator command was sent exactly once).

**Beyond examples.** Property-based tests generate many inputs and check an invariant: `parse(serialize(msg)) == msg`, or "the filter output stays within sensor bounds". Fuzzing (libFuzzer, AFL++) mutates inputs guided by code coverage, and is the most effective tool we have for parsers of untrusted bytes. Sanitizers (day 06) turn silent undefined behavior into loud test failures, but they need separate builds: AddressSanitizer and ThreadSanitizer cannot be combined in one binary, while ASan and UBSan usually can.

**Observability** has three complementary signals:

- **logs**: discrete events with context. Make them structured (`key=value` or JSON) so machines can query them.
- **metrics**: cheap numeric aggregates (counters, gauges, histograms), exported periodically. They answer "how often" and "how slow" without storing every event.
- **traces**: timed spans with parent/child relationships, showing where one request or frame spent its time across stages and threads.

### in code

A deterministic unit test with the fake clock from day 44, using `std::source_location` (C++20) for failure locations instead of a macro:

```cpp
#include <chrono>
#include <cstdio>
#include <source_location>
#include <string_view>

using namespace std::chrono_literals;
using TimePoint = std::chrono::steady_clock::time_point;

struct Clock {                                        // the seam from day 44
    virtual ~Clock() = default;
    virtual TimePoint now() const = 0;
};

class Watchdog {                                      // trips if heartbeats stop
public:
    Watchdog(const Clock& clock, std::chrono::milliseconds timeout)
        : clock_(clock), timeout_(timeout), last_(clock.now()) {}
    void heartbeat() { last_ = clock_.now(); }
    bool expired() const { return clock_.now() - last_ > timeout_; }
private:
    const Clock& clock_;
    std::chrono::milliseconds timeout_;
    TimePoint last_;
};

struct FakeClock final : Clock {                      // a fake: real behavior, controlled time
    TimePoint t{};
    TimePoint now() const override { return t; }
};

int g_failures = 0;
void check(bool ok, std::string_view what,
           std::source_location loc = std::source_location::current()) {
    if (ok) return;
    ++g_failures;
    std::printf("%s:%u: FAILED: %.*s\n", loc.file_name(), static_cast<unsigned>(loc.line()),
                static_cast<int>(what.size()), what.data());
}

void test_watchdog_trips_only_after_timeout() {
    FakeClock clock;
    Watchdog dog(clock, 100ms);
    clock.t += 100ms;
    check(!dog.expired(), "exactly at the timeout it is still alive");
    clock.t += 1ms;
    check(dog.expired(), "trips once the timeout has passed");
    dog.heartbeat();
    check(!dog.expired(), "a heartbeat re-arms it");
}
```

No sleeps, no flakiness, and the boundary (exactly 100 ms) is pinned down, which is where the bugs live. The default argument `std::source_location::current()` is evaluated at the call site, so the failure reports the line of the `check`, not of its definition. In a real project you would use GoogleTest (`EXPECT_TRUE`) or Catch2 (`CHECK`); the test's shape is the same.

Structured logging, where the interesting part is what a disabled log costs:

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

This is one of the few places where a macro still earns its keep: a function cannot avoid evaluating its arguments. If debug logs must cost nothing at all in release builds, add a compile-time floor (`if constexpr (kMinCompiledLevel <= Level::debug)`) so the code is not even generated; the tradeoff is that you cannot turn those logs on in the field without a rebuild. In a C++20 codebase with a newer toolchain, you would format with `std::format` (day 34) rather than `printf`.

Metrics and spans, built so they are safe to use inside a control loop:

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

class ScopeTimer {                                    // a tracing span in miniature (day 08)
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

Relaxed ordering is correct here because each counter is independent and nothing else is published through it (day 40). A reporter thread reads the buckets periodically and exports them; the control loop only ever does one `fetch_add`.

### in practice

A robotics team's CI runs a matrix rather than one build:

```text
release        -O2              unit + integration tests, benchmarks (day 50)
asan+ubsan     -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer
tsan           -O1 -g -fsanitize=thread         concurrency tests, repeated
fuzz (nightly) clang++ -fsanitize=fuzzer,address    the telemetry parser
```

The fuzz target is a single function the fuzzer calls with mutated bytes:

```cpp
extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t* data, std::size_t size) {
    parse_nmea_sentence(std::string_view(reinterpret_cast<const char*>(data), size));
    return 0;   // crashes, sanitizer reports, and timeouts are the failures
}
```

On the robot, each pipeline stage has a latency histogram, a dropped-frame counter, and a span per frame. When an operator reports "the arm hesitated at 14:02", the team pulls the spans for that minute and sees the planner stage at its p99.9 while a log shows a map reload: a diagnosis in minutes instead of a week of trying to reproduce it.

### watch out for

Observability code runs in the paths you are trying to observe, so it can cause the problems it is meant to find. Writing a log line can allocate (day 52), take a lock inside the logging library, and block on I/O when the disk or the network is slow. Inside a 1 kHz control loop, or while holding a mutex (day 41), that turns a diagnostic into a deadline miss or a convoy of blocked threads. Keep hot paths to counters and fixed-size records: push events into a preallocated lock-free ring buffer and let a background thread format and write them, rate-limit repeated messages, and never log while holding a lock you share with a latency-critical thread.

### the takeaway

Design for both questions from the start: deterministic tests through injected seams for "does it work", and cheap, structured logs, metrics, and spans for "what is it doing", built so that observing the system does not change it.

### optional challenge

You add a helper `void check_near(double a, double b, double tol) { check(std::abs(a - b) <= tol, "near"); }` and use it across many tests. Failures now all report the same line. Why, and how do you fix it without a macro?

<details>
<summary>answer</summary>

`std::source_location::current()` as a default argument is evaluated where the call to `check` is written, which is now inside `check_near`, so every failure points at the helper. Give the helper the same defaulted parameter and forward it: `void check_near(double a, double b, double tol, std::source_location loc = std::source_location::current()) { check(std::abs(a - b) <= tol, "near", loc); }`. Each test's call site now fills in its own location, and `check` reports it. This forwarding is how test frameworks and logging libraries built on `source_location` pass the caller's location through layers of helpers.

</details>
