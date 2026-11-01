---
title: views and lifetimes: what a pipeline refers to
standard: C++20
objective: tell which views refer to their data and which own it, and avoid pipelines that outlive their source or a modification of it
prerequisites: views
difficulty: 3
---

### the idea

this function compiles without a warning on GCC 12, returns a perfectly ordinary-looking pipeline, and every use of its result is undefined behavior:

```cpp
auto strong_ids() {
    std::vector<int> ids = load();
    return ids | std::views::filter([](int i) { return i > 2; });   // BUG: refers to a dead local
}
```

a view is closer to a reference than to a container: it stores *how* to produce elements, not the elements. knowing exactly what each pipeline refers to is the price of laziness.

### understanding the concept

what does a view hold? `views::all` decides. for an lvalue container it creates a `ref_view`: a pointer to your container. for an rvalue container it creates an `owning_view` that moves the container in. (`owning_view` came from P2415, a defect report applied to C++20; GCC 12, recent Clang and MSVC implement it. before it, piping an rvalue container did not compile.) so "views do not own" is true for lvalues, which is the common case and the dangerous one.

ranges that are safe to outlive (like `std::string_view` or `std::span`) opt in as *borrowed ranges*, and for those you get a real iterator.

### in code

iterating the result is undefined behavior, and GCC 12 compiles it without a warning. return `std::move(ids) | ...` (an `owning_view`) or return the container. the same trap appears in range-for: `for (int x : next_frame().data() | std::views::take(2))` is UB if `data()` returns a reference into the temporary frame, because the frame dies at the end of the range initializer. (C++23 extends temporary lifetimes in range-for initializers; C++20 does not.)

the fixed version moves the vector into the pipeline, so the returned view owns it:

```cpp
auto strong_ids_fixed() {
    std::vector<int> ids = load();
    return std::move(ids) | std::views::filter([](int i) { return i > 2; });   // owning_view
}
```

returning the filtered *container* is often clearer still: callers then hold ordinary data with no lifetime puzzle attached.

### in practice

a robust convention for APIs that use ranges: **accept views, return owning data.** a function that consumes a sequence takes its parameter as `auto&&` or a constrained template (`std::ranges::input_range auto&& r`), so callers can pass containers, views, or pipelines without copying. a function that produces a sequence returns a container, or a view only when the view's source is clearly owned by something longer-lived, such as a member of the object the function is called on, and that relationship is documented. pipelines then live as local variables in the code that iterates them, which is exactly the scope in which their references are obviously valid.

### watch out for

**`filter_view` caches `begin()`.** to make `begin()` amortized O(1), `filter_view` finds the first match on the first call and remembers it. consequences:

- `begin()` is non-const, so `void dump(const auto& r)` will not accept a filter view. take views by value or by forwarding reference (`auto&&`) instead.
- modifying an element through a filter iterator so that it no longer satisfies the predicate is UB, by the standard's own wording.
- changing the underlying container after the first iteration can leave the cached iterator stale (see the challenge).

### the takeaway

views over lvalues refer to their source and views over rvalues own it; keep pipelines local to the code that iterates them, do not keep a view across modifications of what it views, and return owning data from functions.

### optional challenge

```cpp
std::vector<int> v{1, 2, 3, 4};
auto evens = v | std::views::filter([](int x) { return x % 2 == 0; });
v.push_back(6);
for (int x : evens) std::printf("%d ", x);
```

is this well-defined, and what does it print? does the answer change if you insert a `for (int x : evens) {}` loop before the `push_back`?

<details>
<summary>answer</summary>

as written it is fine and prints `2 4 6`. the view holds a `ref_view` (a pointer to `v` itself, not to its buffer) and has not cached anything yet, so iteration starts from the current `v.begin()`.

if you iterate first, `filter_view` caches an iterator to the `2`. the `push_back` may reallocate (with libstdc++ it does: the capacity after list-initialization is exactly 4), which invalidates that cached iterator, and the next loop starts from it: undefined behavior. the rule of thumb: do not keep a view across modifications of what it views. recreate it; it is cheap.

</details>
