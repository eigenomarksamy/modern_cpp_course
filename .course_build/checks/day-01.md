# checks: day 01

Toolchain: MSYS2 g++ 12.1.0 (x86_64-w64-mingw32), scratch folder outside the repo.

- duplicate symbol (`scale.h` included by `a.cpp` and `b.cpp`): `-std=c++17 -Wall -Wextra -pedantic`. Link fails with `multiple definition of 'scale(double)' ... first defined here` as shown (path prefixes trimmed in the lesson).
- silent ODR violation (`g1.cpp`, `g2.cpp`, `main.cpp`): `-std=c++17 -Wall -Wextra -pedantic`, no warnings. Observed: `-O0` order g1,g2 printed `a: 2` / `b: 2`; order g2,g1 printed `a: 3` / `b: 3`; `-O2` both orders printed `a: 2` / `b: 3`. `-O2 -flto` also printed `a: 2` / `b: 3` with no `-Wodr` warning (matches the lesson's statement that LTO did not flag it).
- mismatched `struct Pose` across two TUs with `-O2 -flto`: `-Wodr` warning with the "first difference ... field 'theta'" note, as quoted (trimmed).
- `nm -C main.o`: run on mingw; the real output also lists `U __main` (a mingw startup detail), which the lesson omits.
- `config.h` snippet (const, inline constexpr double and string_view, inline int, anonymous namespace): compiles cleanly with `-std=c++17 -Wall -Wextra -pedantic` (tested as a .cpp with a function using every name). With `-std=c++14` GCC warns that inline variables need C++17.
- linkage demo: `const int` address compared across TUs gave `0` (different objects); `static int` incremented twice in one TU and once in another read 2 and 1; `inline int` read 3.
- optional challenge `limits.h` in two TUs: link fails only with `multiple definition of 'g_target_count'`.

Not checked: ELF symbol kinds (`W` for inline functions) are not shown in the lesson; `#pragma once` path-aliasing failure was not reproduced (described from compiler documentation).
