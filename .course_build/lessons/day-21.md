<a id="day-21"></a>

## day 21: week 3 review: the library as a vocabulary

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 15 to 20

### recap

| day | key idea |
|---|---|
| [15](#day-15) | A container is a contract: complexity, layout, and invalidation rules. Start with `std::vector`; reference stability is part of the interface. |
| [16](#day-16) | Algorithms see iterators, not containers: hence half-open ranges, erase-remove, `back_inserter`, and iterator categories. |
| [17](#day-17) | A lambda is an object whose members are its captures. Escaping lambdas must own what they use; `std::function` buys flexibility with an indirect call. |
| [18](#day-18) | Templates are recipes: deduction is exact, instantiation needs the definition, dependent names need `typename` and `this->`. |
| [19](#day-19) | `T&&` with deduced `T` remembers the caller's value category; `std::forward<T>` replays it, once. |
| [20](#day-20) | Basic, strong, nothrow: RAII makes basic cheap, work-then-commit makes strong possible, and the error channel is an API decision. |

The thread through the week: the standard library is a set of small, composable contracts, and generic code is how those contracts stay independent of the types they serve.

### review questions

1. You keep `Track*` pointers into a `std::unordered_map<int, Track>`. A burst of inserts triggers a rehash. Which of your pointers and iterators are still valid? What changes if someone replaces the map with a `std::vector<Track>` kept sorted by id?

2. Predict the output:

   ```cpp
   std::vector<int> v{5, 1, 4, 2, 3};
   int threshold = 2;
   auto above = [threshold](int x) { return x > threshold; };
   threshold = 4;
   std::cout << std::count_if(v.begin(), v.end(), above) << '\n';
   ```

3. Which of these parameters are forwarding references?

   ```cpp
   template <class T> void a(T&& x);
   template <class T> void b(const T&& x);
   template <class T> struct S { void c(T&& x); };
   template <class T> void e(std::vector<T>&& x);
   auto&& d = make_frame();
   ```

4. A vector of `Waypoint` copies every element when it grows, even though `Waypoint` has a move constructor. What is the most likely cause, and why does the library do this on purpose?

5. **From week 1.** Given the code below, is `a` safe to use on the next line? Is `b`?

   ```cpp
   struct Config {
       std::string name_;
       const std::string& name() const { return name_; }
   };
   Config load();

   const std::string& a = load().name_;
   const std::string& b = load().name();
   ```

6. **From week 2.** A teammate adds `~Telemetry() { log("closed"); }` to an otherwise rule-of-zero class holding a `std::vector<Sample>`. Everything still compiles. What did that change cost?

### mini exercise

This function is supposed to drop invalid detections, apply a range calibration, and return the ids of the three closest. It has two bugs, one of them undefined behavior. Rewrite it with algorithms and lambdas, keep it correct for fewer than three detections, and decide where a plain loop is still the clearest choice.

```cpp
#include <algorithm>
#include <vector>

struct Detection { int id; float range_m; bool valid; };

std::vector<int> closest_ids(std::vector<Detection>& dets, float scale) {
    for (auto it = dets.begin(); it != dets.end(); ++it) {
        if (!it->valid) dets.erase(it);
        else it->range_m *= scale;
    }
    std::sort(dets.begin(), dets.end(),
              [](const Detection& a, const Detection& b) { return a.range_m < b.range_m; });
    std::vector<int> ids;
    for (std::size_t i = 0; i < 3; ++i) ids.push_back(dets[i].id);
    return ids;
}
```

### answers

<details>
<summary>1. unordered_map rehash versus vector</summary>

Pointers and references to elements of an `unordered_map` stay valid across a rehash, because elements live in separate nodes and only the bucket array is rebuilt. Iterators are invalidated. With a sorted `std::vector<Track>`, any insertion invalidates references and iterators at or after the insertion point, and a reallocation invalidates all of them. The swap compiles, so the bug appears only at run time. Stable ids instead of pointers keep the container choice free (day 15).

</details>

<details>
<summary>2. predict the output</summary>

It prints `3` (the elements 5, 4, and 3). `[threshold]` copies the value when the lambda expression is evaluated, so the closure holds 2; changing the local afterwards has no effect. With `[&threshold]` it would print `1` (only 5 exceeds 4). A by-value capture is a snapshot (day 17).

</details>

<details>
<summary>3. forwarding references</summary>

Only `a` and `d`. `b` is an rvalue reference to `const` (the `const` disqualifies it). `c` is an ordinary rvalue reference, because `T` is fixed by the class, not deduced from the call. `e` is an rvalue reference to `std::vector<T>`, because the parameter is not exactly `T&&`. `auto&&` follows the same deduction rule as `T&&` (day 19).

</details>

<details>
<summary>4. copying on reallocation</summary>

`Waypoint`'s move constructor is probably not `noexcept` (often because it was hand-written, or because a member's move is not `noexcept`). Reallocation uses `std::move_if_noexcept`: if moving could throw halfway, some elements would already be moved out of the old buffer and `push_back` could no longer promise the strong guarantee. Copying keeps the old buffer intact until the new one is complete. Mark the move constructor `noexcept` (or `= default` it, so it inherits the members' `noexcept`), and check with `static_assert(std::is_nothrow_move_constructible_v<Waypoint>)` (days 10 and 20).

</details>

<details>
<summary>5. from week 1: lifetime extension</summary>

`a` is safe; `b` dangles. Binding a reference to a member of a temporary through the built-in `.` operator extends the lifetime of the whole temporary `Config`. Binding to a reference *returned by a function* does not: the compiler cannot see that `name()` returns a part of the temporary, so the temporary dies at the end of the full-expression and `b` refers to a destroyed string. Using `b` is undefined behavior (day 03). The same reasoning explains why a lambda capturing a reference to a member of a temporary dangles.

</details>

<details>
<summary>6. from week 2: a user-declared destructor</summary>

Declaring a destructor suppresses the implicitly declared move constructor and move assignment. The copy operations are still generated (that generation is deprecated, but it happens), so every "move" of a `Telemetry` silently becomes a copy of the whole sample vector: when returned from some functions, when stored in containers, and on every reallocation. Fix it by deleting the destructor and logging from a member whose own destructor does the work, or by defaulting all five special members explicitly (day 11). This is the rule of zero protecting performance as well as correctness.

</details>

<details>
<summary>mini exercise: one possible solution</summary>

The bugs: `dets.erase(it)` invalidates `it`, so the `++it` that follows is undefined behavior (and, even if it worked, the element after an erased one would be skipped). And `dets[i]` reads past the end when fewer than three detections survive, which is also undefined behavior.

```cpp
#include <algorithm>
#include <cstddef>
#include <iterator>
#include <vector>

struct Detection { int id; float range_m; bool valid; };

std::vector<int> closest_ids(std::vector<Detection> dets, float scale, std::size_t k = 3) {
    dets.erase(std::remove_if(dets.begin(), dets.end(),
                              [](const Detection& d) { return !d.valid; }),
               dets.end());
    for (auto& d : dets) d.range_m *= scale;   // a plain loop is the clearest form here

    k = std::min(k, dets.size());
    const auto mid = dets.begin() + static_cast<std::ptrdiff_t>(k);
    std::partial_sort(dets.begin(), mid, dets.end(),
                      [](const Detection& a, const Detection& b) { return a.range_m < b.range_m; });

    std::vector<int> ids;
    ids.reserve(k);
    std::transform(dets.begin(), mid, std::back_inserter(ids),
                   [](const Detection& d) { return d.id; });
    return ids;
}
```

Design notes: taking `dets` by value makes the mutation private (a caller that no longer needs its vector can `std::move` it in, and nobody is surprised by a reordered input). `std::partial_sort` orders only the first `k` elements, O(n log k) instead of O(n log n). The scaling loop stays a loop because `std::transform` in place, or `std::for_each`, would add syntax without adding meaning. In C++20, the first statement becomes `std::erase_if(dets, ...)`.

</details>

### connections

Week 3 rests on the first two weeks. Forwarding references (day 19) are value categories (day 05) put to work, and `std::forward` is a cousin of the `std::move` cast from day 10. Exception safety (day 20) is RAII (day 08) seen from the failure path, and the vector's choice between copying and moving on reallocation ties `noexcept` move constructors (day 10) to the strong guarantee. Iterator invalidation (day 15) is the lifetime rules of day 03 applied to containers.

It also sets up the next five weeks. Week 4 shortens much of this week's code: structured bindings unpack `try_emplace` results (day 22), `if constexpr` and fold expressions replace SFINAE and recursive packs (day 23), and `std::optional` and `std::variant` (days 24 and 25) become error channels for the strategy from day 20. Week 5 replaces `enable_if` with concepts (day 29) and iterator pairs with ranges (day 30). Lambdas return in week 6 as thread bodies, where capture lifetime gets even less forgiving, and `std::function`'s type erasure gets taken apart on day 46. Finally, every "measure it" this week becomes a concrete method on days 50 to 52.
