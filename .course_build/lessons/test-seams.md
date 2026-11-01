---
title: choosing a seam: interfaces, templates, functions, and the linker
standard: C++20
objective: choose between a virtual interface, a constrained template, `std::function`, and a link-time seam by when the decision is made and what it costs
prerequisites: dependency-injection, writing-concepts, callbacks
difficulty: 2
---

### the idea

once a class receives its collaborators, a second question remains: what *type* is the parameter? a virtual interface, a template parameter, a `std::function`, or nothing at all, with the substitution happening in the linker. all four make the code testable. they differ in when the choice is made, what it costs at run time, and how much of the decision is visible when you read the code.

### understanding the concept

a **seam** is a place where you can change what code does without editing that code. dependency injection creates seams deliberately. in C++ you have four main kinds, and they differ in when the choice is made:

| seam | chosen at | cost and constraints | good for |
|---|---|---|---|
| virtual interface, injected via constructor | run time | indirect call, usually not inlined; needs an interface type and a lifetime decision | hardware, I/O, plugins, anything chosen from config |
| template parameter (constrained by a concept) | compile time | no indirection; code lives in headers, each instantiation is separate code, longer builds | hot paths, header-only utilities, policies |
| `std::function` | run time | type erasure: indirect call, may allocate for large callables ([[callbacks]]) | single callbacks: a time source, a log sink |
| link-time | link time | one implementation per binary; invisible in the source | replacing a platform function (time, GPIO) in a test binary |

### in code

**compile-time injection with a concept (C++20).** when the dependency is fixed per build and sits on a hot path, make it a template parameter. the concept documents what the dependency must provide and gives readable errors ([[writing-concepts]]).

```cpp complete
#include <chrono>
#include <concepts>
#include <optional>

template <typename C>
concept SteadyTimeSource = requires(const C& c) {
    { c.now() } -> std::same_as<std::chrono::steady_clock::time_point>;
};

template <SteadyTimeSource Clock>
class RateLimiter {
public:
    RateLimiter(Clock clock, std::chrono::nanoseconds min_gap)
        : clock_(std::move(clock)), gap_(min_gap) {}

    bool allow() {
        const auto t = clock_.now();
        if (last_ && t - *last_ < gap_) return false;
        last_ = t;
        return true;
    }

private:
    Clock clock_;
    std::chrono::nanoseconds gap_;
    std::optional<std::chrono::steady_clock::time_point> last_;
};

struct SystemSteadyClock {                       // production
    auto now() const { return std::chrono::steady_clock::now(); }
};
struct ManualClock {                             // test: reads a time the test controls
    const std::chrono::steady_clock::time_point* t;
    auto now() const { return *t; }
};

// usage in a test:
//   std::chrono::steady_clock::time_point now{};
//   RateLimiter limiter(ManualClock{&now}, 100ms);    // CTAD picks ManualClock
//   limiter.allow();  // true
//   now += 50ms;  limiter.allow();  // false
//   now += 60ms;  limiter.allow();  // true
```

no interface, no virtual call, and `SystemSteadyClock` is an empty class (it still occupies at least one byte as a member; `[[no_unique_address]]` in C++20 can remove that). the price is that `RateLimiter<ManualClock>` and `RateLimiter<SystemSteadyClock>` are different types, so you cannot store both in one container or choose between them from a config file.

**a `std::function` seam** is the lightest runtime option when the dependency is a single operation:

```cpp
#include <functional>

using TimeSource = std::function<std::chrono::steady_clock::time_point()>;

class Watchdog {
public:
    explicit Watchdog(TimeSource now = [] { return std::chrono::steady_clock::now(); })
        : now_(std::move(now)), last_kick_(now_()) {}
    void kick() { last_kick_ = now_(); }
    bool expired(std::chrono::milliseconds limit) const { return now_() - last_kick_ > limit; }
private:
    TimeSource now_;
    std::chrono::steady_clock::time_point last_kick_;
};
```

### in practice

**link-time seams** deserve a mention because embedded and robotics code uses them heavily. suppose the low-level HAL declares `std::uint64_t hal_monotonic_ns();` in a header. the firmware build links `hal_time_stm32.cpp`; the host test build links `hal_time_fake.cpp`, which returns a global the test sets. the code under test has no interface, template, or callback at all. the tradeoffs: only one implementation per binary, the seam is invisible when reading the source (only the build files reveal it), and if both files end up in the same link you get a duplicate-symbol error, or worse, with static libraries the linker silently uses whichever definition it pulls in first. use it for platform functions you cannot change, not for application design.

### watch out for

**an interface on a per-sample hot path.** a virtual seam is cheap when it is called once per frame or per control cycle, and the indirect call disappears in the noise. put the same interface inside a loop that runs a million times per frame (a per-sample filter, a per-point distance function) and the call can no longer be inlined, which also blocks vectorization of the loop around it. the fix is not to give up the seam but to pick the right kind: a template parameter constrained by a concept keeps the substitution point and lets the compiler see through it. as always, measure before and after; the profile decides, not the principle.

### the takeaway

choose the seam by when the decision is made: run time (virtual interface or `std::function`), compile time (a template constrained by a concept), or link time (platform functions only); every kind is testable, and each costs something different.

### optional challenge

`RateLimiter` stores its clock by value. why does the test version use `ManualClock` holding a pointer, instead of passing a `FakeClock` with a mutable `t` member directly?

<details>
<summary>answer</summary>

because `RateLimiter` copies (or moves) the clock into its own member `clock_`. if the test passed a `FakeClock` value, advancing the test's copy would not affect the limiter's copy, so time would never move from the limiter's point of view. the pointer gives the copy a handle back to state the test controls. alternatives: pass a `std::reference_wrapper`-like adapter, or give `RateLimiter` a reference member and accept the borrowed-lifetime rule. value semantics for injected policies is a good default for stateless or cheaply copied policies; when the test needs to observe or steer shared state, some form of indirection is unavoidable.

</details>
