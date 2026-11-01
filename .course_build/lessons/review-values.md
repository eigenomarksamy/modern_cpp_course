---
title: review: references, values, and the language contract
kind: review
standard: C++17
objective: consolidate temporaries and dangling, pointers and references, const, value categories, copy elision, and undefined behavior
prerequisites: temporaries-dangling, pointers-references, const-correctness, value-categories, copy-elision, undefined-behavior, ub-usual-suspects
difficulty: 1
---

### recap

| lesson | key idea |
|---|---|
| [[temporaries-dangling]] | temporaries die at the end of the full-expression unless bound *directly* to a local reference; nothing extends through a function call. |
| [[pointers-references]] | references are non-null, non-rebindable aliases; pointers are nullable, rebindable, and do arithmetic within one array. |
| [[const-correctness]] | `const` is a read-only view and an API contract, shallow on pointer members, and something callers and threads rely on. |
| [[value-categories]] | every expression has a type and a value category; named variables are lvalues, even `T&&` ones. |
| [[copy-elision]] | in C++17 a prvalue is an initializer, so returning one needs no copy or move constructor; NRVO is still optional. |
| [[undefined-behavior]] | implementation-defined, unspecified, undefined: the optimizer assumes UB never happens, so a bug can delete your checks. |
| [[ub-usual-suspects]] | reinterpret bytes with `memcpy` or `bit_cast`, never depend on argument evaluation order, and let sanitizers find the rest. |

the thread through the module: the standard defines an abstract machine, and most surprises come from the gap between that machine and "it is just memory and instructions".

### review questions

1. one of these lines dangles and the other is fine. explain the difference in terms of value categories and lifetime extension.

   ```cpp
   const Frame& f = make_frame();            // make_frame returns Frame by value
   const int&   m = std::max(lo(), hi());    // lo and hi return int by value
   ```

2. a colleague says "the order in which `f(read_header(), read_body())` evaluates its arguments is undefined behavior, just like signed overflow." what is right and wrong about that, and why does the difference matter?
3. a `const` member function fills a `mutable` cache without taking a lock. it compiles and passes single-threaded tests. why is it still a bug, and under what condition would it be fine?
4. `RegisterBlock` has deleted copy and move constructors. does `return RegisterBlock{base};` compile in C++17? does `RegisterBlock b{base}; return b;`?
5. from [[linkage-odr]]: why does marking a header variable `static` make a duplicate-symbol error go away, and why is that usually the wrong fix?

### mini exercise

this helper has three bugs from this module: one lifetime bug and two kinds of undefined behavior. one line that looks suspicious is fine. find all four, then rewrite the function.

```cpp complete
#include <vector>

struct Track { int id = 0; std::vector<float> ranges; };
std::vector<Track> load_tracks();

const float& latest_range(int id) {
    const auto& tracks = load_tracks();
    int index;
    for (std::size_t i = 0; i < tracks.size(); ++i)
        if (tracks[i].id == id) index = i;
    const Track& t = tracks[index];
    return t.ranges[t.ranges.size() - 1];
}
```

### answers

<details>
<summary>answer 1: lifetime extension</summary>

`make_frame()` is a prvalue; binding it directly to `const Frame&` materializes a temporary and extends its life to `f`'s. `std::max(lo(), hi())` is an lvalue (it returns `const int&`): the temporaries from `lo()` and `hi()` were bound to `std::max`'s parameters, which keeps them alive only until the end of the full-expression. extension never passes through a function returning a reference, so `m` dangles at the `;`. `int m = std::max(lo(), hi());` copies the value in time.

</details>

<details>
<summary>answer 2: unspecified versus undefined</summary>

the order is *unspecified*: since C++17 each argument is evaluated completely before the next starts, and either order is a valid execution, so a program correct for both orders is correct. signed overflow is *undefined*: there is no valid execution, and the optimizer may delete code on the assumption it never happens. unspecified order is a portability bug (here, possibly reading the body before the header), fixed by naming intermediate results; UB can corrupt unrelated logic and must be removed.

</details>

<details>
<summary>answer 3: logical constness and threads</summary>

callers, generic code, and the standard library assume that `const` member functions can be called concurrently on the same object. two threads calling the function at once both write the cache: a data race, which is undefined behavior. it is fine only if the object is never shared between threads, or if the `mutable` member is synchronized (a mutex, or an atomic for a simple flag). adding `mutable` makes you responsible for that member's thread safety.

</details>

<details>
<summary>answer 4: guaranteed elision</summary>

`return RegisterBlock{base};` compiles: the prvalue initializes the caller's object directly, and no copy or move constructor is needed or even looked up. `RegisterBlock b{base}; return b;` does not: NRVO is optional, so the language still requires an accessible copy or move constructor, and both are deleted.

</details>

<details>
<summary>answer 5: static in a header</summary>

`static` gives the variable internal linkage, so each translation unit gets its own private object and the linker has nothing to collide. the program now has several variables where the author meant one: an increment in one file is invisible in another. for one shared object, use an `inline` variable (C++17); for one per file, use an anonymous namespace in the `.cpp`.

</details>

<details>
<summary>mini exercise answer</summary>

- **fine (the decoy):** `const auto& tracks = load_tracks();` binds a prvalue directly to a `const&`, so the vector lives until the function returns.
- **UB, uninitialized read:** if no track has the requested `id`, `index` is never assigned and `tracks[index]` reads an indeterminate value.
- **UB, out of bounds:** if the track has no ranges, `t.ranges.size() - 1` wraps to the largest `std::size_t`, and indexing with it is out of bounds.
- **lifetime:** the returned reference points into `tracks`, which is destroyed when the function returns, so every caller gets a dangling reference.

```cpp
#include <optional>
#include <vector>

std::optional<float> latest_range(int id) {
    const auto tracks = load_tracks();        // owned locally, by value
    for (const Track& t : tracks)
        if (t.id == id && !t.ranges.empty())
            return t.ranges.back();           // copy the float out while tracks is alive
    return std::nullopt;                      // not found, or no ranges yet
}
```

`std::optional` gets its own lesson in [[optional]]. if loading every track is expensive, the deeper fix is an API change: the caller owns the track list and passes it in by `const&`.

</details>

### connections

the first two modules described what the language guarantees and what it leaves to you. the next one turns those guarantees into design techniques: [[raii]] relies on deterministic destruction, [[constructors]] is where initialization meets class invariants, and the value categories from [[value-categories]] are the entire mechanism behind [[move-semantics]]. undefined behavior returns whenever threads share data, in [[data-races]].
