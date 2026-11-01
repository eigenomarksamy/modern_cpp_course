# day 46 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++20 -Wall -Wextra -pedantic`, scratch folder outside the repo. Code blocks were extracted from the lesson by script and compiled verbatim.

- CRTP `SensorBase`/`Thermistor` and the `ScaledSensor` concept with `read_si`: compiled, no warnings; printed `102.4 102.4`, matching the comment. `static_assert(!ScaledSensor<int>)` passed.
- Type-erased `Record` (concept/model pair, clone, hidden friend `to_text`) plus the usage block (`imu::Sample`, `vendor::GpsFix`, vector of `Record`, deep copy via `push_back`): compiled together, no warnings; printed `imu #41`, `gps sats=9`, `imu #41`, matching the comments. This also confirms the by-value template constructor does not hijack the copy (no nesting).
- Challenge claim about a forwarding-reference constructor: a modified copy with `T&&` and a `remove_cvref_t` constraint was compiled; copying a non-const lvalue `Record` selected the template and instantiated `Model<Record>`, and GCC 12 reported "satisfaction of atomic constraint ... depends on itself". The lesson's answer states this.
- Not checked: the plugin `dlopen`/`extern "C"` scenario and the comparison table (prose only). No claim about the cost of indirect calls was measured; the lesson says to measure.
