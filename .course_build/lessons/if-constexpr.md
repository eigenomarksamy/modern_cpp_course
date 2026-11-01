---
title: compile-time branching with if constexpr
standard: C++17
objective: replace SFINAE overload sets with if constexpr, and know exactly what a discarded branch skips
prerequisites: class-templates, variadic-templates
difficulty: 2
---

### the idea

you are writing a telemetry encoder that appends fields to a byte buffer. arithmetic values are copied as raw bytes, enums go out as their underlying integer, strings get a length prefix. before C++17, "do something different depending on the type" inside a template meant an overload set guarded by `std::enable_if` or a tag-dispatch helper, which scatters one decision across several functions and produces error messages nobody enjoys. C++17 lets you write the decision as a plain branch, evaluated at compile time, and lets you apply an operator across a whole parameter pack without recursion.

### understanding the concept

`if constexpr (cond)` requires `cond` to be a constant expression convertible to `bool` (narrowing conversions are not allowed). its defining property is what happens to the branch that is not taken: **inside a template**, when the condition is known at instantiation, the discarded branch is not instantiated. code in it may be invalid for the current `T` (calling `v.size()` on an `int`, say) and that is fine, because it is never compiled for that `T`.

two limits follow from "not instantiated" rather than "not compiled at all":

- the discarded branch is still parsed. syntax errors and errors that do not depend on a template parameter are diagnosed.
- outside a template there is nothing to instantiate, so both branches are fully checked. `if constexpr` in a normal function behaves like `if` with a constant condition (with the minor difference that entities only used in the discarded branch need no definition).

a useful side effect: `return` statements in a discarded branch do not take part in return type deduction, so an `auto` function can return different types for different `T`.

### in code

the encoder, before and after. the "before" splits one decision across three overloads:

```cpp complete
#include <cstdint>
#include <cstring>
#include <string>
#include <type_traits>
#include <vector>

using Buffer = std::vector<std::uint8_t>;

namespace before {   // C++14: SFINAE picks an overload
template <class T, std::enable_if_t<std::is_arithmetic<T>::value, int> = 0>
void put(Buffer& b, T v) {
    std::uint8_t raw[sizeof v];
    std::memcpy(raw, &v, sizeof v);        // native byte order
    b.insert(b.end(), raw, raw + sizeof v);
}
template <class T, std::enable_if_t<std::is_enum<T>::value, int> = 0>
void put(Buffer& b, T v) { put(b, static_cast<std::underlying_type_t<T>>(v)); }
inline void put(Buffer& b, const std::string& s) {
    put(b, static_cast<std::uint32_t>(s.size()));
    b.insert(b.end(), s.begin(), s.end());
}
}  // namespace before
```

after: one function, the decision in one place, and a deliberate error for anything else.

```cpp
template <class> inline constexpr bool always_false = false;

template <class T>
void put(Buffer& b, const T& v) {
    if constexpr (std::is_arithmetic_v<T>) {
        std::uint8_t raw[sizeof v];
        std::memcpy(raw, &v, sizeof v);    // native byte order
        b.insert(b.end(), raw, raw + sizeof v);
    } else if constexpr (std::is_enum_v<T>) {
        put(b, static_cast<std::underlying_type_t<T>>(v));
    } else if constexpr (std::is_same_v<T, std::string>) {
        put(b, static_cast<std::uint32_t>(v.size()));
        b.insert(b.end(), v.begin(), v.end());
    } else {
        static_assert(always_false<T>, "put: unsupported field type");
    }
}
```

with a plain `if`, every branch would be instantiated for every `T`: `put(b, 42)` would try to compile `v.size()` on an `int` and fail. with `if constexpr`, `put(b, 42)` instantiates only the first branch.

### in practice

there is also a design judgment hiding here. the `if constexpr` chain is a **closed set**: supporting a new field type means editing `put`. that is a feature when the encoder owns the format and every type must be reviewed. if users of a library should be able to add their own types, an overload or a trait they can specialize is the better seam, because it is open for extension without touching your code. [[variant]] meets the same closed-versus-open tradeoff at runtime.

### watch out for

the obvious way to write the "unsupported type" branch does not work:

```cpp
template <class T>
void put(Buffer& b, const T& v) {
    if constexpr (std::is_arithmetic_v<T>) { /* ... */ }
    else static_assert(false, "unsupported");   // BUG in C++17 and C++20
}
```

`false` does not depend on `T`, so the assertion can never succeed for any instantiation, and a non-dependent assertion is checked when the template is defined, not when a branch is chosen. under the C++17 and C++20 rules the template is ill-formed, and GCC 12 rejects it even if `put` is never called. the fix is to make the condition dependent, as in `always_false<T>` above. C++23 (paper P2593) changed the rule so that `static_assert(false)` is only evaluated when the branch is instantiated; GCC 13 and Clang 17 implement it, but on a C++17 or C++20 code base, keep the dependent-false helper.

### the takeaway

`if constexpr` skips instantiation, not parsing, and only inside templates; it puts a closed set of type-dependent cases in one readable place, which is right when you own the set and wrong when users need to extend it.

### optional challenge

with a plain `if`, does this compile for `T = int`? what changes with `if constexpr`?

```cpp complete
#include <type_traits>

template <class T>
auto count_of(const T& v) {
    if (std::is_integral_v<T>) return 1;
    else return v.size();
}
```

<details>
<summary>answer</summary>

with a plain `if` it fails twice for `int`: both branches are instantiated, so `v.size()` is compiled for an `int`, and the two `return` statements deduce different types (`int` and `std::size_t`) for one `auto` function. with `if constexpr`, the discarded branch is not instantiated and its `return` does not take part in return type deduction, so `count_of(42)` returns `int` and `count_of(std::string("ab"))` returns `std::size_t`. whether a function that returns different types per `T` is good API design is a separate question; here returning `std::size_t` from both branches would be kinder to callers.

</details>

### going deeper

#### what a `constexpr` function may do in C++17

finally, `constexpr` functions. C++14 already allowed local variables, loops, and mutation inside them; C++17 added `constexpr` lambdas and `if constexpr`. still forbidden in C++17: `try` blocks, virtual calls, dynamic allocation, `static` locals, and uninitialized local variables (C++20 relaxes most of these; [[constexpr-evolution]]). a `constexpr` function is *allowed* to run at compile time; it is *required* to only where a constant expression is needed, such as a `static_assert`, an array bound, or a template argument. and in constant evaluation, core-language undefined behavior such as signed overflow is a compile error rather than a silent miscompile.
