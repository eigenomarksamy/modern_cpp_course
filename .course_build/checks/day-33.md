# day 33 compile checks

Toolchain: MSYS2 g++ 12.1.0 (libstdc++ 12), flags `-std=c++20 -Wall -Wextra -pedantic`, scratch folder outside the repo.

- CRC-32 table + `crc32` + `static_assert(crc32("123456789") == 0xCBF43926u)`: compiles clean (the assert passes), also ran at runtime.
- `count_primes` with a transient `std::vector<bool>`: `static_assert(count_primes(100) == 25)` passes. `constexpr std::vector<int> v{1, 2, 3};` fails with "... is not a constant expression because it refers to a result of 'operator new'" (verbatim tail).
- `constexpr` `std::string` concatenation and a `try`/`catch` in a `constexpr` function compile; evaluating the `throw` in a `static_assert` fails with "expression '<throw-expression>' is not a constant expression".
- `consteval` `deg_to_rad` / `can_channel`, `constinit retry_budget`: compiled and ran (`joint_limit` printed 2.967060). `can_channel(16)` fails with "expression '<throw-expression>' is not a constant expression"; `deg_to_rad(d)` with a runtime `d` fails with "the value of 'd' is not usable in a constant expression"; `constinit int bad = compute_default();` fails with "'constinit' variable 'bad_budget' does not have a constant initializer" (the lesson renames the variable to `bad`).
- `if constexpr (std::is_constant_evaluated())`: GCC 12 warns "'std::is_constant_evaluated' always evaluates to true in 'if constexpr' [-Wtautological-compare]" (verbatim).
- `fixed_string` class-type NTTP with `Counter<"dropped_frames">`: compiled and ran (described in prose only).
- `constexpr double s = std::sin(0.5);` is accepted by GCC 12 with `-pedantic`, no diagnostic (GCC extension). Not tested on other compilers.
- build-time data point: `static_assert(count_primes(100000) == 9592)` fails at default limits ("'constexpr' evaluation operation count exceeds limit of 33554432"); with `-fconstexpr-ops-limit=1000000000 -fconstexpr-loop-limit=10000000` the build took about 7.4 s versus 0.35 s without the assert; runtime execution 0.36 s wall including process start. Single run, one machine; the lesson presents it as a single data point.
- challenge: `int g = sq(4)` / `constinit` / local `l` compile and print 16; `-O0 -S` showed no call to `sq` (GCC folds it), so the answer says so.

Not compiled: a `constexpr` virtual-call example. GCC 12 rejected a polymorphic `Gain` with a `virtual constexpr` destructor ("'virtual constexpr Gain::~Gain()' used before its definition"), which appears to be a GCC 12 bug, so virtual calls are mentioned in prose only. Library support versions for constexpr vector/string on libc++ and MSVC are stated from documentation, not tested.
