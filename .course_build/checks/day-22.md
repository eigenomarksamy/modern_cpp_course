# day 22 compile checks

Toolchain: MSYS2 g++ 12.1.0. Flags: `-std=c++17 -Wall -Wextra -pedantic` unless noted. Scratch: `$TEMP/claude/cpp-week-4/`.

- `Pose` predict-the-output snippet: compiled clean, ran, printed `10.0 1.0 20.0` as stated; the `static_assert` that `decltype(ry)` is `double` passed.
- before/after `find_gain` plus `dump`: compiled together (before version wrapped in a namespace to avoid redefinition) with a test `main`; calling the `[[nodiscard]]` version and discarding the result produced `-Wunused-result` warning as described; output correct.
- `switch` with initializer, `[[fallthrough]]`, `[[maybe_unused]]`: compiled clean with stub member definitions, with and without `-DNDEBUG`. Removing `[[fallthrough]]` produced `-Wimplicit-fallthrough=` under `-Wextra`; removing `[[maybe_unused]]` with `-DNDEBUG` produced `-Wunused-variable`, as described.
- telemetry `on_message` with `try_emplace` and `auto&` bindings: compiled and ran; printed `new topic: imu` once, count 2.
- optional challenge: ran, printed `1` then `11`.
- `Range` member reorder trap: compiled the reordered struct; bindings silently swapped (`9 1`), no warning.
- lambda capture of a structured binding: g++ 12 accepts `[a]` and `[&b]` with `-std=c++17 -pedantic` without any diagnostic (the lesson says so). Behavior of Clang/MSVC in C++17 mode was not checked locally; the lesson only says other compilers reject or warn.
- The one-line fragments in "understanding the concept" are illustrative and were not compiled on their own.
