---
title: the special member functions and when the compiler writes them
standard: C++17
objective: predict which special members a class gets, and recognize when a declaration silently turns moves into copies
prerequisites: noexcept-moves
difficulty: 2
---

### the idea

for every class you define, the compiler is prepared to write up to six member functions on your behalf. which ones it writes, and when it quietly stops, follows a short set of rules. they are worth learning once, because the most expensive mistake they allow (a move that has silently become a copy) produces no error, no warning, and correct output.

### understanding the concept

there are six special member functions: the default constructor, the destructor, the copy constructor, copy assignment, the move constructor, and move assignment. the compiler declares the ones you do not, following rules that are worth having in front of you once:

| you declare | default ctor | destructor | copy ctor | copy assign | move ctor | move assign |
|---|---|---|---|---|---|---|
| nothing | defaulted | defaulted | defaulted | defaulted | defaulted | defaulted |
| another constructor | not declared | defaulted | defaulted | defaulted | defaulted | defaulted |
| destructor | defaulted | yours | defaulted (deprecated) | defaulted (deprecated) | not declared | not declared |
| copy ctor | not declared | defaulted | yours | defaulted (deprecated) | not declared | not declared |
| copy assign | defaulted | defaulted | defaulted (deprecated) | yours | not declared | not declared |
| move ctor | not declared | defaulted | deleted | deleted | yours | not declared |
| move assign | defaulted | defaulted | deleted | deleted | not declared | yours |

three things in that table matter in practice.

- **"declare" includes `= default` and `= delete`.** writing `~T() = default;` counts as declaring a destructor and suppresses the implicit moves.
- **"not declared" is not "deleted".** if there is no move constructor, an rvalue argument simply binds to the copy constructor's `const T&` parameter. moves silently become copies, and `std::is_move_constructible_v<T>` still reports `true`.
- **"defaulted" can still mean deleted.** a defaulted copy constructor is defined as deleted if some member cannot be copied. a class with a `std::unique_ptr` member is move-only without you writing anything.

### in code

the type traits make the rules visible. a destructor written for logging removes the implicit move constructor, and the "move" that remains is the copy constructor:

```cpp complete
#include <type_traits>
#include <vector>

struct Plain  { std::vector<int> v; };
struct Logged { std::vector<int> v; ~Logged() {} };

static_assert(std::is_nothrow_move_constructible_v<Plain>);    // a real, noexcept move
static_assert(std::is_move_constructible_v<Logged>);           // true, but it is a copy
static_assert(!std::is_nothrow_move_constructible_v<Logged>);  // copying a vector can throw
```

`std::is_move_constructible_v` only asks whether an rvalue can construct the type, and the copy constructor's `const T&` parameter accepts one. the `nothrow` trait gives the game away, and it is exactly the property `std::vector` checks before deciding to move ([[noexcept-moves]]).

### in practice

the same rule bites polymorphic bases. `virtual ~Sensor() = default;` is a declared destructor, so `Sensor` and every class derived from it lose their implicit moves unless they declare them. the usual fix is to declare all five as `= default` in the base (making the copy operations `protected` if you also want to prevent slicing, which [[virtual-destructors-slicing]] covers).

in the base class, that looks like this:

```cpp complete
class Sensor {
public:
    virtual ~Sensor() = default;
    Sensor() = default;
    Sensor(Sensor&&) = default;
    Sensor& operator=(Sensor&&) = default;
protected:
    Sensor(const Sensor&) = default;              // derived classes may copy their base part
    Sensor& operator=(const Sensor&) = default;   // but outside code cannot slice
};
```

writing all five explicitly costs five lines and documents a decision; leaving them implicit after declaring the destructor costs every derived class its moves.

### watch out for

a destructor added "just for debugging" silently turns moves into copies:

```cpp complete
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

remove the destructor and the same program prints `0` on mainstream implementations (the vector was moved; strictly, its moved-from state is unspecified). nothing warns. GCC and Clang have `-Wdeprecated-copy-dtor`, but it is not enabled by `-Wall` or `-Wextra`. Clang-tidy's `cppcoreguidelines-special-member-functions` catches the pattern.

### the takeaway

declaring any of the destructor, copy, or move operations (even as `= default`) changes what else the compiler generates; when you declare one, decide about all five.

### optional challenge

which special members does `Config` have, and which of these lines compile?

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

the user-declared constructor suppresses the default constructor. the destructor, copy operations, and move operations are all implicitly declared as defaulted, but the copy constructor and copy assignment are defined as deleted because `std::unique_ptr` is not copyable. the move operations work and are `noexcept`, since both members' moves are.

so (1) compiles, (2) fails (deleted copy constructor), (3) compiles, (4) compiles and the vector will move on reallocation, and (5) fails (no default constructor). `Config` is move-only without a single line of special-member code, which is exactly the behavior you want for something that owns a parser.

</details>
