---
title: review: how programs and objects come to be
kind: review
standard: C++17
objective: consolidate the build model, linkage, initialization, integer arithmetic, object layout, and storage duration
prerequisites: build-pipeline, linkage-odr, initialization, integer-types, object-layout, storage-duration
difficulty: 1
---

### recap

| lesson | key idea |
|---|---|
| [[build-pipeline]] | the compiler sees one translation unit and checks it against the declarations it can see; the linker only matches names. |
| [[linkage-odr]] | external linkage means one entity program-wide. classes, inline functions, and templates may be defined in many translation units only if every definition is identical, and nobody has to check. C++17 `inline` variables give one object defined in a header. |
| [[initialization]] | braces reject narrowing but prefer `std::initializer_list` constructors; automatic scalars start indeterminate, statics start zeroed. |
| [[integer-types]] | arithmetic happens in at least `int`, signed meets unsigned as unsigned, and only unsigned wraparound is defined. |
| [[object-layout]] | size and alignment belong to the type; padding keeps members aligned and its bytes have no defined value. |
| [[storage-duration]] | scope belongs to names, lifetime to objects; cross-file static initialization order is unspecified, and a function-local static fixes it. |

### review questions

1. a header included by `planner.cpp` and `controller.cpp` contains `int g_cycle_count;`, `const double kDt = 0.01;`, and `inline double clamp01(double x) { ... }`. which of these links, which does not, and what single C++17 change gives one shared, mutable `g_cycle_count` without touching any `.cpp` file?
2. predict the sizes: `std::vector<int> a{10, 0};`, `std::vector<int> b(10, 0);`, `std::vector<int> c{};`. why does the guideline "use braces everywhere" need an exception for containers?
3. `for (int i = 0; i < v.size() - 1; ++i)` draws a `-Wsign-compare` warning and misbehaves when `v` is empty. explain both, using the conversion rules.
4. two objects of the same struct have equal members, yet `std::memcmp` says they differ. how is that possible, and what should the code compare instead?
5. looking ahead: a `LogFile` class opens a `FILE*` in its constructor. where should `fclose` go so that every way out of a scope, including an exception, closes the file? what goes wrong if a `LogFile` is copied with the compiler-generated copy constructor?

### mini exercise

this header is included by several `.cpp` files of one program. find four problems (two stop the build, two are silent), then fix them.

```cpp complete
// telemetry.h
#pragma once
#include <cstdint>
#include <vector>

struct Sample { bool valid; double value; std::uint8_t channel; };   // stored by the million
int g_samples_dropped;
std::vector<int> g_channel_map{16, -1};                              // intended: 16 entries of -1
inline std::uint32_t scale(std::uint16_t raw, std::uint16_t gain) { return raw * gain; }
```

### answers

<details>
<summary>answer 1: linkage and the ODR</summary>

`int g_cycle_count;` fails: it is a definition with external linkage in two translation units (`multiple definition of 'g_cycle_count'`). `const double kDt` links, because a namespace-scope `const` without `inline` or `extern` has internal linkage: each file gets its own copy, harmless for a value. `inline double clamp01` links, because inline functions may be defined in every translation unit as long as the definitions are identical. `inline int g_cycle_count = 0;` makes it a C++17 inline variable: one object for the whole program, defined in the header.

</details>

<details>
<summary>answer 2: braces and containers</summary>

`a` has 2 elements (10 and 0), `b` has 10 zeros, `c` is empty. a non-empty braced list strongly prefers an `std::initializer_list` constructor; empty braces mean value-initialization. braces are a good default because they reject narrowing and avoid the most vexing parse, but for any class with an `initializer_list` constructor (all standard containers, `std::string`) braces mean "these are the elements", so use parentheses for sizing and fill constructors.

</details>

<details>
<summary>answer 3: signed meets unsigned</summary>

`v.size()` is `std::size_t`, so in `i < v.size() - 1` the `int` is converted to unsigned for the comparison; a negative `i` would compare as a huge value, which is what the warning is about. the real bug is `v.size() - 1`: for an empty vector it wraps to the largest `std::size_t` (well defined, and wrong), so the loop runs far past the end. write `i + 1 < v.size()` with an unsigned `i`, or use `std::ssize(v)` (C++20) and signed arithmetic throughout.

</details>

<details>
<summary>answer 4: padding</summary>

`memcmp` compares the whole object representation, padding included, and padding bytes have unspecified contents: two objects with identical members can carry different leftovers between them. compare member by member (write `operator==`, or default it in C++20). the same reasoning rules out hashing or serializing an object's raw bytes.

</details>

<details>
<summary>answer 5: looking ahead</summary>

`fclose` belongs in the destructor. automatic objects are destroyed when their scope exits by any route: normal flow, `return`, `break`, or stack unwinding from an exception. tying the release to the object's lifetime is RAII ([[raii]]). the generated copy constructor copies the `FILE*`, so two objects hold one handle and both destructors close it: a double close, which is undefined behavior. the class must forbid copying or define what a copy means ([[copy-semantics]]), and it can support *moving* ownership instead ([[move-semantics]]).

</details>

<details>
<summary>mini exercise answer</summary>

- **link error:** `int g_samples_dropped;` is a definition with external linkage in every including file. write `inline int g_samples_dropped = 0;`.
- **link error:** `g_channel_map` is also a non-`inline`, non-`const` variable defined in a header. make it `inline`.
- **silent:** `{16, -1}` builds a two-element vector. with `inline` added, write `inline std::vector<int> g_channel_map(16, -1);`.
- **silent:** `raw * gain` promotes both operands to `int`, and 65535 * 65535 overflows `int`: undefined behavior, despite the unsigned types. write `return std::uint32_t{raw} * gain;`.

a fifth, optional improvement: `Sample` is 24 bytes on a typical 64-bit platform because of padding; ordering the members `double value; bool valid; std::uint8_t channel;` makes it 16, which matters for something stored by the million.

</details>

### connections

this module was about what exists before any of your logic runs: which definitions make up the program, how objects get their first values, how big they are, and how long they live. the next module stays at that level and asks what you can safely *refer to*: temporaries, references, `const`, value categories, and the behavior the standard leaves undefined. after that, [[raii]] turns the destruction order from [[storage-duration]] into the central resource-management technique of the language.
