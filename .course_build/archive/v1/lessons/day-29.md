<a id="day-29"></a>

## day 29: concepts: constraining templates

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 18, 19, 23

### the idea

Call `std::sort(ids.begin(), ids.end())` on a `std::list<int>` and GCC 12 reports `no match for 'operator-'` at line 1938 of `stl_algo.h`, a file you never wrote, followed by a page of instantiation context. The real problem ("sort needs random access") appears nowhere. Call `std::ranges::sort(ids)` instead and the first error is on your line, and the notes say the constraint `random_access_range` was not satisfied because `bidirectional_iterator_tag` is not `random_access_iterator_tag`.

The output is not shorter. It is *located*: the requirement is part of the signature, so the compiler checks it at the call site instead of discovering the problem deep in the body. That is what concepts buy you: a template's requirements move from its implementation into its interface.

### understanding the concept

A **concept** is a named compile-time predicate over template arguments:

```cpp
template <typename T>
concept Arithmetic = std::integral<T> || std::floating_point<T>;
```

`Arithmetic<double>` is a `bool` constant expression. A concept is not a type and has no runtime presence. When a constrained template is a candidate in overload resolution, the compiler deduces the template arguments, then checks the constraints *before* instantiating anything. If they are not satisfied, the candidate is dropped, exactly as SFINAE would drop it (day 18), but the diagnostic names the unsatisfied concept and the failing sub-expression.

The building block for your own concepts is the **requires expression**, `requires (params) { requirements; }`. Its parameters are just names to write expressions with; nothing is evaluated or executed. The compiler only asks "would this be valid?". There are four kinds of requirement:

| kind | form | checks |
|---|---|---|
| simple | `s.reset();` | the expression is valid |
| type | `typename S::sample_type;` | the type exists |
| compound | `{ s.read() } noexcept -> std::same_as<X>;` | valid, optionally `noexcept`, and `decltype((expr))` satisfies the concept |
| nested | `requires std::copyable<X>;` | a further constraint is satisfied |

`<concepts>` gives you the vocabulary: `std::integral`, `std::floating_point`, `std::same_as`, `std::convertible_to`, `std::derived_from`, `std::invocable`, `std::predicate`, `std::totally_ordered`, `std::copyable`, `std::regular`, and more. Build on these instead of reinventing them, for a reason we will see under subsumption.

Concepts are not purely syntactic. `std::regular` means "copyable, default-constructible, and equality-comparable *in a way that behaves like a value*"; `std::totally_ordered` means the comparison operators are consistent with a total order. The compiler checks only the syntax. For standard library templates, a type that satisfies a concept's syntax but violates its semantic requirements makes the program ill-formed, no diagnostic required: you get no error, just no guarantees.

### in code

**Before and after.** C++17 hid the constraint in a defaulted template parameter (day 18). C++20 gives four spellings that mean the same thing for a single parameter:

```cpp
#include <concepts>
#include <type_traits>

// C++17: SFINAE via enable_if
template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
T gcd17(T a, T b) { while (b != 0) { T t = a % b; a = b; b = t; } return a; }

// C++20: constrained template parameter
template <std::integral T>
T gcd(T a, T b) { while (b != 0) { T t = a % b; a = b; b = t; } return a; }

// equivalent: requires clause, or trailing requires clause
template <typename T> requires std::integral<T> T gcd2(T a, T b);
template <typename T> T gcd3(T a, T b) requires std::integral<T>;

// abbreviated function template: each `auto` is its own template parameter
auto scale(std::floating_point auto gain, std::integral auto counts) {
    return gain * counts;
}

// gcd(12, 18L);   // error: deduced conflicting types for 'T' (int and long)
// scale(0.5, 7L); // fine: two independent parameters
// gcd(1.5, 2.5);  // error: 'is_integral_v<double>' evaluated to 'false'
```

Use the constrained parameter when one concept applies to one type; use a `requires` clause when the constraint relates several parameters (`requires std::convertible_to<From, To>`).

**Writing a concept.** A sensor driver contract for a robotics stack:

```cpp
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

That `static_assert` line is worth making a habit. It turns "does my type still fit the template?" into a compile error in the type's own header, not in someone else's instantiation three libraries away.

**Overloading on constraints.** When two constrained overloads are both viable, the more constrained one wins if its constraints *subsume* the other's:

```cpp
#include <cstdio>
void describe(Arithmetic auto)    { std::puts("arithmetic"); }
void describe(std::integral auto) { std::puts("integral"); }

describe(3);     // prints: integral   (integral subsumes integral || floating_point)
describe(2.5);   // prints: arithmetic
describe('a');   // prints: integral   (char is an integral type)
```

Subsumption is decided by breaking constraints into atomic pieces and comparing them, and two atomic constraints are only "the same" if they come from the same expression in the source, which in practice means the same named concept. That is why you build on `std::integral` rather than writing `std::is_integral_v<T>` in each overload (see "watch out for").

Finally, C++20 lambdas can name their template parameters, which lets you constrain them and relate two arguments' types:

```cpp
#include <algorithm>
#include <vector>

auto clamp_all = []<std::floating_point T>(std::vector<T>& v, T lo, T hi) {
    for (T& x : v) x = std::clamp(x, lo, hi);
};
// clamp_all(floats, 0.f, 1.f);  OK
// clamp_all(floats, 0.0, 1.0);  error: conflicting types for 'T' (float and double)
```

With a generic lambda (`auto` parameters, day 17) you could not say "these three are the same `T`" without `decltype` gymnastics.

### in practice

A motion-control library offers `template <Sensor S, Actuator A> class JointController`. Before concepts, the header said `template <typename S, typename A>` and the real contract lived in a wiki page and in the body of `update()`. Integrators found out their encoder wrapper was missing `reset()` when a build failed inside the controller's implementation.

With concepts, the header *is* the contract, every driver header carries `static_assert(Sensor<MyDriver>)`, and the error appears where the driver is written. Compare this with a virtual `ISensor` interface (day 13): the concept version has no vtable, no inheritance requirement, and allows inlining, but every controller instantiation is a separate piece of code (compile time, binary size), and you cannot put heterogeneous sensors in one container without type erasure (day 46). Choose a concept when the type is fixed at build time and the call is hot; choose a virtual interface when you need runtime selection or a stable binary boundary.

### watch out for

**Concepts do not check the template body.** This compiles, because the body is only checked when instantiated:

```cpp
template <std::integral T>
T half(T x) { return x.value / 2; }   // nonsense, but no error until someone calls it
```

Unlike Rust traits, C++20 has no definition checking: the concept constrains *callers*, not the implementation. If the body uses `s.flush()` and the concept forgot to require it, a type can satisfy the concept and still fail inside. Keep the concept and the body in sync, and test with a minimal archetype type that provides only what the concept demands.

A related trap is subsumption with raw traits. These two overloads look like "general" and "more specific", but they are **ambiguous** for `int`:

```cpp
template <typename T> requires std::is_integral_v<T>                        void g(T);
template <typename T> requires std::is_integral_v<T> && (sizeof(T) == 4)   void g(T);
// g(1);  error: call of overloaded 'g(int)' is ambiguous
```

The two `std::is_integral_v<T>` are different atomic constraints because they are different expressions. Write `std::integral<T>` in both and the second overload wins.

### the takeaway

A concept moves a template's requirements from its body into its signature. Write concepts that name a meaningful contract (`Sensor`, `std::regular`), build them from standard concepts so subsumption works, and test them with `static_assert` next to the types that must satisfy them.

### optional challenge

```cpp
template <typename T>
concept Addable = requires(T a, T b) { a + b; };
```

Which of these hold: `Addable<std::string>`, `Addable<const char*>`, `Addable<short>`, `Addable<bool>`? Would you use `Addable` to constrain a `sum()` over sensor readings?

<details>
<summary>answer</summary>

`Addable<std::string>` is true (concatenation). `Addable<const char*>` is false: adding two pointers is ill-formed. `Addable<short>` and `Addable<bool>` are both true, through integral promotion to `int`, so `a + b` does not even have type `T`.

So `Addable` admits strings (concatenation, not summation) and `bool`, and says nothing about the result type. It describes syntax, not meaning. For a sum of readings, constrain on what you mean: `Arithmetic` from this lesson, or a compound requirement such as `{ a + b } -> std::convertible_to<T>` together with a semantic contract documented next to the concept.

</details>
