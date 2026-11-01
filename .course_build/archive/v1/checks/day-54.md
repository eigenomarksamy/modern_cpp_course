# compile checks: day 54

Toolchain: MSYS2 g++ 12.1.0 (Windows), scratch folder outside the repo.

- **legacy `load_calibration` + characterization test**: both blocks extracted verbatim, plus a `write_file` helper (`std::ofstream`) and `main`. `g++ -std=c++17 -Wall -Wextra -pedantic -O2`: no warnings; all asserts passed against the legacy code (including acceptance of `"1 2 3 garbage"`, `"parse failed"` and `"open failed"` messages).
- **modern `read_calibration` + `[[deprecated]]` shim**: block extracted verbatim with `struct Calib` prepended (the lesson reuses the legacy definition), compiled with the same flags; the same characterization test passed against the shim. A separate caller of the shim produced the expected `-Wdeprecated-declarations` warning (suppressed with a pragma only inside the test file used to run the characterization test).
- **strncpy claim**: a scratch program confirmed that `strncpy` into a 4-byte buffer from a longer source leaves no terminator.
- **not run**: `run-clang-tidy`, `clang-format`, and the `.git-blame-ignore-revs` step (clang tools not installed); shown as usage only. The ADR is prose, nothing to compile.
