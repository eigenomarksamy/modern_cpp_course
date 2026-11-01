---
title: writing your own concepts
standard: C++20
objective: write concepts with requires expressions that capture a meaningful contract, and test types against them where they are defined
prerequisites: concepts
difficulty: 3
---

### the idea

a template's real contract tends to live in its body: "`S` must have a `read()` that returns its sample type, a `name()` that does not throw, and a `reset()`". callers learn it by failing to compile against it. a concept of your own puts that contract in one named, reusable place, where the compiler checks it at every call site and where a type's author can check it before anyone else calls anything.

### understanding the concept

the building block for your own concepts is the **requires expression**, `requires (params) { requirements; }`. its parameters are just names to write expressions with; nothing is evaluated or executed. the compiler only asks "would this be valid?". there are four kinds of requirement:

| kind | form | checks |
|---|---|---|
| simple | `s.reset();` | the expression is valid |
| type | `typename S::sample_type;` | the type exists |
| compound | `{ s.read() } noexcept -> std::same_as<X>;` | valid, optionally `noexcept`, and `decltype((expr))` satisfies the concept |
| nested | `requires std::copyable<X>;` | a further constraint is satisfied |

concepts are not purely syntactic. `std::regular` means "copyable, default-constructible, and equality-comparable *in a way that behaves like a value*"; `std::totally_ordered` means the comparison operators are consistent with a total order. the compiler checks only the syntax. for standard library templates, a type that satisfies a concept's syntax but violates its semantic requirements makes the program ill-formed, no diagnostic required: you get no error, just no guarantees.

### in code

**writing a concept.** a sensor driver contract for a robotics stack:

```cpp complete
#include <chrono>
#include <concepts>
#include <cstdint>
#include <string_view>

template <typename S>
concept Sensor = requires(S& s, const S& cs) {
    typename S::sample_type;                                  // type
    { s.read() } -> std::same_as<typename S::sample_type>;    // compound
    { cs.name() } noexcept -> std::convertible_to<std::string_view>;
    s.reset();                                                // simple
    requires std::copyable<typename S::sample_type>;          // nested
};

struct Imu {
    struct sample_type { float ax, ay, az; };
    sample_type read() { return {0.f, 0.f, 9.81f}; }
    std::string_view name() const noexcept { return "imu0"; }
    void reset() {}
};
static_assert(Sensor<Imu>);   // the contract is tested next to the type

struct Encoder {
    using sample_type = std::int32_t;
    std::int64_t read() { return 0; }   // BUG: does not return sample_type
    const char* name() const noexcept { return "enc0"; }
    void reset() {}
};

template <Sensor S>
typename S::sample_type poll(S& s) { return s.read(); }

// poll(enc);  GCC 12: note: 's.read()' does not satisfy return-type-requirement
```

that `static_assert` line is worth making a habit. it turns "does my type still fit the template?" into a compile error in the type's own header, not in someone else's instantiation three libraries away.

finally, C++20 lambdas can name their template parameters, which lets you constrain them and relate two arguments' types:

```cpp complete
#include <algorithm>
#include <vector>

auto clamp_all = []<std::floating_point T>(std::vector<T>& v, T lo, T hi) {
    for (T& x : v) x = std::clamp(x, lo, hi);
};
// clamp_all(floats, 0.f, 1.f);  OK
// clamp_all(floats, 0.0, 1.0);  error: conflicting types for 'T' (float and double)
```

with a generic lambda (`auto` parameters, [[lambdas]]) you could not say "these three are the same `T`" without `decltype` gymnastics.

### in practice

a motion-control library offers `template <Sensor S, Actuator A> class JointController`. before concepts, the header said `template <typename S, typename A>` and the real contract lived in a wiki page and in the body of `update()`. integrators found out their encoder wrapper was missing `reset()` when a build failed inside the controller's implementation.

with concepts, the header *is* the contract, every driver header carries `static_assert(Sensor<MyDriver>)`, and the error appears where the driver is written. compare this with a virtual `ISensor` interface ([[virtual-dispatch]]): the concept version has no vtable, no inheritance requirement, and allows inlining, but every controller instantiation is a separate piece of code (compile time, binary size), and you cannot put heterogeneous sensors in one container without type erasure ([[type-erasure]]). choose a concept when the type is fixed at build time and the call is hot; choose a virtual interface when you need runtime selection or a stable binary boundary.

### watch out for

a related trap is subsumption with raw traits. these two overloads look like "general" and "more specific", but they are **ambiguous** for `int`:

```cpp
template <typename T> requires std::is_integral_v<T>                        void g(T);
template <typename T> requires std::is_integral_v<T> && (sizeof(T) == 4)   void g(T);
// g(1);  error: call of overloaded 'g(int)' is ambiguous
```

the two `std::is_integral_v<T>` are different atomic constraints because they are different expressions. write `std::integral<T>` in both and the second overload wins.

### the takeaway

a concept moves a template's requirements from its body into its signature. write concepts that name a meaningful contract (`Sensor`, `std::regular`), build them from standard concepts so subsumption works, and test them with `static_assert` next to the types that must satisfy them.

### optional challenge

```cpp complete
template <typename T>
concept Addable = requires(T a, T b) { a + b; };
```

which of these hold: `Addable<std::string>`, `Addable<const char*>`, `Addable<short>`, `Addable<bool>`? would you use `Addable` to constrain a `sum()` over sensor readings?

<details>
<summary>answer</summary>

`Addable<std::string>` is true (concatenation). `Addable<const char*>` is false: adding two pointers is ill-formed. `Addable<short>` and `Addable<bool>` are both true, through integral promotion to `int`, so `a + b` does not even have type `T`.

so `Addable` admits strings (concatenation, not summation) and `bool`, and says nothing about the result type. it describes syntax, not meaning. for a sum of readings, constrain on what you mean: `Arithmetic` from this lesson, or a compound requirement such as `{ a + b } -> std::convertible_to<T>` together with a semantic contract documented next to the concept.

</details>
