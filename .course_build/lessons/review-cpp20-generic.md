---
title: review: concepts, ranges, and span
kind: review
standard: C++20
objective: consolidate concepts, range algorithms, view pipelines and their lifetimes, and `std::span`
prerequisites: concepts, writing-concepts, range-algorithms, views, view-lifetimes, span
difficulty: 2
---

### recap

| lesson | key idea |
|---|---|
| [[concepts]] | requirements move from the template body into its signature; errors name the unmet concept at the call site. |
| [[writing-concepts]] | a requires expression states a contract; build on standard concepts so subsumption works, and `static_assert` types against it. |
| [[range-algorithms]] | pass whole ranges and use projections instead of comparison lambdas. |
| [[views]] | pipelines are lazy recipes: callables run per element, on iteration, possibly more than once. |
| [[view-lifetimes]] | views over lvalues refer, views over rvalues own; keep pipelines local and return owning data. |
| [[span]] | pointer plus length as one value: `span<const T>` to read, `span<T>` to write, static extent as a contract. |

### review questions

1. a driver type passes `static_assert(Sensor<LidarDriver>)`, yet `JointController<LidarDriver>` fails to compile with an error inside `JointController::update()`. how is that possible, and what practice reduces the risk?
2. which of these is undefined behavior, and why is the other one fine?

   ```cpp
   std::vector<int> load_ids();                       // returns by value
   struct Config { const std::vector<int>& ids() const; };
   Config config();                                   // returns by value

   auto evens = load_ids() | std::views::filter(is_even);              // (a)
   for (int id : evens) use(id);
   for (int id : config().ids() | std::views::take(3)) use(id);        // (b)
   ```
3. two overloads are constrained with `requires std::is_integral_v<T>` and `requires std::is_integral_v<T> && (sizeof(T) == 4)`. why is `g(1)` ambiguous, and what one change makes the second overload win?
4. from [[string-view]]: `std::string_view name = make_name();` (where `make_name` returns `std::string`) and `std::span<const float> s = make_samples();` (returning `std::vector<float>`) both compile. what is the shared problem, and why does `std::span<float> s = make_samples();` not compile?
5. from [[noexcept-moves]]: `Frame` has a user-written move constructor without `noexcept` and a copy constructor. when a `std::vector<Frame>` reallocates, are the elements moved or copied, and why?

### mini exercise

rewrite this C++17 helper with a range algorithm and a projection, and constrain it so that calling it with a range of something other than `Track` fails at the call site:

```cpp
const Track* most_confident(const std::vector<Track>& tracks) {
    if (tracks.empty()) return nullptr;
    auto it = std::max_element(tracks.begin(), tracks.end(),
        [](const Track& a, const Track& b) { return a.confidence < b.confidence; });
    return &*it;
}
```

### answers

<details>
<summary>answer 1: concept satisfied, body fails</summary>

concepts are checked at the call site against the template arguments; C++20 does not check a template's body against its concepts. if `update()` calls `s.flush()` and `Sensor` never required `flush()`, the driver satisfies the concept and still fails during instantiation ([[concepts]]). keep the concept in sync with what the body uses, and test the template with a minimal *archetype* type that provides exactly what the concept requires and nothing more: if the template compiles with the archetype, the concept is complete.

</details>

<details>
<summary>answer 2: owning versus referencing views</summary>

(a) is fine. `load_ids()` is an rvalue, so `views::all` wraps it in an `owning_view` that moves the vector into the pipeline (P2415, a defect report against C++20). the view owns its data.

(b) is UB. `config().ids()` is an lvalue reference into the temporary `Config`, so the pipeline holds a `ref_view` to it. the temporary is destroyed at the end of the range initializer, before the loop body runs (C++23 extends temporary lifetimes in range-for initializers; C++20 does not). GCC 12 compiles both without a warning ([[views]]).

</details>

<details>
<summary>answer 3: subsumption needs named concepts</summary>

subsumption compares constraints as atomic pieces, and two atomic constraints are the same only if they come from the same expression in the source. the two `std::is_integral_v<T>` are different expressions, so neither overload is more constrained than the other and the call is ambiguous. write `std::integral<T>` in both: the second overload's constraint then contains the first's, subsumes it, and wins for 32-bit types.

</details>

<details>
<summary>answer 4: views into temporaries</summary>

both are non-owning views bound to a temporary that is destroyed at the end of the full-expression, so both dangle immediately ([[string-view]] and [[span]]). they compile because read-only views are deliberately constructible from temporaries, so that `f(make_name())` and `rms(make_samples())` work as function arguments, where the temporary lives long enough. a span of *mutable* elements refuses an rvalue container that is not a borrowed range, because writing into a temporary is almost always a bug. the rule: views are fine as parameters, suspicious as locals initialized from a call.

</details>

<details>
<summary>answer 5: noexcept and reallocation</summary>

copied. to keep the strong exception guarantee for `push_back` and `emplace_back`, `std::vector` moves elements during reallocation only if the move constructor is `noexcept` (or the type is not copyable); otherwise it copies, via `std::move_if_noexcept` ([[noexcept-moves]]). a test with a printing `Frame` on GCC 12 prints `copy`. mark the move constructor `noexcept`, or better, follow the rule of zero ([[rule-of-zero]]) and let the compiler generate it from members whose moves are already `noexcept`.

</details>

<details>
<summary>mini exercise answer</summary>

```cpp
#include <algorithm>
#include <ranges>

template <std::ranges::forward_range R>
    requires std::same_as<std::ranges::range_value_t<R>, Track>
const Track* most_confident(const R& tracks) {
    auto it = std::ranges::max_element(tracks, {}, &Track::confidence);
    return it == std::ranges::end(tracks) ? nullptr : &*it;
}
```

the projection replaces the comparison lambda, the empty case falls out of the algorithm (it returns the end iterator), and the function now accepts any forward range of `Track`: a vector, a `std::span<const Track>`, or a filtered view of confirmed tracks (taken by `const&`, which a `filter_view` does not support, so pass such a view by value or `auto&&` in real code). a constraint like `std::same_as<..., Track>` is deliberately narrow; widening it is a design decision, not a default.

</details>

### connections

this module turned templates from a mechanism into an interface: concepts are what makes generic code readable at the call site, and ranges and span are the standard library's best examples of borrowing data instead of owning it. the next module rounds out the C++20 toolbox with comparisons, compile-time evaluation, and formatting, and then the course moves to threads, where every lifetime rule from these modules gets less forgiving.
