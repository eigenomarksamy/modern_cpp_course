---
title: moving: transferring resources instead of copying them
standard: C++17
objective: implement move operations, explain why `std::move` is only a cast, and state what a moved-from object promises
prerequisites: copy-semantics, value-categories
difficulty: 3
---

### the idea

`std::move` does not move anything. it compiles to no instructions at all. whether a move happens, and what it costs, is decided entirely by which constructor or assignment operator overload resolution picks afterwards, and that is code you (or the compiler) wrote.

once you see moves as "an overload that is allowed to steal, selected by value category", the surprising cases stop being surprising: the `std::move` that copies, the vector that copies when you expected moves, and the `return std::move(x)` that makes code slower.

### understanding the concept

moving gives the destination the source's value and permits the source to be left in a cheaper, emptier state. for a pointer-owning type that means taking the pointer and nulling the source: O(1), no allocation, usually no way to fail.

the selection is plain overload resolution on [[value-categories]]'s value categories. a `T&&` parameter binds to rvalues (prvalues and xvalues); a `const T&` binds to anything. given both, an rvalue argument prefers `T&&`. and `std::move` is just a cast that turns an lvalue into an xvalue:

```cpp
template <typename T>
constexpr std::remove_reference_t<T>&& move(T&& t) noexcept {
    return static_cast<std::remove_reference_t<T>&&>(t);
}
```

what state does the source end up in? for standard library types the rule is "valid but unspecified": the object still satisfies its invariants, so you can destroy it, assign to it, or call functions without preconditions (`size()`, `clear()`), but you must not assume a particular value. a moved-from `std::vector` is empty on every mainstream implementation, but that is not a guarantee you should build on. for your own types, the moved-from state is part of your contract: decide it and document it.

### in code

adding move operations to the `Buffer` from [[copy-semantics]]:

```cpp complete
#include <cstddef>
#include <utility>

class Buffer {
public:
    // constructor, destructor, and copy operations as before
    Buffer(Buffer&& o) noexcept                               // steal, leave o empty
        : size_(std::exchange(o.size_, 0)), data_(std::exchange(o.data_, nullptr)) {}
    Buffer& operator=(Buffer&& o) noexcept {
        if (this != &o) {                                     // survive b = std::move(b)
            delete[] data_;
            size_ = std::exchange(o.size_, 0);
            data_ = std::exchange(o.data_, nullptr);
        }
        return *this;
    }

    std::size_t size() const noexcept { return size_; }       // moved-from: size() == 0
private:
    std::size_t size_;
    float* data_;
};
```

the move constructor steals the pointer and leaves the source empty, so the source's destructor has nothing to free. the move assignment must check for self-assignment: without the check, `b = std::move(b)` would delete the buffer and then adopt the dangling pointer. `std::exchange` keeps "take the value, leave a replacement" on one line, which makes the moved-from contract visible: after a move, `size()` is 0.

that is a lot of code for one pointer, and it is easy to get subtly wrong. [[rule-of-zero]] shows how to make almost all of it disappear.

### in practice

a radar processing chain passes large frames between stages. a stage that keeps what it receives takes the frame by value (a "sink" parameter) and moves it into place:

```cpp
class Tracker {
public:
    void submit(RangeDopplerFrame frame) { pending_.push_back(std::move(frame)); }
private:
    std::vector<RangeDopplerFrame> pending_;
};

RangeDopplerFrame acquire(Receiver& rx) {
    RangeDopplerFrame f = rx.read_frame();
    apply_window(f);
    return f;                        // not std::move(f)
}

void loop(Receiver& rx, Tracker& tracker) {
    RangeDopplerFrame frame = acquire(rx);
    tracker.submit(std::move(frame));  // caller opts in to giving it away
    frame = acquire(rx);               // assigning to a moved-from object is fine
}
```

the signature tells the story: a by-value parameter, a caller that writes `std::move` when it is done with the object, and a copy only when the caller explicitly keeps one. inside `acquire`, `return f;` is deliberately not `return std::move(f);`, for the reasons in [[copy-elision]].

### watch out for

**`std::move` on a `const` object copies, silently.**

```cpp
const std::string config = load_config();
std::string owned = std::move(config);   // copies: const std::string&& binds to const&
```

`std::move(config)` produces `const std::string&&`. the move constructor wants `std::string&&`, which cannot bind to a const object, so overload resolution falls back to the copy constructor. no warning, no error, just a copy. the same applies to `const` data members: a class with a `const std::vector` member cannot be moved efficiently, because that member is copied every time. declare locals `const` freely, but not ones you intend to move from, and think twice about `const` members in types that will be moved.

**use after move is legal and still a bug.** reading `frame.size()` after `submit(std::move(frame))` is well-defined for a standard type and almost always a logic error. `clang-tidy`'s `bugprone-use-after-move` check finds most of these.

### the takeaway

`std::move` only grants permission; the move constructor does the work, and the moved-from object is valid but promises nothing more than its type's contract says.

### optional challenge

`Buffer`'s copy assignment uses `if (this != &o)`. is the check required for correctness, or only an optimization? what about the move assignment?

<details>
<summary>answer</summary>

for the copy assignment it is only an optimization. because it allocates and copies into `fresh` before deleting the old buffer, self-assignment copies the data into a new block, frees the old one, and ends up with an equal value. the check just skips a pointless allocation.

for the move assignment it is required for correctness as written. without it, `b = std::move(b)` runs `delete[] data_`, and then `data_ = std::exchange(o.data_, nullptr)` reads the freed pointer out of the same object (briefly setting it to null) and stores it straight back. `b` now holds a dangling pointer with its old size, and its destructor will `delete[]` the block a second time: undefined behavior. self-move is rare in direct code but appears through aliasing: `std::swap(x, x)` performs `x = std::move(x)` internally, and so does `v[i] = std::move(v[j])` when `i == j`.

</details>
