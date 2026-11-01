---
title: the usual suspects: aliasing, punning, and evaluation order
standard: C++17
objective: recognize the everyday patterns that cause undefined or unspecified behavior, and use the safe spelling of each
prerequisites: undefined-behavior
difficulty: 2
---

### the idea

most undefined behavior in production code comes from a handful of patterns that look completely ordinary: a cast that reinterprets a byte buffer as a struct, an index one past the end, an argument list with two calls that touch the same state. you do not need to memorize the standard's whole list. you need to recognize these patterns on sight and know the safe way to write each one.

### understanding the concept

**the usual suspects**, and what catches them:

| UB | typical form | practical defense |
|---|---|---|
| signed overflow | `INT_MAX + 1`, `a * b` on promoted `uint16_t` ([[integer-types]]) | check before computing; UBSan |
| out of bounds | `v[v.size()]`, pointer arithmetic past the end ([[pointers-references]]) | `.at()` in non-hot code, `-D_GLIBCXX_ASSERTIONS` (libstdc++), ASan |
| use after free / dangling | [[temporaries-dangling]]'s references to dead objects | ownership discipline ([[raii]], [[unique-ptr]]), ASan |
| uninitialized read | `int n; return n;` ([[initialization]]) | default member initializers, `-Wuninitialized`, MSan (Clang), Valgrind |
| strict aliasing | `*reinterpret_cast<std::uint32_t*>(&f)` | `std::memcpy`, C++20 `std::bit_cast` |
| data race | two threads, one non-atomic object, at least one writer | mutexes and atomics ([[data-races]], [[atomics]]), TSan |
| modifying a string literal | `const_cast<char*>("abc")[0] = 'x'` | do not cast away `const` from data you do not own |

the **strict aliasing rule** says you may access an object only through its own type (give or take signedness and cv-qualification) or through `char`, `unsigned char`, or `std::byte`. that lets the compiler assume a write through a `float*` cannot change an `int` it has cached in a register. `bits_bad` printed the right answer (`3f800000` for 1.0f) in our test, with a `-Wstrict-aliasing` warning at `-O2`. correct output today is not evidence of a correct program. `std::memcpy` of a few bytes is generally compiled to a register move by mainstream optimizers; check the generated code if it matters. `std::bit_cast` (C++20) does the same thing as an expression and is `constexpr`.

### in code

**type punning: three ways to read a float's bits** (the last one, commented out, needs C++20).

```cpp ub
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

### in practice

radar and telemetry code is full of the third pattern: a byte buffer arrives from a socket and gets cast to a header struct.

```cpp complete
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

the cast version "works" on x86, which tolerates misaligned loads, and then faults on an ARM controller or gets miscompiled after an unrelated inlining change. the `memcpy` version is correct everywhere (byte order and padding are still your job: those are implementation-defined layout questions, not UB).

### watch out for

**order of evaluation** is the area where folklore lags the standard. C++17 fixed several cases: in `a << b`, `a >> b`, `a[b]`, `a.b`, and `a->b` the left side is evaluated first, and in `a = b` (and `a += b`) the right side is evaluated first. so `std::cout << next() << next();` is now left to right, and `i = i++ + 1;` is well defined (it sets `i` to 1 when `i` starts at 0). GCC 12 still emits `-Wsequence-point` for that line even in C++17 mode, a stale warning worth knowing about.

function arguments did not get an order. in `log_pair(next_id(), next_id())` the two calls are indeterminately sequenced: each runs completely before the other starts (which, since C++17, makes `f(i++, i++)` unspecified rather than undefined), but which one goes first is unspecified. our GCC build printed `2 1`. any code whose result depends on that order is a portability bug; give the values names on separate lines.

### the takeaway

reinterpret bytes with `std::memcpy` or `std::bit_cast`, never through a cast pointer; never let a result depend on the order in which function arguments are evaluated; and for every other suspect, know which sanitizer catches it.

### optional challenge

classify each line as well-defined, unspecified, or undefined. `v` is a `std::vector<int>` holding three elements and `next()` returns an increasing counter.

```cpp
int a = v[v.size()];                                      // (1)
float f = 1.0f;
unsigned char b = *reinterpret_cast<unsigned char*>(&f);  // (2)
std::printf("%d %d\n", next(), next());                   // (3)
int* p = new int[4];
delete p;                                                 // (4)
```

<details>
<summary>answer</summary>

1. undefined: `operator[]` does not check bounds, and index 3 is past the end. `v.at(v.size())` would throw `std::out_of_range` instead.
2. well-defined: any object may be read through `char`, `unsigned char`, or `std::byte`. *which* byte you get depends on the platform's byte order, which is implementation-defined, but the access itself is fine.
3. unspecified: the two calls happen in some order, each completely before the other, so the program may print `1 2` or `2 1`, but nothing worse.
4. undefined: memory from `new[]` must be released with `delete[]`. this "works" on many allocators for `int`, and corrupts the heap for types with destructors.

</details>
