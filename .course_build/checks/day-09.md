# compile checks: day 09

Toolchain: MSYS2 g++ 12.1.0, scratch folder outside the repo. Flags: `-std=c++17 -Wall -Wextra -pedantic`.

- buggy `SampleWindow` (reorder): compiles with the two warnings the lesson names: `-Wreorder` ("'size_' will be initialized after") and `-Wuninitialized` ("member 'SampleWindow::size_' is used uninitialized"). Ran once without crashing; the outcome of the UB is not something the lesson asserts.
- fixed `SampleWindow` with delegating constructor and default member initializer: compiles clean; default and sized construction gave sizes 256 and 16.
- `Sensor`/`Lidar` lifecycle tracer: compiles clean; output matches the `text` block in the lesson exactly.
- `Pipeline` / `Pipeline2` (with stub `Device`, `open_device` that throws, `close_device`, and a `DevicePtr` alias with a printing deleter): both compile clean; both report the exception; on success `Pipeline2` closes the device in its implicit destructor. The leak in `Pipeline` was not observed with a tool (no sanitizers on this mingw build); it follows from the language rule.
- `RangeGate`: compiles clean; valid gate works; NaN for either bound throws `std::invalid_argument`, confirming the "also rejects NaN" comment.
- `Timeout` implicit conversion: `arm_watchdog(5)` compiles. With an `explicit` constructor, both `f(5)` and `T t = {5};` fail to compile (errors "could not convert '5'" and "would use explicit constructor").
- optional challenge `Probe`: prints `Probe(0)`, `~Probe()`, then the handler's message, matching the answer.

Not checked: the static `optional` factory variant of `RangeGate` (described in prose only), `std::make_unique_for_overwrite` (C++20, mentioned only).
