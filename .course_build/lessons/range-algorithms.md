---
title: range algorithms and projections
standard: C++20
objective: call the constrained `std::ranges` algorithms on whole ranges, and use projections instead of hand-written comparison lambdas
prerequisites: concepts, algorithms
difficulty: 2
---

### the idea

`std::sort(dets.begin(), dets.end(), [](const Detection& a, const Detection& b) { return a.range_m < b.range_m; });` says "sort detections by range" in about seventy characters, most of them ceremony: two iterators that always come as a pair, and a lambda whose only job is to pick one member twice. C++20's range algorithms let you write `std::ranges::sort(dets, {}, &Detection::range_m);`, and the shorter version is also the better-checked one.

### understanding the concept

a **range** is anything with `std::ranges::begin` and `std::ranges::end` (the end may be a *sentinel* of a different type). C++20 adds two layers on top of the [[algorithms]] algorithms.

**range algorithms** in `std::ranges::` take a whole range, are constrained with concepts ([[concepts]]), and accept a **projection**: a callable applied to each element before the comparison or predicate. `std::ranges::sort(dets, {}, &Detection::range_m)` sorts by one member with the default `std::ranges::less` (the `{}`); the member pointer works because projections are called through `std::invoke`.

every classic algorithm has a `std::ranges::` counterpart. besides taking a range and a projection, they differ in small ways worth knowing: they are constrained, so misuse fails at the call site; they accept an iterator and a *sentinel* of a different type; and several return more than the classic versions did (`std::ranges::copy` returns both the input and output positions where it stopped), which you can unpack with a structured binding.

### in code

```cpp complete
#include <algorithm>
#include <cstdio>
#include <vector>

struct Detection { float range_m; float snr_db; int track_id; };

int main() {
    std::vector<Detection> dets{{80.f, 15.f, 3}, {30.f, 20.f, 1}, {60.f, 9.f, 2}};

    std::ranges::sort(dets, {}, &Detection::range_m);                    // by range, ascending
    auto strongest = std::ranges::max_element(dets, {}, &Detection::snr_db);
    auto it = std::ranges::find(dets, 2, &Detection::track_id);          // compares the projected id
    auto n = std::ranges::count_if(dets, [](float snr) { return snr > 12.f; }, &Detection::snr_db);

    std::printf("%d %d %d %td\n", dets.front().track_id, strongest->track_id, it->track_id, n);
    // prints: 1 1 2 2
}
```

the projection is applied to each element before the comparison or predicate sees it, so the predicate in `count_if` receives a `float`, not a `Detection`. the `{}` is the default comparator, `std::ranges::less`.

### in practice

projections and comparators combine, which covers most real sorting needs without a custom lambda: `std::ranges::sort(tracks, std::ranges::greater{}, &Track::confidence)` sorts by confidence, highest first. a projection can also be any callable, for keys that are computed rather than stored, such as the distance from the vehicle: `std::ranges::sort(dets, {}, [&](const Detection& d) { return dist2(d, ego); })`. keep such projections cheap: a sort calls the projection twice per comparison, so O(n log n) times. when the key is expensive (a lookup, a string conversion), compute it once per element into a vector of key and index pairs, sort that, and reorder, rather than recomputing inside the sort.

### watch out for

**algorithms on temporaries return `std::ranges::dangling`.**

```cpp
std::vector<int> make_ids();
auto it = std::ranges::find(make_ids(), 42);   // it is std::ranges::dangling
// *it;  error: no match for 'operator*' (operand type is 'std::ranges::dangling')
```

ranges that are safe to outlive (like `std::string_view` or `std::span`) opt in as *borrowed ranges*, and for those you get a real iterator.

the classic algorithms would have returned an iterator into the destroyed vector and let you dereference it. if you need the result, keep the container in a named variable first.

### the takeaway

prefer the `std::ranges::` algorithms: pass the range, not two iterators, and use projections to say "by this member" instead of writing comparison lambdas.

### optional challenge

`std::ranges::sort(v, {}, key)` is called on 1,000 elements, and `key` converts each element's id to a `std::string`. roughly how many conversions happen, and how would you avoid most of them?

<details>
<summary>answer</summary>

a comparison sort makes on the order of n log2 n comparisons, about 10,000 for 1,000 elements, and each comparison projects both operands, so about 20,000 string conversions instead of 1,000. compute the keys once: build a `std::vector<std::pair<std::string, std::size_t>>` of key and original index, sort that (by its first member), and use the indices to reorder or to read the elements in order. the general rule: projections are for cheap accessors, not for computation.

</details>
