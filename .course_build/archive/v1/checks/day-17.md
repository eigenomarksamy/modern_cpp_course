# day 17 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic` unless noted; scratch folder outside the repo. Snippets extracted mechanically from the lesson.

- closure equivalence (`f` versus hand-written `Closure g`): compiled clean inside a driver; both return 2 for input 1.0.
- predict-the-output (by value / by reference / mutable counter copy / immediately invoked lambda): compiled clean, printed `12`, `31`, `fast`, matching the comments.
- `Deferred` dangling capture: file compiled clean; ran the fixed version (`report: radar`). The buggy version was not run (UB; no sanitizers on this mingw build).
- `std::function` versus template with a move-only closure: compiled clean and ran; enabling the commented `count_if_erased(pts, in_range)` line fails with `static assertion failed: std::function target must be copy-constructible`, as described.
- `std::function` allocation claim: measured with a counting global `operator new` on libstdc++ (GCC 12): lambda capturing two doubles 0 allocations, three doubles 1 allocation, reference capture 0. `sizeof(std::function<void()>)` is 32 here.
- `[=]` capturing `this` (`JointController`): compiles clean in C++17; with `-std=c++20` GCC warns `implicit capture of 'this' via '[=]' is deprecated in C++20 [-Wdeprecated]`. `[=, this]` under `-std=c++17` warns that it is a C++20 extension, consistent with the lesson. The use-after-destruction call was not run (UB).
- constexpr lambda with `static_assert(sq(4) == 16)`: compiles under C++17.
- optional challenge: stateful `remove_if` predicate prints `1 2 4 5 7 8 9` on libstdc++, matching the stated result.
- not checked: the 100,000-point / 20 Hz profiling scenario is illustrative, not measured.
