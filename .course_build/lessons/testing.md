---
title: testing that catches real bugs
standard: C++20
objective: structure tests by the test pyramid, test behavior through injected seams, and add property tests, fuzzing, and sanitizer builds where they pay off
prerequisites: test-seams, cpp20-small-features
difficulty: 2
---

### the idea

tests tell you the code did what you expected on inputs you thought of. the useful questions are which inputs, at which level, and against what: a test that pins down the exact boundary of a watchdog's timeout catches more bugs than a dozen tests of the happy path, and a test that asserts how a function did its job breaks on every refactor while catching nothing.

### understanding the concept

**the test pyramid, in C++ terms.** at the base, many fast unit tests that run in milliseconds and need no hardware: pure functions, classes with injected dependencies ([[dependency-injection]]). in the middle, integration tests: several real components wired together, perhaps over loopback sockets or by replaying recorded sensor data. at the top, few and expensive: hardware-in-the-loop (the real controller board driving a simulated plant) and field tests. push each check as low as it can go; a bug found by a unit test costs seconds, one found on the robot costs a day.

**test behavior, not implementation.** a test that asserts "the planner called `compute_cost` 14 times" breaks on every refactor and catches nothing. a test that asserts "the planned path never enters the keep-out zone" survives refactors and catches real bugs. mocks that verify call sequences are right only when the call is the behavior (the actuator command was sent exactly once).

**beyond examples.** property-based tests generate many inputs and check an invariant: `parse(serialize(msg)) == msg`, or "the filter output stays within sensor bounds". fuzzing (libFuzzer, AFL++) mutates inputs guided by code coverage, and is the most effective tool we have for parsers of untrusted bytes. sanitizers ([[ub-usual-suspects]]) turn silent undefined behavior into loud test failures, but they need separate builds: AddressSanitizer and ThreadSanitizer cannot be combined in one binary, while ASan and UBSan usually can.

### in code

a deterministic unit test with the fake clock from [[dependency-injection]], using `std::source_location` (C++20) for failure locations instead of a macro:

```cpp complete
#include <chrono>
#include <cstdio>
#include <source_location>
#include <string_view>

using namespace std::chrono_literals;
using TimePoint = std::chrono::steady_clock::time_point;

struct Clock {                                        // the seam from dependency injection
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

no sleeps, no flakiness, and the boundary (exactly 100 ms) is pinned down, which is where the bugs live. the default argument `std::source_location::current()` is evaluated at the call site, so the failure reports the line of the `check`, not of its definition. in a real project you would use GoogleTest (`EXPECT_TRUE`) or Catch2 (`CHECK`); the test's shape is the same.

### in practice

a robotics team's CI runs a matrix rather than one build:

```text
release        -O2              unit + integration tests, benchmarks
asan+ubsan     -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer
tsan           -O1 -g -fsanitize=thread         concurrency tests, repeated
fuzz (nightly) clang++ -fsanitize=fuzzer,address    the telemetry parser
```

the fuzz target is a single function the fuzzer calls with mutated bytes:

```cpp external
extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t* data, std::size_t size) {
    parse_nmea_sentence(std::string_view(reinterpret_cast<const char*>(data), size));
    return 0;   // crashes, sanitizer reports, and timeouts are the failures
}
```

### watch out for

**tests that sleep.** the tempting way to test a timeout uses real time:

```cpp
Watchdog dog(system_clock_adapter, 100ms);
std::this_thread::sleep_for(150ms);
check(dog.expired(), "trips after the timeout");   // slow, and flaky on a loaded CI machine
```

every such test adds real seconds to the suite, and the margins that make it pass on a laptop fail on a busy CI runner, where the thread may be descheduled for longer than the margin. it also cannot test the exact boundary. inject the clock and advance it explicitly, as the fake-clock test above does: the test becomes instant, deterministic, and precise.

### the takeaway

push each check as low in the pyramid as it can go, test behavior rather than call sequences, inject time and I/O so tests are deterministic, and let sanitizers and fuzzers search the inputs you did not think of.

### optional challenge

you add a helper `void check_near(double a, double b, double tol) { check(std::abs(a - b) <= tol, "near"); }` and use it across many tests. failures now all report the same line. why, and how do you fix it without a macro?

<details>
<summary>answer</summary>

`std::source_location::current()` as a default argument is evaluated where the call to `check` is written, which is now inside `check_near`, so every failure points at the helper. give the helper the same defaulted parameter and forward it: `void check_near(double a, double b, double tol, std::source_location loc = std::source_location::current()) { check(std::abs(a - b) <= tol, "near", loc); }`. each test's call site now fills in its own location, and `check` reports it. this forwarding is how test frameworks and logging libraries built on `source_location` pass the caller's location through layers of helpers.

</details>
