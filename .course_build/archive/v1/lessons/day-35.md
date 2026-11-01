<a id="day-35"></a>

## day 35: week 5 review: the C++20 toolbox

**reading time:** about 8 minutes · **standard:** C++20 · **builds on:** days 29 to 34

### recap

| day | idea in one line |
|---|---|
| [29](#day-29) | Concepts move a template's requirements into its signature; build them from standard concepts so subsumption works, and remember they constrain callers, not the body. |
| [30](#day-30) | Views are lazy recipes; they reference lvalues and own rvalues (`owning_view`), `filter_view` caches `begin()`, and C++20 has no `ranges::to`. |
| [31](#day-31) | `std::span<const T>` replaces pointer plus length; pass by value, use a static extent for fixed-size contracts, never let it outlive its buffer. |
| [32](#day-32) | Default `<=>` for member-wise order; write `<=>` and `==` together when the order is custom; a `float` member makes the order partial. |
| [33](#day-33) | `constexpr` may run at compile time, `consteval` must, `constinit` initializes at compile time and stays mutable. |
| [34](#day-34) | `std::format` is type-safe and checked at compile time through `std::format_string`; `format_to_n` avoids the result allocation; small C++20 additions remove bug patterns. |

The theme of the week: C++20 lets you state more of a contract in the type system (what a template needs, how many elements a buffer has, what kind of order a type has, what must happen at compile time) and have the compiler enforce it at the call site.

### review questions

1. A driver type passes `static_assert(Sensor<LidarDriver>)`, yet `JointController<LidarDriver>` fails to compile with an error inside `JointController::update()`. How is that possible, and what practice reduces the risk?

2. Which of these is undefined behavior, and why is the other one fine?

   ```cpp
   std::vector<int> load_ids();                       // returns by value
   struct Config { const std::vector<int>& ids() const; };
   Config config();                                   // returns by value

   auto evens = load_ids() | std::views::filter(is_even);              // (a)
   for (int id : evens) use(id);
   for (int id : config().ids() | std::views::take(3)) use(id);        // (b)
   ```

3. A tracker keeps `std::set<Detection>`, where `Detection` has a `float range_m` member and `auto operator<=>(const Detection&) const = default;`. One radar frame contains a NaN range. What is wrong, precisely, and what are two reasonable fixes?

4. Pick `constexpr`, `consteval`, or `constinit` for each: (a) a global, mutable `Logger* g_logger` that must be valid before any static constructor in any translation unit runs; (b) a function that validates CAN channel numbers written as literals in source code and must reject bad ones at build time; (c) a CRC function used both in `static_assert` tests and on runtime packets.

5. Why should a project's `log_info` wrapper take `std::format_string<Args...>` rather than `std::string_view` for its format parameter?

6. **From week 4.** `std::string_view name = make_name();` (where `make_name` returns `std::string`) and `std::span<const float> s = make_samples();` (returning `std::vector<float>`) both compile. What is the shared problem, and why does `std::span<float> s = make_samples();` not compile?

7. **From week 2.** `Frame` has a user-written move constructor without `noexcept` and a copy constructor. When a `std::vector<Frame>` reallocates, are the elements moved or copied, and why?

### mini exercise

Write a constrained function `rms` that takes a `std::span` of numeric samples (integers or floating point, but not `bool`), returns an empty `std::optional<double>` for an empty span, and works when called directly with a `std::vector<float>` or a `std::array<std::int16_t, N>`. Then print the result with `std::format` to three decimals. Hint: try calling your first version with a `std::vector<float>` before reading the answer.

### answers

<details>
<summary>1. concept satisfied, body fails</summary>

Concepts are checked at the call site against the template arguments; C++20 does not check a template's body against its concepts. If `update()` calls `s.flush()` and `Sensor` never required `flush()`, the driver satisfies the concept and still fails during instantiation (day 29). Keep the concept in sync with what the body uses, and test the template with a minimal *archetype* type that provides exactly what the concept requires and nothing more: if the template compiles with the archetype, the concept is complete.

</details>

<details>
<summary>2. owning versus referencing views</summary>

(a) is fine. `load_ids()` is an rvalue, so `views::all` wraps it in an `owning_view` that moves the vector into the pipeline (P2415, a defect report against C++20). The view owns its data.

(b) is UB. `config().ids()` is an lvalue reference into the temporary `Config`, so the pipeline holds a `ref_view` to it. The temporary is destroyed at the end of the range initializer, before the loop body runs (C++23 extends temporary lifetimes in range-for initializers; C++20 does not). GCC 12 compiles both without a warning (day 30).

</details>

<details>
<summary>3. NaN in a set</summary>

A `float` member makes the defaulted `<=>` return `std::partial_ordering`, and with NaN, `<` is not a strict weak ordering: the NaN detection is "equivalent" to everything, which breaks transitivity of equivalence. `std::set` requires a strict weak ordering over the values it holds, so violating it is undefined behavior (typical symptoms: lookups that miss and duplicates that should have been rejected). The defaulted `==` is not even reflexive for that element.

Fixes: reject or sanitize NaN at the driver boundary, so the invariant "range is finite" holds for every `Detection`; or define the ordering with `std::strong_order` on the float (IEEE `totalOrder`) or on a non-float key such as a track id (day 32).

</details>

<details>
<summary>4. compile-time keywords</summary>

(a) `constinit Logger* g_logger = nullptr;`: constant-initialized, so it is valid before any dynamic initialization, and still assignable later. (b) `consteval`: every call must be a constant expression, and a `throw` reached during evaluation becomes a compile error. (c) `constexpr`: usable in constant expressions and at runtime (day 33).

</details>

<details>
<summary>5. format_string in wrappers</summary>

The compile-time check lives in the `consteval` constructor of `std::format_string<Args...>`, which runs when the caller's string literal is converted to the parameter type. A wrapper taking `std::format_string<Args...>` performs that conversion at *its* caller, against the real argument types, so a missing argument or bad spec fails there. A `std::string_view` parameter cannot be passed to `std::format` (it is not a constant expression), and switching to `std::vformat` moves every format error to runtime as `std::format_error` (day 34).

</details>

<details>
<summary>6. from week 4: views into temporaries</summary>

Both are non-owning views bound to a temporary that is destroyed at the end of the full-expression, so both dangle immediately (days 26 and 31). They compile because read-only views are deliberately constructible from temporaries, so that `f(make_name())` and `rms(make_samples())` work as function arguments, where the temporary lives long enough. A span of *mutable* elements refuses an rvalue container that is not a borrowed range, because writing into a temporary is almost always a bug. The rule: views are fine as parameters, suspicious as locals initialized from a call.

</details>

<details>
<summary>7. from week 2: noexcept and reallocation</summary>

Copied. To keep the strong exception guarantee for `push_back` and `emplace_back`, `std::vector` moves elements during reallocation only if the move constructor is `noexcept` (or the type is not copyable); otherwise it copies, via `std::move_if_noexcept` (day 10). A test with a printing `Frame` on GCC 12 prints `copy`. Mark the move constructor `noexcept`, or better, follow the rule of zero (day 11) and let the compiler generate it from members whose moves are already `noexcept`.

</details>

<details>
<summary>mini exercise: one solution</summary>

```cpp
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

The trap the hint points at is day 18's rule meeting day 31's type: template argument deduction does not consider implicit conversions, so a function template taking `std::span<const T>` cannot be called with a vector, an array, or even a `std::span<float>` (mutable elements) without help. The options are an explicit argument (`rms<float>(v)`), a non-template function for the one type you need, or a forwarding overload like the one above. The `!std::same_as<T, bool>` matters because `bool` is an integral type, and "the RMS of a bool vector" is almost certainly a bug; `std::vector<bool>` is also not a contiguous range, so it is rejected either way.

</details>

### connections

- **Back to weeks 1 to 4.** Concepts replace the `enable_if` and SFINAE machinery of day 18 and many `if constexpr` dispatch chains of day 23. Range algorithms and views extend day 16's algorithms and day 17's lambdas. `std::span` generalizes day 26's `string_view` and fixes day 04's pointer-plus-length parameters. `constinit` closes day 03's static initialization order fiasco for globals, and `std::bit_cast` is day 06's answer to type punning. Defaulted comparisons are a rule-of-zero idea (day 11) applied to operators.
- **Ahead.** Week 6 brings concurrency: `std::jthread` and `std::stop_token` (day 36) are C++20 library types in the same spirit as this week. Concepts return as compile-time dependency injection (day 44) and in the static versus dynamic polymorphism comparison (day 46). `std::span` and `std::string_view` come back as API design tools (day 47), `std::format` and `std::source_location` in logging and observability (day 53), and the capstone pipeline (day 55) combines a defaulted comparison, a concept, `std::span`, and a range pipeline in one program.

