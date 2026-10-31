# day 45 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic`, scratch folder outside the repo. Code blocks were extracted from the lesson by script and compiled verbatim, with stubs added only where noted.

- Strategy three ways (`Ema`, `Smoother`, `EmaSmoother`, `TrackerV`, `TrackerF`, `TrackerT`): compiled; the three commented construction lines were run as real code and all three trackers produced identical output (100, then 103 for inputs 100, 110 at alpha 0.3). No warnings.
- Factory registry (`SensorConfig`, `Sensor`, `SensorRegistry`, `register_builtin_sensors`) with stub `Imu` and `Lidar` classes: compiled and ran; creating `"lidar"` worked, `"radar"` threw `std::invalid_argument` with message `unknown sensor type: radar`.
- Self-registration snippet: compiled in the same file with a function-local-static `global_registry()` and a `make_lidar` function, no warnings, and registration ran (single executable, no static library). The static-library dead-stripping failure described in the prose was not reproduced here.
- Observer `Signal` / `Subscription`: compiled, no warnings. The commented usage was run as real code: printed `lost 7`, then nothing for `emit(8)`, matching the comments. Extra tests: a one-shot listener resetting its own token during `emit` (fired once, safe), a token reset after its signal was deleted (no crash), move construction and move assignment of tokens.
- Not checked: the cross-thread race described in "watch out for" (prose only). Sanitizers are not available in this MinGW toolchain (`-lasan` missing), so the observer tests ran without ASan/UBSan.
