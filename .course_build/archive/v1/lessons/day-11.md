<a id="day-11"></a>

## day 11: the rule of zero, three, and five

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 08, 09, 10

### the idea

Day 10's `Buffer` needed about 35 lines of copy and move code to manage one pointer correctly, and every line was a chance to get it wrong. Most classes in a healthy codebase have none of those lines. The rule of zero is not "be lazy"; it is a claim about design: managing a resource is one job, and a class that does that job should do nothing else.

### understanding the concept

There are six special member functions: the default constructor, the destructor, the copy constructor, copy assignment, the move constructor, and move assignment. The compiler declares the ones you do not, following rules that are worth having in front of you once:

| you declare | default ctor | destructor | copy ctor | copy assign | move ctor | move assign |
|---|---|---|---|---|---|---|
| nothing | defaulted | defaulted | defaulted | defaulted | defaulted | defaulted |
| another constructor | not declared | defaulted | defaulted | defaulted | defaulted | defaulted |
| destructor | defaulted | yours | defaulted (deprecated) | defaulted (deprecated) | not declared | not declared |
| copy ctor | not declared | defaulted | yours | defaulted (deprecated) | not declared | not declared |
| copy assign | defaulted | defaulted | defaulted (deprecated) | yours | not declared | not declared |
| move ctor | not declared | defaulted | deleted | deleted | yours | not declared |
| move assign | defaulted | defaulted | deleted | deleted | not declared | yours |

Three things in that table matter in practice.

- **"Declare" includes `= default` and `= delete`.** Writing `~T() = default;` counts as declaring a destructor and suppresses the implicit moves.
- **"Not declared" is not "deleted".** If there is no move constructor, an rvalue argument simply binds to the copy constructor's `const T&` parameter. Moves silently become copies, and `std::is_move_constructible_v<T>` still reports `true`.
- **"Defaulted" can still mean deleted.** A defaulted copy constructor is defined as deleted if some member cannot be copied. A class with a `std::unique_ptr` member is move-only without you writing anything.

From those rules come three guidelines:

- **Rule of three** (C++98): if you need a custom destructor, copy constructor, or copy assignment, you almost certainly need all three, because the custom one exists to manage a resource the defaults would mishandle.
- **Rule of five** (C++11): same, plus the two move operations, since declaring any of the three suppresses the implicit moves.
- **Rule of zero**: write classes that need none of them, by composing members that already manage themselves: `std::vector`, `std::string`, `std::unique_ptr`, and the few RAII types of your own.

### in code

Day 10's `Buffer`, refactored to the rule of zero:

```cpp
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

Copy is a deep copy, move steals the buffer, destruction frees it, and the move constructor is `noexcept` because `std::vector`'s is, so day 10's reallocation trap cannot happen. Copy assignment is arguably better than the hand-written one, since `std::vector` can reuse existing capacity instead of always allocating.

One thing did change: the moved-from contract. The hand-written `Buffer` promised `size() == 0` after a move. This one inherits `std::vector`'s "valid but unspecified". If callers relied on the old promise, that is an API change, and it deserves a line in the review. If you want a move-only buffer instead, swap the member for `std::unique_ptr<float[]>` plus a size: copying is then implicitly deleted, and the class still declares no special members.

When you do write the special members, copy-and-swap is the classic way to get assignment right with little code:

```cpp
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

The parameter is taken by value, so the copy (from an lvalue) or move (from an rvalue) happens at the call site, before the function body runs. If the copy throws, `*this` was never touched: the strong guarantee for free, self-assignment handled for free. The cost is real, though. Copy assignment always allocates, even when the target already has enough room, and move assignment does a move plus a swap instead of a direct steal. That is why the standard containers do not use it. It is a good default for types where assignment is rare and correctness matters more than the last allocation.

### in practice

A lidar driver owns a file descriptor, a scratch buffer, a name, and a parser. Only one of those is not already managed by a standard type, so only one class needs special members:

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

`std::unique_ptr` cannot manage a plain `int` handle without contortions (its deleter's `pointer` type must behave like a nullable pointer), so a small handle class is a legitimate place for hand-written members. The point is containment: one 25-line class with special members, tested once, and every class above it composes it and writes none. That is single responsibility applied to resource management, and it scales: a codebase with a handful of handle types and hundreds of rule-of-zero classes has very few places where a leak or double close can hide.

### watch out for

A destructor added "just for debugging" silently turns moves into copies:

```cpp
#include <cstdio>
#include <utility>
#include <vector>

struct Snapshot {
    std::vector<double> samples;
    ~Snapshot() { std::puts("snapshot released"); }   // added later
};

int main() {
    Snapshot a{std::vector<double>(100'000)};
    Snapshot b = std::move(a);                        // copy constructor!
    std::printf("%zu\n", a.samples.size());           // prints: 100000
}
```

Remove the destructor and the same program prints `0` on mainstream implementations (the vector was moved; strictly, its moved-from state is unspecified). Nothing warns. GCC and Clang have `-Wdeprecated-copy-dtor`, but it is not enabled by `-Wall` or `-Wextra`. Clang-tidy's `cppcoreguidelines-special-member-functions` catches the pattern.

The same rule bites polymorphic bases. `virtual ~Sensor() = default;` is a declared destructor, so `Sensor` and every class derived from it lose their implicit moves unless they declare them. The usual fix is to declare all five as `= default` in the base (making the copy operations `protected` if you also want to prevent slicing, which day 13 covers).

### the takeaway

Write the special members in the few classes whose job is to own a resource, and in no others. Everywhere else, the best special member function is the one you did not declare.

### optional challenge

Which special members does `Config` have, and which of these lines compile?

```cpp
struct Config {
    std::string name;
    std::unique_ptr<Parser> parser;
    explicit Config(std::string n);
};

Config a{"lidar"};                 // (1)
Config b = a;                      // (2)
Config c = std::move(a);           // (3)
std::vector<Config> v;
v.push_back(Config{"radar"});      // (4)
Config d;                          // (5)
```

<details>
<summary>answer</summary>

The user-declared constructor suppresses the default constructor. The destructor, copy operations, and move operations are all implicitly declared as defaulted, but the copy constructor and copy assignment are defined as deleted because `std::unique_ptr` is not copyable. The move operations work and are `noexcept`, since both members' moves are.

So (1) compiles, (2) fails (deleted copy constructor), (3) compiles, (4) compiles and the vector will move on reallocation, and (5) fails (no default constructor). `Config` is move-only without a single line of special-member code, which is exactly the behavior you want for something that owns a parser.

</details>
