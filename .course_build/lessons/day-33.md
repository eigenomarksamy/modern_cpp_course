<a id="day-33"></a>

## day 33: compile-time programming in C++20

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 03, 23, 29

### the idea

A radar firmware computes its CRC-32 lookup table in a global constructor: `static CrcTable g_crc;`. Months later someone adds a static `PacketLogger` in another translation unit that checksums a startup banner. On one build configuration every checksum at startup is wrong, because the logger's constructor runs before the table's. That is the static initialization order fiasco from day 03, and the fix is not to order the constructors more cleverly. It is to make the table exist before any constructor runs at all: compute it at compile time.

C++20 gives you three keywords for this, and they make three different promises. `constexpr` says "can run at compile time". `consteval` says "must run at compile time". `constinit` says "this variable is initialized at compile time, but it is not a constant". Mixing them up is the most common mistake in this area.

### understanding the concept

**`constexpr` functions** may be evaluated during constant evaluation, when their arguments are constants and the context requires a constant (a `constexpr` variable, an array bound, a template argument, `static_assert`). Called with runtime values, they are ordinary functions. Each standard widened what they may contain: C++11 allowed a single `return`, C++14 loops and local variables, C++17 lambdas. C++20 adds:

- `try` blocks (but actually evaluating a `throw` during constant evaluation is a compile error),
- virtual function calls, `dynamic_cast`, and `typeid`,
- changing the active member of a union, and uninitialized local variables (reading one is still an error),
- **transient dynamic allocation**: `new`/`delete`, and therefore `std::vector` and `std::string` (library support for `constexpr` `std::vector` and `std::string`: libstdc++ in GCC 12, libc++ 15, MSVC 19.29). Memory allocated during a constant evaluation must be freed within that same evaluation. You can build a vector at compile time and return its size or copy it into a `std::array`; you cannot have a `constexpr std::vector` variable.

**`consteval`** declares an *immediate function*: every call must be a constant expression, or the program is ill-formed. That turns "this should be folded" into "this is checked". Because a `throw` reached during constant evaluation is an error, a `consteval` function that throws on bad input becomes a compile-time validator. That is exactly how C++20 checks `std::format` strings (day 34): `std::format_string` has a `consteval` constructor that parses the literal.

**`constinit`** applies to variables with static or thread storage duration. It asserts that the variable is constant-initialized (initialized before any dynamic initialization runs), and makes it an error if it is not. The variable stays mutable. It answers day 03's fiasco for globals that must be mutable: a `constinit` counter or pointer is valid before any constructor in any translation unit runs.

**`std::is_constant_evaluated()`** (`<type_traits>`) returns `true` when called during constant evaluation, so a `constexpr` function can use a portable loop at compile time and an intrinsic or `memcpy` at runtime. Use it with plain `if`, never `if constexpr` (see "watch out for"). C++23's `if consteval` is a cleaner spelling; it is not C++20.

### in code

**A compile-time table, tested by the compiler.**

```cpp
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

The same `crc32` serves runtime packets and compile-time tests. The `static_assert` is a unit test that runs on every build and cannot be skipped.

**Transient allocation.** C++20 lets constant evaluation use the heap, as long as nothing escapes:

```cpp
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

**`consteval` and `constinit`.**

```cpp
#include <cstdint>
#include <numbers>

consteval double deg_to_rad(double deg) { return deg * std::numbers::pi / 180.0; }

consteval std::uint8_t can_channel(int ch) {
    if (ch < 0 || ch > 15) throw "CAN channel out of range";   // compile-time diagnostic
    return static_cast<std::uint8_t>(ch);
}

constexpr double joint_limit = deg_to_rad(170.0);   // 2.967060
constexpr auto steering_bus  = can_channel(3);
// can_channel(16);    error: expression '<throw-expression>' is not a constant expression
// deg_to_rad(runtime_angle);  error: the value of 'runtime_angle' is not usable in a constant expression

int compute_default();
constinit int retry_budget = 5;                    // OK: mutable, initialized before any constructor
// constinit int bad = compute_default();
// error: 'constinit' variable 'bad' does not have a constant initializer
```

`deg_to_rad` as `consteval` is a design choice: it says "this conversion is for constants in source code", and a runtime angle must go through a different (runtime) function. That keeps an accidental per-cycle conversion out of a control loop, but it also means you cannot reuse it at runtime. Choose `constexpr` when both uses are legitimate.

C++20 also allows class types as non-type template parameters, if they are *structural* (public members, no `mutable`, all members structural). A small `fixed_string` lets a string literal become part of a type, so `Counter<"dropped_frames">` and `Counter<"crc_errors">` are distinct types with their own static storage. Libraries use this for compile-time format strings, units, and register maps.

### in practice

In embedded radar firmware the CRC table above lives in read-only memory (1 KiB), costs nothing at boot, and cannot be observed half-initialized. The alternative, computing it at startup into RAM, costs a few thousand simple operations once at boot and 1 KiB of RAM instead of flash. On a microcontroller with scarce RAM and plenty of flash, compile-time wins; on a desktop it hardly matters, and the real benefit is removing an initialization-order dependency.

The costs are real, though. Constant evaluation is interpreted by the compiler, and compilers impose limits. As a data point on the machine used to check this course: `static_assert(count_primes(100000) == 9592)` hit GCC 12's default operation limit ("'constexpr' evaluation operation count exceeds limit of 33554432"), and with `-fconstexpr-ops-limit` raised it added about 7 seconds to the build, while the same call at runtime finished within process startup time. Anything big generated in a header is paid for by every translation unit that includes it; put it in one `.cpp` file. You cannot step through constant evaluation in a debugger, so keep `constexpr` functions callable at runtime and unit test them there too. And a large generated table makes the binary bigger. "Move it to compile time" is a tradeoff between build time, binary size, startup time, and debuggability, not a free win.

### watch out for

**`constexpr` on a function is permission, not a command.** A local `const auto t = make_crc_table();` may well run at runtime: only a context that requires a constant forces evaluation. If you need the guarantee, use a `constexpr` (or `constinit`) variable, or a `consteval` function.

**`if constexpr (std::is_constant_evaluated())` is always true**, because the condition of `if constexpr` is itself a constant evaluation. Your runtime branch becomes dead code. GCC 12 warns: "'std::is_constant_evaluated' always evaluates to true in 'if constexpr'". Use a plain `if`.

**Compiler extensions leak in.** GCC accepts `constexpr double s = std::sin(0.5);` even with `-pedantic`, because it constant-folds its math builtins. `<cmath>` functions are not `constexpr` in C++20, and other compilers may reject it. Later standards make more of `<cmath>` `constexpr`; until you target one, compute such tables with your own `constexpr` series or generate them offline.

### the takeaway

`constexpr` means "may run at compile time", `consteval` means "must", and `constinit` means "initialized at compile time, mutable afterwards". Use compile-time evaluation to remove startup ordering problems and to turn checks into build errors, and weigh it against build time, binary size, and debuggability.

### optional challenge

```cpp
constexpr int sq(int x) { return x * x; }
int g = sq(4);                 // namespace scope

int main() {
    int l = sq(4);             // local
}
```

Is `g` guaranteed to be initialized at compile time? Is `l`? What changes if you write `constinit int g = sq(4);`?

<details>
<summary>answer</summary>

`g` is guaranteed: a variable with static storage duration whose initializer is a constant expression undergoes *constant initialization*, which happens before any dynamic initialization. That is a language rule, not an optimization. `l` is not guaranteed: it is an ordinary local, and whether `sq(4)` is folded is up to the compiler. (GCC 12 happens to fold it even at `-O0`; that is an implementation choice, not a guarantee.)

`constinit` does not change the behavior of `g`; it adds a check. If someone later changes `sq` so it is no longer `constexpr`, plain `int g = sq(4);` silently becomes dynamic initialization, and the day 03 ordering problem is back. With `constinit`, that change is a compile error.

</details>
