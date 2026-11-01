---
title: defaulted comparisons and the spaceship operator
standard: C++20
objective: replace hand-written comparison operators with a defaulted operator<=> and operator==, and know how C++20 rewrites comparison expressions
prerequisites: writing-concepts, object-layout
difficulty: 2
---

### the idea

to put a two-field grid cell in a `std::set` or sort it, C++17 asked for six operators, usually written as a pile of `std::tie` boilerplate. each one is a chance for a typo (`<=` implemented as `!(a < b)` instead of `!(b < a)`), and the next person to add a field has to update all of them.

C++20 replaces the pile with one line, but the line comes with rules: which operators the compiler synthesizes, which "kind" of ordering you get, and when it quietly stops generating `==` for you. those rules are worth ten minutes, because the failure modes are a missing operator at best and a sort with undefined behavior at worst.

### understanding the concept

**the spaceship.** `a <=> b` returns an object that says less, equal (or equivalent), greater, or, for some types, unordered. you compare it against the literal `0`: `(a <=> b) < 0` means `a < b`.

**rewriting.** you no longer write the relational operators. for `a < b`, the compiler also considers `(a <=> b) < 0` and the reversed form `0 < (b <=> a)`; likewise for `>`, `<=`, `>=`. for `a != b` it considers `!(a == b)` and `!(b == a)`, and for `a == b` it also tries `b == a`. two consequences: one `operator==(const Meters&, double)` makes `2.0 == m` work as well, and a rewritten `!=` requires the `==` it uses to return exactly `bool`.

**defaulting.** `auto operator<=>(const T&) const = default;` compares base classes first, then non-static members **in declaration order**, lexicographically, stopping at the first difference. `bool operator==(const T&) const = default;` compares the same things with `==`. if you default `<=>` and the class declares no `operator==` at all (of any signature), the compiler also declares a defaulted `==` for you. if you *write* `<=>` yourself, it does not.

**why `==` is separate.** the original C++20 design derived `==` from `<=>`, and it was split out (P1185) for performance. equality on containers can return `false` as soon as the sizes differ (that is how the standard specifies container `==`, and mainstream `std::string` implementations do the same); a three-way comparison has to walk to the first differing element, because a shorter string can still compare greater. for two log lines of different lengths sharing a 4 KiB prefix, `==` can stop after comparing sizes, while `<=>` reads the whole prefix.

### in code

**before and after.**

```cpp complete
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

### in practice

defaulted comparisons pay off in the types that are compared most: keys in `std::set` and `std::map`, values checked in unit tests, messages deduplicated in a cache. one line gives a struct a complete, consistent set of operators, and when someone adds a field, equality and ordering include it automatically instead of silently ignoring it, as a forgotten line in a hand-written `operator<` would. that automatic inclusion deserves a moment in code review: adding a `last_seen_s` timestamp to a track that is used as a map key changes which tracks compare equal. whether a field participates in a type's identity is a design decision, and with defaulted comparisons the declaration is where that decision lives.

### watch out for

**declaration order is behavior.**

reordering `row` and `col` in `Cell` changes the ordering. with the defaulted operator, declaration order is part of the type's observable behavior, so keep the most significant key first and leave a comment when it matters.

two smaller traps: writing `<=>` by hand silently removes the implicit `==` (you get "no match for 'operator=='" only where someone uses it), and a hand-written `==` that returns `int` cannot be used for a rewritten `!=` (GCC: "return type of ... is not 'bool'").

### the takeaway

default `<=>` (and get `==` with it) when member-wise comparison in declaration order is what you mean; then the compiler writes every operator, consistently, and keeps them up to date.

### optional challenge

given `struct Meters { double v; auto operator<=>(const Meters&) const = default; bool operator==(double d) const { return v == d; } };` and `Meters m{2.0};`, which of these compile: `m == 2.0`, `2.0 == m`, `m != 2.0`, `m == Meters{2.0}`, `m < 3.0`?

<details>
<summary>answer</summary>

`m == 2.0` calls the member directly. `2.0 == m` compiles via the reversed candidate `m == 2.0`, and `m != 2.0` via the rewritten `!(m == 2.0)`; both rely on the `==` returning `bool`.

`m == Meters{2.0}` does **not** compile, which surprises most people. declaring `operator==(double)` counts as declaring an `operator==`, so the compiler no longer adds the implicit defaulted `operator==(const Meters&)` that defaulting `<=>` would otherwise give you. add `bool operator==(const Meters&) const = default;` explicitly. (`m < Meters{3.0}` still compiles; only `==` is affected.)

`m < 3.0` does not compile either: the only `<=>` takes `const Meters&`, and `Meters` has no converting constructor from `double` (aggregate initialization is not an implicit conversion). if you want it, add `std::partial_ordering operator<=>(double d) const { return v <=> d; }`; the category is partial because of NaN. all five were checked with GCC 12.

</details>
