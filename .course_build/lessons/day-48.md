<a id="day-48"></a>

## day 48: C++20 modules and coroutines: a practical first look

**reading time:** about 10 minutes · **standard:** C++20 · **builds on:** days 01, 03, 08

### the idea

C++20 added two large language features that change how code is *organized* rather than what it computes. Modules replace textual `#include` with compiled interfaces. Coroutines let a function pause and resume, so a scan pattern or a network protocol can be written as straight-line code instead of a hand-rolled state machine. Both are real and usable, and both come with caveats about tooling and lifetimes that you need before you adopt them. This is a first look: enough to read, write, and judge them.

### understanding the concept

**Modules.** Day 01 showed what `#include` really is: pasting text. Every translation unit reparses the same headers, macros defined in one header leak into everything included after it, and the one definition rule depends on every copy of a header being identical. A named module is compiled once into a binary module interface (a compiler-specific file), and importers read that instead of reparsing source. Only what you `export` is visible to importers; macros defined in a named module never leak out of it, and code that imports it is not affected by macros the importer defined earlier.

The vocabulary you need:

- **module interface unit**: starts with `export module name;` and declares what is exported.
- **module implementation unit**: starts with `module name;` and implicitly sees the interface, including its non-exported declarations.
- **global module fragment**: a `module;` line before the module declaration, where legacy `#include`s go so they do not become part of the module.
- **header units**: `import <vector>;` treats a header as an importable unit (it does export macros). Compiler support is uneven.

**Coroutines.** A function becomes a coroutine when its body uses `co_await`, `co_yield`, or `co_return`. Its state (the parameters, the locals that live across a suspension, and a *promise object*) lives in a **coroutine frame**, which is usually heap-allocated; the compiler may elide that allocation when it can prove the frame's lifetime is nested in the caller's, but nothing guarantees it. C++20 supplies only the machinery: the return type must provide a nested `promise_type` that tells the compiler what to do at start, at each `co_yield`, at the end, and on exceptions. The standard ships no ready-made generator or task type in C++20 (`std::generator` arrives in C++23).

`co_await x` asks an *awaiter* three questions: `await_ready()` (can we skip suspending?), `await_suspend(handle)` (we are suspended; who resumes us, and when?), and `await_resume()` (the result of the expression). `std::suspend_always` and `std::suspend_never` are the two trivial awaiters.

### in code

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

### in practice

**Modules today.** Named modules need a build system that scans sources for `import` and `export module` before compiling, because a module must be built before its importers. CMake supports this from 3.28 with the Ninja and Visual Studio generators, on recent compilers (CMake documents MSVC 19.34+, Clang 16+, and GCC 14+). Binary module interfaces are compiler- and flag-specific, so a library still ships source interfaces, not BMIs. `import std;` is C++23, though some toolchains offer it as an extension in C++20 mode. A sensible adoption path: new leaf libraries as modules, internal code first, public headers kept until every consumer's toolchain supports modules. Do not expect it to fix a build dominated by template instantiation or link time; measure where your build time goes first.

**Coroutines today.** They shine for asynchronous I/O (a telemetry uploader written as `co_await socket.async_write(...)` in sequence instead of nested callbacks), protocol state machines, and lazy sequences. In practice you use a library's types: Asio's `awaitable`, folly's coro, or the generator in your toolchain's C++23 mode. Writing your own `task` type with correct continuation, cancellation, and thread handoff is much harder than the generator above.

### watch out for

**Reference parameters dangle across suspension points.** The frame copies parameters, but copying a reference copies the reference.

```cpp
Generator<char> letters(const std::string& s) { for (char c : s) co_yield c; }

auto g = letters("radar");   // BUG: the temporary std::string dies at the end of this line
while (g.next()) { }         // undefined behavior: the frame refers to a destroyed string
```

The fix is to take the parameter by value (`std::string s`), so the frame owns a copy. The same applies to `std::string_view`, `std::span`, and lambda coroutines: a lambda's captures live in the lambda object, not the frame, so the lambda object must outlive the coroutine it started.

Also count the cost: each coroutine call may allocate a frame, and every resume is typically an indirect call through the handle. That is irrelevant for an uploader and potentially relevant in a 10 kHz control loop; custom `operator new` on the promise type gives you control of the allocation, and a profiler tells you whether it matters.

### the takeaway

Modules fix textual inclusion and macro leakage, but adoption is gated by build-system and compiler support, so introduce them from the leaves inward. Coroutines turn state machines into straight-line code; pass parameters by value, let RAII own the frame, and prefer a library's coroutine types for asynchronous work.

### optional challenge

What does `serpentine_scan(2, 3)` execute before the first call to `next()`, and what would change if `initial_suspend()` returned `std::suspend_never`?

<details>
<summary>answer</summary>

With `suspend_always`, the call allocates the frame, copies `rows` and `cols` into it, constructs the promise, obtains the `Generator`, and suspends at the initial suspend point: none of the loop body runs. With `suspend_never`, the body runs immediately until the first `co_yield`, so `current` already holds `(0,0)` when the caller receives the generator. Our `next()` resumes before reading, so the first `next()` would then skip to `(0,1)` and `(0,0)` would be lost. Eager start is a legitimate design (some task types use it), but the rest of the type has to be written for it; this is why the promise's suspend points and the wrapper's API must be designed together.

</details>
