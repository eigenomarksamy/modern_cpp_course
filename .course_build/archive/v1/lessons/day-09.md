<a id="day-09"></a>

## day 09: constructors, destructors, and the object lifecycle

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 02, 03, 08

### the idea

A colleague reorders two members in a header to "group related fields". Nothing else changes. The next build passes, the unit tests pass, and a sample buffer in the radar front end is now sized from garbage. The constructor's initializer list looked perfectly correct; it was the class declaration that changed.

Constructors are where invariants are born, and the rules that govern them (order, partial construction, dispatch) are stricter and less intuitive than they look.

### understanding the concept

A constructor's job is to turn raw storage into an object whose invariant holds. Day 08 put that in RAII terms: if the object exists, the resource is valid. The mechanics:

- **Members are initialized before the body runs.** Anything you do not name in the member initializer list is default-initialized (or uses its default member initializer). Assigning in the body is therefore a second step: construct, then overwrite. For `const` members, references, and types without a default constructor, there is no second step; the initializer list is the only option.
- **Order is fixed by the class definition, not by the initializer list.** For a non-virtual hierarchy: direct bases in declaration order, then non-static members in declaration order, then the constructor body. (Virtual bases come first of all, constructed by the most derived class.) Destruction is the exact reverse. The order you write in the initializer list is ignored, which is why GCC and Clang have `-Wreorder` (enabled by `-Wall`).
- **During construction and destruction, an object is only as derived as the constructor or destructor currently running.** Inside `Base::Base()`, the derived members do not exist yet, so a virtual call dispatches to `Base`'s version, not the override. Calling a *pure* virtual function this way is undefined behavior.
- **If a constructor throws, the object never existed.** Its destructor does not run. Every base and member that *was* fully constructed is destroyed, in reverse order. Raw resources acquired in the body are on their own.

Two conveniences round it out. Default member initializers (`float gain_ = 1.0f;`) give every constructor a sensible starting value. Delegating constructors (`Window() : Window(256) {}`) let one constructor reuse another's work.

### in code

First, the reorder bug and its real fix.

```cpp
#include <cstddef>
#include <vector>

class SampleWindow {
public:
    explicit SampleWindow(std::size_t n)
        : size_(n), samples_(size_) {}   // BUG: samples_ is initialized first
private:
    std::vector<float> samples_;          // declared first, so constructed first
    std::size_t size_;
};
```

`samples_(size_)` reads `size_` before it is initialized. That is a read of an indeterminate value: undefined behavior, which in practice means a vector of some arbitrary size, or a `std::length_error`, or a huge allocation. GCC 12 reports it twice under `-Wall`: `-Wreorder` for the list order and `-Wuninitialized` ("member is used uninitialized"). Matching the list order to the declaration silences the warnings, but the better fix removes the duplicated state:

```cpp
class SampleWindow {
public:
    explicit SampleWindow(std::size_t n) : samples_(n) {}
    SampleWindow() : SampleWindow(default_size) {}   // delegating constructor
    std::size_t size() const { return samples_.size(); }
private:
    static constexpr std::size_t default_size = 256;
    std::vector<float> samples_;
    float gain_ = 1.0f;                              // default member initializer
};
```

A `size_` that must always equal `samples_.size()` is an invariant you have to maintain by hand. Deleting it deletes the bug class.

Second, predict the output. This one shows construction order and the "only as derived as the running constructor" rule.

```cpp
#include <cstdio>

struct Part {
    const char* n;
    explicit Part(const char* name) : n(name) { std::printf("part %s\n", n); }
    ~Part() { std::printf("~part %s\n", n); }
};

struct Sensor {
    Sensor() { std::puts("Sensor()"); describe(); }
    virtual ~Sensor() { std::puts("~Sensor()"); describe(); }
    virtual void describe() const { std::puts("  I am a Sensor"); }
};

struct Lidar : Sensor {
    Part optics{"optics"};
    Part driver{"driver"};
    Lidar() { std::puts("Lidar()"); describe(); }
    ~Lidar() override { std::puts("~Lidar()"); }
    void describe() const override { std::puts("  I am a Lidar"); }
};

int main() { Lidar l; }
```

```text
Sensor()
  I am a Sensor
part optics
part driver
Lidar()
  I am a Lidar
~Lidar()
~part driver
~part optics
~Sensor()
  I am a Sensor
```

The `Sensor` constructor cannot call `Lidar::describe`: `optics` and `driver` have not been constructed yet, and an override is entitled to use them. The same logic applies in reverse in `~Sensor`. If a base class needs derived-specific setup, it cannot get it through a virtual call in its constructor; use a factory function that constructs and then initializes, or pass the information into the base constructor.

Third, partial construction. A class that owns two raw resources leaks the first when acquiring the second fails.

```cpp
class Pipeline {                            // BUG: leaks buf_ if open_device throws
public:
    Pipeline() : buf_(new float[4096]), dev_(open_device()) {}
    ~Pipeline() { close_device(dev_); delete[] buf_; }   // never runs if ctor throws
private:
    float* buf_;
    Device* dev_;
};

class Pipeline2 {                           // fixed: each member cleans up itself
    std::unique_ptr<float[]> buf_ = std::make_unique<float[]>(4096);
    DevicePtr dev_{open_device()};          // unique_ptr with a closing deleter
};
```

In `Pipeline2`, if `open_device` throws, `buf_` is a fully constructed member and is destroyed during unwinding. There is no user-written destructor at all. This is the seed of the rule of zero (day 11). One aside: `make_unique<float[]>(n)` value-initializes, so it zeroes the buffer; C++20's `std::make_unique_for_overwrite` skips that when you are about to fill it anyway.

### in practice

A radar range gate is only meaningful when `0 <= min < max`. Put that check in exactly one place:

```cpp
#include <stdexcept>

class RangeGate {
public:
    RangeGate(double min_m, double max_m) : min_(min_m), max_(max_m) {
        if (!(min_ >= 0.0 && min_ < max_))        // also rejects NaN
            throw std::invalid_argument("RangeGate: need 0 <= min < max");
    }
    bool contains(double r) const { return r >= min_ && r < max_; }
private:
    double min_, max_;
};
```

Every member function can now assume the invariant, and there is no `is_valid()` for callers to forget. In a codebase built with exceptions disabled, the same idea becomes a private constructor plus `static std::optional<RangeGate> make(double, double)`: the invariant still lives in one place, and the failure is still impossible to ignore.

Contrast `struct Detection { double range_m, azimuth_rad, snr_db; };`. Any combination of values is a valid detection, so there is nothing to protect: a plain aggregate with public members is the honest design. The Core Guidelines put it as "use `class` if the class has an invariant; use `struct` if the data members can vary independently." Wrapping independent fields in getters and setters adds ceremony without adding safety.

### watch out for

A single-argument constructor that is not `explicit` is also an implicit conversion.

```cpp
struct Timeout {
    Timeout(int ms) : ms(ms) {}            // implicit: int converts to Timeout
    int ms;
};
void arm_watchdog(Timeout t);

arm_watchdog(5);                           // compiles. 5 ms? 5 s? 5 retries?
```

Mark it `explicit` and the call site must say `arm_watchdog(Timeout{5})`; copy-list-initialization (`Timeout t = {5};`) is rejected too. Make single-argument constructors `explicit` by default, and drop it only when the conversion is genuinely lossless and unsurprising (`std::string` from a string literal, a wider duration from a narrower one). The same applies to conversion operators: write `explicit operator bool()`, which still works in `if (x)` but not in `int n = x;`. Better still, for durations, use `std::chrono` and let the type carry the unit.

### the takeaway

Members are built in declaration order, the body runs last, and a constructor that throws leaves no object behind. Design so that each member cleans up after itself, and those rules work for you instead of against you.

### optional challenge

The target constructor finishes, and then the delegating constructor's body throws. Does `~Probe()` run?

```cpp
struct Probe {
    explicit Probe(int id) { std::printf("Probe(%d)\n", id); }
    Probe() : Probe(0) { throw std::runtime_error("calibration failed"); }
    ~Probe() { std::puts("~Probe()"); }
};
```

<details>
<summary>answer</summary>

Yes. Once a delegating constructor's target constructor completes, the object counts as constructed, so if the delegating constructor's body then exits via an exception, the destructor is invoked. Constructing `Probe p;` inside a `try` prints `Probe(0)`, then `~Probe()`, then whatever the handler prints. This is the one case where a constructor throwing still runs the class's own destructor, and it is why a target constructor should leave the object fully valid: the destructor may have to clean it up.

</details>
