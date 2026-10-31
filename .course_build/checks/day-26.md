# day 26 compile checks

Toolchain: MSYS2 g++ 12.1.0 (libstdc++ 12). Flags: `-std=c++17 -Wall -Wextra -pedantic`. Scratch: `$TEMP/claude/cpp-week-4/`.

- Before/after parameter snippet (`is_tf_topic`, `has_prefix`, `rates` with `std::less<>`, `rate_of`): compiled clean and ran; `rate_of` accepted a view sliced from a larger string. Changing the comparator to `std::less<std::string>` made `rates.find(topic)` fail to compile, as stated.
- `open_log` / `open_log_fixed`: compiled clean (with `fclose` added in place of `// ...`); the fixed version ran on a substring slice. The buggy version's runtime misbehavior was not demonstrated (it is UB-adjacent and data-dependent).
- NMEA parser (`next_field`, `to_double`, `gga_altitude_m`): compiled clean and ran; altitude parsed as `545.4`; `to_double` rejected `"12.5abc"`, `""`, and `"+1"`; a truncated sentence gave an empty optional. Floating-point `from_chars` works on this libstdc++ (GCC 12).
- Dangling watch-out snippet: compiled with `-Wall -Wextra -pedantic` at both `-O0` and `-O2` with no warnings, supporting "none of these produce a warning from GCC 12". Clang `-Wdangling` behavior is stated from general knowledge and hedged ("some of these patterns"); not checked locally (no Clang). ASan unavailable on this mingw build.
- Optional challenge: confirmed the deleted `split(std::string&&)` overload rejects `split(read_line())` at compile time.
