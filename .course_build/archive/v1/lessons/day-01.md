<a id="day-01"></a>

## day 01: from source file to running program

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** none

### the idea

Two files in the same robot driver each contain `inline int gain() { ... }`. One returns 2, the other returns 3. The build is clean, no warnings, and the program prints a different answer depending on whether you built with `-O0` or `-O2`. Nothing about this is a compiler bug. It follows directly from how C++ turns source files into a program, and from a rule that the toolchain is allowed to leave completely unchecked.

### understanding the concept

A C++ build is a pipeline, and each stage sees less than you might think.

```text
widget.cpp --preprocess--> translation unit --compile--> assembly --assemble--> widget.o
                                                                                    |
       other .o files and libraries ------------------------------------------> link --> program
```

1. **Preprocessing** (`g++ -E`) is text substitution. `#include` pastes a file in, macros expand, `#if` removes text. The result is a **translation unit**: one source file plus everything it transitively included. A header is not a module or an interface in any formal sense; it is text that ends up copied into every translation unit that includes it.
2. **Compilation** (`g++ -S`) turns one translation unit into assembly. The compiler sees exactly one translation unit at a time. It has no idea what any other `.cpp` file contains.
3. **Assembly** (`g++ -c`) produces an object file: machine code plus a symbol table listing what this file *defines* and what it *references but does not define*.
4. **Linking** combines object files and libraries, matches every undefined reference to exactly one definition, and patches addresses.

You can see the symbol table with `nm -C`. `U` means "I need this from someone else", `T` means "I define this in my code section":

```sh
$ g++ -std=c++17 -c main.cpp && nm -C main.o
                 U report_a()
                 U report_b()
0000000000000000 T main
```

The linker matches **names**, not types or meaning. The mangled name of `report_a()` encodes its namespace and parameter types, which is why a missing overload shows up as an "undefined reference" rather than a type error. Return types and class layouts are not checked at link time at all.

**Declarations versus definitions.** A declaration introduces a name (`double scale(double);`, `extern int count;`, `struct Pose;`). A definition creates the thing (the function body, the storage for the variable, the full class). You may declare something as often as you like; definitions are restricted.

**Linkage** decides whether the same name in different translation units refers to the same entity:

| linkage | meaning | how you get it |
|---|---|---|
| external | one entity shared across translation units | non-`static` functions and variables at namespace scope |
| internal | private to this translation unit | `static` at namespace scope, anything in an anonymous namespace, non-`inline` `const` variables at namespace scope |
| none | local to a scope | local variables |

**The one definition rule (ODR)** has two halves. Non-inline functions and variables with external linkage must be defined exactly once in the whole program; break this and you usually get a link error. Classes, inline functions, inline variables, and templates may be defined in several translation units (that is how headers work), but every definition must be identical: the same token sequence with the same meaning. Break *that* half and the program is ill-formed, no diagnostic required. The compiler cannot see it (one translation unit at a time) and the linker typically keeps one copy of each inline function and throws the rest away without comparing them.

**Templates live in headers** for the same reason. The compiler generates `std::vector<Detection>` code in the translation unit that uses it, so it must see the template's definition there. The alternative is explicit instantiation (`template class Filter<float>;` in one `.cpp`), which works when the set of types is closed.

**Include guards and `#pragma once`** stop a header from being pasted twice into the *same* translation unit. They do nothing across translation units, which is the source of most confusion about duplicate symbols. `#pragma once` is not in the standard but every mainstream compiler supports it; its weakness is that "the same file" is decided by the compiler, which can be fooled by copies of a header reached through different paths. Classic `#ifndef` guards are decided by the macro name, which you control.

### in code

**A duplicate symbol.** A helper defined in a header, included by two files:

```cpp
// scale.h
#pragma once
double scale(double x) { return x * 2.0; }   // BUG: a definition with external linkage

// a.cpp: #include "scale.h"     b.cpp: #include "scale.h"
```

```text
ld: b.cpp:(.text+0x0): multiple definition of `scale(double)'; a.cpp:(.text+0x0): first defined here
collect2: error: ld returned 1 exit status
```

The guard did its job (one copy per translation unit), and the result is still two definitions in the program. Three correct fixes: declare it in the header and define it in one `.cpp`; mark it `inline` (one entity, many identical definitions allowed); or, for a template, nothing, because templates are already allowed. Marking it `static` also links, but read "watch out for" first.

**A silent ODR violation.** Two translation units, two different bodies for the same inline function:

```cpp
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

With GCC 12 on our test machine, `g++ g1.cpp g2.cpp main.cpp` at `-O0` printed `a: 2` and `b: 2`; swapping the file order printed `3` and `3`. At `-O2` both orders printed `a: 2` and `b: 3`, because each call was inlined before the linker ever chose a copy. None of these outputs is "the right one": the program is ill-formed and the standard does not say what it does. In real code this happens when two files define a helper with a common name, or when a header's content depends on a macro (`#ifdef DEBUG_POSE`) that is set differently in different targets.

**One object, defined in a header (C++17).** Before C++17, a global shared by several translation units needed an `extern` declaration in the header and a definition in exactly one `.cpp`. Inline variables remove that ceremony:

```cpp
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

`kLimit` links fine because namespace-scope `const` implies internal linkage, but every translation unit gets its own object, so `&kLimit` differs between files (we checked: comparing addresses across two files gave `false`). For a value that is usually harmless. For something whose identity matters, or a non-trivial type like `const std::string`, each copy also has its own constructor running at startup. `inline constexpr` gives you one entity with no startup cost, and is the idiomatic way to define header constants in C++17.

### in practice

The ODR bites hardest at the boundaries of a large build. A robotics stack pulls in a header-only math library through two dependencies pinned to different versions, so `struct Pose` has two fields in one library and three in the other. Or a perception library is built with a compile definition that adds a debug member to a struct, while the planner that uses it is not. Every translation unit compiles cleanly. At run time one side writes 24 bytes where the other allocated 16, and the crash happens far from the cause.

Your defenses are mostly process: one version of each dependency per binary, compile definitions that change layout applied consistently (or not used in public headers at all), and a link-time check. GCC with link-time optimization does compare type definitions across translation units:

```text
$ g++ -O2 -flto s1.cpp s2.cpp
s1.cpp:1:8: warning: type 'struct Pose' violates the C++ One Definition Rule [-Wodr]
s2.cpp:1:28: note: the first difference of corresponding definitions is field 'theta'
```

It caught the mismatched struct in our test; it did not flag the two `gain()` bodies above. Treat it as a net, not a guarantee. Keeping headers small and their contents unconditional is the design-level fix: every line in a header is a promise made, identically, to every file that includes it.

### watch out for

`static` in a header "fixes" a duplicate-symbol error by giving every translation unit its own private copy. For a function that is merely code bloat. For a variable it is a logic bug waiting to happen:

```cpp
// counters.h
static int s_dropped_frames = 0;   // BUG: one counter per .cpp file, not one per program
```

Every file that increments `s_dropped_frames` updates its own counter, and the telemetry thread that reads it sees only the copy in its own translation unit. In our test, a `static int` incremented twice in one file and once in another read as 2 and 1, while an `inline int` declared next to it read 3 everywhere. If you want one object, write `inline`. If you want one per file, put it in an anonymous namespace in the `.cpp`, not in a header.

### the takeaway

The compiler sees one translation unit, the linker sees names, and the ODR is a promise that nobody is obliged to check; keep header contents identical everywhere, and use `inline` (C++17 variables included) when you mean "one entity, defined in a header".

### optional challenge

This header is included by `lidar.cpp` and `radar.cpp`, which are linked into one program. Which lines cause a link error, and which compile and link but might not do what the author intended?

```cpp
// limits.h
#pragma once
const int kMaxTargets = 64;
int g_target_count;
inline int g_frame_count = 0;
static double s_last_stamp = 0.0;
```

<details>
<summary>answer</summary>

`int g_target_count;` is the link error. In C++ it is a definition with external linkage (C's "tentative definitions" do not exist in C++), so two translation units means two definitions: `multiple definition of 'g_target_count'`. Fix it with `inline int g_target_count = 0;` or with `extern` in the header and a definition in one `.cpp`.

`kMaxTargets` links fine because `const` gives it internal linkage; each file has its own copy, which is harmless for a value. `g_frame_count` is one shared object (C++17 inline variable). `s_last_stamp` links fine but is the trap: `lidar.cpp` and `radar.cpp` each get their own `s_last_stamp`, so a write in one is invisible in the other. `#pragma once` is irrelevant to all of this; it only prevents double inclusion within a single translation unit.

</details>
