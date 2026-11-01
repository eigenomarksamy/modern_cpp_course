# day 36 compile checks

Toolchain: MSYS2 g++ 12.1.0 (winpthreads), flags `-std=c++20 -Wall -Wextra -pedantic -pthread`, scratch folder outside the repo.

- `ImuPoller` with `std::thread` + `std::atomic<bool>` (the labelled bug): compiles cleanly, no warning about the member-order race (GCC's `-Wreorder` does not apply because the initializer list order matches declaration order). Not run as evidence of anything; the race is UB by reasoning, not by observation.
- `ImuPoller` with `std::jthread` and `stop_token`: compiles, no warnings. Run inside a scope with a 55 ms sleep: printed `stopped after 4 polls`, destructor stopped and joined.
- argument passing (`fill` with `std::ref`, `log_line` with `std::string(buf)`): compiles and runs (`1024`, `radar link up`). The commented-out `std::thread t1(fill, samples);` was compiled separately and fails as stated (`static assertion failed: std::thread arguments must be invocable after conversion to rvalues`). The `t2` dangling-conversion line was not run (UB).
- `reader` with `std::stop_callback`: compiled with a stub `SerialPort` (condition-variable-based `read`/`cancel`) added to make it link; jthread destruction after 50 ms woke the blocked read via the callback (`reader stopped after 61 ms` instead of the 10 s timeout).
- optional challenge: compiles, printed `42` on 6 runs (guarantee is by the join synchronization rule, not by the runs).
- extra check of the "in practice" claim: a single-`stop_token` lambda started with a separate `stop_source`'s token received that token; `jthread::request_stop()` did not stop it; `process.request_stop()` did, and a `stop_callback` on the process token fired. `request_stop()` returned `1` then `0`.
- `std::thread::hardware_concurrency()` returned 16 here (only a hint; not claimed in the lesson).
