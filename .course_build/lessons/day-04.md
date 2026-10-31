<a id="day-04"></a>

## day 04: pointers, references, and const

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days [02](#day-02), [03](#day-03)

### the idea

Read this declaration from a tracking library: `void update(Track* t, Detection* d);`. Can `t` be null? Will `update` modify `d`? Will it keep either pointer after it returns? The signature answers none of these questions. Now compare `void update(Track& t, const Detection& d);`: both must exist, only `t` changes, and nothing in the types suggests the function holds on to them. Pointers, references, and `const` are not only about mechanics. They are the cheapest documentation you will ever write, and the compiler checks it.

### understanding the concept

**A reference is an alias.** Once bound, it names the same object for its whole life; there is no syntax to rebind it. `r = b;` assigns `b`'s value to whatever `r` refers to. A reference must be initialized, and in a valid program it always refers to an object or function, because the only way to make a "null reference" is to dereference a null pointer first, which is already undefined behavior. A reference can still dangle (day 03), so "never null" does not mean "always valid".

**A pointer is an object holding an address.** It can be null, it can be reassigned, it can be compared, and it supports arithmetic within an array. That flexibility is exactly what makes it the right tool for "optional" and "may change what it points to", and the wrong tool when neither applies.

**Reading `const`.** `const` applies to whatever is immediately to its left, or to the right if nothing is on its left. Reading right to left works well:

| declaration | read as | can change pointer | can change pointee |
|---|---|---|---|
| `const T* p` (same as `T const* p`) | pointer to const T | yes | no |
| `T* const p` | const pointer to T | no | yes |
| `const T* const p` | const pointer to const T | no | no |
| `const T& r` | reference to const T | (never) | no |

`const T&` means "read-only access through this name", not "this object is immutable". Someone else holding a non-const path to the same object can change it under you.

**Const member functions.** In a member function marked `const`, `this` has type `const T*`, so data members are treated as `const`. That lets you call the function on `const` objects and through `const&` parameters, and it is a promise: calling it does not change the object's observable state. That is *logical* constness. Sometimes the bits must change while the observable state does not (a cache, a mutex, a statistics counter); `mutable` exempts a member from the rule.

**`nullptr`, not `NULL` or `0`.** `NULL` is an implementation-defined null pointer constant: it might be `0`, `0L`, or a compiler intrinsic like GCC's `__null`. Its type is an integer type in practice, so it can select an integer overload. `nullptr` has type `std::nullptr_t`, which converts to any pointer type and to no integer type.

**Arrays decay.** An array expression converts to a pointer to its first element in most contexts, and a function parameter declared as `T a[N]` is really `T* a`; the `N` is ignored. Pointer arithmetic is defined only within one array: you may form pointers to any element and to *one past the end*, but you may not dereference the one-past-the-end pointer, and merely computing a pointer further out (or before the first element) is undefined behavior. Relational comparison (`<`) of pointers into unrelated objects gives an unspecified result; `std::less<T*>` is guaranteed to give a consistent total order if you need one, for example as a map key.

### in code

**Rebinding that is not rebinding, and an overload that picks the wrong side.**

```cpp
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

The `NULL` line is the interesting one. Which behavior you get depends on the implementation's definition of `NULL`, so the same source can be an error on one toolchain and a silent wrong call on another. `nullptr` removes the question.

**Decay loses the size; pointer arithmetic has hard edges.**

```cpp
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

GCC warns about the first version (`-Wsizeof-array-argument`, on by default), and with a 64-element buffer whose first value is 64, our test printed 32 for `mean_bad` (two elements averaged) and 1 for the reference version. When the array size is not a compile-time constant, the classic pair is pointer plus length; C++20's `std::span` (day 31) packages that pair into one parameter.

**Logical constness with `mutable`.**

```cpp
#include <mutex>
#include <optional>
#include <utility>
#include <vector>

class Calibration {
public:
    explicit Calibration(std::vector<double> raw) : raw_(std::move(raw)) {}

    double offset() const {                      // same answer every call: logically const
        std::lock_guard<std::mutex> lock(mutex_);
        if (!cached_) cached_ = compute();       // allowed: cached_ is mutable
        return *cached_;
    }

private:
    double compute() const {
        double s = 0;
        for (double r : raw_) s += r;
        return s / raw_.size();
    }
    std::vector<double> raw_;
    mutable std::optional<double> cached_;
    mutable std::mutex mutex_;
};
```

The mutex is not decoration. The standard library guarantees that its own `const` member functions can be called concurrently on the same object, and generic code and your colleagues will assume the same of your types. A `mutable` member written from a `const` function breaks that assumption unless it is synchronized (data races are day 37). If you add `mutable`, you own the thread-safety of that member.

### in practice

Here is the tracker API from the opening, written so the signature carries the contract:

```cpp
class Tracker {
public:
    void set_gate(double gate_m);                      // cheap type: by value
    void ingest(const DetectionBatch& batch);          // large, read-only: const&
    void predict(Track& track, double dt) const;       // in/out parameter: non-const&
    const Track* find(TrackId id) const;               // may be absent: pointer, nullptr if not found
    void add(Track track);                             // sink: take by value, move inside (day 10)
};
```

The guidelines behind it: pass cheap-to-copy types (roughly, a couple of machine words: integers, doubles, small structs, iterators, `std::string_view`) by value, because a reference forces an indirection and lets the compiler assume less about aliasing. Pass larger read-only objects by `const&`. Use a non-const reference for an in/out parameter, and prefer returning a value over an "out" parameter when you can. Use a pointer when "nothing" is a legitimate value. None of these says anything about ownership; that is what smart pointers in signatures are for (day 12). A `const Track*` from `find` is a borrowed view, valid until the tracker changes, and that limit belongs in a comment because the type cannot express it.

### watch out for

`const` on a member function is shallow. It makes the *pointer member* const, not what it points to:

```cpp
#include <vector>

struct Joint { double angle = 0.0; };

class Arm {
public:
    void reset_view() const {
        joints_[0].angle = 0.0;     // compiles: joints_ is Joint* const here, joints are not const
        // spare_[0].angle = 0.0;   // error: spare_ is a const vector inside a const function
    }
private:
    Joint* joints_ = nullptr;
    std::vector<Joint> spare_;
};
```

A `std::vector` member propagates constness to its elements because its `operator[] const` returns `const T&`. A raw pointer member (and, for the same reason, a smart pointer member) does not. If an object conceptually owns what a pointer member points to, its `const` functions must enforce that themselves; the compiler will not.

### the takeaway

Make the signature say it: value for cheap inputs, `const&` for large read-only ones, `&` for in/out, pointer for "might be nothing", and `nullptr` always; then treat `const` as a promise about observable state that you must keep, especially across threads.

### optional challenge

Which numbered lines fail to compile? With those lines deleted, what does the program print?

```cpp
#include <iostream>

int main() {
    int a = 1, b = 2;
    const int* p = &a;
    int* const q = &a;
    const int& r = a;
    p = &b;   // (1)
    *q = 3;   // (2)
    *p = 4;   // (3)
    q = &b;   // (4)
    a = 5;    // (5)
    std::cout << r << '\n';
}
```

<details>
<summary>answer</summary>

Lines (3) and (4) fail. `p` is a pointer to `const int`, so `*p = 4` assigns through a read-only path; `q` is a `const` pointer, so it cannot be reseated. Line (1) is fine (the pointer itself is not const), and (2) is fine (the pointee of `q` is not const).

With them removed, it prints `5`. `r` is a read-only view of `a`, not a snapshot and not a promise that `a` never changes: `a` was set to 3 through `q` and then to 5 directly, and `r` sees the current value.

</details>
