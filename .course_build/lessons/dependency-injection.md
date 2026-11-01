---
title: dependency injection: passing collaborators in
standard: C++17
objective: make a class testable by injecting the dependencies that cross a boundary, decide who owns them, and wire everything in one place
prerequisites: coupling-cohesion, ownership-in-interfaces
difficulty: 2
---

### the idea

here is a joint controller that looks perfectly reasonable:

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

how do you test that the derivative term behaves when `dt` is 10 ms? you can't, short of plugging in a CAN adapter and sleeping. the controller decides *what* to compute and also *where its inputs come from*. dependency injection is just separating those: the object receives its collaborators instead of creating or fetching them.

### understanding the concept

a **seam** is a place where you can change what code does without editing that code, and dependency injection creates seams deliberately: an object receives its collaborators (a clock, an actuator, a socket, a random number generator) instead of creating or fetching them itself. the things worth injecting are the ones that cross a boundary or make behavior nondeterministic: time, hardware, I/O, randomness, and third-party services. pure computation stays inside.

two decisions come with every injected dependency. **ownership**: does the controller own the clock (`std::unique_ptr<Clock>`), share it (`std::shared_ptr`, rarely justified), or borrow it (a reference, with the caller promising it outlives the controller)? [[ownership-in-interfaces]]'s rules apply unchanged. **who wires things up**: the answer should be one place near `main`, often called the composition root, where concrete objects are created and passed down. everything below it just takes what it is given.

on the test side, distinguish a **fake** from a **mock**. a fake is a small working implementation with its own state: a clock that only moves when the test advances it. a mock records calls and verifies expectations about them ("`command_torque` called once with 60"). prefer fakes and check outcomes; reach for mocks when the interaction itself is the requirement, such as "the enable command must precede the first torque command".

### in code

**constructor injection with interfaces.** the controller now borrows a clock and an actuator. production code passes the real ones; tests pass fakes.

```cpp complete
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

the test is now deterministic and runs in microseconds:

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

### in practice

in a typical robot stack the result looks like this: `main` reads config, constructs `CanBusMotor`, `SystemClock`, and a `UdpTelemetrySink`, then passes references into controllers and planners. unit tests construct the same controllers with fakes, and hardware-in-the-loop tests swap only the motor. nothing below `main` ever calls `steady_clock::now()` or opens a socket on its own.

### watch out for

**service locators and DI containers.** a global registry you query (`Services::get<Clock>()`) looks convenient, but it hides dependencies again: the constructor no longer tells you what the class needs, missing registrations fail at run time instead of compile time, and tests have to reset global state. reflection-driven DI frameworks from Java or C# have no direct C++ equivalent, and the libraries that emulate them add template complexity to save a few lines in `main`. explicit constructor arguments are usually enough.

**borrowed references outliving their owner.** `JointController` stores references, so this compiles and is undefined behavior on the first `step`:

```cpp
JointController make_controller(Actuator& motor) {
    SystemClock clock;                        // production Clock, local to this function
    return JointController(clock, motor, 10.0, 0.5);
}   // BUG: clock is destroyed; the returned controller holds a dangling reference
```

if lifetimes are not obviously nested, take ownership (`std::unique_ptr<Clock>`) instead.

also watch the constructor length. a class that needs eight injected collaborators is usually telling you about poor cohesion ([[coupling-cohesion]]), not about a lack of DI tooling.

### the takeaway

inject what crosses a boundary (time, hardware, I/O, randomness), make ownership of every injected object explicit, and wire everything in one place near `main`.

### optional challenge

a trajectory follower uses a `std::vector<double>` of waypoints, `std::sqrt`, the system clock, a UDP socket for telemetry, and a random jitter source for testing robustness. which of these would you inject, and why?

<details>
<summary>answer</summary>

inject the clock, the socket, and the random source: each crosses a boundary or makes behavior nondeterministic, so a test needs to control it (advance time, capture what was sent, fix the random sequence). do not inject the vector or `std::sqrt`: they are deterministic, local, and already testable through the follower's inputs and outputs. injecting them would add indirection without adding a single test you could not already write.

</details>
