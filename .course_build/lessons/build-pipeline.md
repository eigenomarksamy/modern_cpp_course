---
title: from source file to running program
standard: C++17
objective: trace how source files become a program, and tell which build stage produced an error
prerequisites: none
difficulty: 1
---

### the idea

you add a call to a function declared in a header, the file compiles without a murmur, and the build fails at the very last step: `undefined reference to 'calibrate(Sensor&)'`. the compiler was satisfied and the linker was not, because they answer different questions. most build errors that feel mysterious stop being mysterious once you know which stage produced them and how little each stage can see.

### understanding the concept

a C++ build is a pipeline, and each stage sees less than you might think.

```text
widget.cpp --preprocess--> translation unit --compile--> assembly --assemble--> widget.o
                                                                                    |
       other .o files and libraries ------------------------------------------> link --> program
```

1. **preprocessing** (`g++ -E`) is text substitution. `#include` pastes a file in, macros expand, `#if` removes text. the result is a **translation unit**: one source file plus everything it transitively included. a header is not a module or an interface in any formal sense; it is text that ends up copied into every translation unit that includes it.
2. **compilation** (`g++ -S`) turns one translation unit into assembly. the compiler sees exactly one translation unit at a time. it has no idea what any other `.cpp` file contains.
3. **assembly** (`g++ -c`) produces an object file: machine code plus a symbol table listing what this file *defines* and what it *references but does not define*.
4. **linking** combines object files and libraries, matches every undefined reference to exactly one definition, and patches addresses.

you can see the symbol table with `nm -C`. `U` means "I need this from someone else", `T` means "I define this in my code section":

```sh
$ g++ -std=c++17 -c main.cpp && nm -C main.o
                 U report_a()
                 U report_b()
0000000000000000 T main
```

the linker matches **names**, not types or meaning. the mangled name of `report_a()` encodes its namespace and parameter types, which is why a missing overload shows up as an "undefined reference" rather than a type error. return types and class layouts are not checked at link time at all.

**declarations versus definitions.** a declaration introduces a name (`double scale(double);`, `extern int count;`, `struct Pose;`). a definition creates the thing (the function body, the storage for the variable, the full class). you may declare something as often as you like; definitions are restricted.

**include guards and `#pragma once`** stop a header from being pasted twice into the *same* translation unit. they do nothing across translation units, which is the source of most confusion about duplicate symbols. `#pragma once` is not in the standard but every mainstream compiler supports it; its weakness is that "the same file" is decided by the compiler, which can be fooled by copies of a header reached through different paths. classic `#ifndef` guards are decided by the macro name, which you control.

### in code

**a missing definition.** a declaration is all the compiler needs to emit a call:

```cpp external
// calib.h
struct Sensor;
void calibrate(Sensor& s);               // declaration only

// main.cpp
#include "calib.h"
void run(Sensor& s) { calibrate(s); }    // compiles: the declaration is enough
```

```text
main.o: in function `run(Sensor&)': undefined reference to `calibrate(Sensor&)'
```

the compiler emitted a call to a symbol named `calibrate(Sensor&)` (mangled as `_Z9calibrateR6Sensor`) and moved on. the linker searched every object file and library on its command line and found no definition. it cannot tell you why, only that the name is missing.

**a duplicate symbol.** a helper defined in a header, included by two files:

```cpp external
// scale.h
#pragma once
double scale(double x) { return x * 2.0; }   // BUG: a definition with external linkage

// a.cpp: #include "scale.h"     b.cpp: #include "scale.h"
```

```text
ld: b.cpp:(.text+0x0): multiple definition of `scale(double)'; a.cpp:(.text+0x0): first defined here
collect2: error: ld returned 1 exit status
```

the guard did its job (one copy per translation unit), and the result is still two definitions in the program. the plain fix is to declare the function in the header and define it in one `.cpp`. the other fixes, `inline` and `static`, change the function's linkage, which is the subject of [[linkage-odr]].

### in practice

in a CMake project, the link errors you meet most often point at build configuration rather than code. "undefined reference" usually means a source file or library is missing from a target: a `.cpp` left out of `add_library`, or a forgotten `target_link_libraries`. "multiple definition" usually means a header defines something it should only declare. and an undefined reference to a function you can *see* defined usually means the declaration and the definition disagree: a missing `const` on a reference parameter, a different namespace, or C code called without `extern "C"`. in each case the two mangled names differ, so to the linker they are unrelated. read the demangled name in the error character by character (`c++filt` turns `_Z9calibrateR6Sensor` back into `calibrate(Sensor&)`) and compare it with the definition; that answers most of these in seconds.

### watch out for

**the linker checks names, not types.** declaring someone else's function by hand instead of including its header can link and still be wrong:

```cpp external
// parse.cpp
#include <cstdlib>
long parse_count(const char* text) { return std::strtol(text, nullptr, 10); }

// main.cpp: declares it by hand instead of including a header
int parse_count(const char* text);       // BUG: wrong return type, links anyway
```

on the Itanium C++ ABI used by GCC and Clang on Linux and macOS, the mangled name of an ordinary function encodes its name, namespace, and parameter types, but not its return type. both declarations produce the same symbol, so the program links, and every call reads an `int` where the function returned a `long`. the standard calls this ill-formed, no diagnostic required: the program has no defined meaning, and nothing is obliged to tell you. the defense is a habit. declare each function in exactly one header, include that header in the `.cpp` that defines it (so the compiler compares the two), and never re-declare a function by hand.

### the takeaway

the compiler checks one translation unit against the declarations it can see; the linker only matches names. a link error is a question about which definitions are in the program, not about your code's logic.

### optional challenge

`sensors.h` declares `namespace sensors { void reset_all(); }`. `sensors.cpp` includes it and defines `void reset_all() { /* ... */ }`. `main.cpp` calls `sensors::reset_all()`. every file compiles. what does the linker report, and why did the compiler not catch the mistake?

<details>
<summary>answer</summary>

`undefined reference to 'sensors::reset_all()'`. `sensors.cpp` defined a different function, `::reset_all()` in the global namespace. that is a perfectly legal new function, so the compiler had nothing to complain about, and the symbol `main.o` needs is defined nowhere.

writing the definition with a qualified name, `void sensors::reset_all() { ... }`, makes the compiler check that a matching declaration exists in `sensors`, which turns this whole class of mistake into a compile error in the file that made it.

</details>
