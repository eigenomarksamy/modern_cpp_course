# day 31 compile checks

Toolchain: MSYS2 g++ 12.1.0 (libstdc++ 12, x86-64), flags `-std=c++20 -Wall -Wextra -pedantic`, scratch folder outside the repo.

- before/after `rms17` / `rms` / `scale` / `demo`: compiled clean; ran `rms` on a C array, vector, `std::array`, and `first`/`last`/`subspan` slices, values as expected (3.53553 for {3, 4}).
- static extent `set_pose(std::span<const double, 6>)`: `std::array<double, 6>` works and ran; `std::array<double, 5>` fails with "could not convert 'p5' from 'std::array<double, 5>' to 'std::span<const double, 6>'" (verbatim); a `std::vector` argument fails similarly; `std::span<const double>(pv).first<6>()` compiles and runs.
- `sizeof(std::span<float>)` = 16 and `sizeof(std::span<float, 4>)` = 8, printed on this toolchain.
- CTAD: `std::span{raw}` has extent 4, `std::span{vec}` has `dynamic_extent`; `std::span{&pkt, 1}` is dynamic, so `as_bytes` yields `std::span<const std::byte>` (static_assert passes). `sizeof(TelemetryPacket)` = 12 and the byte span has 12 elements (printed).
- `RangeDopplerFrame` with `row()` const/non-const and `peak`: compiled clean, ran, printed `3 0 3` and `3`.
- `-D_GLIBCXX_ASSERTIONS` with an out-of-range `span::operator[]`: aborts with "Assertion '__idx < size()' failed" (ran).
- watch out / challenge: `std::span<float> a = make_samples();` fails ("conversion from 'std::vector<float>' to non-scalar type 'std::span<float>' requested"); cases 2, 3 and 4 compile with no warning under `-Wall -Wextra -pedantic`; case 4 ran and printed 9. The dangling cases were compiled only, not run (UB).

Not checked: other standard libraries' span sizes (the lesson says "typical"); C++26 `span::at` (stated from the standard, not compiled).
