---
title: the many faces of initialization
standard: C++17
objective: choose the initialization syntax that says what you mean, and know which forms leave a value indeterminate
prerequisites: build-pipeline
difficulty: 2
---

### the idea

a colleague modernizes a radar module and changes `std::vector<float> gains(8, 0.5f);` to `std::vector<float> gains{8, 0.5f};` because "braces are the modern way". the code compiles. the vector now has two elements, 8.0 and 0.5, and the beamformer reads past the gains it expected. C++ has roughly half a dozen ways to initialize an object, they differ in real ways, and the one advertised as "uniform" is not uniform at all.

### understanding the concept

the forms, from least to most initialized:

| syntax | name | what happens |
|---|---|---|
| `T x;` | default-initialization | class types: default constructor runs. scalars and aggregates of scalars with automatic storage: **indeterminate** value |
| `T x{};` or `T()` | value-initialization | scalars: zero. class with a user-provided default constructor: that constructor runs. otherwise: zeroed, then any non-trivial default construction |
| `T x(a);` | direct-initialization | all constructors considered, including `explicit` ones |
| `T x = a;` | copy-initialization | `explicit` constructors are not considered |
| `T x{a};` / `T x = {a};` | direct/copy-list-initialization | as above, but narrowing is rejected and `std::initializer_list` constructors win |
| `S s{1, 2.0};` | aggregate initialization | members initialized in declaration order; omitted members from their default member initializer, otherwise as if from `{}` |

objects with **static or thread storage duration** are different: they are zero-initialized before anything else happens, so a global `int counter;` is reliably 0. only automatic (and dynamically allocated) scalars start indeterminate, and reading an indeterminate value is undefined behavior ([[undefined-behavior]] will show why the optimizer makes that worse than "you get garbage").

**list-initialization has two special rules.** first, it rejects *narrowing* conversions: floating to integer, `double` to `float` (unless the source is a constant that fits), and integer to a type that cannot represent the value. second, if the class has a constructor taking `std::initializer_list`, a non-empty braced list strongly prefers it over every other constructor, even when another one is a better match. empty braces are the exception: `{}` means the default constructor.

**`auto` with braces** changed in C++17 (compilers also apply the fix in C++14 mode): `auto a{1};` is `int`, `auto b = {1};` is `std::initializer_list<int>`, and `auto c{1, 2};` is ill-formed. the `=` changes the meaning, which is reason enough to write `auto x = 1;` and keep braces for objects.

### in code

**predict the output.** cover the comments and work out each line.

```cpp complete
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

the rule for library types: if the class has an `initializer_list` constructor (containers, `std::string`), braces mean "these are the elements". use parentheses when you mean "call the sizing constructor".

**braces as a narrowing guard, and the most vexing parse.**

```cpp fails
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

the standard makes narrowing in list-initialization ill-formed. GCC 12 reports constants that do not fit (`70000`, `char c{300}`) as errors, but reports the non-constant `int b{measured}` only as a `-Wnarrowing` warning; Clang rejects both. add `-Werror=narrowing` (or `-pedantic-errors`) to get the standard's behavior on GCC. the vexing parse comes from the grammar rule "anything that can be a declaration is a declaration"; GCC 11 and later warn with `-Wvexing-parse`, and braces remove the ambiguity entirely.

### in practice

configuration structs are where initialization style pays off. a telemetry packet header or a sensor configuration as an aggregate with default member initializers gives you three properties at once: every field has a defined value even when the caller forgets one, brace initialization rejects narrowing such as a `double` squeezed into a `std::uint16_t` field, and the type stays trivially copyable for serialization:

```cpp
struct ImuConfig {
    std::uint16_t rate_hz = 200;
    float accel_range_g = 8.0f;
    bool  enable_fifo = true;
};

ImuConfig cfg{400};   // rate_hz = 400, the rest keep their defaults
```

the weakness is that positional aggregate initialization ties every call site to member order; inserting a field in the middle silently shifts meanings when the types are compatible. C++20 designated initializers ([[cpp20-small-features]]) fix that. choosing an aggregate over a class with a constructor is a design decision: an aggregate says "this is plain data with no invariant", which is exactly right for configuration and wrong for anything that must validate its fields.

### watch out for

value-initialization only zeroes members when the compiler supplies the constructor. a user-provided default constructor that forgets a member defeats `{}`:

```cpp complete
struct Raw    { double x, y; };                 // no constructor
struct Sensor { Sensor() {} int id; };          // user-provided, does not set id

Raw r{};       // r.x and r.y are 0.0
Sensor s{};    // s.id is indeterminate: the constructor runs and that is all
Raw r2;        // r2.x is indeterminate (automatic storage)
```

GCC flagged a read of `s.id` with `-Wuninitialized` at `-O2`, but such warnings depend on optimization level and inlining, so do not rely on them. the robust habit is a default member initializer on every scalar member (`int id = 0;`); then every form of initialization, including plain `Sensor s;`, produces a defined value.

### the takeaway

use braces for objects you build from values (they reject narrowing), parentheses when you call a sizing constructor on a container, and a default member initializer on every scalar member.

### optional challenge

what does each object hold? assume the code is inside a function, except where marked.

```cpp complete
struct Gains { float kp = 1.0f; float ki; float kd = 0.0f; };

Gains a;          // (1)
Gains b{};        // (2)
Gains c{2.0f};    // (3)
static Gains d;   // (4)
```

<details>
<summary>answer</summary>

1. `kp` is 1 and `kd` is 0 from their default member initializers, but `ki` is indeterminate: default-initialization of an automatic aggregate leaves scalars without an initializer alone, and reading `a.ki` is undefined behavior.
2. aggregate initialization from an empty list: members with a default member initializer use it, and the rest are initialized as if from `{}`, so `ki` is 0. result: 1, 0, 0.
3. the first member comes from the list (`kp` is 2), the rest as in (2): 2, 0, 0.
4. static storage is zero-initialized before anything else, then default-initialized: 1, 0, 0. the same declaration gives a defined `ki` here and an indeterminate one in (1), which is exactly why "add `= 0.0f` to `ki`" is the robust fix.

</details>

### going deeper

#### what exactly counts as an aggregate

an aggregate (C++17) is an array or a class with no user-provided, `explicit`, or inherited constructors, no private or protected non-static data members, no virtual functions, and no virtual, private, or protected bases. C++20 tightens "user-provided" to "user-declared", so a struct with `S() = default;` stops being an aggregate.
