<a id="day-32"></a>

## day 32: three-way comparison and defaulted equality

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 09, 29

### the idea

To put a two-field grid cell in a `std::set` or sort it, C++17 asked for six operators, usually written as a pile of `std::tie` boilerplate. Each one is a chance for a typo (`<=` implemented as `!(a < b)` instead of `!(b < a)`), and the next person to add a field has to update all of them.

C++20 replaces the pile with one line, but the line comes with rules: which operators the compiler synthesizes, which "kind" of ordering you get, and when it quietly stops generating `==` for you. Those rules are worth ten minutes, because the failure modes are a missing operator at best and a sort with undefined behavior at worst.

### understanding the concept

**The spaceship.** `a <=> b` returns an object that says less, equal (or equivalent), greater, or, for some types, unordered. You compare it against the literal `0`: `(a <=> b) < 0` means `a < b`.

**Rewriting.** You no longer write the relational operators. For `a < b`, the compiler also considers `(a <=> b) < 0` and the reversed form `0 < (b <=> a)`; likewise for `>`, `<=`, `>=`. For `a != b` it considers `!(a == b)` and `!(b == a)`, and for `a == b` it also tries `b == a`. Two consequences: one `operator==(const Meters&, double)` makes `2.0 == m` work as well, and a rewritten `!=` requires the `==` it uses to return exactly `bool`.

**Defaulting.** `auto operator<=>(const T&) const = default;` compares base classes first, then non-static members **in declaration order**, lexicographically, stopping at the first difference. `bool operator==(const T&) const = default;` compares the same things with `==`. If you default `<=>` and the class declares no `operator==` at all (of any signature), the compiler also declares a defaulted `==` for you. If you *write* `<=>` yourself, it does not.

**Why `==` is separate.** The original C++20 design derived `==` from `<=>`, and it was split out (P1185) for performance. Equality on containers can return `false` as soon as the sizes differ (that is how the standard specifies container `==`, and mainstream `std::string` implementations do the same); a three-way comparison has to walk to the first differing element, because a shorter string can still compare greater. For two log lines of different lengths sharing a 4 KiB prefix, `==` can stop after comparing sizes, while `<=>` reads the whole prefix.

**Comparison categories** (`<compare>`) describe what kind of order you have:

| category | values | meaning | example |
|---|---|---|---|
| `std::strong_ordering` | less, equal, greater | equal values are interchangeable | integers, `std::string` |
| `std::weak_ordering` | less, equivalent, greater | equivalent values may differ | case-insensitive keys |
| `std::partial_ordering` | less, equivalent, greater, unordered | some pairs are incomparable | `double` (NaN) |

Stronger converts implicitly to weaker. A defaulted `auto operator<=>` returns the weakest category among its members, so one `float` member makes the whole struct `partial_ordering`. These categories are promises you make; the compiler does not check that your `strong_ordering` is really substitutable.

### in code

**Before and after.**

```cpp
#include <compare>
#include <tuple>

// C++17
struct Cell17 {
    int row, col;
    friend bool operator==(const Cell17& a, const Cell17& b) { return std::tie(a.row, a.col) == std::tie(b.row, b.col); }
    friend bool operator!=(const Cell17& a, const Cell17& b) { return !(a == b); }
    friend bool operator< (const Cell17& a, const Cell17& b) { return std::tie(a.row, a.col) <  std::tie(b.row, b.col); }
    friend bool operator> (const Cell17& a, const Cell17& b) { return b < a; }
    friend bool operator<=(const Cell17& a, const Cell17& b) { return !(b < a); }
    friend bool operator>=(const Cell17& a, const Cell17& b) { return !(a < b); }
};

// C++20
struct Cell {
    int row, col;
    auto operator<=>(const Cell&) const = default;   // also gives a defaulted ==
};
// Cell{1, 2} < Cell{1, 3}: true; result type of <=> is std::strong_ordering
```

Reordering `row` and `col` in `Cell` changes the ordering. With the defaulted operator, declaration order is part of the type's observable behavior, so keep the most significant key first and leave a comment when it matters.

**Predict the output.** A detection with a `float` member:

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

It prints `0 0 0 0`. `x <=> y` is `unordered`, so every relational comparison is false, and the defaulted `==` compares `range_m` with `==`, so `x == x` is false too. Equality that is not reflexive breaks `std::find`, `std::set`, and any cache keyed on the struct.

**A custom ordering, and the `==` you must write.** A parameter server whose keys compare case-insensitively:

```cpp
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

`weak_ordering` is the honest category: `"MaxVelocity"` and `"maxvelocity"` are equivalent for ordering but are not the same string. The hand-written `==` must agree with `<=>`; a defaulted one here would compare case-sensitively and contradict the ordering.

### in practice

A deployment tool decides whether to flash new firmware. Versions look like `2.1.0-rc1` and, per semantic versioning, a prerelease sorts *before* its release. The defaulted operator gets that wrong, because the empty string sorts before `"rc1"`:

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

`std::tie(...) <=> std::tie(...)` uses C++20's `<=>` on `std::tuple`, which keeps the "compare these three in order" logic in one line. Defaulting `==` is fine here: two versions are equal exactly when all four fields are, which agrees with the custom ordering.

Leave out that `==` and you find out quickly: `std::ranges::sort(versions)` and `std::ranges::max(versions)` stop compiling, because `std::totally_ordered` (day 29) requires equality as well as ordering. The concept caught a half-specified type at the call site.

### watch out for

**Partial orders in algorithms that require a strict weak ordering.** `std::sort`, `std::set`, and `std::map` require that the comparison be a strict weak ordering over the values you actually pass. With NaN in the data, `<` on `double` (or on a struct whose defaulted `<=>` is `partial_ordering`) is not one, and violating that precondition is undefined behavior. Typically you get silently misordered output; with some invalid comparators, implementations have also been known to read past the end of the range. Either reject NaN at the boundary (a sensor driver is a good place) or sort with `std::strong_order`, which for IEEE 754 types implements the `totalOrder` predicate (-0 before +0, positive NaNs after all numbers):

```cpp
std::sort(v.begin(), v.end(), [](double a, double b) { return std::strong_order(a, b) < 0; });
// {3, NaN, -0.0, 0.0, 1} sorts to: -0 0 1 3 nan
```

Two smaller traps: writing `<=>` by hand silently removes the implicit `==` (you get "no match for 'operator=='" only where someone uses it), and a hand-written `==` that returns `int` cannot be used for a rewritten `!=` (GCC: "return type of ... is not 'bool'").

### the takeaway

Default `<=>` (and get `==` for free) when member-wise lexicographic order in declaration order is what you mean. When it is not, write `<=>` with an honest category and write `==` next to it, consistent with it. Watch any `float` member: it turns your type's ordering into a partial one.

### optional challenge

Given `struct Meters { double v; auto operator<=>(const Meters&) const = default; bool operator==(double d) const { return v == d; } };` and `Meters m{2.0};`, which of these compile: `m == 2.0`, `2.0 == m`, `m != 2.0`, `m == Meters{2.0}`, `m < 3.0`?

<details>
<summary>answer</summary>

`m == 2.0` calls the member directly. `2.0 == m` compiles via the reversed candidate `m == 2.0`, and `m != 2.0` via the rewritten `!(m == 2.0)`; both rely on the `==` returning `bool`.

`m == Meters{2.0}` does **not** compile, which surprises most people. Declaring `operator==(double)` counts as declaring an `operator==`, so the compiler no longer adds the implicit defaulted `operator==(const Meters&)` that defaulting `<=>` would otherwise give you. Add `bool operator==(const Meters&) const = default;` explicitly. (`m < Meters{3.0}` still compiles; only `==` is affected.)

`m < 3.0` does not compile either: the only `<=>` takes `const Meters&`, and `Meters` has no converting constructor from `double` (aggregate initialization is not an implicit conversion). If you want it, add `std::partial_ordering operator<=>(double d) const { return v <=> d; }`; the category is partial because of NaN. All five were checked with GCC 12.

</details>
