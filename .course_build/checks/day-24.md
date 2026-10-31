# day 24 compile checks

Toolchain: MSYS2 g++ 12.1.0. Flags: `-std=c++17 -Wall -Wextra -pedantic`. Scratch: `$TEMP/claude/cpp-week-4/`.

- `find_gain` returning `std::optional<double>` plus `configure`: compiled clean with a stub `apply_gain` and test `main`; printed `2.50` (found) and `0.10` (fallback).
- Predict-the-output snippet: compiled clean and ran. Output `111`, `empty`, `1`. My first draft said `110` for the first line; corrected to `111` after running (`b == 0` is true).
- `Track` with deleted copy and `lead.emplace`: compiled clean; two successive `emplace` calls left the second track in place (`2 50`).
- `Localizer` member: compiled with stub `GnssFix`, `Pose`, `Timestamp` types and a trivial `pose_at` definition; empty before `on_gnss`, engaged after.
- `optional<bool>` watch-out: compiled with stubs; with an empty optional the buggy `if` did not fire and the `value_or(true)` branch did.
- `sizeof(std::optional<double>)` is 16 and `sizeof(std::optional<int>)` is 8 on this x86-64 mingw toolchain, consistent with the "16 on mainstream 64-bit ABIs" statement (other ABIs not checked).
- `std::optional<int&>`: rejected by libstdc++ 12 (reference member in a union), consistent with "ill-formed in C++17". The C++26 `optional<T&>` note is from standards knowledge, not checked.
- C++23 monadic operations are mentioned only, not compiled.
