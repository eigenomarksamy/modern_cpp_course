# day 44 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++20 -Wall -Wextra -pedantic`, scratch folder outside the repo. Code blocks were extracted from the lesson file by script and included verbatim.

- "the idea" hard-wired `JointController`: compiled and ran with a stub `CanBusMotor`, no warnings.
- Constructor-injection `Clock`, `Actuator`, `JointController` plus the fake-based test `main`: compiled, no warnings; asserts passed and the program printed `-20`, matching the `// prints: -20` comment.
- `SteadyTimeSource` concept, `RateLimiter`, `SystemSteadyClock`, `ManualClock`: compiled; the commented usage was run as real code (CTAD from `ManualClock{&now}`, 100 ms gap) and gave true, false, true as the comments state. `static_assert(!SteadyTimeSource<int>)` passed. Also instantiated with `SystemSteadyClock`.
- `Watchdog` with `std::function` seam: compiled and ran with an injected lambda clock (expired after 30 ms with a 20 ms limit, not expired after `kick`), and with the default argument.
- Dangling `make_controller` example: compiles (with a stand-in `SystemClock : Clock`), as the lesson says; g++ 12 gave no warning. Not run, since it is UB by design.
- Not checked: the link-time seam (described in prose only, no code).
