# compile checks: day 10

Toolchain: MSYS2 g++ 12.1.0, scratch folder outside the repo. Flags: `-std=c++17 -Wall -Wextra -pedantic`.

- `move` definition (placed in a namespace `my` to avoid clashing with `std::move`): compiles clean; `static_assert` that `my::move(x)` on an `int` lvalue yields `int&&` holds.
- buggy `Frame` (shallow implicit copy): compiles with no warning (GCC does not diagnose missing rule-of-three). The double `delete[]` was not run or observed; no sanitizers on this mingw build. UB stated from the language rules.
- `Buffer` (deep copy, `noexcept` moves, `std::exchange`): compiles clean; `static_assert(std::is_nothrow_move_constructible_v<Buffer>)` holds. Exercised copy assign, self copy assign, move construct (moved-from size printed as 0), self move assign, `std::swap(c, c)`, and vector growth; outputs as expected (`0 8 8`, then `8`, `8`).
- `Track` predict-the-output: prints `copy` with the non-`noexcept` move constructor and `move` when compiled with the move constructor marked `noexcept`. Matches the lesson.
- `Tracker` / `acquire` / `loop` (stub frame and receiver types): compiles clean with `return f;`. With `return std::move(f);` GCC 12 emits "moving a local object in a return statement prevents copy elision [-Wpessimizing-move]" under `-Wall`, as the lesson states.
- `const std::string` moved: compiles clean, no warning; the source still has size 100 afterwards. A tracer type confirms `std::move` on a const object calls the copy constructor.

Not checked: the challenge's self-move-without-check analysis was reasoned from the code, not executed (the resulting double delete is UB and not reliably observable without ASan). `clang-tidy bugprone-use-after-move` not run (not installed).
