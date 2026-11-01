---
title: integer types, promotions, and conversions
standard: C++17
objective: predict the type and value of mixed integer arithmetic, and choose integer types whose width and signedness match the contract
prerequisites: initialization
difficulty: 2
---

### the idea

`readings.size() - 1` is not -1 when `readings` is empty. `std::uint8_t id = 65;` prints as `A`. multiplying two `std::uint16_t` values can be undefined behavior even though every type in sight is unsigned. integer arithmetic in C++ happens in types you never wrote, converts signed values to unsigned without asking, and the width of `long` depends on the operating system. none of it is hard, but none of it is what intuition suggests.

### understanding the concept

**types and sizes.** `sizeof(char)` is 1 by definition; everything else is implementation-defined within minimums (`int` at least 16 bits, `long` at least 32, `long long` at least 64). `long` is 64 bits on x86-64 Linux and 32 bits on Windows, including MinGW; our test machine printed `sizeof(long) == 4`. when the width matters (wire formats, registers, file headers), use `<cstdint>`: `std::int32_t`, `std::uint64_t`. the exact-width types are technically optional but exist on every mainstream platform; `std::int_least32_t` and `std::int_fast32_t` always exist.

**promotions and conversions.** arithmetic never happens in types narrower than `int`: `char`, `short`, `std::uint8_t`, and `std::uint16_t` are promoted to `int` first. when a signed and an unsigned operand of the same rank meet, the *signed one is converted to unsigned*. that rule produces most of the surprises.

the full set of "usual arithmetic conversions" is longer, but three outcomes cover nearly every real case:

- both operands are promoted to at least `int`, then the narrower one is converted to the wider type;
- if one operand is unsigned and the other is a signed type of the same or lower rank, the signed one becomes unsigned (`-1 < 1u` is false);
- if the signed type can represent every value of the unsigned one (for example `long long` and `unsigned int` on a typical 64-bit platform), the unsigned one becomes signed instead.

what happens when a result does not fit depends on the signedness. unsigned arithmetic wraps modulo 2^N by definition. signed overflow is undefined behavior (the optimizer assumes it never happens, which [[undefined-behavior]] explores). converting an out-of-range value *to* a signed type was implementation-defined until C++20, which made it modular.

### in code

**integer promotion and signed/unsigned comparison.**

```cpp complete
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

`-Wall` includes `-Wsign-compare` in C++ and flags the `i < u` line. unsigned arithmetic wraps modulo 2^N by definition, so `size() - 1` is not undefined; it is simply a huge number, and a loop `for (std::size_t k = 0; k <= v.size() - 1; ++k)` on an empty vector runs off the end. C++20 adds `std::cmp_less` and friends in `<utility>` for comparisons that are correct across signedness.

### in practice

wire formats are where the width and signedness of every field is part of the contract. decoding a 16-bit signed range-rate field from a radar packet, the arithmetic happens in `int`, so the result has to be converted back explicitly:

```cpp complete
#include <cstdint>

std::int16_t decode_i16(const std::uint8_t* p) {
    // p[0] << 8 is computed in int; the cast says "these 16 bits are a signed value"
    return static_cast<std::int16_t>((p[0] << 8) | p[1]);
}
```

before C++20 that final conversion of a value above 32767 was implementation-defined (every mainstream compiler wraps it); since C++20 it is defined to wrap. the habits that keep this code honest: fixed-width types in every struct that mirrors bytes on a wire or in a register, an explicit `static_cast` wherever a value changes width or signedness, and `-Wconversion -Wsign-conversion` turned on for the modules that do this kind of work (they are noisy in general code, valuable here).

### watch out for

**subtracting unsigned values.** sizes and indices are unsigned, so their difference is too:

```cpp complete
#include <cstddef>

bool lagging(std::size_t expected, std::size_t received) {
    return expected - received > 3;   // BUG: 10 - 12 wraps to a huge number: true
}
```

the subtraction is well defined and wrong. compare without subtracting (`expected > received + 3`), or convert to a signed type first (`std::ptrdiff_t`, or C++20's `std::ssize(container)`) when a negative difference is meaningful. the same trap hides in `for (std::size_t k = 0; k <= v.size() - 1; ++k)`.

### the takeaway

arithmetic happens in `int` or wider, mixed signedness converts to unsigned, and only unsigned wraparound is defined; use fixed-width types where the width is part of a contract, and never subtract sizes without asking what happens when the result is negative.

### optional challenge

assuming a typical platform with a 32-bit `int`, what does this function return for `a = b = 65535`, and is the result even defined?

```cpp complete
#include <cstdint>
std::uint32_t area(std::uint16_t a, std::uint16_t b) { return a * b; }
```

<details>
<summary>answer</summary>

both operands are promoted to `int` (signed, 32 bits) before the multiplication, because `int` can represent every `std::uint16_t` value. 65535 * 65535 = 4,294,836,225, which exceeds `INT_MAX` (2,147,483,647). signed overflow is undefined behavior, so the function has no defined result for those inputs, even though every type in the signature is unsigned. the fix is to convert before multiplying: `return std::uint32_t{a} * b;`, which makes the arithmetic happen in `std::uint32_t` (the other operand is converted to unsigned) where wraparound is defined and, here, there is no overflow at all.

</details>
