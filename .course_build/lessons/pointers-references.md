---
title: pointers and references
standard: C++17
objective: choose between a pointer and a reference by what each can express (null, rebinding, arithmetic), and avoid losing an array's size
prerequisites: storage-duration, temporaries-dangling
difficulty: 1
---

### the idea

`float mean(const float samples[64])` looks like a function that takes 64 floats. it takes a pointer, and inside it `sizeof(samples)` is 8. pointers and references look like small syntax variations on "refer to something elsewhere", but they follow different rules about null, rebinding, arithmetic, and how much of the original type they remember. choosing well starts with knowing those rules precisely.

### understanding the concept

**a reference is an alias.** once bound, it names the same object for its whole life; there is no syntax to rebind it. `r = b;` assigns `b`'s value to whatever `r` refers to. a reference must be initialized, and in a valid program it always refers to an object or function, because the only way to make a "null reference" is to dereference a null pointer first, which is already undefined behavior. a reference can still dangle ([[temporaries-dangling]]), so "never null" does not mean "always valid".

**a pointer is an object holding an address.** it can be null, it can be reassigned, it can be compared, and it supports arithmetic within an array. that flexibility is exactly what makes it the right tool for "optional" and "may change what it points to", and the wrong tool when neither applies.

**`nullptr`, not `NULL` or `0`.** `NULL` is an implementation-defined null pointer constant: it might be `0`, `0L`, or a compiler intrinsic like GCC's `__null`. its type is an integer type in practice, so it can select an integer overload. `nullptr` has type `std::nullptr_t`, which converts to any pointer type and to no integer type.

**arrays decay.** an array expression converts to a pointer to its first element in most contexts, and a function parameter declared as `T a[N]` is really `T* a`; the `N` is ignored. pointer arithmetic is defined only within one array: you may form pointers to any element and to *one past the end*, but you may not dereference the one-past-the-end pointer, and merely computing a pointer further out (or before the first element) is undefined behavior. relational comparison (`<`) of pointers into unrelated objects gives an unspecified result; `std::less<T*>` is guaranteed to give a consistent total order if you need one, for example as a map key.

### in code

**rebinding that is not rebinding, and an overload that picks the wrong side.**

```cpp complete
#include <cstddef>
#include <cstdio>

void log_value(int)         { std::puts("int"); }
void log_value(const char*) { std::puts("const char*"); }

int main() {
    int a = 1, b = 2;
    int& r = a;
    r = b;                      // assigns 2 to a; r still refers to a
    b = 7;
    std::printf("%d %d\n", a, r);   // prints: 2 2

    log_value(0);               // prints: int
    log_value(nullptr);         // prints: const char*
    // log_value(NULL);         // GCC 12: error, ambiguous call. With NULL defined as 0
                                // (as some implementations do), it silently prints: int
}
```

the `NULL` line is the interesting one. which behavior you get depends on the implementation's definition of `NULL`, so the same source can be an error on one toolchain and a silent wrong call on another. `nullptr` removes the question.

**decay loses the size; pointer arithmetic has hard edges.**

```cpp ub
#include <cstddef>
#include <cstdint>

// BUG: the 64 is decoration; samples is const float*
float mean_bad(const float samples[64]) {
    const std::size_t n = sizeof(samples) / sizeof(samples[0]);  // 8 / 4 == 2 on x86-64
    float sum = 0;
    for (std::size_t i = 0; i < n; ++i) sum += samples[i];
    return sum / n;
}

// fixed: a reference to an array keeps N as part of the type
template <std::size_t N>
float mean(const float (&samples)[N]) {
    float sum = 0;
    for (float s : samples) sum += s;
    return sum / N;
}

void edges() {
    std::int16_t buf[256] = {};
    std::int16_t* end = buf + 256;   // fine: one past the end may be formed and compared
    // *end = 0;                     // UB: one-past-the-end must not be dereferenced
    // std::int16_t* p = buf + 257;  // UB: computing it is already undefined
    (void)end;
}
```

GCC warns about the first version (`-Wsizeof-array-argument`, on by default), and with a 64-element buffer whose first value is 64, our test printed 32 for `mean_bad` (two elements averaged) and 1 for the reference version. when the array size is not a compile-time constant, the classic pair is pointer plus length; C++20's `std::span` ([[span]]) packages that pair into one parameter.

### in practice

C APIs and hardware drivers speak in pointers and lengths: `read(fd, buf, len)`, a DMA descriptor's base address and byte count, a callback that receives `void* user_data`. keep that style at the boundary and convert to sized types as soon as you are inside your own code. a fixed buffer is better as `std::array<std::uint8_t, 256>` than as a C array, because `std::array` does not decay, can be passed by reference or returned by value, and knows its `size()`. when you do need the length of a built-in array, C++17's `std::size(arr)` refuses to compile on a decayed pointer, where `sizeof(arr) / sizeof(arr[0])` silently computes nonsense. the pointer-plus-length pair that is left over at the boundary is exactly what C++20's `std::span` ([[span]]) packages into one parameter.

### watch out for

**reference members make a class awkward to copy and easy to dangle.** a reference cannot be rebound, so a class that stores one gets no copy assignment:

```cpp complete
struct Sensor { int id = 0; };

struct Filter {
    Sensor& sensor;                 // must be bound at construction, forever
};

void reassign(Filter& a, const Filter& b) {
    // a = b;                       // error: copy assignment is implicitly deleted
}
```

such a class cannot be reassigned, sorted in a `std::vector`, or reset, and it silently relies on the referenced object outliving it. if the relationship can change or the object must be assignable, store a pointer (`Sensor*`, documented as non-owning) or `std::reference_wrapper<Sensor>` instead. reference members are fine for short-lived helper objects that live entirely inside one function call.

### the takeaway

a reference is a non-null, non-rebindable alias; a pointer is a nullable, rebindable object that may do arithmetic within one array. pick the one whose rules match what you mean, keep sizes in the type where you can, and write `nullptr`.

### optional challenge

which of these lines have undefined behavior?

```cpp complete
int a[4] = {};
int* p = a + 4;             // (1)
bool at_end = (p == a + 4); // (2)
int x = *(a + 4);           // (3)
int* q = a - 1;             // (4)
```

<details>
<summary>answer</summary>

(3) and (4). forming the one-past-the-end pointer (1) is allowed, and so is comparing it (2), which yields `true`. dereferencing it (3) is undefined behavior. computing `a - 1` (4) is undefined even if `q` is never used, because pointer arithmetic is only defined from the first element to one past the last. in practice (4) "works" almost everywhere, which is why sanitizers and compiler warnings matter more than intuition here.

</details>
