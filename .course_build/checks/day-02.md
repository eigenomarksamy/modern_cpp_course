# checks: day 02

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic` unless noted.

- predict-the-output (vectors, strings, `Pose` aggregate): compiled cleanly, ran, printed `3 2 0`, `3 2`, `0 0` as stated.
- `auto` with braces: `static_assert`s that `auto a{1}` is `int` and `auto b = {1}` is `std::initializer_list<int>` pass; `auto c{1, 2};` fails with "direct-list-initialization of 'auto' requires exactly one element".
- narrowing and vexing parse snippet: `RadarConfig cfg{250.0, 70000}` is an error (70000 to uint16_t); `char c{300}` is an error; `int b{measured}` is only a `-Wnarrowing` warning on GCC 12 (lesson says so); `double` non-constant to `float` in an aggregate also only warned. `Timer t(Clock())` gives `-Wvexing-parse` warning and an error on `t.start()`.
- promotions snippet: printed `300`, `0`, `18446744073709551615`, `A`; `-Wsign-compare` warning on `i < u` confirmed. `sizeof(long)` printed 4 on this MinGW target.
- in practice `ImuConfig cfg{400}`: compiles with no warnings (no `-Wmissing-field-initializers` when members have default initializers; a variant without them did warn under `-Wextra`).
- watch out for (`Sensor s{}` reading `id`): `-Wuninitialized` warning at `-O2`, none at `-O0`, consistent with the lesson's caveat.
- challenge: `std::uint32_t{a} * b` with 65535, 65535 printed `4294836225`. The UB of the unfixed version was not "observed" (UB cannot be confirmed by running); it follows from the promotion rules.

Not checked: Clang's behavior (no Clang installed; "Clang rejects both" is from Clang's documented default of treating narrowing as an error). C++20 aggregate rule change and `std::cmp_less` mentioned but not compiled.
