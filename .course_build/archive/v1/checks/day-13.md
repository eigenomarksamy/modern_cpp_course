# compile checks: day 13

Toolchain: MSYS2 g++ 12.1.0, scratch folder outside the repo. Flags: `-std=c++17 -Wall -Wextra -pedantic`.

- NVI `RangeSensor` (stub `SensorFault`, a `Sonar` override): compiles clean; an in-range reading is returned, an out-of-range reading throws `SensorFault` from the base's non-virtual `read_m`.
- `Filter` / `LowPass` / `LowPass2` / `LowPass3`: `LowPass` compiles with no warning under `-Wall -Wextra`; instantiating it fails ("cannot declare variable ... of abstract type 'LowPass'"). `LowPass2` fails with "marked 'override', but does not override". Adding `-Woverloaded-virtual` warns "'virtual double Filter::apply(double) const' was hidden", confirming it is not in GCC 12's `-Wall`. `LowPass3` compiles and runs.
- `Plugin` / `Logger` virtual destructor snippet (wrapped in `demo()` in the lesson): compiles with no warning under `-Wall -Wextra` (the `unique_ptr` deletion is inside a system header). A direct `Plugin* raw = new Logger; delete raw;` triggers `-Wdelete-non-virtual-dtor` under `-Wall`. `-Wnon-virtual-dtor` flags the class definitions. Not run: the `unique_ptr` deletion is UB.
- slicing predict-the-output: prints `lidar sensor sensor`, matching the lesson.
- composition `Robot` / `Drive` (stub `Twist`, `Localizer`, a `DiffDrive`): compiles clean; `static_assert` confirms `Robot` is not copy constructible and is nothrow move constructible; `step` dispatches to the drive.
- optional challenge (`Base::tick` / `Derived::tick` non-virtual): prints `Derived::tick` then `Base::tick`; adding `override` fails with "marked 'override', but does not override".

Not checked: the vtable diagram is a typical Itanium-ABI layout, described from the ABI rather than inspected in this toolchain's output; the lesson labels it implementation-specific. No performance measurement of virtual calls was made; the lesson makes no numeric claim.
