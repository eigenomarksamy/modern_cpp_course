<a id="day-03"></a>

## day 03: scope, storage duration, and object lifetime

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days [01](#day-01), [02](#day-02)

### the idea

"The variable is still in scope, so the object is still alive." That sentence is behind a surprising share of dangling-reference bugs. Scope is a compile-time property of a *name*: the region of source text where the name can be used. Lifetime is a run-time property of an *object*: the interval during which it exists and may be accessed. They often coincide, which is why we conflate them. A reference can be perfectly in scope while the object it names is long gone, and a function-local `static` is out of scope almost everywhere while its object lives until the program exits.

### understanding the concept

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

### in code

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

### in practice

Plugin registries in robotics and tooling frameworks are where the fiasco lives in the wild. Each driver file contains a static registrar, something like `static const bool registered = SensorRegistry::add("velodyne", &make_velodyne);`, so that linking a driver is enough to make it available. Those registrars run during dynamic initialization of their own translation units, in unspecified order. If the registry is a global `std::map`, a registrar can insert into a map whose constructor has not run yet. The standard pattern is a function-local static: `static SensorRegistry& instance() { static SensorRegistry r; return r; }`.

The mirror image happens at shutdown. A static object whose destructor logs through a global logger may run after the logger has been destroyed. A common, deliberate escape hatch is a "leaky" singleton, `static Logger* l = new Logger;`, which is never destroyed; the operating system reclaims the memory, at the price of no destructor running (so flush explicitly). Global mutable state is a coupling problem before it is an ordering problem: every object with static storage that reads another is a hidden dependency, and fewer globals means fewer of these puzzles.

### watch out for

Lifetime extension does not pass through function calls, and the classic victim is a standard algorithm returning a reference:

```cpp
#include <algorithm>

int lo();
int hi();

const int& m = std::max(lo(), hi());   // BUG: dangles
int v = std::max(lo(), hi());          // fine: copied before the ';'
```

`std::max` takes `const int&` parameters and returns one of them. The two temporaries are bound to its parameters, so they live only until the end of the full-expression, and `m` is left referring to a dead temporary. In our test at `-O2`, GCC printed `0` for `m` (and, by luck, warned about an uninitialized read). GCC 13 added `-Wdangling-reference` for this pattern; GCC 12 has nothing specific. The defense is a habit: bind function results by value unless you know the function returns a reference to something that outlives your reference.

### the takeaway

Ask "who owns this object and when does it die?" rather than "is this name in scope?"; temporaries die at the `;` unless bound directly to a local reference, and anything shared between translation units at startup belongs behind a function-local static.

### optional challenge

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
