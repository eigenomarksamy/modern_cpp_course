---
title: fold expressions
standard: C++17
objective: apply an operator across a parameter pack with the right fold form, and use the comma fold for ordered per-argument work
prerequisites: if-constexpr
difficulty: 2
---

### the idea

before C++17, doing something for every element of a parameter pack meant recursion: a function that handles the first argument and calls itself with the rest, plus a base case for the empty pack. it works, it instantiates one function per pack length, and it hides a one-line intent ("log each field", "check that all values are finite") in a small machine. fold expressions write that intent as one expression.

### understanding the concept

**fold expressions** apply a binary operator across a parameter pack ([[variadic-templates]]). there are four forms, and the parentheses are part of the syntax:

| form | written | expands to (for `a, b, c`) |
|---|---|---|
| unary right | `(xs op ...)` | `a op (b op c)` |
| unary left | `(... op xs)` | `(a op b) op c` |
| binary right | `(xs op ... op init)` | `a op (b op (c op init))` |
| binary left | `(init op ... op xs)` | `((init op a) op b) op c` |

a unary fold over an empty pack is ill-formed except for three operators: `&&` gives `true`, `||` gives `false`, and the comma operator gives `void()`. for anything else, use a binary fold with an identity value. the comma fold is the workhorse for "do this for every argument": the built-in comma operator sequences its operands left to right, so `(f(xs), ...)` calls `f` in argument order. contrast that with function arguments, whose evaluation order is still unspecified ([[ub-usual-suspects]]).

### in code

now folds. predict the two results before reading the comments:

```cpp complete
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

put the two together and a whole telemetry frame becomes one line per message type, with the type checks done by the compiler:

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

passing a `std::vector<int>` as a field fails at compile time with the `static_assert` message rather than a page of overload-resolution notes. the costs are real but usually acceptable: every distinct list of field types instantiates a new `encode` (code size and compile time), and the format is native-endian, which is fine for same-host IPC and wrong for a wire protocol. measure compile time with `-ftime-report` (GCC) or `-ftime-trace` (Clang) if a header like this starts to dominate builds.

### watch out for

**the operand of a fold must be a single cast-expression.** anything with a binary operator inside needs its own parentheses:

```cpp complete
template <class... Ts> auto doubled_sum(Ts... xs) {
    // return (xs * 2 + ...);      // error: binary expression in the fold operand
    return ((xs * 2) + ... + 0);   // OK: the operand is parenthesized
}
```

the outer parentheses belong to the fold syntax, and the inner ones make `xs * 2` one operand. the same applies to the comma fold, which is why the logging example writes `((std::cout << xs << ' '), ...)`. with mixed argument types, also check what type the accumulation runs in: in `(xs + ... + 0)` the first step adds the init value's type to the last element's type, and the usual arithmetic conversions from [[integer-types]] apply at every step.

### the takeaway

a fold turns "for each argument" into one expression; choose left or right and unary or binary deliberately, give non-`&&`/`||`/comma folds an initial value, and use the comma fold when order matters.

### optional challenge

which of these compile when called with no arguments, and what do they return?

```cpp complete
template <class... Ts> auto a(Ts... xs) { return (xs + ...); }
template <class... Ts> auto b(Ts... xs) { return (xs && ...); }
template <class... Ts> auto c(Ts... xs) { return (0 + ... + xs); }
```

<details>
<summary>answer</summary>

`a()` does not compile: a unary fold over `+` with an empty pack is ill-formed. `b()` compiles and returns `true` (type `bool`), because `&&` is one of the three operators with a defined empty value. `c()` compiles and returns `0` (type `int`), because a binary fold just yields its initial value when the pack is empty. note that `c` is a left fold; for `+` on numbers the direction does not change the value, but it does change the order of evaluation and, with mixed types, the intermediate types.

</details>
