---
title: construction and destruction order
standard: C++17
objective: predict the order in which bases and members are built and destroyed, and what that means for virtual calls and constructors that throw
prerequisites: constructors
difficulty: 2
---

### the idea

a colleague reorders two members in a header to "group related fields". nothing else changes. the next build passes, the unit tests pass, and a sample buffer in the radar front end is now sized from garbage. the constructor's initializer list looked perfectly correct; it was the class declaration that changed.

constructors are where invariants are born, and the rules that govern them (order, partial construction, dispatch) are stricter and less intuitive than they look.

### understanding the concept

- **order is fixed by the class definition, not by the initializer list.** for a non-virtual hierarchy: direct bases in declaration order, then non-static members in declaration order, then the constructor body. (virtual bases come first of all, constructed by the most derived class.) destruction is the exact reverse. the order you write in the initializer list is ignored, which is why GCC and Clang have `-Wreorder` (enabled by `-Wall`).
- **during construction and destruction, an object is only as derived as the constructor or destructor currently running.** inside `Base::Base()`, the derived members do not exist yet, so a virtual call dispatches to `Base`'s version, not the override. calling a *pure* virtual function this way is undefined behavior.
- **if a constructor throws, the object never existed.** its destructor does not run. every base and member that *was* fully constructed is destroyed, in reverse order. raw resources acquired in the body are on their own.

### in code

first, the reorder bug and its real fix.

```cpp ub
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

`samples_(size_)` reads `size_` before it is initialized. that is a read of an indeterminate value: undefined behavior, which in practice means a vector of some arbitrary size, or a `std::length_error`, or a huge allocation. GCC 12 reports it twice under `-Wall`: `-Wreorder` for the list order and `-Wuninitialized` ("member is used uninitialized"). matching the list order to the declaration silences the warnings, but the better fix removes the duplicated state:

the robust fix is the one from [[constructors]]: remove `size_` and ask `samples_.size()`, so there is no second value to get out of order.

second, predict the output. this one shows construction order and the "only as derived as the running constructor" rule.

```cpp complete
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

the `Sensor` constructor cannot call `Lidar::describe`: `optics` and `driver` have not been constructed yet, and an override is entitled to use them. the same logic applies in reverse in `~Sensor`. if a base class needs derived-specific setup, it cannot get it through a virtual call in its constructor; use a factory function that constructs and then initializes, or pass the information into the base constructor.

### in practice

third, partial construction. a class that owns two raw resources leaks the first when acquiring the second fails.

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

in `Pipeline2`, if `open_device` throws, `buf_` is a fully constructed member and is destroyed during unwinding. there is no user-written destructor at all. this is the seed of the rule of zero ([[rule-of-zero]]). one aside: `make_unique<float[]>(n)` value-initializes, so it zeroes the buffer; C++20's `std::make_unique_for_overwrite` skips that when you are about to fill it anyway.

### watch out for

**do not publish `this` from a constructor.** registering the object with a registry, a timer, or another thread inside a base class constructor hands out a pointer to an object that is not finished:

```cpp
struct Sensor {
    explicit Sensor(Scheduler& s) { s.add(this); }   // BUG: derived part not built yet
    virtual void poll() = 0;
    virtual ~Sensor() = default;
};
```

if the scheduler runs on another thread, it can call `poll()` before the derived constructor finishes: during base construction that is a call to a pure virtual function (undefined behavior), and later it races with the rest of construction. register from a factory function after the object is fully constructed, and unregister before destruction begins.

### the takeaway

members are built in declaration order, the body runs last, and a constructor that throws leaves no object behind. design so that each member cleans up after itself, and those rules work for you instead of against you.

### optional challenge

the target constructor finishes, and then the delegating constructor's body throws. does `~Probe()` run?

```cpp
struct Probe {
    explicit Probe(int id) { std::printf("Probe(%d)\n", id); }
    Probe() : Probe(0) { throw std::runtime_error("calibration failed"); }
    ~Probe() { std::puts("~Probe()"); }
};
```

<details>
<summary>answer</summary>

yes. once a delegating constructor's target constructor completes, the object counts as constructed, so if the delegating constructor's body then exits via an exception, the destructor is invoked. constructing `Probe p;` inside a `try` prints `Probe(0)`, then `~Probe()`, then whatever the handler prints. this is the one case where a constructor throwing still runs the class's own destructor, and it is why a target constructor should leave the object fully valid: the destructor may have to clean it up.

</details>
