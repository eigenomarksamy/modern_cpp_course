# modern c++ daily course: 56 days of C++17 and C++20

*version 1.0. Generated from `.course_build/` by `course.py assemble`; edit the lesson and section sources there, then reassemble.*

<a id="introduction"></a>

## introduction and learning philosophy

You already write C++ for a living. You have shipped code that runs on robots, servers, or build farms, and you have debugged the kind of crash that only happens in release builds on a Tuesday. This course isn't here to teach you C++ from scratch. It is a structured way to revisit the parts of the language you use every day, understand the mechanics underneath them, and get fluent with the C++17 and C++20 features that make production code safer and clearer.

It runs for 56 days, in 8 weeks of 7 days. Each day takes 5 to 10 minutes to read, code included. Six days a week teach something new; the seventh is a short review with questions and a small exercise.

### how this course thinks

- **mechanics before features.** Move semantics make sense once value categories do. `std::string_view` is obvious once lifetime is. So the first weeks rebuild the foundations, and later features are explained in terms of them.
- **examples over prose.** Every lesson leans on small, purposeful code: naive version, then improved version; buggy version, then fixed version; "predict the output" puzzles. Read the code as carefully as the text.
- **judgment over rules.** "Never use raw pointers", "always use algorithms", "SOLID everything": rules like these are compressed experience, and they leak. Each lesson tries to say when a feature is the right tool, when it is not, and what it costs.
- **design is everywhere.** Ownership, coupling, error handling, testability, and compile-time versus runtime tradeoffs show up in every week, not only in the design week.
- **honesty about performance.** You will not find "X is 3x faster" here. You will find complexity, mechanisms (allocations, cache lines, indirections), and how to measure.

### how each day is structured

Instructional days follow the same shape, so you always know where you are:

| section | what it gives you |
| --- | --- |
| the idea | a question, a bug, or a misconception that motivates the topic |
| understanding the concept | the mechanics and the relevant rules, briefly |
| in code | 2 or 3 short examples, often before/after or buggy/fixed |
| in practice | where it matters in real systems |
| watch out for | the most common trap or tradeoff |
| the takeaway | one sentence worth remembering |
| optional challenge | a 2-minute puzzle, with a collapsed answer |

Review days (7, 14, 21, 28, 35, 42, 49, 56) have a recap, review questions (including spaced-repetition questions from earlier weeks), a mini exercise, collapsed answers, and a note on how the week connects to the rest.

### conventions used in the lessons

- Each day lists its **standard** (`C++17` or `C++20`): the minimum language version its examples need. If a single snippet needs something newer, it says so. C++23 features appear only as clearly labelled forward notes.
- `// prints: ...` shows expected output. `// BUG:` marks code that is wrong on purpose.
- Three terms are used precisely, because the difference matters:
  - **undefined behavior (UB):** the standard places no requirements on the program. The optimizer is allowed to assume it never happens, which is why UB bugs can look like time travel.
  - **unspecified behavior:** the program does one of several permitted things, and the implementation doesn't have to tell you which (for example, the order in which function arguments are evaluated).
  - **implementation-defined behavior:** unspecified, but the implementation must document its choice (for example, `sizeof(long)`).
- Cross references look like [day 05](#day-05) and jump to that lesson.

### setting up a playground

Any recent compiler works. A reasonable baseline:

```sh
# GCC 13+ or Clang 17+ for full C++20 library coverage including <format>
g++ -std=c++20 -Wall -Wextra -pedantic -g -fsanitize=address,undefined main.cpp -o main
./main
```

Sanitizers are available with GCC and Clang on Linux and macOS (MSVC supports AddressSanitizer). [Compiler Explorer](https://godbolt.org) is ideal for the short examples, and it lets you compare compilers and look at the generated assembly when a lesson talks about what the compiler does.

### how to use it

Read one day at a time, ideally with a compiler open. Do the optional challenge if it catches your interest, and don't skip the review days: they are short, and retrieval practice is what makes the material stick. Tick off days in the [progress checklist](#progress-checklist) as you go.

Weeks 1 to 4 form a complete, standalone C++17 refresher. Weeks 5 to 8 build on it with C++20, concurrency, design, and production engineering, ending with a small program on day 55 that brings the pieces together.

This is version 1.0 of the course. Each day is its own source file, so lessons can be expanded, corrected, or updated for newer standards one at a time.

<a id="course-overview"></a>

## course overview

```text
 weeks 1 to 4: a complete C++17 refresher

 [1 fundamentals] ─▶ [2 ownership] ─▶ [3 library, templates] ─▶ [4 C++17 in practice]
                                                                          │
 [8 production] ◀─ [7 design] ◀─ [6 concurrency] ◀─ [5 C++20 toolbox] ◀───┘

 weeks 5 to 8: C++20 and production engineering
```

| week | theme | what you will be able to do by the end |
| --- | --- | --- |
| [1](#week-1) | rediscovering C++ fundamentals | explain how source becomes a binary, pick the right initialization, reason about lifetimes and value categories, and recognize undefined behavior |
| [2](#week-2) | ownership and object-oriented C++ | build resource-safe types with RAII, apply the rule of zero, implement and reason about moves, express ownership with smart pointers, and choose composition over inheritance |
| [3](#week-3) | standard library and generic programming | choose containers by cost, write intent-revealing code with algorithms and lambdas, write templates with perfect forwarding, and design for exception safety |
| [4](#week-4) | modernizing with C++17 | use structured bindings, `if constexpr`, `optional`, `variant`, `string_view`, folds, and `filesystem`, and refactor legacy code with them |
| [5](#week-5) | the C++20 toolbox | constrain templates with concepts, build lazy pipelines with ranges, pass buffers as `span`, default comparisons, compute at compile time, and format with `std::format` |
| [6](#week-6) | concurrency and multithreading | run and stop threads with `jthread`, protect state with mutexes, coordinate with condition variables and futures, use atomics with a correct memory model, and avoid deadlocks |
| [7](#week-7) | software design and deeper C++ | apply SOLID with judgment, inject dependencies for testing, use patterns idiomatically, choose between static, dynamic, and type-erased polymorphism, design hard-to-misuse APIs, and get started with modules and coroutines |
| [8](#week-8) | production engineering and integration | benchmark honestly, design for cache locality, control allocations, test and observe production code, refactor legacy code incrementally, and combine it all in one small system |

### the threads that run through every week

Some ideas are not confined to one week; they come back repeatedly, each time with more depth:

- **lifetime and ownership:** days 03, 08, 10 to 12, 17, 26, 31, 36, 45, 47, 48.
- **error handling:** days 20, 24, 25, 27, 39, 47, 53.
- **compile time versus run time:** days 18, 23, 29, 33, 46.
- **design judgment** (coupling, cohesion, abstraction cost): days 09, 13, 17, 25, 37, 43 to 47, 54.
- **performance and measurement:** days 15, 16, 40, 50 to 52.

### pacing

Each day takes 5 to 10 minutes. If you miss a day, read two the next day, or use the review day to catch up; the reviews are deliberately light. If a topic hooks you, the [references](#references) at the end point to the best places to go deeper.

<a id="table-of-contents"></a>

## table of contents

- [introduction and learning philosophy](#introduction)
- [course overview](#course-overview)
- [progress checklist](#progress-checklist)
- [week 1: rediscovering c++ fundamentals](#week-1)
  - [day 01: from source file to running program](#day-01)
  - [day 02: types and the many faces of initialization](#day-02)
  - [day 03: scope, storage duration, and object lifetime](#day-03)
  - [day 04: pointers, references, and const](#day-04)
  - [day 05: value categories without the headache](#day-05)
  - [day 06: undefined behavior and other things the standard won't promise](#day-06)
  - [day 07: week 1 review: the ground beneath your feet](#day-07)
- [week 2: ownership and object-oriented c++](#week-2)
  - [day 08: RAII: let scope do the cleanup](#day-08)
  - [day 09: constructors, destructors, and the object lifecycle](#day-09)
  - [day 10: copy and move semantics](#day-10)
  - [day 11: the rule of zero, three, and five](#day-11)
  - [day 12: smart pointers and ownership in interfaces](#day-12)
  - [day 13: polymorphism, inheritance, and composition](#day-13)
  - [day 14: week 2 review: owning your resources](#day-14)
- [week 3: standard library and generic programming](#week-3)
  - [day 15: containers and what they cost](#day-15)
  - [day 16: iterators and algorithms over raw loops](#day-16)
  - [day 17: lambdas and closures in depth](#day-17)
  - [day 18: templates: writing code for many types](#day-18)
  - [day 19: forwarding references and perfect forwarding](#day-19)
  - [day 20: exception safety and error handling strategy](#day-20)
  - [day 21: week 3 review: the library as a vocabulary](#day-21)
- [week 4: modernizing with c++17](#week-4)
  - [day 22: structured bindings, init-statements, and helpful attributes](#day-22)
  - [day 23: compile-time branching with `if constexpr` and fold expressions](#day-23)
  - [day 24: `std::optional`: modeling "maybe"](#day-24)
  - [day 25: `std::variant` and `std::any`: sum types and type-erased values](#day-25)
  - [day 26: `std::string_view` and non-owning views](#day-26)
  - [day 27: `std::filesystem` and a practical C++17 refactoring](#day-27)
  - [day 28: week 4 review: a complete C++17 refresher](#day-28)
- [week 5: the c++20 toolbox](#week-5)
  - [day 29: concepts: constraining templates](#day-29)
  - [day 30: ranges and views: lazy pipelines](#day-30)
  - [day 31: `std::span`: views over contiguous memory](#day-31)
  - [day 32: three-way comparison and defaulted equality](#day-32)
  - [day 33: compile-time programming in C++20](#day-33)
  - [day 34: `std::format` and other everyday C++20 improvements](#day-34)
  - [day 35: week 5 review: the C++20 toolbox](#day-35)
- [week 6: concurrency and multithreading](#week-6)
  - [day 36: threads and `std::jthread`](#day-36)
  - [day 37: data races and mutexes](#day-37)
  - [day 38: condition variables and the producer-consumer queue](#day-38)
  - [day 39: futures, promises, and tasks](#day-39)
  - [day 40: atomics and the memory model](#day-40)
  - [day 41: deadlocks and concurrency design](#day-41)
  - [day 42: week 6 review: sharing safely](#day-42)
- [week 7: software design and deeper c++](#week-7)
  - [day 43: SOLID, coupling, and cohesion without dogma](#day-43)
  - [day 44: dependency injection and testable seams](#day-44)
  - [day 45: design patterns in modern C++: strategy, factory, and observer](#day-45)
  - [day 46: static versus dynamic polymorphism and type erasure](#day-46)
  - [day 47: designing APIs that are hard to misuse](#day-47)
  - [day 48: C++20 modules and coroutines: a practical first look](#day-48)
  - [day 49: week 7 review: design with judgment](#day-49)
- [week 8: production engineering and integration](#week-8)
  - [day 50: measure first: benchmarking and profiling](#day-50)
  - [day 51: cache locality and data-oriented design](#day-51)
  - [day 52: the cost of allocation](#day-52)
  - [day 53: testing and observability](#day-53)
  - [day 54: refactoring legacy code and architectural tradeoffs](#day-54)
  - [day 55: putting it together: a small sensor-processing pipeline](#day-55)
  - [day 56: week 8 review and the road ahead](#day-56)
- [modern C++17/20 cheat sheet](#cheat-sheet)
- [references for deeper study](#references)

<a id="progress-checklist"></a>

## progress checklist

Tick a box as you finish each day (in an editor, or on a printed copy).

**week 1: rediscovering c++ fundamentals**

- [ ] [day 01: from source file to running program](#day-01)
- [ ] [day 02: types and the many faces of initialization](#day-02)
- [ ] [day 03: scope, storage duration, and object lifetime](#day-03)
- [ ] [day 04: pointers, references, and const](#day-04)
- [ ] [day 05: value categories without the headache](#day-05)
- [ ] [day 06: undefined behavior and other things the standard won't promise](#day-06)
- [ ] [day 07: week 1 review: the ground beneath your feet](#day-07)

**week 2: ownership and object-oriented c++**

- [ ] [day 08: RAII: let scope do the cleanup](#day-08)
- [ ] [day 09: constructors, destructors, and the object lifecycle](#day-09)
- [ ] [day 10: copy and move semantics](#day-10)
- [ ] [day 11: the rule of zero, three, and five](#day-11)
- [ ] [day 12: smart pointers and ownership in interfaces](#day-12)
- [ ] [day 13: polymorphism, inheritance, and composition](#day-13)
- [ ] [day 14: week 2 review: owning your resources](#day-14)

**week 3: standard library and generic programming**

- [ ] [day 15: containers and what they cost](#day-15)
- [ ] [day 16: iterators and algorithms over raw loops](#day-16)
- [ ] [day 17: lambdas and closures in depth](#day-17)
- [ ] [day 18: templates: writing code for many types](#day-18)
- [ ] [day 19: forwarding references and perfect forwarding](#day-19)
- [ ] [day 20: exception safety and error handling strategy](#day-20)
- [ ] [day 21: week 3 review: the library as a vocabulary](#day-21)

**week 4: modernizing with c++17**

- [ ] [day 22: structured bindings, init-statements, and helpful attributes](#day-22)
- [ ] [day 23: compile-time branching with `if constexpr` and fold expressions](#day-23)
- [ ] [day 24: `std::optional`: modeling "maybe"](#day-24)
- [ ] [day 25: `std::variant` and `std::any`: sum types and type-erased values](#day-25)
- [ ] [day 26: `std::string_view` and non-owning views](#day-26)
- [ ] [day 27: `std::filesystem` and a practical C++17 refactoring](#day-27)
- [ ] [day 28: week 4 review: a complete C++17 refresher](#day-28)

**week 5: the c++20 toolbox**

- [ ] [day 29: concepts: constraining templates](#day-29)
- [ ] [day 30: ranges and views: lazy pipelines](#day-30)
- [ ] [day 31: `std::span`: views over contiguous memory](#day-31)
- [ ] [day 32: three-way comparison and defaulted equality](#day-32)
- [ ] [day 33: compile-time programming in C++20](#day-33)
- [ ] [day 34: `std::format` and other everyday C++20 improvements](#day-34)
- [ ] [day 35: week 5 review: the C++20 toolbox](#day-35)

**week 6: concurrency and multithreading**

- [ ] [day 36: threads and `std::jthread`](#day-36)
- [ ] [day 37: data races and mutexes](#day-37)
- [ ] [day 38: condition variables and the producer-consumer queue](#day-38)
- [ ] [day 39: futures, promises, and tasks](#day-39)
- [ ] [day 40: atomics and the memory model](#day-40)
- [ ] [day 41: deadlocks and concurrency design](#day-41)
- [ ] [day 42: week 6 review: sharing safely](#day-42)

**week 7: software design and deeper c++**

- [ ] [day 43: SOLID, coupling, and cohesion without dogma](#day-43)
- [ ] [day 44: dependency injection and testable seams](#day-44)
- [ ] [day 45: design patterns in modern C++: strategy, factory, and observer](#day-45)
- [ ] [day 46: static versus dynamic polymorphism and type erasure](#day-46)
- [ ] [day 47: designing APIs that are hard to misuse](#day-47)
- [ ] [day 48: C++20 modules and coroutines: a practical first look](#day-48)
- [ ] [day 49: week 7 review: design with judgment](#day-49)

**week 8: production engineering and integration**

- [ ] [day 50: measure first: benchmarking and profiling](#day-50)
- [ ] [day 51: cache locality and data-oriented design](#day-51)
- [ ] [day 52: the cost of allocation](#day-52)
- [ ] [day 53: testing and observability](#day-53)
- [ ] [day 54: refactoring legacy code and architectural tradeoffs](#day-54)
- [ ] [day 55: putting it together: a small sensor-processing pipeline](#day-55)
- [ ] [day 56: week 8 review and the road ahead](#day-56)

<a id="week-1"></a>

## week 1: rediscovering c++ fundamentals

The ground floor: how code becomes a program, how objects come into existence, and what the language actually promises.

<a id="day-01"></a>

### day 01: from source file to running program

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** none

#### the idea

Two files in the same robot driver each contain `inline int gain() { ... }`. One returns 2, the other returns 3. The build is clean, no warnings, and the program prints a different answer depending on whether you built with `-O0` or `-O2`. Nothing about this is a compiler bug. It follows directly from how C++ turns source files into a program, and from a rule that the toolchain is allowed to leave completely unchecked.

#### understanding the concept

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

#### in code

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

#### in practice

The ODR bites hardest at the boundaries of a large build. A robotics stack pulls in a header-only math library through two dependencies pinned to different versions, so `struct Pose` has two fields in one library and three in the other. Or a perception library is built with a compile definition that adds a debug member to a struct, while the planner that uses it is not. Every translation unit compiles cleanly. At run time one side writes 24 bytes where the other allocated 16, and the crash happens far from the cause.

Your defenses are mostly process: one version of each dependency per binary, compile definitions that change layout applied consistently (or not used in public headers at all), and a link-time check. GCC with link-time optimization does compare type definitions across translation units:

```text
$ g++ -O2 -flto s1.cpp s2.cpp
s1.cpp:1:8: warning: type 'struct Pose' violates the C++ One Definition Rule [-Wodr]
s2.cpp:1:28: note: the first difference of corresponding definitions is field 'theta'
```

It caught the mismatched struct in our test; it did not flag the two `gain()` bodies above. Treat it as a net, not a guarantee. Keeping headers small and their contents unconditional is the design-level fix: every line in a header is a promise made, identically, to every file that includes it.

#### watch out for

`static` in a header "fixes" a duplicate-symbol error by giving every translation unit its own private copy. For a function that is merely code bloat. For a variable it is a logic bug waiting to happen:

```cpp
// counters.h
static int s_dropped_frames = 0;   // BUG: one counter per .cpp file, not one per program
```

Every file that increments `s_dropped_frames` updates its own counter, and the telemetry thread that reads it sees only the copy in its own translation unit. In our test, a `static int` incremented twice in one file and once in another read as 2 and 1, while an `inline int` declared next to it read 3 everywhere. If you want one object, write `inline`. If you want one per file, put it in an anonymous namespace in the `.cpp`, not in a header.

#### the takeaway

The compiler sees one translation unit, the linker sees names, and the ODR is a promise that nobody is obliged to check; keep header contents identical everywhere, and use `inline` (C++17 variables included) when you mean "one entity, defined in a header".

#### optional challenge

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

[back to table of contents](#table-of-contents)

---

<a id="day-02"></a>

### day 02: types and the many faces of initialization

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** [day 01](#day-01)

#### the idea

A colleague modernizes a radar module and changes `std::vector<float> gains(8, 0.5f);` to `std::vector<float> gains{8, 0.5f};` because "braces are the modern way". The code compiles. The vector now has two elements, 8.0 and 0.5, and the beamformer reads past the gains it expected. C++ has roughly half a dozen ways to initialize an object, they differ in real ways, and the one advertised as "uniform" is not uniform at all.

#### understanding the concept

The forms, from least to most initialized:

| syntax | name | what happens |
|---|---|---|
| `T x;` | default-initialization | class types: default constructor runs. Scalars and aggregates of scalars with automatic storage: **indeterminate** value |
| `T x{};` or `T()` | value-initialization | scalars: zero. Class with a user-provided default constructor: that constructor runs. Otherwise: zeroed, then any non-trivial default construction |
| `T x(a);` | direct-initialization | all constructors considered, including `explicit` ones |
| `T x = a;` | copy-initialization | `explicit` constructors are not considered |
| `T x{a};` / `T x = {a};` | direct/copy-list-initialization | as above, but narrowing is rejected and `std::initializer_list` constructors win |
| `S s{1, 2.0};` | aggregate initialization | members initialized in declaration order; omitted members from their default member initializer, otherwise as if from `{}` |

An aggregate (C++17) is an array or a class with no user-provided, `explicit`, or inherited constructors, no private or protected non-static data members, no virtual functions, and no virtual, private, or protected bases. C++20 tightens "user-provided" to "user-declared", so a struct with `S() = default;` stops being an aggregate.

Objects with **static or thread storage duration** are different: they are zero-initialized before anything else happens, so a global `int counter;` is reliably 0. Only automatic (and dynamically allocated) scalars start indeterminate, and reading an indeterminate value is undefined behavior (day 06 will show why the optimizer makes that worse than "you get garbage").

**List-initialization has two special rules.** First, it rejects *narrowing* conversions: floating to integer, `double` to `float` (unless the source is a constant that fits), and integer to a type that cannot represent the value. Second, if the class has a constructor taking `std::initializer_list`, a non-empty braced list strongly prefers it over every other constructor, even when another one is a better match. Empty braces are the exception: `{}` means the default constructor.

**`auto` with braces** changed in C++17 (compilers also apply the fix in C++14 mode): `auto a{1};` is `int`, `auto b = {1};` is `std::initializer_list<int>`, and `auto c{1, 2};` is ill-formed. The `=` changes the meaning, which is reason enough to write `auto x = 1;` and keep braces for objects.

**Types and sizes.** `sizeof(char)` is 1 by definition; everything else is implementation-defined within minimums (`int` at least 16 bits, `long` at least 32, `long long` at least 64). `long` is 64 bits on x86-64 Linux and 32 bits on Windows, including MinGW; our test machine printed `sizeof(long) == 4`. When the width matters (wire formats, registers, file headers), use `<cstdint>`: `std::int32_t`, `std::uint64_t`. The exact-width types are technically optional but exist on every mainstream platform; `std::int_least32_t` and `std::int_fast32_t` always exist.

**Promotions and conversions.** Arithmetic never happens in types narrower than `int`: `char`, `short`, `std::uint8_t`, and `std::uint16_t` are promoted to `int` first. When a signed and an unsigned operand of the same rank meet, the *signed one is converted to unsigned*. That rule produces most of the surprises.

#### in code

**Predict the output.** Cover the comments and work out each line.

```cpp
#include <iostream>
#include <string>
#include <vector>

struct Pose { double x = 0.0, y = 0.0, theta = 0.0; };

int main() {
    std::vector<int> a(3, 1);   // constructor (count, value)
    std::vector<int> b{3, 1};   // initializer_list constructor wins
    std::vector<int> c{};       // empty braces: default constructor
    std::cout << a.size() << ' ' << b.size() << ' ' << c.size() << '\n';
    // prints: 3 2 0

    std::string s(3, 'a');      // "aaa"
    std::string t{3, 'a'};      // two chars: '\x03' and 'a'
    std::cout << s.size() << ' ' << t.size() << '\n';   // prints: 3 2

    Pose p{};                   // all members from their initializers
    Pose q{1.0, 2.0};           // aggregate init: theta keeps 0.0
    std::cout << p.x << ' ' << q.theta << '\n';         // prints: 0 0
}
```

The rule for library types: if the class has an `initializer_list` constructor (containers, `std::string`), braces mean "these are the elements". Use parentheses when you mean "call the sizing constructor".

**Braces as a narrowing guard, and the most vexing parse.**

```cpp
#include <cstdint>

struct RadarConfig { float max_range_m; std::uint16_t num_bins; };

int truncate(double measured) {
    int a = measured;               // compiles: silently truncates toward zero
    int b{measured};                // ill-formed: narrowing double -> int
    RadarConfig cfg{250.0, 70000};  // ill-formed: 70000 does not fit uint16_t
    return a + b + cfg.num_bins;
}

struct Clock {};
struct Timer { explicit Timer(Clock) {} void start() {} };

void vexing() {
    Timer t(Clock());   // BUG: declares a function t taking a function, returning Timer
    t.start();          // error: t is not an object
    Timer u{Clock{}};   // an object, as intended
}
```

The standard makes narrowing in list-initialization ill-formed. GCC 12 reports constants that do not fit (`70000`, `char c{300}`) as errors, but reports the non-constant `int b{measured}` only as a `-Wnarrowing` warning; Clang rejects both. Add `-Werror=narrowing` (or `-pedantic-errors`) to get the standard's behavior on GCC. The vexing parse comes from the grammar rule "anything that can be a declaration is a declaration"; GCC 11 and later warn with `-Wvexing-parse`, and braces remove the ambiguity entirely.

**Integer promotion and signed/unsigned comparison.**

```cpp
#include <cstdint>
#include <iostream>
#include <vector>

int main() {
    std::uint8_t a = 200, b = 100;
    auto sum = a + b;                 // both promoted to int; sum is int
    std::cout << sum << '\n';         // prints: 300

    int i = -1;
    unsigned u = 1;
    std::cout << (i < u) << '\n';     // prints: 0, because -1 becomes UINT_MAX

    std::vector<int> readings;        // empty
    std::cout << readings.size() - 1 << '\n';
    // prints: 18446744073709551615 with a 64-bit size_t (unsigned wraparound, well defined)

    std::uint8_t id = 65;
    std::cout << id << '\n';          // prints: A (uint8_t is usually unsigned char)
}
```

`-Wall` includes `-Wsign-compare` in C++ and flags the `i < u` line. Unsigned arithmetic wraps modulo 2^N by definition, so `size() - 1` is not undefined; it is simply a huge number, and a loop `for (std::size_t k = 0; k <= v.size() - 1; ++k)` on an empty vector runs off the end. C++20 adds `std::cmp_less` and friends in `<utility>` for comparisons that are correct across signedness.

#### in practice

Configuration structs are where initialization style pays off. A telemetry packet header or a sensor configuration as an aggregate with default member initializers gives you three properties at once: every field has a defined value even when the caller forgets one, brace initialization rejects narrowing such as a `double` squeezed into a `std::uint16_t` field, and the type stays trivially copyable for serialization:

```cpp
struct ImuConfig {
    std::uint16_t rate_hz = 200;
    float accel_range_g = 8.0f;
    bool  enable_fifo = true;
};

ImuConfig cfg{400};   // rate_hz = 400, the rest keep their defaults
```

The weakness is that positional aggregate initialization ties every call site to member order; inserting a field in the middle silently shifts meanings when the types are compatible. C++20 designated initializers (day 34) fix that. Choosing an aggregate over a class with a constructor is a design decision: an aggregate says "this is plain data with no invariant", which is exactly right for configuration and wrong for anything that must validate its fields.

#### watch out for

Value-initialization only zeroes members when the compiler supplies the constructor. A user-provided default constructor that forgets a member defeats `{}`:

```cpp
struct Raw    { double x, y; };                 // no constructor
struct Sensor { Sensor() {} int id; };          // user-provided, does not set id

Raw r{};       // r.x and r.y are 0.0
Sensor s{};    // s.id is indeterminate: the constructor runs and that is all
Raw r2;        // r2.x is indeterminate (automatic storage)
```

GCC flagged a read of `s.id` with `-Wuninitialized` at `-O2`, but such warnings depend on optimization level and inlining, so do not rely on them. The robust habit is a default member initializer on every scalar member (`int id = 0;`); then every form of initialization, including plain `Sensor s;`, produces a defined value.

#### the takeaway

Use braces for objects you build from values (they reject narrowing), parentheses when calling a sizing constructor on a container, default member initializers on every scalar, and fixed-width types wherever the width is part of the contract.

#### optional challenge

Assuming a typical platform with a 32-bit `int`, what does this function return for `a = b = 65535`, and is the result even defined?

```cpp
#include <cstdint>
std::uint32_t area(std::uint16_t a, std::uint16_t b) { return a * b; }
```

<details>
<summary>answer</summary>

Both operands are promoted to `int` (signed, 32 bits) before the multiplication, because `int` can represent every `std::uint16_t` value. 65535 * 65535 = 4,294,836,225, which exceeds `INT_MAX` (2,147,483,647). Signed overflow is undefined behavior, so the function has no defined result for those inputs, even though every type in the signature is unsigned. The fix is to convert before multiplying: `return std::uint32_t{a} * b;`, which makes the arithmetic happen in `std::uint32_t` (the other operand is converted to unsigned) where wraparound is defined and, here, there is no overflow at all.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-03"></a>

### day 03: scope, storage duration, and object lifetime

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days [01](#day-01), [02](#day-02)

#### the idea

"The variable is still in scope, so the object is still alive." That sentence is behind a surprising share of dangling-reference bugs. Scope is a compile-time property of a *name*: the region of source text where the name can be used. Lifetime is a run-time property of an *object*: the interval during which it exists and may be accessed. They often coincide, which is why we conflate them. A reference can be perfectly in scope while the object it names is long gone, and a function-local `static` is out of scope almost everywhere while its object lives until the program exits.

#### understanding the concept

Every object has a **storage duration**, which bounds how long its storage exists:

| storage duration | objects | storage lasts |
|---|---|---|
| automatic | block-scope locals, parameters | until the enclosing block exits |
| static | namespace-scope variables, `static` locals, `static` data members | the whole program |
| thread | `thread_local` variables | the lifetime of each thread (one object per thread) |
| dynamic | objects from `new` (and allocator-based containers) | until you `delete` them |

Temporaries are a fifth case: a temporary object is destroyed at the end of the **full-expression** that created it, which in practice usually means at the `;`.

An object's **lifetime** begins when its storage is obtained and its initialization is complete, and ends when its destructor call starts (or, for types with trivial destructors, when its storage is released or reused). Touching an object outside its lifetime through a pointer or reference is undefined behavior, even if the bytes are still there and still look right.

**Lifetime extension.** When a temporary is bound *directly* to a `const T&` or `T&&` local reference, the temporary lives as long as the reference. "Directly" includes a member accessed on a temporary (`make_frame().ids`). It does not include anything that passes through a function returning a reference, because the compiler cannot see what that reference refers to. Also, a temporary bound to a function's reference parameter only lives until the end of the full-expression containing the call, and a temporary bound to the return value in a `return` statement is not extended at all.

**Static initialization.** Objects with static storage duration are first zero-initialized or constant-initialized (no code runs; the values are in the binary). Anything else is *dynamic* initialization, which runs before `main` (strictly, before first use of something in that translation unit, but mainstream implementations do it at startup). Within one translation unit, dynamic initialization follows definition order. Across translation units, the order is unspecified. That gap is the **static initialization order fiasco**: if a global's initializer reads a global from another file, it may read an object whose lifetime has not begun.

A **function-local static** fixes this: it is initialized the first time control passes through its declaration, and since C++11 that initialization is thread-safe (concurrent callers wait for it to finish). Destruction runs in reverse order of construction completion, for locals and statics alike.

#### in code

**Predict the output.** Construction and destruction across all the durations above:

```cpp
#include <cstdio>

struct Tracer {
    const char* name;
    explicit Tracer(const char* n) : name(n) { std::printf("+%s ", name); }
    ~Tracer() { std::printf("-%s ", name); }
};

Tracer global("global");                        // static storage duration
Tracer make(const char* n) { return Tracer(n); }
void tick() { static Tracer once("static"); }   // block scope, static storage

int main() {
    std::printf("main ");
    Tracer a("a");
    tick();
    tick();                                      // already constructed: nothing printed
    { Tracer b("b"); }
    std::printf("use:%s ", make("temp").name);   // temporary dies at the ';'
    const Tracer& ext = make("ext");             // lifetime extended to ext's scope
    Tracer c("c");
    std::printf("return ");
}
// prints: +global main +a +static +b -b +temp use:temp -temp +ext +c return -c -ext -a -static -global
```

Note that `-static` comes after `-a` but before `-global`: statics die after `main` returns, in reverse order of construction, and `once` finished constructing after `global`.

**Dangling: a reference to a local, and a range-for over a temporary.**

```cpp
#include <string>
#include <vector>

const std::string& frame_id() {
    std::string id = "base_link";
    return id;                // BUG: the reference outlives id (GCC: -Wreturn-local-addr)
}

struct Frame {
    std::vector<int> ids;
    const std::vector<int>& detections() const { return ids; }
};
Frame load_frame();
void consume(int);

void process() {
    for (int d : load_frame().detections()) consume(d);   // BUG: UB in C++17 and C++20
    for (int d : load_frame().ids) consume(d);            // fine: member of a temporary, extended
}
```

The range-for is the subtle one. It expands to roughly `auto&& range = load_frame().detections();` followed by the loop. `detections()` returns a reference, so the `Frame` temporary is not extended; it dies at the end of that hidden declaration and the loop iterates a destroyed vector. GCC 12 gave no warning for it. C++23 extends the lifetime of all temporaries in the range-for initializer, which fixes this exact case, but in C++17 and C++20 it is undefined behavior. The portable fix is to name the object first: `auto frame = load_frame(); for (int d : frame.detections())`.

**The static initialization order fiasco and its fix.**

```cpp
// prefix.cpp
std::string g_prefix = "radar/";

// topic.cpp
extern std::string g_prefix;
std::string g_topic = g_prefix + "tracks";   // BUG: g_prefix may not be constructed yet

// fixed: prefix.cpp
const std::string& prefix() {
    static const std::string p = "radar/";   // constructed on first call, thread-safe
    return p;
}
// fixed: topic.cpp
std::string g_topic = prefix() + "tracks";
```

On our MinGW build, one link order printed `[radar/tracks]` and the other printed `[tracks]`: `g_prefix` was read while its storage was still only zero-initialized. That output is luck, not a guarantee; reading an object before its lifetime begins is undefined behavior and could as easily crash. The fixed version printed `[radar/tracks]` in both orders. If the value is a compile-time constant, an even better fix is to make it one: `inline constexpr std::string_view kPrefix = "radar/";` is constant-initialized and has no order at all (C++20 adds `constinit` to require constant initialization of a non-`const` variable).

#### in practice

Plugin registries in robotics and tooling frameworks are where the fiasco lives in the wild. Each driver file contains a static registrar, something like `static const bool registered = SensorRegistry::add("velodyne", &make_velodyne);`, so that linking a driver is enough to make it available. Those registrars run during dynamic initialization of their own translation units, in unspecified order. If the registry is a global `std::map`, a registrar can insert into a map whose constructor has not run yet. The standard pattern is a function-local static: `static SensorRegistry& instance() { static SensorRegistry r; return r; }`.

The mirror image happens at shutdown. A static object whose destructor logs through a global logger may run after the logger has been destroyed. A common, deliberate escape hatch is a "leaky" singleton, `static Logger* l = new Logger;`, which is never destroyed; the operating system reclaims the memory, at the price of no destructor running (so flush explicitly). Global mutable state is a coupling problem before it is an ordering problem: every object with static storage that reads another is a hidden dependency, and fewer globals means fewer of these puzzles.

#### watch out for

Lifetime extension does not pass through function calls, and the classic victim is a standard algorithm returning a reference:

```cpp
#include <algorithm>

int lo();
int hi();

const int& m = std::max(lo(), hi());   // BUG: dangles
int v = std::max(lo(), hi());          // fine: copied before the ';'
```

`std::max` takes `const int&` parameters and returns one of them. The two temporaries are bound to its parameters, so they live only until the end of the full-expression, and `m` is left referring to a dead temporary. In our test at `-O2`, GCC printed `0` for `m` (and, by luck, warned about an uninitialized read). GCC 13 added `-Wdangling-reference` for this pattern; GCC 12 has nothing specific. The defense is a habit: bind function results by value unless you know the function returns a reference to something that outlives your reference.

#### the takeaway

Ask "who owns this object and when does it die?" rather than "is this name in scope?"; temporaries die at the `;` unless bound directly to a local reference, and anything shared between translation units at startup belongs behind a function-local static.

#### optional challenge

`load()` returns a `Frame` by value. Which of these three lines leave a dangling reference?

```cpp
struct Frame {
    std::vector<int> ids;
    const std::vector<int>& get() const { return ids; }
};
Frame load();

const auto& a = load().ids;     // (1)
const auto& b = load().get();   // (2)
auto c = load().get();          // (3)
```

<details>
<summary>answer</summary>

Only (2). In (1) the reference binds directly to a member subobject of the temporary, so the whole `Frame` temporary is extended to `a`'s lifetime. In (2) the reference comes back through a member function; the compiler does not extend anything, the `Frame` dies at the `;`, and `b` dangles. In (3) `c` is a copy of the vector (`auto` deduces `std::vector<int>`), made while the temporary is still alive, so it is safe and owns its own data.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-04"></a>

### day 04: pointers, references, and const

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days [02](#day-02), [03](#day-03)

#### the idea

Read this declaration from a tracking library: `void update(Track* t, Detection* d);`. Can `t` be null? Will `update` modify `d`? Will it keep either pointer after it returns? The signature answers none of these questions. Now compare `void update(Track& t, const Detection& d);`: both must exist, only `t` changes, and nothing in the types suggests the function holds on to them. Pointers, references, and `const` are not only about mechanics. They are the cheapest documentation you will ever write, and the compiler checks it.

#### understanding the concept

**A reference is an alias.** Once bound, it names the same object for its whole life; there is no syntax to rebind it. `r = b;` assigns `b`'s value to whatever `r` refers to. A reference must be initialized, and in a valid program it always refers to an object or function, because the only way to make a "null reference" is to dereference a null pointer first, which is already undefined behavior. A reference can still dangle (day 03), so "never null" does not mean "always valid".

**A pointer is an object holding an address.** It can be null, it can be reassigned, it can be compared, and it supports arithmetic within an array. That flexibility is exactly what makes it the right tool for "optional" and "may change what it points to", and the wrong tool when neither applies.

**Reading `const`.** `const` applies to whatever is immediately to its left, or to the right if nothing is on its left. Reading right to left works well:

| declaration | read as | can change pointer | can change pointee |
|---|---|---|---|
| `const T* p` (same as `T const* p`) | pointer to const T | yes | no |
| `T* const p` | const pointer to T | no | yes |
| `const T* const p` | const pointer to const T | no | no |
| `const T& r` | reference to const T | (never) | no |

`const T&` means "read-only access through this name", not "this object is immutable". Someone else holding a non-const path to the same object can change it under you.

**Const member functions.** In a member function marked `const`, `this` has type `const T*`, so data members are treated as `const`. That lets you call the function on `const` objects and through `const&` parameters, and it is a promise: calling it does not change the object's observable state. That is *logical* constness. Sometimes the bits must change while the observable state does not (a cache, a mutex, a statistics counter); `mutable` exempts a member from the rule.

**`nullptr`, not `NULL` or `0`.** `NULL` is an implementation-defined null pointer constant: it might be `0`, `0L`, or a compiler intrinsic like GCC's `__null`. Its type is an integer type in practice, so it can select an integer overload. `nullptr` has type `std::nullptr_t`, which converts to any pointer type and to no integer type.

**Arrays decay.** An array expression converts to a pointer to its first element in most contexts, and a function parameter declared as `T a[N]` is really `T* a`; the `N` is ignored. Pointer arithmetic is defined only within one array: you may form pointers to any element and to *one past the end*, but you may not dereference the one-past-the-end pointer, and merely computing a pointer further out (or before the first element) is undefined behavior. Relational comparison (`<`) of pointers into unrelated objects gives an unspecified result; `std::less<T*>` is guaranteed to give a consistent total order if you need one, for example as a map key.

#### in code

**Rebinding that is not rebinding, and an overload that picks the wrong side.**

```cpp
#include <cstddef>
#include <cstdio>

void log_value(int)         { std::puts("int"); }
void log_value(const char*) { std::puts("const char*"); }

int main() {
    int a = 1, b = 2;
    int& r = a;
    r = b;                      // assigns 2 to a; r still refers to a
    b = 7;
    std::printf("%d %d\n", a, r);   // prints: 2 2

    log_value(0);               // prints: int
    log_value(nullptr);         // prints: const char*
    // log_value(NULL);         // GCC 12: error, ambiguous call. With NULL defined as 0
                                // (as some implementations do), it silently prints: int
}
```

The `NULL` line is the interesting one. Which behavior you get depends on the implementation's definition of `NULL`, so the same source can be an error on one toolchain and a silent wrong call on another. `nullptr` removes the question.

**Decay loses the size; pointer arithmetic has hard edges.**

```cpp
#include <cstddef>
#include <cstdint>

// BUG: the 64 is decoration; samples is const float*
float mean_bad(const float samples[64]) {
    const std::size_t n = sizeof(samples) / sizeof(samples[0]);  // 8 / 4 == 2 on x86-64
    float sum = 0;
    for (std::size_t i = 0; i < n; ++i) sum += samples[i];
    return sum / n;
}

// fixed: a reference to an array keeps N as part of the type
template <std::size_t N>
float mean(const float (&samples)[N]) {
    float sum = 0;
    for (float s : samples) sum += s;
    return sum / N;
}

void edges() {
    std::int16_t buf[256] = {};
    std::int16_t* end = buf + 256;   // fine: one past the end may be formed and compared
    // *end = 0;                     // UB: one-past-the-end must not be dereferenced
    // std::int16_t* p = buf + 257;  // UB: computing it is already undefined
    (void)end;
}
```

GCC warns about the first version (`-Wsizeof-array-argument`, on by default), and with a 64-element buffer whose first value is 64, our test printed 32 for `mean_bad` (two elements averaged) and 1 for the reference version. When the array size is not a compile-time constant, the classic pair is pointer plus length; C++20's `std::span` (day 31) packages that pair into one parameter.

**Logical constness with `mutable`.**

```cpp
#include <mutex>
#include <optional>
#include <utility>
#include <vector>

class Calibration {
public:
    explicit Calibration(std::vector<double> raw) : raw_(std::move(raw)) {}

    double offset() const {                      // same answer every call: logically const
        std::lock_guard<std::mutex> lock(mutex_);
        if (!cached_) cached_ = compute();       // allowed: cached_ is mutable
        return *cached_;
    }

private:
    double compute() const {
        double s = 0;
        for (double r : raw_) s += r;
        return s / raw_.size();
    }
    std::vector<double> raw_;
    mutable std::optional<double> cached_;
    mutable std::mutex mutex_;
};
```

The mutex is not decoration. The standard library guarantees that its own `const` member functions can be called concurrently on the same object, and generic code and your colleagues will assume the same of your types. A `mutable` member written from a `const` function breaks that assumption unless it is synchronized (data races are day 37). If you add `mutable`, you own the thread-safety of that member.

#### in practice

Here is the tracker API from the opening, written so the signature carries the contract:

```cpp
class Tracker {
public:
    void set_gate(double gate_m);                      // cheap type: by value
    void ingest(const DetectionBatch& batch);          // large, read-only: const&
    void predict(Track& track, double dt) const;       // in/out parameter: non-const&
    const Track* find(TrackId id) const;               // may be absent: pointer, nullptr if not found
    void add(Track track);                             // sink: take by value, move inside (day 10)
};
```

The guidelines behind it: pass cheap-to-copy types (roughly, a couple of machine words: integers, doubles, small structs, iterators, `std::string_view`) by value, because a reference forces an indirection and lets the compiler assume less about aliasing. Pass larger read-only objects by `const&`. Use a non-const reference for an in/out parameter, and prefer returning a value over an "out" parameter when you can. Use a pointer when "nothing" is a legitimate value. None of these says anything about ownership; that is what smart pointers in signatures are for (day 12). A `const Track*` from `find` is a borrowed view, valid until the tracker changes, and that limit belongs in a comment because the type cannot express it.

#### watch out for

`const` on a member function is shallow. It makes the *pointer member* const, not what it points to:

```cpp
#include <vector>

struct Joint { double angle = 0.0; };

class Arm {
public:
    void reset_view() const {
        joints_[0].angle = 0.0;     // compiles: joints_ is Joint* const here, joints are not const
        // spare_[0].angle = 0.0;   // error: spare_ is a const vector inside a const function
    }
private:
    Joint* joints_ = nullptr;
    std::vector<Joint> spare_;
};
```

A `std::vector` member propagates constness to its elements because its `operator[] const` returns `const T&`. A raw pointer member (and, for the same reason, a smart pointer member) does not. If an object conceptually owns what a pointer member points to, its `const` functions must enforce that themselves; the compiler will not.

#### the takeaway

Make the signature say it: value for cheap inputs, `const&` for large read-only ones, `&` for in/out, pointer for "might be nothing", and `nullptr` always; then treat `const` as a promise about observable state that you must keep, especially across threads.

#### optional challenge

Which numbered lines fail to compile? With those lines deleted, what does the program print?

```cpp
#include <iostream>

int main() {
    int a = 1, b = 2;
    const int* p = &a;
    int* const q = &a;
    const int& r = a;
    p = &b;   // (1)
    *q = 3;   // (2)
    *p = 4;   // (3)
    q = &b;   // (4)
    a = 5;    // (5)
    std::cout << r << '\n';
}
```

<details>
<summary>answer</summary>

Lines (3) and (4) fail. `p` is a pointer to `const int`, so `*p = 4` assigns through a read-only path; `q` is a `const` pointer, so it cannot be reseated. Line (1) is fine (the pointer itself is not const), and (2) is fine (the pointee of `q` is not const).

With them removed, it prints `5`. `r` is a read-only view of `a`, not a snapshot and not a promise that `a` never changes: `a` was set to 3 through `q` and then to 5 directly, and `r` sees the current value.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-05"></a>

### day 05: value categories without the headache

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days [03](#day-03), [04](#day-04)

#### the idea

Here is a function that looks like it moves a string into a container:

```cpp
void Registry::store(std::string&& name) {
    names_.push_back(name);   // copies
}
```

It copies. `name` has type "rvalue reference to `std::string`", but the *expression* `name` is an lvalue, so `push_back(const std::string&)` is chosen. The confusion comes from mixing up two independent properties that every expression has: a **type** and a **value category**. Once you keep them apart, overload resolution, moves, and copy elision stop being folklore.

#### understanding the concept

Value categories classify **expressions**, not variables or objects. Since C++11 there are three leaf categories, and C++17 sharpened what they mean:

```text
                 expression
                /          \
          glvalue           rvalue
         /       \         /      \
     lvalue        xvalue          prvalue
  (identity,     (identity,      (no identity:
   not movable)   movable)        a recipe for a value)
```

- An **lvalue** designates an object or function with an identity you can refer to again: a variable name (of *any* type, including `T&&`), `*p`, `a[i]`, `++x`, a call to a function returning `T&`, a string literal.
- An **xvalue** ("expiring") designates an object whose resources may be reused: `std::move(x)`, a call to a function returning `T&&`, a member access on an xvalue.
- A **prvalue** ("pure") has no identity yet. In C++17 it is not an object at all but an *initializer*: `42`, `x + 1`, `x++`, `Frame{}`, a call to a function returning by value.

A **glvalue** is an lvalue or xvalue (it has identity); an **rvalue** is an xvalue or prvalue (it may be moved from).

**Temporary materialization.** A prvalue becomes an actual object only when it has to: when a reference binds to it, when you access a member of it, or when it is discarded. At that point a temporary is created and the expression becomes an xvalue. Otherwise the prvalue directly initializes its final destination. That is the mechanism behind C++17's **guaranteed copy elision**: `T x = T{...};` and `return T{...};` initialize the target in place. No copy or move constructor is called, and none needs to exist.

Returning a *named* local is different. Named return value optimization (NRVO) lets the compiler construct the local directly in the return slot, but it is permitted, not required, and the copy or move constructor must still be accessible. When NRVO does not happen, a returned local is treated as an rvalue first, so it is moved if it can be.

**Binding rules** decide which overload wins:

| parameter | lvalue | xvalue | prvalue |
|---|---|---|---|
| `T&` | yes | no | no |
| `const T&` | yes | yes | yes |
| `T&&` | no | yes | yes |

When both `const T&` and `T&&` accept an rvalue, `T&&` is the better match. `std::move` does not move anything: it is a cast that turns its argument into an xvalue so that the `T&&` overload is selected. What the move then does is day 10's subject.

#### in code

**Predict which overload is called.**

```cpp
#include <cstdio>
#include <utility>

struct Frame { int id = 0; };

void take(Frame&)       { std::puts("Frame&"); }
void take(const Frame&) { std::puts("const Frame&"); }
void take(Frame&&)      { std::puts("Frame&&"); }

Frame make() { return Frame{}; }

int main() {
    Frame f;
    const Frame cf;
    Frame&& r = make();   // lifetime-extended temporary (day 03)

    take(f);              // 1
    take(cf);             // 2
    take(Frame{});        // 3
    take(make());         // 4
    take(std::move(f));   // 5
    take(r);              // 6
    take(std::move(cf));  // 7
}
```

<details>
<summary>output</summary>

```text
Frame&
const Frame&
Frame&&
Frame&&
Frame&&
Frame&
const Frame&
```

Lines 3 and 4 are prvalues, line 5 is an xvalue. Line 6 is the headline: `r` is declared as `Frame&&`, but the expression `r` is an lvalue, so `Frame&` wins. Line 7: `std::move(cf)` is an xvalue of type `const Frame`; `Frame&&` cannot bind to a const object, so `const Frame&` is chosen. Moving from a `const` object silently copies.

</details>

**`decltype` sees both the name and the expression.** `decltype(name)` gives the declared type of the entity. `decltype(expression)` encodes the category: `T&` for an lvalue, `T&&` for an xvalue, `T` for a prvalue. Parentheses turn a name into an expression:

```cpp
#include <type_traits>
#include <utility>

int x = 0;
static_assert(std::is_same_v<decltype(x), int>);                 // the entity
static_assert(std::is_same_v<decltype((x)), int&>);              // lvalue expression
static_assert(std::is_same_v<decltype(std::move(x)), int&&>);    // xvalue
static_assert(std::is_same_v<decltype(x + 1), int>);             // prvalue
static_assert(std::is_same_v<decltype(x++), int>);               // prvalue
static_assert(std::is_same_v<decltype(++x), int&>);              // lvalue

decltype(auto) value()  { int local = 1; return local; }    // returns int
decltype(auto) dangle() { int local = 1; return (local); }  // BUG: returns int&, dangling
```

The last pair is why `decltype(auto)` (C++14) deserves care: an innocent pair of parentheses changes the return type to a reference to a dead local. GCC flags it with `-Wreturn-local-addr`.

**Guaranteed elision versus NRVO.** A type that logs its special members:

```cpp
#include <cstdio>

struct Big {
    Big() { std::puts("ctor"); }
    Big(const Big&) { std::puts("copy"); }
    Big(Big&&) noexcept { std::puts("move"); }
};

Big make_prvalue() { return Big{}; }                     // guaranteed elision (C++17)
Big make_named()   { Big b; return b; }                  // NRVO: allowed, not required
Big make_either(bool c) { Big a, b; return c ? a : b; }  // not a plain name: copied

int main() {
    Big x = make_prvalue();   // prints: ctor
    Big y = make_named();     // prints: ctor (with NRVO), or ctor move (without)
    Big z = make_either(true);// prints: ctor ctor copy
    (void)x; (void)y; (void)z;
}
```

With GCC 12 at default settings we saw `ctor`, `ctor`, and `ctor ctor copy`. With `-fno-elide-constructors`, which disables optional elision, `make_named` printed `ctor move` while `make_prvalue` still printed only `ctor`: in C++17 that elision is part of the language, not an optimization. `make_either` copies because the conditional expression is an lvalue that is not simply the name of a local, so neither NRVO nor the implicit move applies. Write `if (c) return a; return b;` and each branch qualifies again.

#### in practice

Guaranteed elision changes what you can design, not only how fast it runs. Consider a handle to a memory-mapped device register block in a motor controller. Other components cache its address, so it must never move, and you want no "moved-from" state to reason about:

```cpp
#include <cstdint>

class RegisterBlock {
public:
    explicit RegisterBlock(std::uintptr_t base);
    RegisterBlock(const RegisterBlock&) = delete;
    RegisterBlock& operator=(const RegisterBlock&) = delete;
    // no move operations are declared: deleting copy suppresses them
};

RegisterBlock open_block(std::uintptr_t base) {
    validate(base);                // checks before construction
    return RegisterBlock{base};    // C++17: compiles; C++14: error, deleted copy constructor
}

RegisterBlock motor = open_block(0x4000'0000);   // constructed in place
```

Before C++17 you had to return such a type through `std::unique_ptr` or use a two-phase `init()`, both of which leak complexity into every caller. Now a factory function can return a non-movable type by value, which keeps the class invariant ("if it exists, it is pinned and valid") without a heap allocation. Note the limit: a factory that builds a named local and returns it still fails to compile for this type, because NRVO is optional and needs an accessible constructor.

#### watch out for

"If it has a name, it is an lvalue." Every function parameter, including one declared `T&&`, is an lvalue inside the function body. The fix in the opening example is to say what you mean:

```cpp
void Registry::store(std::string&& name) {
    names_.push_back(std::move(name));   // xvalue: selects push_back(std::string&&)
}
```

The rule exists for safety: a name can be used more than once, and silently moving on first use would leave later uses looking at a gutted object. Moving is therefore always an explicit decision at the point of last use. The opposite mistake is also common: `std::move` on a `const` object (line 7 above), or on an object you read again later.

#### the takeaway

Every expression has a type and a value category; overloads, moves, and elision are decided by the category, a named variable is always an lvalue, and since C++17 a prvalue is just an initializer that builds its object in place.

#### optional challenge

Classify each expression as lvalue, xvalue, or prvalue, given `int x = 0; int& f(); int g(); std::string s;`:
`x`, `x + 1`, `f()`, `g()`, `std::move(x)`, `"abc"`, `x++`, `++x`, `std::move(s).size()`.

<details>
<summary>answer</summary>

- `x`: lvalue (a name).
- `x + 1`: prvalue (built-in arithmetic yields a value).
- `f()`: lvalue (returns `int&`).
- `g()`: prvalue (returns by value).
- `std::move(x)`: xvalue (returns `int&&`).
- `"abc"`: lvalue. String literals are arrays with static storage duration, so they have identity; it is the only literal that is an lvalue.
- `x++`: prvalue (the old value, a copy). `++x`: lvalue (the variable itself, after incrementing).
- `std::move(s).size()`: prvalue. The object expression is an xvalue, but `size()` returns `std::size_t` by value, and the category of a call depends only on the function's return type.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-06"></a>

### day 06: undefined behavior and other things the standard won't promise

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 01 to 05

#### the idea

A telemetry service guards a counter with `if (total + delta < total) reset();`. It works in debug builds. In release builds the reset never fires, the counter goes negative, and dashboards show nonsense. Nobody touched the code; the optimizer read it more carefully than we did. Undefined behavior is not "the hardware does something weird". It is a contract: you promise certain things never happen, and the compiler is entitled to generate code that is only correct if you kept that promise.

#### understanding the concept

The standard describes three different kinds of looseness, and mixing them up leads to bad decisions:

| category | what the standard says | examples |
|---|---|---|
| implementation-defined | one of several outcomes; the implementation must document which | `sizeof(long)`, whether plain `char` is signed, the definition of `NULL`, right-shifting a negative `int` (until C++20) |
| unspecified | one of several outcomes; no documentation required, may vary call to call | order of evaluation of function arguments, whether identical string literals share storage, `<` on pointers to unrelated objects |
| undefined (UB) | no requirements at all | signed overflow, out-of-bounds access, use after free, reading an uninitialized `int`, data races |

Implementation-defined behavior is portable *with a check* (a `static_assert` on `sizeof`, for example). Unspecified behavior is safe as long as your program is correct for every allowed outcome. Undefined behavior is never safe, and the standard explicitly places no requirement on an execution that contains it, *not even on operations before the undefined one*. (Day 01's "ill-formed, no diagnostic required" is a fourth, compile-time cousin: the program is broken and nobody has to tell you.)

**Why the optimizer makes UB dangerous.** Optimizers transform code under the assumption that the program is valid. If signed overflow cannot happen, then `a + b < a` with `b > 0` is always false, and a loop counter `int i` that only increases can never wrap. If dereferencing a null pointer cannot happen, then a pointer that was dereferenced is non-null and a later null check is dead code. Each step is a sound deduction from the rules; the result is that a bug can delete your safety checks.

**The usual suspects**, and what catches them:

| UB | typical form | practical defense |
|---|---|---|
| signed overflow | `INT_MAX + 1`, `a * b` on promoted `uint16_t` (day 02) | check before computing; UBSan |
| out of bounds | `v[v.size()]`, pointer arithmetic past the end (day 04) | `.at()` in non-hot code, `-D_GLIBCXX_ASSERTIONS` (libstdc++), ASan |
| use after free / dangling | day 03's references to dead objects | ownership discipline (week 2), ASan |
| uninitialized read | `int n; return n;` (day 02) | default member initializers, `-Wuninitialized`, MSan (Clang), Valgrind |
| strict aliasing | `*reinterpret_cast<std::uint32_t*>(&f)` | `std::memcpy`, C++20 `std::bit_cast` |
| data race | two threads, one non-atomic object, at least one writer | mutexes and atomics (days 37, 40), TSan |
| modifying a string literal | `const_cast<char*>("abc")[0] = 'x'` | do not cast away `const` from data you do not own |

#### in code

**Signed overflow: the check that is not there.**

```cpp
#include <climits>

bool will_overflow(int a, int b) {     // intended for b > 0
    return a + b < a;                  // BUG: relies on signed overflow (UB)
}

bool will_overflow_fixed(int a, int b) {
    return b > 0 && a > INT_MAX - b;   // decide before doing the arithmetic
}
```

GCC 12 at `-O2` compiled `will_overflow` to a single shift that tests the sign of `b`: it rewrote `a + b < a` as `b < 0`, which is exactly what the expression means when overflow is impossible. The same reasoning shows up in loops. `for (int i = 1; i > 0; i *= 2) ++count;` printed `31` at `-O0` in our test and ran forever at `-O2`, because "a positive `int` doubled stays positive" is true in every program without UB. If you need wraparound, use unsigned types (where it is defined, modulo 2^N); if you need detection, check first, or use your compiler's checked-arithmetic builtins (`__builtin_add_overflow` in GCC and Clang, a non-standard extension).

**A null check deleted because of an earlier dereference.**

```cpp
struct Device { int status; };

int read_status(const Device* d) {
    int s = d->status;     // BUG: dereference before the check
    if (!d) return -1;     // GCC -O2: removed, since d cannot be null here
    return s;
}
```

At `-O0` our build contained the comparison against zero; at `-O2` the whole function was one load and a return. This exact pattern caused a Linux kernel vulnerability in 2009 (the TUN driver), and the kernel has built with `-fno-delete-null-pointer-checks` ever since. The fix is ordinary: check, then dereference.

**Type punning: three ways to read a float's bits** (the last one, commented out, needs C++20).

```cpp
#include <cstdint>
#include <cstring>

std::uint32_t bits_bad(float f) {
    return *reinterpret_cast<std::uint32_t*>(&f);  // BUG: UB, accesses a float as uint32_t
}

std::uint32_t bits_ok(float f) {                    // C++17
    static_assert(sizeof(float) == sizeof(std::uint32_t));
    std::uint32_t u;
    std::memcpy(&u, &f, sizeof u);                  // copies bytes: always allowed
    return u;
}

// C++20:
// #include <bit>
// std::uint32_t bits(float f) { return std::bit_cast<std::uint32_t>(f); }
```

The **strict aliasing rule** says you may access an object only through its own type (give or take signedness and cv-qualification) or through `char`, `unsigned char`, or `std::byte`. That lets the compiler assume a write through a `float*` cannot change an `int` it has cached in a register. `bits_bad` printed the right answer (`3f800000` for 1.0f) in our test, with a `-Wstrict-aliasing` warning at `-O2`. Correct output today is not evidence of a correct program. `std::memcpy` of a few bytes is generally compiled to a register move by mainstream optimizers; check the generated code if it matters. `std::bit_cast` (C++20) does the same thing as an expression and is `constexpr`.

#### in practice

Radar and telemetry code is full of the third pattern: a byte buffer arrives from a socket and gets cast to a header struct.

```cpp
#include <cstdint>
#include <cstring>

struct FrameHeader { std::uint16_t magic; std::uint16_t count; std::uint32_t seq; };

FrameHeader parse(const unsigned char* buf) {
    // BUG: return *reinterpret_cast<const FrameHeader*>(buf);
    //      aliasing violation, and buf + offset may be misaligned for uint32_t
    FrameHeader h;
    std::memcpy(&h, buf, sizeof h);   // FrameHeader is trivially copyable
    return h;
}
```

The cast version "works" on x86, which tolerates misaligned loads, and then faults on an ARM controller or gets miscompiled after an unrelated inlining change. The `memcpy` version is correct everywhere (byte order and padding are still your job: those are implementation-defined layout questions, not UB).

Because UB is invisible in testing until it is not, the defense is tooling in CI, not vigilance:

```sh
# compiler diagnostics on every build
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror ...

# a sanitizer job running the test suite (GCC or Clang)
g++ -std=c++17 -O1 -g -fno-omit-frame-pointer \
    -fsanitize=address,undefined -fno-sanitize-recover=undefined tests.cpp -o tests_asan

# data races need a separate build: ThreadSanitizer cannot be combined with ASan
g++ -std=c++17 -O1 -g -fsanitize=thread tests.cpp -o tests_tsan
```

Sanitizers cost run time and memory (ASan's own documentation cites a typical slowdown of about 2x), so they live in test jobs, not release builds. Sanitizers only see the paths your tests execute, which is one more argument for tests that exercise edge values.

#### watch out for

**Order of evaluation** is the area where folklore lags the standard. C++17 fixed several cases: in `a << b`, `a >> b`, `a[b]`, `a.b`, and `a->b` the left side is evaluated first, and in `a = b` (and `a += b`) the right side is evaluated first. So `std::cout << next() << next();` is now left to right, and `i = i++ + 1;` is well defined (it sets `i` to 1 when `i` starts at 0). GCC 12 still emits `-Wsequence-point` for that line even in C++17 mode, a stale warning worth knowing about.

Function arguments did not get an order. In `log_pair(next_id(), next_id())` the two calls are indeterminately sequenced: each runs completely before the other starts (which, since C++17, makes `f(i++, i++)` unspecified rather than undefined), but which one goes first is unspecified. Our GCC build printed `2 1`. Any code whose result depends on that order is a portability bug; give the values names on separate lines.

Two more misconceptions. `volatile` is for memory-mapped I/O and similar "every access is observable" cases; it makes nothing atomic and orders nothing between threads, so a race on a `volatile int` is still UB (atomics are day 40). And "it works on my machine" is the defining property of UB, not a defense against it.

#### the takeaway

Implementation-defined means "check the documentation", unspecified means "be correct for every outcome", and undefined means "the compiler assumes it never happens"; write code that never relies on UB, and let warnings and sanitizers find the places where you did by accident.

#### optional challenge

Classify each as well-defined, implementation-defined, unspecified, or undefined in C++17, and note any that changed in C++20.

1. `sizeof(int) == 4`
2. Which of `f(a(), b())`'s arguments is evaluated first
3. `int x = INT_MAX; ++x;`
4. `signed char c = 200;` (with 8-bit `signed char`)
5. `int y = -8 >> 1;`
6. `int i = 0; i = i++;`

<details>
<summary>answer</summary>

1. Implementation-defined. Only minimum ranges are guaranteed; `static_assert` it if your code depends on it.
2. Unspecified. Each argument is fully evaluated before the next begins, but the order may differ between compilers or even call sites.
3. Undefined: signed overflow.
4. Implementation-defined in C++17 (converting an out-of-range value to a signed type). Since C++20 it is defined as modulo 2^N, giving -56.
5. Implementation-defined in C++17 (right shift of a negative value; GCC documents an arithmetic shift, giving -4). C++20 requires two's complement and defines it as an arithmetic shift.
6. Well-defined since C++17: the right operand is sequenced before the assignment, so `i` ends up 0. In C++14 it was undefined.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-07"></a>

### day 07: week 1 review: the ground beneath your feet

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days 01 to 06

#### recap

| day | key idea |
|---|---|
| [01](#day-01) | The compiler sees one translation unit; the linker matches names. The ODR lets inline functions, classes, and templates be defined in many translation units only if every definition is identical, and violations need no diagnostic. C++17 `inline` variables give one object defined in a header. |
| [02](#day-02) | Braces reject narrowing but prefer `std::initializer_list` constructors. Automatic scalars start indeterminate; statics start zeroed. Arithmetic happens in at least `int`, and signed meets unsigned as unsigned. |
| [03](#day-03) | Scope belongs to names, lifetime to objects. Temporaries die at the end of the full-expression unless bound *directly* to a local reference. Cross-file static initialization order is unspecified; a function-local static fixes it. |
| [04](#day-04) | References are non-null, non-reseatable aliases; pointers are nullable and reseatable. `const` is a read-only view, shallow on pointer members, and an API contract that callers (and threads) rely on. |
| [05](#day-05) | Every expression has a type and a value category. Named variables are lvalues, even `T&&` ones. In C++17 a prvalue is an initializer, so returning one by value needs no copy or move constructor; NRVO is still optional. |
| [06](#day-06) | Implementation-defined (documented), unspecified (any allowed outcome), undefined (no requirements, and the optimizer assumes it never happens). Warnings and sanitizers are the practical defense. |

The thread through all six days: the standard defines an abstract machine, and most of what surprises engineers is the gap between that machine and the intuition "it's just memory and instructions".

#### review questions

1. A header is included by `planner.cpp` and `controller.cpp`. It contains `int g_cycle_count;`, `const double kDt = 0.01;`, and `inline double clamp01(double x) { ... }`. Which of these links, which does not, and what single C++17 change gives you one shared, mutable `g_cycle_count` without touching any `.cpp` file?

2. Predict the sizes, then explain the rule that decides each: `std::vector<int> a{10, 0};`, `std::vector<int> b(10, 0);`, `std::vector<int> c{};`. Why does the guideline "use braces everywhere" need an exception for containers?

3. One of these lines dangles and the other is fine. Explain the difference in terms of value categories and lifetime extension.

   ```cpp
   const Frame& f = make_frame();               // make_frame returns Frame by value
   const int&   m = std::max(lo(), hi());       // lo and hi return int by value
   ```

4. A colleague says "the order in which `f(read_header(), read_body())` evaluates its arguments is undefined behavior, just like signed overflow." What is right and wrong about that, and why does the difference matter in practice?

5. Looking ahead to week 2: a `LogFile` class opens a `FILE*` in its constructor. Using what you know about storage duration and destruction order (day 03), where should `fclose` go so that every path out of a scope, including an exception, closes the file? And what goes wrong if a `LogFile` is copied with the compiler-generated copy constructor?

#### mini exercise

This radar helper has three bugs that this week's lessons cover: one lifetime bug and two pieces of undefined behavior. One line that looks suspicious is actually fine. Find all four, then rewrite the function so it is correct.

```cpp
#include <vector>

struct Track { int id = 0; std::vector<float> ranges; };
std::vector<Track> load_tracks();

const float& latest_range(int id) {
    const auto& tracks = load_tracks();
    int index;
    for (std::size_t i = 0; i < tracks.size(); ++i)
        if (tracks[i].id == id) index = i;
    const Track& t = tracks[index];
    return t.ranges[t.ranges.size() - 1];
}
```

#### answers

<details>
<summary>answer 1: linkage and the ODR</summary>

`int g_cycle_count;` fails: it is a definition with external linkage in two translation units (`multiple definition of 'g_cycle_count'`). `const double kDt` links, because namespace-scope `const` without `inline` or `extern` has internal linkage: each file gets its own copy, which is fine for a value. `inline double clamp01` links, because inline functions may be defined in every translation unit as long as the definitions are identical. Changing the first line to `inline int g_cycle_count = 0;` makes it a C++17 inline variable: one object for the whole program, defined in the header.

</details>

<details>
<summary>answer 2: braces and containers</summary>

`a` has 2 elements (10 and 0), `b` has 10 zeros, `c` is empty. A non-empty braced list strongly prefers a `std::initializer_list` constructor when one is viable; empty braces mean value-initialization, which calls the default constructor. Braces are a good default because they reject narrowing and avoid the most vexing parse, but for any class with an `initializer_list` constructor (all standard containers, `std::string`) braces mean "these are the elements". Use parentheses for the sizing and fill constructors.

</details>

<details>
<summary>answer 3: lifetime extension</summary>

`make_frame()` is a prvalue. Binding it directly to `const Frame&` materializes a temporary and extends its lifetime to that of `f`, so `f` is fine. `std::max(lo(), hi())` is an lvalue of type `const int` (it returns `const int&`): the temporaries from `lo()` and `hi()` were bound to `std::max`'s reference parameters, which only keeps them alive until the end of the full-expression. Lifetime extension happens only when the reference binds to the temporary itself, never through a function returning a reference, so `m` dangles at the `;`. Writing `int m = std::max(lo(), hi());` copies the value in time.

</details>

<details>
<summary>answer 4: unspecified versus undefined</summary>

The order is *unspecified*, not undefined. Since C++17 each argument is evaluated completely before the next one starts (they are indeterminately sequenced), and either order is a valid execution. The program is correct if it is correct for both orders; GCC happens to evaluate right to left in our tests, and another compiler may not. Signed overflow is *undefined*: there is no valid execution, and the optimizer may delete code on the assumption it never happens. In practice, unspecified order is a portability and reproducibility bug (here: reading the body before the header from a stream), fixed by naming intermediate results; undefined behavior can corrupt unrelated logic and must be eliminated outright.

</details>

<details>
<summary>answer 5: preview of week 2</summary>

`fclose` belongs in the destructor. Automatic objects are destroyed when their scope exits by any route: normal flow, `return`, `break`, or stack unwinding from an exception. Putting the release in the destructor ties the resource's lifetime to the object's lifetime, which is RAII (day 08).

The compiler-generated copy constructor copies the `FILE*` member, so two `LogFile` objects hold the same handle and both destructors call `fclose` on it: a double close, which is undefined behavior. The class must either forbid copying (`= delete`) or define what a copy means, and since C++11 it can also support *moving* ownership of the handle from one object to another. Days 10 and 11 cover how, and day 05's value categories are what decide when a move is chosen.

</details>

<details>
<summary>mini exercise answer</summary>

- **Fine (the decoy):** `const auto& tracks = load_tracks();` binds a prvalue directly to a `const&`, so the vector lives until the function returns.
- **Bug 1, UB (uninitialized read):** if no track has the requested `id`, `index` is never assigned, and `tracks[index]` reads an indeterminate value. GCC 12 at `-O2` warned `'index' may be used uninitialized`; it was the only one of the three bugs any warning caught.
- **Bug 2, UB (out of bounds):** if the track has no ranges, `t.ranges.size() - 1` wraps to the largest `std::size_t` (well-defined unsigned arithmetic, day 02), and indexing with it is out of bounds.
- **Bug 3, lifetime:** the returned reference points into `tracks`, whose lifetime-extended vector is destroyed when the function returns. Every caller receives a dangling reference. Lifetime extension lasts as long as the *reference variable*, which is a local.

A corrected version returns a value and makes "not found" explicit:

```cpp
#include <optional>
#include <vector>

std::optional<float> latest_range(int id) {
    const auto tracks = load_tracks();        // owned locally, by value
    for (const Track& t : tracks)
        if (t.id == id && !t.ranges.empty())
            return t.ranges.back();           // copy the float out while tracks is alive
    return std::nullopt;                      // not found, or no ranges yet
}
```

With test data `{1, {10, 12.5}}` and `{2, {}}`, ids 1, 2, and 3 gave `12.5`, empty, and empty. `std::optional` gets its own lesson on day 24; a `bool` plus an out-parameter would also work, at the cost of a clumsier call site. If loading all tracks is expensive, the real fix is an API change: the caller should own the track list and pass it in by `const&`, so this function no longer creates the data it needs to reference.

</details>

#### connections

This week was about what the language actually guarantees, and every later week leans on it. Week 2 turns day 03's lifetime rules into a design technique: RAII (day 08) puts resource release in destructors because destruction order is deterministic, and constructors (day 09) are where day 02's initialization rules meet class invariants. Day 05's value categories are the entire mechanism behind move semantics (day 10) and the rule of zero and five (day 11), and day 04's "pointers say nothing about ownership" sets up smart pointers in interfaces (day 12).

Further out: day 01's ODR and header model is what C++20 modules (day 48) try to replace; day 06's data races and `volatile` misconception return with mutexes and atomics (days 37 and 40); `std::bit_cast` returns in the C++20 tour (day 34), and `constinit` (day 33) offers another answer to day 03's initialization order fiasco; and the "measure, use sanitizers, trust tools over intuition" habit becomes the whole of week 8.

[back to table of contents](#table-of-contents)

---

<a id="week-2"></a>

## week 2: ownership and object-oriented c++

Who owns what, for how long, and how objects relate to each other.

<a id="day-08"></a>

### day 08: RAII: let scope do the cleanup

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days 03, 06

#### the idea

Here is a function that reads a calibration header from a file. It has three exits, and every one of them must remember `fclose`. Six months later someone adds a call that can throw, and now there is a fourth exit that nobody wrote down.

That is the whole problem RAII solves. Cleanup that depends on every author remembering every exit path will eventually be forgotten. Cleanup that the language performs whenever a scope ends cannot be forgotten, because nobody has to remember it.

#### understanding the concept

RAII (resource acquisition is initialization; the name is famously bad) means: tie a resource to the lifetime of an object. The constructor acquires the resource, or throws if it cannot. The destructor releases it. You then lean on the lifetime rules from day 03: an object with automatic storage duration is destroyed when control leaves its scope, in reverse order of construction, however control leaves.

"However control leaves" is the important part. Normal fall-through, `return`, `break`, `continue`, `goto` out of a block, and an exception propagating to a handler all run the destructors of the automatic objects being left. During exception propagation this is called stack unwinding: each frame between the `throw` and the matching `catch` is torn down, destructors included.

A few exits do not run destructors, and you should know them:

- `std::exit` destroys static objects but not the automatic objects on the stack.
- `std::abort`, `std::_Exit`, a crash, and `kill -9` destroy nothing.
- If an exception is never caught, `std::terminate` is called, and **whether the stack is unwound first is implementation-defined**. GCC and Clang typically do not unwind in that case, so your destructors may not run.

The deeper idea is an invariant: **if the object exists, the resource is valid**. A `File` object that exists holds an open file. There is no "not yet opened" or "already closed" state for every caller to check. That is encapsulation in its most useful form: the class owns a rule, and no caller can break it.

Destructors are implicitly `noexcept` (since C++11), unless a base or member has a potentially-throwing destructor. If an exception escapes a `noexcept` destructor, `std::terminate` is called. Even a destructor explicitly marked `noexcept(false)` that throws while the stack is already unwinding because of another exception calls `std::terminate`. Treat "destructors do not throw" as a hard rule.

#### in code

First, the naive version. It is correct today and fragile tomorrow.

```cpp
#include <cstdio>
#include <optional>

struct Header { char magic[4]; unsigned version; };

std::optional<Header> read_header(const char* path) {
    std::FILE* f = std::fopen(path, "rb");
    if (!f) return std::nullopt;

    Header h{};
    if (std::fread(&h, sizeof h, 1, f) != 1) {
        std::fclose(f);                  // exit 1: remembered
        return std::nullopt;
    }
    if (h.version > 3) {
        return std::nullopt;             // BUG: exit 2 leaks the FILE*
    }
    validate(h);                         // BUG: if this throws, f leaks too
    std::fclose(f);
    return h;
}
```

The RAII version moves the cleanup into a type. You rarely need a hand-written class for a C handle: `std::unique_ptr` with a custom deleter is already a general RAII wrapper.

```cpp
#include <cstdio>
#include <memory>
#include <optional>

struct FileCloser {
    void operator()(std::FILE* f) const noexcept { std::fclose(f); }
};
using FilePtr = std::unique_ptr<std::FILE, FileCloser>;

std::optional<Header> read_header(const char* path) {
    FilePtr f{std::fopen(path, "rb")};
    if (!f) return std::nullopt;

    Header h{};
    if (std::fread(&h, sizeof h, 1, f.get()) != 1) return std::nullopt;
    if (h.version > 3) return std::nullopt;
    validate(h);                         // may throw: f is still closed
    return h;                            // every path closes exactly once
}
```

Two details. `unique_ptr` never calls the deleter on a null pointer, so a failed `fopen` is handled for free. And the deleter is a function object rather than `&std::fclose`: since C++20, forming a pointer to most standard library functions is unspecified (possibly ill-formed), and an empty function object also lets the `unique_ptr` stay pointer-sized (more on that on day 12).

You already use this pattern every day: `std::lock_guard` locks in its constructor and unlocks in its destructor, `std::vector` frees its buffer, `std::ifstream` closes its file. For one-off cleanup that does not deserve its own type, a scope guard turns any callable into a destructor. C++17 class template argument deduction (CTAD) means you never spell out the lambda's type:

```cpp
#include <cstdio>
#include <utility>

template <typename F>
class ScopeGuard {
public:
    explicit ScopeGuard(F f) : f_(std::move(f)) {}
    ~ScopeGuard() { if (active_) f_(); }
    void dismiss() noexcept { active_ = false; }

    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;
private:
    F f_;
    bool active_ = true;
};

int main() {
    ScopeGuard a{[] { std::puts("release a"); }};   // CTAD deduces F
    ScopeGuard b{[] { std::puts("release b"); }};
    ScopeGuard c{[] { std::puts("rollback c"); }};
    c.dismiss();                                    // commit: skip rollback
    std::puts("body done");
}
// prints:
// body done
// release b
// release a
```

Reverse order of construction, as day 03 promised. `dismiss` gives you the commit-or-rollback shape: arm a rollback before a multi-step operation and disarm it once the last step succeeds. The Library Fundamentals TS has `scope_exit`, `scope_fail`, and `scope_success`, but they are not in the C++17 or C++20 standard library, so most codebases carry a guard like this one.

#### in practice

A joint controller enables motor torque before running a trajectory. If the trajectory code throws (a planner exception, a bad sensor reading, an allocation failure), the motors must not be left energized.

```cpp
class TorqueEnable {
public:
    explicit TorqueEnable(MotorBus& bus) : bus_(bus) { bus_.enable_all(); }
    ~TorqueEnable() { bus_.disable_all(); }   // must not throw
    TorqueEnable(const TorqueEnable&) = delete;
    TorqueEnable& operator=(const TorqueEnable&) = delete;
private:
    MotorBus& bus_;
};

void run_trajectory(MotorBus& bus, const Trajectory& t) {
    TorqueEnable power{bus};
    for (const auto& setpoint : t) step(bus, setpoint);   // may throw
}   // torque off on every exit path that unwinds
```

Notice what RAII does not cover. If the process segfaults, is killed, or hits an uncaught exception on an implementation that does not unwind, `disable_all` never runs. For anything safety-relevant, RAII is the software layer; a hardware watchdog that cuts torque when the heartbeat stops is the layer below it. Good engineering uses both, and knows which failure each one handles.

Copying is deleted here deliberately. Two `TorqueEnable` objects for one bus would disable it twice, the first time too early. Whether an RAII type should be copyable, movable, or neither is a design decision about ownership; days 10 and 11 cover how to make it.

#### watch out for

**Release can fail, and a destructor cannot report it.** `fclose` on a file you wrote may flush buffered data and fail (disk full, network filesystem gone). The `FileCloser` above silently drops that error. For read-only handles that is fine. For writes, give the class an explicit `close()` that returns or throws an error, call it on the success path, and let the destructor be the fallback that cleans up quietly (perhaps logging) when an earlier failure already happened.

**An unnamed guard guards nothing.**

```cpp
std::lock_guard<std::mutex>{mtx_};           // BUG: temporary, unlocked at the ;
std::lock_guard<std::mutex> lock{mtx_};      // held until end of scope
```

The first line creates a temporary that dies at the end of the full-expression (day 03), so the critical section is empty. GCC 12 compiles it without a word under `-Wall -Wextra`. The same applies to `ScopeGuard{...};`. Always give guards a name.

#### the takeaway

If something must happen when a scope ends, put it in a destructor. Then every exit path, including the ones someone adds next year, gets it for free.

#### optional challenge

Predict the output, then predict what changes if you delete the `try`/`catch` in `main`.

```cpp
#include <cstdio>
#include <stdexcept>

struct Noisy {
    const char* name;
    ~Noisy() { std::puts(name); }
};

void work() {
    Noisy a{"a"};
    Noisy b{"b"};
    throw std::runtime_error("sensor timeout");
}

int main() {
    try { work(); }
    catch (const std::exception& e) { std::puts(e.what()); }
}
```

<details>
<summary>answer</summary>

With the handler, the stack unwinds to `main` before the `catch` body runs, so you see `b`, `a`, then `sensor timeout`. Destruction is in reverse order of construction, and the destructors run before the handler.

Without the handler, no matching `catch` exists, so `std::terminate` is called. Whether `b` and `a` are destroyed first is implementation-defined. With GCC on Linux and MinGW you typically see neither line, just the terminate message and an abort. This is one reason long-running services catch exceptions at the top of `main` and at the top of every thread function: it guarantees that unwinding, and therefore your RAII cleanup, actually happens.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-09"></a>

### day 09: constructors, destructors, and the object lifecycle

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 02, 03, 08

#### the idea

A colleague reorders two members in a header to "group related fields". Nothing else changes. The next build passes, the unit tests pass, and a sample buffer in the radar front end is now sized from garbage. The constructor's initializer list looked perfectly correct; it was the class declaration that changed.

Constructors are where invariants are born, and the rules that govern them (order, partial construction, dispatch) are stricter and less intuitive than they look.

#### understanding the concept

A constructor's job is to turn raw storage into an object whose invariant holds. Day 08 put that in RAII terms: if the object exists, the resource is valid. The mechanics:

- **Members are initialized before the body runs.** Anything you do not name in the member initializer list is default-initialized (or uses its default member initializer). Assigning in the body is therefore a second step: construct, then overwrite. For `const` members, references, and types without a default constructor, there is no second step; the initializer list is the only option.
- **Order is fixed by the class definition, not by the initializer list.** For a non-virtual hierarchy: direct bases in declaration order, then non-static members in declaration order, then the constructor body. (Virtual bases come first of all, constructed by the most derived class.) Destruction is the exact reverse. The order you write in the initializer list is ignored, which is why GCC and Clang have `-Wreorder` (enabled by `-Wall`).
- **During construction and destruction, an object is only as derived as the constructor or destructor currently running.** Inside `Base::Base()`, the derived members do not exist yet, so a virtual call dispatches to `Base`'s version, not the override. Calling a *pure* virtual function this way is undefined behavior.
- **If a constructor throws, the object never existed.** Its destructor does not run. Every base and member that *was* fully constructed is destroyed, in reverse order. Raw resources acquired in the body are on their own.

Two conveniences round it out. Default member initializers (`float gain_ = 1.0f;`) give every constructor a sensible starting value. Delegating constructors (`Window() : Window(256) {}`) let one constructor reuse another's work.

#### in code

First, the reorder bug and its real fix.

```cpp
#include <cstddef>
#include <vector>

class SampleWindow {
public:
    explicit SampleWindow(std::size_t n)
        : size_(n), samples_(size_) {}   // BUG: samples_ is initialized first
private:
    std::vector<float> samples_;          // declared first, so constructed first
    std::size_t size_;
};
```

`samples_(size_)` reads `size_` before it is initialized. That is a read of an indeterminate value: undefined behavior, which in practice means a vector of some arbitrary size, or a `std::length_error`, or a huge allocation. GCC 12 reports it twice under `-Wall`: `-Wreorder` for the list order and `-Wuninitialized` ("member is used uninitialized"). Matching the list order to the declaration silences the warnings, but the better fix removes the duplicated state:

```cpp
class SampleWindow {
public:
    explicit SampleWindow(std::size_t n) : samples_(n) {}
    SampleWindow() : SampleWindow(default_size) {}   // delegating constructor
    std::size_t size() const { return samples_.size(); }
private:
    static constexpr std::size_t default_size = 256;
    std::vector<float> samples_;
    float gain_ = 1.0f;                              // default member initializer
};
```

A `size_` that must always equal `samples_.size()` is an invariant you have to maintain by hand. Deleting it deletes the bug class.

Second, predict the output. This one shows construction order and the "only as derived as the running constructor" rule.

```cpp
#include <cstdio>

struct Part {
    const char* n;
    explicit Part(const char* name) : n(name) { std::printf("part %s\n", n); }
    ~Part() { std::printf("~part %s\n", n); }
};

struct Sensor {
    Sensor() { std::puts("Sensor()"); describe(); }
    virtual ~Sensor() { std::puts("~Sensor()"); describe(); }
    virtual void describe() const { std::puts("  I am a Sensor"); }
};

struct Lidar : Sensor {
    Part optics{"optics"};
    Part driver{"driver"};
    Lidar() { std::puts("Lidar()"); describe(); }
    ~Lidar() override { std::puts("~Lidar()"); }
    void describe() const override { std::puts("  I am a Lidar"); }
};

int main() { Lidar l; }
```

```text
Sensor()
  I am a Sensor
part optics
part driver
Lidar()
  I am a Lidar
~Lidar()
~part driver
~part optics
~Sensor()
  I am a Sensor
```

The `Sensor` constructor cannot call `Lidar::describe`: `optics` and `driver` have not been constructed yet, and an override is entitled to use them. The same logic applies in reverse in `~Sensor`. If a base class needs derived-specific setup, it cannot get it through a virtual call in its constructor; use a factory function that constructs and then initializes, or pass the information into the base constructor.

Third, partial construction. A class that owns two raw resources leaks the first when acquiring the second fails.

```cpp
class Pipeline {                            // BUG: leaks buf_ if open_device throws
public:
    Pipeline() : buf_(new float[4096]), dev_(open_device()) {}
    ~Pipeline() { close_device(dev_); delete[] buf_; }   // never runs if ctor throws
private:
    float* buf_;
    Device* dev_;
};

class Pipeline2 {                           // fixed: each member cleans up itself
    std::unique_ptr<float[]> buf_ = std::make_unique<float[]>(4096);
    DevicePtr dev_{open_device()};          // unique_ptr with a closing deleter
};
```

In `Pipeline2`, if `open_device` throws, `buf_` is a fully constructed member and is destroyed during unwinding. There is no user-written destructor at all. This is the seed of the rule of zero (day 11). One aside: `make_unique<float[]>(n)` value-initializes, so it zeroes the buffer; C++20's `std::make_unique_for_overwrite` skips that when you are about to fill it anyway.

#### in practice

A radar range gate is only meaningful when `0 <= min < max`. Put that check in exactly one place:

```cpp
#include <stdexcept>

class RangeGate {
public:
    RangeGate(double min_m, double max_m) : min_(min_m), max_(max_m) {
        if (!(min_ >= 0.0 && min_ < max_))        // also rejects NaN
            throw std::invalid_argument("RangeGate: need 0 <= min < max");
    }
    bool contains(double r) const { return r >= min_ && r < max_; }
private:
    double min_, max_;
};
```

Every member function can now assume the invariant, and there is no `is_valid()` for callers to forget. In a codebase built with exceptions disabled, the same idea becomes a private constructor plus `static std::optional<RangeGate> make(double, double)`: the invariant still lives in one place, and the failure is still impossible to ignore.

Contrast `struct Detection { double range_m, azimuth_rad, snr_db; };`. Any combination of values is a valid detection, so there is nothing to protect: a plain aggregate with public members is the honest design. The Core Guidelines put it as "use `class` if the class has an invariant; use `struct` if the data members can vary independently." Wrapping independent fields in getters and setters adds ceremony without adding safety.

#### watch out for

A single-argument constructor that is not `explicit` is also an implicit conversion.

```cpp
struct Timeout {
    Timeout(int ms) : ms(ms) {}            // implicit: int converts to Timeout
    int ms;
};
void arm_watchdog(Timeout t);

arm_watchdog(5);                           // compiles. 5 ms? 5 s? 5 retries?
```

Mark it `explicit` and the call site must say `arm_watchdog(Timeout{5})`; copy-list-initialization (`Timeout t = {5};`) is rejected too. Make single-argument constructors `explicit` by default, and drop it only when the conversion is genuinely lossless and unsurprising (`std::string` from a string literal, a wider duration from a narrower one). The same applies to conversion operators: write `explicit operator bool()`, which still works in `if (x)` but not in `int n = x;`. Better still, for durations, use `std::chrono` and let the type carry the unit.

#### the takeaway

Members are built in declaration order, the body runs last, and a constructor that throws leaves no object behind. Design so that each member cleans up after itself, and those rules work for you instead of against you.

#### optional challenge

The target constructor finishes, and then the delegating constructor's body throws. Does `~Probe()` run?

```cpp
struct Probe {
    explicit Probe(int id) { std::printf("Probe(%d)\n", id); }
    Probe() : Probe(0) { throw std::runtime_error("calibration failed"); }
    ~Probe() { std::puts("~Probe()"); }
};
```

<details>
<summary>answer</summary>

Yes. Once a delegating constructor's target constructor completes, the object counts as constructed, so if the delegating constructor's body then exits via an exception, the destructor is invoked. Constructing `Probe p;` inside a `try` prints `Probe(0)`, then `~Probe()`, then whatever the handler prints. This is the one case where a constructor throwing still runs the class's own destructor, and it is why a target constructor should leave the object fully valid: the destructor may have to clean it up.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-10"></a>

### day 10: copy and move semantics

**reading time:** about 10 minutes · **standard:** C++17 · **builds on:** days 05, 08, 09

#### the idea

`std::move` does not move anything. It compiles to no instructions at all. Whether a move happens, and what it costs, is decided entirely by which constructor or assignment operator overload resolution picks afterwards, and that is code you (or the compiler) wrote.

Once you see moves as "an overload that is allowed to steal, selected by value category", the surprising cases stop being surprising: the `std::move` that copies, the vector that copies when you expected moves, and the `return std::move(x)` that makes code slower.

#### understanding the concept

Copying gives the destination its own independent value; the source is untouched. For a type that owns a resource through a pointer, that means duplicating the resource (a deep copy). Copying just the pointer (a shallow copy) leaves two owners, and day 08's destructor will release the same resource twice.

Moving gives the destination the source's value and permits the source to be left in a cheaper, emptier state. For a pointer-owning type that means taking the pointer and nulling the source: O(1), no allocation, usually no way to fail.

The selection is plain overload resolution on day 05's value categories. A `T&&` parameter binds to rvalues (prvalues and xvalues); a `const T&` binds to anything. Given both, an rvalue argument prefers `T&&`. And `std::move` is just a cast that turns an lvalue into an xvalue:

```cpp
template <typename T>
constexpr std::remove_reference_t<T>&& move(T&& t) noexcept {
    return static_cast<std::remove_reference_t<T>&&>(t);
}
```

What state does the source end up in? For standard library types the rule is "valid but unspecified": the object still satisfies its invariants, so you can destroy it, assign to it, or call functions without preconditions (`size()`, `clear()`), but you must not assume a particular value. A moved-from `std::vector` is empty on every mainstream implementation, but that is not a guarantee you should build on. For your own types, the moved-from state is part of your contract: decide it and document it.

#### in code

The bug that motivates all of this. A class owns a raw buffer and relies on the implicitly generated copy:

```cpp
class Frame {
public:
    explicit Frame(std::size_t n) : size_(n), data_(new float[n]{}) {}
    ~Frame() { delete[] data_; }
private:
    std::size_t size_;
    float* data_;
};

void f() {
    Frame a(1024);
    Frame b = a;        // BUG: implicit copy duplicates the pointer
}                       // double delete[]: undefined behavior
```

The fix spells out what copying and moving mean for this resource:

```cpp
#include <algorithm>
#include <cstddef>
#include <utility>

class Buffer {
public:
    explicit Buffer(std::size_t n) : size_(n), data_(new float[n]{}) {}
    ~Buffer() { delete[] data_; }

    Buffer(const Buffer& o) : size_(o.size_), data_(new float[o.size_]) {
        std::copy(o.data_, o.data_ + size_, data_);           // deep copy
    }
    Buffer& operator=(const Buffer& o) {
        if (this != &o) {
            float* fresh = new float[o.size_];                // may throw: do it first
            std::copy(o.data_, o.data_ + o.size_, fresh);
            delete[] data_;                                   // only now touch *this
            data_ = fresh;
            size_ = o.size_;
        }
        return *this;
    }

    Buffer(Buffer&& o) noexcept                               // steal, leave o empty
        : size_(std::exchange(o.size_, 0)), data_(std::exchange(o.data_, nullptr)) {}
    Buffer& operator=(Buffer&& o) noexcept {
        if (this != &o) {                                     // survive b = std::move(b)
            delete[] data_;
            size_ = std::exchange(o.size_, 0);
            data_ = std::exchange(o.data_, nullptr);
        }
        return *this;
    }

    std::size_t size() const noexcept { return size_; }       // moved-from: size() == 0
private:
    std::size_t size_;
    float* data_;
};
```

Three details carry the weight. The copy assignment allocates before it releases, so if `new` throws, `*this` is unchanged (the strong guarantee, day 20). The move assignment checks for self-assignment because without the check, `b = std::move(b)` would delete the buffer and then adopt the dangling pointer. And `std::exchange` keeps "take the value, leave a replacement" on one line, which makes the moved-from contract visible.

That is a lot of code for one pointer, and it is easy to get subtly wrong. Day 11 shows how to make almost all of it disappear.

Now predict the output. `Track` has a hand-written move constructor that is not `noexcept`:

```cpp
#include <cstdio>
#include <string>
#include <vector>

struct Track {
    std::string id;
    explicit Track(std::string s) : id(std::move(s)) {}
    Track(const Track& o) : id(o.id) { std::puts("copy"); }
    Track(Track&& o) : id(std::move(o.id)) { std::puts("move"); }   // not noexcept
};

int main() {
    std::vector<Track> tracks;
    tracks.reserve(1);
    tracks.emplace_back("T-001");
    tracks.emplace_back("T-002");   // exceeds capacity: reallocates
}
```

It prints `copy`. When `push_back` or `emplace_back` reallocates, `std::vector` promises the strong guarantee: if an exception escapes, the vector is unchanged. Moving the old elements to the new block would gut them, so a move that throws halfway through leaves no way back. The vector therefore uses `std::move_if_noexcept`: it moves only if the move constructor is `noexcept` (or the type cannot be copied at all, in which case the effects of a throwing move are unspecified). Add `noexcept` to the move constructor and the program prints `move`.

Implicitly generated and `= default` move constructors are `noexcept` automatically when every member's move is. The trap is the hand-written one.

#### in practice

A radar processing chain passes large frames between stages. A stage that keeps what it receives takes the frame by value (a "sink" parameter) and moves it into place:

```cpp
class Tracker {
public:
    void submit(RangeDopplerFrame frame) { pending_.push_back(std::move(frame)); }
private:
    std::vector<RangeDopplerFrame> pending_;
};

RangeDopplerFrame acquire(Receiver& rx) {
    RangeDopplerFrame f = rx.read_frame();
    apply_window(f);
    return f;                        // not std::move(f)
}

void loop(Receiver& rx, Tracker& tracker) {
    RangeDopplerFrame frame = acquire(rx);
    tracker.submit(std::move(frame));  // caller opts in to giving it away
    frame = acquire(rx);               // assigning to a moved-from object is fine
}
```

The signature tells the story: by-value parameter, caller writes `std::move` when it is done with the object, copies only when it explicitly keeps one. Inside `acquire`, `return f;` either elides the copy entirely (NRVO, optional but routinely done) or, failing that, treats `f` as an rvalue and moves. Writing `return std::move(f);` changes the operand from a plain name to an xvalue, which disqualifies NRVO, so you trade a possibly free return for a guaranteed move. GCC 12 flags it under `-Wall` with `-Wpessimizing-move`. Use an explicit `std::move` in a `return` only when returning something that is not a plain local or parameter, such as a data member.

#### watch out for

**`std::move` on a `const` object copies, silently.**

```cpp
const std::string config = load_config();
std::string owned = std::move(config);   // copies: const std::string&& binds to const&
```

`std::move(config)` produces `const std::string&&`. The move constructor wants `std::string&&`, which cannot bind to a const object, so overload resolution falls back to the copy constructor. No warning, no error, just a copy. The same applies to `const` data members: a class with a `const std::vector` member cannot be moved efficiently, because that member is copied every time. Declare locals `const` freely, but not ones you intend to move from, and think twice about `const` members in types that will be moved.

**Use after move is legal and still a bug.** Reading `frame.size()` after `submit(std::move(frame))` is well-defined for a standard type and almost always a logic error. `clang-tidy`'s `bugprone-use-after-move` check finds most of these.

#### the takeaway

`std::move` only grants permission; the move constructor does the work, and `noexcept` decides whether containers will trust it.

#### optional challenge

`Buffer`'s copy assignment uses `if (this != &o)`. Is the check required for correctness, or only an optimization? What about the move assignment?

<details>
<summary>answer</summary>

For the copy assignment it is only an optimization. Because it allocates and copies into `fresh` before deleting the old buffer, self-assignment copies the data into a new block, frees the old one, and ends up with an equal value. The check just skips a pointless allocation.

For the move assignment it is required for correctness as written. Without it, `b = std::move(b)` runs `delete[] data_`, and then `data_ = std::exchange(o.data_, nullptr)` reads the freed pointer out of the same object (briefly setting it to null) and stores it straight back. `b` now holds a dangling pointer with its old size, and its destructor will `delete[]` the block a second time: undefined behavior. Self-move is rare in direct code but appears through aliasing: `std::swap(x, x)` performs `x = std::move(x)` internally, and so does `v[i] = std::move(v[j])` when `i == j`.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-11"></a>

### day 11: the rule of zero, three, and five

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 08, 09, 10

#### the idea

Day 10's `Buffer` needed about 35 lines of copy and move code to manage one pointer correctly, and every line was a chance to get it wrong. Most classes in a healthy codebase have none of those lines. The rule of zero is not "be lazy"; it is a claim about design: managing a resource is one job, and a class that does that job should do nothing else.

#### understanding the concept

There are six special member functions: the default constructor, the destructor, the copy constructor, copy assignment, the move constructor, and move assignment. The compiler declares the ones you do not, following rules that are worth having in front of you once:

| you declare | default ctor | destructor | copy ctor | copy assign | move ctor | move assign |
|---|---|---|---|---|---|---|
| nothing | defaulted | defaulted | defaulted | defaulted | defaulted | defaulted |
| another constructor | not declared | defaulted | defaulted | defaulted | defaulted | defaulted |
| destructor | defaulted | yours | defaulted (deprecated) | defaulted (deprecated) | not declared | not declared |
| copy ctor | not declared | defaulted | yours | defaulted (deprecated) | not declared | not declared |
| copy assign | defaulted | defaulted | defaulted (deprecated) | yours | not declared | not declared |
| move ctor | not declared | defaulted | deleted | deleted | yours | not declared |
| move assign | defaulted | defaulted | deleted | deleted | not declared | yours |

Three things in that table matter in practice.

- **"Declare" includes `= default` and `= delete`.** Writing `~T() = default;` counts as declaring a destructor and suppresses the implicit moves.
- **"Not declared" is not "deleted".** If there is no move constructor, an rvalue argument simply binds to the copy constructor's `const T&` parameter. Moves silently become copies, and `std::is_move_constructible_v<T>` still reports `true`.
- **"Defaulted" can still mean deleted.** A defaulted copy constructor is defined as deleted if some member cannot be copied. A class with a `std::unique_ptr` member is move-only without you writing anything.

From those rules come three guidelines:

- **Rule of three** (C++98): if you need a custom destructor, copy constructor, or copy assignment, you almost certainly need all three, because the custom one exists to manage a resource the defaults would mishandle.
- **Rule of five** (C++11): same, plus the two move operations, since declaring any of the three suppresses the implicit moves.
- **Rule of zero**: write classes that need none of them, by composing members that already manage themselves: `std::vector`, `std::string`, `std::unique_ptr`, and the few RAII types of your own.

#### in code

Day 10's `Buffer`, refactored to the rule of zero:

```cpp
#include <cstddef>
#include <vector>

class Buffer {
public:
    explicit Buffer(std::size_t n) : data_(n) {}
    std::size_t size() const noexcept { return data_.size(); }
    float* data() noexcept { return data_.data(); }
    const float* data() const noexcept { return data_.data(); }
private:
    std::vector<float> data_;
};
```

Copy is a deep copy, move steals the buffer, destruction frees it, and the move constructor is `noexcept` because `std::vector`'s is, so day 10's reallocation trap cannot happen. Copy assignment is arguably better than the hand-written one, since `std::vector` can reuse existing capacity instead of always allocating.

One thing did change: the moved-from contract. The hand-written `Buffer` promised `size() == 0` after a move. This one inherits `std::vector`'s "valid but unspecified". If callers relied on the old promise, that is an API change, and it deserves a line in the review. If you want a move-only buffer instead, swap the member for `std::unique_ptr<float[]>` plus a size: copying is then implicitly deleted, and the class still declares no special members.

When you do write the special members, copy-and-swap is the classic way to get assignment right with little code:

```cpp
#include <algorithm>
#include <cstddef>
#include <utility>

class Buffer5 {                                   // rule of five, by hand
public:
    explicit Buffer5(std::size_t n) : size_(n), data_(new float[n]{}) {}
    ~Buffer5() { delete[] data_; }
    Buffer5(const Buffer5& o) : size_(o.size_), data_(new float[o.size_]) {
        std::copy(o.data_, o.data_ + size_, data_);
    }
    Buffer5(Buffer5&& o) noexcept
        : size_(std::exchange(o.size_, 0)), data_(std::exchange(o.data_, nullptr)) {}

    Buffer5& operator=(Buffer5 other) noexcept {  // one operator for copy and move
        swap(*this, other);
        return *this;
    }                                             // other's destructor frees the old buffer
    friend void swap(Buffer5& a, Buffer5& b) noexcept {
        std::swap(a.size_, b.size_);
        std::swap(a.data_, b.data_);
    }
private:
    std::size_t size_;
    float* data_;
};
```

The parameter is taken by value, so the copy (from an lvalue) or move (from an rvalue) happens at the call site, before the function body runs. If the copy throws, `*this` was never touched: the strong guarantee for free, self-assignment handled for free. The cost is real, though. Copy assignment always allocates, even when the target already has enough room, and move assignment does a move plus a swap instead of a direct steal. That is why the standard containers do not use it. It is a good default for types where assignment is rare and correctness matters more than the last allocation.

#### in practice

A lidar driver owns a file descriptor, a scratch buffer, a name, and a parser. Only one of those is not already managed by a standard type, so only one class needs special members:

```cpp
#include <unistd.h>
#include <utility>

class UniqueFd {                       // the one class that manages a resource
public:
    UniqueFd() = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(UniqueFd&& o) noexcept : fd_(std::exchange(o.fd_, -1)) {}
    UniqueFd& operator=(UniqueFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = std::exchange(o.fd_, -1);
        }
        return *this;
    }
    UniqueFd(const UniqueFd&) = delete;             // already implied; say it anyway
    UniqueFd& operator=(const UniqueFd&) = delete;

    int get() const noexcept { return fd_; }
private:
    int fd_ = -1;
};

class LidarDriver {                    // rule of zero: move-only, correct, no special members
public:
    LidarDriver(std::string name, UniqueFd fd)
        : name_(std::move(name)), fd_(std::move(fd)) {}
private:
    std::string name_;
    UniqueFd fd_;
    std::vector<Point> scratch_;
    std::unique_ptr<PacketParser> parser_;
};
```

`std::unique_ptr` cannot manage a plain `int` handle without contortions (its deleter's `pointer` type must behave like a nullable pointer), so a small handle class is a legitimate place for hand-written members. The point is containment: one 25-line class with special members, tested once, and every class above it composes it and writes none. That is single responsibility applied to resource management, and it scales: a codebase with a handful of handle types and hundreds of rule-of-zero classes has very few places where a leak or double close can hide.

#### watch out for

A destructor added "just for debugging" silently turns moves into copies:

```cpp
#include <cstdio>
#include <utility>
#include <vector>

struct Snapshot {
    std::vector<double> samples;
    ~Snapshot() { std::puts("snapshot released"); }   // added later
};

int main() {
    Snapshot a{std::vector<double>(100'000)};
    Snapshot b = std::move(a);                        // copy constructor!
    std::printf("%zu\n", a.samples.size());           // prints: 100000
}
```

Remove the destructor and the same program prints `0` on mainstream implementations (the vector was moved; strictly, its moved-from state is unspecified). Nothing warns. GCC and Clang have `-Wdeprecated-copy-dtor`, but it is not enabled by `-Wall` or `-Wextra`. Clang-tidy's `cppcoreguidelines-special-member-functions` catches the pattern.

The same rule bites polymorphic bases. `virtual ~Sensor() = default;` is a declared destructor, so `Sensor` and every class derived from it lose their implicit moves unless they declare them. The usual fix is to declare all five as `= default` in the base (making the copy operations `protected` if you also want to prevent slicing, which day 13 covers).

#### the takeaway

Write the special members in the few classes whose job is to own a resource, and in no others. Everywhere else, the best special member function is the one you did not declare.

#### optional challenge

Which special members does `Config` have, and which of these lines compile?

```cpp
struct Config {
    std::string name;
    std::unique_ptr<Parser> parser;
    explicit Config(std::string n);
};

Config a{"lidar"};                 // (1)
Config b = a;                      // (2)
Config c = std::move(a);           // (3)
std::vector<Config> v;
v.push_back(Config{"radar"});      // (4)
Config d;                          // (5)
```

<details>
<summary>answer</summary>

The user-declared constructor suppresses the default constructor. The destructor, copy operations, and move operations are all implicitly declared as defaulted, but the copy constructor and copy assignment are defined as deleted because `std::unique_ptr` is not copyable. The move operations work and are `noexcept`, since both members' moves are.

So (1) compiles, (2) fails (deleted copy constructor), (3) compiles, (4) compiles and the vector will move on reallocation, and (5) fails (no default constructor). `Config` is move-only without a single line of special-member code, which is exactly the behavior you want for something that owns a parser.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-12"></a>

### day 12: smart pointers and ownership in interfaces

**reading time:** about 10 minutes · **standard:** C++17 · **builds on:** days 04, 08, 10, 11

#### the idea

Read this signature and tell me who deletes the track:

```cpp
void register_track(Track* t);
```

You cannot. Maybe the registry keeps it and deletes it later, maybe it only reads it during the call, maybe it keeps it but expects you to keep it alive. The type says nothing, so the answer lives in a comment, a wiki, or someone's memory. Smart pointers are RAII for heap objects, but their bigger contribution is that they turn ownership into part of the type, where the compiler can check it and a reviewer can see it.

#### understanding the concept

**`std::unique_ptr<T>`** is sole ownership: move-only (day 11), deletes the object in its destructor. With the default deleter, or any empty function-object deleter, it is typically the same size as a raw pointer, and `get()` and `operator->` compile down to the raw pointer. A stateful deleter costs its size: a function-pointer deleter typically doubles the `unique_ptr`. Create one with `std::make_unique<T>(args...)` (C++14). Before C++17, `make_unique` also prevented a leak in `f(std::unique_ptr<A>(new A), g())`, because the compiler could run `new A`, then `g()`, before constructing the `unique_ptr`. C++17 forbids that interleaving (each argument is fully evaluated before the next one starts), but `make_unique` is still the better spelling: no naked `new`, and the type is written once.

**`std::shared_ptr<T>`** is shared ownership via a reference count. The count lives in a separately allocated *control block* along with a weak count, the deleter, and the allocator. A `shared_ptr` object is typically two pointers (object and control block). Copying it increments the strong count; the last owner to go away destroys the object. The counts are updated atomically, so different `shared_ptr` objects that share one control block may be copied and destroyed on different threads. That is the only thread-safety it gives you; more in "watch out for".

`std::make_shared<T>(args...)` puts the object and the control block in one allocation instead of two. The catch: the memory can only be freed when both counts reach zero, so a long-lived `weak_ptr` keeps a large object's storage allocated after its destructor has run. `make_shared` also cannot take a custom deleter.

**`std::weak_ptr<T>`** observes a shared object without owning it. It touches only the weak count. To use the object you call `lock()`, which returns a `shared_ptr` that is empty if the object is gone. That check-and-acquire is atomic, which is why `weak_ptr` has no `get()`.

**`std::enable_shared_from_this<T>`** lets an object that is already owned by a `shared_ptr` produce another `shared_ptr` to itself (`shared_from_this()`), sharing the existing control block. Since C++17, calling it on an object no `shared_ptr` owns throws `std::bad_weak_ptr` (it used to be undefined behavior).

#### in code

Ownership written into signatures, following the C++ Core Guidelines:

```cpp
#include <memory>

struct Config; struct Map;
struct Detector { virtual ~Detector() = default; virtual void run() = 0; };

std::unique_ptr<Detector> make_detector(const Config& cfg);  // gives you ownership
void install(std::unique_ptr<Detector> d);                   // takes ownership
void share(std::shared_ptr<const Map> m);                    // keeps a share
void inspect(const Detector& d);                             // uses, never owns
void maybe_inspect(const Detector* d);                       // uses; may be null

void setup(const Config& cfg) {
    auto d = make_detector(cfg);
    inspect(*d);                 // borrow: no ownership in the signature
    install(std::move(d));       // transfer: visible at the call site
}
```

| parameter | meaning |
|---|---|
| `T&`, `const T&`, `T*` | borrows for the duration of the call; ownership untouched |
| `std::unique_ptr<T>` by value | sink: the callee now owns it |
| `std::unique_ptr<T>&` | the callee may reseat or reset your pointer (rare) |
| `std::shared_ptr<T>` by value | the callee keeps a share (stores it, or hands it to a thread) |
| `const std::shared_ptr<T>&` | the callee *might* keep a share; otherwise just use `T&` |

The most common mistake in that table is the last row used everywhere. A function that only reads a `Map` should take `const Map&`. Taking `shared_ptr` by value costs an atomic increment and decrement per call, and worse, it couples every caller to one particular ownership strategy.

Shared ownership in both directions is a leak:

```cpp
#include <cstdio>
#include <memory>
#include <vector>

struct Joint;
struct Robot {
    std::vector<std::shared_ptr<Joint>> joints;
    ~Robot() { std::puts("~Robot"); }
};
struct Joint {
    std::shared_ptr<Robot> owner;          // BUG: cycle: Robot -> Joint -> Robot
    ~Joint() { std::puts("~Joint"); }
};

int main() {
    auto robot = std::make_shared<Robot>();
    auto j = std::make_shared<Joint>();
    j->owner = robot;
    robot->joints.push_back(j);
}   // prints nothing: both counts stay at 1, neither destructor runs
```

Reference counting cannot collect cycles. Each object keeps the other's count above zero, so when `robot` and `j` go out of scope, both objects leak. The fix is to decide which direction owns. A robot owns its joints; a joint merely refers back to its robot:

```cpp
struct Joint {
    std::weak_ptr<Robot> owner;            // back-reference: does not own
    void report() const {
        if (auto r = owner.lock()) { /* use *r */ }   // empty if the robot is gone
    }
    ~Joint() { std::puts("~Joint"); }
};
// now prints: ~Robot, then ~Joint
```

Often the even simpler fix is better: if a joint can never outlive its robot, `Robot* owner` (or `Robot&`) states that precisely and costs nothing. `weak_ptr` is for when the referenced object really might disappear first.

#### in practice

A perception stack loads large meshes and maps on demand, and several subsystems may use the same one. You want each loaded once, shared while in use, and released when nobody needs it, without the cache itself keeping everything alive forever. That is exactly what `weak_ptr` expresses:

```cpp
#include <map>
#include <memory>
#include <mutex>
#include <string>

class MeshCache {
public:
    std::shared_ptr<const Mesh> get(const std::string& path) {
        std::lock_guard<std::mutex> lock(mtx_);
        if (auto alive = cache_[path].lock()) return alive;   // still in use somewhere
        auto fresh = std::make_shared<const Mesh>(load_mesh(path));
        cache_[path] = fresh;                                 // observe, do not own
        return fresh;
    }
private:
    std::mutex mtx_;
    std::map<std::string, std::weak_ptr<const Mesh>> cache_;
};
```

Two design notes. `shared_ptr<const Mesh>` makes the shared object immutable, which is what makes sharing it across subsystems and threads safe. And `make_shared` is a questionable choice here: an expired entry's `weak_ptr` pins the whole allocation, mesh storage included, until the entry is overwritten or erased. With large objects and long-lived weak references, `std::shared_ptr<const Mesh>(new Mesh(...))` keeps the object and control block separate so the mesh memory goes back as soon as the last user lets go. (A production cache would also prune expired entries.)

#### watch out for

**Thread-safe count, not thread-safe object.** Two threads may each copy and destroy their own `shared_ptr` to the same object freely. But the pointee gets no protection at all: concurrent writes to `*p` are a data race unless you synchronize them. And one `shared_ptr` *instance* read and assigned by two threads at once is also a data race (undefined behavior); C++20's `std::atomic<std::shared_ptr<T>>` exists for that case.

**One raw pointer, two control blocks.**

```cpp
auto* raw = new Track{};
std::shared_ptr<Track> a(raw);
std::shared_ptr<Track> b(raw);   // BUG: second control block, double delete (UB)
```

Each constructor from a raw pointer creates a fresh control block with its own count. The same bug hides in `std::shared_ptr<Session>(this)` inside a member function, which is exactly the problem `enable_shared_from_this` solves. Create shared objects with `make_shared` at the point of allocation and never hand raw ownership around.

More broadly, treat widespread `shared_ptr` as a smell. "Everything is shared" usually means nobody decided who owns what, and the cost shows up as unclear lifetimes, destructors running on whichever thread happened to drop the last reference, and cycles. Most objects have one obvious owner.

#### the takeaway

Default to `unique_ptr` for ownership and plain references for use; reach for `shared_ptr` only when ownership is genuinely shared, and let every signature say which one it is.

#### optional challenge

What does this print, and when is the `int`'s memory actually freed?

```cpp
auto a = std::make_shared<int>(7);
std::weak_ptr<int> w = a;
auto b = a;
std::printf("%ld ", a.use_count());
a.reset();
std::printf("%ld %d ", w.use_count(), w.expired());
b.reset();
std::printf("%d\n", w.expired());
```

<details>
<summary>answer</summary>

It prints `2 1 0 1`. After `b = a` there are two owners. `a.reset()` leaves one, so the object is alive (`expired()` is false). `b.reset()` drops the last strong reference: the `int` is destroyed and `w` reports expired.

The memory is not freed at that point. `make_shared` put the `int` and the control block in one allocation, and `w` still needs the control block (it holds the weak count). The block, including the dead `int`'s storage, is released when `w` is destroyed. For an `int` that is irrelevant; for a 200 MB point cloud observed by a long-lived `weak_ptr`, it is the difference between memory coming back now and memory coming back much later.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-13"></a>

### day 13: polymorphism, inheritance, and composition

**reading time:** about 10 minutes · **standard:** C++17 · **builds on:** days 09, 11, 12

#### the idea

Inheritance is two features wearing one keyword. It gives you *subtyping* (a `Lidar` can be used wherever a `Sensor&` is expected) and *implementation reuse* (a `Lidar` gets `Sensor`'s members and code). You almost always want the first. The second is where class hierarchies go wrong: deep trees, fragile bases, and a `MecanumDriveLidarRobotWithArm` class that exists only because the hierarchy had nowhere else to put it.

Today: how virtual dispatch actually works, the traps it sets (slicing, missing virtual destructors, broken substitutability), and why "inherit interfaces, compose implementations" is a sound default.

#### understanding the concept

A virtual function call through a reference or pointer selects the override for the object's *dynamic* type. The standard specifies only that behavior. Every mainstream compiler implements it the same way, though, and knowing the mechanism makes the costs concrete:

```text
typical layout (Itanium C++ ABI: GCC and Clang on Linux, also MinGW;
MSVC differs in details; none of this is required by the standard)

  Lidar object                    vtable for Lidar (one per class, read-only)
 +------------------+            +------------------------------------+
 | vptr  -----------+----------> | &Lidar::~Lidar (two entries)       |
 | Sensor members   |            | &Lidar::describe     (overridden)  |
 | Lidar members    |            | &Sensor::calibrate   (inherited)   |
 +------------------+            +------------------------------------+
                                   (RTTI and offset data sit just before)
```

A call `s.describe()` becomes: load the vptr from the object, load the function pointer from a fixed slot, call indirectly. The constructor of each class in the chain sets the vptr to its own class's table, which is exactly why day 09's virtual call in a base constructor reached the base version.

The cost is an extra dependent load or two and an indirect branch, which modern branch predictors handle well when a call site keeps seeing the same type. The larger cost is usually what the compiler cannot do: it cannot inline a call whose target it does not know, so it also cannot optimize across it (constant propagation, vectorizing a loop that contains it). Compilers devirtualize when they can prove the dynamic type, and `final` helps them. Whether any of this matters depends on call frequency, so put virtual boundaries at a coarse grain (one call per frame or per batch, not per sample) and measure before contorting a design to avoid them.

Two more tools for designing hierarchies. An **abstract interface** is a class with only pure virtual functions and a virtual destructor: it carries a contract and no implementation. The **non-virtual interface (NVI)** idiom makes public functions non-virtual and the customization points private virtual, so the base class enforces the contract around every override:

```cpp
class RangeSensor {
public:
    virtual ~RangeSensor() = default;
    double read_m() {                                  // the contract lives here
        double r = do_read_m();
        if (!(r >= min_m() && r <= max_m())) throw SensorFault{"out of range"};
        return r;
    }
private:
    virtual double do_read_m() = 0;                    // what derived classes provide
    virtual double min_m() const = 0;
    virtual double max_m() const = 0;
};
```

Overrides cannot skip the check, and the base can later add logging or timing in one place.

#### in code

First, let the compiler check your overrides.

```cpp
struct Filter {
    virtual ~Filter() = default;
    virtual double apply(double x) const = 0;
};

struct LowPass : Filter {
    double apply(double x);               // BUG: missing const: a new function that
};                                        // hides Filter::apply; LowPass stays abstract

struct LowPass2 final : Filter {
    double apply(double x) override;      // error: marked 'override' but does not override
};

struct LowPass3 final : Filter {
    double apply(double x) const override { return 0.9 * x; }   // correct
};
```

Without `override`, a signature mismatch (missing `const`, `float` versus `double`, a changed base signature after a refactor) silently declares a new function. Here the mistake surfaces only because `LowPass` remains abstract; had the base function not been pure, the base version would run and nothing would complain. GCC 12's `-Woverloaded-virtual` would flag the hiding, but it is not part of `-Wall` in that version. Write `override` on every override; `final` on a class or function says "no further overriding" and gives the optimizer a devirtualization hint.

Second, the virtual destructor, and a twist with smart pointers.

```cpp
struct Plugin { ~Plugin() {} virtual void run() {} };   // BUG: non-virtual destructor
struct Logger : Plugin { std::string path; };

void demo() {
    std::unique_ptr<Plugin> p = std::make_unique<Logger>();
    p.reset();           // UB: deletes a Logger through Plugin* without a virtual dtor

    std::shared_ptr<Plugin> s = std::make_shared<Logger>();
    s.reset();           // OK, by accident: the control block remembers ~Logger
}
```

Deleting a derived object through a base pointer whose destructor is not virtual is undefined behavior, not merely "the derived destructor is skipped". `unique_ptr<Base>` calls `delete` on a `Base*`, so it inherits the bug. `shared_ptr` happens to survive because the control block captured a deleter for the real type at creation, but relying on that is fragile. The rule: a class meant to be deleted through a base pointer gets a public virtual destructor; otherwise make the destructor protected and non-virtual. GCC's `-Wdelete-non-virtual-dtor` (in `-Wall`) catches a direct `delete base_ptr;`, but GCC 12 stays silent on the `unique_ptr` version above, because the `delete` happens inside a system header. `-Wnon-virtual-dtor` (not in `-Wall`) flags the class definition itself and catches both.

Third, predict the output.

```cpp
#include <cstdio>
#include <vector>

struct Sensor {
    virtual ~Sensor() = default;
    virtual const char* name() const { return "sensor"; }
};
struct Lidar : Sensor {
    const char* name() const override { return "lidar"; }
};

int main() {
    Lidar lidar;
    Sensor& ref = lidar;
    Sensor copy = lidar;                  // slicing
    std::vector<Sensor> rack{lidar};      // slicing, again
    std::printf("%s %s %s\n", ref.name(), copy.name(), rack[0].name());
}
// prints: lidar sensor sensor
```

Copying a `Lidar` into a `Sensor` object constructs a `Sensor` from the `Sensor` part and discards the rest: the object's type is `Sensor`, vptr included. Polymorphism needs indirection (references, pointers, or `std::vector<std::unique_ptr<Sensor>>`). To make slicing impossible, delete or protect the base's copy operations (day 11); an abstract base cannot be sliced into at all.

#### in practice

A mobile robot has a drive system and a localizer. The inheritance version models variations as subclasses: `DiffDriveRobot`, then `DiffDriveLidarRobot`, then a mecanum variant that needs half of each. Every new axis of variation multiplies the classes. Composition models each variation as a part:

```cpp
#include <memory>

struct Drive {                                   // interface: inherited
    virtual ~Drive() = default;
    virtual void apply(const Twist& cmd) = 0;
};

class Robot {                                    // implementation: composed
public:
    Robot(std::unique_ptr<Drive> drive, std::unique_ptr<Localizer> loc)
        : drive_(std::move(drive)), loc_(std::move(loc)) {}
    void step(const Twist& cmd) { drive_->apply(cmd); }
private:
    std::unique_ptr<Drive> drive_;
    std::unique_ptr<Localizer> loc_;
};
```

Inheritance has not disappeared; it is confined to small interfaces (`Drive`), where subtyping is what you want. The robot *has* a drive rather than *is* one, so drive and localizer vary independently, can be swapped at run time, and can be replaced by fakes in tests (day 44 builds on this). The `unique_ptr` members also make `Robot` a move-only, rule-of-zero class.

Substitutability is the other half. The Liskov substitution principle says code written against the base must keep working with any derived class. Suppose `RangeSensor`'s contract is "always returns a range in `[min, max]`", and a new `Sonar` returns `-1` when it hears no echo. It compiles, it overrides correctly, and it breaks every caller that trusted the contract. The fix is not a type check in the callers; it is either a contract that admits "no reading" (an `std::optional<double>` result, day 24) or a `Sonar` that is not a `RangeSensor`. Subtyping is a promise about behavior, not just signatures.

#### watch out for

Inheriting for code reuse. If `TelemetryPublisher` derives from `std::vector<Message>` or from a `Socket` class to "get" its functions, every public member of the base becomes part of your interface, users can call `push_back` and bypass your invariants, and changing the base breaks your users. Make the reused type a private member and expose only what your class means. Public inheritance is a statement that the derived class *is substitutable for* the base; if you would not say that sentence out loud, use composition.

#### the takeaway

Use public inheritance for substitutable interfaces, with `override`, a virtual destructor, and no slicing; for reuse and variation, compose.

#### optional challenge

`Base` has a non-virtual public function `void tick()` and `Derived` declares its own `void tick()`. Given `Derived d; Base& b = d;`, which function do `d.tick()` and `b.tick()` call? Would adding `override` to `Derived::tick` help?

<details>
<summary>answer</summary>

`d.tick()` calls `Derived::tick` and `b.tick()` calls `Base::tick`. Without `virtual`, the call is resolved from the static type of the expression, so the same object behaves differently depending on how you name it. `Derived::tick` merely hides `Base::tick`.

Adding `override` would not compile ("marked 'override', but does not override"), and that is the point: it turns the silent mistake into an error that tells you the base function is not virtual. The fix is then a deliberate choice: make `Base::tick` virtual, or rename the derived function so nobody expects dispatch.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-14"></a>

### day 14: week 2 review: owning your resources

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 08 to 13

#### recap

| day | idea in one line |
|---|---|
| [08](#day-08) | RAII ties a resource to an object's lifetime: acquire in the constructor, release in a destructor that never throws, and every exit path that unwinds cleans up. |
| [09](#day-09) | Bases, then members in declaration order, then the body; destruction reverses it. A constructor that throws leaves no object, so only fully constructed members are cleaned up. |
| [10](#day-10) | `std::move` is a cast; overload resolution picks the move. Moves must be `noexcept` for `std::vector` to use them, and moved-from objects are valid but unspecified. |
| [11](#day-11) | Declaring a destructor or copy operation suppresses the implicit moves. Write special members only in resource-owning classes; compose everything else (rule of zero). |
| [12](#day-12) | `unique_ptr` for sole ownership, `shared_ptr` only for genuinely shared ownership, `weak_ptr` to observe or break cycles, references for borrowing; signatures state which. |
| [13](#day-13) | Virtual dispatch needs indirection and a virtual destructor; use `override`, avoid slicing, inherit interfaces, and compose implementations. |

The thread through the week: **ownership is a design decision, and C++ lets you write it into types**. Once it is in the types, the compiler enforces it, destructors execute it, and reviewers can read it.

#### review questions

1. A class's destructor is declared as `~Telemetry() = default;` and nothing else special is declared. Its members are a `std::string` and a `std::vector<Sample>`. When a `std::vector<Telemetry>` reallocates, are the elements moved or copied? Why?

2. Choose a parameter type for each function and say what it communicates: (a) `log_stats` reads a `Frame` and keeps nothing; (b) `Pipeline::enqueue` keeps the frame until a worker processes it, and the caller is done with it; (c) `reload_detector` may replace the caller's `Detector` with a new one.

3. After `std::string b = std::move(a);`, which of these are fine: `a.size()`, `a.clear()`, `a = "x"`, `assert(a.empty())`, `a.front()`?

4. A plugin interface has virtual functions but a public non-virtual destructor. `std::shared_ptr<Plugin> p = std::make_shared<Logger>(); p.reset();` works correctly. The same code with `std::unique_ptr` is undefined behavior. Explain the difference, and why "use `shared_ptr`" is the wrong fix.

5. **From week 1.** Day 05 said C++17 guarantees copy elision for prvalues but not for named locals. How does that connect to day 10's advice against `return std::move(local);`?

6. **From week 1.** Is this safe? `const std::string& name = load_config().name();` where `Config::name()` returns `const std::string&` to a member.

#### mini exercise

This class works in the happy path and has at least four ownership bugs. Find them, then rewrite it so it needs no user-declared special members (or, if it needs one, say why and handle the consequence).

```cpp
#include <cstdio>
#include <cstring>
#include <stdexcept>

class TelemetryLog {
public:
    TelemetryLog(const char* path, std::size_t capacity)
        : file_(std::fopen(path, "a")), buf_(new char[capacity]), cap_(capacity) {
        if (!file_) throw std::runtime_error("cannot open log");
    }
    ~TelemetryLog() { flush(); std::fclose(file_); delete[] buf_; }

    void write(const char* msg) {
        std::size_t n = std::strlen(msg);
        if (used_ + n > cap_) flush();
        if (n > cap_) { std::fwrite(msg, 1, n, file_); return; }
        std::memcpy(buf_ + used_, msg, n);
        used_ += n;
    }
    void flush() { std::fwrite(buf_, 1, used_, file_); used_ = 0; }
private:
    std::FILE* file_;
    char* buf_;
    std::size_t cap_, used_ = 0;
};
```

#### answers

<details>
<summary>1. defaulted destructor and vector reallocation</summary>

Copied. `= default` still counts as *declaring* the destructor (day 11), so the implicit move constructor and move assignment are not declared. Rvalues then bind to the copy constructor, `std::is_nothrow_move_constructible_v<Telemetry>` is false (the copy constructor can throw), and `std::vector` falls back to copying to keep its strong guarantee (day 10). Fix: delete the destructor declaration, or declare all five as `= default`.

</details>

<details>
<summary>2. parameter types</summary>

(a) `const Frame&`: a borrow for the duration of the call; ownership is not the callee's business. (b) A sink: `Frame` by value (if `Frame` is a movable value type) or `std::unique_ptr<Frame>` by value (if frames live on the heap); the caller writes `std::move(frame)`, which makes the hand-over visible. (c) `std::unique_ptr<Detector>&`: the rare "may reseat your pointer" signature. Returning a new `std::unique_ptr<Detector>` is often clearer still.

</details>

<details>
<summary>3. using a moved-from string</summary>

`a.size()`, `a.clear()`, and `a = "x"` are fine: they have no preconditions, and a moved-from standard type is valid but unspecified. `assert(a.empty())` compiles and will probably pass on your implementation, but nothing guarantees it, so it encodes a false assumption. `a.front()` has a precondition (`!a.empty()`); calling it on an empty string is undefined behavior, so it is only safe after you check. (`a[0]`, by contrast, is always valid on a `std::string`: at `size() == 0` it refers to the terminating null.) Treat a moved-from object as "assign or destroy" unless its type documents more.

</details>

<details>
<summary>4. shared_ptr, unique_ptr, and the missing virtual destructor</summary>

`make_shared<Logger>()` creates a control block whose deleter destroys a `Logger`, and converting to `shared_ptr<Plugin>` keeps that control block, so the right destructor runs. `unique_ptr<Plugin>` uses `default_delete<Plugin>`, which does `delete` on a `Plugin*`; without a virtual destructor that is undefined behavior (day 13). Switching to `shared_ptr` papers over the defect for one creation path only: a `shared_ptr<Plugin>(raw_plugin_ptr)` or any plain `delete` brings it back, and it imposes shared ownership where none is needed. The fix is a public virtual destructor in the interface.

</details>

<details>
<summary>5. from week 1: elision and return std::move</summary>

`return local;` is eligible for NRVO, which compilers routinely perform but the standard does not require; if it does not happen, the local is still treated as an rvalue and moved. `return std::move(local);` turns the operand into an xvalue, which is no longer "the name of a local", so NRVO is off the table and you are guaranteed a move instead of possibly nothing. C++17's guaranteed elision applies to prvalues (`return Frame{n};`), where no copy or move constructor is even required. GCC warns with `-Wpessimizing-move`.

</details>

<details>
<summary>6. from week 1: lifetime extension through a member function</summary>

Not safe: `name` dangles. Lifetime extension (day 03) applies only when a reference binds directly to a temporary. Here it binds to whatever `name()` returns, a reference into the temporary `Config`, and that temporary is destroyed at the end of the full-expression. Using `name` afterwards is undefined behavior. Fix: copy (`std::string name = load_config().name();`) or keep the `Config` alive in a named variable.

</details>

<details>
<summary>mini exercise: bugs and a rule-of-zero rewrite</summary>

The bugs:

- If `new char[capacity]` throws `std::bad_alloc`, the destructor never runs (day 09), and the `FILE*` leaks.
- If `fopen` fails, the body throws and `buf_` leaks for the same reason.
- The implicit copy operations copy both raw pointers: two objects, then a double `fclose` and double `delete[]` (UB).
- No moves: the class cannot be returned from a factory or stored in a vector without copying, which is itself the double-free bug.
- The destructor calls `flush()`, whose `fwrite` errors are silently lost (day 08).

The neatest rewrite notices that the hand-made buffer duplicates what stdio already does. Remove it, size the stdio buffer instead, and the class owns exactly one resource through a type that already manages it:

```cpp
#include <cstdio>
#include <memory>
#include <stdexcept>

struct FileCloser {
    void operator()(std::FILE* f) const noexcept { std::fclose(f); }  // fclose flushes
};

class TelemetryLog {                         // move-only, rule of zero
public:
    TelemetryLog(const char* path, std::size_t capacity)
        : file_(std::fopen(path, "a")) {
        if (!file_) throw std::runtime_error("cannot open log");
        std::setvbuf(file_.get(), nullptr, _IOFBF, capacity);
    }
    void write(const char* msg) { std::fputs(msg, file_.get()); }
    [[nodiscard]] bool flush() { return std::fflush(file_.get()) == 0; }  // reports errors
private:
    std::unique_ptr<std::FILE, FileCloser> file_;
};
```

Copying is now implicitly deleted, moves are implicit and `noexcept`, both leak paths are gone, and callers who care about write errors call `flush()` and check it. Document the moved-from state: `file_` is null, so only assignment and destruction are allowed.

If you must keep a custom buffer (say, to batch records into fixed-size packets), make it a `std::vector<char>` member. Flushing it on destruction then needs a user-declared destructor, which suppresses the implicit moves: declare the move operations `= default` and the copy operations `= delete`, so the class states its ownership explicitly instead of losing it by accident.

</details>

#### connections

Week 1 supplied the mechanics this week relies on. RAII is day 03's lifetime rules turned into a design technique. Move semantics is day 05's value categories feeding overload resolution. Double deletes, deleting through a non-virtual base, and dangling back-pointers are day 06's undefined behavior wearing ownership clothes.

Week 3 builds directly on top. Containers (day 15) reward `noexcept` moves and punish iterator invalidation; lambdas (day 17) capture `unique_ptr` with init-captures; perfect forwarding (day 19) is how `make_unique` and `emplace_back` pass arguments through; and exception safety (day 20) formalizes the strong guarantee you met in copy-and-swap and `std::vector` reallocation. Further out, `std::lock_guard` and `std::jthread` (days 36 and 37) are RAII again, and dependency injection (day 44), type erasure (day 46), and the pimpl idiom (day 47) are all ownership decisions expressed through the tools from this week.

[back to table of contents](#table-of-contents)

---

<a id="week-3"></a>

## week 3: standard library and generic programming

The standard library as a vocabulary, and templates as the machinery behind it.

<a id="day-15"></a>

### day 15: containers and what they cost

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 10, 12

#### the idea

You need to keep the live tracks of a radar tracker: a few hundred entries, looked up by track id, updated every frame, occasionally created and deleted. `std::map`, `std::unordered_map`, a sorted `std::vector`? Most engineers answer from habit. The better answer starts from three questions: how is the data accessed, what does each operation cost in complexity *and* in memory traffic, and which guarantees (ordering, reference stability) does the rest of the code silently rely on?

#### understanding the concept

A container is a contract about three things: complexity of operations, memory layout, and invalidation rules. The complexity is what the standard promises. The layout is what your cache experiences. The invalidation rules are what turn a refactor into a use-after-free.

`std::vector` is the default for good reasons. Elements are contiguous, so iteration walks memory linearly and the hardware prefetcher can keep up. `push_back` is amortized O(1) because capacity grows geometrically; the standard only requires the amortized bound, and the growth factor is a library choice (libstdc++ doubles, MSVC grows by 1.5x). `reserve(n)` lets you pay for that growth once. The price: inserting in the middle is O(n), and growth beyond capacity moves every element to a new buffer, which is why day 10's `noexcept` move constructor matters.

The rest of the family, briefly:

| container | layout | lookup | insert / erase | what an insert invalidates |
|---|---|---|---|---|
| `vector` | one contiguous block | O(1) index | O(1) amortized at end, O(n) elsewhere | everything if it reallocates, else iterators at or after the insertion point |
| `array<T, N>` | inline, no heap | O(1) index | fixed size | n/a |
| `deque` | blocks of elements plus an index map | O(1) index | O(1) at both ends | at either end: all iterators, but no references |
| `list` | one node per element | O(n) | O(1) given an iterator | nothing |
| `map` / `set` | one node per element, usually a red-black tree | O(log n) | O(log n) | nothing |
| `unordered_map` | node per element plus a bucket array | O(1) average, O(n) worst | O(1) average | iterators if it rehashes, never references |

Big-O hides the constant factors that often dominate at realistic sizes. Every `map` or `unordered_map` insertion is a separate heap allocation, and every lookup chases pointers through nodes that may sit anywhere in memory. An `unordered_map` lookup also pays for hashing the key (cheap for an integer, real work for a long string) and for at least one indirection through the bucket array. For a few hundred small elements, a linear scan or binary search over a contiguous `vector` can win against a "faster" structure, and it can also lose. You don't know until you measure with realistic sizes and access patterns, which day 50 covers, and day 51 explains why memory layout moves the numbers so much.

`std::list` rarely wins on traversal speed, but it has two real advantages: insertion and erasure never invalidate references to other elements, and `splice` moves nodes between lists without copying or allocating. Splicing one element or a whole list is O(1); splicing a range from a *different* list is linear in the range length, because `size()` must stay O(1).

#### in code

The classic invalidation bug. It passes tests for months because small test inputs happen to fit in the existing capacity.

```cpp
#include <vector>
#include <string>

struct Detection { float range_m; float doppler; std::string label; };

void annotate(std::vector<Detection>& dets) {
    Detection& first = dets.front();
    dets.push_back({0.0f, 0.0f, "synthetic"});  // may reallocate
    first.label = "reference";  // BUG: UB if push_back reallocated; 'first' dangles
}

void annotate_fixed(std::vector<Detection>& dets) {
    const std::size_t first = 0;  // indices survive reallocation, references do not
    dets.push_back({0.0f, 0.0f, "synthetic"});
    dets[first].label = "reference";
}
```

Calling `reserve` before taking the reference would also fix it, but that couples correctness to a capacity calculation somebody will change later. An index (or a stable id) states the intent directly.

C++17 gave the associative containers better insertion functions and node handles. `try_emplace` constructs the value only if the key is absent, and does not move from its arguments when the key already exists. `insert_or_assign` says what `operator[]` plus assignment means, without requiring a default-constructible mapped type and while telling you which case happened.

```cpp
#include <map>
#include <memory>
#include <string>
#include <iostream>

struct Track { explicit Track(int id) : id{id} {} int id; };  // no default constructor

int main() {
    std::map<int, std::unique_ptr<Track>> tracks;
    auto p = std::make_unique<Track>(7);

    tracks.try_emplace(7, std::move(p));
    auto q = std::make_unique<Track>(7);
    auto [it, inserted] = tracks.try_emplace(7, std::move(q));
    std::cout << inserted << ' ' << (q != nullptr) << '\n';  // prints: 0 1  (q not consumed)

    auto [it2, ins2] = tracks.insert_or_assign(7, std::make_unique<Track>(70));
    std::cout << ins2 << ' ' << it2->second->id << '\n';      // prints: 0 70

    // Rekey a node without reallocating it: extract, edit the key, reinsert.
    auto node = tracks.extract(7);
    node.key() = 8;
    tracks.insert(std::move(node));

    std::map<int, std::unique_ptr<Track>> retired;
    retired.try_emplace(8, std::make_unique<Track>(800));
    retired.try_emplace(9, std::make_unique<Track>(9));
    tracks.merge(retired);  // moves node 9 across; key 8 already exists, so it stays behind
    std::cout << tracks.size() << ' ' << retired.size() << '\n';  // prints: 2 1
}
```

`extract` and `merge` relink existing nodes, so no element is copied, moved, or reallocated, and pointers to the elements remain valid (they now refer into the other container). That makes them the right tool for move-only values and for rekeying, which used to require erase plus a fresh insert.

`emplace_back` versus `push_back` is the third everyday decision:

```cpp
#include <vector>
#include <memory>

struct Widget { };

void fill(std::vector<std::unique_ptr<Widget>>& v, std::vector<std::vector<int>>& rows) {
    v.push_back(std::make_unique<Widget>());  // fine: object built first, then moved in
    v.emplace_back(new Widget);  // BUG: if growth throws, the raw pointer leaks

    rows.emplace_back(1'000'000);  // compiles: a row of one million zeros, via an explicit ctor
    // rows.push_back(1'000'000);  // error: no implicit conversion int -> vector<int>
}
```

`emplace_back` forwards its arguments to a constructor (day 19 shows how), which means it happily calls `explicit` constructors that `push_back` would refuse. Use it when you are constructing from constructor arguments; when you already have an object, `push_back` says the same thing and is equivalent. Since C++17, `emplace_back` returns a reference to the new element.

#### in practice

Back to the radar tracker. The first version stores tracks in `std::unordered_map<TrackId, Track>`, and the association stage keeps `Track*` pointers into it across frames. That works, quietly, because `unordered_map` never invalidates references, even on rehash. A later profiling session suggests a `std::vector<Track>` for faster per-frame updates. The swap compiles cleanly and then corrupts memory on the first frame that adds enough tracks to reallocate, because the code was depending on a guarantee that was never written down.

The design lesson: reference stability is part of a container's contract, and code that stores pointers or iterators into a container depends on it. If you want freedom to change containers later, hand out stable identifiers (a track id, or an index plus generation counter) instead of addresses. Then the layout decision becomes a measurement question again rather than a correctness question.

#### watch out for

`operator[]` on `std::map` and `std::unordered_map` inserts a default-constructed value when the key is missing. A "read" such as `if (tracks[id]) ...` grows the table, may allocate, and for `unordered_map` may rehash and invalidate every iterator you hold. It also cannot be called on a `const` map. Use `find` (or C++20 `contains`) to query, `try_emplace` or `insert_or_assign` to write.

#### the takeaway

Pick the container by access pattern, then check the invalidation rules, then measure. Start with `std::vector`, and treat reference stability as part of the interface: whoever depends on it is coupled to your container choice.

#### optional challenge

What does this guarantee, and what doesn't it?

```cpp
std::vector<int> v{1, 2, 3};
v.reserve(4);
int& r = v[0];
v.push_back(4);
v.push_back(5);
int x = r;
```

<details>
<summary>answer</summary>

`reserve(4)` guarantees `capacity() >= 4`, so the first `push_back` (size 3 to 4) cannot reallocate and `r` is still valid after it. The exact capacity after `reserve` is not specified; an implementation may allocate more than you asked for. So whether the second `push_back` (size 4 to 5) reallocates depends on the library. If it does, `r` dangles and `int x = r;` is undefined behavior. With libstdc++, `reserve(4)` on this vector yields exactly 4, so the second `push_back` reallocates. Portable code cannot rely on either outcome; if it must keep `r`, it needs `reserve(5)` or an index.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-16"></a>

### day 16: iterators and algorithms over raw loops

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** day 15

#### the idea

Here is a line that compiles, passes a quick test, and is wrong:

```cpp
v.erase(std::remove_if(v.begin(), v.end(), is_even));
```

It erases one element, not all the even ones. To see why, you need the model behind the standard algorithms: they see iterators, never containers. Once that model clicks, the erase-remove idiom, the iterator categories, and the "use an algorithm instead of a loop" advice all follow from the same idea.

#### understanding the concept

An algorithm like `std::remove_if` receives a pair of iterators `[first, last)`. It can read and write elements through them, but it has no access to the container: it cannot allocate, cannot shrink, cannot erase. That decoupling is the design win of the STL: N algorithms times M containers needs N + M pieces of code, not N × M. The price is that some operations take two steps, one by the algorithm and one by the container.

The half-open range is what makes this compose. `end()` points one past the last element, so an empty range is `first == last`, the length is `last - first` for random-access iterators, and "not found" has a natural value: the algorithm returns `last`. Subranges chain without plus-or-minus-one adjustments: `[first, mid)` and `[mid, last)` cover the whole range exactly once.

Algorithms state what they need from iterators through categories. Each category adds guarantees to the previous one:

| category | adds | typical source |
|---|---|---|
| input | read once, single pass | `std::istream_iterator` |
| forward | multi-pass, can revisit | `std::forward_list`, unordered containers |
| bidirectional | `--it` | `std::list`, `std::map`, `std::set` |
| random access | `it + n`, `it2 - it1`, `<` in O(1) | `std::deque` |
| contiguous (named in C++20) | elements adjacent in memory | `std::vector`, `std::array`, `std::string` |

In C++17 there is no tag for contiguous iterators; contiguity is a property of the container, and C++20 adds `std::contiguous_iterator_tag` and the `std::contiguous_iterator` concept. `std::sort` needs random access, so `std::sort(list.begin(), list.end())` fails to compile. GCC 12 reports it as `no match for 'operator-'` from deep inside `stl_algo.h`, which is the pre-concepts error experience that day 29 fixes. `std::list` has a member `sort()` for exactly this reason.

Why prefer algorithms to hand-written loops? A named algorithm states intent (`any_of` reads as a question, a `for` loop with a `bool found` flag has to be simulated), it gets the boundary conditions right once, and it advertises its complexity. Sean Parent's "no raw loops" is a good default, not a law: when a loop does two things in one pass, or the algorithm version needs a contorted lambda, a plain loop is the clearer code.

#### in code

Intent-revealing algorithms over a telemetry buffer. The lambdas are short on purpose; day 17 covers what they compile to.

```cpp
#include <algorithm>
#include <iterator>
#include <numeric>
#include <vector>

struct Sample { double value; bool valid; };

bool any_fault(const std::vector<Sample>& s) {
    return std::any_of(s.begin(), s.end(), [](const Sample& x) { return !x.valid; });
}

// Returns s.end() if nothing exceeds the limit: the half-open range gives "not found" a value.
auto first_over(const std::vector<Sample>& s, double limit) {
    return std::find_if(s.begin(), s.end(), [limit](const Sample& x) { return x.value > limit; });
}

std::vector<double> scaled(const std::vector<Sample>& s, double gain) {
    std::vector<double> out;
    out.reserve(s.size());
    std::transform(s.begin(), s.end(), std::back_inserter(out),
                   [gain](const Sample& x) { return x.value * gain; });
    return out;
}

double energy(const std::vector<double>& v) {
    return std::accumulate(v.begin(), v.end(), 0.0, [](double acc, double x) { return acc + x * x; });
}
```

`std::back_inserter` is an output iterator whose assignment calls `push_back`. That is how an algorithm that cannot touch the container still appends to it: the container is reached through an iterator adaptor that the caller chose.

Now the erase-remove bug. Predict the output:

```cpp
#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    auto is_even = [](int x) { return x % 2 == 0; };

    std::vector<int> v{1, 2, 3, 4, 5, 6};
    v.erase(std::remove_if(v.begin(), v.end(), is_even));  // BUG: single-iterator erase
    std::cout << v.size() << '\n';                          // prints: 5

    std::vector<int> w{1, 2, 3, 4, 5, 6};
    w.erase(std::remove_if(w.begin(), w.end(), is_even), w.end());  // erase-remove idiom
    std::cout << w.size() << '\n';                                  // prints: 3
}
```

`remove_if` shifts the kept elements (1, 3, 5) to the front and returns an iterator to the new logical end. The elements after it are valid but have unspecified values (with libstdc++ the first buggy vector ends as `1 3 5 5 6`, but don't depend on that). `erase(it)` removes one element; `erase(it, end())` removes the tail. C++20 wraps the idiom as `std::erase_if(w, is_even)`, which returns the number of elements removed.

Partition and stable sort express a common two-step "group, then order" job without index bookkeeping:

```cpp
#include <algorithm>
#include <vector>

struct Det { int id; float range_m; bool confirmed; };

void order_for_display(std::vector<Det>& dets) {
    // confirmed first, each group keeps its original order
    auto mid = std::stable_partition(dets.begin(), dets.end(),
                                     [](const Det& d) { return d.confirmed; });
    // confirmed detections by range; equal ranges keep their previous order
    std::stable_sort(dets.begin(), mid,
                     [](const Det& a, const Det& b) { return a.range_m < b.range_m; });
}
// input ids:  1(40m, conf) 2(12m) 3(12m, conf) 4(40m, conf) 5(7m)
// output ids: 3 1 4 2 5
```

The complexities are part of the choice. `std::partition` is O(n) and does not preserve relative order; `std::stable_partition` does, using a temporary buffer if it can get one (O(n)) and O(n log n) swaps if it cannot. `std::stable_sort` is O(n log n) comparisons with extra memory and O(n log² n) without. If order within groups does not matter, the unstable versions avoid that buffer.

#### in practice

A telemetry service computes the p99 latency of each one-second window. The first version copies the samples, calls `std::sort` (O(n log n)), and reads the element at index `0.99 * n`. `std::nth_element` places exactly that element where it would be after sorting, with everything smaller before it and everything larger after it, in O(n) on average. For a single percentile the full sort does work nobody uses. Knowing the algorithm vocabulary (`nth_element`, `partial_sort`, `lower_bound` on sorted data, `minmax_element`) is often worth more than micro-tuning a loop. Still measure: for a few hundred samples per window, both may be far below the noise floor of the service.

C++17 also added execution policies: `std::sort(std::execution::par, v.begin(), v.end())`. Treat them with care. The callable must not cause data races (locking inside it is allowed for `par`, not for `par_unseq`), an exception escaping an element access calls `std::terminate`, and whether you get parallelism at all depends on the library. MSVC ships a parallel implementation; libstdc++ uses Intel TBB as its parallel backend. On GCC 12 without TBB the code above still compiles and runs, but libstdc++ selects its serial backend, so you pay the policy's constraints without any speedup. Parallel sorting also has a threshold below which the coordination costs more than it saves. Benchmark on the target machine with production-sized inputs before committing to it.

#### watch out for

`std::accumulate` uses the type of its initial value as the accumulator type:

```cpp
std::vector<double> v{0.5, 0.5, 0.5};
auto total = std::accumulate(v.begin(), v.end(), 0);  // BUG: int accumulator; total == 0
```

Each step computes `int + double`, then converts the result back to `int`, truncating 0.5 to 0. GCC 12 gives no warning here even with `-Wconversion`, because the conversion happens inside a system header. Write `0.0` (or `T{}`) and let the initial value carry the type you mean.

#### the takeaway

Algorithms see iterators, not containers. That one fact explains the half-open range, the erase-remove idiom, `back_inserter`, and why `std::sort` cannot sort a list. Reach for a named algorithm first because it says what you mean, and drop back to a loop when the loop is clearer.

#### optional challenge

What is wrong with this, and what are two correct fixes?

```cpp
std::vector<double> in{1.0, 2.0, 3.0};
std::vector<double> out;
std::transform(in.begin(), in.end(), out.begin(), [](double x) { return x * 2; });
```

<details>
<summary>answer</summary>

`out` is empty, so `out.begin()` is also `out.end()`, and `transform` writes three elements past the end: undefined behavior. The algorithm cannot grow `out` because it only has an iterator, not the container. Fix it with `out.resize(in.size())` before the call (then writing through `out.begin()` is valid), or with `out.reserve(in.size())` plus `std::back_inserter(out)` as the destination. The second avoids value-initializing elements that are about to be overwritten, which matters for expensive element types and not at all for doubles.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-17"></a>

### day 17: lambdas and closures in depth

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 03, 12, 16

#### the idea

A lambda looks like an inline function, which is exactly the wrong mental model. A lambda expression creates an *object*. That object has a type, a size, data members, and a lifetime, and every lambda bug you will meet in production (a dangling capture in a callback, a stateful predicate behaving oddly, a `std::function` that refuses to compile) follows from forgetting that.

#### understanding the concept

The compiler turns each lambda expression into a class with a unique, unnamed type (the closure type) and evaluates the expression to a prvalue of that type (the closure object). Captures become data members, initialized when the lambda expression is evaluated. The body becomes `operator()`, which is `const` unless you write `mutable`.

```cpp
double gain = 2.0;
int calls = 0;
auto f = [gain, &calls](double x) { ++calls; return x * gain; };

// is roughly equivalent to:
struct Closure {
    double gain;   // copied when the lambda expression is evaluated
    int& calls;    // a reference: no lifetime extension, no ownership
    double operator()(double x) const { ++calls; return x * gain; }
};
auto g = Closure{gain, calls};
```

Several rules fall out of this picture. A by-value capture is a snapshot taken at creation, not a live view. A `const` call operator can still modify what a reference capture refers to, because the constness applies to the member, not to the referent. Two lambdas with identical text have different types, so you cannot assign one to a variable of the other's type. A lambda with no captures has no state and converts implicitly to a plain function pointer, which is how you pass one to a C API expecting `void(*)(int)`.

C++14 and C++17 added the pieces you use most:

- **init-captures** (`[p = std::move(ptr)]`, C++14) declare a member with any initializer. This is how you move a `std::unique_ptr` into a closure, or capture a computed value under a new name.
- **generic lambdas** (`[](const auto& a, const auto& b) {...}`, C++14) make `operator()` a template, instantiated per argument type.
- **`[*this]`** (C++17) copies the whole enclosing object into the closure, where `[this]` copies only the pointer.
- **constexpr lambdas** (C++17): a lambda's call operator is implicitly `constexpr` when it satisfies the requirements, so `constexpr auto sq = [](int x) { return x * x; }; static_assert(sq(4) == 16);` works.

#### in code

Closures are values: copying one copies its state. Predict the output.

```cpp
#include <iostream>

int main() {
    int n = 1;
    auto by_val = [n] { return n; };
    auto by_ref = [&n] { return n; };
    n = 2;
    std::cout << by_val() << by_ref() << '\n';    // prints: 12

    auto counter = [c = 0]() mutable { return ++c; };
    auto copy = counter;                           // copies the member c (still 0)
    counter();
    counter();
    std::cout << counter() << copy() << '\n';     // prints: 31

    // immediately invoked lambda: complex logic, but the result is const
    const auto mode = [&] {
        if (n > 1) return "fast";
        return "safe";
    }();
    std::cout << mode << '\n';                     // prints: fast
}
```

The last pattern deserves more use than it gets: when a `const` variable needs branching or a loop to compute, an immediately invoked lambda keeps it `const` instead of forcing a mutable variable with a delayed assignment.

The bug that matters most is a reference capture that outlives its referent. The lambda escapes the function, the stack frame goes away, and the closure holds a reference to nothing.

```cpp
#include <cstdio>
#include <functional>
#include <string>
#include <vector>

class Deferred {
    std::vector<std::function<void()>> tasks_;
public:
    void defer(std::function<void()> f) { tasks_.push_back(std::move(f)); }
    void flush() { for (auto& t : tasks_) t(); tasks_.clear(); }
};

void schedule_report(Deferred& d, const std::string& name) {
    std::string msg = "report: " + name;
    d.defer([&] { std::puts(msg.c_str()); });  // BUG: msg dies at return; flush() reads it: UB
}

void schedule_report_fixed(Deferred& d, const std::string& name) {
    std::string msg = "report: " + name;
    d.defer([msg = std::move(msg)] { std::puts(msg.c_str()); });  // the closure owns its data
}
```

`[&]` is fine when the lambda runs before the enclosing scope ends: a predicate passed to `std::find_if`, a comparator for `std::sort`. It is a liability as soon as the lambda is stored, deferred, or handed to another thread. A useful rule: if the lambda leaves the scope, capture by value or by init-capture, and if it must refer to a shared object, capture something that tracks lifetime (a `std::weak_ptr`, day 12) rather than a raw pointer or reference.

Now `std::function` versus a template parameter:

```cpp
#include <functional>
#include <memory>
#include <vector>

struct Point { float x, y, z; };

// Type-erased: one compiled function accepts any callable with this signature.
std::size_t count_if_erased(const std::vector<Point>& pts,
                            const std::function<bool(const Point&)>& keep) {
    std::size_t n = 0;
    for (const auto& p : pts) if (keep(p)) ++n;   // indirect call per point
    return n;
}

// Template: the callable's type is known, so the call can be inlined.
template <typename Pred>
std::size_t count_if_tmpl(const std::vector<Point>& pts, Pred&& keep) {
    std::size_t n = 0;
    for (const auto& p : pts) if (keep(p)) ++n;
    return n;
}

void demo() {
    auto owner = std::make_unique<float>(1.5f);
    auto in_range = [lim = std::move(owner)](const Point& p) { return p.z < *lim; };
    std::vector<Point> pts{{0, 0, 1}, {0, 0, 2}};
    count_if_tmpl(pts, in_range);                // fine
    // count_if_erased(pts, in_range);           // error: std::function needs a copyable callable
}
```

`std::function` stores the callable behind a type-erased interface (day 46 shows how). That costs an indirect call that the optimizer usually cannot inline, and possibly a heap allocation when the callable is too large for the internal buffer. The buffer size is a library detail: with libstdc++ in GCC 12, a lambda capturing two `double`s is stored inline and one capturing three `double`s allocates once. It also requires the callable to be copy-constructible, so closures owning a `unique_ptr` are rejected. (C++23 adds `std::move_only_function` for that case.) The template version has none of those costs, but it must be visible in a header and is instantiated once per callable type.

#### in practice

A point-cloud preprocessing library exposes a filter step that takes a user predicate. The first API used `std::function<bool(const Point&)>`, because it compiles into a single function in a `.cpp` file and accepts anything. Profiling a 100,000-point cloud at 20 Hz showed the per-point indirect call in the hot loop, and the predicate's body could not be inlined or vectorized with the loop.

The fix is not "never use `std::function`". It is placing the type erasure where the call frequency is low. The library now takes a template parameter for the per-point predicate, and uses `std::function` for the per-frame "on cloud ready" callback, which fires twenty times a second and benefits from a stable, non-template, ABI-friendly signature. That is the general judgment: type erasure buys decoupling and a stable binary interface; templates buy inlining at the cost of compile time and header exposure. Pick per call site, and confirm with a profiler (day 50) that the hot path is really where you think it is.

#### watch out for

`[=]` reads as "copy everything", but inside a member function it captures `this`, a pointer, not the members:

```cpp
#include <functional>

struct JointController {
    double kp = 1.5;
    std::function<double(double)> law() {
        return [=](double err) { return kp * err; };   // BUG risk: really this->kp
    }
};
// auto f = JointController{}.law(); f(0.1);   // UB: the temporary controller is gone
```

The closure stores `this`, so calling it after the controller is destroyed is undefined behavior. Capture what you need explicitly (`[kp = kp]`), or copy the object with `[*this]` when it is small and copyable. C++20 deprecates the implicit capture of `this` through `[=]` for exactly this reason, and wants you to write `[=, this]` to say it out loud.

#### the takeaway

A lambda is a small class whose members are its captures. Ask the questions you would ask of any class: what does it own, what does it point to, and how long will it live? Use templates for hot-path callables and `std::function` at boundaries where flexibility is worth an indirect call.

#### optional challenge

On libstdc++, this removes two elements, not one. Why is that allowed?

```cpp
std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8, 9};
v.erase(std::remove_if(v.begin(), v.end(),
                       [n = 0](int) mutable { return ++n == 3; }),
        v.end());
// libstdc++ result: 1 2 4 5 7 8 9
```

<details>
<summary>answer</summary>

The predicate is a closure object, and algorithms are allowed to copy their predicates. libstdc++'s `remove_if` first passes a copy to an internal `find_if` to locate the first element to remove: that copy counts to 3 and finds the element `3`. The algorithm then continues scanning with its own, still-unused copy, whose counter starts from 0 again and hits 3 at element `6`. The standard lets algorithms copy function objects freely and requires a predicate to give the same answer for the same element no matter which copy is called or how often. A counting predicate breaks that requirement, so no result is guaranteed (formally, violating a library requirement is undefined behavior; in practice you get results like this one). Keep predicates stateless, or keep the state outside the closure and capture a reference to it when you truly need it.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-18"></a>

### day 18: templates: writing code for many types

**reading time:** about 10 minutes · **standard:** C++17 · **builds on:** days 01, 16, 17

#### the idea

```cpp
template <typename T>
T clamp_to(T v, T lo, T hi) { return v < lo ? lo : (hi < v ? hi : v); }

double speed = 12.5;
auto s = clamp_to(speed, 0, 10);  // error: deduced conflicting types for 'T' ('double' and 'int')
```

A function would have converted `0` and `10` to `double` without complaint. A template refuses. That refusal is the first rule of templates in action, and the rest of the model (instantiation, headers, specialization, the `typename` keyword nobody remembers to write) follows from taking templates for what they are: not functions or classes, but recipes the compiler uses to generate them.

#### understanding the concept

**Deduction comes before conversion.** For a function template call, the compiler first deduces `T` from each argument independently, and every deduction must agree. Implicit conversions are considered only after `T` is fixed. Here the first argument says `double` and the others say `int`, so deduction fails before conversion is ever considered. The fixes say different things: `clamp_to<double>(speed, 0, 10)` fixes `T` explicitly and lets conversions happen; `clamp_to(speed, 0.0, 10.0)` makes the arguments agree; separate parameters `template <typename T, typename U>` accept the mix but must then define what mixing means. `std::max(1, 2.0)` fails for the same reason.

**Instantiation happens where the template is used.** When the compiler sees `clamp_to<double>`, it stamps out a real function from the template body, which it can only do if the body is visible in that translation unit. That is why template definitions live in headers (day 01): put the body in a `.cpp` and every other translation unit gets an `undefined reference` at link time. Identical instantiations from different translation units are emitted as weak or COMDAT symbols and merged by the linker, so this does not violate the one definition rule. You can opt out with explicit instantiation: `template class RingBuffer<float, 64>;` in one `.cpp`, plus `extern template class RingBuffer<float, 64>;` in the header to stop every other translation unit from instantiating it again.

**Two-phase lookup.** A template is checked twice. At its definition, names that do not depend on a template parameter are looked up and bound, and obvious errors are reported. At instantiation, dependent names (anything involving `T`) are resolved. Because the compiler cannot know what `T::something` is before it knows `T`, you must tell it: `typename` marks a dependent name as a type, and `template` marks a dependent name as a member template.

**Before concepts, SFINAE.** If substituting a deduced type into a template's signature produces an invalid type or expression, that candidate silently drops out of overload resolution ("substitution failure is not an error"). `std::enable_if` exploits this to restrict a template:

```cpp
#include <type_traits>

template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
T half(T v) { return v / 2; }   // half(3.0) finds no viable function
```

It works, but the intent is buried in the syntax and the errors are poor. C++20 concepts (day 29) state the same constraint as `template <std::integral T>`, and `if constexpr` (day 23) replaces many overload-set tricks.

#### in code

A class template, with a non-type parameter for capacity, and C++17 class template argument deduction (CTAD) with a deduction guide:

```cpp
#include <array>
#include <cstddef>
#include <string>

template <typename T, std::size_t N>
class RingBuffer {
    static_assert(N > 0, "capacity must be positive");
    std::array<T, N> buf_{};
    std::size_t next_ = 0, count_ = 0;
public:
    void push(const T& v) { buf_[next_] = v; next_ = (next_ + 1) % N; if (count_ < N) ++count_; }
    std::size_t size() const { return count_; }
    static constexpr std::size_t capacity() { return N; }
};

RingBuffer<float, 64> imu_window;   // N is part of the type: <float, 64> and <float, 128> are unrelated

template <typename T>
class Setting {
public:
    Setting(std::string name, T value) : name_(std::move(name)), value_(std::move(value)) {}
    const T& value() const { return value_; }
private:
    std::string name_;
    T value_;
};
Setting(std::string, const char*) -> Setting<std::string>;   // deduction guide

Setting gain{"gain", 2.5};     // CTAD: Setting<double>
Setting mode{"mode", "auto"};  // without the guide: Setting<const char*>, storing a pointer
                               // with the guide:    Setting<std::string>, owning its text

template <auto Value>          // C++17: the parameter's type is deduced from the argument
struct Constant { static constexpr auto value = Value; };
static_assert(Constant<'x'>::value == 'x' && Constant<42u>::value == 42u);
```

CTAD reads the constructors and synthesizes deduction candidates from them, which is how `std::pair p{1, 2.0}`, `std::vector v{1, 2, 3}`, and `std::lock_guard lock{m}` work without angle brackets. A deduction guide adds a candidate when the constructor's parameter types do not say what you want deduced. Note that CTAD from aggregate initialization without a guide arrived only in C++20.

Specialization customizes a template for particular arguments. Class templates allow full and partial specialization. Function templates allow only full specialization, and even that is usually the wrong tool: overload instead.

```cpp
#include <string>

template <typename T>
struct Serializer {                 // primary template
    static std::string to_text(const T& v) { return std::to_string(v); }
};

template <>
struct Serializer<bool> {           // full specialization
    static std::string to_text(bool b) { return b ? "true" : "false"; }
};

template <typename T>
struct Serializer<T*> {             // partial specialization: any pointer
    static std::string to_text(const T* p) { return p ? Serializer<T>::to_text(*p) : "null"; }
};

template <typename T> std::string describe(const T& v) { return Serializer<T>::to_text(v); }
// template <typename T> std::string describe<T*>(T* p);  // error: function templates cannot
                                                          // be partially specialized
template <typename T> std::string describe(T* p) { return "ptr:" + Serializer<T*>::to_text(p); }  // overload instead
```

Dependent names, the part of templates that produces the most confusing errors:

```cpp
template <typename T>
struct Base { void reset() {} };

template <typename T>
struct Filter : Base<T> {
    void clear() {
        // reset();       // error: not found; the base depends on T, so phase one doesn't look there
        this->reset();    // OK: 'this->' makes the name dependent, looked up at instantiation
    }
};

template <typename Container>
auto first_or(const Container& c, typename Container::value_type fallback) {
    typename Container::const_iterator it = c.begin();   // 'typename': this dependent name is a type
    return it != c.end() ? *it : fallback;
}
```

`Base<T>` could be specialized later so that it has no `reset` at all, which is why the compiler refuses to look inside a dependent base during the first phase. Writing `this->` defers the lookup to instantiation, when the base is known. GCC 12's error says this almost directly: `there are no arguments to 'reset' that depend on a template parameter, so a declaration of 'reset' must be available`.

#### in practice

A robotics middleware team templated its message buffers on both element type and capacity, `MessageQueue<T, N>`, and used it across 60 translation units with a dozen distinct `(T, N)` pairs. Two costs showed up. Compile time: every translation unit that touched a queue re-instantiated the same member functions, and the parser had to chew through the full implementation each time. Binary size: `MessageQueue<Pose, 16>` and `MessageQueue<Pose, 32>` are entirely separate code even though only a constant differs.

The fixes were design decisions, not tricks. Capacity moved to a constructor argument (allocated once at startup), because nothing needed it at compile time; that collapsed the instantiation count by type. The handful of remaining instantiations were declared `extern template` in the header and explicitly instantiated in a single `.cpp`. The rule of thumb: make something a template parameter when the compiler genuinely benefits from knowing it (inline storage, type safety, unrolling, compile-time checks), and a runtime value when it merely varies. Measure the compile side with `-ftime-report` (GCC) or `-ftime-trace` (Clang), and the size side with `nm --size-sort` or a tool like Bloaty.

#### watch out for

Explicit specializations of function templates do not take part in overload resolution; only primary templates do. The result can surprise you:

```cpp
#include <iostream>

template <typename T> void f(T)  { std::cout << "a\n"; }
template <> void f<int*>(int*)   { std::cout << "b\n"; }   // specializes the first template
template <typename T> void f(T*) { std::cout << "c\n"; }

int main() { int x = 0; f(&x); }   // prints: c
```

Overload resolution picks between the two primary templates, chooses the more specialized `f(T*)`, and the specialization of `f(T)` is never considered. Which template a specialization belongs to depends on what was declared before it and how it is spelled: written as `template <> void f(int*)` below the second template, it specializes `f(T*)` and the call prints `b`. Prefer plain overloads for functions, and specialize class templates when you need per-type behavior that a function can forward to.

#### the takeaway

A template is a recipe the compiler runs per set of arguments: deduction is exact, instantiation needs the definition, and dependent names need your help. Every template parameter is a compile-time decision with compile-time and binary-size costs, so give the compiler only what it can actually use.

#### optional challenge

What type does `v` have, and how many elements does it hold?

```cpp
std::vector<int> inner{1, 2};
std::vector v{inner};
```

<details>
<summary>answer</summary>

`std::vector<int>` with 2 elements: a copy of `inner`. You might expect braces to prefer the `std::initializer_list` constructor and produce `std::vector<std::vector<int>>` with one element. But CTAD has a special rule: when the braced list holds a single element whose type is a specialization of the class template being deduced, the copy deduction candidate wins. With two elements, `std::vector w{inner, inner}`, you do get `std::vector<std::vector<int>>`. If you mean a vector of vectors, spell the type out.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-19"></a>

### day 19: forwarding references and perfect forwarding

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 05, 10, 18

#### the idea

You write a thin wrapper: it logs, then passes its argument on to a function that has a copy overload and a move overload. Callers hand it temporaries, so the move overload should run. It never does. Then you "fix" it with `std::move`, and now it quietly steals strings from callers who passed a named variable they still need. The wrapper needs to pass along not just the value but its value category, and that is precisely what forwarding references and `std::forward` are for.

#### understanding the concept

`T&&` means two different things. When `T` is a template parameter deduced from the call, `T&&` is a **forwarding reference** (the standard's term; Scott Meyers popularized "universal reference"). Anywhere else it is an ordinary rvalue reference.

```cpp
template <typename T> void f(T&& x);              // forwarding reference
auto&& r = make_value();                          // forwarding reference (auto deduces like T)
template <typename T> void g(std::vector<T>&& v); // rvalue reference: the parameter isn't exactly T&&
template <typename T> void h(const T&& x);        // rvalue reference: const disqualifies it
template <typename T> struct Box { void put(T&& x); };  // rvalue reference: T was fixed by the class
```

The trick is a special deduction rule plus reference collapsing. If the argument is an lvalue of type `U`, `T` is deduced as `U&`; if it is an rvalue, `T` is deduced as plain `U`. Substituting gives `U& &&` or `U&&`, and since references to references can't exist in source code, the compiler collapses them:

| `T` | `T&&` becomes | meaning |
|---|---|---|
| `U&` | `U& &&` → `U&` | caller passed an lvalue |
| `U&&` | `U&& &&` → `U&&` | (via explicit arguments or aliases) |
| `U` | `U&&` | caller passed an rvalue |

Any `&` in the mix wins; only `&& &&` stays `&&`. The upshot is that `T` *encodes* the caller's value category. Inside the function, though, `x` is a named variable, and a named variable is always an lvalue (day 05), whatever its declared type. To pass the caller's category on, you cast it back: `std::forward<T>(x)` is essentially `static_cast<T&&>(x)`. With `T = U&` that collapses to `U&` (an lvalue); with `T = U` it is `U&&` (an xvalue, so moves can happen). `std::move(x)` is the unconditional version: `static_cast<std::remove_reference_t<T>&&>(x)`, always an rvalue.

Variadic templates generalize this to any number of arguments. `typename... Args` declares a template parameter pack, `Args&&... args` a function parameter pack of forwarding references, and the pattern `std::forward<Args>(args)...` expands element-wise into a comma-separated list. `sizeof...(Args)` gives the count. That combination is the engine behind `std::make_unique`, `std::make_shared`, `std::thread`'s constructor, and every `emplace` function.

#### in code

The wrapper problem, three ways. Predict the output.

```cpp
#include <cstdio>
#include <string>
#include <utility>

void consume(const std::string&) { std::puts("copy"); }
void consume(std::string&&)      { std::puts("move"); }

template <typename T> void relay_named(T&& s) { consume(s); }             // s is an lvalue
template <typename T> void relay_moved(T&& s) { consume(std::move(s)); }  // always an rvalue
template <typename T> void relay(T&& s)       { consume(std::forward<T>(s)); }

int main() {
    std::string name = "lidar_front";
    relay_named(std::string{"tmp"});  // prints: copy  (a missed move)
    relay_moved(name);                // prints: move  (BUG: consume may now steal the caller's 'name')
    relay(name);                      // prints: copy
    relay(std::string{"tmp"});        // prints: move
}
```

A variadic factory that does some bookkeeping and then constructs in place. This is the shape of `make_unique` and of `emplace_back`, which forwards its arguments through the allocator to construct the element directly in the vector's storage.

```cpp
#include <memory>
#include <string>
#include <utility>

inline int g_created = 0;   // C++17 inline variable

template <typename T, typename... Args>
std::unique_ptr<T> make_tracked(Args&&... args) {
    static_assert(sizeof...(Args) <= 4, "keep constructors small");
    ++g_created;
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
    // expands to: new T(std::forward<A1>(a1), std::forward<A2>(a2), ...)
}

struct Joint {
    Joint(std::string name, double limit) : name(std::move(name)), limit(limit) {}
    std::string name;
    double limit;
};

void build() {
    std::string base = "elbow";
    auto a = make_tracked<Joint>(base, 2.6);           // base copied into Joint::name
    auto b = make_tracked<Joint>(base + "_2", 2.6);    // temporary moved into Joint::name
}
```

Note the parentheses in `new T(...)`. In C++17, parentheses cannot initialize an aggregate, so `std::make_unique<Point>(1.0, 2.0)` fails for `struct Point { double x, y; };`. C++20 (P0960) allows parenthesized aggregate initialization, and the same call compiles there.

`auto&&` in a range-for is the forwarding reference you use most often without noticing:

```cpp
#include <vector>

void arm_all(std::vector<bool>& flags) {
    // for (auto& f : flags) f = true;   // error: *it is a prvalue proxy, not a bool&
    for (auto&& f : flags) f = true;     // OK: binds to the proxy, assignment writes through it
}
```

`auto&&` binds to whatever the iterator yields: an lvalue reference for ordinary containers, a temporary proxy for `std::vector<bool>` or for views that compute values. In generic code, `for (auto&& x : range)` is the form that always compiles; use `const auto&` when you mean read-only.

#### in practice

A robot's command queue offers `post<Cmd>(Args&&... args)`, which constructs the command inside the queue's preallocated slot instead of building a temporary and moving it in. For most command types the saving is one move construction, which is cheap, so the honest reasons to prefer it are different: it works for types that are neither copyable nor movable (a command holding a `std::mutex`, say), and it keeps the call site short.

Two production costs come with it. First, every distinct combination of argument types is a separate instantiation, and forwarding references preserve exact types: `post<Log>("ok")` and `post<Log>("fail")` deduce `const char(&)[3]` and `const char(&)[5]`, two instantiations of the same function. In a header used everywhere, that shows up in compile time and binary size. Second, a forwarded argument can be consumed only once. The bug looks innocent:

```cpp
template <typename... Args>
void post_and_log(Args&&... args) {
    log_args(std::forward<Args>(args)...);   // may move from the arguments...
    post(std::forward<Args>(args)...);       // BUG: ...so this may receive moved-from objects
}
```

Pass by `const&` to everything except the last consumer, and forward only there.

#### watch out for

A constructor template taking a forwarding reference is greedier than you think. It can beat the copy constructor:

```cpp
#include <string>
#include <utility>

class Sensor {
public:
    template <typename S>
    explicit Sensor(S&& name) : name_(std::forward<S>(name)) {}
    Sensor(const Sensor&) = default;
private:
    std::string name_;
};

Sensor a{"lidar"};
Sensor b{a};   // error: picks the template with S = Sensor&, then tries std::string(Sensor&)
```

`a` is a non-const lvalue. The copy constructor needs a `const` qualification added; the template deduces `S = Sensor&` and matches exactly, so it wins overload resolution. Copying a `const Sensor` works; copying a non-const one fails to compile here, and in worse cases compiles into the wrong conversion. The same happens with classes derived from `Sensor`. Constrain the template (`std::enable_if_t<!std::is_base_of_v<Sensor, std::decay_t<S>>, int> = 0` in C++17, a `requires` clause in C++20), or, often better, drop the template and take `std::string name` by value and move it into the member. That costs one extra move and removes the whole problem, which is a good trade for anything that is not a hot path.

#### the takeaway

`T&&` with a deduced `T` remembers whether the caller passed an lvalue or an rvalue, and `std::forward<T>` replays that choice exactly once. Use perfect forwarding for factories, emplacement, and generic wrappers; use pass-by-value for ordinary "sink" parameters where simplicity beats the last move.

#### optional challenge

For `template <typename T> void f(T&& x);`, what are `T` and the type of `x` in each call?

```cpp
int i = 0;
const int ci = 0;
f(i);
f(ci);
f(42);
f(std::move(ci));
```

<details>
<summary>answer</summary>

- `f(i)`: lvalue `int`, so `T = int&` and `x` is `int&`.
- `f(ci)`: lvalue `const int`, so `T = const int&` and `x` is `const int&`. Constness is preserved, which is why forwarding never accidentally strips `const`.
- `f(42)`: prvalue, so `T = int` and `x` is `int&&`.
- `f(std::move(ci))`: xvalue of type `const int`, so `T = const int` and `x` is `const int&&`. You can't move from it in any useful way (day 10): a move constructor taking `T&&` won't bind, so a copy happens.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-20"></a>

### day 20: exception safety and error handling strategy

**reading time:** about 10 minutes · **standard:** C++17 · **builds on:** days 08, 10, 11

#### the idea

"Is this function exception-safe?" is the wrong question, because it has no yes-or-no answer. The useful question is: if something in here throws halfway through, what state is the object left in? A tracker whose index map disagrees with its track list, a config that is half old and half new, a robot with half of a new trajectory: these are not crashes, they are worse. They are valid-looking objects that lie. Exception safety is about making that question answerable, and an error-handling strategy is about deciding, per API, how failure is reported at all.

#### understanding the concept

There are three useful guarantees (Dave Abrahams' formulation, which the standard library documents its operations against):

| guarantee | promise if an exception escapes | example |
|---|---|---|
| **basic** | no leaks, all invariants hold, but the state may have changed | `std::vector::insert` in the middle |
| **strong** | commit or rollback: the state is as if the call never happened | `std::vector::push_back` (when the element's move is `noexcept` or it is copyable) |
| **nothrow** | the operation never fails | destructors, `swap`, `pop_back`, move constructors of most standard types |

Anything below basic (a broken invariant or a leak) is simply a bug. RAII (day 08) is what makes the basic guarantee cheap: if every resource is owned by an object, unwinding releases it without any `catch` blocks. The strong guarantee usually needs one more technique: **do all the work that can throw on the side, then commit with operations that cannot throw**. Copy-and-swap (day 11) is the classic form.

That commit step is why the nothrow guarantee matters, and why `noexcept` is a contract rather than an optimization hint. A function declared `noexcept` promises not to let an exception escape; if one tries, `std::terminate` is called, and whether the stack is unwound first is implementation-defined (with GCC 12, a local's destructor did not run before termination in a quick test). Callers can query the promise at compile time with the `noexcept(expr)` operator, and the library does: `std::vector` reallocation uses `std::move_if_noexcept`, so it moves elements only if their move constructor is `noexcept` (or the type cannot be copied), otherwise it copies to keep `push_back` strong (day 10).

Exceptions are not the only error channel, and choosing one is an API decision:

| mechanism | fits when | costs and limits |
|---|---|---|
| exceptions | failure is rare and the immediate caller can't handle it; constructors | throwing is slow and its latency hard to bound; unwind tables add binary size; invisible in signatures |
| error codes (`enum`, `std::error_code`) | failure is expected and handled close by; C interop; `-fno-exceptions` builds | easy to ignore (use `[[nodiscard]]`); constructors can't return them |
| `std::optional<T>` | "no result" needs no explanation (day 24) | carries no reason |
| result types (`std::variant<T, Error>`, day 25) | value or a reason, checked by the caller | more verbose call sites; `std::expected` is C++23 only |

On mainstream ABIs (Itanium-style table-based unwinding, used by GCC and Clang on Linux), a `try` block adds essentially no work to the non-throwing path (it can still constrain some optimizations). Throwing, though, allocates the exception object and searches unwind tables, so its cost is high and hard to bound. That is the honest basis for banning exceptions in hard real-time loops: not "exceptions are slow", but "a throw has no bounded latency". Many embedded projects go further and compile with `-fno-exceptions`, where `throw` and `try` in your code fail to compile, and failures the standard library reports by throwing (`std::bad_alloc`, `at()` out of range) end the program instead, because no handler can exist. The exact mechanism depends on how the library was built.

#### in code

A track table with two structures that must agree. The first version leaves a broken invariant if the second step throws.

```cpp
#include <stdexcept>
#include <unordered_map>
#include <vector>

struct Track { int id; double range_m; };

class TrackTable {
    std::vector<Track> tracks_;
    std::unordered_map<int, std::size_t> index_;   // invariant: index_[t.id] == position of t
public:
    void add_broken(Track t) {
        tracks_.push_back(t);                                 // may throw: fine, nothing changed
        index_.emplace(t.id, tracks_.size() - 1);             // may throw: BUG, track without index
    }

    void add(Track t) {                                       // strong guarantee
        if (index_.count(t.id)) throw std::invalid_argument("duplicate track id");
        tracks_.push_back(t);                                 // strong on its own
        try {
            index_.emplace(t.id, tracks_.size() - 1);
        } catch (...) {
            tracks_.pop_back();                               // rollback cannot throw
            throw;                                            // rethrow the original exception
        }
    }
};
```

The `try`/`catch` rollback is fine for one step. With more steps, a scope guard (day 08) that undoes on destruction unless dismissed keeps the code linear. A tempting alternative, `tracks_.reserve(tracks_.size() + 1)` before both steps, is a trap: calling it on every insert defeats geometric growth, because `reserve` may allocate exactly what you ask for, turning n inserts into O(n²) copying.

Do-the-work-then-commit, for a configuration reload:

```cpp
#include <string>
#include <utility>
#include <vector>

class ControllerConfig {
    std::vector<double> gains_;
    std::string profile_;
public:
    static ControllerConfig parse(const std::string& text);   // may throw on bad input

    void reload(const std::string& text) {
        ControllerConfig next = parse(text);   // all failure-prone work happens on the side
        swap(next);                            // commit: cannot throw
    }                                          // old state is destroyed with 'next'

    void swap(ControllerConfig& other) noexcept {
        gains_.swap(other.gains_);
        profile_.swap(other.profile_);
    }
};
```

The strong guarantee costs a second object alive during the reload. That is cheap for a config and expensive for a 50 MB map, which is why the standard library gives only the basic guarantee for some operations: it refuses to charge every caller for rollback that most don't need.

#### in practice

A robot arm driver library had one error convention everywhere: throw. That was right for `Arm::connect()`, called once at startup, where failure means the process cannot do its job and a clear exception with context is the best report. It was wrong for `Arm::read_joint_states()`, called at 1 kHz from the control loop, where a dropped packet is an expected event and the loop must decide within its cycle budget whether to hold position.

The revised API used a different channel per situation: `connect()` throws, the cyclic read returns a `[[nodiscard]]` status plus data, and constructors establish their invariants or throw. The rule behind it: decide by how expected the failure is, who can act on it, and the latency budget, then document the choice and apply it consistently per layer. Two habits to avoid while you are at it: using exceptions for ordinary control flow (ending a parse loop by catching), and `catch (...) {}` that swallows a failure nobody will ever see. Also avoid catching, logging, and rethrowing at every layer, which produces five log lines for one error.

#### watch out for

Throw by value, catch by `const&`, and rethrow with a bare `throw;`:

```cpp
#include <cstdio>
#include <stdexcept>

void handle() {
    try {
        throw std::out_of_range("joint index 7");
    } catch (std::exception e) {   // BUG: copies and slices to std::exception (GCC: -Wcatch-value)
        std::puts(e.what());       // prints implementation-defined text; libstdc++: "std::exception"
        throw e;                   // throws a new std::exception: the out_of_range is gone
    }
}
```

Catching by value slices the derived exception (day 13) and loses its message; `throw e;` then throws that sliced copy, so callers catching `std::out_of_range` miss it. `catch (const std::exception& e)` and `throw;` preserve the original object and its dynamic type.

#### the takeaway

Every operation should give at least the basic guarantee, and RAII makes that nearly free. Pay for the strong guarantee where callers need commit-or-rollback, and build it from throwing work done on the side plus a `noexcept` commit. Choose the error channel per API from how expected the failure is and how quickly someone must react.

#### optional challenge

Which guarantee does this give, and how would you make it strong?

```cpp
void Planner::set_waypoints(const std::vector<Pose>& w) {
    waypoints_.clear();
    for (const auto& p : w) waypoints_.push_back(p);
}
```

<details>
<summary>answer</summary>

Basic only. If a `push_back` throws partway, `waypoints_` holds a prefix of the new path: valid, no leaks, but neither the old nor the new state, which for a robot is the dangerous kind of valid. `waypoints_ = w;` looks like the fix but is not guaranteed to be strong either, because vector copy assignment may reuse its existing storage element by element. The strong version copies first and commits with a non-throwing swap: `std::vector<Pose> next(w); waypoints_.swap(next);`. The price is holding both vectors briefly.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-21"></a>

### day 21: week 3 review: the library as a vocabulary

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 15 to 20

#### recap

| day | key idea |
|---|---|
| [15](#day-15) | A container is a contract: complexity, layout, and invalidation rules. Start with `std::vector`; reference stability is part of the interface. |
| [16](#day-16) | Algorithms see iterators, not containers: hence half-open ranges, erase-remove, `back_inserter`, and iterator categories. |
| [17](#day-17) | A lambda is an object whose members are its captures. Escaping lambdas must own what they use; `std::function` buys flexibility with an indirect call. |
| [18](#day-18) | Templates are recipes: deduction is exact, instantiation needs the definition, dependent names need `typename` and `this->`. |
| [19](#day-19) | `T&&` with deduced `T` remembers the caller's value category; `std::forward<T>` replays it, once. |
| [20](#day-20) | Basic, strong, nothrow: RAII makes basic cheap, work-then-commit makes strong possible, and the error channel is an API decision. |

The thread through the week: the standard library is a set of small, composable contracts, and generic code is how those contracts stay independent of the types they serve.

#### review questions

1. You keep `Track*` pointers into a `std::unordered_map<int, Track>`. A burst of inserts triggers a rehash. Which of your pointers and iterators are still valid? What changes if someone replaces the map with a `std::vector<Track>` kept sorted by id?

2. Predict the output:

   ```cpp
   std::vector<int> v{5, 1, 4, 2, 3};
   int threshold = 2;
   auto above = [threshold](int x) { return x > threshold; };
   threshold = 4;
   std::cout << std::count_if(v.begin(), v.end(), above) << '\n';
   ```

3. Which of these parameters are forwarding references?

   ```cpp
   template <class T> void a(T&& x);
   template <class T> void b(const T&& x);
   template <class T> struct S { void c(T&& x); };
   template <class T> void e(std::vector<T>&& x);
   auto&& d = make_frame();
   ```

4. A vector of `Waypoint` copies every element when it grows, even though `Waypoint` has a move constructor. What is the most likely cause, and why does the library do this on purpose?

5. **From week 1.** Given the code below, is `a` safe to use on the next line? Is `b`?

   ```cpp
   struct Config {
       std::string name_;
       const std::string& name() const { return name_; }
   };
   Config load();

   const std::string& a = load().name_;
   const std::string& b = load().name();
   ```

6. **From week 2.** A teammate adds `~Telemetry() { log("closed"); }` to an otherwise rule-of-zero class holding a `std::vector<Sample>`. Everything still compiles. What did that change cost?

#### mini exercise

This function is supposed to drop invalid detections, apply a range calibration, and return the ids of the three closest. It has two bugs, one of them undefined behavior. Rewrite it with algorithms and lambdas, keep it correct for fewer than three detections, and decide where a plain loop is still the clearest choice.

```cpp
#include <algorithm>
#include <vector>

struct Detection { int id; float range_m; bool valid; };

std::vector<int> closest_ids(std::vector<Detection>& dets, float scale) {
    for (auto it = dets.begin(); it != dets.end(); ++it) {
        if (!it->valid) dets.erase(it);
        else it->range_m *= scale;
    }
    std::sort(dets.begin(), dets.end(),
              [](const Detection& a, const Detection& b) { return a.range_m < b.range_m; });
    std::vector<int> ids;
    for (std::size_t i = 0; i < 3; ++i) ids.push_back(dets[i].id);
    return ids;
}
```

#### answers

<details>
<summary>1. unordered_map rehash versus vector</summary>

Pointers and references to elements of an `unordered_map` stay valid across a rehash, because elements live in separate nodes and only the bucket array is rebuilt. Iterators are invalidated. With a sorted `std::vector<Track>`, any insertion invalidates references and iterators at or after the insertion point, and a reallocation invalidates all of them. The swap compiles, so the bug appears only at run time. Stable ids instead of pointers keep the container choice free (day 15).

</details>

<details>
<summary>2. predict the output</summary>

It prints `3` (the elements 5, 4, and 3). `[threshold]` copies the value when the lambda expression is evaluated, so the closure holds 2; changing the local afterwards has no effect. With `[&threshold]` it would print `1` (only 5 exceeds 4). A by-value capture is a snapshot (day 17).

</details>

<details>
<summary>3. forwarding references</summary>

Only `a` and `d`. `b` is an rvalue reference to `const` (the `const` disqualifies it). `c` is an ordinary rvalue reference, because `T` is fixed by the class, not deduced from the call. `e` is an rvalue reference to `std::vector<T>`, because the parameter is not exactly `T&&`. `auto&&` follows the same deduction rule as `T&&` (day 19).

</details>

<details>
<summary>4. copying on reallocation</summary>

`Waypoint`'s move constructor is probably not `noexcept` (often because it was hand-written, or because a member's move is not `noexcept`). Reallocation uses `std::move_if_noexcept`: if moving could throw halfway, some elements would already be moved out of the old buffer and `push_back` could no longer promise the strong guarantee. Copying keeps the old buffer intact until the new one is complete. Mark the move constructor `noexcept` (or `= default` it, so it inherits the members' `noexcept`), and check with `static_assert(std::is_nothrow_move_constructible_v<Waypoint>)` (days 10 and 20).

</details>

<details>
<summary>5. from week 1: lifetime extension</summary>

`a` is safe; `b` dangles. Binding a reference to a member of a temporary through the built-in `.` operator extends the lifetime of the whole temporary `Config`. Binding to a reference *returned by a function* does not: the compiler cannot see that `name()` returns a part of the temporary, so the temporary dies at the end of the full-expression and `b` refers to a destroyed string. Using `b` is undefined behavior (day 03). The same reasoning explains why a lambda capturing a reference to a member of a temporary dangles.

</details>

<details>
<summary>6. from week 2: a user-declared destructor</summary>

Declaring a destructor suppresses the implicitly declared move constructor and move assignment. The copy operations are still generated (that generation is deprecated, but it happens), so every "move" of a `Telemetry` silently becomes a copy of the whole sample vector: when returned from some functions, when stored in containers, and on every reallocation. Fix it by deleting the destructor and logging from a member whose own destructor does the work, or by defaulting all five special members explicitly (day 11). This is the rule of zero protecting performance as well as correctness.

</details>

<details>
<summary>mini exercise: one possible solution</summary>

The bugs: `dets.erase(it)` invalidates `it`, so the `++it` that follows is undefined behavior (and, even if it worked, the element after an erased one would be skipped). And `dets[i]` reads past the end when fewer than three detections survive, which is also undefined behavior.

```cpp
#include <algorithm>
#include <cstddef>
#include <iterator>
#include <vector>

struct Detection { int id; float range_m; bool valid; };

std::vector<int> closest_ids(std::vector<Detection> dets, float scale, std::size_t k = 3) {
    dets.erase(std::remove_if(dets.begin(), dets.end(),
                              [](const Detection& d) { return !d.valid; }),
               dets.end());
    for (auto& d : dets) d.range_m *= scale;   // a plain loop is the clearest form here

    k = std::min(k, dets.size());
    const auto mid = dets.begin() + static_cast<std::ptrdiff_t>(k);
    std::partial_sort(dets.begin(), mid, dets.end(),
                      [](const Detection& a, const Detection& b) { return a.range_m < b.range_m; });

    std::vector<int> ids;
    ids.reserve(k);
    std::transform(dets.begin(), mid, std::back_inserter(ids),
                   [](const Detection& d) { return d.id; });
    return ids;
}
```

Design notes: taking `dets` by value makes the mutation private (a caller that no longer needs its vector can `std::move` it in, and nobody is surprised by a reordered input). `std::partial_sort` orders only the first `k` elements, O(n log k) instead of O(n log n). The scaling loop stays a loop because `std::transform` in place, or `std::for_each`, would add syntax without adding meaning. In C++20, the first statement becomes `std::erase_if(dets, ...)`.

</details>

#### connections

Week 3 rests on the first two weeks. Forwarding references (day 19) are value categories (day 05) put to work, and `std::forward` is a cousin of the `std::move` cast from day 10. Exception safety (day 20) is RAII (day 08) seen from the failure path, and the vector's choice between copying and moving on reallocation ties `noexcept` move constructors (day 10) to the strong guarantee. Iterator invalidation (day 15) is the lifetime rules of day 03 applied to containers.

It also sets up the next five weeks. Week 4 shortens much of this week's code: structured bindings unpack `try_emplace` results (day 22), `if constexpr` and fold expressions replace SFINAE and recursive packs (day 23), and `std::optional` and `std::variant` (days 24 and 25) become error channels for the strategy from day 20. Week 5 replaces `enable_if` with concepts (day 29) and iterator pairs with ranges (day 30). Lambdas return in week 6 as thread bodies, where capture lifetime gets even less forgiving, and `std::function`'s type erasure gets taken apart on day 46. Finally, every "measure it" this week becomes a concrete method on days 50 to 52.

[back to table of contents](#table-of-contents)

---

<a id="week-4"></a>

## week 4: modernizing with c++17

The C++17 features that change day-to-day code, ending with a practical refactoring. After this week the reader has a complete standalone refresher.

<a id="day-22"></a>

### day 22: structured bindings, init-statements, and helpful attributes

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days 03, 15

#### the idea

Look at a typical pre-C++17 map lookup: an iterator declared at function scope, a comparison against `end()`, then `it->first` and `it->second` sprinkled through the body. Nothing is wrong with it, but the names say nothing (`first` of what?), and `it` stays in scope long after it stopped being meaningful. Week 4 opens with the small C++17 features that fix exactly this kind of noise. None of them is deep on its own; together they change how ordinary code reads, and the next six days build on them.

#### understanding the concept

**Structured bindings** let you give names to the parts of an object:

```cpp
auto [it, inserted] = counters.try_emplace(topic);
```

The mechanics matter more than the syntax. The compiler introduces a hidden variable, call it `e`, initialized from the right-hand side exactly as if you had written `auto e = counters.try_emplace(topic);`. The names `it` and `inserted` then refer to parts of `e`. Everything written before the brackets (`auto`, `const auto&`, `auto&&`) applies to `e`, not to the individual names. (C++17 also forbids `static`, `thread_local`, and `constexpr` on a structured binding; C++20 allows the first two.)

There are three ways a type can be decomposed:

| kind | example | what the names refer to |
|---|---|---|
| array | `int a[3]` | the elements of `e` |
| tuple-like | `std::pair`, `std::tuple`, `std::array` | the results of `get<i>(e)`, via the tuple protocol |
| aggregate-ish class | `struct Pose { double x, y, theta; };` | the non-static data members of `e`, in declaration order |

The class case requires all non-static data members to be public and declared in the same class (or the same base). Your own non-aggregate types can opt in by specializing `std::tuple_size`, `std::tuple_element`, and providing `get`; that is rarely worth the boilerplate.

Two consequences follow from "names for parts of a hidden object":

- `auto [a, b] = obj;` copies the whole of `obj` into `e`. `auto& [a, b] = obj;` binds `e` to `obj`. And because `e` follows the normal rules from day 03, `const auto& [a, b] = make_pair_func();` extends the temporary's lifetime for as long as `e` lives.
- The names are not variables in the usual sense. `decltype(a)` yields the declared type of the member (`double`, not `double&`), and in C++17 a lambda cannot capture a structured binding. C++20 lifted that restriction. GCC 12 quietly accepts the capture even in `-std=c++17 -pedantic` mode, and other compilers in C++17 mode reject it or warn, so portable C++17 code uses an init-capture: `[a = a]`.

**Init-statements** for `if` and `switch` (also C++17) let you declare a variable whose scope is the whole statement, including the `else` branch:

```cpp
if (auto it = m.find(key); it != m.end()) { /* use it */ } else { /* it is still in scope */ }
```

It is the same scoping rule `for` always had. The point is not saving a line; it is that a reader knows `it` cannot affect anything after the closing brace.

Finally, three **standard attributes** became part of daily use in C++17. `[[nodiscard]]` asks the compiler to warn when a return value is ignored; it can go on a function or on a type, in which case every function returning that type by value is covered. `[[maybe_unused]]` silences unused warnings on a variable, parameter, or function. `[[fallthrough]]` documents an intentional fall-through in a `switch`. All three are hints: the standard only encourages a diagnostic, and the program's meaning never changes.

#### in code

First, predict the output. The binding names look like independent variables, but they are not.

```cpp
#include <cstdio>
#include <type_traits>

struct Pose { double x, y, theta; };

int main() {
    Pose p{1.0, 2.0, 0.5};

    auto [x, y, th] = p;       // hidden copy of p; x, y, th name its members
    x = 10.0;                  // modifies the copy

    auto& [rx, ry, rth] = p;   // hidden reference to p
    ry = 20.0;                 // modifies p.y

    std::printf("%.1f %.1f %.1f\n", x, p.x, p.y);         // prints: 10.0 1.0 20.0
    static_assert(std::is_same_v<decltype(ry), double>);   // not double&
}
```

Second, a before/after modernization of a lookup in a joint-gain table.

```cpp
#include <cstdio>
#include <map>
#include <string>

// before: C++03 style
bool find_gain(const std::map<std::string, double>& gains,
               const std::string& joint, double& out) {
    std::map<std::string, double>::const_iterator it = gains.find(joint);
    if (it == gains.end())
        return false;
    out = it->second;
    return true;
}

// after: C++17
[[nodiscard]] bool find_gain(const std::map<std::string, double>& gains,
                             const std::string& joint, double& out) {
    if (auto it = gains.find(joint); it != gains.end()) {
        out = it->second;
        return true;
    }
    return false;
}

void dump(const std::map<std::string, double>& gains) {
    for (const auto& [joint, gain] : gains)          // instead of p.first, p.second
        std::printf("%s: %.3f\n", joint.c_str(), gain);
}
```

The `[[nodiscard]]` is the most valuable change here: with an out-parameter, a caller who ignores the `bool` and uses `out` anyway may read an uninitialized `double`, which is undefined behavior (day 06). Now they at least get a warning. The out-parameter itself is still awkward; day 24 replaces it with `std::optional<double>`.

Third, `switch` with an initializer plus the other two attributes:

```cpp
#include <cassert>

enum class Mode { idle, homing, tracking, fault };

struct Controller {
    Mode mode() const;
    void zero_encoders();
    void run_loop();
    [[nodiscard]] bool push(double sample);
};

void step(Controller& c, double sample) {
    switch (auto m = c.mode(); m) {
    case Mode::homing:
        c.zero_encoders();
        [[fallthrough]];               // deliberate: homing also runs the loop
    case Mode::tracking:
        c.run_loop();
        break;
    case Mode::idle:
    case Mode::fault:
        break;
    }
    [[maybe_unused]] const bool ok = c.push(sample);
    assert(ok);                        // with NDEBUG, ok would otherwise be "unused"
}
```

Without `[[fallthrough]]`, GCC and Clang warn under `-Wimplicit-fallthrough` (enabled by `-Wextra` in GCC). Empty case labels stacked together, like `idle` and `fault`, never need it.

#### in practice

A telemetry aggregator receives messages tagged with a topic string and keeps per-topic statistics. The hot path is "find or create the entry, then update it", and C++17 lets that read as one thought:

```cpp
#include <cstdint>

struct Stats { std::uint64_t count = 0; double last = 0.0; };

void on_message(std::map<std::string, Stats>& stats, const std::string& topic, double value) {
    auto [it, inserted] = stats.try_emplace(topic);   // one lookup, no default-then-assign
    if (inserted)
        std::printf("new topic: %s\n", topic.c_str());
    auto& [count, last] = it->second;
    ++count;
    last = value;
}
```

`try_emplace` (day 15) returns `pair<iterator, bool>`; naming those parts `it` and `inserted` removes a whole category of `.first.second` confusion. The second binding uses `auto&` so updates land in the map rather than in a copy. Note the design aspect: the binding names are local documentation, but they are not part of `Stats`'s interface. Rename a member and nothing breaks here; reorder members and something does, which brings us to the trap.

#### watch out for

Bindings to a class are **positional**. They follow member declaration order, not names:

```cpp
struct Range { double min_m, max_m; };
auto [lo, hi] = gate.range;          // lo = min_m, hi = max_m

// six months later someone "tidies" the struct:
struct Range { double max_m, min_m; };   // BUG: lo and hi silently swap
```

Because both members are `double`, every use still compiles and no warning fires. Field access by name (`r.min_m`) is immune. So use structured bindings freely for `pair`, `tuple`, map entries, and small local aggregates whose layout is effectively fixed (a 2D point). For a struct that lives in a widely used header and may evolve, member access is the more robust coupling. The same applies to returning a `std::tuple<double, double, double>` from an API: the bindings at the call site are only as good as everyone's memory of the order. A named struct is usually the better contract.

#### the takeaway

A structured binding names the parts of one hidden object; the qualifiers apply to that object, and the names follow member order. Pair it with `if`/`switch` initializers to keep helper variables scoped to the decision they serve, and use `[[nodiscard]]` on anything whose result must not be dropped.

#### optional challenge

What does this print, and why does the second loop compile even though `k` would have to be a `const std::string`?

```cpp
std::map<std::string, int> m{{"a", 1}};
for (auto [k, v] : m) v += 10;
std::printf("%d\n", m["a"]);
for (auto& [k, v] : m) v += 10;
std::printf("%d\n", m["a"]);
```

<details>
<summary>answer</summary>

It prints `1`, then `11`. In the first loop the hidden object is a copy of each `std::pair<const std::string, int>`, so `v += 10` modifies the copy. In the second loop the hidden object is an `auto&` bound to the map's element. The `auto&` deduces `std::pair<const std::string, int>&`, so `k` names a `const std::string` member and `v` names a mutable `int`. The `const` comes from the element type, not from the binding, which is why `auto&` works here without any `const` written by you.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-23"></a>

### day 23: compile-time branching with `if constexpr` and fold expressions

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 18, 19

#### the idea

You are writing a telemetry encoder that appends fields to a byte buffer. Arithmetic values are copied as raw bytes, enums go out as their underlying integer, strings get a length prefix. Before C++17, "do something different depending on the type" inside a template meant an overload set guarded by `std::enable_if` or a tag-dispatch helper, which scatters one decision across several functions and produces error messages nobody enjoys. C++17 lets you write the decision as a plain branch, evaluated at compile time, and lets you apply an operator across a whole parameter pack without recursion.

#### understanding the concept

`if constexpr (cond)` requires `cond` to be a constant expression convertible to `bool` (narrowing conversions are not allowed). Its defining property is what happens to the branch that is not taken: **inside a template**, when the condition is known at instantiation, the discarded branch is not instantiated. Code in it may be invalid for the current `T` (calling `v.size()` on an `int`, say) and that is fine, because it is never compiled for that `T`.

Two limits follow from "not instantiated" rather than "not compiled at all":

- The discarded branch is still parsed. Syntax errors and errors that do not depend on a template parameter are diagnosed.
- Outside a template there is nothing to instantiate, so both branches are fully checked. `if constexpr` in a normal function behaves like `if` with a constant condition (with the minor difference that entities only used in the discarded branch need no definition).

A useful side effect: `return` statements in a discarded branch do not take part in return type deduction, so an `auto` function can return different types for different `T`.

**Fold expressions** apply a binary operator across a parameter pack (day 19). There are four forms, and the parentheses are part of the syntax:

| form | written | expands to (for `a, b, c`) |
|---|---|---|
| unary right | `(xs op ...)` | `a op (b op c)` |
| unary left | `(... op xs)` | `(a op b) op c` |
| binary right | `(xs op ... op init)` | `a op (b op (c op init))` |
| binary left | `(init op ... op xs)` | `((init op a) op b) op c` |

A unary fold over an empty pack is ill-formed except for three operators: `&&` gives `true`, `||` gives `false`, and the comma operator gives `void()`. For anything else, use a binary fold with an identity value. The comma fold is the workhorse for "do this for every argument": the built-in comma operator sequences its operands left to right, so `(f(xs), ...)` calls `f` in argument order. Contrast that with function arguments, whose evaluation order is still unspecified (day 06).

Finally, `constexpr` functions. C++14 already allowed local variables, loops, and mutation inside them; C++17 added `constexpr` lambdas and `if constexpr`. Still forbidden in C++17: `try` blocks, virtual calls, dynamic allocation, `static` locals, and uninitialized local variables (C++20 relaxes most of these; day 33). A `constexpr` function is *allowed* to run at compile time; it is *required* to only where a constant expression is needed, such as a `static_assert`, an array bound, or a template argument. And in constant evaluation, core-language undefined behavior such as signed overflow is a compile error rather than a silent miscompile.

#### in code

The encoder, before and after. The "before" splits one decision across three overloads:

```cpp
#include <cstdint>
#include <cstring>
#include <string>
#include <type_traits>
#include <vector>

using Buffer = std::vector<std::uint8_t>;

namespace before {   // C++14: SFINAE picks an overload
template <class T, std::enable_if_t<std::is_arithmetic<T>::value, int> = 0>
void put(Buffer& b, T v) {
    std::uint8_t raw[sizeof v];
    std::memcpy(raw, &v, sizeof v);        // native byte order
    b.insert(b.end(), raw, raw + sizeof v);
}
template <class T, std::enable_if_t<std::is_enum<T>::value, int> = 0>
void put(Buffer& b, T v) { put(b, static_cast<std::underlying_type_t<T>>(v)); }
inline void put(Buffer& b, const std::string& s) {
    put(b, static_cast<std::uint32_t>(s.size()));
    b.insert(b.end(), s.begin(), s.end());
}
}  // namespace before
```

After: one function, the decision in one place, and a deliberate error for anything else.

```cpp
template <class> inline constexpr bool always_false = false;

template <class T>
void put(Buffer& b, const T& v) {
    if constexpr (std::is_arithmetic_v<T>) {
        std::uint8_t raw[sizeof v];
        std::memcpy(raw, &v, sizeof v);    // native byte order
        b.insert(b.end(), raw, raw + sizeof v);
    } else if constexpr (std::is_enum_v<T>) {
        put(b, static_cast<std::underlying_type_t<T>>(v));
    } else if constexpr (std::is_same_v<T, std::string>) {
        put(b, static_cast<std::uint32_t>(v.size()));
        b.insert(b.end(), v.begin(), v.end());
    } else {
        static_assert(always_false<T>, "put: unsupported field type");
    }
}
```

With a plain `if`, every branch would be instantiated for every `T`: `put(b, 42)` would try to compile `v.size()` on an `int` and fail. With `if constexpr`, `put(b, 42)` instantiates only the first branch.

Now folds. Predict the two results before reading the comments:

```cpp
#include <cmath>
#include <iostream>

template <class... Ts> int lsub(Ts... xs) { return (... - xs); }   // ((1 - 2) - 3)
template <class... Ts> int rsub(Ts... xs) { return (xs - ...); }   // (1 - (2 - 3))

template <class... Ts> auto sum(Ts... xs) { return (xs + ... + 0); }          // empty pack: 0
template <class... Ts> bool all_finite(Ts... xs) { return (std::isfinite(xs) && ...); }

template <class... Ts>
void log_line(const Ts&... xs) {
    ((std::cout << xs << ' '), ...);   // comma fold: guaranteed left to right
    std::cout << '\n';
}

int main() {
    std::cout << lsub(1, 2, 3) << ' ' << rsub(1, 2, 3) << '\n';   // prints: -4 2
    std::cout << sum() << ' ' << sum(1, 2.5) << '\n';             // prints: 0 3.5
    std::cout << all_finite(1.0, NAN) << '\n';                    // prints: 0
    log_line("imu", 3, 0.25);                                     // prints: imu 3 0.25
}
```

`&&` and `||` folds short-circuit just like the operators they expand to, so `all_finite` stops at the first non-finite value.

#### in practice

Put the two together and a whole telemetry frame becomes one line per message type, with the type checks done by the compiler:

```cpp
enum class Mode : std::uint8_t { idle, tracking, fault };

template <class... Fields>
Buffer encode(std::uint16_t msg_id, const Fields&... fields) {
    Buffer b;
    put(b, msg_id);
    (put(b, fields), ...);               // one put per field, in order
    return b;
}

Buffer frame = encode(0x21, Mode::tracking, 12.5f, std::string("base_link"));
// 2 (id) + 1 (mode) + 4 (float) + 4 (length) + 9 (chars) = 20 bytes
```

Passing a `std::vector<int>` as a field fails at compile time with the `static_assert` message rather than a page of overload-resolution notes. The costs are real but usually acceptable: every distinct list of field types instantiates a new `encode` (code size and compile time), and the format is native-endian, which is fine for same-host IPC and wrong for a wire protocol. Measure compile time with `-ftime-report` (GCC) or `-ftime-trace` (Clang) if a header like this starts to dominate builds.

There is also a design judgment hiding here. The `if constexpr` chain is a **closed set**: supporting a new field type means editing `put`. That is a feature when the encoder owns the format and every type must be reviewed. If users of a library should be able to add their own types, an overload or a trait they can specialize is the better seam, because it is open for extension without touching your code. Day 25 meets the same closed-versus-open tradeoff at runtime.

#### watch out for

The obvious way to write the "unsupported type" branch does not work:

```cpp
template <class T>
void put(Buffer& b, const T& v) {
    if constexpr (std::is_arithmetic_v<T>) { /* ... */ }
    else static_assert(false, "unsupported");   // BUG in C++17 and C++20
}
```

`false` does not depend on `T`, so the assertion can never succeed for any instantiation, and a non-dependent assertion is checked when the template is defined, not when a branch is chosen. Under the C++17 and C++20 rules the template is ill-formed, and GCC 12 rejects it even if `put` is never called. The fix is to make the condition dependent, as in `always_false<T>` above. C++23 (paper P2593) changed the rule so that `static_assert(false)` is only evaluated when the branch is instantiated; GCC 13 and Clang 17 implement it, but on a C++17 or C++20 code base, keep the dependent-false helper.

#### the takeaway

`if constexpr` skips instantiation, not parsing, and only inside templates; folds turn "for each argument" into one expression whose order and empty-pack behavior you choose. Together they replace most SFINAE overload sets and recursive variadic helpers, at the cost of putting a closed set of cases in one place.

#### optional challenge

Which of these compile when called with no arguments, and what do they return?

```cpp
template <class... Ts> auto a(Ts... xs) { return (xs + ...); }
template <class... Ts> auto b(Ts... xs) { return (xs && ...); }
template <class... Ts> auto c(Ts... xs) { return (0 + ... + xs); }
```

<details>
<summary>answer</summary>

`a()` does not compile: a unary fold over `+` with an empty pack is ill-formed. `b()` compiles and returns `true` (type `bool`), because `&&` is one of the three operators with a defined empty value. `c()` compiles and returns `0` (type `int`), because a binary fold just yields its initial value when the pack is empty. Note that `c` is a left fold; for `+` on numbers the direction does not change the value, but it does change the order of evaluation and, with mixed types, the intermediate types.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-24"></a>

### day 24: `std::optional`: modeling "maybe"

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days 04, 20, 22

#### the idea

Every code base has its own dialect for "there might not be a value": `-1` for "not found", `NaN` for "no reading", a `bool` return plus an out-parameter, a null pointer to a heap object that did not need to be on the heap. Each dialect has a failure mode. `-1` is a valid value for some other caller, `NaN` poisons arithmetic silently, and the out-parameter (day 22's `find_gain`) leaves the caller holding an uninitialized `double` if they forget the check. C++17's `std::optional<T>` gives "maybe a `T`" a single, typed spelling that the compiler understands.

#### understanding the concept

`std::optional<T>` (header `<optional>`) holds either a `T` or nothing. The storage for the `T` lives *inside* the optional object, next to a flag: no heap allocation, and an empty optional has not constructed a `T` at all. The size is implementation-specific; it is at least `sizeof(T)` plus room for the flag, rounded up for alignment (`sizeof(std::optional<double>)` is 16 on mainstream 64-bit ABIs).

The access API is small, and the differences between its members are the whole point:

| expression | if engaged | if empty |
|---|---|---|
| `o.has_value()`, `if (o)` | `true` | `false` |
| `*o`, `o->m` | the value | undefined behavior |
| `o.value()` | the value | throws `std::bad_optional_access` |
| `o.value_or(d)` | a copy of the value | `d` converted to `T` |

`*o` is unchecked by design, like `vector::operator[]`; use it right after you have tested the optional. `value()` is the checked version, and `value_or` is for the common case of a sensible fallback. Note that `value_or`'s argument is always evaluated, so `o.value_or(load_default_from_disk())` does the I/O even when `o` is engaged.

You create an empty optional with `std::nullopt` (or `{}`), and an engaged one by assigning a `T` or constructing in place: `o.emplace(args...)` and `std::optional<T> o(std::in_place, args...)` construct the `T` directly in the optional's storage, which matters for types that are expensive or impossible to move.

There is no `std::optional<T&>` in C++17 (it is ill-formed; C++26 adds it). For "maybe refers to an existing object", a `T*` is the idiomatic answer and already means exactly that (day 04).

Comparisons are defined between optionals, against `std::nullopt`, and against plain `T` values, with one rule to remember: an empty optional compares less than any engaged one.

Finally, the design meaning. Returning `std::optional<T>` is a contract: "absence is a normal outcome and you must handle it". That is different from an exception (day 20), which says "this should not happen in normal operation". What optional cannot say is *why* the value is missing; when callers need the reason, use a result type (day 25) or an exception.

#### in code

Day 22's out-parameter lookup, finished:

```cpp
#include <map>
#include <optional>
#include <string>

[[nodiscard]] std::optional<double>
find_gain(const std::map<std::string, double>& gains, const std::string& joint) {
    if (auto it = gains.find(joint); it != gains.end())
        return it->second;
    return std::nullopt;
}

void apply_gain(double);

void configure(const std::map<std::string, double>& gains) {
    if (auto kp = find_gain(gains, "elbow"))      // kp is scoped to the if
        apply_gain(*kp);                          // checked just above: * is fine
    double kd = find_gain(gains, "wrist").value_or(0.1);
    apply_gain(kd);
}
```

The caller cannot read the value without going through the optional, and the type says "may be missing" in the signature instead of in a comment.

Now predict the output. Two of these surprise most people.

```cpp
#include <iostream>
#include <optional>
#include <string>

int main() {
    std::optional<int> a;            // empty
    std::optional<int> b = 0;
    std::cout << (a < b) << (a < -100) << (b == 0) << '\n';   // prints: 111

    try {
        std::cout << a.value() << '\n';
    } catch (const std::bad_optional_access& e) {
        std::cout << "empty\n";                                // prints: empty
    }

    std::optional<std::string> s = "fix";
    auto t = std::move(s);
    std::cout << s.has_value() << '\n';                        // prints: 1
}
```

`a < -100` is `true` because empty is less than every value, including negative ones; a range check like `if (reading < limit)` on an optional quietly passes when there is no reading. And moving from an optional does not make it empty: `s` is still engaged and holds a moved-from string (valid but unspecified, day 10). If you need it empty, call `s.reset()`.

In-place construction for a type that should not be copied around:

```cpp
#include <optional>

struct Track {
    Track(int id, double range_m, double vel_mps) : id(id), range_m(range_m), vel_mps(vel_mps) {}
    Track(const Track&) = delete;            // tracks have identity; no accidental copies
    Track& operator=(const Track&) = delete;
    int id; double range_m; double vel_mps;
};

std::optional<Track> lead;                   // no Track constructed yet
void on_new_target(int id, double r, double v) {
    lead.emplace(id, r, v);                  // destroys any old Track, builds the new one in place
}
```

#### in practice

In a localization node, a GNSS fix is genuinely optional: you may not have one yet, or it may be too old to trust. That is exactly what a member should model:

```cpp
class Localizer {
public:
    void on_gnss(const GnssFix& fix) { last_fix_ = fix; }
    [[nodiscard]] std::optional<Pose> pose_at(Timestamp t) const;  // empty if no usable fix
private:
    std::optional<GnssFix> last_fix_;        // "never received" is distinct from any fix value
};
```

Compare the alternatives. A `GnssFix` with a `valid` flag lets every reader forget to check it. A `std::unique_ptr<GnssFix>` adds a heap allocation and pointer semantics for no ownership benefit. The optional keeps the data inline and makes the check visible.

Parameters are a different story. `void configure(std::optional<Limits> limits = std::nullopt)` constructs an optional (and copies the `Limits`) at every call, and the function body is one big `if`. Two overloads, `configure()` and `configure(const Limits&)`, are usually clearer. If the argument is a borrowed object that may be absent, `const Limits*` says that with no copy at all.

#### watch out for

`std::optional<bool>` and `std::optional<T*>` turn a one-character mistake into a logic bug:

```cpp
std::optional<bool> brake_engaged = read_brake_sensor();   // empty on sensor timeout

if (brake_engaged)                 // BUG: means "we got a reading", not "brake is on"
    release_parking_hold();

if (brake_engaged.value_or(true))  // fixed, and the fallback is a safety decision:
    release_parking_hold();        // treat "unknown" as "engaged"
```

The contextual conversion to `bool` tests engagement, whatever `T` is. With `std::optional<bool>`, `if (o == true)` or `value_or` make the intent explicit, and the fallback value deserves a comment because it encodes policy. With `std::optional<Sensor*>` you have two kinds of nothing (`nullopt` and `nullptr`); unless those genuinely mean different things in your domain, a plain pointer is simpler. Some static analyzers flag these patterns; compilers generally do not.

C++23 note: `and_then`, `transform`, and `or_else` (the "monadic" operations) let you chain optional-returning steps without nested `if`s. They are not in C++17 or C++20.

#### the takeaway

Use `std::optional<T>` when absence is a normal, expected outcome: it stores the value inline, puts "maybe" in the type, and makes the check hard to skip. Remember that `*` is unchecked, empty compares less than everything, moved-from optionals stay engaged, and `if (o)` never looks at the value inside.

#### optional challenge

A radar driver exposes `std::optional<std::vector<Detection>> detections()`. A reviewer suggests returning a plain `std::vector<Detection>` and using an empty vector for "nothing". When is the reviewer right, and when is the optional worth keeping?

<details>
<summary>answer</summary>

If "no scan happened" and "the scan found no targets" are handled the same way by every caller, the empty vector is simpler and the optional is just an extra layer to unwrap. If they mean different things (a tracker should coast tracks through a missing scan but may delete them after a genuinely empty scan), then the distinction is real information and the optional is the honest return type. And if callers need to know *why* there was no scan (timeout, CRC error, blanking interval), neither is enough: that is a job for a result type (day 25) or an exception.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-25"></a>

### day 25: `std::variant` and `std::any`: sum types and type-erased values

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 13, 17, 20, 24

#### the idea

A radar front end emits three kinds of messages: raw detections, track updates, and heartbeats. The pre-C++17 options were all uncomfortable. A C `union` plus a tag `enum` is fast but nothing stops you reading the wrong member (undefined behavior) or forgetting to destroy a `std::string` member. A `Message` base class with three subclasses (day 13) is safe but heap-allocates every message, adds pointer chasing, and invites `dynamic_cast` ladders in the consumer. Day 24's `std::optional` was "a `T` or nothing". Today is the generalization: "exactly one of these types", with the compiler keeping track of which.

#### understanding the concept

`std::variant<A, B, C>` (header `<variant>`) holds exactly one value of one of its alternative types, stored inline (no heap allocation by the variant itself), plus an index saying which one. Its size is at least that of the largest alternative plus room for the index. Assigning a different alternative destroys the old value and constructs the new one, so the lifetime bugs of a raw union cannot happen.

Access comes in three strengths:

- `std::holds_alternative<T>(v)` and `v.index()` ask what is there.
- `std::get<T>(v)` (or `std::get<I>(v)`) returns a reference and throws `std::bad_variant_access` on a mismatch.
- `std::get_if<T>(&v)` returns a pointer, `nullptr` on a mismatch. This is the non-throwing "check and use" form.

The idiomatic way to consume a variant, though, is `std::visit(f, v)`, which calls `f` with the active alternative. If `f` cannot be called with one of the alternatives, the program does not compile, which gives you exhaustiveness checking for free. The usual way to build `f` from several lambdas (day 17) is the `overloaded` helper:

```cpp
template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };
template <class... Fs> overloaded(Fs...) -> overloaded<Fs...>;   // needed in C++17 only
```

It inherits from every lambda's closure type and pulls in all their call operators, so normal overload resolution picks the right one. In C++17 the deduction guide is required; C++20 lets CTAD deduce template arguments for aggregates directly, so the second line becomes unnecessary (though harmless).

Three details complete the picture. A default-constructed variant holds a value-initialized first alternative, so the first type must be default constructible, or you put `std::monostate` first as an explicit "empty" alternative. If constructing the new alternative throws after the old one was destroyed, the variant becomes `valueless_by_exception()`: `index()` returns `std::variant_npos` and `visit` throws `bad_variant_access`. This needs a throwing constructor or move to occur mid-assignment, which is rare, but it means a variant's "always one of the types" invariant has one documented escape hatch. Finally, the set of alternatives is fixed at compile time, which is the design decision that matters most.

**Closed versus open.** With inheritance, adding a new message type means writing one new class, but adding a new operation means touching every class (or adding a virtual function to the base). With a variant, adding an operation is one new visitor, but adding a type means updating every visitor, and the compiler will point at each one. This is the "expression problem" in one paragraph. Use a variant when the set of types is small, known, and owned by you (protocol messages, states, parse results). Use virtual functions when the set must be open to code you do not control (plugins, user-supplied sensors). Variants also give you value semantics: they copy, compare, and live in a `std::vector` contiguously.

`std::any` (header `<any>`) is the other end of the spectrum: it holds a single value of *any* copy-constructible type, with the type erased. You get it back with `std::any_cast<T>`, which must name the exact stored type (no conversions, no base classes). Small objects may be stored inline; whether and how much is implementation-specific, and larger types are heap-allocated. Because the type information is gone from the interface, every reader has to guess and check. Legitimate uses are narrow: a framework that carries a user's context object through code that never looks inside it, or a heterogeneous property bag at a plugin boundary. If you can list the possible types, you want a variant.

#### in code

The radar messages as a variant, with an exhaustive visitor:

```cpp
#include <cstdint>
#include <cstdio>
#include <variant>

struct Detection   { float range_m, azimuth_deg, snr_db; };
struct TrackUpdate { int id; float range_m, vel_mps; };
struct Heartbeat   { std::uint32_t seq; };
using RadarMsg = std::variant<Detection, TrackUpdate, Heartbeat>;

void handle(const RadarMsg& m) {
    std::visit(overloaded{
        [](const Detection& d)   { std::printf("det %.1f m\n", d.range_m); },
        [](const TrackUpdate& t) { std::printf("trk %d\n", t.id); },
        [](const Heartbeat& h)   { std::printf("hb %u\n", static_cast<unsigned>(h.seq)); },
    }, m);
}

int main() {
    RadarMsg m = TrackUpdate{7, 1520.0f, -3.2f};
    handle(m);                                       // prints: trk 7
    if (auto* t = std::get_if<TrackUpdate>(&m))      // pointer form: no exception
        t->vel_mps = 0.0f;
    m = Heartbeat{42};                               // old TrackUpdate destroyed
    handle(m);                                       // prints: hb 42
}
```

Delete the `Heartbeat` lambda and `std::visit` fails to compile: no call operator accepts a `Heartbeat`. That error is the feature. (A generic `[](const auto&) {}` catch-all silences it, and with it, the exhaustiveness check.)

A variant as a result type, the error-handling option promised on day 20. It carries the reason that `std::optional` could not:

```cpp
#include <string>
#include <string_view>

struct ParseError { std::size_t column; std::string what; };
using ParseResult = std::variant<Detection, ParseError>;

ParseResult parse_detection(std::string_view line);

void ingest(std::string_view line) {
    auto r = parse_detection(line);
    if (auto* err = std::get_if<ParseError>(&r)) {
        std::printf("bad line at column %zu: %s\n", err->column, err->what.c_str());
        return;
    }
    const Detection& d = std::get<Detection>(r);
    std::printf("det %.1f m\n", d.range_m);
}
```

This works, but it is clunky: nothing in the type says which alternative is the success case. C++23's `std::expected<T, E>` is the purpose-built version; on C++17 many code bases use a small `Result<T, E>` wrapper or a library such as `tl::expected`.

And `std::any`, to see why it is the last resort:

```cpp
#include <any>

std::any a = 42;
int*  p = std::any_cast<int>(&a);    // ok: pointer form, exact type
long* q = std::any_cast<long>(&a);   // nullptr: int is not long, no conversion
double d = std::any_cast<double>(a); // throws std::bad_any_cast
```

#### in practice

Variants make good state machines because each state carries only the data that is meaningful in that state. A robot arm controller:

```cpp
struct Idle   {};
struct Moving { double target_rad; double started_s; };
struct Fault  { std::string reason; };
using ArmState = std::variant<Idle, Moving, Fault>;

ArmState step(const ArmState& s, double now_s, double pos_rad) {
    return std::visit(overloaded{
        [](const Idle&) -> ArmState { return Idle{}; },
        [&](const Moving& m) -> ArmState {
            if (std::abs(pos_rad - m.target_rad) < 1e-3) return Idle{};
            if (now_s - m.started_s > 5.0)               return Fault{"move timeout"};
            return m;
        },
        [](const Fault& f) -> ArmState { return f; },   // only an explicit reset leaves Fault
    }, s);
}
```

Compare the usual alternative: one struct with a `state` enum plus `target_rad`, `started_s`, and `reason` fields, all present all the time. There, nothing stops code from reading `reason` while `Idle` or forgetting to clear `started_s`. With the variant, those states are unrepresentable. The explicit `-> ArmState` return types matter: without them, the lambdas would return `Idle`, `Moving`, and so on, and `visit` requires every call to return the same type.

#### watch out for

The converting constructor picks an alternative by overload resolution, and implicit conversions can surprise you:

```cpp
std::variant<std::string, bool> v = "abc";   // which alternative?
```

Under the original C++17 wording this stored `bool`: `const char*` to `bool` is a standard conversion and beat the user-defined conversion to `std::string`. C++20 (paper P0608) excluded narrowing and boolean conversions from this selection, so it now stores the `std::string`. GCC 12's libstdc++ applies the fix even with `-std=c++17` (index 0, checked), but older standard libraries do not. The robust habits: avoid alternatives that convert into each other (`bool`, `int`, `double` together is asking for trouble), and when in doubt, say what you mean with `std::in_place_type<std::string>` or by constructing the alternative explicitly.

#### the takeaway

`std::variant` is a closed, value-semantic sum type: inline storage, an exhaustive `visit`, and unrepresentable invalid states. Reach for it when you own a small, fixed set of types, keep virtual functions for open sets, and treat `std::any` as a tool for code that genuinely must not know the type.

#### optional challenge

Your team adds a fourth radar message, `Calibration`. With the variant design, what does the compiler do for you, and what does it not do? What would the answer be with a `Message` base class and virtual `handle()`?

<details>
<summary>answer</summary>

With the variant, every `std::visit` built from explicit per-type lambdas stops compiling until it handles `Calibration`, so the compiler hands you a list of places to update. It does not help where someone used a generic `auto` catch-all lambda or `get_if` checks, which silently ignore the new type. With the base class, adding `Calibration` means writing one class and implementing the pure virtuals; existing consumers compile unchanged, which is great if they never need to know, and a silent gap if some of them should have treated calibration specially. Closed sets trade "edit many places" for "the compiler finds them"; open sets trade the opposite way.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-26"></a>

### day 26: `std::string_view` and non-owning views

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 03, 04, 22, 24

#### the idea

`void log_topic(const std::string& topic)` looks like the efficient way to accept a read-only string. Now call it with a literal, `log_topic("/robot/arm/joint_states")`. The parameter needs a `std::string`, so the compiler builds a temporary one, which allocates if the text is longer than the small-string buffer (an implementation-defined capacity, 15 characters in libstdc++). Call it with a substring of a larger buffer and you must first copy that substring into a `std::string`. The function only wanted to *read* some characters. C++17's `std::string_view` lets it say exactly that.

#### understanding the concept

A `std::string_view` (header `<string_view>`) is a pointer and a length, nothing more. It does not own the characters, never allocates, and is cheap to copy, so you pass it by value. Three properties define how you use it:

- **It borrows.** The characters belong to someone else (a `std::string`, a literal, a receive buffer, a memory-mapped file). The view is valid only while that owner is alive and unmodified. This is the same contract as a reference or raw pointer (day 04), with the same failure mode: dangling.
- **It is not necessarily null-terminated.** A view of `"x=1,y=2"` from offset 0, length 3 sees `x=1`, but the byte after it is `,`. There is no `c_str()` for a reason.
- **Slicing is free.** `substr`, `remove_prefix`, and `remove_suffix` just adjust the pointer and length: O(1), no allocation. (`std::string::substr` returns a new string; `std::string_view::substr` returns a new view.)

Conversions are asymmetric, and that is good API design: `std::string` converts *implicitly* to `std::string_view` (cheap and safe while the string lives), while `std::string_view` converts to `std::string` only *explicitly* (`std::string(sv)`), because that allocates and you should see it.

The parsing partners are `std::from_chars` and `std::to_chars` (header `<charconv>`, C++17). Unlike `std::stod` or `strtod`, they take a `[first, last)` character range (perfect for a view), never allocate, never throw, ignore the locale, and report errors through a returned `{ptr, ec}` struct, which unpacks neatly with a structured binding (day 22). `from_chars` does not skip leading whitespace or accept a leading `+`. Integer support is universal; floating-point support arrived later in some standard libraries (libstdc++ has it from GCC 11), so check your toolchain before relying on it.

#### in code

Before and after for a read-only parameter:

```cpp
#include <map>
#include <string>
#include <string_view>

// before: a literal or substring argument materializes a std::string first
bool is_tf_topic(const std::string& topic) { return topic.compare(0, 4, "/tf/") == 0; }

// after: accepts std::string, literals, and slices of other buffers, no allocation
bool has_prefix(std::string_view s, std::string_view prefix) {
    return s.substr(0, prefix.size()) == prefix;    // C++20 adds s.starts_with(prefix)
}

// bonus: heterogeneous lookup in an ordered map (C++14 std::less<>) takes a view directly
std::map<std::string, int, std::less<>> rates{{"imu", 200}, {"gnss", 10}};
int rate_of(std::string_view topic) {
    auto it = rates.find(topic);                   // no std::string temporary
    return it != rates.end() ? it->second : 0;
}
```

With the default `std::less<std::string>`, `rates.find(topic)` would not compile from a view; you would have to write `rates.find(std::string(topic))` and allocate. `std::unordered_map` gets the equivalent (a transparent hash plus `std::equal_to<>`) only in C++20.

The missing null terminator bites at C boundaries:

```cpp
#include <cstdio>

void open_log(std::string_view path) {
    std::FILE* f = std::fopen(path.data(), "r");   // BUG: data() need not be null-terminated
    // ...
}

void open_log_fixed(std::string_view path) {
    const std::string p(path);                     // one explicit copy, guaranteed terminator
    std::FILE* f = std::fopen(p.c_str(), "r");
    // ...
}
```

If `path` is a slice of `"a.log,b.log"`, the buggy version passes `fopen` a pointer whose string continues past `a.log` to the comma and beyond. That is not even a clean failure: `fopen` reads until it happens to find a zero byte. When an API needs a C string, either take `const std::string&` (or `const char*`) in the signature, or make the copy explicit as above.

#### in practice

NMEA 0183 sentences from a GNSS receiver are short comma-separated ASCII lines. A tool that ingests hours of logs parses millions of them, and the naive version allocates a `std::string` per field. With views, the parser touches each byte once and allocates nothing:

```cpp
#include <charconv>
#include <optional>
#include <string_view>

std::string_view next_field(std::string_view& rest) {
    const auto comma = rest.find(',');
    const auto field = rest.substr(0, comma);          // npos: the whole remainder
    rest.remove_prefix(comma == std::string_view::npos ? rest.size() : comma + 1);
    return field;
}

std::optional<double> to_double(std::string_view s) {
    double v{};
    auto [ptr, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
    if (ec != std::errc{} || ptr != s.data() + s.size())   // reject "12.5abc" and ""
        return std::nullopt;
    return v;
}

// "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
std::optional<double> gga_altitude_m(std::string_view sentence) {
    for (int i = 0; i < 9; ++i) next_field(sentence);  // skip to field 9
    return to_double(next_field(sentence));            // 545.4
}
```

Notice how week 4 is composing: views for the slices, a structured binding for the `from_chars` result, `std::optional` for "this field may be empty or garbage". Whether it is measurably faster than a `std::string`-based parser depends on line lengths and the allocator; count allocations (day 52 shows how) and profile before claiming a speedup. The design gain is certain either way: the parser's signature says it borrows the line and keeps nothing.

#### watch out for

Every `string_view` bug is a lifetime bug, and none of these produce a warning from GCC 12 at `-Wall -Wextra`:

```cpp
std::string_view sv = std::string("base") + "_link";  // BUG: the temporary string dies at the ';'

std::string_view make_name(int id) {
    std::string s = "trk_" + std::to_string(id);
    return s;                                         // BUG: view into a destroyed local
}

class Topic {
    std::string_view name_;                           // borrowed: who keeps the characters alive?
public:
    explicit Topic(std::string_view n) : name_(n) {}
};
Topic t{std::string("imu")};                          // BUG: name_ dangles immediately
```

Reading through any of these views is undefined behavior. Day 03's lifetime-extension rule does not rescue you: extension applies when a *reference* binds directly to a temporary, but a `string_view` is an object that merely holds a pointer into it. Clang flags some of these patterns with its `-Wdangling` family of warnings, and AddressSanitizer catches the reads at runtime, but the reliable defense is a rule: use `string_view` for parameters and for short-lived locals, and store `std::string` in members unless the class is explicitly a borrowing view type with a documented lifetime contract. Also remember that a view into a `std::string` is invalidated by anything that may reallocate that string, just like a vector iterator (day 15).

`std::string_view` is the first of the standard's **non-owning views**. Day 31's `std::span` does the same for contiguous arrays of any type, and C++20 ranges views (day 30) generalize the idea. The design question is always the same: does this component *own* the data, or *borrow* it for the duration of a call?

#### the takeaway

`std::string_view` is a borrowed pointer and length: ideal for read-only parameters and zero-copy parsing, wrong for anything that outlives the call unless the owner provably outlives it. Make copies to `std::string` explicit, and never hand `data()` to a function that expects a null terminator.

#### optional challenge

Is there a lifetime bug here? Would changing the parameter to `std::string_view` fix it or make it worse?

```cpp
std::vector<std::string_view> split(const std::string& line);   // views into line
auto parts = split(read_line());                                // read_line() returns std::string
for (auto p : parts) use(p);
```

<details>
<summary>answer</summary>

Yes. `read_line()` returns a temporary `std::string`; it binds to the `const std::string&` parameter and dies at the end of the full-expression, so every view in `parts` dangles before the loop starts (undefined behavior to read). Changing the parameter to `std::string_view` does not fix it and arguably hides it better, because the signature now advertises "I accept anything" while returning views into whatever you passed. Fixes: keep the line in a named variable that outlives `parts` (`const auto line = read_line(); auto parts = split(line);`), or have `split` return `std::vector<std::string>` when callers cannot be trusted with the lifetime. Some code bases also add a deleted overload `split(std::string&&) = delete;` to reject temporaries at compile time.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-27"></a>

### day 27: `std::filesystem` and a practical C++17 refactoring

**reading time:** about 10 minutes · **standard:** C++17 · **builds on:** days 20, 22, 24, 26

#### the idea

Somewhere in your code base there is a function that scans a directory with `opendir`, glues paths together with `+ "/" +`, parses lines with `std::string::substr`, and reports failure through a `bool` and two out-parameters. It works, it is not portable to Windows, and nobody wants to touch it. Today we add the last C++17 library piece of this week, `std::filesystem`, and then use everything from days 22 to 26 to modernize that function, one justified change at a time.

#### understanding the concept

`std::filesystem` (header `<filesystem>`, conventionally aliased `namespace fs = std::filesystem;`) standardizes what used to be POSIX `dirent.h`, Win32 `FindFirstFile`, or Boost.Filesystem. On GCC 8 it needed `-lstdc++fs` at link time; from GCC 9 it is part of the main library.

`fs::path` is a value type holding a path in the platform's native format (`char` on POSIX, `wchar_t` on Windows). You compose with `/`, and you decompose with `filename()`, `stem()`, `extension()`, and `parent_path()`. These are pure string operations: they never touch the disk. Converting back to `std::string` with `.string()` may have to transcode on Windows, so pass `fs::path` itself to APIs that accept it, including `std::ifstream`, whose constructor takes a `path` since C++17.

Operations that do touch the disk (`exists`, `is_regular_file`, `file_size`, `create_directories`, `rename`, `remove`, iteration) come in two overloads:

- without an error argument, they throw `fs::filesystem_error`, which carries the paths and an `std::error_code`;
- with a trailing `std::error_code& ec`, they report failure through `ec` instead.

Choose per call site with day 20's rule: if the failure is exceptional for this program (the config directory is missing at startup), throw; if it is an expected outcome (a file vanished from a drop directory between scans), use the `error_code` overload.

Two semantic details trip people up. `fs::directory_iterator` and `fs::recursive_directory_iterator` visit entries in an **unspecified order**: it is whatever the file system returns, and it differs between machines. And the file system is shared mutable state: another process can change it between any two of your calls, which is the subject of today's watch-out.

#### in code

The basics, with no I/O until the last line:

```cpp
#include <filesystem>
#include <iostream>
namespace fs = std::filesystem;

int main() {
    const fs::path root = "/var/log/robot";
    const fs::path log = root / "arm" / "joint_states.2026-10-30.csv";
    std::cout << log.filename() << ' ' << log.stem() << ' ' << log.extension() << '\n';
    // prints: "joint_states.2026-10-30.csv" "joint_states.2026-10-30" ".csv"
    std::error_code ec;
    const auto bytes = fs::file_size(log, ec);              // no throw
    if (ec) std::cout << "no file: " << ec.message() << '\n';
    else    std::cout << bytes << " bytes\n";
}
```

The quotes come from `operator<<` for `path`, which writes the path quoted (as if by `std::quoted`) so that paths with spaces round-trip. Use `.string()` when you want the raw text.

Now the legacy loader. It reads `key = value` lines from every `*.conf` file in a directory:

```cpp
// before: C++03 style, POSIX only
#include <dirent.h>
#include <fstream>
#include <map>
#include <string>

std::string trim(const std::string& s);   // the usual hand-written helper

bool load_configs(const char* dir, std::map<std::string, std::string>& out,
                  std::string& err) {
    DIR* d = opendir(dir);
    if (!d) { err = "cannot open directory"; return false; }
    while (struct dirent* e = readdir(d)) {
        std::string name = e->d_name;
        if (name.size() < 5 || name.substr(name.size() - 5) != ".conf") continue;
        std::ifstream in((std::string(dir) + "/" + name).c_str());
        std::string line;
        while (std::getline(in, line)) {
            std::string::size_type eq = line.find('=');
            if (line.empty() || line[0] == '#' || eq == std::string::npos) continue;
            out[trim(line.substr(0, eq))] = trim(line.substr(eq + 1));
        }
    }
    closedir(d);
    return true;
}
```

And after, in C++17:

```cpp
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>
namespace fs = std::filesystem;

using Config = std::map<std::string, std::string, std::less<>>;

std::string_view trim(std::string_view s) {
    const auto first = s.find_first_not_of(" \t\r");
    if (first == std::string_view::npos) return {};
    return s.substr(first, s.find_last_not_of(" \t\r") - first + 1);
}

std::optional<std::pair<std::string_view, std::string_view>> parse_line(std::string_view line) {
    line = trim(line);
    const auto eq = line.find('=');
    if (line.empty() || line.front() == '#' || eq == std::string_view::npos)
        return std::nullopt;
    return std::pair{trim(line.substr(0, eq)), trim(line.substr(eq + 1))};
}

[[nodiscard]] Config load_configs(const fs::path& dir) {
    std::vector<fs::path> files;
    for (const auto& entry : fs::directory_iterator(dir))       // throws fs::filesystem_error
        if (entry.is_regular_file() && entry.path().extension() == ".conf")
            files.push_back(entry.path());
    std::sort(files.begin(), files.end());                      // make "last file wins" deterministic

    Config cfg;
    for (const auto& file : files) {
        std::ifstream in(file);
        if (!in) throw std::runtime_error("cannot open " + file.string());
        for (std::string line; std::getline(in, line);)
            if (auto kv = parse_line(line)) {
                auto [key, value] = *kv;
                cfg.insert_or_assign(std::string(key), std::string(value));
            }
    }
    return cfg;
}
```

#### in practice

Each change, and why:

| change | why |
|---|---|
| `opendir`/`readdir` to `fs::directory_iterator` | portable, and no `closedir` to forget on an early return (RAII) |
| string concatenation to `fs::path` and `extension()` | correct separators, no off-by-one suffix check |
| `bool` plus `err` out-parameter to an exception | a missing config directory at startup is exceptional (day 20) |
| out-parameter map to a returned `Config` with `[[nodiscard]]` | the result is the point of the call; returning a local costs at most a move, and NRVO usually removes even that (day 05) |
| `parse_line` returning `std::optional` of a pair of views | a pure, testable function; "not a key-value line" is a normal outcome, not an error |
| structured bindings for the key and value | names instead of `.first` and `.second` |
| sorting the file list | `readdir` order made duplicate keys across files resolve differently per machine |

Be honest about one thing: a refactoring is supposed to preserve behavior, and three behaviors changed here. Duplicate keys now resolve in sorted file order, an unreadable file now throws instead of being skipped silently, and an indented `# comment` is now treated as a comment. Each one is an improvement, and each one belongs in the commit message and in a characterization test written *before* the refactor (day 54 covers that discipline at scale).

One change was deliberately **not** made. The views returned by `parse_line` are tempting to store directly, with a `std::map<std::string_view, std::string_view>`, to avoid the two string copies per line. That would be a dangling bug (day 26): the views point into `line`, which is overwritten on the next `getline` and destroyed when the loop ends. The map must own its strings. The views are the right tool *inside* the parse, and the copies happen exactly once, at the ownership boundary. A second non-change: no parallel parsing and no `std::unordered_map`. A handful of config files at startup is not a performance problem, and changing the container would change the iteration order other code may depend on.

#### watch out for

The classic file-system bug is **check-then-use**, a time-of-check to time-of-use (TOCTOU) race:

```cpp
if (fs::exists(p) && fs::file_size(p) > max_bytes)   // BUG: p can vanish or change in between
    fs::remove(p);
```

Between `exists` and `file_size`, a log rotator can delete or replace the file, and `file_size` then throws. Worse, in security-sensitive code, an attacker can swap `p` for a symlink between the check and the `remove`. The checks do not make the operation safe; they only narrow the window. Prefer to attempt the operation and handle the failure:

```cpp
std::error_code ec;
if (const auto size = fs::file_size(p, ec); !ec && size > max_bytes)
    fs::remove(p, ec);          // still racy in principle, but never throws, and ec reports what happened
```

Truly atomic guarantees come from the operating system (opening a file once and working on the handle, `O_CREAT | O_EXCL`, an atomic `rename` to publish a file), not from `std::filesystem`, which only names paths.

#### the takeaway

`std::filesystem` gives you portable paths and directory operations with a choice of exceptions or error codes per call. A good modernization is a sequence of small, individually justified changes, with behavior changes stated openly and owning types kept at ownership boundaries even when views are tempting.

#### optional challenge

A colleague wants to call `load_configs` every five seconds from a hot-reload thread. During deployments the directory briefly disappears. What would you change in the API, and what would you keep?

<details>
<summary>answer</summary>

A missing directory is now an expected outcome, so throwing and catching every five seconds would be exceptions as control flow (day 20). Add a non-throwing entry point, for example `std::optional<Config> try_load_configs(const fs::path& dir, std::error_code& ec)`, built on the `error_code` overloads of `directory_iterator` and `is_regular_file`, and have the reload thread keep the last good `Config` when it gets `std::nullopt`. Keep the throwing `load_configs` for startup, where failing loudly is correct, ideally implemented on top of the non-throwing version so the parsing logic exists once. If callers need to tell "directory missing" from "file unreadable" from "parse error", the `error_code` (or a variant result from day 25) carries that reason; a bare optional would not.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-28"></a>

### day 28: week 4 review: a complete C++17 refresher

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 22 to 27

#### recap

| day | idea in one line |
|---|---|
| 22 | A structured binding names the parts of one hidden object; qualifiers apply to that object, names follow member order. `if`/`switch` initializers scope helpers to the decision; `[[nodiscard]]` makes ignored results visible. |
| 23 | `if constexpr` skips *instantiation* of the untaken branch, only inside templates. Folds apply an operator across a pack; only `&&`, `||`, and `,` accept an empty pack in unary form. Use a dependent false, not `static_assert(false)`, before C++23. |
| 24 | `std::optional<T>` stores "maybe a `T`" inline. `*` is unchecked, `value()` throws, empty compares less than everything, and `if (o)` tests engagement, never the value. |
| 25 | `std::variant` is a closed, value-semantic sum type with exhaustive `visit`; virtual functions suit open sets; `std::any` is for code that must not know the type. |
| 26 | `std::string_view` is a borrowed pointer and length: great for parameters and zero-copy parsing, dangerous anywhere it can outlive its owner, and not null-terminated. |
| 27 | `std::filesystem` gives portable paths and a per-call choice of exceptions or `error_code`. Modernize in small, justified steps; state behavior changes; keep owning types at ownership boundaries. |

##### checkpoint: the refresher is complete

This is the halfway mark, and the end of the course's standalone refresher. If you stopped here, you would have the full working model of modern C++17: how source becomes a program and what the standard does and does not promise (week 1), who owns every resource and how objects move (week 2), the library and template machinery that the standard library itself is built from (week 3), and the C++17 vocabulary types that make interfaces say what they mean (week 4). A quick self-test: can you explain, without notes, why a `std::string_view` member is riskier than a `std::string` member, why `std::vector` cares whether your move constructor is `noexcept`, and why an unconstrained template's error messages are so long? If yes, the second half will feel like extensions of things you already understand. Weeks 5 to 8 build on this base: the C++20 toolbox, concurrency, design, and production engineering.

#### review questions

1. Does `auto& [id, range] = make_track();` compile if `make_track()` returns a `std::pair<int, double>` by value? What about `const auto&` and `auto&&`, and what happens to the pair's lifetime in those cases?

2. You write `else static_assert(false, "unsupported type");` as the last branch of an `if constexpr` chain in a function template. GCC 12 rejects the file even though no call ever reaches that branch. Why, and what is the C++17 fix?

3. A guard reads `if (latest_temp_c < max_temp_c) keep_running();` where `latest_temp_c` is `std::optional<double>` and `max_temp_c` is a `double`. What happens when no temperature has been received, and how would you rewrite it?

4. Your team is designing the message type for a planner that receives `Goal`, `Cancel`, and `MapUpdate` messages, all defined by your team. A colleague proposes a `Message` base class with virtual `apply()`. Make the case for `std::variant` instead, and name one situation where the base class would be the better choice.

5. What is wrong with this member function, and what is the smallest fix?

   ```cpp
   class Frame {
       std::string prefix_ = "base";
       std::string id_ = "link";
   public:
       std::string_view name() const { return prefix_ + "_" + id_; }
   };
   ```

6. **From week 1.** `const std::string& a = std::string("x") + "y";` and `std::string_view b = std::string("x") + "y";` look alike. Which one is safe to use on the next line, and why does the rule from day 03 treat them differently?

7. **From week 3.** In `template <class... Ts> void emit(Ts&&... xs)`, what kind of references are the parameters? Write one expression that passes every argument to `sink(...)`, one call per argument, in order, preserving each argument's value category.

#### mini exercise

Modernize this pre-C++17 parser using at least three week 4 features. Keep the caller working, and decide which behavior changes you are willing to accept.

```cpp
#include <cstdlib>
#include <map>
#include <string>

// "max_vel=1.5" -> name "max_vel", value 1.5; false if malformed
bool parse_limit(const std::string& line, std::string& name, double& value) {
    std::string::size_type eq = line.find('=');
    if (eq == std::string::npos) return false;
    name = line.substr(0, eq);
    const char* begin = line.c_str() + eq + 1;
    char* end = 0;
    value = std::strtod(begin, &end);
    return end != begin && *end == '\0';
}

void load(std::map<std::string, double>& limits, const std::string& line) {
    std::string name;
    double v;
    if (parse_limit(line, name, v)) limits[name] = v;
}
```

#### answers

<details>
<summary>1. binding a returned pair</summary>

`auto&` does not compile: the hidden object would be a non-const lvalue reference, which cannot bind to the prvalue `make_track()` (day 05). Both `const auto&` and `auto&&` compile: the hidden reference binds directly to the temporary, so its lifetime is extended to match the hidden reference, which lives as long as the bindings' scope (day 03). With `const auto&`, `id` and `range` are const; with `auto&&`, they are modifiable.

</details>

<details>
<summary>2. the eager static_assert</summary>

`false` does not depend on any template parameter, so the assertion is checked when the template is defined, not when a branch is chosen; no instantiation could ever satisfy it, which makes the template ill-formed under C++17 and C++20 rules. The fix is a dependent false: `template <class> inline constexpr bool always_false = false;` and `static_assert(always_false<T>, "...")`. C++23 (P2593) relaxed the rule, and GCC 13 and Clang 17 accept the plain form in C++23 mode.

</details>

<details>
<summary>3. comparing an empty optional</summary>

An empty optional compares less than any value, so the condition is `true` and the system keeps running with no temperature reading at all. That is a fail-open bug. Make the missing case explicit and choose the safe policy: `if (latest_temp_c && *latest_temp_c < max_temp_c) keep_running();`, which stops (or degrades) when there is no reading. The comparison operators are convenient for sorting; in guards, test engagement first.

</details>

<details>
<summary>4. variant versus a base class</summary>

The set of message types is closed and owned by the team, which is exactly where a variant shines: values stored inline (no allocation per message), copyable and storable in containers, no `dynamic_cast`, and every `std::visit` with explicit per-type handlers fails to compile until it handles a newly added message type. Adding new *operations* (logging, serialization, metrics) is a new visitor rather than a change to every class. The base class wins when the set must be open: plugins or other teams adding message types without recompiling your code, or when message types are large and you want each one to own its behavior.

</details>

<details>
<summary>5. the dangling name()</summary>

`prefix_ + "_" + id_` creates a temporary `std::string`; the returned view points into it, and the temporary is destroyed at the end of the `return` statement. Every use of the result is undefined behavior. The smallest fix is to return `std::string`. A view is only appropriate when it refers to storage that outlives the call, for example `std::string_view id() const { return id_; }`, which is valid as long as the `Frame` lives and `id_` is not modified.

</details>

<details>
<summary>6. from week 1: reference versus view</summary>

`a` is safe: binding a `const&` directly to a temporary extends the temporary's lifetime to the reference's (day 03). `b` dangles: `std::string_view` is not a reference but an object that holds a pointer, initialized through `std::string`'s conversion operator. The temporary string is not bound to any reference, so it dies at the end of the full-expression, and reading `b` is undefined behavior. Lifetime extension follows the language's reference-binding rules, not "anything that refers to something".

</details>

<details>
<summary>7. from week 3: forwarding a pack</summary>

They are forwarding references (day 19): `Ts&&` in a deduced context, with `Ts` deduced as an lvalue reference type for lvalue arguments. The expression is a comma fold (day 23): `(sink(std::forward<Ts>(xs)), ...);`. The built-in comma operator guarantees left-to-right order, and `std::forward<Ts>` restores each argument's original value category. (If `sink` returned a type that overloads `operator,`, cast each call to `void`.)

</details>

<details>
<summary>mini exercise: one possible answer</summary>

```cpp
#include <charconv>
#include <map>
#include <optional>
#include <string>
#include <string_view>

struct Limit { std::string_view name; double value; };   // name borrows from the line

[[nodiscard]] std::optional<Limit> parse_limit(std::string_view line) {
    const auto eq = line.find('=');
    if (eq == std::string_view::npos) return std::nullopt;
    const auto text = line.substr(eq + 1);
    double value{};
    if (auto [ptr, ec] = std::from_chars(text.data(), text.data() + text.size(), value);
        ec != std::errc{} || ptr != text.data() + text.size())
        return std::nullopt;
    return Limit{line.substr(0, eq), value};
}

void load(std::map<std::string, double>& limits, std::string_view line) {
    if (auto lim = parse_limit(line))
        limits.insert_or_assign(std::string(lim->name), lim->value);   // copy at the ownership boundary
}
```

Week 4 features used: `std::string_view` parameters and slicing, `std::optional` instead of the `bool` plus out-parameters, an `if` with an initializer around a structured binding of the `from_chars` result, and `[[nodiscard]]`. The `Limit::name` view is safe only as long as the line lives, which is why `load` copies it into the map immediately.

Behavior changes to accept consciously: `std::strtod` skipped leading whitespace, accepted a leading `+`, and depended on the current C locale's decimal point; `std::from_chars` does none of these, so `"max_vel= 1.5"` and `"max_vel=+1.5"` are now rejected. That is usually what you want in a config format, but it is a change and belongs in the commit message. (Floating-point `from_chars` needs GCC 11 or later with libstdc++; check other toolchains.)

</details>

#### connections

Week 4 is mostly week 1 to 3 ideas packaged into types. `std::string_view` and `std::optional` are day 04's pointer-versus-reference-versus-value decision turned into vocabulary, and their traps are day 03's lifetime rules. `std::variant` is day 13's polymorphism question answered for closed sets, and `if constexpr` and folds are day 18 and day 19's template machinery with the SFINAE noise removed. The error-handling options of day 20 now have concrete shapes: exceptions, `std::optional`, variant results, and `std::error_code` overloads in `std::filesystem`.

Week 5 continues directly from here. Concepts (day 29) take over most of what `enable_if` and many `if constexpr` chains do, with better errors. Ranges and views (day 30) and `std::span` (day 31) generalize today's borrowing idea from strings to any sequence, with the same lifetime discipline. Three-way comparison (day 32), C++20 compile-time programming (day 33), and `std::format` (day 34) round out the everyday C++20 toolbox.

[back to table of contents](#table-of-contents)

---

<a id="week-5"></a>

## week 5: the c++20 toolbox

C++20's everyday features: constraints, ranges, views, comparisons, compile-time programming, and formatting.

<a id="day-29"></a>

### day 29: concepts: constraining templates

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 18, 19, 23

#### the idea

Call `std::sort(ids.begin(), ids.end())` on a `std::list<int>` and GCC 12 reports `no match for 'operator-'` at line 1938 of `stl_algo.h`, a file you never wrote, followed by a page of instantiation context. The real problem ("sort needs random access") appears nowhere. Call `std::ranges::sort(ids)` instead and the first error is on your line, and the notes say the constraint `random_access_range` was not satisfied because `bidirectional_iterator_tag` is not `random_access_iterator_tag`.

The output is not shorter. It is *located*: the requirement is part of the signature, so the compiler checks it at the call site instead of discovering the problem deep in the body. That is what concepts buy you: a template's requirements move from its implementation into its interface.

#### understanding the concept

A **concept** is a named compile-time predicate over template arguments:

```cpp
template <typename T>
concept Arithmetic = std::integral<T> || std::floating_point<T>;
```

`Arithmetic<double>` is a `bool` constant expression. A concept is not a type and has no runtime presence. When a constrained template is a candidate in overload resolution, the compiler deduces the template arguments, then checks the constraints *before* instantiating anything. If they are not satisfied, the candidate is dropped, exactly as SFINAE would drop it (day 18), but the diagnostic names the unsatisfied concept and the failing sub-expression.

The building block for your own concepts is the **requires expression**, `requires (params) { requirements; }`. Its parameters are just names to write expressions with; nothing is evaluated or executed. The compiler only asks "would this be valid?". There are four kinds of requirement:

| kind | form | checks |
|---|---|---|
| simple | `s.reset();` | the expression is valid |
| type | `typename S::sample_type;` | the type exists |
| compound | `{ s.read() } noexcept -> std::same_as<X>;` | valid, optionally `noexcept`, and `decltype((expr))` satisfies the concept |
| nested | `requires std::copyable<X>;` | a further constraint is satisfied |

`<concepts>` gives you the vocabulary: `std::integral`, `std::floating_point`, `std::same_as`, `std::convertible_to`, `std::derived_from`, `std::invocable`, `std::predicate`, `std::totally_ordered`, `std::copyable`, `std::regular`, and more. Build on these instead of reinventing them, for a reason we will see under subsumption.

Concepts are not purely syntactic. `std::regular` means "copyable, default-constructible, and equality-comparable *in a way that behaves like a value*"; `std::totally_ordered` means the comparison operators are consistent with a total order. The compiler checks only the syntax. For standard library templates, a type that satisfies a concept's syntax but violates its semantic requirements makes the program ill-formed, no diagnostic required: you get no error, just no guarantees.

#### in code

**Before and after.** C++17 hid the constraint in a defaulted template parameter (day 18). C++20 gives four spellings that mean the same thing for a single parameter:

```cpp
#include <concepts>
#include <type_traits>

// C++17: SFINAE via enable_if
template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
T gcd17(T a, T b) { while (b != 0) { T t = a % b; a = b; b = t; } return a; }

// C++20: constrained template parameter
template <std::integral T>
T gcd(T a, T b) { while (b != 0) { T t = a % b; a = b; b = t; } return a; }

// equivalent: requires clause, or trailing requires clause
template <typename T> requires std::integral<T> T gcd2(T a, T b);
template <typename T> T gcd3(T a, T b) requires std::integral<T>;

// abbreviated function template: each `auto` is its own template parameter
auto scale(std::floating_point auto gain, std::integral auto counts) {
    return gain * counts;
}

// gcd(12, 18L);   // error: deduced conflicting types for 'T' (int and long)
// scale(0.5, 7L); // fine: two independent parameters
// gcd(1.5, 2.5);  // error: 'is_integral_v<double>' evaluated to 'false'
```

Use the constrained parameter when one concept applies to one type; use a `requires` clause when the constraint relates several parameters (`requires std::convertible_to<From, To>`).

**Writing a concept.** A sensor driver contract for a robotics stack:

```cpp
#include <chrono>
#include <concepts>
#include <cstdint>
#include <string_view>

template <typename S>
concept Sensor = requires(S& s, const S& cs) {
    typename S::sample_type;                                  // type
    { s.read() } -> std::same_as<typename S::sample_type>;    // compound
    { cs.name() } noexcept -> std::convertible_to<std::string_view>;
    s.reset();                                                // simple
    requires std::copyable<typename S::sample_type>;          // nested
};

struct Imu {
    struct sample_type { float ax, ay, az; };
    sample_type read() { return {0.f, 0.f, 9.81f}; }
    std::string_view name() const noexcept { return "imu0"; }
    void reset() {}
};
static_assert(Sensor<Imu>);   // the contract is tested next to the type

struct Encoder {
    using sample_type = std::int32_t;
    std::int64_t read() { return 0; }   // BUG: does not return sample_type
    const char* name() const noexcept { return "enc0"; }
    void reset() {}
};

template <Sensor S>
typename S::sample_type poll(S& s) { return s.read(); }

// poll(enc);  GCC 12: note: 's.read()' does not satisfy return-type-requirement
```

That `static_assert` line is worth making a habit. It turns "does my type still fit the template?" into a compile error in the type's own header, not in someone else's instantiation three libraries away.

**Overloading on constraints.** When two constrained overloads are both viable, the more constrained one wins if its constraints *subsume* the other's:

```cpp
#include <cstdio>
void describe(Arithmetic auto)    { std::puts("arithmetic"); }
void describe(std::integral auto) { std::puts("integral"); }

describe(3);     // prints: integral   (integral subsumes integral || floating_point)
describe(2.5);   // prints: arithmetic
describe('a');   // prints: integral   (char is an integral type)
```

Subsumption is decided by breaking constraints into atomic pieces and comparing them, and two atomic constraints are only "the same" if they come from the same expression in the source, which in practice means the same named concept. That is why you build on `std::integral` rather than writing `std::is_integral_v<T>` in each overload (see "watch out for").

Finally, C++20 lambdas can name their template parameters, which lets you constrain them and relate two arguments' types:

```cpp
#include <algorithm>
#include <vector>

auto clamp_all = []<std::floating_point T>(std::vector<T>& v, T lo, T hi) {
    for (T& x : v) x = std::clamp(x, lo, hi);
};
// clamp_all(floats, 0.f, 1.f);  OK
// clamp_all(floats, 0.0, 1.0);  error: conflicting types for 'T' (float and double)
```

With a generic lambda (`auto` parameters, day 17) you could not say "these three are the same `T`" without `decltype` gymnastics.

#### in practice

A motion-control library offers `template <Sensor S, Actuator A> class JointController`. Before concepts, the header said `template <typename S, typename A>` and the real contract lived in a wiki page and in the body of `update()`. Integrators found out their encoder wrapper was missing `reset()` when a build failed inside the controller's implementation.

With concepts, the header *is* the contract, every driver header carries `static_assert(Sensor<MyDriver>)`, and the error appears where the driver is written. Compare this with a virtual `ISensor` interface (day 13): the concept version has no vtable, no inheritance requirement, and allows inlining, but every controller instantiation is a separate piece of code (compile time, binary size), and you cannot put heterogeneous sensors in one container without type erasure (day 46). Choose a concept when the type is fixed at build time and the call is hot; choose a virtual interface when you need runtime selection or a stable binary boundary.

#### watch out for

**Concepts do not check the template body.** This compiles, because the body is only checked when instantiated:

```cpp
template <std::integral T>
T half(T x) { return x.value / 2; }   // nonsense, but no error until someone calls it
```

Unlike Rust traits, C++20 has no definition checking: the concept constrains *callers*, not the implementation. If the body uses `s.flush()` and the concept forgot to require it, a type can satisfy the concept and still fail inside. Keep the concept and the body in sync, and test with a minimal archetype type that provides only what the concept demands.

A related trap is subsumption with raw traits. These two overloads look like "general" and "more specific", but they are **ambiguous** for `int`:

```cpp
template <typename T> requires std::is_integral_v<T>                        void g(T);
template <typename T> requires std::is_integral_v<T> && (sizeof(T) == 4)   void g(T);
// g(1);  error: call of overloaded 'g(int)' is ambiguous
```

The two `std::is_integral_v<T>` are different atomic constraints because they are different expressions. Write `std::integral<T>` in both and the second overload wins.

#### the takeaway

A concept moves a template's requirements from its body into its signature. Write concepts that name a meaningful contract (`Sensor`, `std::regular`), build them from standard concepts so subsumption works, and test them with `static_assert` next to the types that must satisfy them.

#### optional challenge

```cpp
template <typename T>
concept Addable = requires(T a, T b) { a + b; };
```

Which of these hold: `Addable<std::string>`, `Addable<const char*>`, `Addable<short>`, `Addable<bool>`? Would you use `Addable` to constrain a `sum()` over sensor readings?

<details>
<summary>answer</summary>

`Addable<std::string>` is true (concatenation). `Addable<const char*>` is false: adding two pointers is ill-formed. `Addable<short>` and `Addable<bool>` are both true, through integral promotion to `int`, so `a + b` does not even have type `T`.

So `Addable` admits strings (concatenation, not summation) and `bool`, and says nothing about the result type. It describes syntax, not meaning. For a sum of readings, constrain on what you mean: `Arithmetic` from this lesson, or a compound requirement such as `{ a + b } -> std::convertible_to<T>` together with a semantic contract documented next to the concept.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-30"></a>

### day 30: ranges and views: lazy pipelines

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 16, 17, 26, 29

#### the idea

A radar tracker wants "the ranges of the three nearest detections with SNR above 12 dB". The C++17 version copies the strong detections into a temporary vector, sorts it with a lambda that compares one member, and then runs an index loop that stops at three. Three passes, one temporary, and an off-by-one waiting to happen in `i < strong.size() && i < 3`.

C++20 ranges let you say it as a pipeline: filter, project, take. The interesting question is not the syntax but the mechanics: nothing in a pipeline runs until you iterate it, and nothing in it owns your data unless you hand it over. Both facts make pipelines cheap, and both are the source of their bugs.

#### understanding the concept

A **range** is anything with `std::ranges::begin` and `std::ranges::end` (the end may be a *sentinel* of a different type). C++20 adds two layers on top of the day 16 algorithms.

**Range algorithms** in `std::ranges::` take a whole range, are constrained with concepts (day 29), and accept a **projection**: a callable applied to each element before the comparison or predicate. `std::ranges::sort(dets, {}, &Detection::range_m)` sorts by one member with the default `std::ranges::less` (the `{}`); the member pointer works because projections are called through `std::invoke`.

**Views** (`<ranges>`) are lazy adaptors. `std::views::filter(pred)`, `transform(f)`, `take(n)`, `drop(n)`, `reverse`, `iota(a, b)`, `keys`, `values`, and `split(delim)` each produce a small object that stores its underlying range (or a reference to it) plus the callable. Iterating it pulls elements through the chain one at a time. A view is required to be cheap to move, and to copy if it is copyable, independent of how many elements it represents. `r | views::filter(p)` is just `views::filter(r, p)` written left to right.

What does a view hold? `views::all` decides. For an lvalue container it creates a `ref_view`: a pointer to your container. For an rvalue container it creates an `owning_view` that moves the container in. (`owning_view` came from P2415, a defect report applied to C++20; GCC 12, recent Clang and MSVC implement it. Before it, piping an rvalue container did not compile.) So "views do not own" is true for lvalues, which is the common case and the dangerous one.

There is no `std::ranges::to` in C++20 (it is C++23). To materialize a pipeline you write the container yourself, with `std::ranges::copy` into a `back_inserter`, or by constructing from the iterators of a `views::common` adaptor.

#### in code

**Before and after.**

```cpp
#include <algorithm>
#include <iterator>
#include <ranges>
#include <vector>

struct Detection { float range_m; float snr_db; int track_id; };

// C++17
std::vector<float> near_strong_17(const std::vector<Detection>& dets) {
    std::vector<Detection> strong;
    for (const auto& d : dets)
        if (d.snr_db > 12.f) strong.push_back(d);
    std::sort(strong.begin(), strong.end(),
              [](const Detection& a, const Detection& b) { return a.range_m < b.range_m; });
    std::vector<float> out;
    for (std::size_t i = 0; i < strong.size() && i < 3; ++i)
        out.push_back(strong[i].range_m);
    return out;
}

// C++20
std::vector<float> near_strong_20(std::vector<Detection> dets) {   // our own copy to sort
    std::ranges::sort(dets, {}, &Detection::range_m);
    auto nearest = dets
        | std::views::filter([](const Detection& d) { return d.snr_db > 12.f; })
        | std::views::transform(&Detection::range_m)
        | std::views::take(3);
    std::vector<float> out;
    std::ranges::copy(nearest, std::back_inserter(out));
    return out;
}
// both return {30, 60, 80} for the same input
```

Notice a real tradeoff hiding here: we sort *before* filtering because `ranges::sort` needs a random-access range and a filter view is at most bidirectional. So the C++20 version sorts every detection, while the C++17 version sorted only the strong ones. If most detections are weak and the frame is large, that matters; measure with realistic frames before deciding which one wins.

**Predict the output.** Laziness means the callable runs when an element is pulled, and it can run more than once:

```cpp
#include <cstdio>
#include <ranges>
#include <vector>

int calls = 0;
int main() {
    std::vector<int> raw{1, 2, 3, 4, 5, 6};
    auto square = [](int x) { ++calls; return x * x; };
    auto even   = [](int x) { return x % 2 == 0; };

    int sum = 0;
    for (int x : raw | std::views::transform(square) | std::views::filter(even)) sum += x;
    std::printf("sum=%d calls=%d\n", sum, calls);

    calls = 0; sum = 0;
    for (int x : raw | std::views::filter(even) | std::views::transform(square)) sum += x;
    std::printf("sum=%d calls=%d\n", sum, calls);
}
```

Both sums are 56. The first pipeline makes 9 calls: `filter` calls `square` six times to test each element, and the loop's dereference calls it again for the three that pass. The second makes 3. Views do not cache transformed values, so an expensive or side-effecting `transform` ahead of a `filter` is evaluated twice per surviving element. Put cheap filters first, and keep transforms pure.

**Dangling is caught where the library can catch it.** A range algorithm called on an rvalue container returns `std::ranges::dangling` instead of an iterator into a dead object:

```cpp
std::vector<int> make_ids();
auto it = std::ranges::find(make_ids(), 42);   // it is std::ranges::dangling
// *it;  error: no match for 'operator*' (operand type is 'std::ranges::dangling')
```

Ranges that are safe to outlive (like `std::string_view` or `std::span`) opt in as *borrowed ranges*, and for those you get a real iterator.

#### in practice

Telemetry lines like `rpm=1200;temp=71;volt=24` are a natural fit for `views::split`, which with a `std::string_view` source yields contiguous subranges, so each field becomes a `string_view` with no allocation:

```cpp
#include <charconv>
#include <ranges>
#include <string_view>

void parse(std::string_view line) {
    for (auto field : line | std::views::split(';')) {
        std::string_view kv(field.begin(), field.end());   // C++20 iterator-pair constructor
        auto eq = kv.find('=');
        std::string_view key = kv.substr(0, eq);
        int value = 0;
        std::from_chars(kv.data() + eq + 1, kv.data() + kv.size(), value);
        // ... dispatch on key; prints [rpm] -> 1200 and so on in the test build
    }
}
```

These `split` semantics come from P2210, also a defect report against C++20 (the old behavior lives on as `views::lazy_split`). An older standard library may give you a forward-only range where this constructor does not work. The real code checks `eq == npos` and the `from_chars` result; it was left out to keep the example short.

#### watch out for

**A pipeline over a local, returned from a function, dangles.**

```cpp
auto strong_ids() {
    std::vector<int> ids = load();
    return ids | std::views::filter([](int i) { return i > 2; });   // BUG: ref_view to a dead local
}
```

Iterating the result is undefined behavior, and GCC 12 compiles it without a warning. Return `std::move(ids) | ...` (an `owning_view`) or return the container. The same trap appears in range-for: `for (int x : next_frame().data() | std::views::take(2))` is UB if `data()` returns a reference into the temporary frame, because the frame dies at the end of the range initializer. (C++23 extends temporary lifetimes in range-for initializers; C++20 does not.)

**`filter_view` caches `begin()`.** To make `begin()` amortized O(1), `filter_view` finds the first match on the first call and remembers it. Consequences:

- `begin()` is non-const, so `void dump(const auto& r)` will not accept a filter view. Take views by value or by forwarding reference (`auto&&`) instead.
- Modifying an element through a filter iterator so that it no longer satisfies the predicate is UB, by the standard's own wording.
- Changing the underlying container after the first iteration can leave the cached iterator stale (see the challenge).

**Debug builds and compile times.** Each adaptor is a layer of templates. Error messages name types like `filter_view<ref_view<vector<int>>, lambda>`, and in unoptimized builds each layer's `operator++` and `operator*` is a real call. If your robot's debug build has to meet a control-loop deadline, check that before converting a hot loop. And when the logic has early exits, two outputs, or index arithmetic, a plain loop is often clearer than a pipeline. "No raw loops" (day 16) is a guideline.

#### the takeaway

Views are lazy, cheap, and non-owning for lvalues: a pipeline is a recipe that runs when you iterate it, against data that someone else must keep alive. Use range algorithms and projections freely, use pipelines where they read better than the loop, and materialize the result explicitly.

#### optional challenge

```cpp
std::vector<int> v{1, 2, 3, 4};
auto evens = v | std::views::filter([](int x) { return x % 2 == 0; });
v.push_back(6);
for (int x : evens) std::printf("%d ", x);
```

Is this well-defined, and what does it print? Does the answer change if you insert a `for (int x : evens) {}` loop before the `push_back`?

<details>
<summary>answer</summary>

As written it is fine and prints `2 4 6`. The view holds a `ref_view` (a pointer to `v` itself, not to its buffer) and has not cached anything yet, so iteration starts from the current `v.begin()`.

If you iterate first, `filter_view` caches an iterator to the `2`. The `push_back` may reallocate (with libstdc++ it does: the capacity after list-initialization is exactly 4), which invalidates that cached iterator, and the next loop starts from it: undefined behavior. The rule of thumb: do not keep a view across modifications of what it views. Recreate it; it is cheap.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-31"></a>

### day 31: `std::span`: views over contiguous memory

**reading time:** about 8 minutes · **standard:** C++20 · **builds on:** days 04, 26, 30

#### the idea

Every C and C++ codebase has functions like `void process(const float* data, std::size_t n)`. The pointer and the count travel separately, so nothing stops a caller from passing `n` in bytes instead of elements, the size of the wrong buffer, or `n` for the whole buffer with a pointer into the middle of it. And the signature cannot say whether the function writes through `data` beyond the `const` you remembered to type.

`std::span` (C++20, `<span>`) is the pointer and the count fused into one value type. It does for contiguous arrays of any `T` what `std::string_view` (day 26) did for characters: it borrows, it does not own, and it makes the borrowing explicit in the signature.

#### understanding the concept

`std::span<T, Extent>` refers to a contiguous sequence of `T`. It has two forms:

- **dynamic extent** (`std::span<T>`, i.e. `Extent == std::dynamic_extent`): stores a pointer and a size. 16 bytes on a typical 64-bit platform (verified with GCC 12 on x86-64).
- **static extent** (`std::span<T, N>`): the size is part of the type, so typical implementations store only the pointer (8 bytes in the same test). The type itself carries a compile-time guarantee: this is exactly `N` elements.

A span is a cheap trivially copyable value: pass it by value, as you would a `string_view`. It converts implicitly from C arrays, `std::array`, `std::vector`, and any other contiguous, sized range (including another span), and explicitly from a pointer plus a count. The element type carries the constness: `std::span<const float>` is read-only, `std::span<float>` is writable, and a `std::span<float>` converts to `std::span<const float>` but not the other way.

Slicing is O(1) and never copies: `first(n)`, `last(n)`, `subspan(offset, count)`, and static-extent versions `first<N>()`, `last<N>()`, `subspan<Offset, Count>()` that return a `std::span<T, N>`. Finally, `std::as_bytes(s)` and `std::as_writable_bytes(s)` reinterpret any span as a span of `std::byte`, which is the C++20 way to say "the object representation of these elements".

Bounds: C++20 `std::span` has **no** `at()`. `operator[]`, `front()`, `back()`, and the slicing functions have preconditions (index in range, count not past the end), and violating one is undefined behavior. `at()` is added in C++26. Your standard library may check preconditions in a hardened mode: with libstdc++, `-D_GLIBCXX_ASSERTIONS` turns an out-of-range `operator[]` into an assertion failure (checked with GCC 12).

#### in code

**Before and after.**

```cpp
#include <array>
#include <cmath>
#include <span>
#include <vector>

// C++17: two parameters that must agree, and nothing checks that they do
float rms17(const float* data, std::size_t n);

// C++20: one parameter, read-only by type
float rms(std::span<const float> samples) {
    if (samples.empty()) return 0.f;
    float acc = 0.f;
    for (float s : samples) acc += s * s;
    return std::sqrt(acc / static_cast<float>(samples.size()));
}

void scale(std::span<float> samples, float gain) {   // writable by type
    for (float& s : samples) s *= gain;
}

void demo(std::vector<float>& buf, std::array<float, 2>& arr, float (&raw)[4]) {
    rms(buf); rms(arr); rms(raw);                 // all implicit
    rms(std::span(buf).first(2));                 // first two samples, no copy
    rms(std::span(buf).subspan(1, 2));            // elements 1 and 2
    scale(buf, 0.5f);
}
```

The callee no longer cares who owns the samples. The caller can pass a whole buffer or a window into one, and the function body uses range-for instead of index arithmetic.

**Static extent as a contract.** A 6-DoF pose is exactly six numbers. Put that in the type:

```cpp
void set_pose(std::span<const double, 6> pose);

std::array<double, 6> p{};
set_pose(p);                         // OK: size known to match
std::array<double, 5> p5{};
// set_pose(p5);  error: could not convert 'p5' from 'std::array<double, 5>' to 'std::span<const double, 6>'

std::vector<double> pv(7);
// set_pose(pv);  error: a vector's size is a runtime value
set_pose(std::span<const double>(pv).first<6>());   // explicit; UB if pv.size() < 6
```

The dynamic-to-static conversion is deliberately explicit: it is where a runtime size becomes a compile-time promise, so it should be visible in the code (and is a good place for a check).

**Bytes for serialization.**

```cpp
#include <cstdint>

struct TelemetryPacket {
    std::uint32_t seq;
    float         temperature_c;
    std::uint16_t status;
};   // sizeof is 12 with GCC 12 on x86-64: 10 bytes of members, 2 of padding

void append(std::vector<std::byte>& wire, const TelemetryPacket& pkt) {
    auto bytes = std::as_bytes(std::span{&pkt, 1});   // span<const std::byte>, 12 bytes here
    wire.insert(wire.end(), bytes.begin(), bytes.end());
}
```

`as_bytes` is the honest version of `reinterpret_cast<const char*>(&pkt)`: reading any object's bytes through `std::byte` is allowed. What it does not fix is the wire format. The layout of `TelemetryPacket` (padding, byte order, the representation of `float`) is implementation-defined, and the two padding bytes hold indeterminate values (copying them as `std::byte` is allowed, but they are garbage), so you are shipping noise and an ABI-specific layout. That is acceptable for a same-machine ring buffer or shared memory; it is not a protocol. For a real protocol, serialize field by field in a defined byte order.

#### in practice

A radar pipeline stores a range-Doppler frame as one row-major `std::vector<float>` (one allocation, contiguous rows) and hands out rows as spans:

```cpp
class RangeDopplerFrame {
public:
    RangeDopplerFrame(std::size_t doppler_bins, std::size_t range_bins)
        : range_bins_(range_bins), cells_(doppler_bins * range_bins) {}

    std::span<float> row(std::size_t d) {
        assert(d < rows());
        return std::span(cells_).subspan(d * range_bins_, range_bins_);
    }
    std::span<const float> row(std::size_t d) const {
        assert(d < rows());
        return std::span(cells_).subspan(d * range_bins_, range_bins_);
    }
    std::span<const float> cells() const { return cells_; }
    std::size_t rows() const { return cells_.size() / range_bins_; }

private:
    std::size_t range_bins_;
    std::vector<float> cells_;
};

float peak(std::span<const float> cells);   // CFAR, FFT, stats: none know about the frame
```

This is a coupling decision. Signal-processing functions that take spans work on a frame row, a `std::array` in a unit test, a `pmr::vector`, or a DMA buffer the driver mapped into memory. If they took `const std::vector<float>&`, every caller would need a `std::vector`, and you would copy a DMA buffer into one just to call a function. The frame keeps ownership and the invariant (rows have `range_bins_` cells); the algorithms borrow.

Compared with neighbors: `std::string_view` is a read-only span of characters with string operations; `std::span` is any `T`, mutable or not, and has no comparison operators (use `std::ranges::equal`). Range views (day 30) are lazy computations over any range; a span is just memory, and it requires contiguity.

#### watch out for

**Dangling, and the const case that compiles.** `std::span<float> s = make_samples();` is rejected: a mutable span cannot bind to a temporary container. But a span of `const` elements can, by design (so that `rms(make_samples())` works as a function argument):

```cpp
std::vector<float> make_samples();
std::span<const float> s = make_samples();   // BUG: compiles; the vector dies at the semicolon
float first = s[0];                          // UB: reads freed memory
```

GCC 12 compiles this without a warning. The same goes for a span into a vector that later reallocates (`push_back` after taking the span): the span holds the old pointer. Treat a span like a reference: fine as a parameter, suspicious as a local initialized from a function call, and a design decision as a data member.

**`const` is shallow.** `const std::span<float> s` makes the span itself immutable (you cannot reseat it), but `s[0] = 1.f` still compiles. Read-only access is spelled `std::span<const float>`. This is the same distinction as `T* const` versus `const T*` from day 04.

#### the takeaway

Replace pointer-plus-length parameters with `std::span<const T>` (read) or `std::span<T>` (write), pass it by value, use a static extent when the size is part of the contract, and never let a span outlive the buffer it borrows.

#### optional challenge

Which of these compile, and which are correct?

```cpp
std::vector<float> v{1.f, 2.f};
std::span<float>          a = make_samples();            // 1
std::span<const float>    b = make_samples();            // 2
std::span<const float, 4> c = std::array<float, 4>{};    // 3
const std::span<float>    d = v;  d[0] = 9.f;            // 4
```

<details>
<summary>answer</summary>

1 does not compile: a span of mutable elements cannot be constructed from an rvalue `std::vector` (it is not a borrowed range). 2 compiles and dangles. 3 compiles too, through the constructor taking `const std::array<T, N>&`, and dangles just the same: the temporary array dies at the end of the declaration. 4 compiles and is correct: the span object is `const`, its elements are not, so `v[0]` becomes `9`. All four were checked with GCC 12, which warns about none of them.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-32"></a>

### day 32: three-way comparison and defaulted equality

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 09, 29

#### the idea

To put a two-field grid cell in a `std::set` or sort it, C++17 asked for six operators, usually written as a pile of `std::tie` boilerplate. Each one is a chance for a typo (`<=` implemented as `!(a < b)` instead of `!(b < a)`), and the next person to add a field has to update all of them.

C++20 replaces the pile with one line, but the line comes with rules: which operators the compiler synthesizes, which "kind" of ordering you get, and when it quietly stops generating `==` for you. Those rules are worth ten minutes, because the failure modes are a missing operator at best and a sort with undefined behavior at worst.

#### understanding the concept

**The spaceship.** `a <=> b` returns an object that says less, equal (or equivalent), greater, or, for some types, unordered. You compare it against the literal `0`: `(a <=> b) < 0` means `a < b`.

**Rewriting.** You no longer write the relational operators. For `a < b`, the compiler also considers `(a <=> b) < 0` and the reversed form `0 < (b <=> a)`; likewise for `>`, `<=`, `>=`. For `a != b` it considers `!(a == b)` and `!(b == a)`, and for `a == b` it also tries `b == a`. Two consequences: one `operator==(const Meters&, double)` makes `2.0 == m` work as well, and a rewritten `!=` requires the `==` it uses to return exactly `bool`.

**Defaulting.** `auto operator<=>(const T&) const = default;` compares base classes first, then non-static members **in declaration order**, lexicographically, stopping at the first difference. `bool operator==(const T&) const = default;` compares the same things with `==`. If you default `<=>` and the class declares no `operator==` at all (of any signature), the compiler also declares a defaulted `==` for you. If you *write* `<=>` yourself, it does not.

**Why `==` is separate.** The original C++20 design derived `==` from `<=>`, and it was split out (P1185) for performance. Equality on containers can return `false` as soon as the sizes differ (that is how the standard specifies container `==`, and mainstream `std::string` implementations do the same); a three-way comparison has to walk to the first differing element, because a shorter string can still compare greater. For two log lines of different lengths sharing a 4 KiB prefix, `==` can stop after comparing sizes, while `<=>` reads the whole prefix.

**Comparison categories** (`<compare>`) describe what kind of order you have:

| category | values | meaning | example |
|---|---|---|---|
| `std::strong_ordering` | less, equal, greater | equal values are interchangeable | integers, `std::string` |
| `std::weak_ordering` | less, equivalent, greater | equivalent values may differ | case-insensitive keys |
| `std::partial_ordering` | less, equivalent, greater, unordered | some pairs are incomparable | `double` (NaN) |

Stronger converts implicitly to weaker. A defaulted `auto operator<=>` returns the weakest category among its members, so one `float` member makes the whole struct `partial_ordering`. These categories are promises you make; the compiler does not check that your `strong_ordering` is really substitutable.

#### in code

**Before and after.**

```cpp
#include <compare>
#include <tuple>

// C++17
struct Cell17 {
    int row, col;
    friend bool operator==(const Cell17& a, const Cell17& b) { return std::tie(a.row, a.col) == std::tie(b.row, b.col); }
    friend bool operator!=(const Cell17& a, const Cell17& b) { return !(a == b); }
    friend bool operator< (const Cell17& a, const Cell17& b) { return std::tie(a.row, a.col) <  std::tie(b.row, b.col); }
    friend bool operator> (const Cell17& a, const Cell17& b) { return b < a; }
    friend bool operator<=(const Cell17& a, const Cell17& b) { return !(b < a); }
    friend bool operator>=(const Cell17& a, const Cell17& b) { return !(a < b); }
};

// C++20
struct Cell {
    int row, col;
    auto operator<=>(const Cell&) const = default;   // also gives a defaulted ==
};
// Cell{1, 2} < Cell{1, 3}: true; result type of <=> is std::strong_ordering
```

Reordering `row` and `col` in `Cell` changes the ordering. With the defaulted operator, declaration order is part of the type's observable behavior, so keep the most significant key first and leave a comment when it matters.

**Predict the output.** A detection with a `float` member:

```cpp
#include <cstdio>
#include <limits>

struct Detection {
    float range_m;
    int   track_id;
    auto operator<=>(const Detection&) const = default;   // std::partial_ordering
};

int main() {
    float nan = std::numeric_limits<float>::quiet_NaN();
    Detection x{nan, 1}, y{5.f, 2};
    std::printf("%d %d %d %d\n", x < y, x > y, x == y, x == x);
}
```

It prints `0 0 0 0`. `x <=> y` is `unordered`, so every relational comparison is false, and the defaulted `==` compares `range_m` with `==`, so `x == x` is false too. Equality that is not reflexive breaks `std::find`, `std::set`, and any cache keyed on the struct.

**A custom ordering, and the `==` you must write.** A parameter server whose keys compare case-insensitively:

```cpp
#include <algorithm>
#include <cctype>
#include <string>

class ParamKey {
public:
    explicit ParamKey(std::string s) : s_(std::move(s)) {}
    std::weak_ordering operator<=>(const ParamKey& o) const {
        return std::lexicographical_compare_three_way(          // C++20 algorithm
            s_.begin(), s_.end(), o.s_.begin(), o.s_.end(),
            [](unsigned char a, unsigned char b) { return std::tolower(a) <=> std::tolower(b); });
    }
    bool operator==(const ParamKey& o) const { return (*this <=> o) == 0; }  // not generated
private:
    std::string s_;
};
// std::set<ParamKey>: inserting "MaxVelocity" then "maxvelocity" leaves size 1
```

`weak_ordering` is the honest category: `"MaxVelocity"` and `"maxvelocity"` are equivalent for ordering but are not the same string. The hand-written `==` must agree with `<=>`; a defaulted one here would compare case-sensitively and contradict the ordering.

#### in practice

A deployment tool decides whether to flash new firmware. Versions look like `2.1.0-rc1` and, per semantic versioning, a prerelease sorts *before* its release. The defaulted operator gets that wrong, because the empty string sorts before `"rc1"`:

```cpp
struct Version {
    int major = 0, minor = 0, patch = 0;
    std::string pre;   // empty for a release
    std::strong_ordering operator<=>(const Version& o) const {
        if (auto c = std::tie(major, minor, patch) <=> std::tie(o.major, o.minor, o.patch); c != 0)
            return c;
        if (pre.empty() != o.pre.empty())   // a release outranks its prereleases
            return pre.empty() ? std::strong_ordering::greater : std::strong_ordering::less;
        return pre <=> o.pre;               // simplified: full semver compares dot-separated parts
    }
    bool operator==(const Version&) const = default;
};
// sorted: 2.0.9  2.1.0-rc1  2.1.0
```

`std::tie(...) <=> std::tie(...)` uses C++20's `<=>` on `std::tuple`, which keeps the "compare these three in order" logic in one line. Defaulting `==` is fine here: two versions are equal exactly when all four fields are, which agrees with the custom ordering.

Leave out that `==` and you find out quickly: `std::ranges::sort(versions)` and `std::ranges::max(versions)` stop compiling, because `std::totally_ordered` (day 29) requires equality as well as ordering. The concept caught a half-specified type at the call site.

#### watch out for

**Partial orders in algorithms that require a strict weak ordering.** `std::sort`, `std::set`, and `std::map` require that the comparison be a strict weak ordering over the values you actually pass. With NaN in the data, `<` on `double` (or on a struct whose defaulted `<=>` is `partial_ordering`) is not one, and violating that precondition is undefined behavior. Typically you get silently misordered output; with some invalid comparators, implementations have also been known to read past the end of the range. Either reject NaN at the boundary (a sensor driver is a good place) or sort with `std::strong_order`, which for IEEE 754 types implements the `totalOrder` predicate (-0 before +0, positive NaNs after all numbers):

```cpp
std::sort(v.begin(), v.end(), [](double a, double b) { return std::strong_order(a, b) < 0; });
// {3, NaN, -0.0, 0.0, 1} sorts to: -0 0 1 3 nan
```

Two smaller traps: writing `<=>` by hand silently removes the implicit `==` (you get "no match for 'operator=='" only where someone uses it), and a hand-written `==` that returns `int` cannot be used for a rewritten `!=` (GCC: "return type of ... is not 'bool'").

#### the takeaway

Default `<=>` (and get `==` for free) when member-wise lexicographic order in declaration order is what you mean. When it is not, write `<=>` with an honest category and write `==` next to it, consistent with it. Watch any `float` member: it turns your type's ordering into a partial one.

#### optional challenge

Given `struct Meters { double v; auto operator<=>(const Meters&) const = default; bool operator==(double d) const { return v == d; } };` and `Meters m{2.0};`, which of these compile: `m == 2.0`, `2.0 == m`, `m != 2.0`, `m == Meters{2.0}`, `m < 3.0`?

<details>
<summary>answer</summary>

`m == 2.0` calls the member directly. `2.0 == m` compiles via the reversed candidate `m == 2.0`, and `m != 2.0` via the rewritten `!(m == 2.0)`; both rely on the `==` returning `bool`.

`m == Meters{2.0}` does **not** compile, which surprises most people. Declaring `operator==(double)` counts as declaring an `operator==`, so the compiler no longer adds the implicit defaulted `operator==(const Meters&)` that defaulting `<=>` would otherwise give you. Add `bool operator==(const Meters&) const = default;` explicitly. (`m < Meters{3.0}` still compiles; only `==` is affected.)

`m < 3.0` does not compile either: the only `<=>` takes `const Meters&`, and `Meters` has no converting constructor from `double` (aggregate initialization is not an implicit conversion). If you want it, add `std::partial_ordering operator<=>(double d) const { return v <=> d; }`; the category is partial because of NaN. All five were checked with GCC 12.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-33"></a>

### day 33: compile-time programming in C++20

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 03, 23, 29

#### the idea

A radar firmware computes its CRC-32 lookup table in a global constructor: `static CrcTable g_crc;`. Months later someone adds a static `PacketLogger` in another translation unit that checksums a startup banner. On one build configuration every checksum at startup is wrong, because the logger's constructor runs before the table's. That is the static initialization order fiasco from day 03, and the fix is not to order the constructors more cleverly. It is to make the table exist before any constructor runs at all: compute it at compile time.

C++20 gives you three keywords for this, and they make three different promises. `constexpr` says "can run at compile time". `consteval` says "must run at compile time". `constinit` says "this variable is initialized at compile time, but it is not a constant". Mixing them up is the most common mistake in this area.

#### understanding the concept

**`constexpr` functions** may be evaluated during constant evaluation, when their arguments are constants and the context requires a constant (a `constexpr` variable, an array bound, a template argument, `static_assert`). Called with runtime values, they are ordinary functions. Each standard widened what they may contain: C++11 allowed a single `return`, C++14 loops and local variables, C++17 lambdas. C++20 adds:

- `try` blocks (but actually evaluating a `throw` during constant evaluation is a compile error),
- virtual function calls, `dynamic_cast`, and `typeid`,
- changing the active member of a union, and uninitialized local variables (reading one is still an error),
- **transient dynamic allocation**: `new`/`delete`, and therefore `std::vector` and `std::string` (library support for `constexpr` `std::vector` and `std::string`: libstdc++ in GCC 12, libc++ 15, MSVC 19.29). Memory allocated during a constant evaluation must be freed within that same evaluation. You can build a vector at compile time and return its size or copy it into a `std::array`; you cannot have a `constexpr std::vector` variable.

**`consteval`** declares an *immediate function*: every call must be a constant expression, or the program is ill-formed. That turns "this should be folded" into "this is checked". Because a `throw` reached during constant evaluation is an error, a `consteval` function that throws on bad input becomes a compile-time validator. That is exactly how C++20 checks `std::format` strings (day 34): `std::format_string` has a `consteval` constructor that parses the literal.

**`constinit`** applies to variables with static or thread storage duration. It asserts that the variable is constant-initialized (initialized before any dynamic initialization runs), and makes it an error if it is not. The variable stays mutable. It answers day 03's fiasco for globals that must be mutable: a `constinit` counter or pointer is valid before any constructor in any translation unit runs.

**`std::is_constant_evaluated()`** (`<type_traits>`) returns `true` when called during constant evaluation, so a `constexpr` function can use a portable loop at compile time and an intrinsic or `memcpy` at runtime. Use it with plain `if`, never `if constexpr` (see "watch out for"). C++23's `if consteval` is a cleaner spelling; it is not C++20.

#### in code

**A compile-time table, tested by the compiler.**

```cpp
#include <array>
#include <cstdint>
#include <string_view>

constexpr std::array<std::uint32_t, 256> make_crc_table() {
    std::array<std::uint32_t, 256> table{};
    for (std::uint32_t i = 0; i < 256; ++i) {
        std::uint32_t c = i;
        for (int k = 0; k < 8; ++k)
            c = (c & 1u) ? 0xEDB88320u ^ (c >> 1) : c >> 1;
        table[i] = c;
    }
    return table;
}
inline constexpr auto crc_table = make_crc_table();   // no constructor, no ordering

constexpr std::uint32_t crc32(std::string_view data) {
    std::uint32_t c = 0xFFFFFFFFu;
    for (unsigned char b : data)
        c = crc_table[(c ^ b) & 0xFFu] ^ (c >> 8);
    return c ^ 0xFFFFFFFFu;
}
static_assert(crc32("123456789") == 0xCBF43926u);   // the standard CRC-32 check value
```

The same `crc32` serves runtime packets and compile-time tests. The `static_assert` is a unit test that runs on every build and cannot be skipped.

**Transient allocation.** C++20 lets constant evaluation use the heap, as long as nothing escapes:

```cpp
#include <vector>

constexpr int count_primes(int n) {
    std::vector<bool> composite(n + 1, false);   // allocated and freed during evaluation
    int count = 0;
    for (int i = 2; i <= n; ++i) {
        if (composite[i]) continue;
        ++count;
        for (int j = 2 * i; j <= n; j += i) composite[j] = true;
    }
    return count;
}
static_assert(count_primes(100) == 25);

// constexpr std::vector<int> v{1, 2, 3};
// error: ... is not a constant expression because it refers to a result of 'operator new'
```

**`consteval` and `constinit`.**

```cpp
#include <cstdint>
#include <numbers>

consteval double deg_to_rad(double deg) { return deg * std::numbers::pi / 180.0; }

consteval std::uint8_t can_channel(int ch) {
    if (ch < 0 || ch > 15) throw "CAN channel out of range";   // compile-time diagnostic
    return static_cast<std::uint8_t>(ch);
}

constexpr double joint_limit = deg_to_rad(170.0);   // 2.967060
constexpr auto steering_bus  = can_channel(3);
// can_channel(16);    error: expression '<throw-expression>' is not a constant expression
// deg_to_rad(runtime_angle);  error: the value of 'runtime_angle' is not usable in a constant expression

int compute_default();
constinit int retry_budget = 5;                    // OK: mutable, initialized before any constructor
// constinit int bad = compute_default();
// error: 'constinit' variable 'bad' does not have a constant initializer
```

`deg_to_rad` as `consteval` is a design choice: it says "this conversion is for constants in source code", and a runtime angle must go through a different (runtime) function. That keeps an accidental per-cycle conversion out of a control loop, but it also means you cannot reuse it at runtime. Choose `constexpr` when both uses are legitimate.

C++20 also allows class types as non-type template parameters, if they are *structural* (public members, no `mutable`, all members structural). A small `fixed_string` lets a string literal become part of a type, so `Counter<"dropped_frames">` and `Counter<"crc_errors">` are distinct types with their own static storage. Libraries use this for compile-time format strings, units, and register maps.

#### in practice

In embedded radar firmware the CRC table above lives in read-only memory (1 KiB), costs nothing at boot, and cannot be observed half-initialized. The alternative, computing it at startup into RAM, costs a few thousand simple operations once at boot and 1 KiB of RAM instead of flash. On a microcontroller with scarce RAM and plenty of flash, compile-time wins; on a desktop it hardly matters, and the real benefit is removing an initialization-order dependency.

The costs are real, though. Constant evaluation is interpreted by the compiler, and compilers impose limits. As a data point on the machine used to check this course: `static_assert(count_primes(100000) == 9592)` hit GCC 12's default operation limit ("'constexpr' evaluation operation count exceeds limit of 33554432"), and with `-fconstexpr-ops-limit` raised it added about 7 seconds to the build, while the same call at runtime finished within process startup time. Anything big generated in a header is paid for by every translation unit that includes it; put it in one `.cpp` file. You cannot step through constant evaluation in a debugger, so keep `constexpr` functions callable at runtime and unit test them there too. And a large generated table makes the binary bigger. "Move it to compile time" is a tradeoff between build time, binary size, startup time, and debuggability, not a free win.

#### watch out for

**`constexpr` on a function is permission, not a command.** A local `const auto t = make_crc_table();` may well run at runtime: only a context that requires a constant forces evaluation. If you need the guarantee, use a `constexpr` (or `constinit`) variable, or a `consteval` function.

**`if constexpr (std::is_constant_evaluated())` is always true**, because the condition of `if constexpr` is itself a constant evaluation. Your runtime branch becomes dead code. GCC 12 warns: "'std::is_constant_evaluated' always evaluates to true in 'if constexpr'". Use a plain `if`.

**Compiler extensions leak in.** GCC accepts `constexpr double s = std::sin(0.5);` even with `-pedantic`, because it constant-folds its math builtins. `<cmath>` functions are not `constexpr` in C++20, and other compilers may reject it. Later standards make more of `<cmath>` `constexpr`; until you target one, compute such tables with your own `constexpr` series or generate them offline.

#### the takeaway

`constexpr` means "may run at compile time", `consteval` means "must", and `constinit` means "initialized at compile time, mutable afterwards". Use compile-time evaluation to remove startup ordering problems and to turn checks into build errors, and weigh it against build time, binary size, and debuggability.

#### optional challenge

```cpp
constexpr int sq(int x) { return x * x; }
int g = sq(4);                 // namespace scope

int main() {
    int l = sq(4);             // local
}
```

Is `g` guaranteed to be initialized at compile time? Is `l`? What changes if you write `constinit int g = sq(4);`?

<details>
<summary>answer</summary>

`g` is guaranteed: a variable with static storage duration whose initializer is a constant expression undergoes *constant initialization*, which happens before any dynamic initialization. That is a language rule, not an optimization. `l` is not guaranteed: it is an ordinary local, and whether `sq(4)` is folded is up to the compiler. (GCC 12 happens to fold it even at `-O0`; that is an implementation choice, not a guarantee.)

`constinit` does not change the behavior of `g`; it adds a check. If someone later changes `sq` so it is no longer `constexpr`, plain `int g = sq(4);` silently becomes dynamic initialization, and the day 03 ordering problem is back. With `constinit`, that change is a compile error.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-34"></a>

### day 34: `std::format` and other everyday C++20 improvements

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 15, 16, 26, 33

#### the idea

Every C++ codebase formats text, and until C++20 the standard offered two bad choices. `printf("%llu", frame_id)` is compact, but passing an argument whose type does not match the conversion specifier is undefined behavior, and `std::uint64_t` is `unsigned long` on LP64 Linux, so `%llu` is wrong there and right on Windows. iostreams are type-safe, but `std::cout << std::setw(8) << std::fixed << std::setprecision(3) << x` is verbose, and `std::fixed` and `setprecision` stay set on the stream for whoever prints next.

`std::format` (C++20, `<format>`) keeps printf's compact format strings, gets the type from the argument instead of the string, checks the string at compile time, and has no hidden stream state. The second half of this lesson is a quick tour of small C++20 additions that remove everyday friction.

**Library support:** `<format>` needs GCC 13+, Clang with libc++ 17+, or MSVC 19.29+ (Visual Studio 2019 16.10), and the compile-time checking described below needs a recent version of each. On older toolchains, the {fmt} library (`fmt::format`) offers the same syntax; `std::format` was standardized from it. GCC 12, used to check this course, has no `<format>`, so the `std::format` code in this lesson is written against the standard but **not compile-checked**. The tour at the end was compiled with GCC 12.

#### understanding the concept

A replacement field is `{index:spec}`. Both parts are optional; `{}` takes the next argument. The spec mini-language is `[[fill]align][sign][#][0][width][.precision][type]`: `{:>10.3f}` is right-aligned, width 10, three decimals, fixed; `{:#x}` is hex with a `0x` prefix; `{:*^9}` centers in nine characters, padded with `*`. Each type defines which specs it accepts.

**Compile-time checking.** In C++20 as amended by P2216 (a defect report, so it applies to C++20 mode), the format string parameter is not a plain `string_view`. It is `std::format_string<Args...>`, whose constructor is `consteval` (day 33): it parses the literal during compilation, against the actual argument types. A bad spec or a missing argument is a compile error at your call site. (P2508 made the name `std::format_string` public for user code; current versions of the implementations above provide it in C++20 mode.) The flip side: the format string must be a constant expression. For a string known only at runtime (a user-configurable log template), call `std::vformat(fmt, std::make_format_args(a, b))`, which throws `std::format_error` on a bad string.

**Locale.** `std::format` is locale-independent unless you ask for it with the `L` option. `{:.2f}` always uses `.` as the decimal separator, which is what you want for telemetry and file formats; printf follows the C locale (`LC_NUMERIC`).

#### in code

**The basics, and what the compiler rejects.**

```cpp
#include <cstdint>
#include <format>
#include <string>

std::uint64_t frame = 1234567;
double range_m = 1234.56789;
int status = 255;

std::string s = std::format("frame {} range {:>10.3f} m status {:#x}", frame, range_m, status);
// "frame 1234567 range   1234.568 m status 0xff"

std::string t = std::format("{0}->{1}, {1}->{0}", "a", "b");   // "a->b, b->a"

// std::format("{:d}", range_m);   compile error: 'd' is not a valid presentation type for double
// std::format("{} {}", frame);    compile error: the string refers to an argument that does not exist
```

**A formatter for a domain type.** Specialize `std::formatter`. Inheriting from `std::formatter<double>` reuses its `parse`, so the caller's spec (`{:.2f}`) applies to each number:

```cpp
#include <format>

struct Pose2D { double x, y, theta; };

template <>
struct std::formatter<Pose2D> : std::formatter<double> {
    // parse() inherited. format() is const: C++23 requires it (LWG 3636), C++20 libraries accept it
    auto format(const Pose2D& p, std::format_context& ctx) const {
        ctx.advance_to(std::format_to(ctx.out(), "(x="));
        ctx.advance_to(std::formatter<double>::format(p.x, ctx));
        ctx.advance_to(std::format_to(ctx.out(), ", y="));
        ctx.advance_to(std::formatter<double>::format(p.y, ctx));
        ctx.advance_to(std::format_to(ctx.out(), ", theta="));
        ctx.advance_to(std::formatter<double>::format(p.theta, ctx));
        return std::format_to(ctx.out(), ")");
    }
};

// std::format("{:.2f}", Pose2D{1.0, 2.5, 0.785398})  ->  "(x=1.00, y=2.50, theta=0.79)"
```

The `advance_to` calls matter: the base `format` writes at `ctx.out()`, so the context must know where the previous write ended.

##### a quick tour of smaller C++20 additions

Excerpts from one file that was compiled and run with GCC 12, `-std=c++20`:

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
auto removed = std::erase_if(ids, [](int id) { return id < 0; });   // replaces erase-remove (day 16)

void trace(std::string_view msg, std::source_location loc = std::source_location::current());
// default argument is evaluated at the call site: prints the caller's file, line, function (day 53)

std::popcount(0b1011u);                  // 3; unsigned types only: popcount(11) does not compile
std::bit_cast<std::uint32_t>(1.0f);      // 0x3F800000 with IEEE 754 float; no UB, unlike type punning
std::endian::native == std::endian::little;

enum class Mode { idle, tracking, fault };
switch (m) { using enum Mode; case idle: /* ... */ case tracking: /* ... */ case fault: /* ... */ }

std::midpoint(INT_MAX - 2, INT_MAX);     // 2147483646; (a + b) / 2 would overflow: UB
for (auto i = std::ssize(ids) - 1; i >= 0; --i) { /* signed index, no wraparound */ }
```

Designated initializers must follow declaration order, cannot nest (`.pose.x`), and cannot be mixed with positional ones; they make configuration structs self-documenting at the call site. `std::bit_cast` (introduced on day 06 as the fix for type punning) is `constexpr` and requires equal sizes and trivially copyable types; the bit pattern itself depends on the implementation's floating-point representation.

#### in practice

A joint-controller thread logs at 1 kHz and must not allocate in steady state (day 52 has the details). `std::format` returns a `std::string`, which can allocate. `std::format_to` writes to any output iterator, and `std::format_to_n` writes at most `n` characters, so a reusable fixed buffer avoids the result allocation:

```cpp
#include <algorithm>
#include <array>
#include <format>

std::array<char, 96> line;   // owned by the logger, reused every cycle

void log_cycle(long t_us, int joint, double err) {
    auto r = std::format_to_n(line.data(), line.size(),
                              "t={} joint={} err={:+.4f}", t_us, joint, err);
    // r.out: one past the last char written; r.size: the length *without* truncation
    auto len = std::min(static_cast<std::size_t>(r.size), line.size());
    bool truncated = static_cast<std::size_t>(r.size) > line.size();
    sink_write(line.data(), len, truncated);   // no null terminator was written
}
// log_cycle(1712, 3, -0.00123456) writes "t=1712 joint=3 err=-0.0012"
```

The standard does not promise that formatting performs no internal allocation, so verify with an allocation counter (day 52) on your implementation before you rely on it in a real-time loop.

Your own logging wrapper must keep the compile-time check. Take `std::format_string<Args...>`, not `std::string_view`:

```cpp
template <typename... Args>
void log_info(std::format_string<Args...> fmt, Args&&... args) {
    write_line(std::format(fmt, std::forward<Args>(args)...));
}
// log_info("joint {} over limit by {:.2f}", id);   compile error at *this* call: missing argument
```

A `std::string_view fmt` parameter cannot be passed on to `std::format` at all (it is not a constant expression), and the usual "fix", switching to `std::vformat`, silently moves every format error from compile time to runtime.

#### watch out for

**`[[likely]]` and `[[unlikely]]` are hints, not optimizations.** Written as `if (frame.empty()) [[unlikely]] { return; }`, they influence block layout and branch weighting; they do not make code faster by themselves, and a wrong hint can make it slower. Use them only where a profile (day 50) shows a hot branch with a stable, known bias, such as an error path. Profile-guided optimization derives the same information from measured frequencies, and unlike a hand annotation it does not go stale when the code around it changes.

The other trap is assuming `std::format` exists. Libraries that must build on GCC 12 or older Clang often use {fmt} directly, or a thin wrapper that switches between `std::format` and `fmt::format`, rather than sprinkling feature tests (`__cpp_lib_format`) around the codebase.

#### the takeaway

`std::format` combines printf's compact syntax with type safety, compile-time checked format strings, and no stream state; keep the check alive in your wrappers with `std::format_string`, and use `format_to_n` when allocation matters. The small C++20 conveniences in the tour are worth adopting for the same reason: each one removes a bug pattern, not just keystrokes.

#### optional challenge

A colleague writes `std::string msg = std::format(cfg.log_template, id, value);`, where `log_template` is a `std::string` loaded from a config file. Does it compile? If not, what is the correct replacement, and what new failure mode does it introduce?

<details>
<summary>answer</summary>

It does not compile in C++20 (as amended by P2216): the format string is converted to `std::format_string<int, double>` through a `consteval` constructor, and a runtime `std::string` is not a constant expression. The replacement is `std::vformat(cfg.log_template, std::make_format_args(id, value))`, with `id` and `value` as lvalues (`make_format_args` stores references to them). The new failure mode is runtime: a template like `"{} {} {}"` or `"{:d}"` applied to a `double` throws `std::format_error`. Validate the template once when the config is loaded (format it with representative values inside a `try`), not on every log call.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-35"></a>

### day 35: week 5 review: the C++20 toolbox

**reading time:** about 8 minutes · **standard:** C++20 · **builds on:** days 29 to 34

#### recap

| day | idea in one line |
|---|---|
| [29](#day-29) | Concepts move a template's requirements into its signature; build them from standard concepts so subsumption works, and remember they constrain callers, not the body. |
| [30](#day-30) | Views are lazy recipes; they reference lvalues and own rvalues (`owning_view`), `filter_view` caches `begin()`, and C++20 has no `ranges::to`. |
| [31](#day-31) | `std::span<const T>` replaces pointer plus length; pass by value, use a static extent for fixed-size contracts, never let it outlive its buffer. |
| [32](#day-32) | Default `<=>` for member-wise order; write `<=>` and `==` together when the order is custom; a `float` member makes the order partial. |
| [33](#day-33) | `constexpr` may run at compile time, `consteval` must, `constinit` initializes at compile time and stays mutable. |
| [34](#day-34) | `std::format` is type-safe and checked at compile time through `std::format_string`; `format_to_n` avoids the result allocation; small C++20 additions remove bug patterns. |

The theme of the week: C++20 lets you state more of a contract in the type system (what a template needs, how many elements a buffer has, what kind of order a type has, what must happen at compile time) and have the compiler enforce it at the call site.

#### review questions

1. A driver type passes `static_assert(Sensor<LidarDriver>)`, yet `JointController<LidarDriver>` fails to compile with an error inside `JointController::update()`. How is that possible, and what practice reduces the risk?

2. Which of these is undefined behavior, and why is the other one fine?

   ```cpp
   std::vector<int> load_ids();                       // returns by value
   struct Config { const std::vector<int>& ids() const; };
   Config config();                                   // returns by value

   auto evens = load_ids() | std::views::filter(is_even);              // (a)
   for (int id : evens) use(id);
   for (int id : config().ids() | std::views::take(3)) use(id);        // (b)
   ```

3. A tracker keeps `std::set<Detection>`, where `Detection` has a `float range_m` member and `auto operator<=>(const Detection&) const = default;`. One radar frame contains a NaN range. What is wrong, precisely, and what are two reasonable fixes?

4. Pick `constexpr`, `consteval`, or `constinit` for each: (a) a global, mutable `Logger* g_logger` that must be valid before any static constructor in any translation unit runs; (b) a function that validates CAN channel numbers written as literals in source code and must reject bad ones at build time; (c) a CRC function used both in `static_assert` tests and on runtime packets.

5. Why should a project's `log_info` wrapper take `std::format_string<Args...>` rather than `std::string_view` for its format parameter?

6. **From week 4.** `std::string_view name = make_name();` (where `make_name` returns `std::string`) and `std::span<const float> s = make_samples();` (returning `std::vector<float>`) both compile. What is the shared problem, and why does `std::span<float> s = make_samples();` not compile?

7. **From week 2.** `Frame` has a user-written move constructor without `noexcept` and a copy constructor. When a `std::vector<Frame>` reallocates, are the elements moved or copied, and why?

#### mini exercise

Write a constrained function `rms` that takes a `std::span` of numeric samples (integers or floating point, but not `bool`), returns an empty `std::optional<double>` for an empty span, and works when called directly with a `std::vector<float>` or a `std::array<std::int16_t, N>`. Then print the result with `std::format` to three decimals. Hint: try calling your first version with a `std::vector<float>` before reading the answer.

#### answers

<details>
<summary>1. concept satisfied, body fails</summary>

Concepts are checked at the call site against the template arguments; C++20 does not check a template's body against its concepts. If `update()` calls `s.flush()` and `Sensor` never required `flush()`, the driver satisfies the concept and still fails during instantiation (day 29). Keep the concept in sync with what the body uses, and test the template with a minimal *archetype* type that provides exactly what the concept requires and nothing more: if the template compiles with the archetype, the concept is complete.

</details>

<details>
<summary>2. owning versus referencing views</summary>

(a) is fine. `load_ids()` is an rvalue, so `views::all` wraps it in an `owning_view` that moves the vector into the pipeline (P2415, a defect report against C++20). The view owns its data.

(b) is UB. `config().ids()` is an lvalue reference into the temporary `Config`, so the pipeline holds a `ref_view` to it. The temporary is destroyed at the end of the range initializer, before the loop body runs (C++23 extends temporary lifetimes in range-for initializers; C++20 does not). GCC 12 compiles both without a warning (day 30).

</details>

<details>
<summary>3. NaN in a set</summary>

A `float` member makes the defaulted `<=>` return `std::partial_ordering`, and with NaN, `<` is not a strict weak ordering: the NaN detection is "equivalent" to everything, which breaks transitivity of equivalence. `std::set` requires a strict weak ordering over the values it holds, so violating it is undefined behavior (typical symptoms: lookups that miss and duplicates that should have been rejected). The defaulted `==` is not even reflexive for that element.

Fixes: reject or sanitize NaN at the driver boundary, so the invariant "range is finite" holds for every `Detection`; or define the ordering with `std::strong_order` on the float (IEEE `totalOrder`) or on a non-float key such as a track id (day 32).

</details>

<details>
<summary>4. compile-time keywords</summary>

(a) `constinit Logger* g_logger = nullptr;`: constant-initialized, so it is valid before any dynamic initialization, and still assignable later. (b) `consteval`: every call must be a constant expression, and a `throw` reached during evaluation becomes a compile error. (c) `constexpr`: usable in constant expressions and at runtime (day 33).

</details>

<details>
<summary>5. format_string in wrappers</summary>

The compile-time check lives in the `consteval` constructor of `std::format_string<Args...>`, which runs when the caller's string literal is converted to the parameter type. A wrapper taking `std::format_string<Args...>` performs that conversion at *its* caller, against the real argument types, so a missing argument or bad spec fails there. A `std::string_view` parameter cannot be passed to `std::format` (it is not a constant expression), and switching to `std::vformat` moves every format error to runtime as `std::format_error` (day 34).

</details>

<details>
<summary>6. from week 4: views into temporaries</summary>

Both are non-owning views bound to a temporary that is destroyed at the end of the full-expression, so both dangle immediately (days 26 and 31). They compile because read-only views are deliberately constructible from temporaries, so that `f(make_name())` and `rms(make_samples())` work as function arguments, where the temporary lives long enough. A span of *mutable* elements refuses an rvalue container that is not a borrowed range, because writing into a temporary is almost always a bug. The rule: views are fine as parameters, suspicious as locals initialized from a call.

</details>

<details>
<summary>7. from week 2: noexcept and reallocation</summary>

Copied. To keep the strong exception guarantee for `push_back` and `emplace_back`, `std::vector` moves elements during reallocation only if the move constructor is `noexcept` (or the type is not copyable); otherwise it copies, via `std::move_if_noexcept` (day 10). A test with a printing `Frame` on GCC 12 prints `copy`. Mark the move constructor `noexcept`, or better, follow the rule of zero (day 11) and let the compiler generate it from members whose moves are already `noexcept`.

</details>

<details>
<summary>mini exercise: one solution</summary>

```cpp
#include <cmath>
#include <concepts>
#include <format>       // GCC 13+; the rest compiles with GCC 12
#include <optional>
#include <ranges>
#include <span>

template <typename T>
concept Numeric = (std::integral<T> && !std::same_as<T, bool>) || std::floating_point<T>;

template <Numeric T>
std::optional<double> rms(std::span<const T> xs) {
    if (xs.empty()) return std::nullopt;
    double acc = 0.0;
    for (T x : xs) acc += static_cast<double>(x) * static_cast<double>(x);
    return std::sqrt(acc / static_cast<double>(xs.size()));
}

// Deduction does not look through conversions: rms(vec) cannot deduce T
// from span<const T> ("'std::vector<float>' is not derived from 'std::span<const T>'").
// This overload accepts any contiguous range of Numeric and forwards to the span version.
template <std::ranges::contiguous_range R>
    requires std::ranges::sized_range<R> && Numeric<std::ranges::range_value_t<R>>
std::optional<double> rms(const R& r) {
    using T = std::ranges::range_value_t<R>;
    return rms(std::span<const T>(std::ranges::data(r), std::ranges::size(r)));
}

// std::vector<float> v{3.f, 4.f};
// if (auto r = rms(v)) std::string line = std::format("rms {:.3f} over {} samples", *r, v.size());
//                                       // "rms 3.536 over 2 samples"
```

The trap the hint points at is day 18's rule meeting day 31's type: template argument deduction does not consider implicit conversions, so a function template taking `std::span<const T>` cannot be called with a vector, an array, or even a `std::span<float>` (mutable elements) without help. The options are an explicit argument (`rms<float>(v)`), a non-template function for the one type you need, or a forwarding overload like the one above. The `!std::same_as<T, bool>` matters because `bool` is an integral type, and "the RMS of a bool vector" is almost certainly a bug; `std::vector<bool>` is also not a contiguous range, so it is rejected either way.

</details>

#### connections

- **Back to weeks 1 to 4.** Concepts replace the `enable_if` and SFINAE machinery of day 18 and many `if constexpr` dispatch chains of day 23. Range algorithms and views extend day 16's algorithms and day 17's lambdas. `std::span` generalizes day 26's `string_view` and fixes day 04's pointer-plus-length parameters. `constinit` closes day 03's static initialization order fiasco for globals, and `std::bit_cast` is day 06's answer to type punning. Defaulted comparisons are a rule-of-zero idea (day 11) applied to operators.
- **Ahead.** Week 6 brings concurrency: `std::jthread` and `std::stop_token` (day 36) are C++20 library types in the same spirit as this week. Concepts return as compile-time dependency injection (day 44) and in the static versus dynamic polymorphism comparison (day 46). `std::span` and `std::string_view` come back as API design tools (day 47), `std::format` and `std::source_location` in logging and observability (day 53), and the capstone pipeline (day 55) combines a defaulted comparison, a concept, `std::span`, and a range pipeline in one program.

[back to table of contents](#table-of-contents)

---

<a id="week-6"></a>

## week 6: concurrency and multithreading

Threads, synchronization, and the memory model, with an emphasis on designs that avoid trouble.

<a id="day-36"></a>

### day 36: threads and `std::jthread`

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 08, 09, 17

#### the idea

You have a sensor driver that polls an IMU every 10 ms on its own thread. Starting the thread is one line. Stopping it correctly, on every path including exceptions and early returns, is where the bugs live. If a `std::thread` object is destroyed while it still represents a running thread, your process does not leak or hang: it calls `std::terminate`. This week is about sharing safely, and it starts with owning threads safely.

#### understanding the concept

A `std::thread` is a handle that owns at most one thread of execution. Constructing it with a callable starts the thread; the standard says the end of the constructor *synchronizes with* the start of the callable, so everything the parent did before constructing the thread is visible inside it. When the thread finishes, its completion synchronizes with the return of `join()`, so everything the thread did is visible after `join` returns. We will make "synchronizes with" precise on day 40; for now, `join` is your visibility guarantee.

A thread object is *joinable* if it still owns a thread. It stops being joinable after `join()`, `detach()`, or being moved from. Destroying (or move-assigning to) a joinable `std::thread` calls `std::terminate`. That sounds harsh, but both alternatives were worse: an implicit `join` can hang a destructor forever, and an implicit `detach` lets the thread keep running with references to locals that are gone.

`detach()` is rarely right. A detached thread cannot be waited for, so you cannot know when it has stopped touching your objects. At process exit, static objects are destroyed while a detached thread may still be running, and any access to an object after its lifetime ends is UB. Use `detach` only for work that touches nothing but its own copies, and even then, ask what happens at shutdown.

Arguments are *decay-copied* into storage owned by the new thread, in the constructing thread, and then passed to the callable as rvalues. Two consequences follow. A parameter of type `T&` will not bind unless you pass `std::ref(x)`, and then `x`'s lifetime is your problem. And any conversion to the parameter type (say `const char*` to `std::string`) happens later, inside the new thread.

If an exception escapes the thread's top-level function, `std::terminate` is called. There is nobody to catch it. Day 39 shows how futures carry exceptions across threads.

C++20 `std::jthread` fixes the ownership story. Its destructor does `if (joinable()) { request_stop(); join(); }`, which is RAII applied to threads (day 08). It also owns a `std::stop_source`; if the callable's first parameter is a `std::stop_token`, the jthread passes it one. The three stop types:

| type | role |
|---|---|
| `std::stop_source` | the "remote control": `request_stop()` (returns `true` only for the call that made the request) |
| `std::stop_token` | a read-only view: `stop_requested()`, cheap to copy and pass down |
| `std::stop_callback` | registers a callable that runs when stop is requested |

Cancellation is cooperative. Nothing interrupts the thread; the thread has to look at the token.

#### in code

First, the classic hand-rolled version. It has a real bug, and it is not the one you might look for first.

```cpp
#include <atomic>
#include <chrono>
#include <thread>

class ImuPoller {
public:
    ImuPoller() : worker_([this] { run(); }) {}
    ~ImuPoller() {
        running_ = false;
        worker_.join();
    }
private:
    void run() {
        while (running_) {                       // may run before running_ is initialized
            poll_once();
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }
    void poll_once() { /* read registers, publish a sample */ }

    std::thread worker_;                         // BUG: declared first, so started first
    std::atomic<bool> running_{true};
};
```

Members are initialized in declaration order (day 09), so the thread starts before `running_` exists. Initializing an atomic is not an atomic operation, so the thread's load races with it: UB. Swapping the declarations fixes that, but the class still needs a hand-written destructor, and the shutdown logic is something every author reimplements slightly differently. With `std::jthread`:

```cpp
#include <chrono>
#include <stop_token>
#include <thread>

class ImuPoller {
public:
    ImuPoller() : worker_([this](std::stop_token st) { run(st); }) {}
    // no destructor: ~jthread requests stop, then joins

private:
    void run(std::stop_token st) {
        while (!st.stop_requested()) {
            poll_once();
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }
    void poll_once() { /* read registers, publish a sample */ }

    // Other members (buffers, config) go above this line.
    std::jthread worker_;   // declared last: constructed last, destroyed first
};
```

The comment on `worker_` is the important design rule. Destruction runs in reverse declaration order, so the thread is stopped and joined before any member it uses is destroyed. If the jthread is declared first, it is destroyed last, and the thread can briefly run against members that are already gone.

Second, how arguments travel:

```cpp
#include <string>
#include <thread>
#include <vector>

void fill(std::vector<double>& out) { out.assign(1024, 0.0); }
void log_line(const std::string& s) { /* write s somewhere */ }

void demo() {
    std::vector<double> samples;
    // std::thread t1(fill, samples);         // error: the copy is an rvalue, cannot bind to double&
    std::thread t1(fill, std::ref(samples));  // OK: samples must outlive the thread
    t1.join();                                // join makes the writes to samples visible here

    char buf[32] = "radar link up";
    std::thread t2(log_line, buf);            // BUG: buf decays to char*; the std::string
    t2.detach();                              // is built later, in t2, maybe after buf is gone (UB)

    std::thread t3(log_line, std::string(buf));  // fixed: convert before the thread starts
    t3.join();
}
```

Third, `std::stop_callback` lets a stop request reach into code that is blocked and not looking at the token:

```cpp
#include <optional>
#include <stop_token>

struct Frame { /* payload */ };
struct SerialPort {                  // driver API
    std::optional<Frame> read();     // blocks until a frame arrives or cancel() is called
    void cancel();                   // documented as safe to call from any thread
};
void handle(const Frame&);

void reader(std::stop_token st, SerialPort& port) {
    // Runs inside request_stop() on the requesting thread,
    // or immediately here if stop was already requested.
    std::stop_callback on_stop(st, [&port] { port.cancel(); });  // makes read() return early
    while (!st.stop_requested()) {
        if (auto frame = port.read())        // blocks until data or cancel()
            handle(*frame);
    }
}   // ~stop_callback deregisters; if the callback is running on another thread, it waits
```

The callback runs on whichever thread requests the stop, which is why `cancel()`'s thread-safety is part of the driver's contract. Started as `std::jthread t(reader, std::ref(port));`, the jthread's destructor triggers the callback.

#### in practice

In a robot stack, each driver component (lidar, IMU, motor bus) typically owns one thread. Making that thread a `std::jthread` member declared last gives you a component whose destructor is correct by construction, and whose shutdown order follows ownership: destroying the component tree in reverse order stops threads from the leaves up.

For process-wide shutdown (SIGTERM from systemd, say), keep one `std::stop_source` in `main`, and give each component a `std::stop_token` from it as a constructor argument. Be aware that a jthread's own stop source is separate. The jthread injects its token only when the callable accepts one as an extra first argument; a lambda taking a single `std::stop_token`, started as `std::jthread t(f, process_token)`, receives *your* token, and `~jthread`'s `request_stop()` then reaches nobody. A `stop_callback` on the process token that calls `worker_.request_stop()` bridges the two cleanly.

How many threads? `std::thread::hardware_concurrency()` is a hint, and it may return 0 when the value is not computable. Creating a thread is a system call plus a stack (commonly megabytes of reserved address space; the size is platform-dependent and `std::thread` gives you no portable way to set it). That cost is fine for a dozen long-lived component threads and wrong for one thread per incoming request, which is why thread pools exist (day 41).

#### watch out for

Cooperative cancellation is only as responsive as the checks. In the jthread example, `sleep_for` does not observe the token, so destruction can block for up to one period. With 10 ms that is harmless. With a blocking `read()` that waits for a sensor that has been unplugged, the destructor hangs forever, and a hung destructor is worse than a crash because nothing reports it. Every blocking call inside a stoppable thread needs a way to be woken: a `stop_callback`, a timeout, or a stop-token-aware wait such as `std::condition_variable_any::wait` with a token (day 38).

#### the takeaway

Own every thread with RAII: `std::jthread`, declared after everything it touches, with a `stop_token` checked at every point where the thread can block. Treat `detach` as a code smell that needs a written justification.

#### optional challenge

What does this print, and is it guaranteed?

```cpp
#include <iostream>
#include <thread>

int main() {
    int value = 0;
    {
        std::jthread t([&value] { value = 42; });
    }
    std::cout << value << '\n';
}
```

<details>
<summary>answer</summary>

It prints `42`, guaranteed. The inner scope ends, `~jthread` calls `request_stop()` (ignored, since the lambda takes no token) and then `join()`. The thread's completion synchronizes with the return of `join()`, so the write to `value` happens before the read in `main`. There is no data race. Replace `std::jthread` with `std::thread` and the program calls `std::terminate` at the closing brace instead, because the thread is still joinable.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-37"></a>

### day 37: data races and mutexes

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 06, 08, 19, 36

#### the idea

Two radar worker threads each count processed frames into a shared `long`, a million frames each. On one machine with GCC 12, an `-O0` build printed totals between 1.0 and 1.5 million, different on every run. The `-O2` build printed exactly 2,000,000 every time. A colleague concludes the release build is fine and the debug build is "just losing a few counts." Both conclusions are wrong. The program has a data race, and a data race is undefined behavior, not an imprecise number. The release build only looks right because the optimizer, assuming no race, collapsed each thread's loop into a single addition.

#### understanding the concept

The standard's definition is precise, and worth knowing word for word in spirit:

- Two expression evaluations **conflict** if they access the same memory location and at least one of them modifies it. (A memory location is a scalar object or a run of adjacent non-zero-width bit-fields; two different `char` members are different locations, which is why threads may safely write neighbouring struct members.)
- A program has a **data race** if it contains two potentially concurrent conflicting actions, at least one of which is not atomic, and neither happens before the other.
- Any data race is **UB** (day 06).

Why UB rather than "some interleaving of the two"? Because the compiler is allowed to optimize single-threaded code as if no other thread could be watching. It may keep a variable in a register for a whole loop, merge or split stores, or hoist a load out of a loop entirely, which turns `while (!done) {}` into an infinite loop. On some targets a 64-bit store is two instructions, and a reader can see half of each value. `++count` is a read-modify-write: three steps, and even when it compiles to a single x86 instruction, it is not atomic without a `lock` prefix.

A **race condition** is different: a bug where the result depends on timing. You can have one with no data race at all, when every access is properly locked but the *sequence* of operations is not. Locking each step separately does not make the sequence atomic.

A mutex fixes data races by creating happens-before edges. Each `unlock()` of a mutex synchronizes with the next `lock()` of the same mutex, so everything a thread wrote inside its critical section is visible to the next thread that takes the lock. You never call `lock()`/`unlock()` by hand; you use an RAII lock (day 08) so exceptions and early returns cannot leave it held.

| lock type | when to use |
|---|---|
| `std::lock_guard` | one mutex, locked for the whole scope; the default |
| `std::scoped_lock` (C++17) | one *or several* mutexes; locks several without deadlock (day 41) |
| `std::unique_lock` | needs to unlock early, defer, try, time out, or be moved; required by `std::condition_variable` (day 38) |
| `std::shared_lock` + `std::shared_mutex` (C++17) | many readers or one writer |

#### in code

The counter, broken and fixed:

```cpp
#include <mutex>
#include <thread>

long frames = 0;
void count_frames_racy() {
    for (int i = 0; i < 1'000'000; ++i) ++frames;   // BUG: data race, UB
}

std::mutex frames_mutex;
long frames_safe = 0;
void count_frames() {
    for (int i = 0; i < 1'000'000; ++i) {
        std::lock_guard lock(frames_mutex);          // CTAD: lock_guard<std::mutex>
        ++frames_safe;
    }
}

int main() {
    std::thread a(count_frames), b(count_frames);
    a.join();
    b.join();
    // frames_safe == 2'000'000, guaranteed
}
```

Locking per increment is correct but makes the threads take turns on every iteration. Better designs avoid sharing: count locally and add once at the end, or use an atomic counter (day 40). Correct first, then reduce sharing.

Now a race condition with no data race. Every method locks, and the code is still wrong:

```cpp
#include <map>
#include <mutex>

struct Track { double range_m; double velocity_mps; };

class TrackTable {
public:
    bool contains(int id) const {
        std::lock_guard lock(m_);
        return tracks_.count(id) != 0;
    }
    void insert(int id, Track t) {
        std::lock_guard lock(m_);
        tracks_[id] = t;
    }
    // Fix: make the operation callers need a single critical section.
    bool insert_if_absent(int id, Track t) {
        std::lock_guard lock(m_);
        return tracks_.try_emplace(id, t).second;
    }
private:
    mutable std::mutex m_;              // mutable: const readers must lock too
    std::map<int, Track> tracks_;
};

// BUG (race condition, not UB): another thread may insert between the two calls
// if (!table.contains(id)) table.insert(id, initial_track);
```

The lesson is about API design: the critical section is part of the interface. A thread-safe class must offer the *transactions* its callers need, not just thread-safe getters and setters.

Finally, encapsulate the mutex with the data it protects, so it is impossible to touch the data without the lock:

```cpp
#include <mutex>
#include <utility>

template <typename T>
class Synchronized {
public:
    explicit Synchronized(T value) : value_(std::move(value)) {}

    template <typename F>
    auto with_lock(F&& f) {                 // 'auto' returns by value:
        std::lock_guard lock(m_);           // a reference returned by f is copied,
        return std::forward<F>(f)(value_);  // not leaked past the lock
    }
private:
    std::mutex m_;
    T value_;
};

// Synchronized<std::vector<Detection>> pending{{}};
// pending.with_lock([&](auto& v) { v.push_back(d); });
// auto n = pending.with_lock([](auto& v) { return v.size(); });
```

`with_lock` deliberately returns `auto`, not `decltype(auto)`: a lambda that returns `auto&` gets a copy, so a reference to the guarded data cannot escape by accident. A determined caller can still smuggle out a pointer; the wrapper prevents mistakes, not malice.

#### in practice

A motion controller reads a calibration table at 1 kHz from several control threads; an operator tool updates it a few times per hour. This looks like the textbook case for `std::shared_mutex`, and it might be, but measure before assuming. A shared lock is not free: every reader still writes to the mutex's internal state, so the cache line holding it moves between cores on every acquisition, and if critical sections are short, that traffic can cost as much as the exclusive lock you were avoiding. The standard also says nothing about fairness between readers and writers, so writer starvation depends on the implementation.

An alternative worth knowing is the immutable snapshot: keep a `std::shared_ptr<const CalibrationTable>`, and have readers lock a mutex only long enough to copy the pointer. The writer builds a new table outside any lock and swaps the pointer under the mutex. Readers then use their snapshot with no lock held, and an old table lives until its last reader drops it (day 12). Sharing immutable data is the cheapest kind of sharing to reason about.

Whatever you choose, keep critical sections small: no I/O, no logging, no allocation-heavy formatting, and no calls into unknown code while holding a lock. Copy what you need out, unlock, then do the slow work.

#### watch out for

Returning references, pointers, iterators, or `string_view`s into guarded data. The lock protects the data only while it is held:

```cpp
const Track& find(int id) const {
    std::lock_guard lock(m_);
    return tracks_.at(id);   // BUG: the caller reads it after the lock is released
}
```

The caller's read races with any writer, and if another thread erases the entry, the reference dangles. Return by value (`std::optional<Track>`), or pass a callable in, as `with_lock` does. Tools help but do not replace design: ThreadSanitizer (`-fsanitize=thread` with GCC or Clang on Linux and macOS) reports races that occur on paths your tests actually execute, and silence means only that.

#### the takeaway

A data race is UB, not an imprecise result. Bundle each mutex with the data it guards, make each method one complete transaction, and never let a reference to guarded data outlive the lock.

#### optional challenge

This compiles. What does it actually protect?

```cpp
void TrackTable::clear() {
    std::unique_lock<std::mutex>(m_);
    tracks_.clear();
}
```

<details>
<summary>answer</summary>

Nothing. `std::unique_lock<std::mutex>(m_);` is parsed as a *declaration* (the same rule behind the most vexing parse, day 02): a new local variable named `m_`, of type `std::unique_lock<std::mutex>`, default-constructed, owning no mutex. It shadows the member, and `tracks_.clear()` runs unlocked. With `std::lock_guard` the same mistake fails to compile, because `lock_guard` has no default constructor, which is one more reason to prefer it. Always name your locks: `std::unique_lock lock(m_);`. GCC 12 with `-Wall` does warn here ("unnecessary parentheses in declaration of 'm_'"), and `-Wshadow` reports the shadowing, which is a good argument for treating warnings as errors.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-38"></a>

### day 38: condition variables and the producer-consumer queue

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 24, 36, 37

#### the idea

A detection stage hands work to a tracker thread through a mutex-protected `std::deque`. The first version of the tracker loops on `if (q.empty()) continue;`, which burns a core doing nothing. The second sleeps 1 ms between checks, which adds up to a millisecond of latency to every frame and still wakes a thousand times a second. What you actually want is "sleep until there is something to do", and that is what a condition variable provides.

#### understanding the concept

A `std::condition_variable` is a wait queue tied to a mutex. `cv.wait(lock)` does two things atomically: it releases the mutex and puts the thread to sleep. When woken, it reacquires the mutex before returning. That atomicity is the whole point: there is no window between "I checked the condition" and "I am asleep" in which another thread can change the condition and notify.

Two rules make it correct.

**Always wait with a predicate.** Waits may return without any notification (a *spurious wakeup*, explicitly allowed by the standard), and even a real notification may arrive after another thread has already consumed what you were woken for. So the condition is re-checked under the lock every time. The overload `cv.wait(lock, pred)` is exactly `while (!pred()) cv.wait(lock);`.

**Modify the predicate's state while holding the same mutex.** A notification has no memory: if nobody is waiting, `notify_one()` does nothing. If the producer changes the state without the mutex, it can do so after the consumer evaluated the predicate (false) but before the consumer went to sleep. The notify finds nobody waiting, and the consumer sleeps forever. This is the *lost wakeup*, and making the flag `std::atomic` does not fix it: it removes the data race, not the window.

`std::condition_variable` works only with `std::unique_lock<std::mutex>`, because `wait` must unlock and relock it. `std::condition_variable_any` works with any lockable type, at some cost in overhead, and in C++20 it gained stop-token-aware waits.

Notifying while holding the lock or right after releasing it are both correct, provided the state change happened under the lock. Notifying after unlocking can avoid waking a thread that immediately blocks on the mutex you still hold (some implementations mitigate this anyway). Notifying under the lock is the safer choice when a woken waiter might destroy the condition variable itself, for example by returning and ending the lifetime of the object that contains it; a notify on a destroyed condition variable is UB.

#### in code

The lost wakeup, labelled:

```cpp
#include <atomic>
#include <condition_variable>
#include <mutex>

std::mutex m;
std::condition_variable cv;
std::atomic<bool> ready{false};

void producer_buggy() {
    ready = true;            // BUG: not under m; the consumer may be between
    cv.notify_one();         // its predicate check and its sleep: wakeup lost
}

void producer() {
    {
        std::lock_guard lock(m);
        ready = true;        // a plain bool would now be enough
    }
    cv.notify_one();
}

void consumer() {
    std::unique_lock lock(m);
    cv.wait(lock, [] { return ready.load(); });
    // ready is true here, and m is held again
}
```

Now the workhorse of this week, a bounded blocking queue with shutdown. `push` blocks when full, `pop` blocks when empty, and `close` wakes everyone:

```cpp
#include <condition_variable>
#include <cstddef>
#include <deque>
#include <mutex>
#include <optional>

template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {}  // capacity > 0

    bool push(T item) {                                  // false if closed
        std::unique_lock lock(m_);
        not_full_.wait(lock, [&] { return closed_ || q_.size() < capacity_; });
        if (closed_) return false;
        q_.push_back(std::move(item));
        lock.unlock();
        not_empty_.notify_one();
        return true;
    }

    std::optional<T> pop() {                             // nullopt: closed and drained
        std::unique_lock lock(m_);
        not_empty_.wait(lock, [&] { return closed_ || !q_.empty(); });
        if (q_.empty()) return std::nullopt;
        std::optional<T> item(std::move(q_.front()));
        q_.pop_front();
        lock.unlock();
        not_full_.notify_one();
        return item;
    }

    void close() {
        { std::lock_guard lock(m_); closed_ = true; }
        not_full_.notify_all();                          // every waiter must re-check
        not_empty_.notify_all();
    }

private:
    std::mutex m_;
    std::condition_variable not_full_, not_empty_;
    std::deque<T> q_;
    std::size_t capacity_;
    bool closed_ = false;
};
```

A consumer is just `while (auto d = queue.pop()) track(*d);`, and it exits cleanly after `close()` once the queue is drained. Returning `std::optional` (day 24) makes "no more items" part of the type instead of a sentinel. Notice that the class is the unit of synchronization: the mutex, both condition variables, and the state they guard are private, and every public operation is one complete transaction (day 37).

Not every stage should block the producer. For a planner that only cares about the newest camera frame, a single overwrite slot is the right policy. This one needs C++20 for the stop-token wait:

```cpp
// C++20: condition_variable_any::wait(lock, stop_token, pred)
#include <condition_variable>
#include <mutex>
#include <optional>
#include <stop_token>
#include <utility>

template <typename T>
class LatestSlot {                     // producer never blocks; stale values are dropped
public:
    void publish(T v) {
        { std::lock_guard lock(m_); value_ = std::move(v); }
        cv_.notify_one();
    }
    std::optional<T> wait_next(std::stop_token st) {
        std::unique_lock lock(m_);
        if (!cv_.wait(lock, st, [&] { return value_.has_value(); }))
            return std::nullopt;       // woken by a stop request, nothing to return
        return std::exchange(value_, std::nullopt);
    }
private:
    std::mutex m_;
    std::condition_variable_any cv_;
    std::optional<T> value_;
};
```

The token overload registers a stop callback that wakes the waiter, then returns the final value of the predicate. Inside a `std::jthread` (day 36), this makes the blocking wait respond to the jthread's destructor without any extra close flag.

#### in practice

Back-pressure is a design decision, and the queue is where you make it explicit. In a radar chain, every detection matters for the tracker, so a bounded queue that blocks the detector is reasonable: when the tracker falls behind, the slowdown propagates upstream, and memory stays bounded. For a camera feeding a planner, a frame that is 200 ms old is worse than no frame, so drop-oldest (the `LatestSlot` above, or a ring buffer that overwrites) is the right policy. Telemetry export sits in between: bounded, drop newest, and count what you dropped.

What you should almost never ship is an *unbounded* queue between stages with different throughput. It does not remove overload, it hides it until the process runs out of memory, usually in the field. Whatever policy you pick, export the queue depth and drop counts as metrics: they are the first thing you will want when the pipeline misbehaves.

#### watch out for

Producers and consumers sharing one condition variable. If both "not full" and "not empty" waiters sleep on the same `cv`, a `notify_one()` intended for a consumer can wake a producer instead. That producer re-checks its predicate, finds it still false, and goes back to sleep; the notification is used up, and the consumer that should have run keeps sleeping. The program can stall with items in the queue. The fix is either one condition variable per condition (as in `BoundedQueue`) or `notify_all()` on a shared one, which is correct but wakes everyone. The same reasoning is why `close()` uses `notify_all()`: every waiter must observe `closed_`.

#### the takeaway

A condition variable is not a signal, it is a way to sleep until shared state changes. Guard that state with the mutex, wait with a predicate, and decide deliberately what happens when the producer is faster than the consumer.

#### optional challenge

After the wait in `pop()`, why does the code test `q_.empty()` rather than `closed_`? What would change if it returned `std::nullopt` whenever `closed_` is true?

<details>
<summary>answer</summary>

Testing `q_.empty()` gives drain-on-close semantics: items pushed before `close()` are still delivered, and `pop()` reports the end only when the queue is both closed and empty. If it returned on `closed_`, any items still queued at shutdown would be silently discarded, so a final batch of detections or log records would be lost. Sometimes that is what you want (a fast abort), but then it should be a separate, explicitly named operation, not an accident of the predicate.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-39"></a>

### day 39: futures, promises, and tasks

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 20, 36, 38

#### the idea

A thread function returns `void`, and an exception that escapes it calls `std::terminate` (day 36). So how does a worker hand back "here are the surface normals for your point cloud chunk" or "the calibration file was corrupt"? You could build a queue (day 38) for a single value, plus an error slot, plus a flag. The standard library already has that one-shot channel: a promise on one end, a future on the other.

#### understanding the concept

`std::promise<T>` and `std::future<T>` share a heap-allocated *shared state* holding either a `T` or a `std::exception_ptr`. The promise writes it exactly once with `set_value` or `set_exception`, which makes the state *ready*. The future waits for that with `wait()`, `wait_for()`, or `get()`. Making the state ready synchronizes with the return of the call that observes it, so everything the producer wrote before `set_value` is visible after `get()` returns, much like `join`.

The edges are well defined, and worth knowing:

| situation | result |
|---|---|
| `get()` on a ready future holding an exception | the exception is rethrown in the caller |
| `get()` called twice on a `std::future` | UB: `get()` leaves the future invalid (`valid() == false`), and calling `get` or a `wait` function on an invalid future is UB; libstdc++ happens to throw `std::future_error` |
| promise destroyed without setting anything | the future receives a `std::future_error` with `broken_promise` |
| `set_value` called twice | `std::future_error` with `promise_already_satisfied` |

`std::packaged_task<R(Args...)>` wraps a callable together with a promise: invoking the task calls the function and stores the return value or the thrown exception. It separates *what* to run from *where* it runs, which is exactly what a task queue or thread pool needs.

`std::async(policy, f, args...)` bundles both: it runs `f` and gives you the future. The policy matters:

- `std::launch::async`: run as if on a new thread.
- `std::launch::deferred`: do nothing now; run `f` on the calling thread the first time someone calls `get()` or `wait()`.
- no policy (`async | deferred`): the implementation chooses. You might get no concurrency at all.

There is one more rule that surprises everyone: the destructor of the last future referring to a shared state created by `std::async` blocks until the task completes. That is deliberate (otherwise the task could outlive everything it references), but it has a sharp edge, shown below.

`std::shared_future<T>` lets several consumers wait for the same result; `get()` returns a `const T&` and can be called repeatedly. Give each thread its own copy of the `shared_future` object: copies referring to one shared state are safe to use concurrently, while calls on a single object from several threads are not synchronized.

Finally, C++20 still has no continuations: no `.then()`, no `when_all`. Those lived in the Concurrency TS and were not standardized. If you need composition, you need a library, or a different structure.

#### in code

A worker that reports either a result or its exception:

```cpp
#include <future>
#include <stdexcept>
#include <thread>

struct Calibration { double offset; double gain; };

Calibration run_calibration() { throw std::runtime_error("checksum mismatch"); }

void calibrate(std::promise<Calibration> result) {
    try {
        result.set_value(run_calibration());
    } catch (...) {
        result.set_exception(std::current_exception());  // ships the exception to get()
    }
}

int main() {
    std::promise<Calibration> p;
    std::future<Calibration> f = p.get_future();
    std::thread worker(calibrate, std::move(p));        // the promise is move-only
    try {
        Calibration c = f.get();                        // rethrows runtime_error here
        (void)c;
    } catch (const std::exception& e) {
        // report e.what(): "checksum mismatch"
    }
    worker.join();
}
```

Now fork-join over a point cloud with `std::async`, including the classic bug:

```cpp
#include <algorithm>
#include <cstddef>
#include <functional>
#include <future>
#include <vector>

struct Point { float x, y, z; };

double sum_heights(const std::vector<Point>& cloud, std::size_t first, std::size_t last) {
    double sum = 0;
    for (std::size_t i = first; i < last; ++i) sum += cloud[i].z;
    return sum;
}

double mean_height(const std::vector<Point>& cloud, std::size_t parts) {  // parts > 0
    const std::size_t n = cloud.size(), step = (n + parts - 1) / parts;
    std::vector<std::future<double>> futures;
    for (std::size_t first = 0; first < n; first += step) {
        const std::size_t last = std::min(first + step, n);
        // BUG version: std::async(std::launch::async, sum_heights, std::cref(cloud), first, last);
        // The discarded future is destroyed at the end of the statement and waits:
        // every chunk runs to completion before the next starts. Sequential, with thread overhead.
        futures.push_back(std::async(std::launch::async, sum_heights,
                                     std::cref(cloud), first, last));
    }
    double total = 0;
    for (auto& f : futures) total += f.get();  // may rethrow a chunk's exception
    return n ? total / n : 0.0;
}
```

Recent libstdc++ marks `std::async` as `[[nodiscard]]`, so GCC warns about the bug version; do not count on every standard library doing so. The blocking destructor also does useful work here. If the first `get()` throws, the remaining futures are destroyed during stack unwinding, and each destructor waits for its task. So no task can still be reading `cloud` after `mean_height` has returned, and the `std::cref` is safe. A detached thread would offer no such guarantee.

Third, `std::packaged_task` separates the callable from the thread that runs it:

```cpp
#include <future>
#include <stdexcept>
#include <thread>

int main() {
    std::packaged_task<int(int)> task([](int range_bin) {
        if (range_bin < 0) throw std::out_of_range("negative range bin");
        return range_bin * 2;
    });
    std::future<int> f = task.get_future();
    std::thread t(std::move(task), 21);   // packaged_task is move-only, like the promise
    t.join();
    return f.get() == 42 ? 0 : 1;         // the value, or the exception, is in f
}
```

`packaged_task` is move-only, and `std::function` requires a copyable callable, so a pool built on `std::queue<std::function<void()>>` cannot hold one directly. The usual C++17/20 workaround is to wrap it in a `std::shared_ptr` and capture that; C++23 adds `std::move_only_function` for exactly this reason.

#### in practice

At startup, a robot loads its map, its URDF model, and its sensor calibrations. These are independent and I/O-heavy, so launching each with `std::async(std::launch::async, ...)` and calling `get()` on all three is a clean fork-join, with each loader's exceptions arriving at the one place that can decide whether to abort.

Several sensor threads may need the calibration before they start publishing. A `std::shared_future<Calibration>` (from `f.share()`) handed to each of them, by value, lets them all block on `get()` until it is ready, with no extra flags or condition variables.

Futures fit one-shot results. For a *stream* of items, use a queue (day 38). For many small tasks, use a pool (day 41) rather than one `std::async` per task, because whether `std::async` reuses threads is up to the implementation and you cannot bound how many it creates.

#### watch out for

The default launch policy. `std::async(f)` may defer `f`, and a deferred task never runs until you call `get()` or `wait()`. This innocent-looking progress loop then never finishes:

```cpp
auto f = std::async(compute_tracks);   // policy: async | deferred, implementation's choice
while (f.wait_for(std::chrono::milliseconds(10)) != std::future_status::ready) {
    report_progress();                 // if deferred, wait_for returns 'deferred' forever
}
```

Pass `std::launch::async` explicitly whenever you need concurrency, or handle `std::future_status::deferred` in the loop. Treat the default policy as "I don't care whether this runs concurrently", which is rarely what you mean.

#### the takeaway

A future is a one-shot channel that carries a value or an exception and synchronizes like `join`. Name the launch policy, keep every `std::async` future alive for as long as the work should run in parallel, and reach for queues or pools when you have more than a handful of tasks.

#### optional challenge

`calibrate` is changed to return early, without touching the promise, when the calibration file does not exist. What does the caller's `f.get()` do now?

<details>
<summary>answer</summary>

When `calibrate` returns, its by-value `std::promise` parameter is destroyed without having set a value. The destructor stores a `std::future_error` with error code `std::future_errc::broken_promise` in the shared state and makes it ready, so `f.get()` throws that exception. The caller does not hang, which is the point: abandoning a promise is reported, not silently lost. It is still better to call `set_exception` with a meaningful error, because "broken promise" tells the caller nothing about the missing file.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-40"></a>

### day 40: atomics and the memory model

**reading time:** about 10 minutes · **standard:** C++20 · **builds on:** days 06, 36, 37

#### the idea

A radar thread fills a frame buffer and then sets `bool ready = true;`. A processing thread spins on `ready`, then reads the frame. On your x86 workstation it seems to work. It is still UB: `ready` is accessed concurrently and is not atomic, so it is a data race (day 37); the optimizer may hoist the load out of the spin loop; and even with a correct flag, the question remains whether the *frame data* written before the flag is guaranteed to be visible after it. Answering that precisely is what the memory model is for.

#### understanding the concept

`std::atomic<T>` (for trivially copyable `T`) makes each operation on the object indivisible, and concurrent atomic operations on the same object are never a data race. Every atomic object also has a single *modification order* that all threads agree on. What atomicity alone does not give you is any promise about *other* memory. Compilers reorder independent loads and stores, and so do CPUs (store buffers, out-of-order execution). The memory model defines which reorderings other threads may observe, using three relations:

- **sequenced-before**: program order within one thread.
- **synchronizes-with**: a *release* store to an atomic synchronizes with an *acquire* load of the same atomic that reads the value written by that store (or by a later read-modify-write in its release sequence).
- **happens-before**: built from the two above, transitively. If a write happens before a read of the same location, with no other write in between, the read sees that write. If two conflicting accesses, one non-atomic, are not ordered by happens-before, you have a data race.

Mutex unlock/lock, thread start and `join`, and future readiness, which you have used all week, are all defined in terms of this relation. Atomics let you build the edges yourself, choosing a `std::memory_order` per operation:

| order | what it guarantees | typical use |
|---|---|---|
| `seq_cst` (default) | acquire/release, plus one total order of all `seq_cst` operations that every thread agrees on | the default; anything you have not proven needs less |
| `release` (stores) / `acquire` (loads) / `acq_rel` (read-modify-writes) | the synchronizes-with edge: writes before the release are visible after the acquire that reads it | publishing data through a flag or pointer |
| `relaxed` | atomicity and the per-object modification order, nothing else | counters and statistics that publish nothing |
| `consume` | intended as a cheaper acquire for dependent loads | do not use: its specification is under revision, and compilers implement it as `acquire` |

Read-modify-write operations (`exchange`, `fetch_add`, `compare_exchange_weak/strong`) are atomic as a whole. `compare_exchange` writes the new value only if the current value equals `expected` (compared byte for byte like `memcmp`, not with `operator==`, which matters for `float` and padding); on failure it loads the current value into `expected`. The `weak` form may fail spuriously (even when the values are equal), which is fine in a loop and can be cheaper on LL/SC architectures such as ARM.

Not every atomic is lock-free. `std::atomic<T>::is_always_lock_free` (C++17, `constexpr`) and `is_lock_free()` tell you; a large `T` may be implemented with a hidden lock. The standard guarantees lock-freedom only for `std::atomic_flag` (and, in C++20, the `std::atomic_signed_lock_free` and `std::atomic_unsigned_lock_free` aliases). C++20 adds `wait`/`notify_one`/`notify_all` on atomics (block until the value changes, without a condition variable) and `std::atomic_ref<T>`, which applies atomic operations to an ordinary object; while any `atomic_ref` to an object exists, every access to it must go through an `atomic_ref`.

#### in code

Message passing, the pattern behind almost every correct use of acquire/release:

```cpp
#include <array>
#include <atomic>
#include <cassert>
#include <cstdint>

struct Frame { std::array<float, 1024> samples; std::uint64_t seq; };

Frame frame;                          // plain, non-atomic data
std::atomic<bool> ready{false};

void producer() {
    frame.samples.fill(1.0f);
    frame.seq = 42;
    ready.store(true, std::memory_order_release);        // (1) publish
}

void consumer() {
    while (!ready.load(std::memory_order_acquire)) {}    // (2) spin until published
    assert(frame.seq == 42);                             // guaranteed, no data race
}
```

```text
producer                                consumer
frame.samples = ...   | sequenced
frame.seq = 42        | before
ready.store(release) ---synchronizes-with--> ready.load(acquire) reads true
                                             | sequenced before
                                             frame.seq == 42 (happens after the write)
```

Weaken either side to `relaxed` and the edge disappears: the reads of `frame` then race with the writes, which is UB, even though `ready` itself is still race-free. Using a plain `bool` makes `ready` itself a data race. Note the asymmetry: the order protects the *non-atomic* data around the atomic.

Relaxed operations and a compare-and-swap loop, for statistics that publish nothing:

```cpp
#include <atomic>
#include <cstdint>

std::atomic<std::uint64_t> frames_dropped{0};
std::atomic<float> peak_power{0.0f};

void on_drop() {
    frames_dropped.fetch_add(1, std::memory_order_relaxed);   // only the count matters
}

void record_power(float p) {
    float cur = peak_power.load(std::memory_order_relaxed);
    while (cur < p &&
           !peak_power.compare_exchange_weak(cur, p, std::memory_order_relaxed)) {
        // failed: cur now holds the latest value; the loop re-checks cur < p
    }
}
```

There is no `fetch_max` in C++20, so the CAS loop is the standard way to build any read-modify-write the library lacks. Relaxed is correct here because nobody reads other data based on these values; a monitoring thread that loads them sees *some* value from each modification order, and after `join` the final values are exact.

Third, C++20 replaces the spin with a blocking wait, and keeps hot atomics on separate cache lines:

```cpp
#include <atomic>
#include <cstdint>

std::atomic<std::uint32_t> generation{0};

void publish_next() {                    // producer, after writing the new frame
    generation.fetch_add(1, std::memory_order_release);
    generation.notify_all();
}

void await_next(std::uint32_t& seen) {   // consumer
    generation.wait(seen, std::memory_order_acquire);   // blocks while value == seen
    seen = generation.load(std::memory_order_acquire);
}

struct alignas(64) WorkerStats {         // 64: a common cache-line size, not a guarantee
    std::atomic<std::uint64_t> processed{0};
};
WorkerStats stats[8];                    // one per worker: no false sharing between them
```

`wait(old)` returns only after observing a value different from `old`; it may wake spuriously internally, but it re-checks for you. It compares values, so if the counter changed and changed back before the waiter looked, the waiter keeps sleeping (the ABA problem), which is why a monotonically increasing generation counter is used rather than a toggling flag. Note that this only signals. If the producer rewrites a single shared frame buffer while a consumer is still reading the previous frame, that is a data race again; pair the signal with double buffering or hand frames over through a queue (day 38).

#### in practice

The `alignas(64)` matters when several threads each update their own counter at high rates. If two such counters share a cache line, every write by one core invalidates the line in the other core's cache, and two logically independent threads end up contending: *false sharing*. C++17 added `std::hardware_destructive_interference_size` in `<new>` for this, but support varies: GCC provides it from version 12 (64 on x86-64 here) and warns (`-Winterference-size`) when it is used in a header, because the value can change with tuning flags and so becomes an ABI hazard. Check `__cpp_lib_hardware_interference_size`, or use a named constant you control. Day 51 shows how to measure the effect with hardware counters.

The engineering advice is conservative. Use mutexes for compound state, `seq_cst` atomics for single flags and counters, and weaken orders only with a written justification and a benchmark showing it matters. Lock-free does not mean faster: a contended atomic still bounces a cache line between cores, CAS loops can retry under contention, and a lock-free design's correctness argument is much harder to review. What lock-freedom does guarantee is progress (some thread always makes progress, no thread can block others by being descheduled while holding a lock), and that is the property to want it for, for example in a real-time thread that must never block on a lower-priority one.

#### watch out for

Mixing up "atomic" and "ordered". A `relaxed` flag is perfectly atomic and still publishes nothing: code that sets data, then `ready.store(true, std::memory_order_relaxed)`, then reads the data on the other side has a data race on the data. It may pass every test on x86, whose hardware ordering is strong enough to hide many such bugs, and then fail on ARM, or after a compiler upgrade reorders the stores. The memory model is a contract with the compiler and every CPU you will ever ship on, not a description of your test machine.

#### the takeaway

Atomicity makes a single variable race-free; memory orders decide what *other* memory becomes visible. Release/acquire pairs build happens-before edges, `relaxed` builds none, and `seq_cst` is the right default until a measurement says otherwise.

#### optional challenge

`x` and `y` are `std::atomic<int>` initialized to 0. Thread A runs `x.store(1, release); r1 = y.load(acquire);` and thread B runs `y.store(1, release); r2 = x.load(acquire);`. After both finish, can `r1 == 0 && r2 == 0`? What if every operation is `seq_cst`?

<details>
<summary>answer</summary>

With release/acquire, yes. Each acquire load synchronizes only with a release store *whose value it reads*; if both loads read 0, no synchronizes-with edge exists and nothing forbids the outcome. Real hardware produces it: a store can sit in the core's store buffer while the subsequent load of a different address executes. With `seq_cst` on all four operations, no: there is a single total order of the four operations consistent with each thread's program order, so whichever store comes first in that order precedes the other thread's load, which must then read 1. This "store buffering" pattern (as in Dekker's mutual exclusion algorithm) is the classic case where `seq_cst` is required and acquire/release is not enough.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-41"></a>

### day 41: deadlocks and concurrency design

**reading time:** about 10 minutes · **standard:** C++20 · **builds on:** days 36, 37, 38, 39, 40

#### the idea

A tracker merges track stores: `merge(a, b)` locks `a`, then `b`. Under rare timing, one thread runs `merge(left, right)` while another runs `merge(right, left)`. Each holds one mutex and waits forever for the other. Nothing crashes and nothing is logged; the robot simply stops publishing tracks after three days in the field. Deadlocks are the concurrency bug that hides best in testing, so the defenses have to be structural.

#### understanding the concept

A deadlock needs four conditions at once: mutual exclusion, hold-and-wait (holding one resource while waiting for another), no preemption (nobody can take a lock away), and a circular wait. Mutexes give you the first three for free, so practical defenses break the cycle:

- **Acquire several locks at once** with `std::scoped_lock(m1, m2)` (C++17). It uses the `std::lock` deadlock-avoidance algorithm, so argument order does not matter.
- **Fixed lock ordering** when locks are taken at different times: every code path acquires them in the same global order. A *lock hierarchy* makes this checkable: give each mutex a level and assert, in debug builds, that a thread only acquires locks with a lower level than any it already holds.
- **Never call unknown code while holding a lock.** A callback, a virtual function overridden elsewhere, or a user-supplied `std::function` can take other locks (creating a cycle you cannot see) or call back into your object and try to lock the same `std::mutex` again. Locking a `std::mutex` the calling thread already owns is UB, and in practice usually a self-deadlock. `std::recursive_mutex` hides the symptom, but the callback then runs while your invariants may be half-updated.

Two cousins are worth naming. In a *livelock*, threads keep reacting to each other (both back off with `try_lock`, both retry, forever) without progress. In *starvation*, one thread never gets its turn, for example a writer behind a constant stream of readers on a `std::shared_mutex`, whose fairness the standard does not specify.

C++20 also added three coordination primitives that replace many hand-rolled condition variable patterns:

| primitive | semantics | typical use |
|---|---|---|
| `std::latch` | one-shot countdown; `wait()` until it reaches zero | startup: wait until every driver is initialized |
| `std::barrier` | reusable; all participants `arrive_and_wait()` per phase; an optional completion function runs once per phase | lock-step simulation or pipelines |
| `std::counting_semaphore<N>` | a counter of permits; `acquire()` blocks at zero; any thread may `release()` | limit concurrent access to a resource |

#### in code

The merge deadlock and its fix:

```cpp
#include <mutex>
#include <vector>

struct Track { int id; double range_m; };
struct TrackStore {
    std::mutex m;
    std::vector<Track> tracks;
};

void merge_buggy(TrackStore& into, TrackStore& from) {
    std::lock_guard a(into.m);
    std::lock_guard b(from.m);     // BUG: merge(x, y) || merge(y, x) can deadlock
    into.tracks.insert(into.tracks.end(), from.tracks.begin(), from.tracks.end());
    from.tracks.clear();
}

void merge(TrackStore& into, TrackStore& from) {
    if (&into == &from) return;               // locking one std::mutex twice would be UB
    std::scoped_lock lock(into.m, from.m);    // both or neither, in any argument order
    into.tracks.insert(into.tracks.end(), from.tracks.begin(), from.tracks.end());
    from.tracks.clear();
}
```

Calling out of the lock. The tempting version runs handlers inside the critical section; if a handler calls `subscribe()`, the same thread locks `m_` twice:

```cpp
#include <functional>
#include <mutex>
#include <vector>

struct Detection { float range_m; };

class DetectionBus {
public:
    using Handler = std::function<void(const Detection&)>;
    void subscribe(Handler h) {
        std::lock_guard lock(m_);
        handlers_.push_back(std::move(h));
    }
    void publish(const Detection& d) {
        std::vector<Handler> snapshot;
        {
            std::lock_guard lock(m_);
            snapshot = handlers_;              // copy under the lock...
        }
        for (const auto& h : snapshot) h(d);   // ...call unknown code with no lock held
    }
private:
    std::mutex m_;
    std::vector<Handler> handlers_;
};
```

The copy costs allocations per publish; a `std::shared_ptr<const std::vector<Handler>>` snapshot (day 37) avoids that. Day 45 returns to this as the observer pattern, including unsubscription.

The C++20 primitives, one use each:

```cpp
#include <barrier>
#include <latch>
#include <semaphore>
#include <stop_token>
#include <thread>
#include <vector>

struct Blob;                                   // provided elsewhere:
void init_driver(int);  void run_driver(int, std::stop_token);  void run_until_shutdown();
void swap_buffers() noexcept;  void update_partition(int);  void send(const Blob&);

void start_drivers(int n) {
    std::latch initialized(n);                 // declared before the threads that use it
    std::vector<std::jthread> drivers;
    for (int i = 0; i < n; ++i)
        drivers.emplace_back([&initialized, i](std::stop_token st) {
            init_driver(i);
            initialized.count_down();
            run_driver(i, st);
        });
    initialized.wait();                        // every driver is initialized here
    run_until_shutdown();
}                                              // drivers stop and join, then the latch dies

std::barrier step_done(4, []() noexcept { swap_buffers(); });   // runs once per phase
void simulate(int part, int steps) {           // run by 4 threads
    for (int s = 0; s < steps; ++s) {
        update_partition(part);                // reads the old buffer, writes the new one
        step_done.arrive_and_wait();
    }
}

std::counting_semaphore<4> upload_slots(4);    // at most 4 concurrent uploads
void upload(const Blob& b) {
    upload_slots.acquire();
    struct Release { std::counting_semaphore<4>& s; ~Release() { s.release(); } } guard{upload_slots};
    send(b);                                   // released even if send throws
}
```

The barrier's completion function must be `noexcept`-invocable; it runs after all participants arrive and before any is released, which makes it the safe place to swap double buffers. A semaphore has no owner, unlike a mutex, so nothing stops a missing `release()`: wrap it in RAII as shown.

Finally, the minimal thread pool, built on day 38's `BoundedQueue`:

```cpp
#include <cstddef>
#include <functional>
#include <thread>
#include <vector>
// plus BoundedQueue<T> from day 38

class ThreadPool {
public:
    explicit ThreadPool(std::size_t n) : tasks_(1024) {
        for (std::size_t i = 0; i < n; ++i)
            workers_.emplace_back([this] {
                while (auto task = tasks_.pop()) (*task)();   // a throwing task terminates
            });
    }
    ~ThreadPool() { tasks_.close(); }     // workers drain the queue and exit, then join
    bool submit(std::function<void()> f) { return tasks_.push(std::move(f)); }
private:
    BoundedQueue<std::function<void()>> tasks_;
    std::vector<std::jthread> workers_;   // declared last: joined before tasks_ dies
};
```

It is about fifteen lines, and it is missing what production pools need: futures for results (day 39's `packaged_task`), exception handling, work stealing, priorities, and protection against the deadlock below. Use an existing executor (Boost.Asio's `thread_pool`, oneTBB, or your framework's) unless you have a reason not to.

#### in practice

The best way to avoid deadlocks is to need fewer locks. Three designs do most of the work:

- **Confinement**: each piece of mutable state is owned by exactly one thread. A lidar driver's parser state lives on the driver thread and is never shared.
- **Message passing**: threads communicate by moving values through queues (day 38). Ownership transfers with the message, so nothing is shared at all.
- **Immutable shared data**: configuration and calibration published as `std::shared_ptr<const T>` snapshots can be read by everyone without locks.

Locks then remain only inside a few small, well-tested components (queues, snapshot holders), which is where they belong. Test those components with stress tests: many iterations, more threads than cores, random small delays injected around the critical sections, and assertions on invariants. In a separate build on Linux or macOS, run them under ThreadSanitizer (`-fsanitize=thread` with GCC or Clang), which reports data races on the paths your tests execute and also lock-order inversions, the deadlock risk above, even in runs that did not actually deadlock.

#### watch out for

Thread-starvation deadlock in pools. A task running on a pool submits a subtask to the same pool and blocks on its future. If every worker does this at once, all workers are waiting for subtasks that no free worker can run. No mutex is involved, so lock ordering cannot save you. Avoid blocking waits inside pool tasks; split the work so the waiting happens outside the pool, or use a framework that runs nested tasks while waiting (work-stealing schedulers do).

#### the takeaway

Deadlocks come from cycles, so break the cycle by design: take multiple locks with `std::scoped_lock`, never call unknown code under a lock, and prefer confinement, message passing, and immutable data so that few locks exist at all.

#### optional challenge

In the fixed `merge`, why does the self-merge check matter? Without it, what does `merge(store, store)` do?

<details>
<summary>answer</summary>

`std::scoped_lock lock(into.m, from.m)` would be asked to lock the same `std::mutex` twice. The standard leaves the deadlock-avoidance algorithm unspecified; typical implementations lock one mutex and then `try_lock` the others. Either way, calling `lock` or `try_lock` on a `std::mutex` the calling thread already owns is UB. In practice the thread may hang, spin forever, or appear to succeed. Even if locking worked, the function body would then insert a vector into itself through iterators that the insertion can invalidate. The early return turns an invalid call into a no-op; documenting `into != from` as a precondition (and asserting it) is a reasonable alternative.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-42"></a>

### day 42: week 6 review: sharing safely

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 36 to 41

#### recap

| day | idea in one line |
|---|---|
| [36](#day-36) | Own every thread with RAII: `std::jthread` joins in its destructor, `stop_token` makes cancellation cooperative, and `detach` needs a written justification. |
| [37](#day-37) | A data race is UB; bundle each mutex with the data it guards, make each method one transaction, and never let a reference to guarded data escape the lock. |
| [38](#day-38) | A condition variable lets you sleep until shared state changes: change that state under the mutex, wait with a predicate, and choose a back-pressure policy on purpose. |
| [39](#day-39) | A future is a one-shot channel for a value or an exception; name the launch policy and keep `std::async` futures alive while the work should run. |
| [40](#day-40) | Atomicity makes one variable race-free; memory orders decide what *other* memory becomes visible. Release/acquire publishes, `relaxed` publishes nothing, `seq_cst` is the default. |
| [41](#day-41) | Deadlocks are cycles: take several locks with `std::scoped_lock`, never call unknown code under a lock, and design so that few locks exist at all. |

The theme of the week: shared mutable state is the problem, and every tool this week is a different way of controlling it. Mutexes serialize it, atomics shrink it to one variable, futures and queues hand it over, and good design (confinement, message passing, immutable snapshots) removes it.

#### review questions

1. A `Poller` class declares `std::jthread worker_;` first and `std::vector<float> buffer_;` second, and the thread function writes into `buffer_`. Every member is RAII. What can go wrong when a `Poller` is destroyed?

2. Two threads run this. Is it correct?

   ```cpp
   std::atomic<int> count{0};
   std::vector<int> data;

   void add(int x) {
       if (count.load() < 100) { data.push_back(x); ++count; }
   }
   ```

3. The producer never touches the mutex. Is there a data race? Can the consumer hang?

   ```cpp
   std::atomic<bool> ready{false};
   std::mutex m;
   std::condition_variable cv;

   void producer() { ready = true; cv.notify_one(); }
   void consumer() {
       std::unique_lock lock(m);
       cv.wait(lock, [] { return ready.load(); });
   }
   ```

4. This loop was meant to process chunks of a point cloud in parallel. A profile shows one core busy at a time. Why?

   ```cpp
   for (auto& chunk : chunks)
       std::async(std::launch::async, process, std::ref(chunk));
   ```

5. Pick a memory order for each: (a) a frames-processed counter that a statistics thread prints once a second; (b) a flag that tells a consumer a calibration struct has been fully written; (c) two threads that each set their own "I want to enter" flag and then read the other thread's flag.

6. **From week 5.** What is wrong here, and what are two fixes?

   ```cpp
   void start_fft(std::jthread& worker) {
       std::vector<float> samples = read_frame();
       worker = std::jthread([s = std::span<const float>(samples)] { fft(s); });
   }
   ```

7. **From week 2.** Threads A and B each hold their own copy of a `std::shared_ptr<const Config>` and reset it at the same time. Threads C and D share one global `std::shared_ptr<const Config> g_config`; C assigns a new config to it while D copies it. Which pair is safe?

#### mini exercise

Find three concurrency bugs in this class, then fix them. Assume `on_change`, `set`, and `get` can each be called from any thread at any time.

```cpp
#include <functional>
#include <map>
#include <mutex>
#include <string>

class TelemetryHub {
public:
    using Listener = std::function<void(const std::string&, double)>;

    void on_change(Listener l) { listener_ = std::move(l); }

    void set(const std::string& key, double value) {
        std::lock_guard lock(m_);
        latest_[key] = value;
        if (listener_) listener_(key, value);
    }

    const double& get(const std::string& key) {
        std::lock_guard lock(m_);
        return latest_.at(key);
    }

private:
    std::mutex m_;
    std::map<std::string, double> latest_;
    Listener listener_;
};
```

#### answers

<details>
<summary>1. member order and jthread</summary>

Members are destroyed in reverse declaration order, so `buffer_` is destroyed first, while `worker_` is still running. The thread can write into a destroyed vector until `worker_`'s destructor requests stop and joins: UB. Declare the `std::jthread` last, after everything it touches (day 36). The same rule kept day 41's `ThreadPool` correct.

</details>

<details>
<summary>2. an atomic counter does not protect a vector</summary>

No, and for two separate reasons. `data.push_back` from two threads is a data race on the vector, which is UB; making `count` atomic says nothing about other memory (day 40). And even with the vector protected, check-then-act is a race condition: both threads can see 99 and both append (day 37). Fix both with one mutex guarding the vector, with the check and the push in one critical section; `data.size()` then replaces the counter.

</details>

<details>
<summary>3. lost wakeup</summary>

No data race, since `ready` is atomic. Yes, it can hang. The consumer checks the predicate under `m` and sees `false`. Before it blocks, the producer sets `ready` and calls `notify_one()`; nobody is waiting yet, so the notification is lost and the consumer sleeps forever (unless a spurious wakeup rescues it). Because the producer never takes `m`, nothing orders its store between the consumer's check and its sleep. Fix: `{ std::lock_guard lk(m); ready = true; } cv.notify_one();`. With the store under the mutex, `ready` can be a plain `bool` (day 38).

</details>

<details>
<summary>4. the accidentally sequential loop</summary>

Each returned `std::future` is a temporary destroyed at the end of the statement, and a future from `std::async` blocks in its destructor until its task finishes. Every iteration waits for its own chunk (day 39). Since C++20, `std::async` is `[[nodiscard]]`, so GCC warns about this line. Keep the futures in a `std::vector<std::future<void>>`, then call `get()` on each, which also rethrows any exception a chunk threw.

</details>

<details>
<summary>5. choosing memory orders</summary>

(a) `relaxed`: only the count matters, and nothing is published through it. (b) `release` on the store and `acquire` on the load: the edge makes the struct's non-atomic writes visible after the flag is seen. (c) `seq_cst`: this is the store-buffering pattern from day 40's challenge, where acquire/release allows both threads to read `false`. If you are unsure, the default `seq_cst` is never wrong, only sometimes slower.

</details>

<details>
<summary>6. from week 5: a span handed to a thread</summary>

`std::span` borrows (day 31). `samples` is destroyed when `start_fft` returns, while the new thread may still be reading it: a dangling span and UB. A span is only safe to borrow across threads when the owner provably outlives the thread. Fixes: move ownership into the thread (`[v = std::move(samples)] { fft(v); }`, with `fft` taking a span so the vector converts), or share immutable data with `std::shared_ptr<const std::vector<float>>` when several threads need it.

</details>

<details>
<summary>7. from week 2: shared_ptr and threads</summary>

A and B are safe: the reference count updates are atomic, so separate `shared_ptr` objects that share a control block may be copied and destroyed concurrently (day 12). C and D are a data race on the single `g_config` object, UB. Copy it under a mutex (day 37's snapshot pattern) or use C++20's `std::atomic<std::shared_ptr<const Config>>`. That specialization is not guaranteed to be lock-free, so measure before assuming it beats a mutex. Either way, the `Config` itself is safe to read because it is `const`.

</details>

<details>
<summary>mini exercise: one solution</summary>

The bugs: (1) `on_change` writes `listener_` without the lock while `set` reads it, a data race. (2) `set` calls the listener while holding `m_`; a listener that calls `get()` locks `m_` again on the same thread (UB, in practice a self-deadlock), and one that takes another lock can form a lock-order cycle (day 41). (3) `get` returns a reference into the map; reading it after the lock is released races with a concurrent `set` of the same key (day 37).

```cpp
class TelemetryHub {
public:
    using Listener = std::function<void(const std::string&, double)>;

    void on_change(Listener l) {
        std::lock_guard lock(m_);
        listener_ = std::move(l);
    }

    void set(const std::string& key, double value) {
        Listener listener;
        {
            std::lock_guard lock(m_);
            latest_[key] = value;
            listener = listener_;           // copy under the lock
        }
        if (listener) listener(key, value); // call unknown code with no lock held
    }

    double get(const std::string& key) const {
        std::lock_guard lock(m_);
        return latest_.at(key);             // a copy, not a reference
    }

private:
    mutable std::mutex m_;
    std::map<std::string, double> latest_;
    Listener listener_;
};
```

The fix has a price worth naming: listeners now run outside the lock, so two concurrent `set` calls on the same key can notify in the opposite order to their writes. If listeners need a consistent order, push the updates into a queue drained by one thread (day 38). Copying the `std::function` may allocate on every `set`; a `std::shared_ptr<const Listener>` snapshot avoids that if a profile says it matters.

</details>

#### connections

- **Back to weeks 1 to 5.** A data race is the most common UB in concurrent code (day 06). RAII carries the week: `jthread`, `lock_guard`, `scoped_lock`, and day 41's semaphore guard are day 08's idea applied to threads and locks. Lambda captures (day 17) decide what a thread can touch and for how long. Futures carry exceptions with the guarantees from day 20, `std::optional` (day 24) is how a closed queue says "no more items", and `std::span` (day 31) is fine to hand to a thread only while its owner lives.
- **Ahead.** Week 7 is design. The thread-safe class as a unit of cohesion (day 37) returns with SOLID (day 43). Injecting a clock (day 44) makes timeouts and periodic threads testable. Day 41's `DetectionBus` becomes the observer pattern with RAII subscriptions (day 45), and coroutines (day 48) show asynchrony without a thread per task. Day 53 adds stress testing and sanitizers, and the day 55 capstone wires `BoundedQueue`, `std::jthread`, and `stop_token` into one pipeline.

[back to table of contents](#table-of-contents)

---

<a id="week-7"></a>

## week 7: software design and deeper c++

Design principles applied with judgment, plus C++20's two largest new language features.

<a id="day-43"></a>

### day 43: SOLID, coupling, and cohesion without dogma

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days 11, 12, 13

#### the idea

Every codebase has a class that everybody touches. In a radar team it might be `TrackFileProcessor`: it opens the recording, parses binary frames, drops low-SNR detections, converts units, and writes CSV. A new file format, a new filter threshold, and a new output column are three unrelated changes, made by three people, all landing in the same 900-line file and the same merge conflicts.

SOLID is usually presented as five rules that fix this. It is more useful to read the five letters as heuristics about one question: when a requirement changes, how much code has to change with it, and how much has to be recompiled, retested, and redeployed?

#### understanding the concept

Each principle in one sentence, phrased as the change it protects you from:

| principle | one-sentence version | the change it absorbs |
|---|---|---|
| single responsibility (SRP) | a module should have one reason to change, meaning one group of people or one requirement driving it | a format change does not touch filtering |
| open/closed (OCP) | you can add behaviour by adding code rather than editing working code | a new sensor type is a new class or a new variant alternative, not a new `case` in ten switches |
| Liskov substitution (LSP) | a derived type must honour the base contract, not just its signatures (day 13) | callers of `Sensor::read()` keep working with every sensor |
| interface segregation (ISP) | clients should not depend on functions they do not call | a change to calibration does not recompile the planner |
| dependency inversion (DIP) | high-level policy should depend on an abstraction it owns, and low-level detail should implement it | swapping the map backend does not touch the planner |

Two older ideas sit underneath all five. **Coupling** is the degree to which two pieces of code must change together. **Cohesion** is the degree to which the things inside one piece belong together, meaning they change for the same reasons and use the same data. Good design is high cohesion inside a module and low coupling between modules. SOLID is mostly a list of tactics for those two goals.

C++ adds a dimension most languages hide: **physical coupling**. Every `#include` in a header is a compile-time dependency for every file that includes that header, transitively. A logical design can look clean on a whiteboard while one widely included header pulls a heavy linear-algebra header into 400 translation units. That cost shows up as build times and as rebuild cascades when someone edits a private detail. Logical coupling decides what has to change together; physical coupling decides what has to recompile together.

#### in code

**SRP: separate the decision from the plumbing.** The before version mixes I/O, parsing, and policy, so you cannot test the filter without a file on disk.

```cpp
// before: three reasons to change in one function
void process_track_file(const std::string& in_path, const std::string& out_path) {
    std::ifstream in(in_path, std::ios::binary);
    std::ofstream out(out_path);
    RawFrame frame;
    while (in.read(reinterpret_cast<char*>(&frame), sizeof frame)) {  // format
        if (frame.snr_db < 12.0f) continue;                           // policy
        out << frame.range_m << ',' << frame.azimuth_deg << '\n';     // output
    }
}
```

```cpp
#include <algorithm>
#include <iterator>
#include <vector>

struct Detection { float range_m, azimuth_deg, snr_db; };

// policy: pure, cohesive, trivially unit-testable
struct SnrGate {
    float min_snr_db;
    bool accept(const Detection& d) const { return d.snr_db >= min_snr_db; }
};

std::vector<Detection> gate(const std::vector<Detection>& in, SnrGate g) {
    std::vector<Detection> out;
    std::copy_if(in.begin(), in.end(), std::back_inserter(out),
                 [&](const Detection& d) { return g.accept(d); });
    return out;
}

// format and output live in their own functions (or files), e.g.
// std::optional<Detection> parse_frame(const std::byte* p, std::size_t n);
// void write_csv(std::ostream& os, const std::vector<Detection>& ds);
```

Notice what we did not do: no `IDetectionFilter` interface, no factory. The responsibilities are separated by plain functions and a small value type. An abstraction can come later if a second filter actually appears.

**ISP and DIP: let the client define the interface.** A path planner that takes the whole robot couples to everything the robot can do.

```cpp
// before: the planner sees calibration, firmware update, and motor control
class Robot {
public:
    virtual ~Robot() = default;
    virtual bool is_occupied(int x, int y) const = 0;
    virtual void calibrate_lidar() = 0;
    virtual void flash_firmware(const std::vector<unsigned char>& image) = 0;
    virtual void set_wheel_speeds(double left, double right) = 0;
};
std::vector<Cell> plan(const Robot& robot, Cell from, Cell to);
```

```cpp
// after: the planner owns the narrow interface it needs (DIP),
// and nothing else leaks into it (ISP)
struct Cell { int x, y; };

class OccupancyQuery {        // lives in the planner's header, not the robot's
public:
    virtual ~OccupancyQuery() = default;
    virtual bool is_occupied(Cell c) const = 0;
};

std::vector<Cell> plan(const OccupancyQuery& map, Cell from, Cell to);

// the low-level module depends upward on the planner's abstraction
class GridMap final : public OccupancyQuery {
public:
    GridMap(int width, int height) : width_(width), cells_(std::size_t(width) * height) {}
    bool is_occupied(Cell c) const override {
        return cells_[std::size_t(c.y) * width_ + c.x] != 0;  // caller keeps c in range
    }
private:
    int width_;
    std::vector<unsigned char> cells_;
};
```

The key detail of DIP is *ownership* of the interface. If `OccupancyQuery` lived in the map library, the planner would still depend on the map library. Putting it next to the planner reverses the arrow: the map adapts to the planner, and a test can pass a ten-line fake (day 44 builds on exactly this).

**Physical coupling: keep headers light.** A header only needs a full definition when it uses the size or members of a type.

```cpp
// tracker.h
#pragma once
#include <memory>
#include <vector>

class KalmanFilter;           // forward declaration: no heavy include here
struct Detection;

class Tracker {
public:
    explicit Tracker(std::shared_ptr<const KalmanFilter> model);
    void update(const std::vector<Detection>& detections);  // incomplete type is fine in a declaration
private:
    std::shared_ptr<const KalmanFilter> model_;  // fine with an incomplete type
};                                               // (a unique_ptr member needs more care: day 47)
// tracker.cpp includes "kalman_filter.h" and "detection.h"
```

Now editing `kalman_filter.h` rebuilds `tracker.cpp`, not every file that includes `tracker.h`. Day 47 takes this further with pimpl.

#### in practice

A common failure mode in robotics stacks is the opposite of the god class: every concrete class gets an `I`-prefixed interface, a mock, and a factory, "for testability". After a year the codebase has 300 interfaces with exactly one production implementation each. Reading the control flow means jumping through an interface, a factory, and a registry to find the one class that actually runs. Every signature change is made twice. The mocks encode call sequences, so refactors break tests that did not catch any bug.

A better default is **the smallest thing that keeps options open**:

- Start concrete. Pure functions and value types are already decoupled and testable.
- Introduce an interface at a *real* seam: hardware, time, network, filesystem, a third-party library, or a point where you genuinely have two implementations today.
- Let the consumer own the interface, and keep it as narrow as that consumer needs.
- Keep headers lean, because the build graph is part of the architecture.

YAGNI ("you aren't gonna need it") is the counterweight to OCP. Being open for extension in a direction nobody extends costs indirection forever. Extracting an interface from concrete code when the second implementation arrives is usually a short, mechanical refactor; removing a speculative abstraction that ten modules depend on is not.

#### watch out for

The principles conflict, and following one to the extreme violates another. Taken literally, SRP produces dozens of one-method classes, which raises coupling between them because every behaviour now needs five collaborators wired together. OCP via virtual dispatch hides control flow: the debugger shows `filter->apply()`, and you need runtime state to know what ran. DIP through a virtual interface also has a mechanism cost (an indirect call that usually cannot be inlined); in a 1 kHz control loop that is almost never the bottleneck, but in a per-sample inner loop over millions of samples it can be, so measure with a profiler before and after rather than guessing.

Also notice that "reason to change" is about people and requirements, not about counting methods. A `Quaternion` class with 40 methods is cohesive: it all changes when the math changes, which is never.

#### the takeaway

SOLID, coupling, and cohesion are tools for predicting the cost of change. Use them to place seams where change actually happens, keep the rest concrete and boring, and remember that in C++ your header graph is part of your design.

#### optional challenge

A `MotorController` class has methods `set_torque`, `read_encoder`, `log_to_file`, `load_gains_from_yaml`, and `publish_diagnostics_over_udp`. Which of these would you pull out first, and which principle are you really applying?

<details>
<summary>answer</summary>

The control core is `set_torque` and `read_encoder`: they share state and change with the control law. `log_to_file`, `load_gains_from_yaml`, and `publish_diagnostics_over_udp` each change for a different reason (logging policy, config format, network protocol) and drag in heavy dependencies (filesystem, a YAML parser, sockets) that make the controller hard to build and test. Pull the YAML loading out first: it is pure input conversion and can become a free function returning a `Gains` value, which the controller accepts in its constructor. That is SRP, but the practical win is physical: the controller no longer includes the YAML library, so it compiles faster and can be tested without files. Diagnostics and logging can become an injected sink (day 44) once you need to swap them.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-44"></a>

### day 44: dependency injection and testable seams

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 12, 13, 17, 29, 43

#### the idea

Here is a joint controller that looks perfectly reasonable:

```cpp
class JointController {
public:
    void step(double target_rad) {
        const auto t = std::chrono::steady_clock::now();       // hidden dependency
        const double dt = std::chrono::duration<double>(t - last_).count();
        const double err = target_rad - motor_.position();
        motor_.command_torque(kp_ * err + kd_ * (err - last_err_) / dt);
        last_ = t;
        last_err_ = err;
    }
private:
    CanBusMotor motor_{"can0", 0x141};                          // hidden dependency
    double kp_ = 10.0, kd_ = 0.5, last_err_ = 0.0;
    std::chrono::steady_clock::time_point last_ = std::chrono::steady_clock::now();
};
```

How do you test that the derivative term behaves when `dt` is 10 ms? You can't, short of plugging in a CAN adapter and sleeping. The controller decides *what* to compute and also *where its inputs come from*. Dependency injection is just separating those: the object receives its collaborators instead of creating or fetching them.

#### understanding the concept

A **seam** is a place where you can change what code does without editing that code. Dependency injection creates seams deliberately. In C++ you have four main kinds, and they differ in when the choice is made:

| seam | chosen at | cost and constraints | good for |
|---|---|---|---|
| virtual interface, injected via constructor | run time | indirect call, usually not inlined; needs an interface type and a lifetime decision | hardware, I/O, plugins, anything chosen from config |
| template parameter (constrained by a concept) | compile time | no indirection; code lives in headers, each instantiation is separate code, longer builds | hot paths, header-only utilities, policies |
| `std::function` | run time | type erasure: indirect call, may allocate for large callables (day 17) | single callbacks: a time source, a log sink |
| link-time | link time | one implementation per binary; invisible in the source | replacing a platform function (time, GPIO) in a test binary |

Two decisions come with every injected dependency. **Ownership**: does the controller own the clock (`std::unique_ptr<Clock>`), share it (`std::shared_ptr`, rarely justified), or borrow it (a reference, with the caller promising it outlives the controller)? Day 12's rules apply unchanged. **Who wires things up**: the answer should be one place near `main`, often called the composition root, where concrete objects are created and passed down. Everything below it just takes what it is given.

On the test side, distinguish a **fake** from a **mock**. A fake is a small working implementation with its own state: a clock that only moves when the test advances it. A mock records calls and verifies expectations about them ("`command_torque` called once with 60"). Prefer fakes and check outcomes; reach for mocks when the interaction itself is the requirement, such as "the enable command must precede the first torque command".

#### in code

**Constructor injection with interfaces.** The controller now borrows a clock and an actuator. Production code passes the real ones; tests pass fakes.

```cpp
#include <chrono>

class Clock {
public:
    virtual ~Clock() = default;
    virtual std::chrono::steady_clock::time_point now() const = 0;
};

class Actuator {
public:
    virtual ~Actuator() = default;
    virtual double position() const = 0;           // rad
    virtual void command_torque(double nm) = 0;
};

class JointController {
public:
    JointController(const Clock& clock, Actuator& motor, double kp, double kd)
        : clock_(clock), motor_(motor), kp_(kp), kd_(kd), last_(clock.now()) {}

    void step(double target_rad) {
        const auto t = clock_.now();
        const double dt = std::chrono::duration<double>(t - last_).count();
        const double err = target_rad - motor_.position();
        const double derr = dt > 0.0 ? (err - last_err_) / dt : 0.0;
        motor_.command_torque(kp_ * err + kd_ * derr);
        last_ = t;
        last_err_ = err;
    }

private:
    const Clock& clock_;         // borrowed: must outlive the controller
    Actuator& motor_;            // borrowed
    double kp_, kd_;
    std::chrono::steady_clock::time_point last_;
    double last_err_ = 0.0;
};
```

The test is now deterministic and runs in microseconds:

```cpp
#include <cassert>
#include <cmath>
#include <iostream>

struct FakeClock final : Clock {
    std::chrono::steady_clock::time_point t{};
    std::chrono::steady_clock::time_point now() const override { return t; }
};

struct FakeActuator final : Actuator {
    double pos = 0.0, last_torque = 0.0;
    double position() const override { return pos; }
    void command_torque(double nm) override { last_torque = nm; }
};

int main() {
    using namespace std::chrono_literals;
    FakeClock clock;
    FakeActuator motor;
    JointController ctl(clock, motor, /*kp=*/10.0, /*kd=*/0.5);

    clock.t += 10ms;
    ctl.step(1.0);                     // err 1.0, derr 100/s: 10 + 50
    assert(std::abs(motor.last_torque - 60.0) < 1e-9);

    motor.pos = 0.5;
    clock.t += 10ms;
    ctl.step(1.0);                     // err 0.5, derr -50/s: 5 - 25
    std::cout << motor.last_torque << '\n';   // prints: -20
}
```

**Compile-time injection with a concept (C++20).** When the dependency is fixed per build and sits on a hot path, make it a template parameter. The concept documents what the dependency must provide and gives readable errors (day 29).

```cpp
#include <chrono>
#include <concepts>
#include <optional>

template <typename C>
concept SteadyTimeSource = requires(const C& c) {
    { c.now() } -> std::same_as<std::chrono::steady_clock::time_point>;
};

template <SteadyTimeSource Clock>
class RateLimiter {
public:
    RateLimiter(Clock clock, std::chrono::nanoseconds min_gap)
        : clock_(std::move(clock)), gap_(min_gap) {}

    bool allow() {
        const auto t = clock_.now();
        if (last_ && t - *last_ < gap_) return false;
        last_ = t;
        return true;
    }

private:
    Clock clock_;
    std::chrono::nanoseconds gap_;
    std::optional<std::chrono::steady_clock::time_point> last_;
};

struct SystemSteadyClock {                       // production
    auto now() const { return std::chrono::steady_clock::now(); }
};
struct ManualClock {                             // test: reads a time the test controls
    const std::chrono::steady_clock::time_point* t;
    auto now() const { return *t; }
};

// usage in a test:
//   std::chrono::steady_clock::time_point now{};
//   RateLimiter limiter(ManualClock{&now}, 100ms);    // CTAD picks ManualClock
//   limiter.allow();  // true
//   now += 50ms;  limiter.allow();  // false
//   now += 60ms;  limiter.allow();  // true
```

No interface, no virtual call, and `SystemSteadyClock` is an empty class (it still occupies at least one byte as a member; `[[no_unique_address]]` in C++20 can remove that). The price is that `RateLimiter<ManualClock>` and `RateLimiter<SystemSteadyClock>` are different types, so you cannot store both in one container or choose between them from a config file.

**A `std::function` seam** is the lightest runtime option when the dependency is a single operation:

```cpp
#include <functional>

using TimeSource = std::function<std::chrono::steady_clock::time_point()>;

class Watchdog {
public:
    explicit Watchdog(TimeSource now = [] { return std::chrono::steady_clock::now(); })
        : now_(std::move(now)), last_kick_(now_()) {}
    void kick() { last_kick_ = now_(); }
    bool expired(std::chrono::milliseconds limit) const { return now_() - last_kick_ > limit; }
private:
    TimeSource now_;
    std::chrono::steady_clock::time_point last_kick_;
};
```

#### in practice

**Link-time seams** deserve a mention because embedded and robotics code uses them heavily. Suppose the low-level HAL declares `std::uint64_t hal_monotonic_ns();` in a header. The firmware build links `hal_time_stm32.cpp`; the host test build links `hal_time_fake.cpp`, which returns a global the test sets. The code under test has no interface, template, or callback at all. The tradeoffs: only one implementation per binary, the seam is invisible when reading the source (only the build files reveal it), and if both files end up in the same link you get a duplicate-symbol error, or worse, with static libraries the linker silently uses whichever definition it pulls in first. Use it for platform functions you cannot change, not for application design.

In a typical robot stack the result looks like this: `main` reads config, constructs `CanBusMotor`, `SystemClock`, and a `UdpTelemetrySink`, then passes references into controllers and planners. Unit tests construct the same controllers with fakes, and hardware-in-the-loop tests swap only the motor. Nothing below `main` ever calls `steady_clock::now()` or opens a socket on its own.

#### watch out for

**Service locators and DI containers.** A global registry you query (`Services::get<Clock>()`) looks convenient, but it hides dependencies again: the constructor no longer tells you what the class needs, missing registrations fail at run time instead of compile time, and tests have to reset global state. Reflection-driven DI frameworks from Java or C# have no direct C++ equivalent, and the libraries that emulate them add template complexity to save a few lines in `main`. Explicit constructor arguments are usually enough.

**Borrowed references outliving their owner.** `JointController` stores references, so this compiles and is undefined behavior on the first `step`:

```cpp
JointController make_controller(Actuator& motor) {
    SystemClock clock;                        // production Clock, local to this function
    return JointController(clock, motor, 10.0, 0.5);
}   // BUG: clock is destroyed; the returned controller holds a dangling reference
```

If lifetimes are not obviously nested, take ownership (`std::unique_ptr<Clock>`) instead.

Also watch the constructor length. A class that needs eight injected collaborators is usually telling you about poor cohesion (day 43), not about a lack of DI tooling.

#### the takeaway

Inject what crosses a boundary (time, hardware, I/O, randomness), choose the seam by when the decision is made (run time, compile time, link time), make ownership explicit, and wire everything in one place near `main`.

#### optional challenge

`RateLimiter` stores its clock by value. Why does the test version use `ManualClock` holding a pointer, instead of passing a `FakeClock` with a mutable `t` member directly?

<details>
<summary>answer</summary>

Because `RateLimiter` copies (or moves) the clock into its own member `clock_`. If the test passed a `FakeClock` value, advancing the test's copy would not affect the limiter's copy, so time would never move from the limiter's point of view. The pointer gives the copy a handle back to state the test controls. Alternatives: pass a `std::reference_wrapper`-like adapter, or give `RateLimiter` a reference member and accept the borrowed-lifetime rule. Value semantics for injected policies is a good default for stateless or cheaply copied policies; when the test needs to observe or steer shared state, some form of indirection is unavoidable.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-45"></a>

### day 45: design patterns in modern C++: strategy, factory, and observer

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 12, 17, 25, 41, 43

#### the idea

The classic pattern catalogue was written for C++98 and Smalltalk, before lambdas, `std::function`, `std::variant`, and smart pointers. Some patterns survive unchanged, some shrink to a single line, and some need modern care that the original books never mentioned, such as who owns an observer and which thread calls it. Today we look at three that every production codebase uses, and at what each one looks like when written with the tools you have now.

#### understanding the concept

A pattern is a name for a recurring solution, not a goal. Its main value is vocabulary: "the planner takes a cost strategy" tells a reviewer a lot in six words. The risk is building the pattern because it is a pattern.

- **Strategy** makes an algorithm a replaceable part. In C++ you have three ways to plug it in, with different tradeoffs (the table below).
- **Factory** hides which concrete type gets created. In modern C++ the default form is a plain function returning `std::unique_ptr<Base>`; a registry of creators appears when the choice comes from data (a config file, a plugin name).
- **Observer** lets a subject notify interested parties without knowing them. The hard parts are lifetime (an observer destroyed while still registered) and concurrency (calling unknown code while holding a lock, day 41).

Several other classic patterns collapse into language features. Command is usually a lambda stored in a `std::function` or a queue. Visitor over a closed set of types is `std::visit` on a `std::variant` (day 25). Template method is often better served by passing a callable than by inheritance.

#### in code

**Strategy, three ways.** An exponential moving average smooths radar range measurements inside a tracker.

```cpp
#include <functional>
#include <memory>

struct Ema {                                    // the algorithm as a plain value type
    double alpha;
    double y = 0.0;
    bool primed = false;
    double operator()(double x) {
        y = primed ? alpha * x + (1.0 - alpha) * y : x;
        primed = true;
        return y;
    }
};

// (a) virtual interface: strategies must inherit
class Smoother {
public:
    virtual ~Smoother() = default;
    virtual double operator()(double x) = 0;
};
class EmaSmoother final : public Smoother {
public:
    explicit EmaSmoother(double alpha) : ema_{alpha} {}
    double operator()(double x) override { return ema_(x); }
private:
    Ema ema_;
};
struct TrackerV { std::unique_ptr<Smoother> smooth; };

// (b) std::function: any callable with the right signature
struct TrackerF { std::function<double(double)> smooth; };

// (c) template parameter: fixed at compile time
template <typename Smooth>
struct TrackerT { Smooth smooth; };

// TrackerV v{std::make_unique<EmaSmoother>(0.3)};
// TrackerF f{Ema{0.3}};
// TrackerT<Ema> t{Ema{0.3}};
```

| | virtual interface | `std::function` | template parameter |
|---|---|---|---|
| chosen at | run time | run time | compile time |
| strategy types | must derive from `Smoother` | any copyable callable | any type the code compiles with (use a concept in C++20) |
| call mechanism | indirect call, rarely inlined | indirect call through type erasure; construction may allocate | direct call, inlinable |
| copying the owner | needs a `clone()` | value semantics | value semantics |
| mixed strategies in one container | yes | yes | no, each is a distinct type |
| best for | several related operations per strategy | one operation, callbacks | hot inner loops, per-build choice |

**Factory with a registry.** When a config file says `type: lidar`, something has to map that string to a constructor.

```cpp
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>

struct SensorConfig { std::string type, device; };

class Sensor {
public:
    virtual ~Sensor() = default;
    virtual double read() = 0;
};

using SensorFactory = std::function<std::unique_ptr<Sensor>(const SensorConfig&)>;

class SensorRegistry {
public:
    void add(std::string type, SensorFactory f) { makers_[std::move(type)] = std::move(f); }
    std::unique_ptr<Sensor> create(const SensorConfig& cfg) const {
        const auto it = makers_.find(cfg.type);
        if (it == makers_.end()) throw std::invalid_argument("unknown sensor type: " + cfg.type);
        return it->second(cfg);
    }
private:
    std::unordered_map<std::string, SensorFactory> makers_;
};

// explicit registration, called once from main: visible, ordered, link-safe
void register_builtin_sensors(SensorRegistry& r) {
    r.add("imu",   [](const SensorConfig& c) { return std::make_unique<Imu>(c.device); });
    r.add("lidar", [](const SensorConfig& c) { return std::make_unique<Lidar>(c.device); });
}
```

The tempting alternative is self-registration, where each `.cpp` file registers itself from a namespace-scope initializer:

```cpp
// lidar.cpp: "automatic" registration
namespace {
const bool lidar_registered = (global_registry().add("lidar", make_lidar), true);
}
```

It works in a demo and breaks in production for two reasons. First, if `lidar.o` lives in a static library and nothing else references a symbol in it, the linker never pulls that object file into the executable, so the initializer never runs and `"lidar"` is silently unknown (the usual workarounds, `--whole-archive` or `/WHOLEARCHIVE`, are build-system patches for a design problem). Second, the registry itself must be a function-local static, or you have the static initialization order problem from day 03. An explicit `register_builtin_sensors` call costs one line and has neither problem.

**Observer with RAII subscriptions.** The subscription token unsubscribes in its destructor, and `emit` calls observers outside the lock.

```cpp
#include <functional>
#include <map>
#include <memory>
#include <mutex>
#include <vector>

template <typename... Args>
class Signal {
    using Slot = std::function<void(Args...)>;
    struct State {
        std::mutex m;
        std::map<int, std::shared_ptr<Slot>> slots;
        int next_id = 0;
    };
    std::shared_ptr<State> state_ = std::make_shared<State>();

public:
    class Subscription {
    public:
        Subscription(std::weak_ptr<State> s, int id) : state_(std::move(s)), id_(id) {}
        Subscription(Subscription&&) noexcept = default;
        Subscription& operator=(Subscription&& o) noexcept {
            if (this != &o) { reset(); state_ = std::move(o.state_); id_ = o.id_; }
            return *this;
        }
        ~Subscription() { reset(); }
        void reset() {
            if (auto s = state_.lock()) {            // the signal may already be gone
                std::lock_guard lock(s->m);
                s->slots.erase(id_);
            }
            state_.reset();
        }
    private:
        std::weak_ptr<State> state_;
        int id_;
    };

    [[nodiscard]] Subscription subscribe(Slot f) {
        std::lock_guard lock(state_->m);
        const int id = state_->next_id++;
        state_->slots.emplace(id, std::make_shared<Slot>(std::move(f)));
        return Subscription(state_, id);
    }

    void emit(Args... args) const {
        std::vector<std::shared_ptr<Slot>> snapshot;
        {
            std::lock_guard lock(state_->m);
            for (const auto& kv : state_->slots) snapshot.push_back(kv.second);
        }
        for (const auto& slot : snapshot) (*slot)(args...);   // no lock held here
    }
};

// Signal<int> track_lost;
// {
//     auto sub = track_lost.subscribe([](int id) { std::cout << "lost " << id << '\n'; });
//     track_lost.emit(7);        // prints: lost 7
// }                              // sub destroyed: unsubscribed
// track_lost.emit(8);            // prints nothing
```

`[[nodiscard]]` matters here: discarding the token would unsubscribe immediately. The `weak_ptr` lets a token outlive its signal safely. The moved-from token holds an empty `weak_ptr`, so its destructor does nothing.

#### in practice

A radar tracker publishes "track confirmed" and "track lost" events to a display, a recorder, and a fusion module. With a raw `std::vector<Listener*>` in the tracker, the display gets closed, its object is destroyed, and the next event calls through a dangling pointer: undefined behavior, typically a crash far from the cause. RAII tokens tie the subscription's lifetime to the subscriber object (store the token as a member, and it unsubscribes when the subscriber dies).

The other classic fix is a subject holding `std::weak_ptr<Listener>` and calling `lock()` before each notification. It is correct, but it forces every observer to be owned by a `shared_ptr`, which is an ownership decision imposed by the notification mechanism (day 12 calls that a smell). Tokens leave ownership to the observer.

Calling observers outside the lock is the day 41 rule in action: a slot that subscribes, unsubscribes, or emits again would deadlock on a non-recursive mutex if `emit` held it, and a slow slot would block every other thread trying to subscribe.

#### watch out for

The snapshot in `emit` has a consequence. A slot can be called after its token was reset, if the reset happened after the snapshot was taken. The `shared_ptr<Slot>` keeps the `std::function` alive, but not whatever its lambda captured by reference, so if the subscriber object is gone, the call is undefined behavior. In a single thread this only happens when one slot destroys another subscriber during `emit`; re-checking under the lock that each slot is still registered just before calling it closes that case. Across threads the re-check can go stale between the check and the call, so either make `reset` wait until in-flight calls to that slot finish, or deliver events by posting to the subscriber's own thread or queue (day 38). Decide which threading contract your signal offers and document it.

Patterns also invite premature generality. A `SensorRegistry` for two sensor types that are chosen by a compile-time flag is overkill; a `switch` in one factory function is clearer until the set becomes data-driven.

#### the takeaway

Use pattern names as vocabulary, then pick the lightest C++ mechanism that does the job: a callable for one-operation strategies, a function returning `std::unique_ptr` for factories, and RAII tokens plus lock-free notification for observers. Explicit wiring beats clever static registration.

#### optional challenge

A colleague changes `emit` to hold the lock while calling the slots, "to fix the cross-thread race". What breaks, even in a single-threaded program?

<details>
<summary>answer</summary>

Any slot that touches the same signal from inside the callback now deadlocks, because `std::mutex` is not recursive and locking it twice from the same thread is undefined behavior (in practice usually a deadlock). Common cases are a one-shot listener that destroys its own token when it fires, a listener that subscribes a follow-up handler, and an event handler that emits another event on the same signal. Switching to `std::recursive_mutex` hides the deadlock but not the problem: erasing from `slots` while `emit` is iterating over it invalidates the iterator, which is also undefined behavior. The snapshot exists precisely to make reentrancy safe; the cross-thread issue needs a different fix (wait for in-flight calls, or post to the subscriber's thread).

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-46"></a>

### day 46: static versus dynamic polymorphism and type erasure

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 13, 17, 25, 29, 45

#### the idea

A telemetry recorder must store a mixed stream of records: IMU samples from your team, battery states from the power team, GPS fixes from a vendor library you cannot modify. Each can render itself as text. How do you put them in one `std::vector` and call "render" on each?

"Make them inherit from `Record`" is the reflex, and it fails on the vendor type straight away. C++ gives you at least four ways to get "one call, many types", and they differ in who has to know about whom, when the choice is made, and what you pay for it.

#### understanding the concept

| | virtual functions | templates + concepts | `std::variant` | type erasure |
|---|---|---|---|---|
| set of types | open | open | closed (listed in the variant) | open |
| user types must inherit | yes | no | no | no |
| semantics | reference (via pointer to base) | value | value | value |
| one heterogeneous container | yes, of pointers | no | yes | yes |
| call mechanism | indirect call, usually through a vtable | direct, inlinable | `std::visit` dispatch (implementation-specific, often a jump table) | indirect call inside the wrapper |
| typical cost to watch | heap allocation per object, no inlining | compile time, code size per instantiation | adding a type touches every visitor | allocation per object unless small-buffer optimized, a clone per copy |
| across a shared-library boundary | the standard plugin mechanism | not applicable, code is instantiated in the caller | adding an alternative changes the type and its layout | possible if the wrapper's layout is fixed |

None of the "call mechanism" entries is a performance verdict. An indirect call costs a load and a branch that may be predicted well or badly, and it blocks inlining, which often matters more than the call itself. Whether any of that shows up depends on how much work each call does. Measure with a profiler on the real workload before choosing on speed.

**Static polymorphism** resolves the call at compile time. The old tool is CRTP (the curiously recurring template pattern): a base class template that casts `this` to the derived type. In C++20, a concept plus a free function template often does the same job with less ceremony, and C++23's deducing `this` (an explicit object parameter, `this const auto& self`) removes most of CRTP's boilerplate. That is C++23 only.

**Type erasure** is how `std::function` and `std::any` work. A template constructor sees the concrete type once, wraps it in an internal "model" object that implements a private interface, and stores it behind a pointer of fixed type. After construction the wrapper's type no longer mentions the concrete type: it has been erased. Inheritance still exists, but it is hidden inside the wrapper instead of imposed on users.

#### in code

**Static polymorphism: CRTP versus a concept.** Both share the "raw times scale" logic without a virtual call.

```cpp
#include <concepts>

// CRTP: the base knows the derived type through the template argument
template <typename Derived>
class SensorBase {
public:
    double read_si() const {
        const auto& self = static_cast<const Derived&>(*this);
        return self.raw() * self.scale();
    }
};
class Thermistor : public SensorBase<Thermistor> {
public:
    int raw() const { return 2048; }
    double scale() const { return 0.05; }
};

// C++20 alternative: no base class at all
template <typename S>
concept ScaledSensor = requires(const S& s) {
    { s.raw() } -> std::integral;
    { s.scale() } -> std::floating_point;
};
double read_si(const ScaledSensor auto& s) { return s.raw() * s.scale(); }

// Thermistor{}.read_si() and read_si(Thermistor{}) both return 102.4
```

`SensorBase<Thermistor>` and `SensorBase<StrainGauge>` are unrelated types, so CRTP gives shared code, not a common type to store. Either way you cannot put both sensors in one container.

**Hand-written type erasure.** The users' types implement nothing; they only need a free function `to_text` that argument-dependent lookup can find, which also works for the vendor type because you can write that function yourself in its namespace.

```cpp
#include <concepts>
#include <memory>
#include <string>
#include <utility>

template <typename T>
concept TextRenderable = requires(const T& t) {
    { to_text(t) } -> std::convertible_to<std::string>;
};

class Record {
public:
    template <TextRenderable T>
    Record(T value) : self_(std::make_unique<Model<T>>(std::move(value))) {}

    Record(const Record& other) : self_(other.self_->clone()) {}
    Record& operator=(const Record& other) { return *this = Record(other); }
    Record(Record&&) noexcept = default;
    Record& operator=(Record&&) noexcept = default;

    friend std::string to_text(const Record& r) { return r.self_->render(); }

private:
    struct Concept {                                    // private interface
        virtual ~Concept() = default;
        virtual std::string render() const = 0;
        virtual std::unique_ptr<Concept> clone() const = 0;
    };
    template <typename T>
    struct Model final : Concept {                      // one per stored type
        explicit Model(T v) : value(std::move(v)) {}
        std::string render() const override { return to_text(value); }
        std::unique_ptr<Concept> clone() const override { return std::make_unique<Model>(*this); }
        T value;
    };
    std::unique_ptr<Concept> self_;
};
```

The virtual function is named `render`, not `to_text`, on purpose: inside `Model`, an unqualified call to `to_text` would otherwise find the member first, and finding a class member suppresses argument-dependent lookup, so the user's free function would never be considered.

Using it:

```cpp
#include <iostream>
#include <vector>

namespace imu {
struct Sample { int seq; };
std::string to_text(const Sample& s) { return "imu #" + std::to_string(s.seq); }
}
namespace vendor {                                      // pretend we cannot edit this struct
struct GpsFix { int sats; };
}
namespace vendor {                                      // but we can add a function next to it
std::string to_text(const GpsFix& g) { return "gps sats=" + std::to_string(g.sats); }
}

int main() {
    std::vector<Record> records{imu::Sample{41}, vendor::GpsFix{9}};
    records.push_back(records.front());                  // value semantics: deep copy
    for (const auto& r : records) std::cout << to_text(r) << '\n';
    // prints: imu #41
    //         gps sats=9
    //         imu #41
}
```

Adding a function to a vendor's namespace is your code, in your translation units, so it is fine; adding declarations to namespace `std` is not (with narrow exceptions such as specializing certain templates for your own types).

#### in practice

In a robotics stack the four options usually coexist, each where it fits:

- **Plugins loaded at run time** (a `dlopen`'d planner or driver) use a virtual interface plus an `extern "C"` factory function. Templates cannot cross that boundary, and a virtual interface is the most widely understood ABI contract, as long as you never change the virtual functions of a released interface (even adding one can shift vtable slots, which is implementation-specific); publish a new versioned interface instead.
- **Messages on an internal bus** with a fixed, versioned set of types are a `std::variant`. The closed set is a feature: the compiler can tell you about every visitor you forgot to update (day 25).
- **Hot numerical kernels** take their policies as template parameters constrained by concepts, so filters and interpolators inline into the loop.
- **Task queues and callbacks** store `std::function` or a small custom erased wrapper, because the queue must hold arbitrary callables by value.

Sean Parent's line "inheritance is the base class of evil" is about the first option leaking into everything: if the interface is a base class, every user type must inherit from it, objects live behind pointers, and copying needs a `clone()` hierarchy. Type erasure keeps the inheritance private and gives users plain value types.

#### watch out for

**Type erasure is not free and not always worth it.** The wrapper above allocates once per stored object and once per copy, every call is an indirect call, and debuggers show you `Model<imu::Sample>` frames you did not write. Real implementations often add a **small buffer optimization**: store small objects inside the wrapper itself and fall back to the heap for large ones. Whether and when `std::function` does this is an implementation detail (buffer sizes and conditions differ between libstdc++, libc++, and MSVC), so do not design around it; count allocations if it matters (day 52). Also note that the wrapper requires copyable types; a move-only callable needs a move-only wrapper, which the standard only provides in C++23 (`std::move_only_function`).

If you own all the types, need reference semantics anyway, and the set is open, a ten-line virtual interface is easier to read and debug than a forty-line erased wrapper. Reach for type erasure when you need value semantics or must accept types that cannot inherit from your base.

#### the takeaway

Choose by the shape of the problem: virtual functions for open sets behind pointers and binary boundaries, templates and concepts for compile-time choice and speed, `std::variant` for closed sets, and type erasure for open sets with value semantics. The cost model is different for each, so measure before choosing on performance.

#### optional challenge

`Record`'s converting constructor takes `T` by value and is constrained by `TextRenderable`. `Record` itself satisfies `TextRenderable` (its hidden friend `to_text` is found by ADL). So why doesn't `Record copy = records.front();` wrap a `Record` inside a `Model<Record>`?

<details>
<summary>answer</summary>

Because the copy constructor wins. For `Record copy = records.front();` the argument is a `Record` lvalue. Overload resolution looks at the copy constructor `Record(const Record&)` and at the constructor template, but the standard says a constructor template is never instantiated to produce a constructor whose first parameter is the class type by value (that signature would be a broken copy constructor), so the template is not a viable candidate here. If the constructor took `T&&` (a forwarding reference) instead, a non-const lvalue `Record` would deduce `T = Record&`, the template would be a better match than `const Record&`, and copying would try to wrap a `Record` inside a `Model<Record>`: at best a silent extra layer of allocation and indirection per copy, and with this concept GCC 12 reports a recursive constraint error instead. That is why forwarding constructors in erased wrappers need an explicit `!std::same_as<std::remove_cvref_t<T>, Record>` constraint.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-47"></a>

### day 47: designing APIs that are hard to misuse

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 04, 12, 20, 26, 31

#### the idea

```cpp
bool move_joint(int joint, double position, double velocity, double timeout);

move_joint(2, 1.5, 0.5, 30);    // radians? degrees? 30 seconds or 30 ms? did it fail?
```

This compiles whether you swap position and velocity, pass degrees, or ignore the result. Every one of those mistakes is a bug that only shows up on the robot. A good API makes the correct call easy to write and the wrong call hard to write, ideally impossible to compile. Today is about the tools C++ gives you for that, and about the extra promise a library makes once it ships as a binary.

#### understanding the concept

An API is a contract with three parts. **Preconditions** are what the caller must guarantee (the joint index exists, the span is non-empty). **Postconditions** are what the function guarantees on success (the joint reached the target within tolerance). **Invariants** are what is always true of an object between calls (a `Trajectory` is time-ordered). C++20 has no language feature for contracts; C++26 adds `pre`, `post`, and `contract_assert`, but in C++20 you have, in decreasing order of strength:

1. **Types** that make violations unrepresentable: strong types, enums instead of `bool` flags, `std::span` instead of pointer plus length.
2. **Construction** that establishes invariants (a constructor that validates, or a factory returning `std::optional`).
3. **Assertions** for preconditions you cannot encode in types.
4. **Documentation** for the rest.

The signature itself is part of the contract. Day 12's ownership rules and week 4 and 5's view types give a compact vocabulary:

| parameter | tells the caller |
|---|---|
| `T` (cheap or sink) | "I take my own copy" |
| `const T&` | "I read it during the call and keep nothing" |
| `std::string_view`, `std::span<const T>` | "I borrow a sequence for the duration of the call" |
| `T*` | "may be null, I do not own it" |
| `std::unique_ptr<T>` by value | "ownership transfers to me" |
| `std::shared_ptr<T>` by value | "I will share ownership beyond this call" |

Then choose **one error channel per kind of failure** and use it consistently across the API (day 20): exceptions for failures the immediate caller cannot handle, return values (`std::optional`, a `std::variant` or small result type, an error code) for expected outcomes such as a sensor timeout. Mark those return types or functions `[[nodiscard]]` so ignoring them is a warning. (`std::expected` is the standard result type in C++23.)

Finally, separate **API** stability (source code that compiled against version 1 still compiles against version 2) from **ABI** stability (binaries built against version 1 still link and run against version 2's shared library). ABI is much more fragile: changing a class's size, the order of its members, its virtual functions, or an inline function's body breaks it, even when the source-level API is unchanged.

#### in code

**Strong types and enums at the call site.**

```cpp
#include <chrono>
#include <compare>
#include <cstdint>
#include <optional>

template <typename Tag>
struct Quantity {
    double value;
    constexpr explicit Quantity(double v) : value(v) {}
    friend constexpr Quantity operator+(Quantity a, Quantity b) { return Quantity(a.value + b.value); }
    friend constexpr auto operator<=>(Quantity, Quantity) = default;
};
using Radians          = Quantity<struct RadiansTag>;
using RadiansPerSecond = Quantity<struct RadiansPerSecondTag>;

enum class JointId : std::uint8_t {};
enum class MoveError { unreachable, timeout, estop_active };

struct MoveRequest {
    Radians target;
    RadiansPerSecond max_speed;
    std::chrono::milliseconds timeout;
};

[[nodiscard]] std::optional<MoveError> move_joint(JointId joint, const MoveRequest& req);

// move_joint(JointId{2}, {Radians(1.5), RadiansPerSecond(0.5), std::chrono::seconds(30)});
// move_joint(JointId{2}, {RadiansPerSecond(0.5), Radians(1.5), ...});  // does not compile
// move_joint(2, ...);                                                    // does not compile
```

Each `struct ...Tag` declared inside the template argument creates a distinct type, so `Radians` and `RadiansPerSecond` do not mix. `std::chrono` already does this for time, including safe conversion from seconds to milliseconds. For real unit algebra (meters divided by seconds giving meters per second) use a units library such as mp-units rather than growing this template. The `JointId{2}` form uses C++17's rule that an enum with a fixed underlying type can be list-initialized from an integer, while `JointId j = 2;` is still an error.

One honest weakness: `std::optional<MoveError>` reads backwards (an engaged optional means failure). A small result type with a named `ok()` member, or C++23 `std::expected<void, MoveError>`, says it better.

**The pimpl idiom: a compile-time and ABI firewall.**

```cpp
// lidar_driver.h: the only thing clients see
#pragma once
#include <cstddef>
#include <memory>
#include <span>
#include <string_view>

class LidarDriver {
public:
    explicit LidarDriver(std::string_view device);
    ~LidarDriver();                                   // declared here, defined in the .cpp
    LidarDriver(LidarDriver&&) noexcept;
    LidarDriver& operator=(LidarDriver&&) noexcept;

    [[nodiscard]] std::size_t read_scan(std::span<float> ranges_out);
    [[nodiscard]] bool healthy() const;

private:
    struct Impl;                                      // incomplete in every client
    std::unique_ptr<Impl> impl_;
};
```

```cpp
// lidar_driver.cpp: vendor SDK headers and private state live here
#include "lidar_driver.h"
#include <algorithm>
#include <string>
#include <vector>

struct LidarDriver::Impl {
    std::string device;
    std::vector<float> last_scan = std::vector<float>(360, 5.0f);
    int error_count = 0;
};

LidarDriver::LidarDriver(std::string_view device)
    : impl_(std::make_unique<Impl>(Impl{std::string(device)})) {}
LidarDriver::~LidarDriver() = default;                // Impl is complete here
LidarDriver::LidarDriver(LidarDriver&&) noexcept = default;
LidarDriver& LidarDriver::operator=(LidarDriver&&) noexcept = default;

std::size_t LidarDriver::read_scan(std::span<float> out) {
    const std::size_t n = std::min(out.size(), impl_->last_scan.size());
    std::copy_n(impl_->last_scan.begin(), n, out.begin());
    return n;
}
bool LidarDriver::healthy() const { return impl_->error_count == 0; }
```

Why the out-of-line destructor? `std::unique_ptr<Impl>` deletes through `std::default_delete<Impl>`, and the program is ill-formed if `Impl` is incomplete at that point. If you let the compiler define `~LidarDriver` implicitly, it is defined inline in every client translation unit, where `Impl` is incomplete, and compilation fails. Declaring the destructor (and the move operations, which also need to destroy an `Impl`) in the header and defaulting them in the `.cpp` puts the definitions where `Impl` is complete.

What you get: clients never include the vendor SDK, editing `Impl` recompiles one file, and `sizeof(LidarDriver)` stays one `unique_ptr` regardless of private state, so adding a private member does not change the class layout that client binaries were compiled against. What you pay: one heap allocation per object, an extra indirection on every member access, and no inlining of member functions into callers (unless link-time optimization does it).

**Evolving an API without breaking callers.**

```cpp
#include <cstddef>
#include <span>

class LidarDriverV2 {
public:
    [[nodiscard]] std::size_t read_scan(std::span<float> ranges_out);

    [[deprecated("use read_scan(std::span<float>); removed in 3.0")]]
    int read_scan(float* out, int max_count) {
        return static_cast<int>(read_scan(std::span<float>(out, static_cast<std::size_t>(max_count))));
    }
};
```

The old overload keeps source compatibility for a release cycle, warns at every call site, and forwards to the new implementation so there is only one code path.

#### in practice

A radar vendor ships `libradar.so` to integrators who cannot recompile when it updates. That makes every public header a binary contract. Typical rules on such teams: public classes are pimpl or abstract interfaces with a factory, no inline functions that touch private data, no standard-library types across the boundary unless every party uses the same toolchain and standard library build (libstdc++'s `std::string` changed layout in GCC 5, which is why it ships a dual ABI), and a symbol-visibility policy that exports only the intended API.

Then there is **Hyrum's law**: with enough users, every observable behavior of your API will be depended on by somebody, whether or not you promised it. If `get_detections()` happened to return detections sorted by range for three years, someone's tracker now assumes it, and "unsorted" becomes a breaking change. Document what is guaranteed, and where order or timing is not guaranteed, consider making that visible early (some libraries deliberately randomize iteration order for this reason).

#### watch out for

**`const` does not propagate through pimpl.** Inside `healthy() const`, `impl_` is a `const std::unique_ptr<Impl>`, but `*impl_` is a non-const `Impl&`, so a const member function can modify private state without a compiler complaint. Add a pair of private accessors (`Impl& impl()` and `const Impl& impl() const`) and use them everywhere instead of `impl_` directly. Also, a moved-from `LidarDriver` has a null `impl_`; calling `read_scan` on it dereferences null (undefined behavior), so document that a moved-from driver may only be destroyed or assigned to, or check in every member.

**Not every class needs this.** Pimpl, strong types, and result types each add code. Use them on boundaries: public library headers, hardware interfaces, and functions where swapping two arguments is plausible. Internal helpers with one caller can stay plain.

#### the takeaway

Push contracts into types first, assertions second, and comments last. Make ownership, borrowing, and failure visible in the signature, pick one error channel per kind of failure, and remember that a shipped shared library promises an ABI, which is far stricter than an API.

#### optional challenge

List what is wrong with this public function from a deployment tool, and sketch a better signature: `bool deploy(char* host, int port, double timeout, bool force, bool dry_run);`

<details>
<summary>answer</summary>

`char*` says nothing about ownership or null termination, and non-const suggests the function may modify the string: take `std::string_view`. `double timeout` has no unit: use `std::chrono::milliseconds` (or `seconds`). Two adjacent `bool` flags are easy to swap and unreadable at the call site (`deploy(h, 22, 30, true, false)`): use enums such as `enum class Mode { apply, dry_run }` and `enum class Conflict { abort, overwrite }`, or a small options struct with designated initializers (C++20). The `bool` return hides why it failed and is easy to ignore: return a `[[nodiscard]]` result carrying an error enum and message. Port could be a `std::uint16_t` or a strong `Port` type. For example: `[[nodiscard]] DeployResult deploy(std::string_view host, std::uint16_t port, const DeployOptions& opts);` with `DeployOptions{.timeout = 30s, .mode = Mode::dry_run}` at the call site.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-48"></a>

### day 48: C++20 modules and coroutines: a practical first look

**reading time:** about 10 minutes · **standard:** C++20 · **builds on:** days 01, 03, 08

#### the idea

C++20 added two large language features that change how code is *organized* rather than what it computes. Modules replace textual `#include` with compiled interfaces. Coroutines let a function pause and resume, so a scan pattern or a network protocol can be written as straight-line code instead of a hand-rolled state machine. Both are real and usable, and both come with caveats about tooling and lifetimes that you need before you adopt them. This is a first look: enough to read, write, and judge them.

#### understanding the concept

**Modules.** Day 01 showed what `#include` really is: pasting text. Every translation unit reparses the same headers, macros defined in one header leak into everything included after it, and the one definition rule depends on every copy of a header being identical. A named module is compiled once into a binary module interface (a compiler-specific file), and importers read that instead of reparsing source. Only what you `export` is visible to importers; macros defined in a named module never leak out of it, and code that imports it is not affected by macros the importer defined earlier.

The vocabulary you need:

- **module interface unit**: starts with `export module name;` and declares what is exported.
- **module implementation unit**: starts with `module name;` and implicitly sees the interface, including its non-exported declarations.
- **global module fragment**: a `module;` line before the module declaration, where legacy `#include`s go so they do not become part of the module.
- **header units**: `import <vector>;` treats a header as an importable unit (it does export macros). Compiler support is uneven.

**Coroutines.** A function becomes a coroutine when its body uses `co_await`, `co_yield`, or `co_return`. Its state (the parameters, the locals that live across a suspension, and a *promise object*) lives in a **coroutine frame**, which is usually heap-allocated; the compiler may elide that allocation when it can prove the frame's lifetime is nested in the caller's, but nothing guarantees it. C++20 supplies only the machinery: the return type must provide a nested `promise_type` that tells the compiler what to do at start, at each `co_yield`, at the end, and on exceptions. The standard ships no ready-made generator or task type in C++20 (`std::generator` arrives in C++23).

`co_await x` asks an *awaiter* three questions: `await_ready()` (can we skip suspending?), `await_suspend(handle)` (we are suspended; who resumes us, and when?), and `await_resume()` (the result of the expression). `std::suspend_always` and `std::suspend_never` are the two trivial awaiters.

#### in code

**A small module.** File extensions and compiler flags vary by toolchain (`.cppm`, `.ixx`, `.mpp`; GCC before 14 needs the experimental `-fmodules-ts`).

```cpp
// geometry.cppm: module interface unit
export module robotics.geometry;

double square(double v) { return v * v; } // not exported: visible only inside the module

export namespace geo {
struct Vec2 { double x, y; };
double norm(Vec2 v);                      // exported declaration
}
```

```cpp
// geometry.cpp: module implementation unit
module;                                   // global module fragment: legacy includes
#include <cmath>
module robotics.geometry;                 // implicitly imports the interface

namespace geo {
double norm(Vec2 v) { return std::sqrt(square(v.x) + square(v.y)); }
}

// main.cpp: a consumer
#include <cstdio>
import robotics.geometry;

int main() { std::printf("%.1f\n", geo::norm({3.0, 4.0})); }   // prints: 5.0
// square(2.0) here would not compile: it is not exported
```

**A hand-written generator.** This is the whole contract between the compiler and a generator type.

```cpp
#include <coroutine>
#include <utility>

template <typename T>
class Generator {
public:
    struct promise_type {
        T current{};
        Generator get_return_object() {
            return Generator(std::coroutine_handle<promise_type>::from_promise(*this));
        }
        std::suspend_always initial_suspend() noexcept { return {}; }  // start lazily
        std::suspend_always final_suspend() noexcept { return {}; }    // keep frame until we destroy it
        std::suspend_always yield_value(T v) {                         // co_yield v
            current = std::move(v);
            return {};
        }
        void return_void() noexcept {}
        void unhandled_exception() { throw; }  // rethrows out of resume() into next()
    };

    explicit Generator(std::coroutine_handle<promise_type> h) : h_(h) {}
    Generator(Generator&& o) noexcept : h_(std::exchange(o.h_, {})) {}
    Generator& operator=(Generator&&) = delete;
    ~Generator() { if (h_) h_.destroy(); }         // RAII for the frame (day 08)

    bool next() {                                  // run to the next co_yield or the end
        h_.resume();
        return !h_.done();
    }
    const T& value() const { return h_.promise().current; }

private:
    std::coroutine_handle<promise_type> h_;
};
```

Walk through it once. Calling a coroutine allocates the frame, constructs the promise, calls `get_return_object()` (which is what the caller receives), then `co_await`s `initial_suspend()`. Ours suspends, so nothing runs until the first `next()`. Each `co_yield v` becomes `co_await promise.yield_value(v)`, which stores the value and suspends. Falling off the end calls `return_void()` and suspends at `final_suspend()`, so `done()` becomes true and the `Generator` destructor frees the frame. (This version requires `T` to be default-constructible; a production one would store a pointer or `std::optional`.)

Now the payoff. A radar steering beams in a serpentine raster:

```cpp
#include <iostream>

struct Beam { int elevation, azimuth; };

Generator<Beam> serpentine_scan(int rows, int cols) {    // parameters copied into the frame
    for (int el = 0; el < rows; ++el) {
        const bool forward = (el % 2 == 0);
        for (int i = 0; i < cols; ++i)
            co_yield Beam{el, forward ? i : cols - 1 - i};
    }
}

int main() {
    auto scan = serpentine_scan(2, 3);
    while (scan.next())
        std::cout << '(' << scan.value().elevation << ',' << scan.value().azimuth << ") ";
    // prints: (0,0) (0,1) (0,2) (1,2) (1,1) (1,0)
}
```

As an iterator class this needs `el`, `i`, and `forward` as members plus an `increment()` that reconstructs where the loops were. The coroutine keeps that state in its frame and lets the nested loops stay nested loops.

#### in practice

**Modules today.** Named modules need a build system that scans sources for `import` and `export module` before compiling, because a module must be built before its importers. CMake supports this from 3.28 with the Ninja and Visual Studio generators, on recent compilers (CMake documents MSVC 19.34+, Clang 16+, and GCC 14+). Binary module interfaces are compiler- and flag-specific, so a library still ships source interfaces, not BMIs. `import std;` is C++23, though some toolchains offer it as an extension in C++20 mode. A sensible adoption path: new leaf libraries as modules, internal code first, public headers kept until every consumer's toolchain supports modules. Do not expect it to fix a build dominated by template instantiation or link time; measure where your build time goes first.

**Coroutines today.** They shine for asynchronous I/O (a telemetry uploader written as `co_await socket.async_write(...)` in sequence instead of nested callbacks), protocol state machines, and lazy sequences. In practice you use a library's types: Asio's `awaitable`, folly's coro, or the generator in your toolchain's C++23 mode. Writing your own `task` type with correct continuation, cancellation, and thread handoff is much harder than the generator above.

#### watch out for

**Reference parameters dangle across suspension points.** The frame copies parameters, but copying a reference copies the reference.

```cpp
Generator<char> letters(const std::string& s) { for (char c : s) co_yield c; }

auto g = letters("radar");   // BUG: the temporary std::string dies at the end of this line
while (g.next()) { }         // undefined behavior: the frame refers to a destroyed string
```

The fix is to take the parameter by value (`std::string s`), so the frame owns a copy. The same applies to `std::string_view`, `std::span`, and lambda coroutines: a lambda's captures live in the lambda object, not the frame, so the lambda object must outlive the coroutine it started.

Also count the cost: each coroutine call may allocate a frame, and every resume is typically an indirect call through the handle. That is irrelevant for an uploader and potentially relevant in a 10 kHz control loop; custom `operator new` on the promise type gives you control of the allocation, and a profiler tells you whether it matters.

#### the takeaway

Modules fix textual inclusion and macro leakage, but adoption is gated by build-system and compiler support, so introduce them from the leaves inward. Coroutines turn state machines into straight-line code; pass parameters by value, let RAII own the frame, and prefer a library's coroutine types for asynchronous work.

#### optional challenge

What does `serpentine_scan(2, 3)` execute before the first call to `next()`, and what would change if `initial_suspend()` returned `std::suspend_never`?

<details>
<summary>answer</summary>

With `suspend_always`, the call allocates the frame, copies `rows` and `cols` into it, constructs the promise, obtains the `Generator`, and suspends at the initial suspend point: none of the loop body runs. With `suspend_never`, the body runs immediately until the first `co_yield`, so `current` already holds `(0,0)` when the caller receives the generator. Our `next()` resumes before reading, so the first `next()` would then skip to `(0,1)` and `(0,0)` would be lost. Eager start is a legitimate design (some task types use it), but the rest of the type has to be written for it; this is why the promise's suspend points and the wrapper's API must be designed together.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-49"></a>

### day 49: week 7 review: design with judgment

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 43 to 48

#### recap

| day | key idea |
|---|---|
| [43](#day-43) | SOLID, coupling, and cohesion are heuristics for the cost of change. Put seams where change actually happens, let the client own narrow interfaces, and treat the header graph as part of the design. |
| [44](#day-44) | Inject what crosses a boundary (time, hardware, I/O). Choose the seam by when the decision is made: virtual interface (run time), template plus concept (compile time), `std::function` (one operation), link time (platform functions). Wire everything near `main`. Prefer fakes to mocks. |
| [45](#day-45) | Patterns are vocabulary. Strategy is a callable, an interface, or a template parameter; factories return `std::unique_ptr`; registries are filled explicitly, not by static self-registration; observers use RAII tokens and are notified outside the lock. |
| [46](#day-46) | Four kinds of polymorphism: virtual (open set, reference semantics, binary boundaries), templates and concepts (compile time), `std::variant` (closed set), type erasure (open set with value semantics). Measure before choosing on speed. |
| [47](#day-47) | Contracts go into types first: strong types, enums instead of `bool`, views for borrowing, `[[nodiscard]]` results, one error channel per kind of failure. Pimpl buys a compile-time and ABI firewall for an allocation and an indirection. |
| [48](#day-48) | Modules replace textual inclusion; adopt from the leaves, gated by build-system support. Coroutines keep state in a frame; the return type's `promise_type` defines behavior, and reference parameters dangle across suspension points. |

#### review questions

1. Your codebase has `IConfigLoader` with exactly one implementation, `YamlConfigLoader`, used only by `App`, and a mock used in one test that checks `load()` was called once. Keep the interface, or remove it? What would change your answer?
2. In day 45's `Signal`, why does `subscribe` return a `[[nodiscard]]` token, and why does the token hold a `std::weak_ptr` to the signal's state rather than a raw pointer or a `shared_ptr`?
3. A radar processing chain passes about a dozen message types defined by a versioned interface document, and a hot loop dispatches on them. Separately, third-party detection plugins are loaded from shared libraries at startup. Which polymorphism mechanism fits each, and why?
4. A pimpl class compiles in its own `.cpp` file but every client fails with an error about applying `sizeof` to an incomplete type. What is missing, and why does the fix work?
5. Predict the problem:

   ```cpp
   Generator<std::string_view> fields(std::string_view line);   // splits on commas, lazily
   std::string read_line();

   auto f = fields(read_line());
   while (f.next()) use(f.value());
   ```

6. **From week 3.** A type-erased wrapper declares `template <typename T> Wrapper(T&& value);` with no constraint. What happens on `Wrapper copy = original;` when `original` is a non-const `Wrapper`, and which earlier lesson predicted this?
7. **From week 6.** Day 45's `emit` copies the subscriber list under the lock and then calls the slots without it. Name two distinct failures if it called the slots while holding a `std::mutex` instead.

#### mini exercise

This uploader cannot be unit tested: it constructs its own HTTP client and reads the wall clock directly. Refactor it so that the transport and the clock are injected, then write a fake transport and a test that checks two behaviors: the buffer is kept when sending fails, and cleared when it succeeds. Keep the production wiring simple.

```cpp
class TelemetryUploader {
public:
    void record(std::string line) { buffer_.push_back(std::move(line)); }
    void flush() {
        if (buffer_.empty()) return;
        HttpClient client("https://telemetry.internal");          // hard-wired transport
        const auto now = std::chrono::system_clock::now();         // hard-wired clock
        if (client.post("/batch", serialize(buffer_, now)) == 200) buffer_.clear();
    }
private:
    std::vector<std::string> buffer_;
};
```

#### answers

<details>
<summary>1. the single-implementation interface</summary>

Probably remove it. An interface with one implementation and a test that only verifies a call happened is indirection without a seam: config loading is input conversion, and the better design is a free function that turns text into a `Config` value, plus an `App` constructor that takes the `Config` (day 43's MotorController challenge). The test then builds a `Config` directly and needs no mock at all. Keep or add an interface when there is a real boundary to cross at run time: config fetched from a remote service in some deployments and a file in others, or tests that need to simulate failures of the source (permissions, timeouts) that a value cannot express.

</details>

<details>
<summary>2. tokens and weak_ptr</summary>

The token is the subscription: its destructor unsubscribes. Discarding the return value would subscribe and immediately unsubscribe, a silent bug, so `[[nodiscard]]` turns it into a warning. The token must work whether it dies before or after the signal. A raw pointer would dangle if the signal were destroyed first. A `shared_ptr` would keep the signal's state alive as long as any token exists, so ownership would be dictated by subscribers, the opposite of what an observer should do. `weak_ptr::lock()` answers "is the signal still there?" safely and does not extend its life.

</details>

<details>
<summary>3. radar messages and plugins</summary>

The internal messages are a closed, versioned set: `std::variant` with `std::visit`. Value semantics, no per-message heap allocation, and adding a type forces every visitor to be updated (with an `overloaded` visitor lacking a catch-all, a missing case fails to compile). Templates alone cannot hold mixed types in one stream. The plugins form an open set that crosses a shared-library boundary: a virtual interface plus an `extern "C"` factory, because templates cannot cross that boundary and a variant cannot be extended by someone else. If the hot loop ever shows the dispatch in a profile, that is the time to reconsider, not before.

</details>

<details>
<summary>4. pimpl and the incomplete type</summary>

The class does not declare its destructor (and probably its move operations), so the compiler defines them implicitly and inline, in every client translation unit. They destroy the `std::unique_ptr<Impl>`, and `std::default_delete<Impl>` requires `Impl` to be complete, which it is only in the class's own `.cpp`. Declaring `~Widget();` and the move operations in the header and defining them as `= default` in the `.cpp` (after `Impl` is defined) moves the code that destroys `Impl` to the one place where it is complete.

</details>

<details>
<summary>5. the lazy splitter</summary>

`read_line()` returns a temporary `std::string`. The `std::string_view` parameter is copied into the coroutine frame, but it points into that temporary, which is destroyed at the end of the full-expression `auto f = fields(read_line());`. Because the generator starts lazily, all of the splitting happens later, reading freed memory: undefined behavior. Every yielded `string_view` would also point into the dead string. Fix: take `std::string line` by value so the frame owns the text, and make sure consumers are done with each yielded view before the generator is destroyed, or yield `std::string` values.

</details>

<details>
<summary>6. from week 3: the greedy forwarding constructor</summary>

For a non-const lvalue, `T` deduces to `Wrapper&`, so the template's parameter is `Wrapper&`: an exact match, better than the copy constructor's `const Wrapper&`. The template wins and wraps a `Wrapper` inside the wrapper (or fails to compile in some confusing way). Day 19 called this the hijacked copy constructor; day 46's challenge showed why a by-value parameter avoids it. Fix by constraining: `requires (!std::same_as<std::remove_cvref_t<T>, Wrapper>)`.

</details>

<details>
<summary>7. from week 6: callbacks under a lock</summary>

First, reentrancy: a slot that subscribes, unsubscribes (for example a one-shot handler that resets its own token), or emits on the same signal locks the same non-recursive `std::mutex` again, which is undefined behavior and in practice usually a deadlock. Second, lock-order deadlocks across threads (day 41): the slot may take its own mutex while thread B, holding that mutex, tries to subscribe and waits for the signal's mutex. A third, softer problem is latency: a slow slot blocks every thread that wants to subscribe or emit.

</details>

<details>
<summary>mini exercise: one possible solution</summary>

The transport becomes a narrow interface owned by the uploader's module (day 43's DIP), and the clock a `std::function` (one operation, day 44). The production `main` would pass an adapter over the real HTTP client and `std::chrono::system_clock::now`.

```cpp
#include <cassert>
#include <chrono>
#include <functional>
#include <string>
#include <string_view>
#include <vector>

class BatchSink {
public:
    virtual ~BatchSink() = default;
    virtual bool send(std::string_view payload) = 0;   // true on success
};

using WallClock = std::function<std::chrono::system_clock::time_point()>;

class TelemetryUploader {
public:
    TelemetryUploader(BatchSink& sink, WallClock now) : sink_(sink), now_(std::move(now)) {}
    void record(std::string line) { buffer_.push_back(std::move(line)); }
    void flush() {
        if (buffer_.empty()) return;
        if (sink_.send(serialize(now_()))) buffer_.clear();
    }
    std::size_t pending() const { return buffer_.size(); }
private:
    std::string serialize(std::chrono::system_clock::time_point t) const {
        std::string out = std::to_string(t.time_since_epoch().count()) + '\n';
        for (const auto& l : buffer_) out += l + '\n';
        return out;
    }
    BatchSink& sink_;
    WallClock now_;
    std::vector<std::string> buffer_;
};

struct FakeSink final : BatchSink {
    bool succeed = false;
    std::vector<std::string> sent;
    bool send(std::string_view payload) override {
        sent.emplace_back(payload);
        return succeed;
    }
};

int main() {
    FakeSink sink;
    TelemetryUploader up(sink, [] { return std::chrono::system_clock::time_point{}; });
    up.record("battery=24.1");
    up.flush();                                        // sink fails
    assert(up.pending() == 1 && sink.sent.size() == 1);
    sink.succeed = true;
    up.flush();                                        // sink succeeds
    assert(up.pending() == 0 && sink.sent.back() == "0\nbattery=24.1\n");
}
```

Notice what the fake lets you test that the original could not: the failure path, and the exact payload, both without a network. Note also the borrowed `BatchSink&`: the sink must outlive the uploader, which is natural when both are created in `main`.

</details>

#### connections

This week leaned on almost everything before it. Ownership in signatures and `std::unique_ptr` with incomplete types came from week 2 (days 11 to 13), which is also where virtual dispatch and Liskov substitution were introduced. `std::function`, forwarding references, and exception-safe error channels came from week 3. `std::variant` as a closed-set alternative to inheritance came from week 4 (day 25), and concepts as the constraint language for compile-time injection and type erasure came from week 5 (day 29), along with `std::span` and `std::string_view` as borrowing parameters. Week 6's rule about not calling unknown code under a lock reappeared in the observer.

Week 8 cashes these designs in. Day 50 gives you the tools to settle "is the virtual call too slow?" with data instead of opinion. Day 53 builds tests on day 44's fakes and seams, day 54 uses seams to get legacy code under test before changing it, and day 55 assembles an injected clock, a variant message type, concepts, and RAII shutdown into one small pipeline.

[back to table of contents](#table-of-contents)

---

<a id="week-8"></a>

## week 8: production engineering and integration

Making code fast, observable, testable, and maintainable, then putting it all together.

<a id="day-50"></a>

### day 50: measure first: benchmarking and profiling

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 15, 16

#### the idea

A colleague replaces a `std::map` with a sorted `std::vector` and posts a microbenchmark: 40 times faster. You rebuild it with `-O2` and the measured loop takes almost no time at all, because the compiler deleted it. Both numbers are wrong, and only one of them looks wrong. Performance work starts with measurements you can trust, and most bad optimization decisions trace back to a number nobody questioned.

#### understanding the concept

Intuition fails because the machine we reason about (one instruction after another, memory with uniform cost) is not the machine we run on. Out-of-order execution, branch prediction, caches, prefetchers, and dynamic clock frequencies mean that instruction counts and complexity classes predict only part of the cost. Complexity tells you how cost grows; constant factors, memory behavior, and the input distribution decide what happens at your sizes (day 15 made this point for containers).

Two kinds of tools answer two different questions:

- **benchmarks** answer "how long does this take, under these conditions?" A microbenchmark isolates one function. A macrobenchmark runs a realistic workload: replaying a recorded radar session, or a full planning cycle on logged sensor data.
- **profilers** answer "where does the time go?" Sampling profilers (`perf` on Linux, Intel VTune, Apple Instruments) interrupt the program at intervals and record the call stack: low overhead, whole-program coverage, statistical results. Instrumentation profilers (Tracy, or your own scope timers) record explicit begin and end events, giving exact per-frame, per-thread timelines at the cost of touching the code. A flame graph draws sampled stacks so that width is proportional to time: wide plateaus are where to look.

The workflow that works: profile a realistic run to find the hot spot, write a benchmark around that hot spot, change the code, benchmark again, then confirm with the profiler that the whole program got faster, not just the microbenchmark.

For timing inside code, use `std::chrono::steady_clock`. It is monotonic, so an NTP adjustment cannot make an interval negative or inflate it. `system_clock` is calendar time and may jump. `high_resolution_clock` is allowed to be an alias of either (libstdc++ makes it `system_clock`, MSVC makes it `steady_clock`), so don't reach for it because of its name.

**Amdahl's law** bounds what any optimization can buy. If a fraction `p` of the runtime is sped up by a factor `s`, the overall speedup is `1 / ((1 - p) + p / s)`. Make a function that takes 10 percent of the frame infinitely fast and you save at most 10 percent. This is why profiling comes first: it tells you `p` before you spend effort on `s`.

#### in code

The benchmark from the idea, reduced to its bugs:

```cpp
#include <chrono>
#include <cstdio>
#include <numeric>
#include <vector>

int main() {
    std::vector<int> v(1'000'000, 1);
    auto t0 = std::chrono::system_clock::now();          // BUG: wall clock, may jump
    for (int rep = 0; rep < 100; ++rep) {
        int sum = std::accumulate(v.begin(), v.end(), 0); // BUG: result never used
        (void)sum;
    }
    auto t1 = std::chrono::system_clock::now();
    auto us = std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0);
    std::printf("100 sums: %lld us\n", static_cast<long long>(us.count()));
}
```

The sum has no observable effect, so under the as-if rule the optimizer may remove the whole loop (dead-code elimination). GCC 12 at `-O2` does exactly that: the generated assembly contains the two `now()` calls and nothing between them. Even if the result were used, the input is a compile-time constant pattern the optimizer might fold. And it is one sample, taken cold, with no idea of the spread.

A small harness that fixes each problem:

```cpp
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <numeric>
#include <random>
#include <vector>

struct Stats { double median_us, min_us, max_us; };

template <typename F>
Stats measure(F&& work, int warmup = 3, int reps = 31) {
    using clock = std::chrono::steady_clock;          // monotonic: never jumps
    for (int i = 0; i < warmup; ++i) work();          // caches, page faults, clock ramp-up
    std::vector<double> samples;
    samples.reserve(reps);
    for (int i = 0; i < reps; ++i) {
        const auto t0 = clock::now();
        work();
        const auto t1 = clock::now();
        samples.push_back(std::chrono::duration<double, std::micro>(t1 - t0).count());
    }
    std::sort(samples.begin(), samples.end());
    return {samples[samples.size() / 2], samples.front(), samples.back()};
}

volatile long long g_sink;  // a volatile write is observable behavior: it must happen

int main(int argc, char**) {
    std::mt19937 rng(static_cast<unsigned>(argc));     // input unknown at compile time
    std::vector<int> v(1'000'000);
    for (auto& x : v) x = static_cast<int>(rng() % 100);

    const Stats s = measure([&] { g_sink = std::accumulate(v.begin(), v.end(), 0LL); });
    std::printf("median %.1f us (min %.1f, max %.1f)\n", s.median_us, s.min_us, s.max_us);
}
```

Why the median and the extremes rather than the mean: timing noise is one-sided. Interrupts, thread migrations, and page faults only ever add time, so the distribution has a long right tail that drags the mean around. The median is robust; the minimum approximates "nothing interfered"; the maximum tells you whether the tail matters. For a control loop with a deadline, the tail (p99, worst case) is the requirement, so report it.

A hand-rolled harness is fine for a quick check, but a library handles iteration counts, repetitions, and statistics for you. With Google Benchmark (not part of the standard; shown for its idioms):

```cpp
#include <benchmark/benchmark.h>
#include <map>

static void BM_MapFind(benchmark::State& state) {
    std::map<int, int> m;
    for (int i = 0; i < state.range(0); ++i) m[i * 2] = i;
    int key = 0;
    for (auto _ : state) {                         // the library chooses the iteration count
        auto it = m.find(key);
        benchmark::DoNotOptimize(it);              // forces the result to be "used"
        key = (key + 7) % static_cast<int>(2 * state.range(0));
    }
}
BENCHMARK(BM_MapFind)->Range(64, 1 << 16);         // several sizes, not one
BENCHMARK_MAIN();
```

Run it with `--benchmark_repetitions=10 --benchmark_report_aggregates_only=true` to get mean, median, standard deviation, and coefficient of variation per size. Note that `DoNotOptimize` keeps a value alive but does not stop the compiler from hoisting loop-invariant work out of the timed loop; the varying `key` above is what prevents that, and `benchmark::ClobberMemory()` exists for the memory side of the same problem.

#### in practice

A radar team wants to catch performance regressions in CI. The naive version runs benchmarks on shared CI runners and fails the build if anything is 5 percent slower. Within a week it is ignored, because run-to-run noise on a shared virtual machine is often larger than 5 percent.

What tends to work:

- Run timing benchmarks on a dedicated, quiet machine with a fixed CPU frequency (the `performance` governor, turbo disabled) and pinned cores, or accept wider thresholds.
- Compare against a stored baseline with repetitions on both sides, and flag only differences larger than the measured spread. Google Benchmark ships a `compare.py` tool for this.
- On noisy runners, track a proxy with less noise, such as instruction counts from `perf stat -e instructions` or Cachegrind. Instructions are not time (a cache miss costs far more than an add), so treat a proxy alarm as a prompt to measure, not a verdict.

For profiling, build the release configuration with symbols, not a debug build:

```sh
g++ -O2 -g -fno-omit-frame-pointer ...        # optimized, but with usable stacks
perf record -g ./radar_replay session.bin     # sample with call graphs
perf report                                   # or render a flame graph from 'perf script'
```

A debug build measures a different program: no inlining, every abstraction paid in full. Its hot spots are frequently not the release build's hot spots.

#### watch out for

A microbenchmark is a best-case laboratory. The data is hot in cache, branches are perfectly predicted after a few iterations, the allocator has a warm free list, and no other thread competes for memory bandwidth. Production sees cold caches, varied inputs, and contention. A function that wins a microbenchmark by 30 percent can make no measurable difference in the full pipeline, or even lose if its larger code or tables evict something else. Always close the loop with a macro measurement.

Remember the other side of the ledger, too: every optimization has a maintenance cost (less obvious code, more invariants, more tests). Optimize where the profile points, stop when the requirement is met, and leave a comment with the measurement that justified the change.

#### the takeaway

Profile to find where time goes, benchmark to compare alternatives, and distrust any number until you know what the compiler did to the code and how much the result varies.

#### optional challenge

A teammate benchmarks `std::sort` with the harness above: `measure([&] { std::sort(v.begin(), v.end()); })`. The median looks impressively low. What is it actually measuring, and how would you fix it?

<details>
<summary>answer</summary>

After the first warm-up call the vector is sorted, so every timed repetition sorts already-sorted data, which is a very different (and for typical introsort implementations, much cheaper) workload. Copy the original unsorted input into a working vector inside each repetition. The copy then becomes part of the measurement, so either measure the copy alone and report both, or sort many independent copies prepared in advance and divide. Google Benchmark has `state.PauseTiming()`, but pausing has its own overhead and is unreliable for very short regions. The general lesson: a benchmark that mutates its input must restore it, or it measures a different input after the first iteration.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-51"></a>

### day 51: cache locality and data-oriented design

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 15, 40, 50

#### the idea

Two loops do the same arithmetic over the same number of elements, both O(n), and one runs several times slower than the other. Nothing in the source explains it, because the difference is not in the instructions: it is in where the bytes live. Most code that is "slow for no reason" is waiting on memory.

#### understanding the concept

The CPU does not read bytes from RAM; it reads cache lines (64 bytes on most x86-64 and many ARM cores, 128 on some designs) through a hierarchy of caches. The numbers below are rough orders of magnitude only. They vary considerably across CPU generations and vendors, so treat them as a sense of scale, not as constants:

| level | typical size | rough latency |
|---|---|---|
| registers | a few hundred bytes | effectively zero |
| L1 data cache | 32 to 128 KiB per core | about 1 ns (a handful of cycles) |
| L2 | 256 KiB to a few MiB | a few ns |
| L3 (shared) | several to tens of MiB | around 10 to 20 ns |
| DRAM | GiB | around 50 to 100+ ns |

Three mechanisms explain most of what you will observe:

- **spatial locality**: once a line is loaded, its other 63 bytes are nearly free. Code that uses every byte it fetches gets the most out of each miss.
- **prefetching**: hardware prefetchers detect sequential and constant-stride access and fetch lines before you ask. They cannot predict where a pointer points.
- **memory-level parallelism**: a modern core can have many misses in flight at once, if it knows the addresses. In a linked list, the next address is inside the node you are still waiting for, so misses serialize: each one pays the full latency.

Data-oriented design takes these mechanisms as the starting point. Instead of asking "what is a detection?" you ask "which bytes does this loop read, how many times, in what order?" and lay the data out to match.

#### in code

Three traversals, identical arithmetic:

```cpp
#include <list>
#include <memory>
#include <vector>

struct Point { float x, y, z; };

float sum_x(const std::vector<Point>& pts) {                   // contiguous, sequential
    float s = 0; for (const Point& p : pts) s += p.x; return s;
}
float sum_x(const std::vector<std::unique_ptr<Point>>& pts) {  // one indirection each
    float s = 0; for (const auto& p : pts) s += p->x; return s;
}
float sum_x(const std::list<Point>& pts) {                     // dependent pointer chase
    float s = 0; for (const Point& p : pts) s += p.x; return s;
}
```

The vector is the friendly case: sequential lines, prefetcher engaged. The vector of `unique_ptr` stores pointers contiguously but the pointees go wherever the allocator put them. In a fresh benchmark process they are often allocated back to back, so it looks fine; after hours of allocation churn they scatter, and the benchmark flattered the design (day 50's warning about laboratory conditions). The list adds a dependency chain on top of the scatter.

Now a radar detection, laid out as an array of structs (AoS):

```cpp
#include <cstddef>
#include <cstdint>
#include <vector>

struct Detection {                                    // AoS: 64 bytes on common 64-bit ABIs
    float range_m, azimuth_rad, doppler_mps, snr_db;  // 16
    std::uint64_t timestamp_ns;                       //  8
    std::uint32_t track_id, flags;                    //  8
    char source[32];                                  // 32: sensor name, rarely read
};

std::size_t count_strong(const std::vector<Detection>& ds, float min_snr) {
    std::size_t n = 0;
    for (const Detection& d : ds) n += d.snr_db >= min_snr;  // 4 useful bytes per 64 fetched
    return n;
}
```

Every iteration pulls in a whole line to use one `float`. The struct of arrays (SoA) version stores each field contiguously:

```cpp
#include <array>

struct Detections {                                   // SoA: one array per field
    std::vector<float> range_m, azimuth_rad, doppler_mps, snr_db;
    std::vector<std::uint64_t> timestamp_ns;
    std::vector<std::uint32_t> track_id, flags;
    std::vector<std::array<char, 32>> source;
};

std::size_t count_strong(const Detections& ds, float min_snr) {
    std::size_t n = 0;
    for (float snr : ds.snr_db) n += snr >= min_snr;  // 16 useful floats per line
    return n;
}
```

The gating loop now moves one sixteenth of the bytes, and its body is a uniform operation over contiguous floats, which is exactly the shape compilers auto-vectorize most readily. Whether that turns into a large speedup depends on whether the AoS loop was memory-bound to begin with: for a few hundred detections that fit in L1, the difference may be noise. For hundreds of thousands per frame, it usually is not.

A middle ground is **hot/cold splitting**: keep the fields every loop touches in one compact struct (here `range`, `azimuth`, `doppler`, `snr`, `track_id`, `flags`: 24 bytes) and move the rarely read ones (timestamp, sensor name) into a parallel array indexed the same way. You keep most of the AoS ergonomics and stop paying for bytes you never read.

#### in practice

A robot localizer runs a particle filter with tens of thousands of particles. Each cycle has three phases: predict (update every pose from odometry), weight (score every pose against the latest scan), and resample (cumulative sum over weights, then copy chosen poses). Originally each `Particle` was a class with pose, weight, a history buffer for debugging, and virtual methods, held in a `std::vector<std::unique_ptr<Particle>>`.

The data-oriented rewrite stored `x`, `y`, `theta`, and `weight` as four float arrays inside a `ParticleSet` class, moved the debug history into a separate structure that is only filled when diagnostics are enabled, and split the weighting phase across threads with per-thread partial sums. Those partial sums sat in an array of adjacent `double`s, which put several threads' accumulators on one cache line: false sharing (day 40). Padding each accumulator to its own line fixed it:

```cpp
struct alignas(64) PaddedSum { double value = 0; };  // one cache line per thread
std::vector<PaddedSum> partial(num_threads);          // C++17 vector honours over-alignment
```

(`std::hardware_destructive_interference_size` from `<new>` is the portable spelling of the 64, where your standard library provides it.)

Each step was justified with numbers, not intuition: the day 50 harness on a recorded dataset for time per cycle, and hardware counters for the mechanism, for example `perf stat -e cache-references,cache-misses,L1-dcache-load-misses ./localizer_replay run.bag`. Available event names vary by CPU; `perf list` shows yours. A drop in misses with no change in cycle time means memory was not the bottleneck, and the change probably is not worth its cost.

Note the design move: the SoA arrays are private to `ParticleSet`, which guarantees they always have equal length and exposes whole-set operations (`predict`, `normalize_weights`). Encapsulation moved from the element to the collection; it did not disappear.

#### watch out for

SoA is a tradeoff, not an upgrade. Code that accesses all fields of one element at a time (a tracker associating one detection, a lookup by index) touches one line in AoS and several lines in SoA. Every new field touches several places. Sorting means permuting every array, or sorting an index array instead. Element identity becomes "an index", which invalidates as easily as an iterator (day 15). And the readability cost is real: `particles.x[i]` reads worse than `particle.x`.

Choose layout from the dominant access pattern of the hot loops, keep it behind an interface so the choice can change, and verify with counters that memory was the bottleneck before paying the complexity.

#### the takeaway

Performance is often decided by which bytes travel from memory and in what order; lay out data for the loops that run hottest, and keep that layout encapsulated so it stays a decision rather than an accident.

#### optional challenge

On a typical 64-bit ABI, `struct Particle { bool active; double x, y, z; bool dirty; };` is 40 bytes. Why, what is the smallest you can make it by reordering, and what would you do instead if the hot loop only checks `active` and skips most particles?

<details>
<summary>answer</summary>

Each `double` needs 8-byte alignment, so `active` is followed by 7 bytes of padding, and `dirty` is followed by 7 more so that the size is a multiple of the alignment (arrays must keep every element aligned): 1 + 7 + 24 + 1 + 7 = 40. Putting the doubles first and the two `bool`s together gives 24 + 2 = 26, rounded up to 32 bytes, so exactly two particles per 64-byte line instead of 1.6. Padding is implementation-defined in general, but these numbers hold on the common x86-64 and AArch64 ABIs.

If the hot loop only needs `active` and most particles are inactive, layout tweaks are the wrong tool: the loop still visits every particle. Keep the active ones compacted at the front of the arrays (swap-remove on deactivation), or keep a separate dense list of active indices, so the loop never touches inactive particles at all. Doing less work beats doing the same work with fewer misses.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-52"></a>

### day 52: the cost of allocation

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 12, 15, 17, 50

#### the idea

A 1 kHz joint controller meets its deadline in every lab test, then misses one every few minutes in the field. The profiler shows nothing hot. The culprit is a `std::string` built for a log line and a `std::vector` that grows inside the loop: allocation calls whose cost is usually small but occasionally very large. In real-time code the average does not matter; the worst case does, and the general-purpose heap has no useful worst-case bound.

#### understanding the concept

`operator new` (and `malloc` beneath it) is a general-purpose allocator. On each call it may:

- find a free block of the right size class and update its bookkeeping (the cheap, common path, often served from a per-thread cache in modern allocators such as glibc's tcache, jemalloc, tcmalloc, or mimalloc);
- take a lock or touch shared structures when the thread cache is empty or memory was freed by another thread;
- ask the operating system for more memory (`brk`, `mmap`, `VirtualAlloc`), which is a system call, and the fresh pages are then page-faulted in on first touch.

So the cost distribution has a cheap mode and a long tail you cannot bound. Allocation also scatters data (each node or object lands wherever a block was free, which is day 51's locality problem), and long-running processes fragment the heap.

The expensive part is that allocations hide. Each of these allocates, or may:

| code | allocation |
|---|---|
| `std::string` longer than the small-string buffer | one per string (buffer size is implementation-defined: 15 chars in libstdc++ and MSVC, 22 in libc++, on 64-bit targets) |
| string concatenation `a + b + c` | possibly one per intermediate |
| `std::function` holding a large capture | one, beyond a small internal buffer (size implementation-specific) |
| `std::make_shared<T>()` | one (object and control block together); `shared_ptr<T>(new T)` makes two (day 12) |
| `std::map`, `std::set`, `std::list`, `std::unordered_map` | one per node |
| `push_back` without `reserve` | about log2(n) reallocations with geometric growth |
| `throw` | the runtime allocates the exception object |

The tools, roughly in order of how often you reach for them: `reserve` and reuse; avoiding node containers in hot paths; `std::pmr` resources for scoped, fast allocation; object pools for fixed-size objects; and the strongest pattern of all for real-time code, an allocation-free steady state: allocate everything at startup, then never again.

#### in code

First, measure. Replacing the global allocation functions is a standard, supported mechanism. Put the replacement in its own file and link it only into test binaries:

```cpp
// alloc_counter.cpp: link into test binaries only
#include <atomic>
#include <cstddef>
#include <cstdlib>
#include <new>

std::atomic<std::size_t> g_allocs{0};

void* operator new(std::size_t n) {                  // replaces the global allocation function
    g_allocs.fetch_add(1, std::memory_order_relaxed);
    if (void* p = std::malloc(n ? n : 1)) return p;
    throw std::bad_alloc{};
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

// elsewhere:
template <typename F>
std::size_t count_allocs(F&& f) {
    const std::size_t before = g_allocs.load();
    f();
    return g_allocs.load() - before;
}
```

The array forms forward to these by default. With GCC 12 and libstdc++ on x86-64, `count_allocs` reported: a 6-character string 0, a 22-character string 1, a `std::function` capturing a `std::array<double, 8>` 1, `make_shared<int>` 1, 100 `std::map` inserts 100, and 1,000 `push_back` calls without `reserve` 11. These are implementation details, which is exactly why you count rather than guess. A complete counter also replaces the C++17 `std::align_val_t` overloads; libstdc++'s default `pmr` resource, for one, allocates through them.

Second, `std::pmr` (C++17). A `memory_resource` is a runtime-polymorphic allocator, and the `std::pmr::` containers hold a pointer to one. `monotonic_buffer_resource` is a bump allocator: allocation advances a pointer, deallocation is a no-op, and everything is released at once when the resource dies.

```cpp
#include <array>
#include <cstddef>
#include <memory_resource>
#include <vector>

struct Detection { float range_m, azimuth_rad, snr_db; };

std::size_t process_frame(const std::vector<Detection>& raw) {
    alignas(std::max_align_t) std::array<std::byte, 16 * 1024> buffer;   // scratch on the stack
    std::pmr::monotonic_buffer_resource arena(buffer.data(), buffer.size(),
                                              std::pmr::null_memory_resource());
    std::pmr::vector<Detection> gated(&arena);
    gated.reserve(raw.size());                   // a pointer bump, no heap
    for (const Detection& d : raw)
        if (d.snr_db > 10.0f) gated.push_back(d);
    return gated.size();
}                                                // everything released at once
```

The `null_memory_resource()` upstream is a deliberate choice: if a frame ever needs more than 16 KiB, allocation throws `std::bad_alloc` instead of silently falling back to the heap. In a test, that is a loud failure you want; in production you might prefer the default upstream plus a metric. Note `reserve`: with a monotonic resource, a growing vector leaves every outgrown buffer behind as dead space until the arena is released.

Third, the real-time pattern: preallocate, then reuse.

```cpp
class LocalPlanner {
public:
    explicit LocalPlanner(std::size_t max_obstacles) {
        nearby_.reserve(max_obstacles);           // pay once, at startup
    }
    std::size_t cycle(const std::vector<Obstacle>& scan) {
        nearby_.clear();                          // destroys elements, keeps capacity
        for (const Obstacle& o : scan)
            if (o.x * o.x + o.y * o.y < 25.0f) nearby_.push_back(o);
        return nearby_.size();
    }
private:
    std::vector<Obstacle> nearby_;                // reused every cycle
};

void test_planner_steady_state_is_allocation_free() {
    std::vector<Obstacle> scan(256, Obstacle{1.0f, 1.0f, 0.5f});
    LocalPlanner planner(512);
    planner.cycle(scan);                          // warm-up
    const std::size_t before = g_allocs.load();
    for (int i = 0; i < 1000; ++i) planner.cycle(scan);
    assert(g_allocs.load() == before);            // the steady state never touches the heap
}
```

The test turns a performance property into a regression test: if someone adds a `std::string` to `cycle` next year, CI fails instead of the robot.

#### in practice

A radar tracker processed each frame with a `std::map<TrackId, Track>` and built a fresh `std::vector` of candidate associations per track. A heap profiler (heaptrack on Linux, or Valgrind's massif) showed hundreds of thousands of allocations per second, and the tail of the frame time tracked them.

The fix came in layers, each verified with the counter and day 50's harness: tracks moved into a `std::vector` sorted by id (day 15), candidate lists became members cleared each frame, and per-frame temporaries moved to a `monotonic_buffer_resource` reset at frame boundaries. The steady state dropped to zero allocations, and the remaining frame-time variation came from the work itself.

Object pools fill the remaining gap: when objects of one type are created and destroyed at runtime (tracks born and dying), a fixed-capacity pool with a free list gives O(1) allocation with no system calls. `std::pmr::unsynchronized_pool_resource` is a general-purpose version for single-threaded use; `synchronized_pool_resource` adds locking.

#### watch out for

`pmr` propagation surprises people. A pmr container does not propagate its resource on copy: `std::pmr::vector<int> copy = a;` gets the default resource (normally the heap), not `a`'s arena. Moving keeps the resource, but move-assigning between containers with different resources copies element by element. Uses-allocator construction passes the resource down only to elements that accept one: `pmr::vector<pmr::string>` puts the strings in the arena, `pmr::vector<std::string>` does not. And the resource must outlive every container using it; a container whose arena has been destroyed holds dangling memory, and touching it is undefined behavior.

Two measurement traps. The standard allows a new-expression to omit or merge its call to a replaceable allocation function, so an optimized build may count fewer allocations than the source suggests. And on Windows, a replacement in the executable does not intercept allocations made inside a DLL that has its own `operator new`: with MinGW's shared libstdc++, string allocations inside the library went uncounted until the program was linked with `-static`. Exceptions are separate again: the common Itanium ABI runtimes allocate the exception object with `malloc`, so an `operator new` counter never sees it.

#### the takeaway

Count allocations instead of guessing, move them out of hot loops and into startup, and when a steady state must be allocation-free, write a test that says so.

#### optional challenge

`std::pmr::vector<std::pmr::string> names(&arena); names.push_back("front_left_radar_long_name");` How many allocations come from the arena, and what changes if the element type is `std::string`?

<details>
<summary>answer</summary>

With `pmr::string` elements, uses-allocator construction gives the new string the vector's resource, so both the vector's buffer and the string's heap buffer (the name is longer than the small-string buffer) come from the arena. One subtlety: `push_back` first constructs a temporary `pmr::string` from the literal using the default resource, then moves it into the vector; because the resources differ, the move copies into arena memory, so the temporary's allocation hits the heap. `emplace_back("...")` constructs in place with the arena and avoids that. With `std::string` elements, only the vector's buffer is in the arena; every long string allocates from the global heap, defeating the point of the arena.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-53"></a>

### day 53: testing and observability

**reading time:** about 10 minutes · **standard:** C++20 · **builds on:** days 06, 08, 34, 41, 44

#### the idea

Tests tell you the code did what you expected on inputs you thought of. Observability tells you what it did in production on inputs you did not think of. A team with only the first ships bugs it cannot diagnose; a team with only the second diagnoses the same bug every week. Both are design concerns, and both are cheaper when the code was built for them.

#### understanding the concept

**The test pyramid, in C++ terms.** At the base, many fast unit tests that run in milliseconds and need no hardware: pure functions, classes with injected dependencies (day 44). In the middle, integration tests: several real components wired together, perhaps over loopback sockets or by replaying recorded sensor data. At the top, few and expensive: hardware-in-the-loop (the real controller board driving a simulated plant) and field tests. Push each check as low as it can go; a bug found by a unit test costs seconds, one found on the robot costs a day.

**Test behavior, not implementation.** A test that asserts "the planner called `compute_cost` 14 times" breaks on every refactor and catches nothing. A test that asserts "the planned path never enters the keep-out zone" survives refactors and catches real bugs. Mocks that verify call sequences are right only when the call is the behavior (the actuator command was sent exactly once).

**Beyond examples.** Property-based tests generate many inputs and check an invariant: `parse(serialize(msg)) == msg`, or "the filter output stays within sensor bounds". Fuzzing (libFuzzer, AFL++) mutates inputs guided by code coverage, and is the most effective tool we have for parsers of untrusted bytes. Sanitizers (day 06) turn silent undefined behavior into loud test failures, but they need separate builds: AddressSanitizer and ThreadSanitizer cannot be combined in one binary, while ASan and UBSan usually can.

**Observability** has three complementary signals:

- **logs**: discrete events with context. Make them structured (`key=value` or JSON) so machines can query them.
- **metrics**: cheap numeric aggregates (counters, gauges, histograms), exported periodically. They answer "how often" and "how slow" without storing every event.
- **traces**: timed spans with parent/child relationships, showing where one request or frame spent its time across stages and threads.

#### in code

A deterministic unit test with the fake clock from day 44, using `std::source_location` (C++20) for failure locations instead of a macro:

```cpp
#include <chrono>
#include <cstdio>
#include <source_location>
#include <string_view>

using namespace std::chrono_literals;
using TimePoint = std::chrono::steady_clock::time_point;

struct Clock {                                        // the seam from day 44
    virtual ~Clock() = default;
    virtual TimePoint now() const = 0;
};

class Watchdog {                                      // trips if heartbeats stop
public:
    Watchdog(const Clock& clock, std::chrono::milliseconds timeout)
        : clock_(clock), timeout_(timeout), last_(clock.now()) {}
    void heartbeat() { last_ = clock_.now(); }
    bool expired() const { return clock_.now() - last_ > timeout_; }
private:
    const Clock& clock_;
    std::chrono::milliseconds timeout_;
    TimePoint last_;
};

struct FakeClock final : Clock {                      // a fake: real behavior, controlled time
    TimePoint t{};
    TimePoint now() const override { return t; }
};

int g_failures = 0;
void check(bool ok, std::string_view what,
           std::source_location loc = std::source_location::current()) {
    if (ok) return;
    ++g_failures;
    std::printf("%s:%u: FAILED: %.*s\n", loc.file_name(), static_cast<unsigned>(loc.line()),
                static_cast<int>(what.size()), what.data());
}

void test_watchdog_trips_only_after_timeout() {
    FakeClock clock;
    Watchdog dog(clock, 100ms);
    clock.t += 100ms;
    check(!dog.expired(), "exactly at the timeout it is still alive");
    clock.t += 1ms;
    check(dog.expired(), "trips once the timeout has passed");
    dog.heartbeat();
    check(!dog.expired(), "a heartbeat re-arms it");
}
```

No sleeps, no flakiness, and the boundary (exactly 100 ms) is pinned down, which is where the bugs live. The default argument `std::source_location::current()` is evaluated at the call site, so the failure reports the line of the `check`, not of its definition. In a real project you would use GoogleTest (`EXPECT_TRUE`) or Catch2 (`CHECK`); the test's shape is the same.

Structured logging, where the interesting part is what a disabled log costs:

```cpp
#include <atomic>
#include <initializer_list>

enum class Level { debug, info, warn, error };
inline std::atomic<Level> g_level{Level::info};       // adjustable at runtime

struct Field { std::string_view key; double value; };

void log_event(Level lvl, std::string_view event, std::initializer_list<Field> fields,
               std::source_location loc = std::source_location::current()) {
    if (lvl < g_level.load(std::memory_order_relaxed)) return;
    std::fprintf(stderr, "level=%d event=%.*s", static_cast<int>(lvl),
                 static_cast<int>(event.size()), event.data());
    for (const Field& f : fields)
        std::fprintf(stderr, " %.*s=%g", static_cast<int>(f.key.size()), f.key.data(), f.value);
    std::fprintf(stderr, " src=%s:%u\n", loc.file_name(), static_cast<unsigned>(loc.line()));
}

// The arguments of a disabled log_event() call are still evaluated. The macro checks first.
#define LOG_DEBUG(event, ...)                                                   \
    do {                                                                        \
        if (g_level.load(std::memory_order_relaxed) <= Level::debug)            \
            log_event(Level::debug, event, __VA_ARGS__);                        \
    } while (0)

// LOG_DEBUG("cycle", {{"residual", compute_residual()}});
// prints nothing at level info, and compute_residual() is never called
```

This is one of the few places where a macro still earns its keep: a function cannot avoid evaluating its arguments. If debug logs must cost nothing at all in release builds, add a compile-time floor (`if constexpr (kMinCompiledLevel <= Level::debug)`) so the code is not even generated; the tradeoff is that you cannot turn those logs on in the field without a rebuild. In a C++20 codebase with a newer toolchain, you would format with `std::format` (day 34) rather than `printf`.

Metrics and spans, built so they are safe to use inside a control loop:

```cpp
#include <algorithm>
#include <array>
#include <bit>

class LatencyHistogram {          // log2 buckets in microseconds: [0,1), [1,2), [2,4), ...
public:
    static constexpr std::size_t kBuckets = 24;
    void record(std::chrono::nanoseconds d) {
        const auto us = static_cast<std::uint64_t>(std::max<std::int64_t>(d.count(), 0) / 1000);
        const auto b = std::min<std::size_t>(std::bit_width(us), kBuckets - 1);
        counts_[b].fetch_add(1, std::memory_order_relaxed);   // no lock, no allocation
    }
    std::uint64_t count(std::size_t b) const { return counts_[b].load(std::memory_order_relaxed); }
private:
    std::array<std::atomic<std::uint64_t>, kBuckets> counts_{};
};

class ScopeTimer {                                    // a tracing span in miniature (day 08)
public:
    explicit ScopeTimer(LatencyHistogram& h) : h_(h), start_(std::chrono::steady_clock::now()) {}
    ~ScopeTimer() { h_.record(std::chrono::steady_clock::now() - start_); }
    ScopeTimer(const ScopeTimer&) = delete;
    ScopeTimer& operator=(const ScopeTimer&) = delete;
private:
    LatencyHistogram& h_;
    std::chrono::steady_clock::time_point start_;
};

// void control_cycle() { ScopeTimer span(g_cycle_latency); /* ... */ }
```

Relaxed ordering is correct here because each counter is independent and nothing else is published through it (day 40). A reporter thread reads the buckets periodically and exports them; the control loop only ever does one `fetch_add`.

#### in practice

A robotics team's CI runs a matrix rather than one build:

```text
release        -O2              unit + integration tests, benchmarks (day 50)
asan+ubsan     -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer
tsan           -O1 -g -fsanitize=thread         concurrency tests, repeated
fuzz (nightly) clang++ -fsanitize=fuzzer,address    the telemetry parser
```

The fuzz target is a single function the fuzzer calls with mutated bytes:

```cpp
extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t* data, std::size_t size) {
    parse_nmea_sentence(std::string_view(reinterpret_cast<const char*>(data), size));
    return 0;   // crashes, sanitizer reports, and timeouts are the failures
}
```

On the robot, each pipeline stage has a latency histogram, a dropped-frame counter, and a span per frame. When an operator reports "the arm hesitated at 14:02", the team pulls the spans for that minute and sees the planner stage at its p99.9 while a log shows a map reload: a diagnosis in minutes instead of a week of trying to reproduce it.

#### watch out for

Observability code runs in the paths you are trying to observe, so it can cause the problems it is meant to find. Writing a log line can allocate (day 52), take a lock inside the logging library, and block on I/O when the disk or the network is slow. Inside a 1 kHz control loop, or while holding a mutex (day 41), that turns a diagnostic into a deadline miss or a convoy of blocked threads. Keep hot paths to counters and fixed-size records: push events into a preallocated lock-free ring buffer and let a background thread format and write them, rate-limit repeated messages, and never log while holding a lock you share with a latency-critical thread.

#### the takeaway

Design for both questions from the start: deterministic tests through injected seams for "does it work", and cheap, structured logs, metrics, and spans for "what is it doing", built so that observing the system does not change it.

#### optional challenge

You add a helper `void check_near(double a, double b, double tol) { check(std::abs(a - b) <= tol, "near"); }` and use it across many tests. Failures now all report the same line. Why, and how do you fix it without a macro?

<details>
<summary>answer</summary>

`std::source_location::current()` as a default argument is evaluated where the call to `check` is written, which is now inside `check_near`, so every failure points at the helper. Give the helper the same defaulted parameter and forward it: `void check_near(double a, double b, double tol, std::source_location loc = std::source_location::current()) { check(std::abs(a - b) <= tol, "near", loc); }`. Each test's call site now fills in its own location, and `check` reports it. This forwarding is how test frameworks and logging libraries built on `source_location` pass the caller's location through layers of helpers.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-54"></a>

### day 54: refactoring legacy code and architectural tradeoffs

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 08, 12, 24, 26, 27, 43, 44, 53

#### the idea

Every engineer has opened a 4,000-line file full of raw `new`, `char*` buffers, and out-parameters and thought "this needs a rewrite". Big rewrites usually take far longer than planned, while the old code keeps shipping and accumulating fixes the new code lacks. The approach that works is less dramatic: change the code in small, verified steps, each one leaving the system working, and make the architectural calls deliberately and in writing.

#### understanding the concept

Legacy code, in the useful definition, is code without tests: you cannot change it with confidence. So the first step is not modernization; it is getting a safety net.

**Characterization tests** record what the code does today, not what it should do. You feed it inputs, observe outputs, and assert those outputs, including the strange ones. They are scaffolding for refactoring: when one fails, you changed behavior, and you decide whether that was intended.

**Seams** (day 44) are where you can change behavior without editing the code in place: a constructor parameter, a virtual function, a template parameter, a link-time substitution. Legacy code often has none; creating the first seam with a minimal, careful edit is usually the riskiest step, so keep it mechanical.

A safe **modernization order** goes from zero-risk to higher-risk changes:

1. Turn on warnings (`-Wall -Wextra`, then `-Werror` directory by directory) and run sanitizer builds in CI (day 53). This finds real bugs without touching a line.
2. Write characterization tests around the code you are about to change.
3. Fix ownership at boundaries: RAII wrappers and `std::unique_ptr` in signatures (days 08, 12), so leaks become impossible rather than unlikely.
4. Adopt vocabulary types: `std::string_view` for read-only strings, `std::optional` or a variant result for "maybe" and errors, `std::filesystem::path` for paths (days 24 to 27).
5. Apply mechanical modernizations with tools, one kind of change per commit.

The **strangler pattern** replaces a subsystem without a big bang: put an interface in front of the old implementation, build the new one behind the same interface, route a growing share of traffic to it, and delete the old one when nothing uses it. In robotics this often means running the new module in shadow mode on recorded data and comparing its outputs with the old one before it ever drives a motor.

#### in code

The legacy function, with its problems labelled:

```cpp
// calib_loader.cpp, circa 2009
#include <cstdio>
#include <cstring>

struct Calib { double gain, offset, skew; };

bool load_calibration(const char* path, Calib** out, char* err, int errlen) {
    FILE* f = std::fopen(path, "r");
    if (!f) { std::strncpy(err, "open failed", errlen); return false; }  // BUG: may not terminate
    Calib* c = new Calib;
    if (std::fscanf(f, "%lf %lf %lf", &c->gain, &c->offset, &c->skew) != 3) {
        std::strncpy(err, "parse failed", errlen);
        std::fclose(f);
        return false;                                                    // BUG: leaks c
    }
    std::fclose(f);
    *out = c;                                                            // caller must delete
    return true;
}
```

`strncpy` does not write a terminator when the source is at least `errlen` characters long, so a caller that prints `err` reads past the buffer: undefined behavior. The parse-failure path leaks. Ownership of `*out` lives only in a comment.

Before changing anything, pin the behavior down:

```cpp
// Pin what the code does today, including the parts that look odd.
void characterize_load_calibration() {
    char err[64] = {};
    Calib* c = nullptr;

    write_file("ok.cal", "1.5 0.25 -3\n");
    assert(load_calibration("ok.cal", &c, err, sizeof err));
    assert(c->gain == 1.5 && c->offset == 0.25 && c->skew == -3.0);
    delete c;

    write_file("trailing.cal", "1 2 3 garbage\n");                // accepted today: keep?
    assert(load_calibration("trailing.cal", &c, err, sizeof err));
    delete c;

    write_file("short.cal", "1 2\n");
    assert(!load_calibration("short.cal", &c, err, sizeof err));
    assert(std::string(err) == "parse failed");                   // someone greps for this

    assert(!load_calibration("missing.cal", &c, err, sizeof err));
    assert(std::string(err) == "open failed");
}
```

The trailing-garbage case is the interesting one. It may be a bug, but some calibration file in the fleet may rely on it. Hyrum's law (day 47): every observable behavior has a user. The test makes that behavior visible so changing it becomes a decision.

Now the modern core, plus a shim so existing callers keep compiling:

```cpp
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <string>
#include <variant>

struct LoadError { std::string message; };

[[nodiscard]] std::variant<Calib, LoadError> read_calibration(const std::filesystem::path& path) {
    std::ifstream in(path);
    if (!in) return LoadError{"open failed"};
    Calib c{};
    if (!(in >> c.gain >> c.offset >> c.skew)) return LoadError{"parse failed"};
    return c;                                     // value, no ownership question at all
}

// Compatibility shim: old signature, new implementation. Delete when the last caller is gone.
[[deprecated("use read_calibration")]]
bool load_calibration(const char* path, Calib** out, char* err, int errlen) {
    auto result = read_calibration(path);
    if (auto* c = std::get_if<Calib>(&result)) { *out = new Calib(*c); return true; }
    std::snprintf(err, static_cast<std::size_t>(errlen), "%s",
                  std::get<LoadError>(result).message.c_str());   // always terminated
    return false;
}
```

The same characterization test passes against the shim, which is the evidence that the refactor preserved behavior. The `[[deprecated]]` attribute turns every remaining caller into a compiler warning, a built-in migration to-do list. Note what was deliberately not changed: the error strings, and the acceptance of trailing text. `fscanf` and `operator>>` can also differ on unusual numeric input, which is exactly why the test, not a code review, is the judge.

#### in practice

Mechanical modernization is where tools beat people. `clang-tidy` has a family of `modernize-*` checks (`use-nullptr`, `use-override`, `make-unique`, `loop-convert`, `use-using`, `pass-by-value`, and more) that rewrite code with fixes:

```sh
# one check per commit: each diff is large but trivially reviewable
run-clang-tidy -p build -checks='-*,modernize-use-nullptr' -fix
run-clang-tidy -p build -checks='-*,modernize-use-override' -fix
# reformat once, in its own commit, then hide it from blame
clang-format -i $(git ls-files '*.cpp' '*.h')
git rev-parse HEAD >> .git-blame-ignore-revs     # git config blame.ignoreRevsFile ...
```

The refactors that need judgment get written down. A lightweight architecture decision record (ADR) fits in a file next to the code:

```text
ADR-017: track storage layout
status:       accepted
context:      tracker misses its frame budget at high detection counts; perf counters
              show the association loop is dominated by cache misses (day 51).
decision:     store tracks as struct-of-arrays inside TrackTable; public API unchanged.
alternatives: keep AoS with hot/cold split (measured, not enough);
              pooled Track objects (fewer allocations, same misses).
consequences: + association loop within budget on recorded sessions
              - a new track field touches three places in TrackTable
              - debugger shows arrays, not tracks (pretty-printer added)
revisit if:   per-track behavior grows (polymorphic motion models) or counts drop.
```

The format matters less than the habit: context, the decision, the alternatives considered, the costs accepted, and when to revisit. The classic tradeoffs (maintainability versus performance, abstraction versus overengineering, compile-time versus runtime flexibility, object-oriented versus data-oriented layout) stop being religious arguments once each side has to write down its consequences.

Not everything should be refactored. Code that works, rarely changes, and is scheduled for retirement is cheapest left alone. Prioritize by change frequency times pain: `git log` tells you which files churn, and the bug tracker tells you which ones hurt.

#### watch out for

Never mix a refactoring and a behavior change in one commit. A refactoring should leave every characterization test green; a behavior change should change specific tests on purpose. Combine them and a failing test no longer tells you which change caused it, the review cannot separate "moved code" from "changed meaning", and a revert throws away both. The discipline is tedious and it is what makes legacy work safe.

#### the takeaway

Get a safety net before you change anything, then modernize in small, separately verifiable steps, and record the architectural decisions with their costs so the next engineer can revisit them instead of rediscovering them.

#### optional challenge

Product decides that trailing garbage in calibration files must now be rejected. Describe how you would ship that change safely after the refactoring above.

<details>
<summary>answer</summary>

Treat it as a behavior change in its own commit, after the refactor has landed and been verified. First check reality: scan the calibration files actually deployed (or a fleet sample) for trailing content, because a robot that refuses to start is worse than one that ignores a comment. Then change the rule in `read_calibration` (after the three reads, check that only whitespace remains), and update the characterization test deliberately: the "trailing" case now expects `parse failed` or, better, a more specific error. If files in the field do have trailing text, consider a transition period in which the loader accepts the file but logs a structured warning (day 53) so you can see who would break. Document the decision, briefly, where the next person will look.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-55"></a>

### day 55: putting it together: a small sensor-processing pipeline

**reading time:** about 10 minutes · **standard:** C++20 · **builds on:** days 12, 25, 29, 30, 31, 32, 36, 38, 44

#### the idea

Each lesson so far isolated one idea. Real code is where the ideas meet and pull against each other: the queue wants ownership to move, the processing stage wants to borrow, the test wants seams, and shutdown wants all of it to unwind in the right order. Today is one small program, about 160 lines, that compiles with `-std=c++20`, followed by a review of every decision in it.

#### understanding the concept

The shape is a classic two-stage pipeline:

```text
 source (fake sensor)          bounded queue            consumer thread
 producer jthread  ---push--->  [ Message x 8 ]  ---pop--->  Processor<Sink>
                                                              gate(span) -> sink.on_frame(span)
```

A producer thread pulls `Message`s (a frame of detections or a sensor fault) from an injected source and pushes them into a bounded queue. A consumer thread pops them, gates each frame's detections (drop weak and distant returns, sort strongest first), and hands the result to an injected sink. Ownership flows one way: a `Frame` is created by the source, moved through the queue, and owned by exactly one stage at a time. The sink only borrows the result.

Read the four parts for structure first, then the design review that follows.

#### in code

Part 1 defines the vocabulary: a value type and a closed set of messages.

```cpp
// part 1: values and messages (days 25, 32)
#include <algorithm>
#include <cassert>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <deque>
#include <functional>
#include <mutex>
#include <optional>
#include <ranges>
#include <span>
#include <stop_token>
#include <thread>
#include <utility>
#include <variant>
#include <vector>

struct Detection {
    double range_m{}, azimuth_rad{}, snr_db{};
    bool operator==(const Detection&) const = default;  // equality yes, ordering no
};
struct Frame { std::uint64_t seq{}; std::vector<Detection> detections; };
struct SensorFault { std::uint64_t seq{}; int code{}; };
using Message = std::variant<Frame, SensorFault>;

template <typename... Fs> struct overloaded : Fs... { using Fs::operator()...; };
```

Part 2 is day 38's queue, with close semantics so shutdown never leaves a thread blocked forever.

```cpp
// part 2: a bounded, closable queue (day 38)
template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {}
    bool push(T item) {                      // blocks while full; false once closed
        std::unique_lock lock(m_);
        not_full_.wait(lock, [&] { return closed_ || q_.size() < capacity_; });
        if (closed_) return false;
        q_.push_back(std::move(item));
        not_empty_.notify_one();
        return true;
    }
    std::optional<T> pop() {                 // blocks while empty; nullopt once closed and drained
        std::unique_lock lock(m_);
        not_empty_.wait(lock, [&] { return closed_ || !q_.empty(); });
        std::optional<T> item;
        if (!q_.empty()) {
            item.emplace(std::move(q_.front()));
            q_.pop_front();
            not_full_.notify_one();
        }
        return item;
    }
    void close() {
        { std::lock_guard lock(m_); closed_ = true; }
        not_full_.notify_all(); not_empty_.notify_all();
    }
private:
    std::mutex m_;
    std::condition_variable not_full_, not_empty_;
    std::deque<T> q_;
    std::size_t capacity_;
    bool closed_ = false;
};
```

Part 3 is the actual work. `gate` is a pure function over a borrowed span; `Processor` adapts it to messages and is constrained on what a sink must provide.

```cpp
// part 3: the processing stage (days 29, 30, 31, 52)
struct GateConfig { double min_snr_db = 10.0; double max_range_m = 200.0; };

// Pure, and allocation-free once `out` has enough capacity.
void gate(std::span<const Detection> in, const GateConfig& cfg, std::vector<Detection>& out) {
    auto keep = [&](const Detection& d) {
        return d.snr_db >= cfg.min_snr_db && d.range_m <= cfg.max_range_m;
    };
    out.clear();
    for (const Detection& d : in | std::views::filter(keep)) out.push_back(d);
    std::ranges::sort(out, std::ranges::greater{}, &Detection::snr_db);   // strongest first
}

template <typename S>
concept DetectionSink = requires(S& s, std::uint64_t seq, std::span<const Detection> ds, int code) {
    s.on_frame(seq, ds);       // ds is borrowed: valid only during the call
    s.on_fault(seq, code);
};

template <DetectionSink Sink>
class Processor {
public:
    Processor(GateConfig cfg, Sink& sink) : cfg_(cfg), sink_(sink) {}
    void operator()(const Message& msg) {
        std::visit(overloaded{
            [&](const Frame& f) { gate(f.detections, cfg_, scratch_); sink_.on_frame(f.seq, scratch_); },
            [&](const SensorFault& e) { sink_.on_fault(e.seq, e.code); },
        }, msg);
    }
private:
    GateConfig cfg_;
    Sink& sink_;
    std::vector<Detection> scratch_;         // reused every frame
};
```

Part 4 wires it together. Member order is the shutdown protocol, and `main` doubles as the test.

```cpp
// part 4: wiring, shutdown, and a test run (days 08, 36, 44)
using Source = std::function<std::optional<Message>()>;   // runtime seam: nullopt = end

template <DetectionSink Sink>
class Pipeline {
public:
    Pipeline(GateConfig cfg, Sink& sink, Source source)
        : source_(std::move(source)), queue_(8), processor_(cfg, sink),
          consumer_([this](std::stop_token st) {
              std::stop_callback on_stop(st, [this] { queue_.close(); });  // stop = close, then drain
              while (auto msg = queue_.pop()) processor_(*msg);
          }),
          producer_([this](std::stop_token st) {
              while (!st.stop_requested()) {
                  auto msg = source_();
                  if (!msg || !queue_.push(std::move(*msg))) return;
              }
          }) {}
    void finish() {                          // let the source run dry, then drain the queue
        if (producer_.joinable()) producer_.join();
        consumer_.request_stop();
        if (consumer_.joinable()) consumer_.join();
    }
    ~Pipeline() { producer_.request_stop(); finish(); }
private:
    Source source_;
    BoundedQueue<Message> queue_;
    Processor<Sink> processor_;
    std::jthread consumer_, producer_;       // last members: stopped and joined first
};

struct RecordingSink {                       // a fake, touched only by the consumer thread
    std::vector<std::pair<std::uint64_t, std::vector<Detection>>> frames;
    std::vector<int> faults;
    void on_frame(std::uint64_t seq, std::span<const Detection> ds) {   // ds is borrowed: copy it
        frames.emplace_back(seq, std::vector<Detection>(ds.begin(), ds.end())); }
    void on_fault(std::uint64_t, int code) { faults.push_back(code); }
};

int main() {
    std::vector<Detection> out;               // unit test of the pure stage: no threads
    const Detection strong{40, 0, 25}, weak{40, 0, 3}, far{900, 0, 40};
    const std::vector<Detection> in{weak, strong, far};
    gate(in, GateConfig{}, out);
    assert(out.size() == 1 && out[0] == strong);

    std::uint64_t seq = 0;                    // a fake sensor: deterministic frames, one fault
    Source fake_sensor = [&seq]() -> std::optional<Message> {
        if (seq == 4) return std::nullopt;
        if (seq == 2) return SensorFault{seq++, 17};
        const double s = static_cast<double>(seq);
        return Frame{seq++, {{50 + s, 0.1, 18}, {250, 0.2, 30}, {80, -0.3, 12 + s}, {120, 0, 6}}};
    };
    RecordingSink sink;
    {
        Pipeline pipeline(GateConfig{}, sink, fake_sensor);
        pipeline.finish();
    }                                         // threads joined: reading the sink is safe
    for (const auto& [n, ds] : sink.frames) {
        std::printf("frame %llu:", static_cast<unsigned long long>(n));
        for (const Detection& d : ds) std::printf("  %.0f m / %.0f dB", d.range_m, d.snr_db);
        std::printf("\n");
    }
    std::printf("faults: %zu (code %d)\n", sink.faults.size(), sink.faults.at(0));
}
```

Concatenated in order, the four parts form one translation unit. Built with `g++ -std=c++20 -Wall -Wextra -pedantic -O2 -pthread` (GCC 12), it compiles without warnings and prints:

```text
frame 0:  50 m / 18 dB  80 m / 12 dB
frame 1:  51 m / 18 dB  80 m / 13 dB
frame 3:  53 m / 18 dB  80 m / 15 dB
faults: 1 (code 17)
```

The output is deterministic even though two threads are involved: the queue is FIFO and there is one consumer, so the order of messages is fixed by the source.

#### in practice

Here is the design review, the part of the exercise that matters most. Every row is a decision someone could reasonably have made differently.

| decision | alternative | why this one |
|---|---|---|
| `Detection` defaults `==` only | also default `<=>` | `double` members give only `partial_ordering`, and detections have no natural order; sort by an explicit projection instead (day 32) |
| `Message` is a `std::variant` | base class with virtual `handle()` | closed set, value semantics, no allocation per message; a missing case in the visitor fails to compile (day 25) |
| bounded queue, producer blocks | unbounded queue, or drop-oldest | back-pressure bounds memory and latency; a sensor that cannot wait would need drop-oldest instead (day 38) |
| `gate` is a free function on `std::span` | member function taking `std::vector` | pure and testable without threads; any contiguous owner works (day 31) |
| `scratch_` reused every frame | return a fresh vector | no steady-state allocation (day 52); the cost is that `Processor` is stateful and not reentrant |
| sink: template constrained by a concept | virtual interface, or `std::function` | the per-frame call can inline, and a wrong sink fails to compile where the pipeline is created, naming the unmet requirement (days 29, 44); the cost is that `Pipeline` is a template |
| source: `std::function` | another template parameter | called once per frame, so one indirect call is noise next to sensor I/O; keeps `Pipeline` to one template parameter (day 17) |
| `jthread` plus a `stop_callback` that closes the queue | atomic flag and manual `join` | every exit path stops and joins, including a constructor that throws after the first thread started (day 36) |
| threads declared last | threads declared anywhere | members are built in declaration order, so the threads start only after everything they use exists; if construction fails midway, they are the first to be stopped (day 09) |
| `views::filter` feeding a loop | `std::copy_if` | equally good; C++20 has no `ranges::to` (that is C++23), so materializing is explicit either way (day 30) |

What a production version would add, and where it would go: a real sensor behind `Source` with a read timeout; a latency histogram and dropped-frame counter (day 53) around `processor_(*msg)`; validated configuration instead of defaults; and `std::format` (day 34) for output on a toolchain that has it. None of these require changing the structure, which is the real test of a design: the seams are where the next requirements land.

#### watch out for

The producer checks its stop token only between messages. If `source_()` blocks indefinitely (a sensor read with no timeout), `~Pipeline` waits for it, and shutdown hangs. Cooperative cancellation (day 36) only works if every blocking call cooperates: give the real source a timeout, or pass it the stop token so it can abandon the read. The same discipline applies to the sink: it receives a span into `scratch_` that is overwritten by the next frame, so a sink that keeps the span instead of copying the data would read garbage later (the lifetime rule from days 26 and 31, now enforced only by a comment in the concept).

#### the takeaway

Good C++ design is mostly about who owns what, who may block, and what can be substituted; when those three answers are explicit in the types, the rest of the program becomes small and testable.

#### optional challenge

What goes wrong if you move `BoundedQueue<Message> queue_;` below the two `std::jthread` members, leaving the constructor's initializer list unchanged?

<details>
<summary>answer</summary>

Members are initialized in declaration order, not initializer-list order (day 09). The `jthread`s would be constructed first, so the consumer thread could call `queue_.pop()` (and the producer `queue_.push()`) before `queue_` has been constructed: undefined behavior, and a race you might not see in testing. GCC's `-Wreorder` (part of `-Wall`) warns, because the initializer list no longer matches the declaration order, but that warning is the only safety net. Normal destruction would happen to survive, because the destructor body joins both threads before any member is destroyed. The exceptional path would not: if a later member's constructor threw, the already-running threads would be torn down around a queue that was never built. Declaring threads last, after everything they touch, makes both orders correct by construction.

</details>

[back to table of contents](#table-of-contents)

---

<a id="day-56"></a>

### day 56: week 8 review and the road ahead

**reading time:** about 10 minutes · **standard:** C++20 · **builds on:** days 50 to 55

#### recap

| day | key idea |
|---|---|
| [50](#day-50) | Profile to find where time goes, benchmark to compare alternatives; defeat dead-code elimination, warm up, repeat, report median and spread; Amdahl bounds the payoff. |
| [51](#day-51) | Memory moves in cache lines; contiguous, predictable access wins; AoS versus SoA and hot/cold splitting are layout choices driven by the hottest loops. |
| [52](#day-52) | Allocation has an unbounded tail; count it, `reserve` and reuse, use `std::pmr` arenas, and test that the steady state never touches the heap. |
| [53](#day-53) | Deterministic tests through injected seams; sanitizers and fuzzing in CI; structured logs, lock-free metrics, and RAII spans that are safe in hot paths. |
| [54](#day-54) | Characterization tests first, then small verified steps; shims and `[[deprecated]]` for migration; architecture decisions written down with their costs. |
| [55](#day-55) | One program where ownership, borrowing, seams, concurrency, and shutdown order all have to agree. |

#### review questions

**This week**

1. A microbenchmark says your new hash function is 25 percent faster, but the end-to-end frame time does not move. Give two distinct explanations and how you would tell them apart.
2. After converting detections from AoS to SoA, the SNR gating loop got faster but the per-detection association step got slower. Why is that plausible?
3. `std::pmr::vector<int> copy = arena_vec;` quietly puts `copy` on the heap. Why, and how do you keep it in the arena?
4. In day 55's pipeline, the consumer registers a `std::stop_callback` that closes the queue. Why not simply check `st.stop_requested()` in the loop?
5. Your characterization test asserts a behavior you are fairly sure is a bug. Why keep it during the refactor?

**Spaced repetition across the course**

6. *From week 1:* classify each as undefined, unspecified, or implementation-defined: `sizeof(long)`; the order in which `a()` and `b()` run in `f(a(), b())`; `INT_MAX + 1` for `int`.
7. *From week 2:* why does `std::vector<T>` copy rather than move elements during reallocation when `T`'s move constructor is not `noexcept`?
8. *From week 3:* `const Track& t = tracks.front(); tracks.push_back(next);` Is `t` still usable?
9. *From week 4:* what is wrong with `std::string_view sv = std::string("radar") + "_0";` followed by any use of `sv`?
10. *From week 5:* why can you not iterate a `const std::ranges::filter_view`?
11. *From week 6:* a producer writes a non-atomic payload and then sets an atomic `ready` flag with `memory_order_relaxed`; the consumer spins on `ready` with relaxed loads, then reads the payload. What is the bug?
12. *From week 7:* with pimpl and `std::unique_ptr<Impl>`, why must the destructor be declared in the header and defined in the `.cpp`?

#### mini exercise

Extend the day 55 pipeline so that the time each sink call takes is recorded in day 53's `LatencyHistogram`, without editing `Pipeline`, `Processor`, or `RecordingSink`. Decide which seam the feature belongs behind, and name one thing your choice cannot measure.

#### answers

<details>
<summary>1. faster microbenchmark, unchanged frame time</summary>

Either the hash is a small share of the frame (Amdahl: 25 percent of 2 percent is invisible), or the microbenchmark's conditions (hot cache, one key pattern, no contention) do not hold in the pipeline. A profile of the real workload distinguishes them: if the hash's share is tiny, it is the first; if the share is large but did not shrink, it is the second.

</details>

<details>
<summary>2. SoA helps one loop and hurts another</summary>

Gating reads one field across many detections, so SoA packs 16 useful floats per line. Association reads all fields of one detection at a time, which in SoA touches a different line per field instead of one line. Layout should follow the dominant access pattern; sometimes a hot/cold split serves both.

</details>

<details>
<summary>3. pmr copy on the heap</summary>

Copy construction asks `select_on_container_copy_construction`, which for `polymorphic_allocator` returns a default-constructed allocator, meaning the default resource. Use the allocator-extended constructor: `std::pmr::vector<int> copy(arena_vec, &arena);`.

</details>

<details>
<summary>4. why the stop callback closes the queue</summary>

A consumer blocked inside `pop()` is waiting on a condition variable and never reaches the loop condition, so checking the token would not wake it. Closing the queue wakes it, lets it drain, and makes `pop()` return `nullopt`. (A `std::condition_variable_any` wait that takes the stop token is the other C++20 option.)

</details>

<details>
<summary>5. keeping a test for a bug</summary>

The refactor must not change behavior; if it fixes the bug in passing, you cannot tell intended change from accident, and someone may depend on the old behavior. Keep the test green through the refactor, then change the behavior in its own commit and update the test deliberately.

</details>

<details>
<summary>6. from week 1</summary>

`sizeof(long)`: implementation-defined (documented by the implementation). Argument order: unspecified (since C++17 the two calls are indeterminately sequenced, never interleaved). `INT_MAX + 1`: undefined behavior, and the optimizer may assume it never happens.

</details>

<details>
<summary>7. from week 2</summary>

Reallocation offers the strong guarantee. If a move could throw halfway, the old buffer would already be partly moved from and could not be restored. `std::move_if_noexcept` therefore copies when the move is not `noexcept` and a copy constructor exists.

</details>

<details>
<summary>8. from week 3</summary>

Only if no reallocation happened. If `size() == capacity()` before the `push_back`, the elements move to a new buffer, every reference is invalidated, and using `t` is undefined behavior. Copy the value, keep an index, or `reserve` first.

</details>

<details>
<summary>9. from week 4</summary>

The concatenation produces a temporary `std::string` that is destroyed at the end of the full-expression. `sv` points into freed memory, so any read is undefined behavior. A view never extends a lifetime.

</details>

<details>
<summary>10. from week 5</summary>

`filter_view::begin()` caches the first matching position so that repeated calls are amortized O(1). Caching mutates the view, so `begin()` is non-const. Take the view by value or by non-const reference.

</details>

<details>
<summary>11. from week 6</summary>

Relaxed operations create no synchronizes-with edge, so seeing `ready == true` does not make the payload write visible. The payload accesses are an unordered conflicting pair: a data race, which is undefined behavior. Use `release` on the store and `acquire` on the load.

</details>

<details>
<summary>12. from week 7</summary>

`std::unique_ptr<Impl>`'s deleter needs a complete `Impl` where the destructor is instantiated. An implicit destructor is inline in the header, where `Impl` is incomplete, so it fails to compile (libstdc++ reports "invalid application of `sizeof` to incomplete type"). Declare `~Widget();` in the header and define it as `= default` in the `.cpp` after `Impl`; the same applies to the move operations.

</details>

<details>
<summary>mini exercise</summary>

The sink concept is already a seam, so the feature fits behind it as a decorator that satisfies `DetectionSink` by forwarding:

```cpp
template <DetectionSink Inner>
class TimingSink {                         // same concept in, same concept out
public:
    TimingSink(Inner& inner, LatencyHistogram& h) : inner_(inner), h_(h) {}
    void on_frame(std::uint64_t seq, std::span<const Detection> ds) {
        ScopeTimer span(h_);               // day 53
        inner_.on_frame(seq, ds);
    }
    void on_fault(std::uint64_t seq, int code) { inner_.on_fault(seq, code); }
private:
    Inner& inner_;
    LatencyHistogram& h_;
};

// RecordingSink recorder; LatencyHistogram h; TimingSink timed(recorder, h);
// Pipeline pipeline(GateConfig{}, timed, fake_sensor);   // Pipeline is unchanged
```

No existing class changes (open/closed, day 43), and the decorator inlines because the seam is compile-time. What it cannot measure: time spent in `gate`, and end-to-end latency from sensor to sink. The first needs timing inside `Processor`; the second needs a capture timestamp in `Frame`, a change to the message type itself. Features that change what the data means belong in the types; features that observe it belong behind seams.

</details>

#### connections

Week 8 leaned on everything before it. Benchmarking and cache behavior gave substance to the container choices of day 15 and the false sharing of day 40. The cost of allocation explained why the rule of zero (day 11), `reserve` (day 15), and the hidden costs of `std::function` (day 17) and `shared_ptr` (day 12) matter in practice. Testing and observability turned dependency injection (day 44), RAII (day 08), and `std::source_location` (day 34) into everyday tools, and the sanitizers of day 06 into CI jobs. Legacy refactoring was week 4's C++17 vocabulary applied at scale, and day 55 needed something from every week: value semantics, variants, concepts, spans, views, `jthread`, a condition-variable queue, and member order as a shutdown protocol.

##### where to go next

You now have the core of modern C++17 and C++20 and, more importantly, the habit of asking what each feature costs and what it promises. C++23 is the natural next step, and most of it builds directly on this course:

- `std::expected<T, E>`: the result type days 20 and 25 approximated with variants, now standard.
- `std::print` and `std::println`: `std::format` (day 34) straight to output.
- deducing `this`: explicit object parameters that simplify CRTP (day 46) and remove const/non-const duplication.
- `std::generator`: the coroutine generator you wrote by hand on day 48, ready-made.
- `std::mdspan`: multidimensional views over contiguous memory, `std::span` (day 31) for matrices and images.
- `std::flat_map` and `std::flat_set`: sorted-vector associative containers, day 15's locality argument as a library type.

Further out, the C++26 feature set includes language contracts (preconditions and postconditions as declarations, the formal version of day 47's API contracts) and static reflection, which lets code inspect types at compile time and will reshape serialization and boilerplate generation. Treat both as directions to watch; check your compiler's status pages before relying on them.

The most effective practice from here is unglamorous: read compiler output on Compiler Explorer when you wonder what something costs, run your tests under sanitizers, measure before you optimize, and write down the tradeoffs you choose. The language will keep growing; the judgment you built over these eight weeks is what makes each new feature easy to place. Thanks for reading, and enjoy the code you write next.

[back to table of contents](#table-of-contents)

---

<a id="cheat-sheet"></a>

## modern C++17/20 cheat sheet

A compact reference for after the course. The day numbers point back to the full explanations.

### initialization ([day 02](#day-02))

```cpp
int a;            // local: indeterminate value, reading it is UB
int b{};          // value-initialized: 0
int c{3.5};       // error: narrowing is rejected inside braces
auto d{1};        // int (C++17 rule); auto e = {1}; is std::initializer_list<int>
std::vector<int> v1(3, 1);  // {1, 1, 1}
std::vector<int> v2{3, 1};  // {3, 1}: braces prefer initializer_list constructors
Point p{.x = 1, .y = 2};    // C++20 designated initializers, in declaration order
```

### special members and ownership ([days 08 to 12](#day-08))

| you declare | copy ops generated? | move ops generated? |
| --- | --- | --- |
| nothing | yes | yes |
| destructor | yes (deprecated) | no, copies are used instead |
| copy constructor or copy assignment | the other one yes (deprecated) | no |
| move constructor or move assignment | no (deleted) | only the one you wrote |

- **rule of zero:** hold resources in members that manage themselves (`std::vector`, `std::string`, `std::unique_ptr`) and declare no special members.
- **rule of five:** if you must write one of destructor, copy constructor, copy assignment, move constructor, or move assignment, think about all five.
- Mark move operations `noexcept` so `std::vector` can move instead of copy when it reallocates.
- Destructors are implicitly `noexcept` (unless a member or base says otherwise); never let them throw.

| signature | meaning |
| --- | --- |
| `void f(Widget&)` / `void f(const Widget&)` | borrow, must not be null |
| `void f(Widget*)` | borrow, may be null |
| `void f(std::unique_ptr<Widget>)` | takes ownership |
| `void f(std::unique_ptr<Widget>&)` | may reseat the caller's pointer (rare) |
| `void f(std::shared_ptr<Widget>)` | shares ownership (keeps it alive) |
| `void f(std::span<const T>)`, `void f(std::string_view)` | borrows a contiguous sequence |
| `std::unique_ptr<Widget> make()` | caller becomes the owner |

### value categories and moves ([days 05](#day-05), [10](#day-10), [19](#day-19))

```text
           expression
           /        \
      glvalue      rvalue
      /     \      /    \
  lvalue    xvalue     prvalue

lvalue:  has identity, not moved from implicitly   x, *p, a[i], f() returning T&
xvalue:  has identity, can be moved from           std::move(x), f() returning T&&
prvalue: no identity until materialized            42, T{}, f() returning T
```

- `std::move(x)` is only a cast to `T&&`; the move happens when a move constructor or assignment picks it up.
- `std::forward<T>(x)` keeps the caller's value category; use it only with forwarding references (`T&&` with deduced `T`, or `auto&&`).
- Don't `return std::move(local);`: it blocks copy elision. Returning a prvalue is guaranteed to be elided since C++17.
- A named rvalue reference is an lvalue.

### undefined, unspecified, implementation-defined ([day 06](#day-06))

| category | meaning | examples |
| --- | --- | --- |
| undefined | no requirements at all; the optimizer assumes it never happens | signed overflow, out-of-bounds access, use after free, data race, reading an uninitialized `int`, strict aliasing violation |
| unspecified | one of several valid outcomes, not documented | order of evaluation of function arguments, string literal storage overlap |
| implementation-defined | chosen and documented by the implementation | `sizeof(int)`, signedness of plain `char`, `CHAR_BIT`, right shift of a negative integer (before C++20) |

Defenses: `-Wall -Wextra`, `-fsanitize=address,undefined` (and `thread` for races), `std::bit_cast` or `std::memcpy` instead of pointer type punning.

### containers and algorithms ([days 15 to 17](#day-15))

| container | access | insert/erase | notes |
| --- | --- | --- | --- |
| `vector` | O(1) random | O(1) amortized at end, O(n) elsewhere | default choice; contiguous; reallocation invalidates everything |
| `array` | O(1) random | fixed size | no heap |
| `deque` | O(1) random | O(1) at both ends | chunked, not contiguous |
| `list` | O(n) | O(1) with an iterator | stable references, splicing; one allocation per node |
| `map` / `set` | O(log n) | O(log n) | ordered; node-based |
| `unordered_map` / `set` | O(1) average | O(1) average | hashing cost; rehash invalidates iterators |

```cpp
std::erase_if(v, [](const Track& t) { return t.stale; });      // C++20
v.erase(std::remove_if(v.begin(), v.end(), is_stale), v.end()); // C++17 equivalent
auto [it, inserted] = m.try_emplace(key, args...);             // no move-from if key exists
if (auto it = m.find(k); it != m.end()) use(it->second);        // C++17 if-initializer
```

Lambda captures: `[=]` copies what is used (implicitly capturing `this` through `[=]` is deprecated in C++20), `[&]` references (beware escaping), `[p = std::move(ptr)]` init-capture, `[this]` captures the pointer, `[*this]` copies the object (C++17).

### C++17 at a glance ([week 4](#week-4))

| feature | example |
| --- | --- |
| structured bindings | `for (const auto& [name, value] : config)` |
| `if`/`switch` initializers | `if (auto r = parse(s); r) { ... }` |
| `if constexpr` | `if constexpr (std::is_integral_v<T>) { ... }` |
| fold expressions | `(std::cout << ... << args);` / `(... && checks)` |
| CTAD | `std::pair p{1, 2.0};` `std::lock_guard lock{m};` |
| inline variables | `inline constexpr int kMaxJoints = 7;` in a header |
| guaranteed copy elision | returning a prvalue of a non-movable type works |
| nested namespaces | `namespace robot::control { }` |
| attributes | `[[nodiscard]]`, `[[maybe_unused]]`, `[[fallthrough]]` |
| `std::optional<T>` | maybe a value; `value_or`, `*opt` (UB if empty) |
| `std::variant<Ts...>` | one of several types; `std::visit`, `std::get_if` |
| `std::any` | any copyable type; `std::any_cast`; rarely the right tool |
| `std::string_view` | non-owning, not null-terminated; never outlive the source |
| `std::filesystem` | `path`, `exists`, `directory_iterator`, `error_code` overloads |
| `std::from_chars`, `std::to_chars` | locale-free, allocation-free number conversion |
| `std::pmr` | memory resources: `monotonic_buffer_resource`, pool resources |
| `std::scoped_lock`, `std::shared_mutex` | multi-mutex locking, reader/writer locks |

```cpp
template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };
template <class... Fs> overloaded(Fs...) -> overloaded<Fs...>;  // not needed in C++20

std::visit(overloaded{
    [](const Detection& d) { handle(d); },
    [](const Heartbeat&)   { /* ignore */ },
}, message);
```

### C++20 at a glance ([week 5](#week-5))

| feature | example |
| --- | --- |
| concepts | `template <std::integral T>`, `void f(std::floating_point auto x)` |
| custom concept | `template <class T> concept Sensor = requires(T s) { { s.read() } -> std::convertible_to<double>; };` |
| ranges and views | `v \| std::views::filter(pred) \| std::views::transform(f)` |
| projections | `std::ranges::sort(tracks, {}, &Track::range_m);` |
| `std::span<T>` | `void process(std::span<const float> samples)` |
| three-way comparison | `auto operator<=>(const T&) const = default;` |
| `consteval` / `constinit` | forced compile-time call / compile-time-initialized static |
| `std::format` | `std::format("{:>8.3f} m", range)` (GCC 13+, Clang 17+, MSVC 19.29+) |
| `std::jthread` | joins on destruction; `std::stop_token` for cancellation |
| `std::latch`, `std::barrier`, `std::counting_semaphore` | one-shot sync, phased sync, limited concurrency |
| atomic `wait`/`notify_one` | block on an atomic value change |
| `std::source_location` | file, line, function for logging without macros |
| `<bit>` | `std::bit_cast`, `std::popcount`, `std::endian` |
| container helpers | `contains`, `starts_with`, `ends_with`, `std::erase_if`, `std::ssize` |
| templated lambdas | `[]<class T>(const std::vector<T>& v) { ... }` |
| coroutines | `co_await`, `co_yield`, `co_return` (machinery only; no ready-made types) |
| modules | `export module sensors;` / `import sensors;` (tooling still maturing) |

### not in C++20 (easy to mix up)

| C++23 | what to use in C++20 |
| --- | --- |
| `std::expected` | `std::variant<T, Error>`, a small result type, or exceptions |
| `std::print`, `std::println` | `std::cout << std::format(...)` or `std::fputs` |
| `std::ranges::to` | construct the container from `begin()`/`end()` of the view |
| `std::views::zip`, `enumerate`, `chunk` | index loops or a hand-written helper |
| `std::generator` | a hand-written coroutine type or a library (cppcoro) |
| deducing `this` | CRTP |
| `std::mdspan` | `std::span` plus manual index math |
| `std::move_only_function` | `std::function` (requires copyable callables) or a custom wrapper |
| `std::flat_map` | sorted `std::vector` of pairs plus `std::lower_bound` |
| `if consteval` | `if (std::is_constant_evaluated())` |

### concurrency rules of thumb ([week 6](#week-6))

- A data race (unsynchronized conflicting access, at least one write) is UB. A race condition (wrong timing logic) can exist without one.
- Prefer `std::jthread` with `std::stop_token` over `std::thread` plus a flag; never let a joinable `std::thread` be destroyed.
- Keep a mutex next to the data it protects, lock with `std::scoped_lock`, keep critical sections short, never call unknown code (callbacks) while holding a lock.
- Always wait on a condition variable with a predicate: `cv.wait(lock, [&] { return !queue.empty() || closed; });`
- The future returned by `std::async` blocks in its destructor; keep it.
- Atomics: default to `seq_cst`; use `release` on the publishing store and `acquire` on the observing load for the flag pattern; `relaxed` only for independent counters.
- Lock ordering or `std::scoped_lock` prevents lock-order deadlocks. Confinement and message passing prevent most of the rest.

### design reminders ([week 7](#week-7))

| need | first choice | alternative |
| --- | --- | --- |
| open set of types, runtime choice | virtual interface | type erasure for value semantics |
| closed set of types | `std::variant` + `std::visit` | virtual interface |
| zero-overhead customization | template + concept | CRTP |
| store any callable | `std::function` | template parameter |
| testable dependency | constructor injection of an interface or a concept-constrained template | `std::function` seam, link-time seam |
| stable ABI | pimpl | C interface |

### performance habits ([week 8](#week-8))

- Measure first: optimized build, `std::chrono::steady_clock` or a benchmark library, many repetitions, report median and spread.
- Contiguous data and predictable access patterns usually beat clever algorithms on small and medium inputs; confirm with a profiler and hardware counters.
- Reserve, reuse, and preallocate; keep allocations out of real-time loops; consider `std::pmr` arenas.
- Optimize where the profile says, and write down why the code is now less obvious.

### compiler flags worth knowing

```sh
-std=c++20 -Wall -Wextra -pedantic -Werror=return-type   # language mode and warnings
-O2 -g                                                     # optimized, still debuggable
-fsanitize=address,undefined                               # ASan + UBSan (debug/test builds)
-fsanitize=thread                                          # TSan, in a separate build
-D_GLIBCXX_ASSERTIONS                                      # bounds-checked libstdc++ operator[]
```

<a id="references"></a>

## references for deeper study

A short, curated list. Where a resource covers several weeks, it is listed once under the area where it helps most.

### primary references

- **cppreference.com**: <https://en.cppreference.com/w/cpp>. The day-to-day reference for the language and library, with a version tag on every feature. Its compiler support tables (<https://en.cppreference.com/w/cpp/compiler_support>) tell you which compiler version implements which C++17/20/23 feature.
- **the C++ Core Guidelines** (Stroustrup and Sutter, eds.): <https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines>. Rules with rationale for resource management (R), interfaces (I), functions (F), classes (C), concurrency (CP), and error handling (E). Most `clang-tidy` `cppcoreguidelines-*` checks trace back to it.
- **the working draft of the standard**: <https://eel.is/c++draft/>. A browsable, linkable version of the latest draft. Use it when cppreference is not precise enough; for a specific published standard, look for the final draft of that version (N4659 for C++17, N4861 for C++20).
- **isocpp.org**: <https://isocpp.org>. The Standard C++ Foundation's site, including the C++ FAQ and links to proposals and trip reports.

### books

| book | best for |
| --- | --- |
| Bjarne Stroustrup, *A Tour of C++*, 3rd edition (2022) | a fast, authoritative tour of modern C++ up to C++20 |
| Scott Meyers, *Effective Modern C++* (2014) | move semantics, forwarding references, smart pointers, lambdas (weeks 2 and 3); written for C++11/14 but still the clearest treatment of those topics |
| Nicolai Josuttis, *C++17: The Complete Guide* (2019) | every C++17 feature in depth (week 4) |
| Nicolai Josuttis, *C++20: The Complete Guide* (2022) | concepts, ranges, `<=>`, `span`, `jthread`, coroutines, modules (weeks 5 to 7) |
| Nicolai Josuttis, *C++ Move Semantics: The Complete Guide* (2020) | everything about moves, including the edge cases (day 10) |
| Anthony Williams, *C++ Concurrency in Action*, 2nd edition (2019) | threads, synchronization, and the memory model (week 6) |
| Klaus Iglberger, *C++ Software Design* (2022) | design principles, patterns, and type erasure in modern C++ (week 7) |
| Fedor Pikus, *The Art of Writing Efficient Programs* (2021) | performance, the memory hierarchy, and concurrency performance (week 8) |
| Michael Feathers, *Working Effectively with Legacy Code* (2004) | seams, characterization tests, and safe refactoring (days 44 and 54) |
| Herb Sutter, *Exceptional C++* (1999) and *More Exceptional C++* (2001) | exception safety and the reasoning behind the guarantees (day 20) |

### talks and articles

- Herb Sutter, "atomic<> Weapons: The C++ Memory Model and Modern Hardware" (C++ and Beyond 2012): the clearest long-form explanation of acquire/release and sequential consistency (day 40).
- Sean Parent, "Inheritance Is the Base Class of Evil" (GoingNative 2013) and "C++ Seasoning" (GoingNative 2013): value semantics with runtime polymorphism, and "no raw loops" (days 16 and 46).
- Mike Acton, "Data-Oriented Design and C++" (CppCon 2014): thinking in data and access patterns (day 51).
- Chandler Carruth, "Tuning C++: Benchmarks, and CPUs, and Compilers! Oh My!" (CppCon 2015): how to benchmark without fooling yourself (day 50).
- Ulrich Drepper, "What Every Programmer Should Know About Memory" (2007): the deep background on caches and memory (day 51).
- Lewis Baker, "Asymmetric Transfer" blog series: <https://lewissbaker.github.io>. The best explanation of how C++20 coroutines work under the hood (day 48).
- Hyrum's law: <https://www.hyrumslaw.com>. One paragraph that will change how you think about API changes (day 47).
- Herb Sutter, "Guru of the Week" archive: <https://herbsutter.com/gotw/>. Short, deep puzzles in the same spirit as this course's challenges.

### tools for exploring and verifying

| tool | use |
| --- | --- |
| Compiler Explorer, <https://godbolt.org> | compile snippets on many compilers and standards; read the generated assembly |
| C++ Insights, <https://cppinsights.io> | see what the compiler generates for lambdas, range-for, structured bindings, coroutines |
| Quick C++ Benchmark, <https://quick-bench.com> | run small Google Benchmark comparisons online (results are indicative, not your production hardware) |
| sanitizers (ASan, UBSan, TSan) | GCC and Clang documentation: <https://clang.llvm.org/docs/AddressSanitizer.html> and sibling pages |
| clang-tidy, <https://clang.llvm.org/extra/clang-tidy/> | `modernize-*`, `bugprone-*`, `performance-*`, and `cppcoreguidelines-*` checks (day 54) |
| Google Benchmark, <https://github.com/google/benchmark> | microbenchmarks with statistics (day 50) |
| GoogleTest and Catch2 | unit testing frameworks (day 53) |
| {fmt}, <https://fmt.dev> | the library `std::format` was standardized from; use it on toolchains without `<format>` (day 34) |

### staying current

- **C++23 and later:** cppreference marks every feature with its version, and the compiler support page shows what you can use today. The forward notes on [day 56](#day-56) list the C++23 features most likely to matter to you next.
- **trip reports:** after each ISO committee meeting, several committee members (Herb Sutter among them) publish summaries of what changed. They are the fastest way to follow the language's direction.
