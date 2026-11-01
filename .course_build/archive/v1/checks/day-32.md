# day 32 compile checks

Toolchain: MSYS2 g++ 12.1.0 (libstdc++ 12), flags `-std=c++20 -Wall -Wextra -pedantic`, scratch folder outside the repo.

- before/after `Cell17` / `Cell`: compiled clean, ran; `Cell{1,2} < Cell{1,3}` etc. as expected; `static_assert` that `Cell <=> Cell` is `std::strong_ordering` passes.
- predict-the-output `Detection` with a `float` NaN: `static_assert` that the defaulted `<=>` returns `std::partial_ordering` passes; ran, printed `0 0 0 0` as stated.
- `ParamKey` (case-insensitive, `weak_ordering`, `std::lexicographical_compare_three_way`): ran; inserting "MaxVelocity" and "maxvelocity" into a `std::set` leaves size 1.
- `Version` custom `<=>` with `std::tie(...) <=> std::tie(...)`: ran, sorted output `2.0.9 2.1.0-rc1 2.1.0`; the naive defaulted version ranks `2.1.0-rc1` above `2.1.0` (printed `rc<rel: 0`). Removing the defaulted `==` makes `==`, `std::ranges::sort` and `std::ranges::max` fail to compile ("no match for 'operator=='", "no match for call to '(const std::ranges::__sort_fn) ...'").
- `std::strong_order` sort of `{3, NaN, -0.0, 0.0, 1}`: ran, printed `-0 0 1 3 nan`. (Under `-std=c++17` it does not exist, as expected.)
- `int`-returning `operator==` used for `!=`: fails with "return type of 'int IntEqNoNe::operator==(const IntEqNoNe&) const' is not 'bool'".
- challenge `Meters`: `m == 2.0`, `2.0 == m`, `m != 2.0` compile and print `1 1 0`; `m == Meters{2.0}` fails ("no match for 'operator=='"), confirming that declaring `operator==(double)` suppresses the implicit defaulted `==` (the first draft of the answer had this wrong and was corrected); `m < 3.0` fails; `m < Meters{3.0}` compiles.

Investigated and left out: an old-style non-const member `operator==` that is said to become ambiguous under C++20 reversed candidates compiled without error or warning on GCC 12, so the lesson makes no claim about it.

Not checked: the claim that invalid comparators can make some `std::sort` implementations read out of range is stated from known reports, not reproduced (UB).
