<a id="day-30"></a>

## day 30: ranges and views: lazy pipelines

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 16, 17, 26, 29

### the idea

A radar tracker wants "the ranges of the three nearest detections with SNR above 12 dB". The C++17 version copies the strong detections into a temporary vector, sorts it with a lambda that compares one member, and then runs an index loop that stops at three. Three passes, one temporary, and an off-by-one waiting to happen in `i < strong.size() && i < 3`.

C++20 ranges let you say it as a pipeline: filter, project, take. The interesting question is not the syntax but the mechanics: nothing in a pipeline runs until you iterate it, and nothing in it owns your data unless you hand it over. Both facts make pipelines cheap, and both are the source of their bugs.

### understanding the concept

A **range** is anything with `std::ranges::begin` and `std::ranges::end` (the end may be a *sentinel* of a different type). C++20 adds two layers on top of the day 16 algorithms.

**Range algorithms** in `std::ranges::` take a whole range, are constrained with concepts (day 29), and accept a **projection**: a callable applied to each element before the comparison or predicate. `std::ranges::sort(dets, {}, &Detection::range_m)` sorts by one member with the default `std::ranges::less` (the `{}`); the member pointer works because projections are called through `std::invoke`.

**Views** (`<ranges>`) are lazy adaptors. `std::views::filter(pred)`, `transform(f)`, `take(n)`, `drop(n)`, `reverse`, `iota(a, b)`, `keys`, `values`, and `split(delim)` each produce a small object that stores its underlying range (or a reference to it) plus the callable. Iterating it pulls elements through the chain one at a time. A view is required to be cheap to move, and to copy if it is copyable, independent of how many elements it represents. `r | views::filter(p)` is just `views::filter(r, p)` written left to right.

What does a view hold? `views::all` decides. For an lvalue container it creates a `ref_view`: a pointer to your container. For an rvalue container it creates an `owning_view` that moves the container in. (`owning_view` came from P2415, a defect report applied to C++20; GCC 12, recent Clang and MSVC implement it. Before it, piping an rvalue container did not compile.) So "views do not own" is true for lvalues, which is the common case and the dangerous one.

There is no `std::ranges::to` in C++20 (it is C++23). To materialize a pipeline you write the container yourself, with `std::ranges::copy` into a `back_inserter`, or by constructing from the iterators of a `views::common` adaptor.

### in code

**Before and after.**

```cpp
#include <algorithm>
#include <iterator>
#include <ranges>
#include <vector>

struct Detection { float range_m; float snr_db; int track_id; };

// C++17
std::vector<float> near_strong_17(const std::vector<Detection>& dets) {
    std::vector<Detection> strong;
    for (const auto& d : dets)
        if (d.snr_db > 12.f) strong.push_back(d);
    std::sort(strong.begin(), strong.end(),
              [](const Detection& a, const Detection& b) { return a.range_m < b.range_m; });
    std::vector<float> out;
    for (std::size_t i = 0; i < strong.size() && i < 3; ++i)
        out.push_back(strong[i].range_m);
    return out;
}

// C++20
std::vector<float> near_strong_20(std::vector<Detection> dets) {   // our own copy to sort
    std::ranges::sort(dets, {}, &Detection::range_m);
    auto nearest = dets
        | std::views::filter([](const Detection& d) { return d.snr_db > 12.f; })
        | std::views::transform(&Detection::range_m)
        | std::views::take(3);
    std::vector<float> out;
    std::ranges::copy(nearest, std::back_inserter(out));
    return out;
}
// both return {30, 60, 80} for the same input
```

Notice a real tradeoff hiding here: we sort *before* filtering because `ranges::sort` needs a random-access range and a filter view is at most bidirectional. So the C++20 version sorts every detection, while the C++17 version sorted only the strong ones. If most detections are weak and the frame is large, that matters; measure with realistic frames before deciding which one wins.

**Predict the output.** Laziness means the callable runs when an element is pulled, and it can run more than once:

```cpp
#include <cstdio>
#include <ranges>
#include <vector>

int calls = 0;
int main() {
    std::vector<int> raw{1, 2, 3, 4, 5, 6};
    auto square = [](int x) { ++calls; return x * x; };
    auto even   = [](int x) { return x % 2 == 0; };

    int sum = 0;
    for (int x : raw | std::views::transform(square) | std::views::filter(even)) sum += x;
    std::printf("sum=%d calls=%d\n", sum, calls);

    calls = 0; sum = 0;
    for (int x : raw | std::views::filter(even) | std::views::transform(square)) sum += x;
    std::printf("sum=%d calls=%d\n", sum, calls);
}
```

Both sums are 56. The first pipeline makes 9 calls: `filter` calls `square` six times to test each element, and the loop's dereference calls it again for the three that pass. The second makes 3. Views do not cache transformed values, so an expensive or side-effecting `transform` ahead of a `filter` is evaluated twice per surviving element. Put cheap filters first, and keep transforms pure.

**Dangling is caught where the library can catch it.** A range algorithm called on an rvalue container returns `std::ranges::dangling` instead of an iterator into a dead object:

```cpp
std::vector<int> make_ids();
auto it = std::ranges::find(make_ids(), 42);   // it is std::ranges::dangling
// *it;  error: no match for 'operator*' (operand type is 'std::ranges::dangling')
```

Ranges that are safe to outlive (like `std::string_view` or `std::span`) opt in as *borrowed ranges*, and for those you get a real iterator.

### in practice

Telemetry lines like `rpm=1200;temp=71;volt=24` are a natural fit for `views::split`, which with a `std::string_view` source yields contiguous subranges, so each field becomes a `string_view` with no allocation:

```cpp
#include <charconv>
#include <ranges>
#include <string_view>

void parse(std::string_view line) {
    for (auto field : line | std::views::split(';')) {
        std::string_view kv(field.begin(), field.end());   // C++20 iterator-pair constructor
        auto eq = kv.find('=');
        std::string_view key = kv.substr(0, eq);
        int value = 0;
        std::from_chars(kv.data() + eq + 1, kv.data() + kv.size(), value);
        // ... dispatch on key; prints [rpm] -> 1200 and so on in the test build
    }
}
```

These `split` semantics come from P2210, also a defect report against C++20 (the old behavior lives on as `views::lazy_split`). An older standard library may give you a forward-only range where this constructor does not work. The real code checks `eq == npos` and the `from_chars` result; it was left out to keep the example short.

### watch out for

**A pipeline over a local, returned from a function, dangles.**

```cpp
auto strong_ids() {
    std::vector<int> ids = load();
    return ids | std::views::filter([](int i) { return i > 2; });   // BUG: ref_view to a dead local
}
```

Iterating the result is undefined behavior, and GCC 12 compiles it without a warning. Return `std::move(ids) | ...` (an `owning_view`) or return the container. The same trap appears in range-for: `for (int x : next_frame().data() | std::views::take(2))` is UB if `data()` returns a reference into the temporary frame, because the frame dies at the end of the range initializer. (C++23 extends temporary lifetimes in range-for initializers; C++20 does not.)

**`filter_view` caches `begin()`.** To make `begin()` amortized O(1), `filter_view` finds the first match on the first call and remembers it. Consequences:

- `begin()` is non-const, so `void dump(const auto& r)` will not accept a filter view. Take views by value or by forwarding reference (`auto&&`) instead.
- Modifying an element through a filter iterator so that it no longer satisfies the predicate is UB, by the standard's own wording.
- Changing the underlying container after the first iteration can leave the cached iterator stale (see the challenge).

**Debug builds and compile times.** Each adaptor is a layer of templates. Error messages name types like `filter_view<ref_view<vector<int>>, lambda>`, and in unoptimized builds each layer's `operator++` and `operator*` is a real call. If your robot's debug build has to meet a control-loop deadline, check that before converting a hot loop. And when the logic has early exits, two outputs, or index arithmetic, a plain loop is often clearer than a pipeline. "No raw loops" (day 16) is a guideline.

### the takeaway

Views are lazy, cheap, and non-owning for lvalues: a pipeline is a recipe that runs when you iterate it, against data that someone else must keep alive. Use range algorithms and projections freely, use pipelines where they read better than the loop, and materialize the result explicitly.

### optional challenge

```cpp
std::vector<int> v{1, 2, 3, 4};
auto evens = v | std::views::filter([](int x) { return x % 2 == 0; });
v.push_back(6);
for (int x : evens) std::printf("%d ", x);
```

Is this well-defined, and what does it print? Does the answer change if you insert a `for (int x : evens) {}` loop before the `push_back`?

<details>
<summary>answer</summary>

As written it is fine and prints `2 4 6`. The view holds a `ref_view` (a pointer to `v` itself, not to its buffer) and has not cached anything yet, so iteration starts from the current `v.begin()`.

If you iterate first, `filter_view` caches an iterator to the `2`. The `push_back` may reallocate (with libstdc++ it does: the capacity after list-initialization is exactly 4), which invalidates that cached iterator, and the next loop starts from it: undefined behavior. The rule of thumb: do not keep a view across modifications of what it views. Recreate it; it is cheap.

</details>
