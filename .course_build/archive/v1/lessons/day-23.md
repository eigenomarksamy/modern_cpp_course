<a id="day-23"></a>

## day 23: compile-time branching with `if constexpr` and fold expressions

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 18, 19

### the idea

You are writing a telemetry encoder that appends fields to a byte buffer. Arithmetic values are copied as raw bytes, enums go out as their underlying integer, strings get a length prefix. Before C++17, "do something different depending on the type" inside a template meant an overload set guarded by `std::enable_if` or a tag-dispatch helper, which scatters one decision across several functions and produces error messages nobody enjoys. C++17 lets you write the decision as a plain branch, evaluated at compile time, and lets you apply an operator across a whole parameter pack without recursion.

### understanding the concept

`if constexpr (cond)` requires `cond` to be a constant expression convertible to `bool` (narrowing conversions are not allowed). Its defining property is what happens to the branch that is not taken: **inside a template**, when the condition is known at instantiation, the discarded branch is not instantiated. Code in it may be invalid for the current `T` (calling `v.size()` on an `int`, say) and that is fine, because it is never compiled for that `T`.

Two limits follow from "not instantiated" rather than "not compiled at all":

- The discarded branch is still parsed. Syntax errors and errors that do not depend on a template parameter are diagnosed.
- Outside a template there is nothing to instantiate, so both branches are fully checked. `if constexpr` in a normal function behaves like `if` with a constant condition (with the minor difference that entities only used in the discarded branch need no definition).

A useful side effect: `return` statements in a discarded branch do not take part in return type deduction, so an `auto` function can return different types for different `T`.

**Fold expressions** apply a binary operator across a parameter pack (day 19). There are four forms, and the parentheses are part of the syntax:

| form | written | expands to (for `a, b, c`) |
|---|---|---|
| unary right | `(xs op ...)` | `a op (b op c)` |
| unary left | `(... op xs)` | `(a op b) op c` |
| binary right | `(xs op ... op init)` | `a op (b op (c op init))` |
| binary left | `(init op ... op xs)` | `((init op a) op b) op c` |

A unary fold over an empty pack is ill-formed except for three operators: `&&` gives `true`, `||` gives `false`, and the comma operator gives `void()`. For anything else, use a binary fold with an identity value. The comma fold is the workhorse for "do this for every argument": the built-in comma operator sequences its operands left to right, so `(f(xs), ...)` calls `f` in argument order. Contrast that with function arguments, whose evaluation order is still unspecified (day 06).

Finally, `constexpr` functions. C++14 already allowed local variables, loops, and mutation inside them; C++17 added `constexpr` lambdas and `if constexpr`. Still forbidden in C++17: `try` blocks, virtual calls, dynamic allocation, `static` locals, and uninitialized local variables (C++20 relaxes most of these; day 33). A `constexpr` function is *allowed* to run at compile time; it is *required* to only where a constant expression is needed, such as a `static_assert`, an array bound, or a template argument. And in constant evaluation, core-language undefined behavior such as signed overflow is a compile error rather than a silent miscompile.

### in code

The encoder, before and after. The "before" splits one decision across three overloads:

```cpp
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

After: one function, the decision in one place, and a deliberate error for anything else.

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

With a plain `if`, every branch would be instantiated for every `T`: `put(b, 42)` would try to compile `v.size()` on an `int` and fail. With `if constexpr`, `put(b, 42)` instantiates only the first branch.

Now folds. Predict the two results before reading the comments:

```cpp
#include <cmath>
#include <iostream>

template <class... Ts> int lsub(Ts... xs) { return (... - xs); }   // ((1 - 2) - 3)
template <class... Ts> int rsub(Ts... xs) { return (xs - ...); }   // (1 - (2 - 3))

template <class... Ts> auto sum(Ts... xs) { return (xs + ... + 0); }          // empty pack: 0
template <class... Ts> bool all_finite(Ts... xs) { return (std::isfinite(xs) && ...); }

template <class... Ts>
void log_line(const Ts&... xs) {
    ((std::cout << xs << ' '), ...);   // comma fold: guaranteed left to right
    std::cout << '\n';
}

int main() {
    std::cout << lsub(1, 2, 3) << ' ' << rsub(1, 2, 3) << '\n';   // prints: -4 2
    std::cout << sum() << ' ' << sum(1, 2.5) << '\n';             // prints: 0 3.5
    std::cout << all_finite(1.0, NAN) << '\n';                    // prints: 0
    log_line("imu", 3, 0.25);                                     // prints: imu 3 0.25
}
```

`&&` and `||` folds short-circuit just like the operators they expand to, so `all_finite` stops at the first non-finite value.

### in practice

Put the two together and a whole telemetry frame becomes one line per message type, with the type checks done by the compiler:

```cpp
enum class Mode : std::uint8_t { idle, tracking, fault };

template <class... Fields>
Buffer encode(std::uint16_t msg_id, const Fields&... fields) {
    Buffer b;
    put(b, msg_id);
    (put(b, fields), ...);               // one put per field, in order
    return b;
}

Buffer frame = encode(0x21, Mode::tracking, 12.5f, std::string("base_link"));
// 2 (id) + 1 (mode) + 4 (float) + 4 (length) + 9 (chars) = 20 bytes
```

Passing a `std::vector<int>` as a field fails at compile time with the `static_assert` message rather than a page of overload-resolution notes. The costs are real but usually acceptable: every distinct list of field types instantiates a new `encode` (code size and compile time), and the format is native-endian, which is fine for same-host IPC and wrong for a wire protocol. Measure compile time with `-ftime-report` (GCC) or `-ftime-trace` (Clang) if a header like this starts to dominate builds.

There is also a design judgment hiding here. The `if constexpr` chain is a **closed set**: supporting a new field type means editing `put`. That is a feature when the encoder owns the format and every type must be reviewed. If users of a library should be able to add their own types, an overload or a trait they can specialize is the better seam, because it is open for extension without touching your code. Day 25 meets the same closed-versus-open tradeoff at runtime.

### watch out for

The obvious way to write the "unsupported type" branch does not work:

```cpp
template <class T>
void put(Buffer& b, const T& v) {
    if constexpr (std::is_arithmetic_v<T>) { /* ... */ }
    else static_assert(false, "unsupported");   // BUG in C++17 and C++20
}
```

`false` does not depend on `T`, so the assertion can never succeed for any instantiation, and a non-dependent assertion is checked when the template is defined, not when a branch is chosen. Under the C++17 and C++20 rules the template is ill-formed, and GCC 12 rejects it even if `put` is never called. The fix is to make the condition dependent, as in `always_false<T>` above. C++23 (paper P2593) changed the rule so that `static_assert(false)` is only evaluated when the branch is instantiated; GCC 13 and Clang 17 implement it, but on a C++17 or C++20 code base, keep the dependent-false helper.

### the takeaway

`if constexpr` skips instantiation, not parsing, and only inside templates; folds turn "for each argument" into one expression whose order and empty-pack behavior you choose. Together they replace most SFINAE overload sets and recursive variadic helpers, at the cost of putting a closed set of cases in one place.

### optional challenge

Which of these compile when called with no arguments, and what do they return?

```cpp
template <class... Ts> auto a(Ts... xs) { return (xs + ...); }
template <class... Ts> auto b(Ts... xs) { return (xs && ...); }
template <class... Ts> auto c(Ts... xs) { return (0 + ... + xs); }
```

<details>
<summary>answer</summary>

`a()` does not compile: a unary fold over `+` with an empty pack is ill-formed. `b()` compiles and returns `true` (type `bool`), because `&&` is one of the three operators with a defined empty value. `c()` compiles and returns `0` (type `int`), because a binary fold just yields its initial value when the pack is empty. Note that `c` is a left fold; for `+` on numbers the direction does not change the value, but it does change the order of evaluation and, with mixed types, the intermediate types.

</details>
