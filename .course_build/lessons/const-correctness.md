---
title: const as a contract
standard: C++17
objective: read and apply const on pointers, references, and member functions, and choose parameter types that state a function's contract
prerequisites: pointers-references
difficulty: 2
---

### the idea

read this declaration from a tracking library: `void update(Track* t, Detection* d);`. can `t` be null? will `update` modify `d`? will it keep either pointer after it returns? the signature answers none of these questions. now compare `void update(Track& t, const Detection& d);`: both must exist, only `t` changes, and nothing in the types suggests the function holds on to them. pointers, references, and `const` are not only about mechanics. they are the cheapest documentation you will ever write, and the compiler checks it.

### understanding the concept

**reading `const`.** `const` applies to whatever is immediately to its left, or to the right if nothing is on its left. reading right to left works well:

| declaration | read as | can change pointer | can change pointee |
|---|---|---|---|
| `const T* p` (same as `T const* p`) | pointer to const T | yes | no |
| `T* const p` | const pointer to T | no | yes |
| `const T* const p` | const pointer to const T | no | no |
| `const T& r` | reference to const T | (never) | no |

`const T&` means "read-only access through this name", not "this object is immutable". someone else holding a non-const path to the same object can change it under you.

**const member functions.** in a member function marked `const`, `this` has type `const T*`, so data members are treated as `const`. that lets you call the function on `const` objects and through `const&` parameters, and it is a promise: calling it does not change the object's observable state. that is *logical* constness. sometimes the bits must change while the observable state does not (a cache, a mutex, a statistics counter); `mutable` exempts a member from the rule.

### in code

**logical constness with `mutable`.**

```cpp complete
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

the mutex is not decoration. the standard library guarantees that its own `const` member functions can be called concurrently on the same object, and generic code and your colleagues will assume the same of your types. a `mutable` member written from a `const` function breaks that assumption unless it is synchronized (data races are [[data-races]]). if you add `mutable`, you own the thread-safety of that member.

### in practice

here is the tracker API from the opening, written so the signature carries the contract:

```cpp
class Tracker {
public:
    void set_gate(double gate_m);                      // cheap type: by value
    void ingest(const DetectionBatch& batch);          // large, read-only: const&
    void predict(Track& track, double dt) const;       // in/out parameter: non-const&
    const Track* find(TrackId id) const;               // may be absent: pointer, nullptr if not found
    void add(Track track);                             // sink: take by value, move inside
};
```

the guidelines behind it: pass cheap-to-copy types (roughly, a couple of machine words: integers, doubles, small structs, iterators, `std::string_view`) by value, because a reference forces an indirection and lets the compiler assume less about aliasing. pass larger read-only objects by `const&`. use a non-const reference for an in/out parameter, and prefer returning a value over an "out" parameter when you can. use a pointer when "nothing" is a legitimate value. none of these says anything about ownership; that is what smart pointers in signatures are for ([[ownership-in-interfaces]]). a `const Track*` from `find` is a borrowed view, valid until the tracker changes, and that limit belongs in a comment because the type cannot express it.

### watch out for

`const` on a member function is shallow. it makes the *pointer member* const, not what it points to:

```cpp complete
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

a `std::vector` member propagates constness to its elements because its `operator[] const` returns `const T&`. a raw pointer member (and, for the same reason, a smart pointer member) does not. if an object conceptually owns what a pointer member points to, its `const` functions must enforce that themselves; the compiler will not.

### the takeaway

make the signature say it: value for cheap inputs, `const&` for large read-only ones, `&` for in/out, pointer for "might be nothing", and `nullptr` always; then treat `const` as a promise about observable state that you must keep, especially across threads.

### optional challenge

which numbered lines fail to compile? with those lines deleted, what does the program print?

```cpp fails
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

lines (3) and (4) fail. `p` is a pointer to `const int`, so `*p = 4` assigns through a read-only path; `q` is a `const` pointer, so it cannot be reseated. line (1) is fine (the pointer itself is not const), and (2) is fine (the pointee of `q` is not const).

with them removed, it prints `5`. `r` is a read-only view of `a`, not a snapshot and not a promise that `a` never changes: `a` was set to 3 through `q` and then to 5 directly, and `r` sees the current value.

</details>
