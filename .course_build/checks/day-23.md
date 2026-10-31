# day 23 compile checks

Toolchain: MSYS2 g++ 12.1.0. Flags: `-std=c++17 -Wall -Wextra -pedantic`. Scratch: `$TEMP/claude/cpp-week-4/`.

- `before::put` (enable_if overloads) and the `if constexpr` `put`: compiled together; encoding `42`, an enum with `uint16_t` underlying type, and `std::string("hi")` produced identical 12-byte buffers from both versions.
- Passing `std::vector<int>` to `put`: failed with `static assertion failed: put: unsupported field type`, as described.
- Same `put` rewritten with plain `if`: `put(b, 42)` failed (`no type named 'type' in std::underlying_type<int>`, `request for member 'size' in 'v'`), supporting the "plain if instantiates every branch" claim.
- Fold snippet (`lsub`, `rsub`, `sum`, `all_finite`, `log_line`): ran; output `-4 2`, `0 3.5`, `0`, `imu 3 0.25 ` (trailing space) matches the comments.
- `encode` telemetry frame: compiled and ran; frame size 20 bytes, matching the stated arithmetic.
- `static_assert(false)` in a discarded branch: GCC 12 rejects it with `-std=c++17`, `-std=c++20`, and `-std=c++2b`, even when the template is never instantiated (tested with an empty `main`). GCC 13 / Clang 17 support for P2593 is stated from release notes knowledge, not checked locally.
- Non-template `if constexpr` with an invalid discarded branch: rejected, as described.
- Optional challenge: `a()` fails with `fold of empty expansion over operator+`; `b()` is `bool` `true`, `c()` is `int` `0` (checked with `static_assert` on the types and the exit code).
