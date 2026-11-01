---
title: comparison categories and custom orderings
standard: C++20
objective: choose an honest comparison category, write a custom operator<=> with a consistent operator==, and keep NaN out of algorithms that need a strict weak ordering
prerequisites: defaulted-comparisons
difficulty: 3
---

### the idea

one `float` member silently changes what "less than" means for a whole struct, and with it whether `std::sort` on a vector of them has defined behavior. case-insensitive keys are ordered but two different strings can compare equivalent. comparison categories make those distinctions part of the type of `<=>`'s result, so the compiler and every reader can see what kind of order a type really has.

### understanding the concept

**comparison categories** (`<compare>`) describe what kind of order you have:

| category | values | meaning | example |
|---|---|---|---|
| `std::strong_ordering` | less, equal, greater | equal values are interchangeable | integers, `std::string` |
| `std::weak_ordering` | less, equivalent, greater | equivalent values may differ | case-insensitive keys |
| `std::partial_ordering` | less, equivalent, greater, unordered | some pairs are incomparable | `double` (NaN) |

stronger converts implicitly to weaker. a defaulted `auto operator<=>` returns the weakest category among its members, so one `float` member makes the whole struct `partial_ordering`. these categories are promises you make; the compiler does not check that your `strong_ordering` is really substitutable.

### in code

**predict the output.** a detection with a `float` member:

```cpp
#include <cstdio>
#include <limits>

struct Detection {
    float range_m;
    int   track_id;
    auto operator<=>(const Detection&) const = default;   // std::partial_ordering
};

int main() {
    float nan = std::numeric_limits<float>::quiet_NaN();
    Detection x{nan, 1}, y{5.f, 2};
    std::printf("%d %d %d %d\n", x < y, x > y, x == y, x == x);
}
```

it prints `0 0 0 0`. `x <=> y` is `unordered`, so every relational comparison is false, and the defaulted `==` compares `range_m` with `==`, so `x == x` is false too. equality that is not reflexive breaks `std::find`, `std::set`, and any cache keyed on the struct.

**a custom ordering, and the `==` you must write.** a parameter server whose keys compare case-insensitively:

```cpp complete
#include <algorithm>
#include <cctype>
#include <string>

class ParamKey {
public:
    explicit ParamKey(std::string s) : s_(std::move(s)) {}
    std::weak_ordering operator<=>(const ParamKey& o) const {
        return std::lexicographical_compare_three_way(          // C++20 algorithm
            s_.begin(), s_.end(), o.s_.begin(), o.s_.end(),
            [](unsigned char a, unsigned char b) { return std::tolower(a) <=> std::tolower(b); });
    }
    bool operator==(const ParamKey& o) const { return (*this <=> o) == 0; }  // not generated
private:
    std::string s_;
};
// std::set<ParamKey>: inserting "MaxVelocity" then "maxvelocity" leaves size 1
```

`weak_ordering` is the honest category: `"MaxVelocity"` and `"maxvelocity"` are equivalent for ordering but are not the same string. the hand-written `==` must agree with `<=>`; a defaulted one here would compare case-sensitively and contradict the ordering.

### in practice

a deployment tool decides whether to flash new firmware. versions look like `2.1.0-rc1` and, per semantic versioning, a prerelease sorts *before* its release. the defaulted operator gets that wrong, because the empty string sorts before `"rc1"`:

```cpp
struct Version {
    int major = 0, minor = 0, patch = 0;
    std::string pre;   // empty for a release
    std::strong_ordering operator<=>(const Version& o) const {
        if (auto c = std::tie(major, minor, patch) <=> std::tie(o.major, o.minor, o.patch); c != 0)
            return c;
        if (pre.empty() != o.pre.empty())   // a release outranks its prereleases
            return pre.empty() ? std::strong_ordering::greater : std::strong_ordering::less;
        return pre <=> o.pre;               // simplified: full semver compares dot-separated parts
    }
    bool operator==(const Version&) const = default;
};
// sorted: 2.0.9  2.1.0-rc1  2.1.0
```

`std::tie(...) <=> std::tie(...)` uses C++20's `<=>` on `std::tuple`, which keeps the "compare these three in order" logic in one line. defaulting `==` is fine here: two versions are equal exactly when all four fields are, which agrees with the custom ordering.

leave out that `==` and you find out quickly: `std::ranges::sort(versions)` and `std::ranges::max(versions)` stop compiling, because `std::totally_ordered` ([[writing-concepts]]) requires equality as well as ordering. the concept caught a half-specified type at the call site.

### watch out for

**partial orders in algorithms that require a strict weak ordering.** `std::sort`, `std::set`, and `std::map` require that the comparison be a strict weak ordering over the values you actually pass. with NaN in the data, `<` on `double` (or on a struct whose defaulted `<=>` is `partial_ordering`) is not one, and violating that precondition is undefined behavior. typically you get silently misordered output; with some invalid comparators, implementations have also been known to read past the end of the range. either reject NaN at the boundary (a sensor driver is a good place) or sort with `std::strong_order`, which for IEEE 754 types implements the `totalOrder` predicate (-0 before +0, positive NaNs after all numbers):

```cpp
std::sort(v.begin(), v.end(), [](double a, double b) { return std::strong_order(a, b) < 0; });
// {3, NaN, -0.0, 0.0, 1} sorts to: -0 0 1 3 nan
```

### the takeaway

default `<=>` (and get `==` for free) when member-wise lexicographic order in declaration order is what you mean. when it is not, write `<=>` with an honest category and write `==` next to it, consistent with it. watch any `float` member: it turns your type's ordering into a partial one.

### optional challenge

which comparison category should `operator<=>` return for each type: (a) a timestamp stored as integer nanoseconds; (b) a file path compared case-insensitively; (c) a 2D point ordered by its distance from the origin; (d) a sensor reading whose value is a `double`?

<details>
<summary>answer</summary>

(a) `std::strong_ordering`: equal timestamps are interchangeable. (b) `std::weak_ordering`: `"Log.TXT"` and `"log.txt"` are equivalent for ordering but are different values. (c) `std::weak_ordering`: distinct points at the same distance are equivalent, not equal, and calling that `strong` would be a false promise to any code that substitutes one for the other. (d) `std::partial_ordering`, because NaN is unordered; if the type's invariant excludes NaN (checked in its constructor), you may document and return a stronger category, but then the check is what makes the promise true.

</details>
