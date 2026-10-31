<a id="day-46"></a>

## day 46: static versus dynamic polymorphism and type erasure

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 13, 17, 25, 29, 45

### the idea

A telemetry recorder must store a mixed stream of records: IMU samples from your team, battery states from the power team, GPS fixes from a vendor library you cannot modify. Each can render itself as text. How do you put them in one `std::vector` and call "render" on each?

"Make them inherit from `Record`" is the reflex, and it fails on the vendor type straight away. C++ gives you at least four ways to get "one call, many types", and they differ in who has to know about whom, when the choice is made, and what you pay for it.

### understanding the concept

| | virtual functions | templates + concepts | `std::variant` | type erasure |
|---|---|---|---|---|
| set of types | open | open | closed (listed in the variant) | open |
| user types must inherit | yes | no | no | no |
| semantics | reference (via pointer to base) | value | value | value |
| one heterogeneous container | yes, of pointers | no | yes | yes |
| call mechanism | indirect call, usually through a vtable | direct, inlinable | `std::visit` dispatch (implementation-specific, often a jump table) | indirect call inside the wrapper |
| typical cost to watch | heap allocation per object, no inlining | compile time, code size per instantiation | adding a type touches every visitor | allocation per object unless small-buffer optimized, a clone per copy |
| across a shared-library boundary | the standard plugin mechanism | not applicable, code is instantiated in the caller | adding an alternative changes the type and its layout | possible if the wrapper's layout is fixed |

None of the "call mechanism" entries is a performance verdict. An indirect call costs a load and a branch that may be predicted well or badly, and it blocks inlining, which often matters more than the call itself. Whether any of that shows up depends on how much work each call does. Measure with a profiler on the real workload before choosing on speed.

**Static polymorphism** resolves the call at compile time. The old tool is CRTP (the curiously recurring template pattern): a base class template that casts `this` to the derived type. In C++20, a concept plus a free function template often does the same job with less ceremony, and C++23's deducing `this` (an explicit object parameter, `this const auto& self`) removes most of CRTP's boilerplate. That is C++23 only.

**Type erasure** is how `std::function` and `std::any` work. A template constructor sees the concrete type once, wraps it in an internal "model" object that implements a private interface, and stores it behind a pointer of fixed type. After construction the wrapper's type no longer mentions the concrete type: it has been erased. Inheritance still exists, but it is hidden inside the wrapper instead of imposed on users.

### in code

**Static polymorphism: CRTP versus a concept.** Both share the "raw times scale" logic without a virtual call.

```cpp
#include <concepts>

// CRTP: the base knows the derived type through the template argument
template <typename Derived>
class SensorBase {
public:
    double read_si() const {
        const auto& self = static_cast<const Derived&>(*this);
        return self.raw() * self.scale();
    }
};
class Thermistor : public SensorBase<Thermistor> {
public:
    int raw() const { return 2048; }
    double scale() const { return 0.05; }
};

// C++20 alternative: no base class at all
template <typename S>
concept ScaledSensor = requires(const S& s) {
    { s.raw() } -> std::integral;
    { s.scale() } -> std::floating_point;
};
double read_si(const ScaledSensor auto& s) { return s.raw() * s.scale(); }

// Thermistor{}.read_si() and read_si(Thermistor{}) both return 102.4
```

`SensorBase<Thermistor>` and `SensorBase<StrainGauge>` are unrelated types, so CRTP gives shared code, not a common type to store. Either way you cannot put both sensors in one container.

**Hand-written type erasure.** The users' types implement nothing; they only need a free function `to_text` that argument-dependent lookup can find, which also works for the vendor type because you can write that function yourself in its namespace.

```cpp
#include <concepts>
#include <memory>
#include <string>
#include <utility>

template <typename T>
concept TextRenderable = requires(const T& t) {
    { to_text(t) } -> std::convertible_to<std::string>;
};

class Record {
public:
    template <TextRenderable T>
    Record(T value) : self_(std::make_unique<Model<T>>(std::move(value))) {}

    Record(const Record& other) : self_(other.self_->clone()) {}
    Record& operator=(const Record& other) { return *this = Record(other); }
    Record(Record&&) noexcept = default;
    Record& operator=(Record&&) noexcept = default;

    friend std::string to_text(const Record& r) { return r.self_->render(); }

private:
    struct Concept {                                    // private interface
        virtual ~Concept() = default;
        virtual std::string render() const = 0;
        virtual std::unique_ptr<Concept> clone() const = 0;
    };
    template <typename T>
    struct Model final : Concept {                      // one per stored type
        explicit Model(T v) : value(std::move(v)) {}
        std::string render() const override { return to_text(value); }
        std::unique_ptr<Concept> clone() const override { return std::make_unique<Model>(*this); }
        T value;
    };
    std::unique_ptr<Concept> self_;
};
```

The virtual function is named `render`, not `to_text`, on purpose: inside `Model`, an unqualified call to `to_text` would otherwise find the member first, and finding a class member suppresses argument-dependent lookup, so the user's free function would never be considered.

Using it:

```cpp
#include <iostream>
#include <vector>

namespace imu {
struct Sample { int seq; };
std::string to_text(const Sample& s) { return "imu #" + std::to_string(s.seq); }
}
namespace vendor {                                      // pretend we cannot edit this struct
struct GpsFix { int sats; };
}
namespace vendor {                                      // but we can add a function next to it
std::string to_text(const GpsFix& g) { return "gps sats=" + std::to_string(g.sats); }
}

int main() {
    std::vector<Record> records{imu::Sample{41}, vendor::GpsFix{9}};
    records.push_back(records.front());                  // value semantics: deep copy
    for (const auto& r : records) std::cout << to_text(r) << '\n';
    // prints: imu #41
    //         gps sats=9
    //         imu #41
}
```

Adding a function to a vendor's namespace is your code, in your translation units, so it is fine; adding declarations to namespace `std` is not (with narrow exceptions such as specializing certain templates for your own types).

### in practice

In a robotics stack the four options usually coexist, each where it fits:

- **Plugins loaded at run time** (a `dlopen`'d planner or driver) use a virtual interface plus an `extern "C"` factory function. Templates cannot cross that boundary, and a virtual interface is the most widely understood ABI contract, as long as you never change the virtual functions of a released interface (even adding one can shift vtable slots, which is implementation-specific); publish a new versioned interface instead.
- **Messages on an internal bus** with a fixed, versioned set of types are a `std::variant`. The closed set is a feature: the compiler can tell you about every visitor you forgot to update (day 25).
- **Hot numerical kernels** take their policies as template parameters constrained by concepts, so filters and interpolators inline into the loop.
- **Task queues and callbacks** store `std::function` or a small custom erased wrapper, because the queue must hold arbitrary callables by value.

Sean Parent's line "inheritance is the base class of evil" is about the first option leaking into everything: if the interface is a base class, every user type must inherit from it, objects live behind pointers, and copying needs a `clone()` hierarchy. Type erasure keeps the inheritance private and gives users plain value types.

### watch out for

**Type erasure is not free and not always worth it.** The wrapper above allocates once per stored object and once per copy, every call is an indirect call, and debuggers show you `Model<imu::Sample>` frames you did not write. Real implementations often add a **small buffer optimization**: store small objects inside the wrapper itself and fall back to the heap for large ones. Whether and when `std::function` does this is an implementation detail (buffer sizes and conditions differ between libstdc++, libc++, and MSVC), so do not design around it; count allocations if it matters (day 52). Also note that the wrapper requires copyable types; a move-only callable needs a move-only wrapper, which the standard only provides in C++23 (`std::move_only_function`).

If you own all the types, need reference semantics anyway, and the set is open, a ten-line virtual interface is easier to read and debug than a forty-line erased wrapper. Reach for type erasure when you need value semantics or must accept types that cannot inherit from your base.

### the takeaway

Choose by the shape of the problem: virtual functions for open sets behind pointers and binary boundaries, templates and concepts for compile-time choice and speed, `std::variant` for closed sets, and type erasure for open sets with value semantics. The cost model is different for each, so measure before choosing on performance.

### optional challenge

`Record`'s converting constructor takes `T` by value and is constrained by `TextRenderable`. `Record` itself satisfies `TextRenderable` (its hidden friend `to_text` is found by ADL). So why doesn't `Record copy = records.front();` wrap a `Record` inside a `Model<Record>`?

<details>
<summary>answer</summary>

Because the copy constructor wins. For `Record copy = records.front();` the argument is a `Record` lvalue. Overload resolution looks at the copy constructor `Record(const Record&)` and at the constructor template, but the standard says a constructor template is never instantiated to produce a constructor whose first parameter is the class type by value (that signature would be a broken copy constructor), so the template is not a viable candidate here. If the constructor took `T&&` (a forwarding reference) instead, a non-const lvalue `Record` would deduce `T = Record&`, the template would be a better match than `const Record&`, and copying would try to wrap a `Record` inside a `Model<Record>`: at best a silent extra layer of allocation and indirection per copy, and with this concept GCC 12 reports a recursive constraint error instead. That is why forwarding constructors in erased wrappers need an explicit `!std::same_as<std::remove_cvref_t<T>, Record>` constraint.

</details>
