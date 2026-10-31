# compile checks: day 55

Toolchain: MSYS2 g++ 12.1.0 (Windows), scratch folder outside the repo.

- **the complete program**: the four cpp blocks were spliced into the lesson by script from the exact files that were compiled, then re-extracted from the lesson file and concatenated in order (161 lines). Built with `g++ -std=c++20 -Wall -Wextra -pedantic -O2 -pthread`: no warnings. Also built at `-O0`, `-O1`, `-O3`: no warnings, identical output.
- **output**: the `text` block in the lesson is the exact program output. Ran 50 times: identical output every run (single consumer, FIFO queue).
- **GCC 12 false positive avoided**: an earlier `pop()` written as `T item = std::move(q_.front()); ... return item;` triggered `-Wmaybe-uninitialized` at `-O1`/`-O2`/`-O3` (variant moved into optional inside libstdc++). The published version builds the `std::optional<T>` with `emplace` and returns it, which compiles cleanly at all levels.
- **challenge claim**: moving `queue_` below the `jthread` members (initializer list unchanged) produced the expected `-Wreorder` warning under `-Wall`.
- **assert**: the `gate` unit test in `main` uses `assert`; it is compiled out under `NDEBUG`, which the lesson does not rely on for the printed output.
- **not checked**: no ThreadSanitizer run (not available with this MinGW GCC); thread-safety argued from the design (single consumer touches the sink; `main` reads it only after both threads are joined). `std::format` deliberately not used (no `<format>` in GCC 12).
