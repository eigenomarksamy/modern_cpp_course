# day 39 compile checks

Toolchain: MSYS2 g++ 12.1.0 (winpthreads), flags `-std=c++17 -Wall -Wextra -pedantic -pthread`; code blocks extracted verbatim from the lesson into a scratch folder outside the repo.

- promise/future `calibrate` example: compiles cleanly, runs, exit 0 (the `runtime_error` was rethrown by `get()` and caught).
- `mean_height` with `std::async`: compiles cleanly. Test harness: 1,000,001 points, 4 parts, result matched the serial expectation (4.499996); empty cloud returned 0.
- the "accidentally sequential" bug: with a 100 ms task, 4 discarded `std::async` futures took 443 ms, 4 kept futures took 117 ms (single run; illustrative only). GCC 12 emits `-Wunused-result` for the discarded future because libstdc++ declares `std::async` `[[nodiscard]]`; the lesson now says so.
- edge-case table: `get()` twice threw `std::future_error: No associated state` on libstdc++ (the standard makes it UB; lesson says libstdc++ happens to throw); abandoned promise gave `broken_promise`; second `set_value` gave `promise_already_satisfied`; `wait_for` on a `deferred` future returned `future_status::deferred`; `shared_future::get()` callable twice.
- `packaged_task` example: compiles cleanly, exit 0 (value 42).
- watch-out loop: syntax-checked with stub `compute_tracks`/`report_progress`; not run (with the default policy libstdc++ chooses async, so the infinite loop would not reproduce here; the claim rests on the standard's policy rules).
- Not checked: whether `std::async` reuses threads on other implementations (described as implementation-dependent only).
