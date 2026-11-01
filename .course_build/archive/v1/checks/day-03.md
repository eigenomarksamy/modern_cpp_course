# checks: day 03

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic`. Code blocks were extracted from the lesson file and compiled as written (plus stub definitions where a block only declares functions).

- predict-the-output (`Tracer`): compiled cleanly, ran, printed exactly `+global main +a +static +b -b +temp use:temp -temp +ext +c return -c -ext -a -static -global`.
- dangling block: `-Wreturn-local-addr` warning for `frame_id()` as stated. No warning for the range-for over `load_frame().detections()` (lesson says GCC 12 gave none). Runtime effect of that UB was not inspected.
- static initialization order fiasco: built as two real files. Link order `prefix.cpp topic.cpp` printed `[tracks]`, order `topic.cpp prefix.cpp` printed `[radar/tracks]` (lesson does not say which order gave which). Function-local static version printed `[radar/tracks]` in both orders.
- `std::max` dangling: compiled at `-O2` with a stub `lo()`/`hi()` and a `printf` of both values; printed `0 7` and GCC emitted a `-Wuninitialized` warning, as the lesson says. Compiled at default optimization: no warning.
- challenge snippet: compiles cleanly (wrapped in a function with stub `load()`); safety analysis is from the standard's lifetime extension rules, not observed.

Not checked: C++23 range-for lifetime extension (P2718) and GCC 13 `-Wdangling-reference` (not available in GCC 12); C++20 `constinit` mentioned but not compiled; leaky singleton described only.
