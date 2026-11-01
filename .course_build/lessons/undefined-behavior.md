---
title: undefined behavior and the optimizer
standard: C++17
objective: tell undefined, unspecified, and implementation-defined behavior apart, and explain how the optimizer turns UB into deleted checks
prerequisites: integer-types, pointers-references
difficulty: 2
---

### the idea

a telemetry service guards a counter with `if (total + delta < total) reset();`. it works in debug builds. in release builds the reset never fires, the counter goes negative, and dashboards show nonsense. nobody touched the code; the optimizer read it more carefully than we did. undefined behavior is not "the hardware does something weird". it is a contract: you promise certain things never happen, and the compiler is entitled to generate code that is only correct if you kept that promise.

### understanding the concept

the standard describes three different kinds of looseness, and mixing them up leads to bad decisions:

| category | what the standard says | examples |
|---|---|---|
| implementation-defined | one of several outcomes; the implementation must document which | `sizeof(long)`, whether plain `char` is signed, the definition of `NULL`, right-shifting a negative `int` (until C++20) |
| unspecified | one of several outcomes; no documentation required, may vary call to call | order of evaluation of function arguments, whether identical string literals share storage, `<` on pointers to unrelated objects |
| undefined (UB) | no requirements at all | signed overflow, out-of-bounds access, use after free, reading an uninitialized `int`, data races |

implementation-defined behavior is portable *with a check* (a `static_assert` on `sizeof`, for example). unspecified behavior is safe as long as your program is correct for every allowed outcome. undefined behavior is never safe, and the standard explicitly places no requirement on an execution that contains it, *not even on operations before the undefined one*. ([[linkage-odr]]'s "ill-formed, no diagnostic required" is a fourth, compile-time cousin: the program is broken and nobody has to tell you.)

**why the optimizer makes UB dangerous.** optimizers transform code under the assumption that the program is valid. if signed overflow cannot happen, then `a + b < a` with `b > 0` is always false, and a loop counter `int i` that only increases can never wrap. if dereferencing a null pointer cannot happen, then a pointer that was dereferenced is non-null and a later null check is dead code. each step is a sound deduction from the rules; the result is that a bug can delete your safety checks.

### in code

**signed overflow: the check that is not there.**

```cpp ub
#include <climits>

bool will_overflow(int a, int b) {     // intended for b > 0
    return a + b < a;                  // BUG: relies on signed overflow (UB)
}

bool will_overflow_fixed(int a, int b) {
    return b > 0 && a > INT_MAX - b;   // decide before doing the arithmetic
}
```

GCC 12 at `-O2` compiled `will_overflow` to a single shift that tests the sign of `b`: it rewrote `a + b < a` as `b < 0`, which is exactly what the expression means when overflow is impossible. the same reasoning shows up in loops. `for (int i = 1; i > 0; i *= 2) ++count;` printed `31` at `-O0` in our test and ran forever at `-O2`, because "a positive `int` doubled stays positive" is true in every program without UB. if you need wraparound, use unsigned types (where it is defined, modulo 2^N); if you need detection, check first, or use your compiler's checked-arithmetic builtins (`__builtin_add_overflow` in GCC and Clang, a non-standard extension).

**a null check deleted because of an earlier dereference.**

```cpp ub
struct Device { int status; };

int read_status(const Device* d) {
    int s = d->status;     // BUG: dereference before the check
    if (!d) return -1;     // GCC -O2: removed, since d cannot be null here
    return s;
}
```

at `-O0` our build contained the comparison against zero; at `-O2` the whole function was one load and a return. this exact pattern caused a Linux kernel vulnerability in 2009 (the TUN driver), and the kernel has built with `-fno-delete-null-pointer-checks` ever since. the fix is ordinary: check, then dereference.

### in practice

because UB is invisible in testing until it is not, the defense is tooling in CI, not vigilance:

```sh
# compiler diagnostics on every build
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror ...

# a sanitizer job running the test suite (GCC or Clang)
g++ -std=c++17 -O1 -g -fno-omit-frame-pointer \
    -fsanitize=address,undefined -fno-sanitize-recover=undefined tests.cpp -o tests_asan

# data races need a separate build: ThreadSanitizer cannot be combined with ASan
g++ -std=c++17 -O1 -g -fsanitize=thread tests.cpp -o tests_tsan
```

sanitizers cost run time and memory (ASan's own documentation cites a typical slowdown of about 2x), so they live in test jobs, not release builds. sanitizers only see the paths your tests execute, which is one more argument for tests that exercise edge values.

### watch out for

**"it works on my machine" is the defining property of UB, not a defense against it.** a program with undefined behavior can produce the right answer in every test, then change behavior after a compiler upgrade, a new optimization level, or an unrelated edit that changes inlining. passing tests prove that the paths you ran did what you expected, on that build. they say nothing about what the program means.

two more misconceptions. `volatile` is for memory-mapped I/O and similar "every access is observable" cases; it makes nothing atomic and orders nothing between threads, so a race on a `volatile int` is still UB (atomics are [[atomics]]). and "it works on my machine" is the defining property of UB, not a defense against it.

### the takeaway

implementation-defined means "check the documentation", unspecified means "be correct for every outcome", and undefined means "the compiler assumes it never happens"; write code that never relies on UB, and let warnings and sanitizers find the places where you did by accident.

### optional challenge

classify each as well-defined, implementation-defined, unspecified, or undefined in C++17, and note any that changed in C++20.

1. `sizeof(int) == 4`
2. which of `f(a(), b())`'s arguments is evaluated first
3. `int x = INT_MAX; ++x;`
4. `signed char c = 200;` (with 8-bit `signed char`)
5. `int y = -8 >> 1;`
6. `int i = 0; i = i++;`

<details>
<summary>answer</summary>

1. implementation-defined. only minimum ranges are guaranteed; `static_assert` it if your code depends on it.
2. unspecified. each argument is fully evaluated before the next begins, but the order may differ between compilers or even call sites.
3. undefined: signed overflow.
4. implementation-defined in C++17 (converting an out-of-range value to a signed type). since C++20 it is defined as modulo 2^N, giving -56.
5. implementation-defined in C++17 (right shift of a negative value; GCC documents an arithmetic shift, giving -4). C++20 requires two's complement and defines it as an arithmetic shift.
6. well-defined since C++17: the right operand is sequenced before the assignment, so `i` ends up 0. in C++14 it was undefined.

</details>
