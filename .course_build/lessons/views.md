---
title: views: lazy pipelines
standard: C++20
objective: compose lazy view pipelines and predict when, and how often, their callables run
prerequisites: range-algorithms, string-view
difficulty: 2
---

### the idea

a radar tracker wants "the ranges of the three nearest detections with SNR above 12 dB". the C++17 version copies the strong detections into a temporary vector, sorts it with a lambda that compares one member, and then runs an index loop that stops at three. three passes, one temporary, and an off-by-one waiting to happen in `i < strong.size() && i < 3`.

C++20 ranges let you say it as a pipeline: filter, project, take. the interesting question is not the syntax but the mechanics: nothing in a pipeline runs until you iterate it, and nothing in it owns your data unless you hand it over. both facts make pipelines cheap, and both are the source of their bugs.

### understanding the concept

**views** (`<ranges>`) are lazy adaptors. `std::views::filter(pred)`, `transform(f)`, `take(n)`, `drop(n)`, `reverse`, `iota(a, b)`, `keys`, `values`, and `split(delim)` each produce a small object that stores its underlying range (or a reference to it) plus the callable. iterating it pulls elements through the chain one at a time. a view is required to be cheap to move, and to copy if it is copyable, independent of how many elements it represents. `r | views::filter(p)` is just `views::filter(r, p)` written left to right.

there is no `std::ranges::to` in C++20 (it is C++23). to materialize a pipeline you write the container yourself, with `std::ranges::copy` into a `back_inserter`, or by constructing from the iterators of a `views::common` adaptor.

### in code

**before and after.**

```cpp complete
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

**predict the output.** laziness means the callable runs when an element is pulled, and it can run more than once:

```cpp complete
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

both sums are 56. the first pipeline makes 9 calls: `filter` calls `square` six times to test each element, and the loop's dereference calls it again for the three that pass. the second makes 3. views do not cache transformed values, so an expensive or side-effecting `transform` ahead of a `filter` is evaluated twice per surviving element. put cheap filters first, and keep transforms pure.

### in practice

telemetry lines like `rpm=1200;temp=71;volt=24` are a natural fit for `views::split`, which with a `std::string_view` source yields contiguous subranges, so each field becomes a `string_view` with no allocation:

```cpp complete
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

these `split` semantics come from P2210, also a defect report against C++20 (the old behavior lives on as `views::lazy_split`). an older standard library may give you a forward-only range where this constructor does not work. the real code checks `eq == npos` and the `from_chars` result; it was left out to keep the example short.

### watch out for

**debug builds and compile times.** each adaptor is a layer of templates. error messages name types like `filter_view<ref_view<vector<int>>, lambda>`, and in unoptimized builds each layer's `operator++` and `operator*` is a real call. if your robot's debug build has to meet a control-loop deadline, check that before converting a hot loop. and when the logic has early exits, two outputs, or index arithmetic, a plain loop is often clearer than a pipeline. "No raw loops" ([[algorithms]]) is a guideline.

### the takeaway

views are lazy and cheap: a pipeline is a recipe that runs element by element when you iterate it, so put cheap filters first, keep transforms pure, and materialize the result explicitly.

### optional challenge

what does this print, and why does it terminate even though `std::views::iota(1)` never ends?

```cpp
auto odd = [](int x) { return x % 2 == 1; };
for (int x : std::views::iota(1) | std::views::filter(odd) | std::views::take(3))
    std::printf("%d ", x);
```

<details>
<summary>answer</summary>

it prints `1 3 5`. `iota(1)` is an unbounded range, which is fine because nothing is computed up front: the loop pulls one element at a time through `take`, which pulls through `filter`, which pulls from `iota`. after the third element, `take` reports the end and the loop stops, so `iota` is asked for only five numbers. an eager pipeline (build a container, then filter it, then truncate it) could not even start.

</details>

### going deeper

#### sorting before filtering

notice a real tradeoff hiding here: we sort *before* filtering because `ranges::sort` needs a random-access range and a filter view is at most bidirectional. so the C++20 version sorts every detection, while the C++17 version sorted only the strong ones. if most detections are weak and the frame is large, that matters; measure with realistic frames before deciding which one wins.
