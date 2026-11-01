# compile checks: day 11

Toolchain: MSYS2 g++ 12.1.0, scratch folder outside the repo. Flags: `-std=c++17 -Wall -Wextra -pedantic`.

- rule-of-zero `Buffer`: compiles clean; `static_assert`s for nothrow move construction and copy construction hold. Copy, move, and moved-from size (0 on libstdc++) observed.
- `Buffer5` copy-and-swap: compiles clean; `static_assert(std::is_nothrow_move_assignable_v<Buffer5>)` holds; copy assign, self assign, and move assign exercised.
- `UniqueFd` and `LidarDriver` (stub `Point` and `PacketParser`, `<unistd.h>` from mingw): compiles clean; `static_assert`s confirm `LidarDriver` is not copy constructible and is nothrow move constructible and assignable; moved into a vector at run time with a `dup`ed descriptor.
- `Snapshot` watch-out: with the destructor it prints `100000` (copy); with the destructor removed (`-DNODTOR`) it prints `0` on libstdc++. No warning under `-Wall -Wextra -pedantic`; adding `-Wdeprecated-copy-dtor` produces "implicitly-declared 'Snapshot::Snapshot(const Snapshot&)' is deprecated". Matches the lesson. (The program also prints the destructor's message twice, which the lesson does not claim either way.)
- optional challenge `Config`: `static_assert`s confirm no default constructor, deleted copy operations, nothrow moves. Lines (1), (3), (4) compile; (2) fails with "use of deleted function 'Config::Config(const Config&)'"; (5) fails with "no matching function for call to 'Config::Config()'".

Not checked: the special-member table was written from the standard's rules ([class.default.ctor], [class.copy.ctor], [class.copy.assign], [class.dtor]) rather than exhaustively tested; the rows exercised above agree with it. `clang-tidy cppcoreguidelines-special-member-functions` not run (not installed).
