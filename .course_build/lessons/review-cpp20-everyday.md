---
title: review: comparisons, compile time, and formatting
kind: review
standard: C++20
objective: consolidate defaulted comparisons and categories, constexpr, consteval and constinit, `std::format`, and the small C++20 features
prerequisites: defaulted-comparisons, comparison-categories, constexpr-evolution, consteval-constinit, format, cpp20-small-features
difficulty: 2
---

### recap

| lesson | key idea |
|---|---|
| [[defaulted-comparisons]] | one defaulted `<=>` gives every relational operator and a defaulted `==`; declaration order is behavior. |
| [[comparison-categories]] | strong, weak, partial: a `float` member makes ordering partial, and NaN breaks algorithms that need a strict weak ordering. |
| [[constexpr-evolution]] | `constexpr` may run at compile time, including transient allocation; force it and test it with `static_assert`. |
| [[consteval-constinit]] | `consteval` must run at compile time; `constinit` initializes a mutable global before any constructor runs. |
| [[format]] | type-safe, compile-time checked formatting; keep the check in wrappers with `std::format_string`. |
| [[cpp20-small-features]] | small additions that each remove a bug pattern: designated initializers, `contains`, `erase_if`, `midpoint`, `ssize`. |

### review questions

1. a tracker keeps `std::set<Detection>`, where `Detection` has a `float range_m` member and `auto operator<=>(const Detection&) const = default;`. one radar frame contains a NaN range. what is wrong, precisely, and what are two reasonable fixes?
2. pick `constexpr`, `consteval`, or `constinit` for each: (a) a global, mutable `Logger* g_logger` that must be valid before any static constructor in any translation unit runs; (b) a function that validates CAN channel numbers written as literals in source code and must reject bad ones at build time; (c) a CRC function used both in `static_assert` tests and on runtime packets.

3. why should a project's `log_info` wrapper take `std::format_string<Args...>` rather than `std::string_view` for its format parameter?
4. from [[integer-types]]: `for (std::size_t i = v.size() - 1; i >= 0; --i)` never terminates. why, and how does a C++20 helper make the reverse loop correct?

### mini exercise

write a constrained function `rms` that takes a `std::span` of numeric samples (integers or floating point, but not `bool`), returns an empty `std::optional<double>` for an empty span, and works when called directly with a `std::vector<float>` or a `std::array<std::int16_t, N>`. then print the result with `std::format` to three decimals. hint: try calling your first version with a `std::vector<float>` before reading the answer.

### answers

<details>
<summary>answer 1: NaN in a set</summary>

a `float` member makes the defaulted `<=>` return `std::partial_ordering`, and with NaN, `<` is not a strict weak ordering: the NaN detection is "equivalent" to everything, which breaks transitivity of equivalence. `std::set` requires a strict weak ordering over the values it holds, so violating it is undefined behavior (typical symptoms: lookups that miss and duplicates that should have been rejected). the defaulted `==` is not even reflexive for that element.

fixes: reject or sanitize NaN at the driver boundary, so the invariant "range is finite" holds for every `Detection`; or define the ordering with `std::strong_order` on the float (IEEE `totalOrder`) or on a non-float key such as a track id ([[defaulted-comparisons]]).

</details>

<details>
<summary>answer 2: compile-time keywords</summary>

(a) `constinit Logger* g_logger = nullptr;`: constant-initialized, so it is valid before any dynamic initialization, and still assignable later. (b) `consteval`: every call must be a constant expression, and a `throw` reached during evaluation becomes a compile error. (c) `constexpr`: usable in constant expressions and at runtime ([[constexpr-evolution]]).

</details>

<details>
<summary>answer 3: format_string in wrappers</summary>

the compile-time check lives in the `consteval` constructor of `std::format_string<Args...>`, which runs when the caller's string literal is converted to the parameter type. a wrapper taking `std::format_string<Args...>` performs that conversion at *its* caller, against the real argument types, so a missing argument or bad spec fails there. a `std::string_view` parameter cannot be passed to `std::format` (it is not a constant expression), and switching to `std::vformat` moves every format error to runtime as `std::format_error` ([[format]]).

</details>

<details>
<summary>answer 4: the reverse loop</summary>

`i` is unsigned, so `i >= 0` is always true: after `i` reaches 0, `--i` wraps to the largest `std::size_t` and the loop indexes far out of bounds (and for an empty `v`, it starts there). use a signed index: `for (auto i = std::ssize(v) - 1; i >= 0; --i)`, where `std::ssize` returns `std::ptrdiff_t`.

</details>

<details>
<summary>mini exercise answer</summary>

```cpp complete
#include <cmath>
#include <concepts>
#include <format>       // GCC 13+; the rest compiles with GCC 12
#include <optional>
#include <ranges>
#include <span>

template <typename T>
concept Numeric = (std::integral<T> && !std::same_as<T, bool>) || std::floating_point<T>;

template <Numeric T>
std::optional<double> rms(std::span<const T> xs) {
    if (xs.empty()) return std::nullopt;
    double acc = 0.0;
    for (T x : xs) acc += static_cast<double>(x) * static_cast<double>(x);
    return std::sqrt(acc / static_cast<double>(xs.size()));
}

// Deduction does not look through conversions: rms(vec) cannot deduce T
// from span<const T> ("'std::vector<float>' is not derived from 'std::span<const T>'").
// This overload accepts any contiguous range of Numeric and forwards to the span version.
template <std::ranges::contiguous_range R>
    requires std::ranges::sized_range<R> && Numeric<std::ranges::range_value_t<R>>
std::optional<double> rms(const R& r) {
    using T = std::ranges::range_value_t<R>;
    return rms(std::span<const T>(std::ranges::data(r), std::ranges::size(r)));
}

// std::vector<float> v{3.f, 4.f};
// if (auto r = rms(v)) std::string line = std::format("rms {:.3f} over {} samples", *r, v.size());
//                                       // "rms 3.536 over 2 samples"
```

the trap the hint points at is [[function-templates]]'s rule meeting [[span]]'s type: template argument deduction does not consider implicit conversions, so a function template taking `std::span<const T>` cannot be called with a vector, an array, or even a `std::span<float>` (mutable elements) without help. the options are an explicit argument (`rms<float>(v)`), a non-template function for the one type you need, or a forwarding overload like the one above. the `!std::same_as<T, bool>` matters because `bool` is an integral type, and "the RMS of a bool vector" is almost certainly a bug; `std::vector<bool>` is also not a contiguous range, so it is rejected either way.

</details>

### connections

with this module the C++20 toolbox is complete: constrained templates, ranges and views, span, comparisons, compile-time evaluation, and formatting. none of it changes the foundations from the first modules; each feature makes an existing intent checkable. the next two modules are about threads, where the ownership and lifetime rules from the whole course meet a new kind of undefined behavior: data races ([[data-races]]).
