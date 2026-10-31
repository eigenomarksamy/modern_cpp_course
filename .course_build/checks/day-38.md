# day 38 compile checks

Toolchain: MSYS2 g++ 12.1.0 (winpthreads), flags `-Wall -Wextra -pedantic -pthread`; code blocks extracted verbatim from the lesson into a scratch folder outside the repo.

- lost-wakeup snippet (`producer_buggy`, `producer`, `consumer`): `-std=c++17`, compiles cleanly; ran the fixed `producer` with `consumer` on two threads, consumer woke. The buggy producer was compiled but not used to "demonstrate" a hang (timing-dependent; the argument is by reasoning).
- `BoundedQueue<T>`: `-std=c++17`, compiles cleanly. Stress test at `-O2`: capacity 4, 3 producers x 10,000 items, 3 consumers, then `close()`; 20 iterations per run, 2 runs: every item delivered exactly once (count and sum checked), `push` after `close` returned `false`. Drain-on-close checked: 2 items pushed, closed, `pop` returned both then `nullopt` (matches the challenge answer).
- `LatestSlot<T>`: confirmed it does not compile as C++17 (`std::stop_token` not declared), compiles cleanly as `-std=c++20`. Ran inside a `std::jthread` with a slow consumer: consumer saw only some values (2 of 1000, last = 1000) and exited when `~jthread` requested stop, confirming the stop-token wait wakes the waiter.
- Not checked: spurious wakeups cannot be provoked deliberately; the single-cv `notify_one` stall in "watch out for" is described by reasoning, not reproduced. ThreadSanitizer is not available on this toolchain.
