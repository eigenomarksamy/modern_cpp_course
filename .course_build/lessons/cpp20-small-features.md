---
title: small C++20 features that remove bug patterns
standard: C++20
objective: adopt the small C++20 library and language additions that replace error-prone idioms in everyday code
prerequisites: format, algorithms, ub-usual-suspects
difficulty: 1
---

### the idea

`m.find(k) != m.end()` to ask a yes-or-no question, an erase-remove pair that is easy to get half right, `(lo + hi) / 2` that overflows, `s.substr(0, 7) == "/radar/"`, positional struct initialization that silently shifts when someone inserts a field. none of these is hard, and each has a long history of small bugs. C++20 added a set of small features whose main value is not saving keystrokes but removing one bug pattern each.

### understanding the concept

| feature | replaces | bug pattern removed |
|---|---|---|
| designated initializers `{.kp = 2.5}` | positional aggregate initialization | arguments shifting when a field is inserted |
| `contains(key)` | `find(key) != end()`, `count(key) != 0` | noise, and accidental `operator[]` inserts |
| `std::erase`, `std::erase_if` | the erase-remove idiom | the single-iterator `erase` bug from [[algorithms]] |
| `starts_with`, `ends_with` | `substr` or `compare` with offsets | off-by-one and length mistakes |
| `std::source_location` | `__FILE__` and `__LINE__` macros | macros, and losing the *caller's* location |
| `std::bit_cast`, `std::popcount`, `std::endian` | pointer punning, compiler builtins | undefined behavior and non-portable code |
| `using enum` | repeated qualification in `switch` | noise in exhaustive switches |
| `std::midpoint`, `std::ssize` | `(a + b) / 2`, `size() - 1` loops | signed overflow and unsigned wraparound |

### in code

excerpts from one file that was compiled and run with GCC 12, `-std=c++20`:

```cpp
#include <bit>
#include <climits>
#include <cstdint>
#include <map>
#include <numeric>
#include <source_location>
#include <string_view>
#include <vector>

struct PidConfig { double kp = 1.0; double ki = 0.0; double kd = 0.0; int rate_hz = 100; };
PidConfig cfg{.kp = 2.5, .kd = 0.1};   // designated initializers: ki and rate_hz keep defaults
// PidConfig bad{.kd = 0.1, .kp = 2.5};  error: designator order ... does not match declaration order

bool known = tracks.contains(42);                            // map, set, unordered_*: no find() != end()
bool radar = topic.starts_with("/radar/");                   // string and string_view; also ends_with
auto removed = std::erase_if(ids, [](int id) { return id < 0; });   // replaces erase-remove

void trace(std::string_view msg, std::source_location loc = std::source_location::current());
// default argument is evaluated at the call site: prints the caller's file, line, function

std::popcount(0b1011u);                  // 3; unsigned types only: popcount(11) does not compile
std::bit_cast<std::uint32_t>(1.0f);      // 0x3F800000 with IEEE 754 float; no UB, unlike type punning
std::endian::native == std::endian::little;

enum class Mode { idle, tracking, fault };
switch (m) { using enum Mode; case idle: /* ... */ case tracking: /* ... */ case fault: /* ... */ }

std::midpoint(INT_MAX - 2, INT_MAX);     // 2147483646; (a + b) / 2 would overflow: UB
for (auto i = std::ssize(ids) - 1; i >= 0; --i) { /* signed index, no wraparound */ }
```

designated initializers must follow declaration order, cannot nest (`.pose.x`), and cannot be mixed with positional ones; they make configuration structs self-documenting at the call site. `std::bit_cast` (introduced on [[ub-usual-suspects]] as the fix for type punning) is `constexpr` and requires equal sizes and trivially copyable types; the bit pattern itself depends on the implementation's floating-point representation.

### in practice

designated initializers change how configuration code reads and how it fails. a radar configuration built positionally, `RadarConfig cfg{250.0, 512, 8, true};`, cannot be reviewed without opening the header, and inserting a field before `num_bins` silently shifts every later value into the wrong member when the types are compatible. the designated version, `RadarConfig cfg{.max_range_m = 250.0, .num_bins = 512, .chirps = 8, .enable_cfar = true};`, documents itself at the call site, lets omitted fields keep their default member initializers, and turns a reordered or renamed field into a compile error instead of a misconfigured sensor. the order rule (designators must follow declaration order) is a small price, and it is checked by the compiler.

### watch out for

**`[[likely]]` and `[[unlikely]]` are hints, not optimizations.** written as `if (frame.empty()) [[unlikely]] { return; }`, they influence block layout and branch weighting; they do not make code faster by themselves, and a wrong hint can make it slower. use them only where a profile ([[profiling]]) shows a hot branch with a stable, known bias, such as an error path. profile-guided optimization derives the same information from measured frequencies, and unlike a hand annotation it does not go stale when the code around it changes.

### the takeaway

each of these small features removes a specific bug pattern: adopt them where they replace the error-prone idiom, and treat performance hints like `[[likely]]` as measurements to justify, not decorations.

### optional challenge

what do these produce, and which one does not compile?

```cpp
std::vector<int> v;
auto a = std::midpoint(0u, 10u);              // (1)
auto b = std::ssize(v) - 1;                   // (2)
auto c = std::popcount(-1);                   // (3)
auto d = std::bit_cast<float>(0x3F800000u);   // (4)
```

<details>
<summary>answer</summary>

(1) is `5u`. (2) is `-1` of a signed type (`std::ptrdiff_t`), so a loop down to zero behaves, unlike `v.size() - 1`, which wraps to a huge unsigned value. (3) does not compile: `std::popcount` accepts only unsigned integer types, deliberately, because the bit count of a negative number depends on its width; write `std::popcount(static_cast<unsigned>(x))` to say which width you mean. (4) is `1.0f` on any platform whose `float` is IEEE 754 single precision, with no undefined behavior.

</details>
