---
title: storage duration and object lifetime
standard: C++17
objective: separate a name's scope from an object's lifetime, and predict construction and destruction order for every storage duration
prerequisites: initialization
difficulty: 2
---

### the idea

"the variable is still in scope, so the object is still alive." that sentence is behind a surprising share of dangling-reference bugs. scope is a compile-time property of a *name*: the region of source text where the name can be used. lifetime is a run-time property of an *object*: the interval during which it exists and may be accessed. they often coincide, which is why we conflate them. a reference can be perfectly in scope while the object it names is long gone, and a function-local `static` is out of scope almost everywhere while its object lives until the program exits.

### understanding the concept

every object has a **storage duration**, which bounds how long its storage exists:

| storage duration | objects | storage lasts |
|---|---|---|
| automatic | block-scope locals, parameters | until the enclosing block exits |
| static | namespace-scope variables, `static` locals, `static` data members | the whole program |
| thread | `thread_local` variables | the lifetime of each thread (one object per thread) |
| dynamic | objects from `new` (and allocator-based containers) | until you `delete` them |

temporaries are a fifth case: a temporary object is destroyed at the end of the **full-expression** that created it, which in practice usually means at the `;`.

an object's **lifetime** begins when its storage is obtained and its initialization is complete, and ends when its destructor call starts (or, for types with trivial destructors, when its storage is released or reused). touching an object outside its lifetime through a pointer or reference is undefined behavior, even if the bytes are still there and still look right.

**static initialization.** objects with static storage duration are first zero-initialized or constant-initialized (no code runs; the values are in the binary). anything else is *dynamic* initialization, which runs before `main` (strictly, before first use of something in that translation unit, but mainstream implementations do it at startup). within one translation unit, dynamic initialization follows definition order. across translation units, the order is unspecified. that gap is the **static initialization order fiasco**: if a global's initializer reads a global from another file, it may read an object whose lifetime has not begun.

a **function-local static** fixes this: it is initialized the first time control passes through its declaration, and since C++11 that initialization is thread-safe (concurrent callers wait for it to finish). destruction runs in reverse order of construction completion, for locals and statics alike.

### in code

**predict the output.** construction and destruction across all the durations above:

```cpp complete
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

note that `-static` comes after `-a` but before `-global`: statics die after `main` returns, in reverse order of construction, and `once` finished constructing after `global`.

`ext` survives its `;` because a temporary bound directly to a local `const&` lives as long as the reference; [[temporaries-dangling]] covers exactly when that rule applies and when it does not.

**the static initialization order fiasco and its fix.**

```cpp external
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

on our MinGW build, one link order printed `[radar/tracks]` and the other printed `[tracks]`: `g_prefix` was read while its storage was still only zero-initialized. that output is luck, not a guarantee; reading an object before its lifetime begins is undefined behavior and could as easily crash. the fixed version printed `[radar/tracks]` in both orders. if the value is a compile-time constant, an even better fix is to make it one: `inline constexpr std::string_view kPrefix = "radar/";` is constant-initialized and has no order at all (C++20 adds `constinit` to require constant initialization of a non-`const` variable).

### in practice

plugin registries in robotics and tooling frameworks are where the fiasco lives in the wild. each driver file contains a static registrar, something like `static const bool registered = SensorRegistry::add("velodyne", &make_velodyne);`, so that linking a driver is enough to make it available. those registrars run during dynamic initialization of their own translation units, in unspecified order. if the registry is a global `std::map`, a registrar can insert into a map whose constructor has not run yet. the standard pattern is a function-local static: `static SensorRegistry& instance() { static SensorRegistry r; return r; }`.

### watch out for

**thread-safe initialization is not thread-safe use.** the function-local static fix makes construction safe when several threads call `instance()` at once. it says nothing about what happens afterwards:

```cpp complete
#include <vector>

std::vector<int>& scratch() {
    static std::vector<int> buffer;   // constructed once, safely
    return buffer;                    // BUG if two threads use it: a data race
}
```

a static local is one object shared by every call on every thread, which is a global with better manners about initialization. when it is mutable, it still needs a mutex or a `thread_local` instead of `static`.

### the takeaway

ask "who owns this object and when does it die?" rather than "is this name in scope?"; objects die in reverse order of construction, and anything shared between translation units at startup belongs behind a function-local static or a `constexpr` constant.

### optional challenge

`log()` and `registry()` each return a function-local static. the registry's destructor writes a final message through `log()`. is shutdown safe if the program first calls `registry()` and only later calls `log()`? what if the registry's constructor calls `log()`?

<details>
<summary>answer</summary>

statics are destroyed in reverse order of the *completion* of their construction. in the first scenario the registry finishes constructing first and the logger second, so the logger is destroyed first, and the registry's destructor then uses a dead logger: undefined behavior that typically shows up as a crash or lost output at exit.

if the registry's constructor calls `log()`, the logger finishes constructing *before* the registry does (it completes inside the registry's constructor), so it is destroyed *after* the registry. touching a dependency in your constructor is the standard trick for making the shutdown order follow the dependency order.

</details>

### going deeper

#### shutdown order and leaky singletons

the mirror image happens at shutdown. a static object whose destructor logs through a global logger may run after the logger has been destroyed. a common, deliberate escape hatch is a "leaky" singleton, `static Logger* l = new Logger;`, which is never destroyed; the operating system reclaims the memory, at the price of no destructor running (so flush explicitly). global mutable state is a coupling problem before it is an ordering problem: every object with static storage that reads another is a hidden dependency, and fewer globals means fewer of these puzzles.
