# day 18 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic`; scratch folder outside the repo. Snippets extracted mechanically from the lesson.

- `clamp_to(speed, 0, 10)`: fails with `no matching function` and the note `deduced conflicting types for parameter 'T' ('double' and 'int')`, as described.
- `enable_if` `half`: `half(4)` compiles and returns 2; `half(3.0)` fails with `no matching function` (substitution failure on `enable_if<false, int>`).
- `RingBuffer`, `Setting` with deduction guide, `Constant<auto>`: compiled clean; `static_assert`s confirm `gain` is `Setting<double>` and `mode` is `Setting<std::string>`. With the guide removed, `mode` is `Setting<const char*>`, confirming the comment.
- `Serializer` specializations and `describe` overloads: printed `3 true ptr:3 null`. Enabling the commented partial specialization of `describe` fails with `non-class, non-variable partial specialization 'describe<T*>' is not allowed`.
- dependent base (`Filter::clear`): `this->reset()` version compiles and runs; the unqualified `reset()` version fails with the quoted GCC message (checked by forcing instantiation).
- specialization surprise: prints `c`, matching the comment. Also checked the alternative stated in prose: `template <> void f(int*)` declared after both templates prints `b`, while `template <> void f<int*>(int*)` after both still prints `c`.
- optional challenge: `std::vector v{inner}` is `std::vector<int>` with size 2 (static_assert + runtime check); `std::vector w{inner, inner}` is `std::vector<std::vector<int>>`.
- not checked: `extern template`/explicit instantiation build-time savings and the 60-translation-unit scenario are illustrative, not measured. `-ftime-trace` is a Clang flag, not available in this toolchain.
