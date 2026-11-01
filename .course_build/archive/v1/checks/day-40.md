# day 40 compile checks

Toolchain: MSYS2 g++ 12.1.0 (libstdc++ 12), flags `-std=c++20 -Wall -Wextra -pedantic -pthread`, scratch folder outside the repo.

## the three `in code` snippets: compiled and run

All three snippets in one file with a `main` that exercises them. Compiled clean (no warnings) and ran:

- Message passing: producer and consumer threads with release/acquire on `ready`; the `assert(frame.seq == 42)` held (assertions enabled).
- Relaxed counter and CAS loop: four threads each called `on_drop()` and `record_power()` 10,000 times; printed `dropped 40000 peak 39999`.
- C++20 `wait`/`notify_all` on `std::atomic<std::uint32_t>`: consumer blocked in `await_next`, producer called `publish_next`; printed `seen 1`. `sizeof(WorkerStats)` and the stride of `stats[8]` are both 64.
- `std::atomic<float>` and `std::atomic<std::uint64_t>` are `is_always_lock_free` on this x86-64 target; an `std::atomic` of a 64-byte struct is not (supports "a large `T` may be implemented with a hidden lock").

A single run of a threaded program is evidence the code works, not proof of the ordering guarantees. Those come from the standard ([intro.races], [atomics.order]); the lesson states them as such.

## `std::hardware_destructive_interference_size`: compiled and run

- `__cpp_lib_hardware_interference_size` is defined (`201703`) and the value is `64` with GCC 12 on x86-64.
- Used in `alignas` inside a header: GCC 12 warns "use of 'std::hardware_destructive_interference_size' [-Winterference-size]". The same use in the main `.cpp` file does not warn. This matches the lesson's statement.

## not compile-checked

- The optional challenge (store buffering) is a reasoning question; the `r1 == 0 && r2 == 0` outcome under release/acquire was not reproduced on hardware here.

## edit made while reviewing the interrupted draft

- Added that `compare_exchange` compares object representations byte for byte (like `memcmp`), not with `operator==`, since the lesson's own CAS example uses `float`.
