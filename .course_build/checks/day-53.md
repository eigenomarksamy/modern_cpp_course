# compile checks: day 53

Toolchain: MSYS2 g++ 12.1.0 (Windows), scratch folder outside the repo.

- **all four cpp blocks extracted verbatim** (Watchdog + FakeClock + `check` with `std::source_location`; `log_event` + `LOG_DEBUG` macro; `LatencyHistogram` + `ScopeTimer`; the `LLVMFuzzerTestOneInput` target) and concatenated with a small driver (`compute_residual`, a stub `parse_nmea_sentence`, `main`). Flags: `g++ -std=c++20 -Wall -Wextra -pedantic -O2`. No warnings.
- **observed behavior**: the watchdog test passed (0 failures) and a deliberate failing `check` printed the caller's file and line; at level `info`, `LOG_DEBUG` did not evaluate its arguments (`compute_residual` called once, only after switching to `debug`), while a direct disabled `log_event` call did evaluate its argument (checked in a separate scratch version); the histogram recorded one span per `ScopeTimer`.
- **fuzz target**: compiled as an ordinary function only; not linked with libFuzzer (clang/libFuzzer not installed). No fuzzing was run.
- **sanitizer CI matrix**: shown as configuration text; not run (GCC on MinGW here has no sanitizer runtime). The ASan/TSan incompatibility is from the sanitizer documentation.
- `std::format` deliberately not used in compiled code (no `<format>` in GCC 12); the lesson mentions it only as the preferred formatter on newer toolchains.
