# day 47 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++20 -Wall -Wextra -pedantic`, scratch folder outside the repo. Code blocks were extracted from the lesson by script.

- "the idea" `move_joint(int, double, double, double)`: the declaration plus the call (wrapped in a function, since the lesson shows the call bare) compiled with no warnings, which is the lesson's point.
- Strong types (`Quantity`, `Radians`, `RadiansPerSecond`, `JointId`, `MoveError`, `MoveRequest`, `move_joint`): compiled with a stub definition and ran the first commented call (timeout converted to 30000 ms). Defaulted `<=>`/`==` and `operator+` exercised. Each commented "does not compile" line was compiled separately and rejected (swapped quantities, plain `int` for `JointId`), and `JointId j = 2;` was rejected. Ignoring the result produced the `nodiscard` warning.
- Pimpl: `lidar_driver.h` and `lidar_driver.cpp` taken verbatim as two files, plus a client `.cpp` that includes only the header: compiled and linked, no warnings; `read_scan` into an 8-float buffer returned 8 with value 5, `healthy()` true, move construction worked, `sizeof(LidarDriver)` was 8 (one pointer) on this 64-bit target.
- Implicit destructor failure: a copy of the header without the declared destructor and moves, used from a client, failed with "invalid application of 'sizeof' to incomplete type 'LidarDriver::Impl'" (libstdc++'s check in `default_delete`), as the lesson says.
- `[[deprecated]]` overload: compiled with a stub for the span overload; calling the old overload gave `-Wdeprecated-declarations` with the message, and it forwarded correctly (returned 4).
- Not checked: ABI claims (dual ABI, layout stability) are prose from documentation, not experiments.
