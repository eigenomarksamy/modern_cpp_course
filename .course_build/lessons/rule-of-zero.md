---
title: the rule of zero
standard: C++17
objective: design classes that need no hand-written special members by composing types that manage themselves
prerequisites: special-members
difficulty: 2
---

### the idea

[[move-semantics]]'s `Buffer` needed about 35 lines of copy and move code to manage one pointer correctly, and every line was a chance to get it wrong. most classes in a healthy codebase have none of those lines. the rule of zero is not "be lazy"; it is a claim about design: managing a resource is one job, and a class that does that job should do nothing else.

### understanding the concept

from those rules come three guidelines:

- **rule of three** (C++98): if you need a custom destructor, copy constructor, or copy assignment, you almost certainly need all three, because the custom one exists to manage a resource the defaults would mishandle.
- **rule of five** (C++11): same, plus the two move operations, since declaring any of the three suppresses the implicit moves.
- **rule of zero**: write classes that need none of them, by composing members that already manage themselves: `std::vector`, `std::string`, `std::unique_ptr`, and the few RAII types of your own.

### in code

[[move-semantics]]'s `Buffer`, refactored to the rule of zero:

```cpp complete
#include <cstddef>
#include <vector>

class Buffer {
public:
    explicit Buffer(std::size_t n) : data_(n) {}
    std::size_t size() const noexcept { return data_.size(); }
    float* data() noexcept { return data_.data(); }
    const float* data() const noexcept { return data_.data(); }
private:
    std::vector<float> data_;
};
```

copy is a deep copy, move steals the buffer, destruction frees it, and the move constructor is `noexcept` because `std::vector`'s is, so the reallocation trap from [[noexcept-moves]] cannot happen. copy assignment is arguably better than the hand-written one, since `std::vector` can reuse existing capacity instead of always allocating.

one thing did change: the moved-from contract. the hand-written `Buffer` promised `size() == 0` after a move. this one inherits `std::vector`'s "valid but unspecified". if callers relied on the old promise, that is an API change, and it deserves a line in the review. if you want a move-only buffer instead, swap the member for `std::unique_ptr<float[]>` plus a size: copying is then implicitly deleted, and the class still declares no special members.

### in practice

a lidar driver owns a file descriptor, a scratch buffer, a name, and a parser. only one of those is not already managed by a standard type, so only one class needs special members:

```cpp
#include <unistd.h>
#include <utility>

class UniqueFd {                       // the one class that manages a resource
public:
    UniqueFd() = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(UniqueFd&& o) noexcept : fd_(std::exchange(o.fd_, -1)) {}
    UniqueFd& operator=(UniqueFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = std::exchange(o.fd_, -1);
        }
        return *this;
    }
    UniqueFd(const UniqueFd&) = delete;             // already implied; say it anyway
    UniqueFd& operator=(const UniqueFd&) = delete;

    int get() const noexcept { return fd_; }
private:
    int fd_ = -1;
};

class LidarDriver {                    // rule of zero: move-only, correct, no special members
public:
    LidarDriver(std::string name, UniqueFd fd)
        : name_(std::move(name)), fd_(std::move(fd)) {}
private:
    std::string name_;
    UniqueFd fd_;
    std::vector<Point> scratch_;
    std::unique_ptr<PacketParser> parser_;
};
```

`std::unique_ptr` cannot manage a plain `int` handle without contortions (its deleter's `pointer` type must behave like a nullable pointer), so a small handle class is a legitimate place for hand-written members. the point is containment: one 25-line class with special members, tested once, and every class above it composes it and writes none. that is single responsibility applied to resource management, and it scales: a codebase with a handful of handle types and hundreds of rule-of-zero classes has very few places where a leak or double close can hide.

### watch out for

**`const` and reference members quietly delete assignment.** a rule-of-zero class inherits its members' limitations:

```cpp complete
#include <vector>

struct Track {
    const int id;                    // looks like good hygiene
    std::vector<double> ranges;
};

void sort_by_id(std::vector<Track>& tracks);   // std::sort needs move assignment: does not compile
```

a `const` member cannot be assigned, so `Track` has no copy or move assignment, and anything that reassigns elements (`std::sort`, `std::remove_if`, `tracks[i] = other`) fails to compile. a type meant to behave like a value should keep its members non-`const` and private, and expose them through `const` accessors; the immutability belongs to the interface, not the storage.

### the takeaway

write the special members in the few classes whose job is to own a resource, and in no others. everywhere else, the best special member function is the one you did not declare.

### optional challenge

which special members does `LidarDriver` from the practice section have? can it be copied, moved, and stored in a `std::vector` that reallocates efficiently?

<details>
<summary>answer</summary>

it has a user-declared constructor, so no default constructor. the destructor and the move operations are implicitly defaulted, and the moves are `noexcept`, because every member (`std::string`, `UniqueFd`, `std::vector`, `std::unique_ptr`) has a `noexcept` move. the copy operations are implicitly deleted, because `UniqueFd` and `std::unique_ptr` are not copyable. so: not copyable, movable, and a `std::vector<LidarDriver>` moves its elements on reallocation. all of that without declaring a single special member.

</details>

### going deeper

#### copy-and-swap

when you do write the special members, copy-and-swap is the classic way to get assignment right with little code:

```cpp complete
#include <algorithm>
#include <cstddef>
#include <utility>

class Buffer5 {                                   // rule of five, by hand
public:
    explicit Buffer5(std::size_t n) : size_(n), data_(new float[n]{}) {}
    ~Buffer5() { delete[] data_; }
    Buffer5(const Buffer5& o) : size_(o.size_), data_(new float[o.size_]) {
        std::copy(o.data_, o.data_ + size_, data_);
    }
    Buffer5(Buffer5&& o) noexcept
        : size_(std::exchange(o.size_, 0)), data_(std::exchange(o.data_, nullptr)) {}

    Buffer5& operator=(Buffer5 other) noexcept {  // one operator for copy and move
        swap(*this, other);
        return *this;
    }                                             // other's destructor frees the old buffer
    friend void swap(Buffer5& a, Buffer5& b) noexcept {
        std::swap(a.size_, b.size_);
        std::swap(a.data_, b.data_);
    }
private:
    std::size_t size_;
    float* data_;
};
```

the parameter is taken by value, so the copy (from an lvalue) or move (from an rvalue) happens at the call site, before the function body runs. if the copy throws, `*this` was never touched: the strong guarantee for free, self-assignment handled for free. the cost is real, though. copy assignment always allocates, even when the target already has enough room, and move assignment does a move plus a swap instead of a direct steal. that is why the standard containers do not use it. it is a good default for types where assignment is rare and correctness matters more than the last allocation.
