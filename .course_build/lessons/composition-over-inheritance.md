---
title: composition, interfaces, and substitutability
standard: C++17
objective: use public inheritance only for substitutable interfaces, keep contracts in the base with the NVI idiom, and compose implementations instead of inheriting them
prerequisites: virtual-destructors-slicing
difficulty: 2
---

### the idea

inheritance is two features wearing one keyword. it gives you *subtyping* (a `Lidar` can be used wherever a `Sensor&` is expected) and *implementation reuse* (a `Lidar` gets `Sensor`'s members and code). you almost always want the first. the second is where class hierarchies go wrong: deep trees, fragile bases, and a `MecanumDriveLidarRobotWithArm` class that exists only because the hierarchy had nowhere else to put it.

### understanding the concept

two more tools for designing hierarchies. an **abstract interface** is a class with only pure virtual functions and a virtual destructor: it carries a contract and no implementation. the **non-virtual interface (NVI)** idiom makes public functions non-virtual and the customization points private virtual, so the base class enforces the contract around every override:

```cpp
class RangeSensor {
public:
    virtual ~RangeSensor() = default;
    double read_m() {                                  // the contract lives here
        double r = do_read_m();
        if (!(r >= min_m() && r <= max_m())) throw SensorFault{"out of range"};
        return r;
    }
private:
    virtual double do_read_m() = 0;                    // what derived classes provide
    virtual double min_m() const = 0;
    virtual double max_m() const = 0;
};
```

overrides cannot skip the check, and the base can later add logging or timing in one place.

### in code

a mobile robot has a drive system and a localizer. the inheritance version models variations as subclasses: `DiffDriveRobot`, then `DiffDriveLidarRobot`, then a mecanum variant that needs half of each. every new axis of variation multiplies the classes. composition models each variation as a part:

```cpp
#include <memory>

struct Drive {                                   // interface: inherited
    virtual ~Drive() = default;
    virtual void apply(const Twist& cmd) = 0;
};

class Robot {                                    // implementation: composed
public:
    Robot(std::unique_ptr<Drive> drive, std::unique_ptr<Localizer> loc)
        : drive_(std::move(drive)), loc_(std::move(loc)) {}
    void step(const Twist& cmd) { drive_->apply(cmd); }
private:
    std::unique_ptr<Drive> drive_;
    std::unique_ptr<Localizer> loc_;
};
```

inheritance has not disappeared; it is confined to small interfaces (`Drive`), where subtyping is what you want. the robot *has* a drive rather than *is* one, so drive and localizer vary independently, can be swapped at run time, and can be replaced by fakes in tests ([[dependency-injection]] builds on this). the `unique_ptr` members also make `Robot` a move-only, rule-of-zero class.

### in practice

substitutability is the other half. the Liskov substitution principle says code written against the base must keep working with any derived class. suppose `RangeSensor`'s contract is "always returns a range in `[min, max]`", and a new `Sonar` returns `-1` when it hears no echo. it compiles, it overrides correctly, and it breaks every caller that trusted the contract. the fix is not a type check in the callers; it is either a contract that admits "no reading" (an `std::optional<double>` result, [[optional]]) or a `Sonar` that is not a `RangeSensor`. subtyping is a promise about behavior, not just signatures.

### watch out for

inheriting for code reuse. if `TelemetryPublisher` derives from `std::vector<Message>` or from a `Socket` class to "get" its functions, every public member of the base becomes part of your interface, users can call `push_back` and bypass your invariants, and changing the base breaks your users. make the reused type a private member and expose only what your class means. public inheritance is a statement that the derived class *is substitutable for* the base; if you would not say that sentence out loud, use composition.

### the takeaway

use public inheritance for substitutable interfaces, with `override`, a virtual destructor, and no slicing; for reuse and variation, compose.

### optional challenge

a colleague proposes `template <typename T> class ThreadSafeQueue : public std::queue<T>`, adding a mutex and locked versions of `push` and `pop`. what is wrong with the design, and what would you suggest instead?

<details>
<summary>answer</summary>

public inheritance makes every public member of `std::queue<T>` part of `ThreadSafeQueue`'s interface, including the unlocked `push`, `pop`, `front`, and `size`. any caller can bypass the mutex, so the class cannot keep its one invariant. it is also not substitutable: code that takes a `std::queue<T>&` will happily use it without locking. make the `std::queue<T>` a private member and expose only the locked operations (ideally a combined `try_pop` that checks and removes in one step, since a separate `empty()` check is stale by the time you act on it).

</details>
