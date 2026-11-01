---
title: constexpr in C++20: computing at compile time
standard: C++20
objective: write constexpr functions that build tables and use transient allocation, force and test their evaluation, and weigh compile-time work against its costs
prerequisites: storage-duration, if-constexpr, concepts
difficulty: 2
---

### the idea

a radar firmware computes its CRC-32 lookup table in a global constructor: `static CrcTable g_crc;`. months later someone adds a static `PacketLogger` in another translation unit that checksums a startup banner. on one build configuration every checksum at startup is wrong, because the logger's constructor runs before the table's. that is the static initialization order fiasco from [[storage-duration]], and the fix is not to order the constructors more cleverly. it is to make the table exist before any constructor runs at all: compute it at compile time.

### understanding the concept

**`constexpr` functions** may be evaluated during constant evaluation, when their arguments are constants and the context requires a constant (a `constexpr` variable, an array bound, a template argument, `static_assert`). called with runtime values, they are ordinary functions. each standard widened what they may contain: C++11 allowed a single `return`, C++14 loops and local variables, C++17 lambdas. C++20 adds:

- `try` blocks (but actually evaluating a `throw` during constant evaluation is a compile error),
- virtual function calls, `dynamic_cast`, and `typeid`,
- changing the active member of a union, and uninitialized local variables (reading one is still an error),
- **transient dynamic allocation**: `new`/`delete`, and therefore `std::vector` and `std::string` (library support for `constexpr` `std::vector` and `std::string`: libstdc++ in GCC 12, libc++ 15, MSVC 19.29). memory allocated during a constant evaluation must be freed within that same evaluation. you can build a vector at compile time and return its size or copy it into a `std::array`; you cannot have a `constexpr std::vector` variable.

### in code

**a compile-time table, tested by the compiler.**

```cpp complete
#include <array>
#include <cstdint>
#include <string_view>

constexpr std::array<std::uint32_t, 256> make_crc_table() {
    std::array<std::uint32_t, 256> table{};
    for (std::uint32_t i = 0; i < 256; ++i) {
        std::uint32_t c = i;
        for (int k = 0; k < 8; ++k)
            c = (c & 1u) ? 0xEDB88320u ^ (c >> 1) : c >> 1;
        table[i] = c;
    }
    return table;
}
inline constexpr auto crc_table = make_crc_table();   // no constructor, no ordering

constexpr std::uint32_t crc32(std::string_view data) {
    std::uint32_t c = 0xFFFFFFFFu;
    for (unsigned char b : data)
        c = crc_table[(c ^ b) & 0xFFu] ^ (c >> 8);
    return c ^ 0xFFFFFFFFu;
}
static_assert(crc32("123456789") == 0xCBF43926u);   // the standard CRC-32 check value
```

the same `crc32` serves runtime packets and compile-time tests. the `static_assert` is a unit test that runs on every build and cannot be skipped.

**transient allocation.** C++20 lets constant evaluation use the heap, as long as nothing escapes:

```cpp complete
#include <vector>

constexpr int count_primes(int n) {
    std::vector<bool> composite(n + 1, false);   // allocated and freed during evaluation
    int count = 0;
    for (int i = 2; i <= n; ++i) {
        if (composite[i]) continue;
        ++count;
        for (int j = 2 * i; j <= n; j += i) composite[j] = true;
    }
    return count;
}
static_assert(count_primes(100) == 25);

// constexpr std::vector<int> v{1, 2, 3};
// error: ... is not a constant expression because it refers to a result of 'operator new'
```

### in practice

in embedded radar firmware the CRC table above lives in read-only memory (1 KiB), costs nothing at boot, and cannot be observed half-initialized. the alternative, computing it at startup into RAM, costs a few thousand simple operations once at boot and 1 KiB of RAM instead of flash. on a microcontroller with scarce RAM and plenty of flash, compile-time wins; on a desktop it hardly matters, and the real benefit is removing an initialization-order dependency.

the costs are real, though. constant evaluation is interpreted by the compiler, and compilers impose limits. as a data point on the machine used to check this course: `static_assert(count_primes(100000) == 9592)` hit GCC 12's default operation limit ("'constexpr' evaluation operation count exceeds limit of 33554432"), and with `-fconstexpr-ops-limit` raised it added about 7 seconds to the build, while the same call at runtime finished within process startup time. anything big generated in a header is paid for by every translation unit that includes it; put it in one `.cpp` file. you cannot step through constant evaluation in a debugger, so keep `constexpr` functions callable at runtime and unit test them there too. and a large generated table makes the binary bigger. "move it to compile time" is a tradeoff between build time, binary size, startup time, and debuggability, not a free win.

### watch out for

**`constexpr` on a function is permission, not a command.** a local `const auto t = make_crc_table();` may well run at runtime: only a context that requires a constant forces evaluation. if you need the guarantee, use a `constexpr` (or `constinit`) variable, or a `consteval` function.

**compiler extensions leak in.** GCC accepts `constexpr double s = std::sin(0.5);` even with `-pedantic`, because it constant-folds its math builtins. `<cmath>` functions are not `constexpr` in C++20, and other compilers may reject it. later standards make more of `<cmath>` `constexpr`; until you target one, compute such tables with your own `constexpr` series or generate them offline.

### the takeaway

a `constexpr` function may run at compile time and still works at run time; force evaluation with a `constexpr` variable or `static_assert`, use that as a free unit test, and treat moving work to compile time as a tradeoff, not a free win.

### optional challenge

which of these are guaranteed to evaluate `make_crc_table()` at compile time?

```cpp
constexpr auto a = make_crc_table();                 // (1) namespace scope
void f() {
    const auto b = make_crc_table();                 // (2)
    static const auto c = make_crc_table();          // (3)
    static_assert(make_crc_table()[1] != 0);         // (4)
}
```

<details>
<summary>answer</summary>

(1), (3), and (4). a `constexpr` variable (1) must be initialized by a constant expression. a `static` local (3) has static storage duration, and a static variable whose initializer is a constant expression is *constant-initialized*, which is a language guarantee rather than an optimization. a `static_assert` (4) is a context that requires a constant. (2) is an ordinary local: the compiler may fold the call, and at higher optimization levels it probably will, but nothing requires it.

</details>
