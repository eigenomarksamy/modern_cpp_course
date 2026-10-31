# day 19 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic` unless noted; scratch folder outside the repo. Snippets extracted mechanically from the lesson.

- forwarding versus rvalue reference declarations: compiled clean (the `auto&& r` line wrapped in a function for compilation).
- relay predict-the-output: printed `copy`, `move`, `copy`, `move`, matching the comments.
- `make_tracked` variadic factory with `Joint`: compiled clean, ran, counter reached 2.
- C++17 versus C++20 parenthesized aggregate init: `std::make_unique<Point>(1.0, 2.0)` fails under `-std=c++17` (`new initializer expression list treated as compound expression`) and compiles and runs under `-std=c++20`.
- `auto&&` over `std::vector<bool>`: compiled clean and set all flags; the commented `auto&` form fails with `cannot bind non-const lvalue reference ... to an rvalue`, as described.
- `post_and_log` double-forward fragment: compiled with stub `log_args`/`post` (the bug is semantic, not a compile error).
- greedy `Sensor` constructor: `Sensor b{a}` fails with `no matching function for call to std::string::basic_string(Sensor&)`. Copying from a `const Sensor` compiles. The `enable_if_t<!std::is_base_of_v<Sensor, std::decay_t<S>>, int> = 0` constraint makes `Sensor b{a}` compile.
- optional challenge: `__PRETTY_FUNCTION__` shows `T = int&`, `const int&`, `int`, `const int` for the four calls, matching the answer.
- not checked: the instantiation-count claim for string literals of different lengths was reasoned from deduction rules (`const char(&)[N]`), not measured in a binary.
