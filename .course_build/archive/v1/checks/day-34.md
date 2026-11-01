# day 34 compile checks

Toolchain: MSYS2 g++ 12.1.0 (libstdc++ 12), flags `-std=c++20 -Wall -Wextra -pedantic`, scratch folder outside the repo.

## `std::format` code: NOT compile-checked

GCC 12 / libstdc++ 12 has no `<format>` (it arrived in GCC 13), and no other compiler or {fmt} install is available on this machine. The basics block, the `std::formatter<Pose2D>` specialization, `log_cycle` with `std::format_to_n`, `log_info` with `std::format_string<Args...>`, and the challenge answer (`std::vformat` / `std::make_format_args`) were written against the C++20 standard as amended by P2216 (compile-time checked format strings), P2418 (arguments taken by forwarding reference), and P2905 (`make_format_args` takes lvalues, which the challenge answer respects), with `format()` declared `const` per LWG 3636.

What was done instead, and must not be mistaken for a real check:

- Syntax-only check (`-fsyntax-only`) of the format snippets against a hand-written stub header that declares `formatter`, `format_context`, `format_string`, `format`, `format_to`, `format_to_n` with standard-like signatures. Passed. This catches typos only; it says nothing about the real library's behavior or its compile-time format checking.
- Expected output strings cross-checked with Python's `str.format`, whose mini-language `std::format` follows for these specs: `"frame 1234567 range   1234.568 m status 0xff"`, `"a->b, b->a"`, `"(x=1.00, y=2.50, theta=0.79)"`, `"t=1712 joint=3 err=-0.0012"`, `"***ok****"` for `{:*^9}`.
- The compile errors claimed for `{:d}` with a `double` and `"{} {}"` with one argument follow from the P2216 consteval check; not observed.
- Library support versions (GCC 13, libc++ 17, MSVC 19.29) and the statement that current implementations expose the name `std::format_string` in C++20 mode (P2508) are from documentation, not tested.

## tour of other C++20 features: compiled and run

One file containing all tour excerpts (`PidConfig` designated initializers, `map::contains`, `starts_with`/`ends_with`, `std::erase_if`, `std::source_location` default argument, `popcount`/`has_single_bit`/`bit_width`/`countl_zero`, `bit_cast`, `std::endian`, `using enum` in a `switch`, `[[unlikely]]`, `std::midpoint`, `std::ssize` loop). Compiled clean and ran; observed output:

- `2.5 0 0.1 100` (designated initializer defaults), `1 0` (contains), `1 1` (starts_with/ends_with), `removed 2, left 3` (erase_if)
- `tour.cpp:51 int main(): frame dropped` (source_location reports the caller)
- `3 1 8 31` (popcount, has_single_bit, bit_width(255), countl_zero(uint32 1)), `3F800000 1` (bit_cast of 1.0f, little endian)
- `tracking` (using enum), `2147483646` (midpoint of INT_MAX-2 and INT_MAX), `9 7 3` (ssize reverse loop)
- broken variants: out-of-order designators fail with "designator order for field 'PidConfig::kp' does not match declaration order in 'PidConfig'"; `std::popcount(11)` fails with "no matching function for call to 'popcount(int)'".
