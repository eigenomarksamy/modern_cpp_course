<a id="day-13"></a>

## day 13: polymorphism, inheritance, and composition

**reading time:** about 10 minutes · **standard:** C++17 · **builds on:** days 09, 11, 12

### the idea

Inheritance is two features wearing one keyword. It gives you *subtyping* (a `Lidar` can be used wherever a `Sensor&` is expected) and *implementation reuse* (a `Lidar` gets `Sensor`'s members and code). You almost always want the first. The second is where class hierarchies go wrong: deep trees, fragile bases, and a `MecanumDriveLidarRobotWithArm` class that exists only because the hierarchy had nowhere else to put it.

Today: how virtual dispatch actually works, the traps it sets (slicing, missing virtual destructors, broken substitutability), and why "inherit interfaces, compose implementations" is a sound default.

### understanding the concept

A virtual function call through a reference or pointer selects the override for the object's *dynamic* type. The standard specifies only that behavior. Every mainstream compiler implements it the same way, though, and knowing the mechanism makes the costs concrete:

```text
typical layout (Itanium C++ ABI: GCC and Clang on Linux, also MinGW;
MSVC differs in details; none of this is required by the standard)

  Lidar object                    vtable for Lidar (one per class, read-only)
 +------------------+            +------------------------------------+
 | vptr  -----------+----------> | &Lidar::~Lidar (two entries)       |
 | Sensor members   |            | &Lidar::describe     (overridden)  |
 | Lidar members    |            | &Sensor::calibrate   (inherited)   |
 +------------------+            +------------------------------------+
                                   (RTTI and offset data sit just before)
```

A call `s.describe()` becomes: load the vptr from the object, load the function pointer from a fixed slot, call indirectly. The constructor of each class in the chain sets the vptr to its own class's table, which is exactly why day 09's virtual call in a base constructor reached the base version.

The cost is an extra dependent load or two and an indirect branch, which modern branch predictors handle well when a call site keeps seeing the same type. The larger cost is usually what the compiler cannot do: it cannot inline a call whose target it does not know, so it also cannot optimize across it (constant propagation, vectorizing a loop that contains it). Compilers devirtualize when they can prove the dynamic type, and `final` helps them. Whether any of this matters depends on call frequency, so put virtual boundaries at a coarse grain (one call per frame or per batch, not per sample) and measure before contorting a design to avoid them.

Two more tools for designing hierarchies. An **abstract interface** is a class with only pure virtual functions and a virtual destructor: it carries a contract and no implementation. The **non-virtual interface (NVI)** idiom makes public functions non-virtual and the customization points private virtual, so the base class enforces the contract around every override:

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

Overrides cannot skip the check, and the base can later add logging or timing in one place.

### in code

First, let the compiler check your overrides.

```cpp
struct Filter {
    virtual ~Filter() = default;
    virtual double apply(double x) const = 0;
};

struct LowPass : Filter {
    double apply(double x);               // BUG: missing const: a new function that
};                                        // hides Filter::apply; LowPass stays abstract

struct LowPass2 final : Filter {
    double apply(double x) override;      // error: marked 'override' but does not override
};

struct LowPass3 final : Filter {
    double apply(double x) const override { return 0.9 * x; }   // correct
};
```

Without `override`, a signature mismatch (missing `const`, `float` versus `double`, a changed base signature after a refactor) silently declares a new function. Here the mistake surfaces only because `LowPass` remains abstract; had the base function not been pure, the base version would run and nothing would complain. GCC 12's `-Woverloaded-virtual` would flag the hiding, but it is not part of `-Wall` in that version. Write `override` on every override; `final` on a class or function says "no further overriding" and gives the optimizer a devirtualization hint.

Second, the virtual destructor, and a twist with smart pointers.

```cpp
struct Plugin { ~Plugin() {} virtual void run() {} };   // BUG: non-virtual destructor
struct Logger : Plugin { std::string path; };

void demo() {
    std::unique_ptr<Plugin> p = std::make_unique<Logger>();
    p.reset();           // UB: deletes a Logger through Plugin* without a virtual dtor

    std::shared_ptr<Plugin> s = std::make_shared<Logger>();
    s.reset();           // OK, by accident: the control block remembers ~Logger
}
```

Deleting a derived object through a base pointer whose destructor is not virtual is undefined behavior, not merely "the derived destructor is skipped". `unique_ptr<Base>` calls `delete` on a `Base*`, so it inherits the bug. `shared_ptr` happens to survive because the control block captured a deleter for the real type at creation, but relying on that is fragile. The rule: a class meant to be deleted through a base pointer gets a public virtual destructor; otherwise make the destructor protected and non-virtual. GCC's `-Wdelete-non-virtual-dtor` (in `-Wall`) catches a direct `delete base_ptr;`, but GCC 12 stays silent on the `unique_ptr` version above, because the `delete` happens inside a system header. `-Wnon-virtual-dtor` (not in `-Wall`) flags the class definition itself and catches both.

Third, predict the output.

```cpp
#include <cstdio>
#include <vector>

struct Sensor {
    virtual ~Sensor() = default;
    virtual const char* name() const { return "sensor"; }
};
struct Lidar : Sensor {
    const char* name() const override { return "lidar"; }
};

int main() {
    Lidar lidar;
    Sensor& ref = lidar;
    Sensor copy = lidar;                  // slicing
    std::vector<Sensor> rack{lidar};      // slicing, again
    std::printf("%s %s %s\n", ref.name(), copy.name(), rack[0].name());
}
// prints: lidar sensor sensor
```

Copying a `Lidar` into a `Sensor` object constructs a `Sensor` from the `Sensor` part and discards the rest: the object's type is `Sensor`, vptr included. Polymorphism needs indirection (references, pointers, or `std::vector<std::unique_ptr<Sensor>>`). To make slicing impossible, delete or protect the base's copy operations (day 11); an abstract base cannot be sliced into at all.

### in practice

A mobile robot has a drive system and a localizer. The inheritance version models variations as subclasses: `DiffDriveRobot`, then `DiffDriveLidarRobot`, then a mecanum variant that needs half of each. Every new axis of variation multiplies the classes. Composition models each variation as a part:

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

Inheritance has not disappeared; it is confined to small interfaces (`Drive`), where subtyping is what you want. The robot *has* a drive rather than *is* one, so drive and localizer vary independently, can be swapped at run time, and can be replaced by fakes in tests (day 44 builds on this). The `unique_ptr` members also make `Robot` a move-only, rule-of-zero class.

Substitutability is the other half. The Liskov substitution principle says code written against the base must keep working with any derived class. Suppose `RangeSensor`'s contract is "always returns a range in `[min, max]`", and a new `Sonar` returns `-1` when it hears no echo. It compiles, it overrides correctly, and it breaks every caller that trusted the contract. The fix is not a type check in the callers; it is either a contract that admits "no reading" (an `std::optional<double>` result, day 24) or a `Sonar` that is not a `RangeSensor`. Subtyping is a promise about behavior, not just signatures.

### watch out for

Inheriting for code reuse. If `TelemetryPublisher` derives from `std::vector<Message>` or from a `Socket` class to "get" its functions, every public member of the base becomes part of your interface, users can call `push_back` and bypass your invariants, and changing the base breaks your users. Make the reused type a private member and expose only what your class means. Public inheritance is a statement that the derived class *is substitutable for* the base; if you would not say that sentence out loud, use composition.

### the takeaway

Use public inheritance for substitutable interfaces, with `override`, a virtual destructor, and no slicing; for reuse and variation, compose.

### optional challenge

`Base` has a non-virtual public function `void tick()` and `Derived` declares its own `void tick()`. Given `Derived d; Base& b = d;`, which function do `d.tick()` and `b.tick()` call? Would adding `override` to `Derived::tick` help?

<details>
<summary>answer</summary>

`d.tick()` calls `Derived::tick` and `b.tick()` calls `Base::tick`. Without `virtual`, the call is resolved from the static type of the expression, so the same object behaves differently depending on how you name it. `Derived::tick` merely hides `Base::tick`.

Adding `override` would not compile ("marked 'override', but does not override"), and that is the point: it turns the silent mistake into an error that tells you the base function is not virtual. The fix is then a deliberate choice: make `Base::tick` virtual, or rename the derived function so nobody expects dispatch.

</details>
