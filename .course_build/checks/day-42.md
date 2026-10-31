# day 42 compile checks

Toolchain: MSYS2 g++ 12.1.0 (libstdc++ 12), flags `-std=c++20 -Wall -Wextra -pedantic -pthread`, scratch folder outside the repo.

## review question snippets: compiled, and run where meaningful

One file with Q1 (`Poller` with `jthread` declared before the buffer), Q2 (`add`), Q3 (producer/consumer), Q4 (the `std::async` loop and the fixed version that keeps futures), Q6 (`start_fft` and the move-capture fix), Q7 (`std::atomic<std::shared_ptr<const Config>>`).

- Q4: GCC 12 warns "ignoring return value of 'std::async(...)', declared with attribute 'nodiscard' [-Wunused-result]", supporting the answer's claim. The fixed loop with `std::vector<std::future<void>>` and `get()` runs.
- Q3: with the store under the mutex (`producer_fixed`), the consumer wakes. The lost wakeup was reproduced by writing out the predicate loop that `wait(lock, pred)` performs with a 200 ms sleep inserted between the check and `cv.wait(lock)`: a producer that sets the atomic flag and notifies without the mutex during that window leaves the consumer asleep (`consumer woke: no (lost wakeup)` after 2 s).
- Q6: the fix `[v = std::move(samples)] { fft(v); }` with `fft(std::span<const float>)` compiles (the const vector converts) and runs (`fft sum 1024`). The buggy version compiles without a warning; it was not run (UB).
- Q7: `std::atomic<std::shared_ptr<const Config>>` exists in libstdc++ 12; concurrent `store` and `load` from two threads ran; `is_lock_free()` returned `0` on this target, matching "not guaranteed to be lock-free".
- Q1, Q2: compiled only (both are UB by design).

## mini exercise: compiled and run

- Original `TelemetryHub` with a listener that calls `get()`: `set()` on another thread never completes (`listener calls: 0` after 2 s), the self-deadlock on `m_` that the answer describes (formally UB).
- Fixed `TelemetryHub` (verbatim from the lesson): the same re-entrant listener runs (`listener calls: 1`); a 4-thread stress test mixing `set`, `get`, and `on_change` completed. A single stress run is evidence, not proof; no ThreadSanitizer on MinGW.
