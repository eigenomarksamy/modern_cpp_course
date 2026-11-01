# day 29 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++20 -Wall -Wextra -pedantic`, scratch folder outside the repo.

- "the idea": `std::sort` on `std::list<int>` versus `std::ranges::sort` compiled with both spellings. Old: first error `no match for 'operator-'` in `stl_algo.h:1938`. New: error at the call line, notes name `random_access_range` and `'std::random_access_iterator_tag' is not a base of 'std::bidirectional_iterator_tag'`. Line counts were similar (24 versus 30), so the lesson does not claim shorter output.
- before/after `gcd17` / `gcd` / `gcd2` / `gcd3` / `scale`: compiles clean, ran: gcd results 6, `scale(0.5, 7L)` = 3.5. `gcd(12, 18L)` fails with "deduced conflicting types for parameter 'T' ('int' and 'long int')"; `gcd(1.5, 2.5)` fails with "'is_integral_v<_Tp> [with _Tp = double]' evaluated to 'false'".
- `Sensor` concept, `Imu`, `Encoder`, `poll`: compiles clean, `static_assert(Sensor<Imu>)` passes. `poll(enc)` fails with "'s.read()' does not satisfy return-type-requirement" (verbatim GCC 12 note).
- `describe` overloads: ran, printed `integral`, `arithmetic`, `integral` as stated.
- templated lambda `clamp_all`: ran; float call works; `(floats, 0.0, 1.0)` fails with conflicting types float/double.
- raw-trait overloads `g`: `g(1)` gives "call of overloaded 'g(int)' is ambiguous"; with `std::integral<T>` in both, the 4-byte overload is selected (printed `32-bit integral` for `int32_t`, `integral` for `int64_t`).
- `half` with `x.value` in a constrained template: compiles with no error when not instantiated.
- challenge `Addable`: `static_assert`s for string (true), `const char*` (false), `short` (true), `bool` (true) all pass.

Not checked: nothing in this lesson needs a newer toolchain.
