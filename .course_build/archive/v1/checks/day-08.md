# compile checks: day 08

Toolchain: MSYS2 g++ 12.1.0, scratch folder outside the repo. Flags: `-std=c++17 -Wall -Wextra -pedantic` unless noted.

- naive `read_header` (with a stub `validate` and `main`): compiles, no warnings. The leak is a logic bug, not diagnosed; not run under a leak checker (no sanitizers on this mingw build).
- RAII `read_header` with `FileCloser`/`FilePtr` (stub `validate` that throws for version 0, deleter instrumented with a print): compiles clean; run showed `fclose` printed before the exception was caught, and a missing file returns empty without calling the deleter. Added `static_assert(sizeof(FilePtr) == sizeof(std::FILE*))`: holds on this toolchain.
- `ScopeGuard` with CTAD: compiles clean with `-std=c++17` and `-std=c++20`; output `body done`, `release b`, `release a`, matching the lesson.
- `TorqueEnable` / `run_trajectory` (stub `MotorBus`, `step` throws on a setpoint over 1.0): compiles clean; output `enable`, `disable`, then the caught message, confirming destructor before handler.
- unnamed `std::lock_guard<std::mutex>{mtx_};`: compiles with no warning under `-Wall -Wextra -pedantic` (the lesson states this).
- optional challenge: with the handler prints `b`, `a`, `sensor timeout`. With the `try`/`catch` removed (`-DNOCATCH`): prints only the libstdc++ terminate message, exit code 3, no destructor output; consistent with "implementation-defined, GCC typically does not unwind".

Not checked: the C++20 rule that forming a pointer to a non-addressable standard library function is unspecified (stated from the standard wording, [namespace.std]; GCC does not diagnose it). Library Fundamentals TS `scope_exit` not compiled.
