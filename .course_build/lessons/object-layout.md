---
title: objects in memory: size, alignment, and padding
standard: C++17
objective: predict an object's size and alignment, explain where padding comes from, and know which layout facts are guaranteed
prerequisites: integer-types
difficulty: 2
---

### the idea

`struct Detection { bool valid; double range; bool tracked; double doppler; };` holds 18 bytes of data and occupies 32 bytes on a typical 64-bit platform. reorder the members and it occupies 24. send it over a socket with `write(fd, &d, sizeof d)` and 14 of the bytes you ship are whatever happened to be in memory. an object is a region of storage with a type, and the type decides more about that storage than its list of members suggests.

### understanding the concept

every object has a **size** (`sizeof`) and an **alignment** (`alignof`): its address must be a multiple of its alignment. the values are implementation-defined. on mainstream 64-bit platforms `char` has alignment 1, `int` 4, and `double` and pointers 8, and `alignof(T)` never exceeds `sizeof(T)` for scalar types.

a class lays out its non-static data members in declaration order (strictly, members with the same access control; mixing `public:` and `private:` sections loosens even that). to keep each member aligned, the compiler inserts **padding** between members where needed. it also adds **tail padding** at the end, so that `sizeof` is a multiple of the class's alignment, which is the largest alignment among its members. tail padding is what keeps the second element of an array correctly aligned.

```text
Loose { bool valid; double range; bool tracked; double doppler; }
|v|.......|range...|t|.......|doppler.|     32 bytes, 14 of them padding

Tight { double range; double doppler; bool valid; bool tracked; }
|range...|doppler.|v|t|......|              24 bytes, 6 of them tail padding
```

two more facts complete the picture. the bytes of padding belong to the object's *representation* but not its *value*: their contents are unspecified, and copying the object member by member need not preserve them. and some types can be treated as plain bytes: a **trivially copyable** type (no user-provided copy, move, or destructor) may be copied with `std::memcpy`, which is why [[ub-usual-suspects]] could `memcpy` a frame header out of a buffer.

### in code

**measuring layout.**

```cpp complete
#include <cstddef>
#include <cstdio>

struct Loose { bool valid; double range; bool tracked; double doppler; };
struct Tight { double range; double doppler; bool valid; bool tracked; };

int main() {
    std::printf("%zu %zu\n", sizeof(Loose), alignof(Loose));  // prints: 32 8 (typical 64-bit)
    std::printf("%zu %zu\n", sizeof(Tight), alignof(Tight));  // prints: 24 8
    std::printf("%zu\n", offsetof(Loose, range));             // prints: 8
}
```

**pinning layout assumptions.** when a struct mirrors a wire format or a hardware register block, its layout is part of a contract, and the contract rests on implementation-defined facts. make the compiler check them:

```cpp complete
#include <cstdint>
#include <type_traits>

struct WireHeader {
    std::uint32_t seq;
    std::uint16_t magic;
    std::uint16_t count;
};

static_assert(sizeof(WireHeader) == 8, "no padding expected");
static_assert(alignof(WireHeader) == 4);
static_assert(std::is_trivially_copyable_v<WireHeader>, "must stay memcpy-able");
```

on the day someone adds a `bool` in the middle, or the code is built for a platform with different alignment rules, the build fails in this file instead of corrupting packets at run time.

### in practice

layout matters most for objects you store by the million. a radar pipeline that keeps one `Loose` detection per reflection in a `std::vector` moves 32 MB through the memory system for every million detections; the same data as `Tight` is 24 MB, a quarter fewer cache lines per pass over the data. a common rule of thumb for structs stored in bulk is to order members from the largest alignment to the smallest. for a one-off configuration object, grouping members by meaning is worth more than a few bytes. [[cache-locality]] comes back to how layout affects speed, and how to measure it rather than guess.

compilers offer `#pragma pack` to remove padding. it produces misaligned members: reading them through the struct works on the compilers that support it, but taking a pointer or reference to a packed member and using it elsewhere is not portable and faults on some architectures. for wire formats, explicit serialization (copying each field to and from a byte buffer) is the robust alternative.

### watch out for

**padding bytes are not zero, so do not compare or hash raw bytes.**

```cpp
#include <cstring>

bool same(const Loose& a, const Loose& b) {
    return std::memcmp(&a, &b, sizeof a) == 0;   // BUG: compares padding too
}
```

two `Loose` objects with identical members can differ in their padding, so `same` may return `false` for equal values. the same bug appears when hashing an object's bytes or using them as a cache key, and sending raw structs over the network can leak stale memory contents through the padding. compare members, not bytes; C++20 can generate the member-wise comparison for you ([[defaulted-comparisons]]).

### the takeaway

size and alignment are properties of the type, padding is the price of alignment, and almost every layout fact beyond "declared order, aligned members" is implementation-defined, so `static_assert` the ones your code relies on.

### optional challenge

on a platform where `int` has size and alignment 4, what are `sizeof` and `alignof` for these two types, and why is `sizeof(S)` not 6?

```cpp complete
struct S { char c; int i; char d; };
struct T { int i; char c; char d; };
```

<details>
<summary>answer</summary>

`S`: `c` at offset 0, three bytes of padding, `i` at 4, `d` at 8, then three bytes of tail padding: `sizeof(S) == 12`, `alignof(S) == 4`. `T`: `i` at 0, `c` at 4, `d` at 5, two bytes of tail padding: `sizeof(T) == 8`, `alignof(T) == 4`.

`sizeof(S)` cannot be 6 because `i` must sit at a multiple of 4, and the tail padding is needed for arrays: in `S arr[2]`, the second element starts at `arr + sizeof(S)`, and its `i` is only aligned if `sizeof(S)` is a multiple of 4.

</details>

### going deeper

#### empty classes and the empty base optimization

an object of an empty class still has a size of at least 1, because distinct objects of the same type must have distinct addresses. as a base class, though, an empty class may occupy no space at all (the *empty base optimization*). that is how `std::unique_ptr` with a stateless deleter stays the size of a raw pointer: implementations store the deleter so that it takes no room. C++20 adds `[[no_unique_address]]`, which grants the same freedom to a data member, so a class can hold an empty policy or allocator member without paying a byte plus padding for it.

#### standard-layout types and `offsetof`

`offsetof` is only guaranteed to work for *standard-layout* classes: roughly, all non-static data members have the same access control, there are no virtual functions or virtual bases, and base classes do not also declare data members. for other classes it is conditionally-supported since C++17, which means a compiler may reject it. GCC accepts it with a warning (`-Winvalid-offsetof`). the type trait `std::is_standard_layout_v<T>` tells you which side of the line a type is on.
