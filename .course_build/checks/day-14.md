# compile checks: day 14

Toolchain: MSYS2 g++ 12.1.0, scratch folder outside the repo. Flags: `-std=c++17 -Wall -Wextra -pedantic`.

- question 1 (`~Telemetry() = default;` with `std::string` and `std::vector<Sample>` members, `Sample` instrumented): `std::is_nothrow_move_constructible_v<Telemetry>` is 0, and both the initial `push_back` of a temporary and the reallocation copy the samples. With the destructor declaration removed, the trait is 1 and nothing is copied. Matches the answer.
- question 3: moved-from `std::string` (40 chars, so not SSO) has size 0 and `a[0]` is `'\0'` on libstdc++; `clear()` and assignment compile and run. Only the "valid but unspecified" contract is asserted in the lesson; `a.front()` on an empty string was not run (UB).
- question 6 (`load_config().name()` bound to `const std::string&`): compiles with no warning under `-Wall -Wextra` on GCC 12. It ran without crashing, which proves nothing; the lesson calls it UB from the lifetime rules (no sanitizers on this mingw build).
- mini exercise, original `TelemetryLog`: compiles clean (none of its bugs are diagnosed) and works on the happy path. The leak paths and double close are stated from the language rules, not observed.
- mini exercise, rule-of-zero rewrite: compiles clean; `static_assert`s confirm not copy constructible and nothrow move constructible/assignable. Run: stored in a vector, moved out, written, `flush()` checked, file contents correct; opening a path in a nonexistent directory throws "cannot open log".

Not checked: questions 2, 4, and 5 are conceptual and rely on snippets already compiled for days 10, 12, and 13 (`-Wpessimizing-move`, the `shared_ptr`/`unique_ptr` non-virtual destructor behavior).
