---
title: concepts: constraining templates
standard: C++20
objective: constrain templates with standard concepts so requirements are part of the signature, and predict which constrained overload is chosen
prerequisites: function-templates, if-constexpr
difficulty: 2
---

### the idea

call `std::sort(ids.begin(), ids.end())` on a `std::list<int>` and GCC 12 reports `no match for 'operator-'` at line 1938 of `stl_algo.h`, a file you never wrote, followed by a page of instantiation context. the real problem ("sort needs random access") appears nowhere. call `std::ranges::sort(ids)` instead and the first error is on your line, and the notes say the constraint `random_access_range` was not satisfied because `bidirectional_iterator_tag` is not `random_access_iterator_tag`.

the output is not shorter. it is *located*: the requirement is part of the signature, so the compiler checks it at the call site instead of discovering the problem deep in the body. that is what concepts buy you: a template's requirements move from its implementation into its interface.

### understanding the concept

a **concept** is a named compile-time predicate over template arguments:

```cpp
template <typename T>
concept Arithmetic = std::integral<T> || std::floating_point<T>;
```

`Arithmetic<double>` is a `bool` constant expression. a concept is not a type and has no runtime presence. when a constrained template is a candidate in overload resolution, the compiler deduces the template arguments, then checks the constraints *before* instantiating anything. if they are not satisfied, the candidate is dropped, exactly as SFINAE would drop it ([[function-templates]]), but the diagnostic names the unsatisfied concept and the failing sub-expression.

`<concepts>` gives you the vocabulary: `std::integral`, `std::floating_point`, `std::same_as`, `std::convertible_to`, `std::derived_from`, `std::invocable`, `std::predicate`, `std::totally_ordered`, `std::copyable`, `std::regular`, and more. build on these instead of reinventing them, for a reason we will see under subsumption.

### in code

**before and after.** C++17 hid the constraint in a defaulted template parameter ([[function-templates]]). C++20 gives four spellings that mean the same thing for a single parameter:

```cpp complete
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

use the constrained parameter when one concept applies to one type; use a `requires` clause when the constraint relates several parameters (`requires std::convertible_to<From, To>`).

**overloading on constraints.** when two constrained overloads are both viable, the more constrained one wins if its constraints *subsume* the other's:

```cpp
#include <cstdio>
void describe(Arithmetic auto)    { std::puts("arithmetic"); }
void describe(std::integral auto) { std::puts("integral"); }

describe(3);     // prints: integral   (integral subsumes integral || floating_point)
describe(2.5);   // prints: arithmetic
describe('a');   // prints: integral   (char is an integral type)
```

subsumption is decided by breaking constraints into atomic pieces and comparing them, and two atomic constraints are only "the same" if they come from the same expression in the source, which in practice means the same named concept. that is why you build on `std::integral` rather than writing `std::is_integral_v<T>` in each overload (see "watch out for").

### in practice

migrating a C++17 template library to concepts is mostly mechanical and immediately visible to users. every `std::enable_if_t<...>` in a template parameter list becomes a constrained parameter or a `requires` clause, behavior stays the same, and the error a user gets for a wrong type moves from the middle of the implementation to the line they wrote, naming the requirement they missed. the standard library made the same move: `std::ranges::sort` and the other range algorithms are constrained versions of the C++98 algorithms, which is exactly why the opening example's diagnostic improved. a good first step in your own code is the templates that users instantiate most often with the wrong types, because that is where the error messages cost the most time.

### watch out for

**concepts do not check the template body.** this compiles, because the body is only checked when instantiated:

```cpp
template <std::integral T>
T half(T x) { return x.value / 2; }   // nonsense, but no error until someone calls it
```

unlike Rust traits, C++20 has no definition checking: the concept constrains *callers*, not the implementation. if the body uses `s.flush()` and the concept forgot to require it, a type can satisfy the concept and still fail inside. keep the concept and the body in sync, and test with a minimal archetype type that provides only what the concept demands.

### the takeaway

a concept moves a template's requirements from its body into its signature; constrain with standard concepts, so error messages name the requirement and the most specific overload wins.

### optional challenge

for `template <std::integral T> T gcd(T a, T b);`, which calls compile?

```cpp
gcd(12, 18);      // (1)
gcd(12u, 18u);    // (2)
gcd(12, 18L);     // (3)
gcd('a', 'b');    // (4)
gcd(true, false); // (5)
```

<details>
<summary>answer</summary>

(1), (2), (4), and (5) compile; (3) does not. deduction happens first and must agree, so `int` and `long` conflict before the constraint is even checked. `unsigned`, `char`, and `bool` all satisfy `std::integral`, which may be more than a `gcd` should accept; a `requires` clause such as `std::integral<T> && !std::same_as<T, bool>` states the narrower intent.

</details>
