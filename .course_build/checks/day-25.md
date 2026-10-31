# day 25 compile checks

Toolchain: MSYS2 g++ 12.1.0. Flags: `-std=c++17 -Wall -Wextra -pedantic` unless noted. Scratch: `$TEMP/claude/cpp-week-4/`.

- `overloaded` helper plus the radar `RadarMsg` example: compiled clean, ran, printed `trk 7` then `hb 42` as commented.
- Same example with the `Heartbeat` lambda removed: failed to compile (`no type named 'type' in std::invoke_result<..., const Heartbeat&>`), confirming the exhaustiveness claim.
- Same example without the deduction guide: compiles and runs with `-std=c++20`; fails with `-std=c++17` (`class template argument deduction failed`), confirming the C++17/C++20 note.
- `ParseResult` variant-as-result: compiled with a stub `parse_detection`; printed the error path and the success path correctly.
- `std::any` snippet (inside `main`): `any_cast<int>(&a)` gave 42, `any_cast<long>(&a)` gave `nullptr`, `any_cast<double>(a)` threw `std::bad_any_cast`.
- `ArmState` state machine: compiled and ran with a driver; Moving stays Moving before timeout (index 1), becomes Fault "move timeout" after 5 s (index 2), and becomes Idle at target (index 0). Removing the `-> ArmState` return types failed with "inconsistent types deduced for lambda return type", as the lesson says.
- P0608 watch-out: `std::variant<std::string, bool> v = "abc";` gives `index() == 0` (string) with both `-std=c++17` and `-std=c++20` on GCC 12's libstdc++. The "original C++17 wording picked bool" claim is from standards history (P0608), not reproducible on this toolchain.
- `valueless_by_exception` behavior is described from the standard; not exercised.
