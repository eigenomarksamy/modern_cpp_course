---
title: consteval and constinit
standard: C++20
objective: use consteval for functions that must run at compile time and constinit for mutable globals that must be initialized before any constructor runs
prerequisites: constexpr-evolution
difficulty: 2
---

### the idea

C++20 gives you three keywords for this, and they make three different promises. `constexpr` says "can run at compile time". `consteval` says "must run at compile time". `constinit` says "this variable is initialized at compile time, but it is not a constant". mixing them up is the most common mistake in this area.

the difference matters in exactly the places compile-time code is most useful: validating constants that would otherwise be checked at run time (or never), and making mutable globals safe from the initialization order problems in [[storage-duration]].

### understanding the concept

**`consteval`** declares an *immediate function*: every call must be a constant expression, or the program is ill-formed. that turns "this should be folded" into "this is checked". because a `throw` reached during constant evaluation is an error, a `consteval` function that throws on bad input becomes a compile-time validator. that is exactly how C++20 checks `std::format` strings ([[format]]): `std::format_string` has a `consteval` constructor that parses the literal.

**`constinit`** applies to variables with static or thread storage duration. it asserts that the variable is constant-initialized (initialized before any dynamic initialization runs), and makes it an error if it is not. the variable stays mutable. it answers [[storage-duration]]'s fiasco for globals that must be mutable: a `constinit` counter or pointer is valid before any constructor in any translation unit runs.

**`std::is_constant_evaluated()`** (`<type_traits>`) returns `true` when called during constant evaluation, so a `constexpr` function can use a portable loop at compile time and an intrinsic or `memcpy` at runtime. use it with plain `if`, never `if constexpr` (see "watch out for"). C++23's `if consteval` is a cleaner spelling; it is not C++20.

### in code

**`consteval` and `constinit`.**

```cpp complete
#include <cstdint>
#include <numbers>

consteval double deg_to_rad(double deg) { return deg * std::numbers::pi / 180.0; }

consteval std::uint8_t can_channel(int ch) {
    if (ch < 0 || ch > 15) throw "CAN channel out of range";   // compile-time diagnostic
    return static_cast<std::uint8_t>(ch);
}

constexpr double joint_limit = deg_to_rad(170.0);   // 2.967060
constexpr auto steering_bus  = can_channel(3);
// can_channel(16);    error: expression '<throw-expression>' is not a constant expression
// deg_to_rad(runtime_angle);  error: the value of 'runtime_angle' is not usable in a constant expression

int compute_default();
constinit int retry_budget = 5;                    // OK: mutable, initialized before any constructor
// constinit int bad = compute_default();
// error: 'constinit' variable 'bad' does not have a constant initializer
```

`deg_to_rad` as `consteval` is a design choice: it says "this conversion is for constants in source code", and a runtime angle must go through a different (runtime) function. that keeps an accidental per-cycle conversion out of a control loop, but it also means you cannot reuse it at runtime. choose `constexpr` when both uses are legitimate.

### in practice

`constinit` is the C++20 answer for mutable globals that other startup code may touch, which is common in embedded and real-time code: a statistics counter, a pointer to the active configuration, a flag set by an interrupt handler.

```cpp complete
#include <atomic>

constinit std::atomic<unsigned> g_dropped_frames{0};   // valid before any constructor runs
constinit const char* g_active_profile = "default";    // mutable pointer, constant initializer
```

both are initialized before any dynamic initialization in any translation unit, so a static constructor elsewhere can safely increment the counter or read the profile. and if a later edit changes either initializer into something that needs code at startup, the build fails instead of quietly reintroducing the ordering problem. `consteval` plays the same role for constants: register addresses, bus channels, unit conversions, and format strings ([[format]]) can be validated where they are written, so an out-of-range value never reaches the hardware.

### watch out for

**`if constexpr (std::is_constant_evaluated())` is always true**, because the condition of `if constexpr` is itself a constant evaluation. your runtime branch becomes dead code. GCC 12 warns: "'std::is_constant_evaluated' always evaluates to true in 'if constexpr'". use a plain `if`.

### the takeaway

`constexpr` means "may run at compile time", `consteval` means "must", and `constinit` means "initialized at compile time, mutable afterwards". use compile-time evaluation to remove startup ordering problems and to turn checks into build errors, and weigh it against build time, binary size, and debuggability.

### optional challenge

```cpp complete
constexpr int sq(int x) { return x * x; }
int g = sq(4);                 // namespace scope

int main() {
    int l = sq(4);             // local
}
```

is `g` guaranteed to be initialized at compile time? is `l`? what changes if you write `constinit int g = sq(4);`?

<details>
<summary>answer</summary>

`g` is guaranteed: a variable with static storage duration whose initializer is a constant expression undergoes *constant initialization*, which happens before any dynamic initialization. that is a language rule, not an optimization. `l` is not guaranteed: it is an ordinary local, and whether `sq(4)` is folded is up to the compiler. (GCC 12 happens to fold it even at `-O0`; that is an implementation choice, not a guarantee.)

`constinit` does not change the behavior of `g`; it adds a check. if someone later changes `sq` so it is no longer `constexpr`, plain `int g = sq(4);` silently becomes dynamic initialization, and the [[storage-duration]] ordering problem is back. with `constinit`, that change is a compile error.

</details>

### going deeper

#### class types as template arguments

C++20 also allows class types as non-type template parameters, if they are *structural* (public members, no `mutable`, all members structural). a small `fixed_string` lets a string literal become part of a type, so `Counter<"dropped_frames">` and `Counter<"crc_errors">` are distinct types with their own static storage. libraries use this for compile-time format strings, units, and register maps.
