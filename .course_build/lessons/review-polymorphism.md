---
title: review: inheritance and polymorphism
kind: review
standard: C++17
objective: consolidate virtual dispatch, virtual destructors and slicing, and composition, with spaced repetition from the ownership modules
prerequisites: virtual-dispatch, virtual-destructors-slicing, composition-over-inheritance
difficulty: 1
---

### recap

| lesson | key idea |
|---|---|
| [[virtual-dispatch]] | a virtual call picks the override from the dynamic type through an indirect call; `override` turns near-miss signatures into errors, and coarse-grained interfaces keep the cost irrelevant. |
| [[virtual-destructors-slicing]] | deleting through a base pointer needs a public virtual destructor (or a protected non-virtual one that forbids it); copying a derived object into a base object slices it. |
| [[composition-over-inheritance]] | inherit interfaces, compose implementations; a derived class must keep the base's behavioral contract, not just its signatures. |

this module was short because its ideas are few and sharp; the questions below also revisit the ownership modules that make polymorphic objects safe to hold.

### review questions

1. `Filter::apply(double) const` is pure virtual. a derived class declares `double apply(double x);` (no `const`, no `override`). what happens at compile time, and what would happen if the base function were not pure?
2. why does `std::vector<Sensor>` filled with `Lidar` objects compile, run, and still be wrong? what should the vector hold instead?
3. a `Sonar` derives from `RangeSensor`, whose contract says `read_m()` always returns a range in `[min, max]`. `Sonar` returns `-1` when it hears no echo. every override compiles. what principle does it break, and what are the two honest fixes?
4. from [[rule-of-zero]]: a polymorphic base declares `virtual ~Sensor() = default;` and nothing else. what does that do to the move operations of `Sensor` and of every class derived from it?
5. from [[ownership-in-interfaces]]: a function that runs every stage of a pipeline once takes `const std::vector<std::shared_ptr<Stage>>&`. what would you change, and why?

### mini exercise

the robot below inherits its capabilities. sketch a composed version with one small interface, and say which part of the design became testable that was not before.

```cpp complete
class DiffDriveRobot {
public:
    virtual ~DiffDriveRobot() = default;
    virtual void drive(double v, double w);   // talks to the motor controller
};

class LidarDiffDriveRobot : public DiffDriveRobot {
public:
    void scan();                               // talks to the lidar
};
```

### answers

<details>
<summary>answer 1: the missing const</summary>

the derived function has a different signature, so it does not override; it declares a new function that hides `Filter::apply`. because the base function is pure, the derived class stays abstract, and the error appears only where someone tries to create an object of it. had the base function not been pure, every call through a `Filter&` would silently run the base version. `override` on the derived declaration turns either case into an immediate error at the declaration.

</details>

<details>
<summary>answer 2: slicing in a container</summary>

each element of `std::vector<Sensor>` *is* a `Sensor`; inserting a `Lidar` copies its `Sensor` part and discards the rest, including the vptr, so every virtual call runs `Sensor`'s version. nothing is undefined, which is why it compiles and runs. polymorphic objects need indirection: `std::vector<std::unique_ptr<Sensor>>` keeps each object whole and gives the vector ownership. making `Sensor` abstract would have turned the mistake into a compile error.

</details>

<details>
<summary>answer 3: substitutability</summary>

the Liskov substitution principle: code written against `RangeSensor` must keep working with any derived class, and `Sonar` violates the behavioral contract every caller relies on. the fixes are to change the contract so that "no reading" is representable (for example `std::optional<double>`, [[optional]]), or to stop pretending a `Sonar` is a `RangeSensor` and give it its own interface. adding `if (dynamic_cast<Sonar*>(...))` in callers is the dishonest third option.

</details>

<details>
<summary>answer 4: a defaulted virtual destructor</summary>

declaring the destructor, even as `= default`, suppresses the implicit move constructor and move assignment, so `Sensor` and every derived class that does not declare its own moves will copy when asked to move. declare all five special members `= default` in the base (with the copy operations `protected` if you also want to prevent slicing), as shown in [[special-members]].

</details>

<details>
<summary>answer 5: borrowing, not sharing</summary>

the function only uses the stages during the call, so it should not mention ownership at all: take `const std::vector<Stage*>&`, or better, `std::span<Stage* const>` later in the course, or have the pipeline expose a loop over `Stage&`. taking `shared_ptr`s forces every caller to share ownership with them even when one object owns all the stages, and couples this function to that ownership strategy.

</details>

<details>
<summary>mini exercise answer</summary>

```cpp
struct Drive {                                // one small interface
    virtual ~Drive() = default;
    virtual void apply(double v, double w) = 0;
};

class Robot {
public:
    Robot(std::unique_ptr<Drive> drive, std::unique_ptr<Lidar> lidar)
        : drive_(std::move(drive)), lidar_(std::move(lidar)) {}
    void step(double v, double w) { drive_->apply(v, w); }
private:
    std::unique_ptr<Drive> drive_;
    std::unique_ptr<Lidar> lidar_;            // optional capability: may be null
};
```

the drive is now a part, not a base class: a mecanum drive or a simulated one plugs in without a new robot class, and a lidar is something a robot may or may not have, rather than a level in a hierarchy. the newly testable part is `Robot`'s own logic: a test can pass a fake `Drive` that records the commands it receives, with no motor controller attached. [[dependency-injection]] builds a whole technique on this.

</details>

### connections

inheritance is where ownership and lifetime meet runtime polymorphism: virtual destructors, slicing, and the special members of a base class are all ownership questions in disguise. the alternatives to virtual functions come later, once templates are available: compile-time polymorphism and type erasure in [[static-polymorphism]] and [[type-erasure]], and closed sets of types with `std::variant` in [[variant]]. next, the standard library: containers, algorithms, and lambdas.
