---
title: one call, many types: choosing a polymorphism mechanism
standard: C++20
objective: compare virtual functions, templates with concepts, `std::variant`, and type erasure, and use static polymorphism where the choice is made at compile time
prerequisites: strategy, writing-concepts, variant-design
difficulty: 2
---

### the idea

a telemetry recorder must store a mixed stream of records: IMU samples from your team, battery states from the power team, GPS fixes from a vendor library you cannot modify. each can render itself as text. how do you put them in one `std::vector` and call "render" on each?

"make them inherit from `Record`" is the reflex, and it fails on the vendor type straight away. C++ gives you at least four ways to get "one call, many types", and they differ in who has to know about whom, when the choice is made, and what you pay for it.

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

none of the "call mechanism" entries is a performance verdict. an indirect call costs a load and a branch that may be predicted well or badly, and it blocks inlining, which often matters more than the call itself. whether any of that shows up depends on how much work each call does. measure with a profiler on the real workload before choosing on speed.

**static polymorphism** resolves the call at compile time. the old tool is CRTP (the curiously recurring template pattern): a base class template that casts `this` to the derived type. in C++20, a concept plus a free function template often does the same job with less ceremony, and C++23's deducing `this` (an explicit object parameter, `this const auto& self`) removes most of CRTP's boilerplate. that is C++23 only.

### in code

**static polymorphism: CRTP versus a concept.** both share the "raw times scale" logic without a virtual call.

```cpp complete
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

`SensorBase<Thermistor>` and `SensorBase<StrainGauge>` are unrelated types, so CRTP gives shared code, not a common type to store. either way you cannot put both sensors in one container.

### in practice

in a robotics stack the four options usually coexist, each where it fits:

- **plugins loaded at run time** (a `dlopen`'d planner or driver) use a virtual interface plus an `extern "C"` factory function. templates cannot cross that boundary, and a virtual interface is the most widely understood ABI contract, as long as you never change the virtual functions of a released interface (even adding one can shift vtable slots, which is implementation-specific); publish a new versioned interface instead.
- **messages on an internal bus** with a fixed, versioned set of types are a `std::variant`. the closed set is a feature: the compiler can tell you about every visitor you forgot to update ([[variant-design]]).
- **hot numerical kernels** take their policies as template parameters constrained by concepts, so filters and interpolators inline into the loop.
- **task queues and callbacks** store `std::function` or a small custom erased wrapper, because the queue must hold arbitrary callables by value.

### watch out for

**the CRTP copy-paste bug.** the base trusts its template argument completely:

```cpp
class StrainGauge : public SensorBase<Thermistor> {   // BUG: copied from Thermistor
public:
    int raw() const { return 512; }
    double scale() const { return 0.2; }
};
```

`StrainGauge{}.read_si()` compiles and casts a `StrainGauge` to `const Thermistor&`, which it is not: undefined behavior. a common guard is a private constructor in the base with `friend Derived;`, so only the class named in the template argument can construct it, and the mistake fails to compile. the concept-based version has no such hole, which is one more reason to prefer it in C++20.

### the takeaway

choose by the shape of the problem: virtual functions for open sets behind pointers and binary boundaries, templates and concepts for compile-time choice and speed, `std::variant` for closed sets, and type erasure for open sets with value semantics; measure before choosing on performance.

### optional challenge

the telemetry recorder from the opening must store IMU samples (your type), battery states (another team's type, which you can change), and GPS fixes (a vendor type you cannot change), by value, in one container, and new record types are added every few months. which of the four options fits, and why do the others not?

<details>
<summary>answer</summary>

type erasure. a virtual base class fails on the vendor type, which cannot inherit from it, and forces pointer semantics. templates and concepts give no single type to store in one container. a `std::variant` could hold the three types, but the set keeps growing, and every addition changes the variant type and every visitor; that is acceptable for a protocol you own, less so for an open-ended set. type erasure keeps an open set, value semantics, and requires nothing of the stored types except the operations the wrapper uses, which [[type-erasure]] builds.

</details>
