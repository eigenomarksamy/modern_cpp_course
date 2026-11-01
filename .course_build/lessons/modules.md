---
title: C++20 modules: a practical first look
standard: C++20
objective: read and write a named module with interface and implementation units, and judge when the tooling makes adoption worthwhile
prerequisites: linkage-odr, coupling-cohesion
difficulty: 2
---

### the idea

`#include` is a sixty-year-old idea: paste the text of another file here. every translation unit reparses the same headers, macros leak from one header into everything included after it, and the one definition rule quietly depends on every pasted copy being identical. C++20 modules replace pasting with importing a compiled interface. the language feature is real and usable; the tooling around it is still arriving, and both facts matter for when you adopt it.

### understanding the concept

**modules.** [[build-pipeline]] showed what `#include` really is: pasting text. every translation unit reparses the same headers, macros defined in one header leak into everything included after it, and the one definition rule depends on every copy of a header being identical. a named module is compiled once into a binary module interface (a compiler-specific file), and importers read that instead of reparsing source. only what you `export` is visible to importers; macros defined in a named module never leak out of it, and code that imports it is not affected by macros the importer defined earlier.

the vocabulary you need:

- **module interface unit**: starts with `export module name;` and declares what is exported.
- **module implementation unit**: starts with `module name;` and implicitly sees the interface, including its non-exported declarations.
- **global module fragment**: a `module;` line before the module declaration, where legacy `#include`s go so they do not become part of the module.
- **header units**: `import <vector>;` treats a header as an importable unit (it does export macros). compiler support is uneven.

### in code

**a small module.** file extensions and compiler flags vary by toolchain (`.cppm`, `.ixx`, `.mpp`; GCC before 14 needs the experimental `-fmodules-ts`).

```cpp external
// geometry.cppm: module interface unit
export module robotics.geometry;

double square(double v) { return v * v; } // not exported: visible only inside the module

export namespace geo {
struct Vec2 { double x, y; };
double norm(Vec2 v);                      // exported declaration
}
```

```cpp external
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

### in practice

**modules today.** named modules need a build system that scans sources for `import` and `export module` before compiling, because a module must be built before its importers. CMake supports this from 3.28 with the Ninja and Visual Studio generators, on recent compilers (CMake documents MSVC 19.34+, Clang 16+, and GCC 14+). binary module interfaces are compiler- and flag-specific, so a library still ships source interfaces, not BMIs. `import std;` is C++23, though some toolchains offer it as an extension in C++20 mode. a sensible adoption path: new leaf libraries as modules, internal code first, public headers kept until every consumer's toolchain supports modules. do not expect it to fix a build dominated by template instantiation or link time; measure where your build time goes first.

### watch out for

**includes belong in the global module fragment.** a header included *after* the module declaration becomes part of the module's purview:

```cpp external
export module robotics.geometry;
#include <cmath>          // BUG: <cmath>'s declarations now belong to this module
```

the declarations from that header are attached to `robotics.geometry`, which can conflict with the same header included normally elsewhere in the program and produces confusing errors or ODR problems. legacy includes go between `module;` and the module declaration, exactly as in `geometry.cpp`; `import` declarations and the module's own code come after it.

### the takeaway

modules fix textual inclusion and macro leakage, but adoption is gated by build-system and compiler support, so introduce them from the leaves inward and measure where your build time goes before expecting a speedup.

### optional challenge

in `main.cpp`, which of these compile: `geo::norm(v)`, `geo::Vec2{1, 2}`, `square(2.0)`, `std::sqrt(2.0)` (with no `#include <cmath>` in `main.cpp`)?

<details>
<summary>answer</summary>

`geo::norm` and `geo::Vec2` compile: both are declared inside the `export namespace geo` block. `square` does not: it is not exported, so it is visible only inside the module. `std::sqrt` does not either: `<cmath>` was included in the implementation unit's global module fragment, and nothing from it is exported to importers. unlike an `#include`, importing a module brings in exactly what the module exports, so `main.cpp` must include `<cmath>` itself if it needs it.

</details>
