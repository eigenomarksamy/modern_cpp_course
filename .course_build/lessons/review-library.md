---
title: review: containers, algorithms, and lambdas
kind: review
standard: C++17
objective: consolidate container choice and invalidation, algorithms over iterator ranges, and lambda captures and lifetimes
prerequisites: sequence-containers, associative-containers, algorithms, lambdas, callbacks
difficulty: 1
---

### recap

| lesson | key idea |
|---|---|
| [[sequence-containers]] | start with `std::vector`; complexity, memory layout, and invalidation rules are all part of a container's contract. |
| [[associative-containers]] | ordered map for order and stable references, hash map for fast lookups, sorted vector for read-mostly data; `operator[]` inserts. |
| [[algorithms]] | algorithms see iterators, never containers: half-open ranges, erase-remove, `back_inserter`, and why `std::sort` cannot sort a list. |
| [[lambdas]] | a lambda is an object whose members are its captures; by-value captures are snapshots. |
| [[callbacks]] | a stored lambda must not capture what it outlives; `std::function` erases the type at the cost of an indirect call and a copyable callable. |

### review questions

1. you keep `Track*` pointers into a `std::unordered_map<int, Track>`. a burst of inserts triggers a rehash. which of your pointers and iterators are still valid? what changes if someone replaces the map with a `std::vector<Track>` kept sorted by id?
2. predict the output:

   ```cpp
   std::vector<int> v{5, 1, 4, 2, 3};
   int threshold = 2;
   auto above = [threshold](int x) { return x > threshold; };
   threshold = 4;
   std::cout << std::count_if(v.begin(), v.end(), above) << '\n';
   ```

3. why does `std::transform(in.begin(), in.end(), out.begin(), f)` with an empty `out` corrupt memory, while the same call with `std::back_inserter(out)` works?
4. a per-point filter in a hot loop takes `const std::function<bool(const Point&)>&`. a profiler shows the call overhead. what changes, and what do you give up?
5. from [[special-members]]: a teammate adds `~Telemetry() { log("closed"); }` to an otherwise rule-of-zero class holding a `std::vector<Sample>`. everything still compiles. what did that change cost?

### mini exercise

this function is supposed to drop invalid detections, apply a range calibration, and return the ids of the three closest. it has two bugs, one of them undefined behavior. rewrite it with algorithms and lambdas, keep it correct for fewer than three detections, and decide where a plain loop is still the clearest choice.

```cpp complete
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
<summary>answer 1: rehash versus vector</summary>

pointers and references to elements of an `unordered_map` stay valid across a rehash, because elements live in separate nodes and only the bucket array is rebuilt. iterators are invalidated. with a sorted `std::vector<Track>`, any insertion invalidates references and iterators at or after the insertion point, and a reallocation invalidates all of them. the swap compiles, so the bug appears only at run time. stable ids instead of pointers keep the container choice free ([[associative-containers]]).

</details>

<details>
<summary>answer 2: predict the output</summary>

it prints `3` (the elements 5, 4, and 3). `[threshold]` copies the value when the lambda expression is evaluated, so the closure holds 2; changing the local afterwards has no effect. with `[&threshold]` it would print `1` (only 5 exceeds 4). a by-value capture is a snapshot ([[lambdas]]).

</details>

<details>
<summary>answer 3: algorithms cannot grow containers</summary>

an algorithm only has iterators, so it cannot add elements. with an empty `out`, `out.begin()` equals `out.end()`, and `transform` writes past the end: undefined behavior. `std::back_inserter(out)` is an output iterator whose assignment calls `out.push_back`, so the container grows through an adaptor the caller chose. `out.resize(in.size())` before the call also works.

</details>

<details>
<summary>answer 4: std::function versus a template</summary>

make the filter a template parameter (`template <typename Pred> ... Pred&& keep`). the compiler then knows the callable's type, can inline it into the loop, and may vectorize the loop. you give up a single compiled function in a `.cpp` file: the template must live in a header, is instantiated per callable type, and adds compile time. keep `std::function` for low-frequency boundaries such as per-frame callbacks.

</details>

<details>
<summary>answer 5: a user-declared destructor</summary>

declaring a destructor suppresses the implicitly declared move constructor and move assignment. the copy operations are still generated (that generation is deprecated, but it happens), so every "move" of a `Telemetry` silently becomes a copy of the whole sample vector: when returned from some functions, when stored in containers, and on every reallocation. fix it by deleting the destructor and logging from a member whose own destructor does the work, or by defaulting all five special members explicitly ([[special-members]]). this is the rule of zero protecting performance as well as correctness.

</details>

<details>
<summary>mini exercise answer</summary>

the bugs: `dets.erase(it)` invalidates `it`, so the `++it` that follows is undefined behavior (and, even if it worked, the element after an erased one would be skipped). and `dets[i]` reads past the end when fewer than three detections survive, which is also undefined behavior.

```cpp complete
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

design notes: taking `dets` by value makes the mutation private (a caller that no longer needs its vector can `std::move` it in, and nobody is surprised by a reordered input). `std::partial_sort` orders only the first `k` elements, O(n log k) instead of O(n log n). the scaling loop stays a loop because `std::transform` in place, or `std::for_each`, would add syntax without adding meaning. in C++20, the first statement becomes `std::erase_if(dets, ...)`.

</details>

### connections

this module put the first two modules to work: iterator invalidation is the lifetime rules of [[temporaries-dangling]] applied to containers, the vector's copy-or-move choice is [[noexcept-moves]], and a lambda's captures are ownership decisions like any other members. the next module looks inside the machinery the library is built from: templates, deduction, and perfect forwarding, which is how `emplace_back` passes its arguments through.
