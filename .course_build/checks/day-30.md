# day 30 compile checks

Toolchain: MSYS2 g++ 12.1.0 (libstdc++ 12), flags `-std=c++20 -Wall -Wextra -pedantic`, scratch folder outside the repo.

- before/after `near_strong_17` / `near_strong_20`: compiled clean and ran on a 5-detection input; both returned `30 60 80` as stated.
- predict-the-output (transform then filter versus filter then transform): ran, printed `sum=56 calls=9` and `sum=56 calls=3`. Also confirmed that building the view alone makes 0 calls.
- `std::ranges::find(make_ids(), 42)`: `static_assert` that the result type is `std::ranges::dangling` passes; dereferencing fails with "no match for 'operator*' (operand type is 'std::ranges::dangling')" (verbatim).
- extra checks behind the prose: `ranges::min` with projection, `views::keys`/`values` on a map, `iota | reverse | drop`, and P2415 `owning_view` from an rvalue vector all compile and run; `next_frame().cells | views::take(2)` is `take_view<owning_view<vector<int>>>` (static_assert passes), which is why the lesson's range-for dangling example uses a reference-returning accessor instead.
- telemetry `parse` with `views::split` and the `string_view` iterator-pair constructor: ran, printed `[rpm] -> 1200`, `[temp] -> 71`, `[volt] -> 24`.
- `strong_ids` (dangling ref_view) compiles with no warning under GCC 12 (claim in lesson); the `std::move(ids)` version runs and prints `3 4`. The dangling version and the `next_frame().data()` range-for were compiled only, not run (UB; no sanitizer run on this MinGW toolchain).
- const `filter_view` passed to `void dump(const auto&)`: fails with "passing 'const std::ranges::filter_view<...>' as 'this' argument discards qualifiers"; the `auto&&` version works.
- challenge: as written prints `2 4 6`; capacity printed 4 before and 8 after the `push_back` (libstdc++), supporting the reallocation statement. The iterate-first variant is UB and was not run.

Not checked: behavior on other standard libraries (P2210/P2415 support is stated from the papers, not tested elsewhere).
