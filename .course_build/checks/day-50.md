# compile checks: day 50

Toolchain: MSYS2 g++ 12.1.0 (Windows), scratch folder outside the repo.

- **naive benchmark** (`system_clock`, unused `std::accumulate` result): compiled with `g++ -std=c++17 -Wall -Wextra -pedantic -O2`, no warnings. Inspected `-O2 -S` output: the two `system_clock::now()` calls are adjacent with no summation code between them, confirming the dead-code-elimination claim for GCC 12. The run printed a near-zero time (not shown in the lesson).
- **`measure` harness** with `steady_clock`, warm-up, 31 repetitions, median/min/max, `volatile` sink, runtime-seeded input: compiled with the same flags plus `-O2`, no warnings; ran and printed a median/min/max line. No timing numbers are quoted in the lesson.
- **Google Benchmark example**: not compiled; the library is not installed. Checked by reading against the library's documented API (`benchmark::State`, `state.range(0)`, `DoNotOptimize`, `BENCHMARK(...)->Range`, `BENCHMARK_MAIN`, `--benchmark_repetitions`, `--benchmark_report_aggregates_only`).
- **perf commands**: not run (perf is not available on this Windows machine); shown as usage only.
- Library facts stated: libstdc++ defines `high_resolution_clock` as `system_clock`; MSVC's STL defines it as `steady_clock` (from library sources/documentation, not tested here).
