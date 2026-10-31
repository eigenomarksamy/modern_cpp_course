# checks: day 07

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic`.

- mini exercise (buggy `latest_range`): compiles; at `-O2` the only diagnostic is `'index' may be used uninitialized [-Wmaybe-uninitialized]`, matching the answer's claim that it was the only bug a warning caught. The dangling return and the empty-vector out-of-bounds index produced no warning. The buggy function was not run (UB).
- fixed `latest_range` returning `std::optional<float>`: compiled cleanly with a stub `load_tracks()` returning `{1, {10, 12.5}}` and `{2, {}}`; ids 1, 2, 3 gave 12.5, empty, empty, as stated.
- question 3 lines: compile without warnings on GCC 12 (wrapped in a function with stubs); the dangling analysis is from the lifetime rules (GCC 13's `-Wdangling-reference` is not available here).
- question 2 sizes (`{10, 0}` gives 2, `(10, 0)` gives 10): checked by running, printed `2 10`.
- question 1 and 4 facts were verified on days 01 and 06 (multiple definition link error; right-to-left argument evaluation observed with GCC).

Not checked: question 5 is conceptual (double `fclose` described from the C standard library's rules, not run).
