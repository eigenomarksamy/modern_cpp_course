# day 43 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic`, scratch folder outside the repo.

- SRP before (`process_track_file`, with a stand-in `RawFrame` struct) and after (`Detection`, `SnrGate`, `gate`): compiled together in one file, no warnings. A test `main` gated three detections at 12 dB and printed `2` as expected (the lesson states no output).
- ISP/DIP before (`Robot` fat interface, `plan` declaration) and after (`Cell`, `OccupancyQuery`, `GridMap`, `plan`): compiled with a toy `plan` definition and `main`, no warnings, ran.
- Physical coupling: `tracker.h` exactly as shown, a client `user.cpp` that includes only `tracker.h` (constructs and deletes a `Tracker` with `KalmanFilter` and `Detection` incomplete), and `tracker.cpp` that defines the types. Compiled and linked as two translation units, no warnings, ran.
- Not checked: the commented-out declarations `parse_frame` and `write_csv` (prose only).
