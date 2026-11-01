# day 41 compile checks

Toolchain: MSYS2 g++ 12.1.0 (libstdc++ 12, MinGW-w64, winpthreads), flags `-std=c++20 -Wall -Wextra -pedantic -pthread`, scratch folder outside the repo.

## all four `in code` snippets: compiled clean

One file containing `TrackStore`, `merge_buggy`, `merge`, `DetectionBus`, the latch/barrier/semaphore block (with stub definitions for `init_driver`, `run_driver`, `send`, etc.), and `ThreadPool` built on the `BoundedQueue<T>` extracted verbatim from `lessons/day-38.md`. No warnings. The `Release` guard (a local aggregate with a reference member and a destructor) and CTAD for `std::barrier` with a `noexcept` lambda both compile.

## run results

- `merge`: two threads, 20,000 calls each of `merge(a, b)` and `merge(b, a)`: completed, `2 tracks total`; `merge(a, a)` returns early.
- `merge_buggy` (with a 50 ms sleep injected between the two locks to widen the window): after 2 s, `try_lock` on both mutexes failed (`a held, b held`), i.e. the two threads deadlocked as the lesson says.
- `DetectionBus`: a handler that calls `subscribe()` from inside `publish()` works (`calls 2`), because handlers run outside the lock.
- `start_drivers` (latch + `jthread` + `stop_token`): `all 3 drivers initialized`; in isolation, 200 iterations x 3 runs, no hang.
- `upload` with `counting_semaphore<4>`: 16 threads, a 2 ms `send`, one throwing upload: max concurrent uploads observed `4`, `1` failure, and all `4` permits available afterwards (the RAII guard released on the exception path).
- `ThreadPool(3)`: 100 submitted tasks all ran before the destructor returned (`pool ran 100 tasks`), confirming drain-on-close plus join order.

## `std::barrier`: compiles, but cannot be run reliably on this toolchain

The barrier example (4 threads, `arrive_and_wait` per step, `noexcept` completion function) hung in about a third of full-program runs, and an isolated 4-thread, 5-phase barrier program hung in 3 of 3 runs. A 2-thread barrier without a completion function completed 50 phases. The code is a textbook use of `std::barrier` (one `arrive_and_wait` per participant per phase). The hang is consistent with known libstdc++ bugs in the atomic-wait fallback used on targets without futex support, Windows among them (GCC PR 101037, fixed on later branches). That diagnosis was not proven, and the example was not run on another toolchain. The lesson text is unchanged.

## not run

- ThreadSanitizer: not available for MinGW; the lesson already says to use it on Linux or macOS.
- The thread-starvation deadlock in `watch out for` is prose only.
