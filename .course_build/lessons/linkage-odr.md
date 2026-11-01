---
title: linkage and the one definition rule
standard: C++17
objective: predict whether a name in two translation units is one entity or two, and keep header definitions ODR-safe
prerequisites: build-pipeline
difficulty: 2
---

### the idea

two files in the same robot driver each contain `inline int gain() { ... }`. one returns 2, the other returns 3. the build is clean, no warnings, and the program prints a different answer depending on whether you built with `-O0` or `-O2`. nothing about this is a compiler bug. it follows directly from how C++ turns source files into a program, and from a rule that the toolchain is allowed to leave completely unchecked.

### understanding the concept

**linkage** decides whether the same name in different translation units refers to the same entity:

| linkage | meaning | how you get it |
|---|---|---|
| external | one entity shared across translation units | non-`static` functions and variables at namespace scope |
| internal | private to this translation unit | `static` at namespace scope, anything in an anonymous namespace, non-`inline` `const` variables at namespace scope |
| none | local to a scope | local variables |

**the one definition rule (ODR)** has two halves. non-inline functions and variables with external linkage must be defined exactly once in the whole program; break this and you usually get a link error. classes, inline functions, inline variables, and templates may be defined in several translation units (that is how headers work), but every definition must be identical: the same token sequence with the same meaning. break *that* half and the program is ill-formed, no diagnostic required. the compiler cannot see it (one translation unit at a time) and the linker typically keeps one copy of each inline function and throws the rest away without comparing them.

**templates live in headers** for the same reason. the compiler generates `std::vector<Detection>` code in the translation unit that uses it, so it must see the template's definition there. the alternative is explicit instantiation (`template class Filter<float>;` in one `.cpp`), which works when the set of types is closed.

### in code

**a silent ODR violation.** two translation units, two different bodies for the same inline function:

```cpp external
// g1.cpp
#include <cstdio>
inline int gain() { return 2; }
void report_a() { std::printf("a: %d\n", gain()); }

// g2.cpp
#include <cstdio>
inline int gain() { return 3; }   // BUG: ODR violation, no diagnostic required
void report_b() { std::printf("b: %d\n", gain()); }

// main.cpp
void report_a();
void report_b();
int main() { report_a(); report_b(); }
```

with GCC 12 on our test machine, `g++ g1.cpp g2.cpp main.cpp` at `-O0` printed `a: 2` and `b: 2`; swapping the file order printed `3` and `3`. at `-O2` both orders printed `a: 2` and `b: 3`, because each call was inlined before the linker ever chose a copy. none of these outputs is "the right one": the program is ill-formed and the standard does not say what it does. in real code this happens when two files define a helper with a common name, or when a header's content depends on a macro (`#ifdef DEBUG_POSE`) that is set differently in different targets.

**one object, defined in a header (C++17).** before C++17, a global shared by several translation units needed an `extern` declaration in the header and a definition in exactly one `.cpp`. inline variables remove that ceremony:

```cpp complete
// config.h
#pragma once
#include <string_view>

const int kLimit = 10;                       // internal linkage: a separate copy per TU
inline constexpr double kMaxRangeM = 250.0;  // C++17: one entity program-wide
inline constexpr std::string_view kFrameId = "base_link";
inline int g_instances = 0;                  // one mutable object, no .cpp needed

namespace {                                  // in a .cpp, never in a header
int local_helper() { return 42; }           // internal linkage
}
```

`kLimit` links fine because namespace-scope `const` implies internal linkage, but every translation unit gets its own object, so `&kLimit` differs between files (we checked: comparing addresses across two files gave `false`). for a value that is usually harmless. for something whose identity matters, or a non-trivial type like `const std::string`, each copy also has its own constructor running at startup. `inline constexpr` gives you one entity with no startup cost, and is the idiomatic way to define header constants in C++17.

### in practice

the ODR bites hardest at the boundaries of a large build. a robotics stack pulls in a header-only math library through two dependencies pinned to different versions, so `struct Pose` has two fields in one library and three in the other. or a perception library is built with a compile definition that adds a debug member to a struct, while the planner that uses it is not. every translation unit compiles cleanly. at run time one side writes 24 bytes where the other allocated 16, and the crash happens far from the cause.

your defenses are mostly process: one version of each dependency per binary, compile definitions that change layout applied consistently (or not used in public headers at all), and a link-time check. GCC with link-time optimization does compare type definitions across translation units:

```text
$ g++ -O2 -flto s1.cpp s2.cpp
s1.cpp:1:8: warning: type 'struct Pose' violates the C++ One Definition Rule [-Wodr]
s2.cpp:1:28: note: the first difference of corresponding definitions is field 'theta'
```

it caught the mismatched struct in our test; it did not flag the two `gain()` bodies above. treat it as a net, not a guarantee. keeping headers small and their contents unconditional is the design-level fix: every line in a header is a promise made, identically, to every file that includes it.

### watch out for

`static` in a header "fixes" a duplicate-symbol error by giving every translation unit its own private copy. for a function that is merely code bloat. for a variable it is a logic bug waiting to happen:

```cpp complete
// counters.h
static int s_dropped_frames = 0;   // BUG: one counter per .cpp file, not one per program
```

every file that increments `s_dropped_frames` updates its own counter, and the telemetry thread that reads it sees only the copy in its own translation unit. in our test, a `static int` incremented twice in one file and once in another read as 2 and 1, while an `inline int` declared next to it read 3 everywhere. if you want one object, write `inline`. if you want one per file, put it in an anonymous namespace in the `.cpp`, not in a header.

### the takeaway

the compiler sees one translation unit, the linker sees names, and the ODR is a promise that nobody is obliged to check; keep header contents identical everywhere, and use `inline` (C++17 variables included) when you mean "one entity, defined in a header".

### optional challenge

this header is included by `lidar.cpp` and `radar.cpp`, which are linked into one program. which lines cause a link error, and which compile and link but might not do what the author intended?

```cpp complete
// limits.h
#pragma once
const int kMaxTargets = 64;
int g_target_count;
inline int g_frame_count = 0;
static double s_last_stamp = 0.0;
```

<details>
<summary>answer</summary>

`int g_target_count;` is the link error. in C++ it is a definition with external linkage (C's "tentative definitions" do not exist in C++), so two translation units means two definitions: `multiple definition of 'g_target_count'`. fix it with `inline int g_target_count = 0;` or with `extern` in the header and a definition in one `.cpp`.

`kMaxTargets` links fine because `const` gives it internal linkage; each file has its own copy, which is harmless for a value. `g_frame_count` is one shared object (C++17 inline variable). `s_last_stamp` links fine but is the trap: `lidar.cpp` and `radar.cpp` each get their own `s_last_stamp`, so a write in one is invisible in the other. `#pragma once` is irrelevant to all of this; it only prevents double inclusion within a single translation unit.

</details>
