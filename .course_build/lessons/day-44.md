<a id="day-44"></a>

## day 44: dependency injection and testable seams

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 12, 13, 17, 29, 43

### the idea

Here is a joint controller that looks perfectly reasonable:

```cpp
class JointController {
public:
    void step(double target_rad) {
        const auto t = std::chrono::steady_clock::now();       // hidden dependency
        const double dt = std::chrono::duration<double>(t - last_).count();
        const double err = target_rad - motor_.position();
        motor_.command_torque(kp_ * err + kd_ * (err - last_err_) / dt);
        last_ = t;
        last_err_ = err;
    }
private:
    CanBusMotor motor_{"can0", 0x141};                          // hidden dependency
    double kp_ = 10.0, kd_ = 0.5, last_err_ = 0.0;
    std::chrono::steady_clock::time_point last_ = std::chrono::steady_clock::now();
};
```

How do you test that the derivative term behaves when `dt` is 10 ms? You can't, short of plugging in a CAN adapter and sleeping. The controller decides *what* to compute and also *where its inputs come from*. Dependency injection is just separating those: the object receives its collaborators instead of creating or fetching them.

### understanding the concept

A **seam** is a place where you can change what code does without editing that code. Dependency injection creates seams deliberately. In C++ you have four main kinds, and they differ in when the choice is made:

| seam | chosen at | cost and constraints | good for |
|---|---|---|---|
| virtual interface, injected via constructor | run time | indirect call, usually not inlined; needs an interface type and a lifetime decision | hardware, I/O, plugins, anything chosen from config |
| template parameter (constrained by a concept) | compile time | no indirection; code lives in headers, each instantiation is separate code, longer builds | hot paths, header-only utilities, policies |
| `std::function` | run time | type erasure: indirect call, may allocate for large callables (day 17) | single callbacks: a time source, a log sink |
| link-time | link time | one implementation per binary; invisible in the source | replacing a platform function (time, GPIO) in a test binary |

Two decisions come with every injected dependency. **Ownership**: does the controller own the clock (`std::unique_ptr<Clock>`), share it (`std::shared_ptr`, rarely justified), or borrow it (a reference, with the caller promising it outlives the controller)? Day 12's rules apply unchanged. **Who wires things up**: the answer should be one place near `main`, often called the composition root, where concrete objects are created and passed down. Everything below it just takes what it is given.

On the test side, distinguish a **fake** from a **mock**. A fake is a small working implementation with its own state: a clock that only moves when the test advances it. A mock records calls and verifies expectations about them ("`command_torque` called once with 60"). Prefer fakes and check outcomes; reach for mocks when the interaction itself is the requirement, such as "the enable command must precede the first torque command".

### in code

**Constructor injection with interfaces.** The controller now borrows a clock and an actuator. Production code passes the real ones; tests pass fakes.

```cpp
#include <chrono>

class Clock {
public:
    virtual ~Clock() = default;
    virtual std::chrono::steady_clock::time_point now() const = 0;
};

class Actuator {
public:
    virtual ~Actuator() = default;
    virtual double position() const = 0;           // rad
    virtual void command_torque(double nm) = 0;
};

class JointController {
public:
    JointController(const Clock& clock, Actuator& motor, double kp, double kd)
        : clock_(clock), motor_(motor), kp_(kp), kd_(kd), last_(clock.now()) {}

    void step(double target_rad) {
        const auto t = clock_.now();
        const double dt = std::chrono::duration<double>(t - last_).count();
        const double err = target_rad - motor_.position();
        const double derr = dt > 0.0 ? (err - last_err_) / dt : 0.0;
        motor_.command_torque(kp_ * err + kd_ * derr);
        last_ = t;
        last_err_ = err;
    }

private:
    const Clock& clock_;         // borrowed: must outlive the controller
    Actuator& motor_;            // borrowed
    double kp_, kd_;
    std::chrono::steady_clock::time_point last_;
    double last_err_ = 0.0;
};
```

The test is now deterministic and runs in microseconds:

```cpp
#include <cassert>
#include <cmath>
#include <iostream>

struct FakeClock final : Clock {
    std::chrono::steady_clock::time_point t{};
    std::chrono::steady_clock::time_point now() const override { return t; }
};

struct FakeActuator final : Actuator {
    double pos = 0.0, last_torque = 0.0;
    double position() const override { return pos; }
    void command_torque(double nm) override { last_torque = nm; }
};

int main() {
    using namespace std::chrono_literals;
    FakeClock clock;
    FakeActuator motor;
    JointController ctl(clock, motor, /*kp=*/10.0, /*kd=*/0.5);

    clock.t += 10ms;
    ctl.step(1.0);                     // err 1.0, derr 100/s: 10 + 50
    assert(std::abs(motor.last_torque - 60.0) < 1e-9);

    motor.pos = 0.5;
    clock.t += 10ms;
    ctl.step(1.0);                     // err 0.5, derr -50/s: 5 - 25
    std::cout << motor.last_torque << '\n';   // prints: -20
}
```

**Compile-time injection with a concept (C++20).** When the dependency is fixed per build and sits on a hot path, make it a template parameter. The concept documents what the dependency must provide and gives readable errors (day 29).

```cpp
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

No interface, no virtual call, and `SystemSteadyClock` is an empty class (it still occupies at least one byte as a member; `[[no_unique_address]]` in C++20 can remove that). The price is that `RateLimiter<ManualClock>` and `RateLimiter<SystemSteadyClock>` are different types, so you cannot store both in one container or choose between them from a config file.

**A `std::function` seam** is the lightest runtime option when the dependency is a single operation:

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

**Link-time seams** deserve a mention because embedded and robotics code uses them heavily. Suppose the low-level HAL declares `std::uint64_t hal_monotonic_ns();` in a header. The firmware build links `hal_time_stm32.cpp`; the host test build links `hal_time_fake.cpp`, which returns a global the test sets. The code under test has no interface, template, or callback at all. The tradeoffs: only one implementation per binary, the seam is invisible when reading the source (only the build files reveal it), and if both files end up in the same link you get a duplicate-symbol error, or worse, with static libraries the linker silently uses whichever definition it pulls in first. Use it for platform functions you cannot change, not for application design.

In a typical robot stack the result looks like this: `main` reads config, constructs `CanBusMotor`, `SystemClock`, and a `UdpTelemetrySink`, then passes references into controllers and planners. Unit tests construct the same controllers with fakes, and hardware-in-the-loop tests swap only the motor. Nothing below `main` ever calls `steady_clock::now()` or opens a socket on its own.

### watch out for

**Service locators and DI containers.** A global registry you query (`Services::get<Clock>()`) looks convenient, but it hides dependencies again: the constructor no longer tells you what the class needs, missing registrations fail at run time instead of compile time, and tests have to reset global state. Reflection-driven DI frameworks from Java or C# have no direct C++ equivalent, and the libraries that emulate them add template complexity to save a few lines in `main`. Explicit constructor arguments are usually enough.

**Borrowed references outliving their owner.** `JointController` stores references, so this compiles and is undefined behavior on the first `step`:

```cpp
JointController make_controller(Actuator& motor) {
    SystemClock clock;                        // production Clock, local to this function
    return JointController(clock, motor, 10.0, 0.5);
}   // BUG: clock is destroyed; the returned controller holds a dangling reference
```

If lifetimes are not obviously nested, take ownership (`std::unique_ptr<Clock>`) instead.

Also watch the constructor length. A class that needs eight injected collaborators is usually telling you about poor cohesion (day 43), not about a lack of DI tooling.

### the takeaway

Inject what crosses a boundary (time, hardware, I/O, randomness), choose the seam by when the decision is made (run time, compile time, link time), make ownership explicit, and wire everything in one place near `main`.

### optional challenge

`RateLimiter` stores its clock by value. Why does the test version use `ManualClock` holding a pointer, instead of passing a `FakeClock` with a mutable `t` member directly?

<details>
<summary>answer</summary>

Because `RateLimiter` copies (or moves) the clock into its own member `clock_`. If the test passed a `FakeClock` value, advancing the test's copy would not affect the limiter's copy, so time would never move from the limiter's point of view. The pointer gives the copy a handle back to state the test controls. Alternatives: pass a `std::reference_wrapper`-like adapter, or give `RateLimiter` a reference member and accept the borrowed-lifetime rule. Value semantics for injected policies is a good default for stateless or cheaply copied policies; when the test needs to observe or steer shared state, some form of indirection is unavoidable.

</details>
