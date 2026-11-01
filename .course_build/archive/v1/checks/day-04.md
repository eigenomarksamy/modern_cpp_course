# checks: day 04

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic`. Blocks extracted from the lesson and compiled as written, with small `main` functions or stub types appended where needed.

- reference/nullptr block: compiled cleanly, printed `2 2`, `int`, `const char*`. Uncommenting `log_value(NULL)` gives "call of overloaded 'log_value(NULL)' is ambiguous" on GCC 12 (NULL is `__null`), as stated. The "silently prints int where NULL is 0" case is from the rules, not run on such an implementation.
- decay block: `-Wsizeof-array-argument` warning confirmed (without asking for it). With a 64-element buffer whose first element is 64, printed `32 1` (mean_bad, template mean). The commented UB lines were not executed.
- side check: with both functions named `mean`, GCC picked the template for a non-const `float[4]`; the lesson avoids making any claim about that.
- `Calibration` (mutable cache + mutex): compiled cleanly, `offset()` on a const object with {1,2,3} printed `2`.
- `Tracker` signatures: compiled with stub `DetectionBatch`, `Track`, `TrackId`; clean.
- `Arm` shallow-const block: clean; uncommenting the `spare_` line gives "assignment of member 'Joint::angle' in read-only object". A run with a non-null `joints_` confirmed the joint was modified through a const object.
- challenge: lines (3) and (4) are errors ("assignment of read-only location '* p'", "assignment of read-only variable 'q'"); without them the program printed `5`.

Not checked: the claim that `std::less<T*>` gives a total order and that unrelated-pointer `<` is unspecified are from the standard, not testable by running.
