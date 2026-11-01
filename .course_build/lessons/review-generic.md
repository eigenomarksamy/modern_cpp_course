---
title: review: templates and generic programming
kind: review
standard: C++17
objective: consolidate deduction, class templates, forwarding references, variadic templates, if constexpr, and fold expressions
prerequisites: function-templates, class-templates, forwarding-references, variadic-templates, if-constexpr, fold-expressions
difficulty: 2
---

### recap

| lesson | key idea |
|---|---|
| [[function-templates]] | deduction is exact and per argument, instantiation needs the definition, dependent names need `typename` or `this->`. |
| [[class-templates]] | each argument set is a distinct class; CTAD deduces from constructors; specialize class templates, overload function templates. |
| [[forwarding-references]] | `T&&` with deduced `T` encodes the caller's value category; `std::forward<T>` replays it. |
| [[variadic-templates]] | a pack of forwarding references plus `std::forward<Args>(args)...` is the shape of every factory and `emplace`. |
| [[if-constexpr]] | the discarded branch is not instantiated (inside templates only); a closed set of cases lives in one place. |
| [[fold-expressions]] | one expression applies an operator across a pack; the comma fold runs in order. |

### review questions

1. which of these parameters are forwarding references?

   ```cpp
   template <class T> void a(T&& x);
   template <class T> void b(const T&& x);
   template <class T> struct S { void c(T&& x); };
   template <class T> void e(std::vector<T>&& x);
   auto&& d = make_frame();
   ```

2. why does `std::max(1, 2.0)` fail to compile when `std::max(1.0, 2.0)` and `1 < 2.0` are fine?
3. a wrapper forwards its argument twice: first to a logging function, then to the real consumer. what can go wrong, and how do you fix it?
4. in an `if constexpr` chain, why must the final "unsupported type" branch use something like `static_assert(always_false<T>, ...)` instead of `static_assert(false, ...)` in C++17 and C++20?
5. from [[callbacks]]: a function template takes `Pred&& keep` and calls it in a loop, while an older version took `const std::function<bool(const Point&)>&`. name one thing each version can do that the other cannot.

### mini exercise

write `all_in_range(lo, hi, xs...)`, a variadic function template that returns `true` when every value in `xs` lies in `[lo, hi]`, works for any mix of arithmetic types, returns `true` for an empty pack, and stops evaluating at the first failure.

### answers

<details>
<summary>answer 1: forwarding references</summary>

`a` and `d` only. a forwarding reference is exactly `T&&` (or `auto&&`) where `T` is deduced from that very argument. `b` adds `const`, `e` wraps `T` in another type, and in `S::c` the `T` was fixed when the class was instantiated, so nothing is deduced at the call: all three are plain rvalue references.

</details>

<details>
<summary>answer 2: deduction before conversion</summary>

`std::max` is `template <class T> const T& max(const T&, const T&)`. deduction runs per argument and must agree: the first says `int`, the second `double`, so deduction fails before any conversion is considered. the built-in `<` is not a template, so the usual arithmetic conversions apply. write `std::max<double>(1, 2.0)` or make the arguments agree.

</details>

<details>
<summary>answer 3: forwarding twice</summary>

`std::forward` on an rvalue argument produces an rvalue, so the logging function may move from it, and the real consumer then receives a moved-from object. forward only at the last use: pass the argument to the logger as an lvalue (or `const&`), and `std::forward` it to the consumer.

</details>

<details>
<summary>answer 4: dependent false</summary>

`static_assert(false)` does not depend on a template parameter, so under the C++17 and C++20 rules it is checked when the template is defined, and the template is ill-formed even if that branch is never chosen (GCC 12 rejects it outright). `always_false<T>` depends on `T`, so it is only evaluated when the branch is instantiated. C++23 relaxed the rule, but code targeting C++17 or C++20 needs the helper.

</details>

<details>
<summary>answer 5: templates versus std::function</summary>

the template can inline the predicate, accepts move-only callables (a closure owning a `unique_ptr`), and costs no allocation. the `std::function` version can be compiled once in a `.cpp` file, keeps a stable non-template signature (useful at library and ABI boundaries), and can be stored in a member or container of uniform type.

</details>

<details>
<summary>mini exercise answer</summary>

```cpp complete
template <class L, class H, class... Ts>
constexpr bool all_in_range(L lo, H hi, Ts... xs) {
    return ((lo <= xs && xs <= hi) && ...);
}

static_assert(all_in_range(0, 10));              // empty pack: true
static_assert(all_in_range(0, 10, 1, 2.5, 9u));
static_assert(!all_in_range(0.0, 1.0, 0.5, 2));
```

the unary `&&` fold gives `true` for an empty pack and short-circuits at the first `false`, so later elements are not evaluated. separate template parameters for `lo`, `hi`, and the pack let each argument keep its own type; the comparisons then use the usual arithmetic conversions, so mixing signed and unsigned integers would bring back the surprises from [[integer-types]]. a production version might constrain the parameters to arithmetic types, which [[concepts]] makes easy.

</details>

### connections

templates are the machinery under the library modules: `emplace_back` and `make_unique` are variadic forwarding templates, and algorithms are function templates over iterator types. the error-handling module next uses `if constexpr` and `std::variant` together, and the C++20 modules replace `enable_if` with concepts ([[concepts]]) and extend compile-time evaluation ([[constexpr-evolution]]). static polymorphism ([[static-polymorphism]]) returns to templates as a design tool rather than a mechanism.
