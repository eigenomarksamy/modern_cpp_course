---
title: constructors that establish invariants
standard: C++17
objective: write constructors that make an invalid object impossible, using initializer lists, validation, delegation, and explicit
prerequisites: raii, initialization
difficulty: 2
---

### the idea

a radar range gate has two numbers and one rule: `0 <= min < max`. a class with a default constructor plus `set_min()` and `set_max()` lets every caller build a gate that breaks the rule, if only between two calls, so every function that receives a gate has to check it again. a constructor exists to make that impossible: if the object exists, its invariant holds.

### understanding the concept

a constructor's job is to turn raw storage into an object whose invariant holds. [[raii]] put that in RAII terms: if the object exists, the resource is valid. the mechanics:

- **members are initialized before the body runs.** anything you do not name in the member initializer list is default-initialized (or uses its default member initializer). assigning in the body is therefore a second step: construct, then overwrite. for `const` members, references, and types without a default constructor, there is no second step; the initializer list is the only option.

two conveniences round it out. default member initializers (`float gain_ = 1.0f;`) give every constructor a sensible starting value. delegating constructors (`Window() : Window(256) {}`) let one constructor reuse another's work.

### in code

**validate once, in the constructor.**

```cpp complete
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

every member function can now assume the invariant, and there is no `is_valid()` for callers to forget. in a codebase built with exceptions disabled, the same idea becomes a private constructor plus `static std::optional<RangeGate> make(double, double)`: the invariant still lives in one place, and the failure is still impossible to ignore.

**delegating constructors and default member initializers.**

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

each constructor states only what differs, and `gain_` has a sensible value however the object was built. notice also what the class does *not* store: a separate `size_` member would have to agree with `samples_.size()` forever. state you can derive is better derived than stored, because duplicated state is an invariant you must maintain by hand ([[construction-order]] shows how that particular duplicate goes wrong).

### in practice

the payoff of validating in constructors grows with the size of the system. parse configuration, network messages, and user input into types like `RangeGate` at the boundary, and the code behind the boundary never re-checks: it cannot receive an invalid gate, because none can be built. invariants enforced by types travel with the data, while checks scattered through call sites erode one refactor at a time.

contrast `struct Detection { double range_m, azimuth_rad, snr_db; };`. any combination of values is a valid detection, so there is nothing to protect: a plain aggregate with public members is the honest design. the Core Guidelines put it as "use `class` if the class has an invariant; use `struct` if the data members can vary independently." wrapping independent fields in getters and setters adds ceremony without adding safety.

### watch out for

a single-argument constructor that is not `explicit` is also an implicit conversion.

```cpp
struct Timeout {
    Timeout(int ms) : ms(ms) {}            // implicit: int converts to Timeout
    int ms;
};
void arm_watchdog(Timeout t);

arm_watchdog(5);                           // compiles. 5 ms? 5 s? 5 retries?
```

mark it `explicit` and the call site must say `arm_watchdog(Timeout{5})`; copy-list-initialization (`Timeout t = {5};`) is rejected too. make single-argument constructors `explicit` by default, and drop it only when the conversion is genuinely lossless and unsurprising (`std::string` from a string literal, a wider duration from a narrower one). the same applies to conversion operators: write `explicit operator bool()`, which still works in `if (x)` but not in `int n = x;`. better still, for durations, use `std::chrono` and let the type carry the unit.

### the takeaway

a constructor's job is to establish the invariant: initialize members in the initializer list, validate once, derive what you can instead of storing it, and make single-argument constructors `explicit`.

### optional challenge

which of the numbered lines compile?

```cpp
struct Meters { explicit Meters(double v) : value(v) {} double value; };
void set_range(Meters m);

set_range(5.0);           // (1)
set_range(Meters{5.0});   // (2)
Meters a = 5.0;           // (3)
Meters b{5.0};            // (4)
Meters c = {5.0};         // (5)
```

<details>
<summary>answer</summary>

only (2) and (4). an `explicit` constructor is not used for implicit conversions, so (1) fails, and copy-initialization (3) does not consider it at all. (5) is copy-list-initialization: overload resolution does find the `explicit` constructor, and choosing it makes the program ill-formed. direct forms (2) and (4) name the type and are fine.

</details>
