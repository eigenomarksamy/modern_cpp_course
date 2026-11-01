<a id="day-02"></a>

## day 02: types and the many faces of initialization

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** [day 01](#day-01)

### the idea

A colleague modernizes a radar module and changes `std::vector<float> gains(8, 0.5f);` to `std::vector<float> gains{8, 0.5f};` because "braces are the modern way". The code compiles. The vector now has two elements, 8.0 and 0.5, and the beamformer reads past the gains it expected. C++ has roughly half a dozen ways to initialize an object, they differ in real ways, and the one advertised as "uniform" is not uniform at all.

### understanding the concept

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

### in code

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

### in practice

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

### watch out for

Value-initialization only zeroes members when the compiler supplies the constructor. A user-provided default constructor that forgets a member defeats `{}`:

```cpp
struct Raw    { double x, y; };                 // no constructor
struct Sensor { Sensor() {} int id; };          // user-provided, does not set id

Raw r{};       // r.x and r.y are 0.0
Sensor s{};    // s.id is indeterminate: the constructor runs and that is all
Raw r2;        // r2.x is indeterminate (automatic storage)
```

GCC flagged a read of `s.id` with `-Wuninitialized` at `-O2`, but such warnings depend on optimization level and inlining, so do not rely on them. The robust habit is a default member initializer on every scalar member (`int id = 0;`); then every form of initialization, including plain `Sensor s;`, produces a defined value.

### the takeaway

Use braces for objects you build from values (they reject narrowing), parentheses when calling a sizing constructor on a container, default member initializers on every scalar, and fixed-width types wherever the width is part of the contract.

### optional challenge

Assuming a typical platform with a 32-bit `int`, what does this function return for `a = b = 65535`, and is the result even defined?

```cpp
#include <cstdint>
std::uint32_t area(std::uint16_t a, std::uint16_t b) { return a * b; }
```

<details>
<summary>answer</summary>

Both operands are promoted to `int` (signed, 32 bits) before the multiplication, because `int` can represent every `std::uint16_t` value. 65535 * 65535 = 4,294,836,225, which exceeds `INT_MAX` (2,147,483,647). Signed overflow is undefined behavior, so the function has no defined result for those inputs, even though every type in the signature is unsigned. The fix is to convert before multiplying: `return std::uint32_t{a} * b;`, which makes the arithmetic happen in `std::uint32_t` (the other operand is converted to unsigned) where wraparound is defined and, here, there is no overflow at all.

</details>
