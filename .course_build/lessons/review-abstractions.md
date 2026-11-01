---
title: review: polymorphism choices, APIs, modules, and coroutines
kind: review
standard: C++20
objective: consolidate the polymorphism options and type erasure, API contracts and ABI stability, modules, and coroutines
prerequisites: static-polymorphism, type-erasure, api-contracts, api-stability, modules, coroutines, coroutine-generator
difficulty: 2
---

### recap

| lesson | key idea |
|---|---|
| [[static-polymorphism]] | virtual functions, templates with concepts, `std::variant`, and type erasure fit different shapes of "one call, many types". |
| [[type-erasure]] | a template constructor captures the type in a private model; users get value semantics without inheritance. |
| [[api-contracts]] | contracts go into types first: strong types, enums, views, `[[nodiscard]]` result types. |
| [[api-stability]] | an ABI is stricter than an API: pimpl, no inline private logic in public headers, deprecate before removing. |
| [[modules]] | compiled interfaces instead of pasted text; adopt from the leaves inward as tooling allows. |
| [[coroutines]] | state lives in a frame across suspensions; take parameters by value. |
| [[coroutine-generator]] | `promise_type` decides when a coroutine starts, what `co_yield` does, and who destroys the frame. |

### review questions

1. a radar processing chain passes about a dozen message types defined by a versioned interface document, and a hot loop dispatches on them. separately, third-party detection plugins are loaded from shared libraries at startup. which polymorphism mechanism fits each, and why?
2. a pimpl class compiles in its own `.cpp` file but every client fails with an error about applying `sizeof` to an incomplete type. what is missing, and why does the fix work?
3. predict the problem:

   ```cpp
   Generator<std::string_view> fields(std::string_view line);   // splits on commas, lazily
   std::string read_line();

   auto f = fields(read_line());
   while (f.next()) use(f.value());
   ```

4. a type-erased wrapper declares `template <typename T> Wrapper(T&& value);` with no constraint. what happens on `Wrapper copy = original;` when `original` is a non-const `Wrapper`, and which earlier lesson predicted this?
5. a public function is `bool deploy(char* host, int port, double timeout, bool force, bool dry_run);`. name three changes that make it hard to misuse, and the lesson each comes from.

### mini exercise

a header-only library exposes `class Tracker { public: void update(const Frame&); private: std::vector<Track> tracks_; KalmanFilter kf_; };` and is about to become a prebuilt shared library. sketch the header you would ship, and list what clients can no longer depend on.

### answers

<details>
<summary>answer 1: radar messages and plugins</summary>

the internal messages are a closed, versioned set: `std::variant` with `std::visit`. value semantics, no per-message heap allocation, and adding a type forces every visitor to be updated (with an `overloaded` visitor lacking a catch-all, a missing case fails to compile). templates alone cannot hold mixed types in one stream. the plugins form an open set that crosses a shared-library boundary: a virtual interface plus an `extern "C"` factory, because templates cannot cross that boundary and a variant cannot be extended by someone else. if the hot loop ever shows the dispatch in a profile, that is the time to reconsider, not before.

</details>

<details>
<summary>answer 2: pimpl and the incomplete type</summary>

the class does not declare its destructor (and probably its move operations), so the compiler defines them implicitly and inline, in every client translation unit. they destroy the `std::unique_ptr<Impl>`, and `std::default_delete<Impl>` requires `Impl` to be complete, which it is only in the class's own `.cpp`. declaring `~Widget();` and the move operations in the header and defining them as `= default` in the `.cpp` (after `Impl` is defined) moves the code that destroys `Impl` to the one place where it is complete.

</details>

<details>
<summary>answer 3: the lazy splitter</summary>

`read_line()` returns a temporary `std::string`. the `std::string_view` parameter is copied into the coroutine frame, but it points into that temporary, which is destroyed at the end of the full-expression `auto f = fields(read_line());`. because the generator starts lazily, all of the splitting happens later, reading freed memory: undefined behavior. every yielded `string_view` would also point into the dead string. fix: take `std::string line` by value so the frame owns the text, and make sure consumers are done with each yielded view before the generator is destroyed, or yield `std::string` values.

</details>

<details>
<summary>answer 4: the greedy forwarding constructor</summary>

for a non-const lvalue, `T` deduces to `Wrapper&`, so the template's parameter is `Wrapper&`: an exact match, better than the copy constructor's `const Wrapper&`. the template wins and wraps a `Wrapper` inside the wrapper (or fails to compile in some confusing way). [[forwarding-references]] called this the hijacked copy constructor; [[static-polymorphism]]'s challenge showed why a by-value parameter avoids it. fix by constraining: `requires (!std::same_as<std::remove_cvref_t<T>, Wrapper>)`.

</details>

<details>
<summary>answer 5: a signature that states its contract</summary>

`std::string_view host` instead of `char*` (borrowing, no null-termination assumptions: [[string-view]]); `std::chrono::milliseconds timeout` instead of a unitless `double`, and enums or an options struct instead of two adjacent `bool`s ([[api-contracts]]); and a `[[nodiscard]]` result type that says why it failed instead of a `bool` that is easy to ignore ([[error-strategy]]).

</details>

<details>
<summary>mini exercise answer</summary>

```cpp complete
// tracker.h: the shipped header
#pragma once
#include <memory>

struct Frame;

class Tracker {
public:
    Tracker();
    ~Tracker();                                   // defined in the .cpp, where Impl is complete
    Tracker(Tracker&&) noexcept;
    Tracker& operator=(Tracker&&) noexcept;
    void update(const Frame& frame);
private:
    struct Impl;                                  // tracks_, kf_, and anything added later
    std::unique_ptr<Impl> impl_;
};
```

clients can no longer depend on `sizeof(Tracker)` changing with its members, on including `KalmanFilter`'s header transitively, or on inlining `update`. in exchange, the library can add members and change its filter without breaking binaries built against this header. a factory returning `std::unique_ptr<TrackerInterface>` would be the alternative if the library also wants to hide which tracker implementation is in use.

</details>

### connections

the last two modules were about structure rather than mechanism: where seams go, how components are wired, and what an interface promises over time. the final modules turn to production engineering: measuring performance honestly, designing data for the cache, controlling allocation, testing and observing running systems, and changing legacy code safely, before putting the whole course together in one small program.
