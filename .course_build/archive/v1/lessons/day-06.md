<a id="day-06"></a>

## day 06: undefined behavior and other things the standard won't promise

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 01 to 05

### the idea

A telemetry service guards a counter with `if (total + delta < total) reset();`. It works in debug builds. In release builds the reset never fires, the counter goes negative, and dashboards show nonsense. Nobody touched the code; the optimizer read it more carefully than we did. Undefined behavior is not "the hardware does something weird". It is a contract: you promise certain things never happen, and the compiler is entitled to generate code that is only correct if you kept that promise.

### understanding the concept

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

### in code

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

### in practice

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

### watch out for

**Order of evaluation** is the area where folklore lags the standard. C++17 fixed several cases: in `a << b`, `a >> b`, `a[b]`, `a.b`, and `a->b` the left side is evaluated first, and in `a = b` (and `a += b`) the right side is evaluated first. So `std::cout << next() << next();` is now left to right, and `i = i++ + 1;` is well defined (it sets `i` to 1 when `i` starts at 0). GCC 12 still emits `-Wsequence-point` for that line even in C++17 mode, a stale warning worth knowing about.

Function arguments did not get an order. In `log_pair(next_id(), next_id())` the two calls are indeterminately sequenced: each runs completely before the other starts (which, since C++17, makes `f(i++, i++)` unspecified rather than undefined), but which one goes first is unspecified. Our GCC build printed `2 1`. Any code whose result depends on that order is a portability bug; give the values names on separate lines.

Two more misconceptions. `volatile` is for memory-mapped I/O and similar "every access is observable" cases; it makes nothing atomic and orders nothing between threads, so a race on a `volatile int` is still UB (atomics are day 40). And "it works on my machine" is the defining property of UB, not a defense against it.

### the takeaway

Implementation-defined means "check the documentation", unspecified means "be correct for every outcome", and undefined means "the compiler assumes it never happens"; write code that never relies on UB, and let warnings and sanitizers find the places where you did by accident.

### optional challenge

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
