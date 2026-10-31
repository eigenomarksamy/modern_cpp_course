# checks: day 06

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic` (plus `-O2` where stated). Blocks extracted from the lesson.

- `will_overflow`: inspected `-O2` assembly. GCC emitted `shrl $31, %edx` / `ret` (tests the sign of `b` only), as the lesson says. The fixed version keeps the `INT_MAX - b` comparison.
- overflow loop `for (int i = 1; i > 0; i *= 2) ++count;`: printed `31` at `-O0`; at `-O2` it did not terminate (killed by a 3 s timeout). No warning was emitted.
- `read_status`: `-O0` assembly contains `cmpq $0` and the `-1` path; `-O2` assembly is a single `movl (%rcx), %eax` / `ret`.
- type punning: `-O2` gives `-Wstrict-aliasing` for `bits_bad`; all three versions (bad, memcpy, and C++20 `std::bit_cast` compiled with `-std=c++20`) printed `3f800000`. `bits_ok` at `-O2` compiled to `movd %xmm0, %eax` / `ret`, supporting the "register move" remark.
- `FrameHeader parse`: compiled cleanly, parsed `{0xEF,0xBE,2,0,7,0,0,0}` as `beef 2 7` on this little-endian target.
- order of evaluation: `log_pair(next_id(), next_id())` printed `2 1`; `i = i++ + 1` printed `1`; GCC 12 emits `-Wsequence-point` for it even with `-std=c++17`, as stated.
- challenge items 4 to 6: `signed char c = 200` gave `-56`, `-8 >> 1` gave `-4`, `i = i++` gave `0` (GCC again warned `-Wsequence-point`).
- `-D_GLIBCXX_ASSERTIONS`: an out-of-range `operator[]` aborted with the libstdc++ assertion message.

Not checked: sanitizers. This MinGW toolchain has no libasan/libubsan/libtsan (`cannot find -lasan`), so the sanitizer commands are written from GCC/Clang documentation and were not run. MSan, Valgrind, and the 2009 kernel incident are cited from documentation and history, not tested. The `-Werror` build line was not exercised on a project.
