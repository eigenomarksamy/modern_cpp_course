---
title: copying: deep, shallow, and the double free
standard: C++17
objective: explain what a copy must produce, why the generated copy is wrong for a class that owns a resource through a pointer, and write a correct deep copy
prerequisites: raii, construction-order
difficulty: 2
---

### the idea

every class you write can be copied unless you say otherwise, because the compiler generates a copy constructor that copies each member in turn. for a `std::vector` member that is exactly right. for a raw pointer to memory the class owns, it produces two objects that both believe they own the same block, and the program finds out when the second destructor runs.

### understanding the concept

copying gives the destination its own independent value; the source is untouched. for a type that owns a resource through a pointer, that means duplicating the resource (a deep copy). copying just the pointer (a shallow copy) leaves two owners, and [[raii]]'s destructor will release the same resource twice.

a copy is supposed to produce an *independent value*: after `b = a`, changing `b` must not change `a`, and destroying one must not affect the other. that is what makes value types easy to reason about. the compiler-generated copy constructor and copy assignment copy each base and member with *its* copy operation. for members that are themselves values (`int`, `std::string`, `std::vector`), the result is a correct deep copy for free. for a member that is a handle to something else (a raw pointer, a file descriptor, an index into a global table), copying the handle is a shallow copy, and whether that is right depends entirely on who owns the thing it refers to.

### in code

the bug that motivates all of this. a class owns a raw buffer and relies on the implicitly generated copy:

```cpp
class Frame {
public:
    explicit Frame(std::size_t n) : size_(n), data_(new float[n]{}) {}
    ~Frame() { delete[] data_; }
private:
    std::size_t size_;
    float* data_;
};

void f() {
    Frame a(1024);
    Frame b = a;        // BUG: implicit copy duplicates the pointer
}                       // double delete[]: undefined behavior
```

the fix spells out what copying means for this resource:

```cpp complete
#include <algorithm>
#include <cstddef>

class Buffer {
public:
    explicit Buffer(std::size_t n) : size_(n), data_(new float[n]{}) {}
    ~Buffer() { delete[] data_; }

    Buffer(const Buffer& o) : size_(o.size_), data_(new float[o.size_]) {
        std::copy(o.data_, o.data_ + size_, data_);           // deep copy
    }
    Buffer& operator=(const Buffer& o) {
        if (this != &o) {
            float* fresh = new float[o.size_];                // may throw: do it first
            std::copy(o.data_, o.data_ + o.size_, fresh);
            delete[] data_;                                   // only now touch *this
            data_ = fresh;
            size_ = o.size_;
        }
        return *this;
    }
private:
    std::size_t size_;
    float* data_;
};
```

the copy assignment allocates before it releases, so if `new` throws, `*this` is unchanged: the strong exception-safety guarantee, which [[exception-safety]] defines properly. the self-assignment check is only an optimization here; because the data is copied into `fresh` first, `b = b` would still end with an equal value.

### in practice

value semantics is a design tool, not only a mechanism. a motion planner that takes a *copy* of the world model at the start of each planning cycle can work on it for 50 ms without locks, while the perception thread keeps updating the live model; the copy is the snapshot. the price is the copy itself, which is why the next lessons care so much about avoiding unnecessary ones. the decision for each type you write is therefore explicit: copyable with a deep copy (values like `Buffer`), not copyable at all (unique handles like a serial port), or shared deliberately (a later lesson's `std::shared_ptr`). the generated copy is only correct when every member already made that decision correctly.

### watch out for

**the "obvious" copy assignment is wrong twice.**

```cpp
Buffer& Buffer::operator=(const Buffer& o) {
    delete[] data_;                          // BUG 1: if o is *this, the source is gone
    size_ = o.size_;
    data_ = new float[size_];                // BUG 2: if this throws, data_ dangles
    std::copy(o.data_, o.data_ + size_, data_);
    return *this;
}
```

for `b = b`, the first line frees the very data it is about to copy. and if `new` throws, the object is left holding a pointer to freed memory, which its destructor will free again. "acquire the new state first, then release the old one" fixes both, which is why the version above is written in that order.

### the takeaway

a copy must produce an independent value; when a class owns a resource through a handle, the generated memberwise copy creates two owners instead, so either write a deep copy or forbid copying.

### optional challenge

which of these types can safely use the compiler-generated copy constructor?

```cpp
struct A { std::vector<double> samples; };
struct B { double* samples; ~B() { delete[] samples; } };
struct C { const Config* config; };        // points to a config owned elsewhere
struct D { std::FILE* log; ~D() { std::fclose(log); } };
```

<details>
<summary>answer</summary>

`A` is safe: `std::vector` deep-copies itself. `C` is safe as long as the pointer is genuinely non-owning, since two objects observing the same config is the intended meaning. `B` and `D` are not: each copy would share the handle, and both destructors would release it (a double `delete[]` and a double `fclose`). `B` needs a deep copy or, better, a `std::vector<double>` member; `D` should be non-copyable, since duplicating an open file has no sensible meaning.

</details>
