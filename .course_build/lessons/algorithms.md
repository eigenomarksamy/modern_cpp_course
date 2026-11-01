---
title: iterators and algorithms over raw loops
standard: C++17
objective: use standard algorithms over half-open iterator ranges to state intent, and apply the erase-remove idiom correctly
prerequisites: sequence-containers
difficulty: 2
---

### the idea

here is a line that compiles, passes a quick test, and is wrong:

```cpp
v.erase(std::remove_if(v.begin(), v.end(), is_even));
```

it erases one element, not all the even ones. to see why, you need the model behind the standard algorithms: they see iterators, never containers. once that model clicks, the erase-remove idiom, the iterator categories, and the "use an algorithm instead of a loop" advice all follow from the same idea.

### understanding the concept

an algorithm like `std::remove_if` receives a pair of iterators `[first, last)`. it can read and write elements through them, but it has no access to the container: it cannot allocate, cannot shrink, cannot erase. that decoupling is the design win of the STL: N algorithms times M containers needs N + M pieces of code, not N × M. the price is that some operations take two steps, one by the algorithm and one by the container.

the half-open range is what makes this compose. `end()` points one past the last element, so an empty range is `first == last`, the length is `last - first` for random-access iterators, and "not found" has a natural value: the algorithm returns `last`. subranges chain without plus-or-minus-one adjustments: `[first, mid)` and `[mid, last)` cover the whole range exactly once.

algorithms state what they need from iterators through categories. each category adds guarantees to the previous one:

| category | adds | typical source |
|---|---|---|
| input | read once, single pass | `std::istream_iterator` |
| forward | multi-pass, can revisit | `std::forward_list`, unordered containers |
| bidirectional | `--it` | `std::list`, `std::map`, `std::set` |
| random access | `it + n`, `it2 - it1`, `<` in O(1) | `std::deque` |
| contiguous (named in C++20) | elements adjacent in memory | `std::vector`, `std::array`, `std::string` |

in C++17 there is no tag for contiguous iterators; contiguity is a property of the container, and C++20 adds `std::contiguous_iterator_tag` and the `std::contiguous_iterator` concept. `std::sort` needs random access, so `std::sort(list.begin(), list.end())` fails to compile. GCC 12 reports it as `no match for 'operator-'` from deep inside `stl_algo.h`, which is the pre-concepts error experience that [[concepts]] fixes. `std::list` has a member `sort()` for exactly this reason.

why prefer algorithms to hand-written loops? a named algorithm states intent (`any_of` reads as a question, a `for` loop with a `bool found` flag has to be simulated), it gets the boundary conditions right once, and it advertises its complexity. Sean Parent's "no raw loops" is a good default, not a law: when a loop does two things in one pass, or the algorithm version needs a contorted lambda, a plain loop is the clearer code.

### in code

intent-revealing algorithms over a telemetry buffer. the lambdas are short on purpose; [[lambdas]] covers what they compile to.

```cpp complete
#include <algorithm>
#include <iterator>
#include <numeric>
#include <vector>

struct Sample { double value; bool valid; };

bool any_fault(const std::vector<Sample>& s) {
    return std::any_of(s.begin(), s.end(), [](const Sample& x) { return !x.valid; });
}

// Returns s.end() if nothing exceeds the limit: the half-open range gives "not found" a value.
auto first_over(const std::vector<Sample>& s, double limit) {
    return std::find_if(s.begin(), s.end(), [limit](const Sample& x) { return x.value > limit; });
}

std::vector<double> scaled(const std::vector<Sample>& s, double gain) {
    std::vector<double> out;
    out.reserve(s.size());
    std::transform(s.begin(), s.end(), std::back_inserter(out),
                   [gain](const Sample& x) { return x.value * gain; });
    return out;
}

double energy(const std::vector<double>& v) {
    return std::accumulate(v.begin(), v.end(), 0.0, [](double acc, double x) { return acc + x * x; });
}
```

`std::back_inserter` is an output iterator whose assignment calls `push_back`. that is how an algorithm that cannot touch the container still appends to it: the container is reached through an iterator adaptor that the caller chose.

now the erase-remove bug. predict the output:

```cpp complete
#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    auto is_even = [](int x) { return x % 2 == 0; };

    std::vector<int> v{1, 2, 3, 4, 5, 6};
    v.erase(std::remove_if(v.begin(), v.end(), is_even));  // BUG: single-iterator erase
    std::cout << v.size() << '\n';                          // prints: 5

    std::vector<int> w{1, 2, 3, 4, 5, 6};
    w.erase(std::remove_if(w.begin(), w.end(), is_even), w.end());  // erase-remove idiom
    std::cout << w.size() << '\n';                                  // prints: 3
}
```

`remove_if` shifts the kept elements (1, 3, 5) to the front and returns an iterator to the new logical end. the elements after it are valid but have unspecified values (with libstdc++ the first buggy vector ends as `1 3 5 5 6`, but don't depend on that). `erase(it)` removes one element; `erase(it, end())` removes the tail. C++20 wraps the idiom as `std::erase_if(w, is_even)`, which returns the number of elements removed.

### in practice

a telemetry service computes the p99 latency of each one-second window. the first version copies the samples, calls `std::sort` (O(n log n)), and reads the element at index `0.99 * n`. `std::nth_element` places exactly that element where it would be after sorting, with everything smaller before it and everything larger after it, in O(n) on average. for a single percentile the full sort does work nobody uses. knowing the algorithm vocabulary (`nth_element`, `partial_sort`, `lower_bound` on sorted data, `minmax_element`) is often worth more than micro-tuning a loop. still measure: for a few hundred samples per window, both may be far below the noise floor of the service.

### watch out for

`std::accumulate` uses the type of its initial value as the accumulator type:

```cpp
std::vector<double> v{0.5, 0.5, 0.5};
auto total = std::accumulate(v.begin(), v.end(), 0);  // BUG: int accumulator; total == 0
```

each step computes `int + double`, then converts the result back to `int`, truncating 0.5 to 0. GCC 12 gives no warning here even with `-Wconversion`, because the conversion happens inside a system header. write `0.0` (or `T{}`) and let the initial value carry the type you mean.

### the takeaway

algorithms see iterators, not containers. that one fact explains the half-open range, the erase-remove idiom, `back_inserter`, and why `std::sort` cannot sort a list. reach for a named algorithm first because it says what you mean, and drop back to a loop when the loop is clearer.

### optional challenge

what is wrong with this, and what are two correct fixes?

```cpp
std::vector<double> in{1.0, 2.0, 3.0};
std::vector<double> out;
std::transform(in.begin(), in.end(), out.begin(), [](double x) { return x * 2; });
```

<details>
<summary>answer</summary>

`out` is empty, so `out.begin()` is also `out.end()`, and `transform` writes three elements past the end: undefined behavior. the algorithm cannot grow `out` because it only has an iterator, not the container. fix it with `out.resize(in.size())` before the call (then writing through `out.begin()` is valid), or with `out.reserve(in.size())` plus `std::back_inserter(out)` as the destination. the second avoids value-initializing elements that are about to be overwritten, which matters for expensive element types and not at all for doubles.

</details>

### going deeper

#### partition and stable sort

partition and stable sort express a common two-step "group, then order" job without index bookkeeping:

```cpp complete
#include <algorithm>
#include <vector>

struct Det { int id; float range_m; bool confirmed; };

void order_for_display(std::vector<Det>& dets) {
    // confirmed first, each group keeps its original order
    auto mid = std::stable_partition(dets.begin(), dets.end(),
                                     [](const Det& d) { return d.confirmed; });
    // confirmed detections by range; equal ranges keep their previous order
    std::stable_sort(dets.begin(), mid,
                     [](const Det& a, const Det& b) { return a.range_m < b.range_m; });
}
// input ids:  1(40m, conf) 2(12m) 3(12m, conf) 4(40m, conf) 5(7m)
// output ids: 3 1 4 2 5
```

the complexities are part of the choice. `std::partition` is O(n) and does not preserve relative order; `std::stable_partition` does, using a temporary buffer if it can get one (O(n)) and O(n log n) swaps if it cannot. `std::stable_sort` is O(n log n) comparisons with extra memory and O(n log² n) without. if order within groups does not matter, the unstable versions avoid that buffer.

#### parallel execution policies

C++17 also added execution policies: `std::sort(std::execution::par, v.begin(), v.end())`. treat them with care. the callable must not cause data races (locking inside it is allowed for `par`, not for `par_unseq`), an exception escaping an element access calls `std::terminate`, and whether you get parallelism at all depends on the library. MSVC ships a parallel implementation; libstdc++ uses Intel TBB as its parallel backend. on GCC 12 without TBB the code above still compiles and runs, but libstdc++ selects its serial backend, so you pay the policy's constraints without any speedup. parallel sorting also has a threshold below which the coordination costs more than it saves. benchmark on the target machine with production-sized inputs before committing to it.
