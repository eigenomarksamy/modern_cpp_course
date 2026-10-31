# compile checks: day 51

Toolchain: MSYS2 g++ 12.1.0 (x86-64, Windows), scratch folder outside the repo.

- **all four cpp blocks** (three `sum_x` traversals; AoS `Detection` + `count_strong`; SoA `Detections` + `count_strong`; `alignas(64) PaddedSum` in a `std::vector`) were extracted verbatim from the lesson file, concatenated with a small driver `main` (and a `num_threads` constant for the in-practice fragment), and compiled with `g++ -std=c++17 -Wall -Wextra -pedantic -O2`: no warnings, ran correctly.
- **layout claims checked by printing `sizeof`** on this target: `Detection` = 64, hot part (4 floats + 2 uint32) = 24, `Particle {bool; double x3; bool}` = 40, reordered = 32. The lesson labels these as typical 64-bit ABI values, not guarantees.
- **over-aligned vector elements**: verified `&partial[1]` is 64-byte aligned with `std::vector<PaddedSum>` under C++17 (aligned `operator new`).
- **not measured**: no timings are claimed; the latency table is explicitly labelled as rough orders of magnitude. `perf stat` was not run (not available on Windows); shown as usage only.
