<a id="day-10"></a>

## day 10: copy and move semantics

**reading time:** about 10 minutes · **standard:** C++17 · **builds on:** days 05, 08, 09

### the idea

`std::move` does not move anything. It compiles to no instructions at all. Whether a move happens, and what it costs, is decided entirely by which constructor or assignment operator overload resolution picks afterwards, and that is code you (or the compiler) wrote.

Once you see moves as "an overload that is allowed to steal, selected by value category", the surprising cases stop being surprising: the `std::move` that copies, the vector that copies when you expected moves, and the `return std::move(x)` that makes code slower.

### understanding the concept

Copying gives the destination its own independent value; the source is untouched. For a type that owns a resource through a pointer, that means duplicating the resource (a deep copy). Copying just the pointer (a shallow copy) leaves two owners, and day 08's destructor will release the same resource twice.

Moving gives the destination the source's value and permits the source to be left in a cheaper, emptier state. For a pointer-owning type that means taking the pointer and nulling the source: O(1), no allocation, usually no way to fail.

The selection is plain overload resolution on day 05's value categories. A `T&&` parameter binds to rvalues (prvalues and xvalues); a `const T&` binds to anything. Given both, an rvalue argument prefers `T&&`. And `std::move` is just a cast that turns an lvalue into an xvalue:

```cpp
template <typename T>
constexpr std::remove_reference_t<T>&& move(T&& t) noexcept {
    return static_cast<std::remove_reference_t<T>&&>(t);
}
```

What state does the source end up in? For standard library types the rule is "valid but unspecified": the object still satisfies its invariants, so you can destroy it, assign to it, or call functions without preconditions (`size()`, `clear()`), but you must not assume a particular value. A moved-from `std::vector` is empty on every mainstream implementation, but that is not a guarantee you should build on. For your own types, the moved-from state is part of your contract: decide it and document it.

### in code

The bug that motivates all of this. A class owns a raw buffer and relies on the implicitly generated copy:

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

The fix spells out what copying and moving mean for this resource:

```cpp
#include <algorithm>
#include <cstddef>
#include <utility>

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

Three details carry the weight. The copy assignment allocates before it releases, so if `new` throws, `*this` is unchanged (the strong guarantee, day 20). The move assignment checks for self-assignment because without the check, `b = std::move(b)` would delete the buffer and then adopt the dangling pointer. And `std::exchange` keeps "take the value, leave a replacement" on one line, which makes the moved-from contract visible.

That is a lot of code for one pointer, and it is easy to get subtly wrong. Day 11 shows how to make almost all of it disappear.

Now predict the output. `Track` has a hand-written move constructor that is not `noexcept`:

```cpp
#include <cstdio>
#include <string>
#include <vector>

struct Track {
    std::string id;
    explicit Track(std::string s) : id(std::move(s)) {}
    Track(const Track& o) : id(o.id) { std::puts("copy"); }
    Track(Track&& o) : id(std::move(o.id)) { std::puts("move"); }   // not noexcept
};

int main() {
    std::vector<Track> tracks;
    tracks.reserve(1);
    tracks.emplace_back("T-001");
    tracks.emplace_back("T-002");   // exceeds capacity: reallocates
}
```

It prints `copy`. When `push_back` or `emplace_back` reallocates, `std::vector` promises the strong guarantee: if an exception escapes, the vector is unchanged. Moving the old elements to the new block would gut them, so a move that throws halfway through leaves no way back. The vector therefore uses `std::move_if_noexcept`: it moves only if the move constructor is `noexcept` (or the type cannot be copied at all, in which case the effects of a throwing move are unspecified). Add `noexcept` to the move constructor and the program prints `move`.

Implicitly generated and `= default` move constructors are `noexcept` automatically when every member's move is. The trap is the hand-written one.

### in practice

A radar processing chain passes large frames between stages. A stage that keeps what it receives takes the frame by value (a "sink" parameter) and moves it into place:

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

The signature tells the story: by-value parameter, caller writes `std::move` when it is done with the object, copies only when it explicitly keeps one. Inside `acquire`, `return f;` either elides the copy entirely (NRVO, optional but routinely done) or, failing that, treats `f` as an rvalue and moves. Writing `return std::move(f);` changes the operand from a plain name to an xvalue, which disqualifies NRVO, so you trade a possibly free return for a guaranteed move. GCC 12 flags it under `-Wall` with `-Wpessimizing-move`. Use an explicit `std::move` in a `return` only when returning something that is not a plain local or parameter, such as a data member.

### watch out for

**`std::move` on a `const` object copies, silently.**

```cpp
const std::string config = load_config();
std::string owned = std::move(config);   // copies: const std::string&& binds to const&
```

`std::move(config)` produces `const std::string&&`. The move constructor wants `std::string&&`, which cannot bind to a const object, so overload resolution falls back to the copy constructor. No warning, no error, just a copy. The same applies to `const` data members: a class with a `const std::vector` member cannot be moved efficiently, because that member is copied every time. Declare locals `const` freely, but not ones you intend to move from, and think twice about `const` members in types that will be moved.

**Use after move is legal and still a bug.** Reading `frame.size()` after `submit(std::move(frame))` is well-defined for a standard type and almost always a logic error. `clang-tidy`'s `bugprone-use-after-move` check finds most of these.

### the takeaway

`std::move` only grants permission; the move constructor does the work, and `noexcept` decides whether containers will trust it.

### optional challenge

`Buffer`'s copy assignment uses `if (this != &o)`. Is the check required for correctness, or only an optimization? What about the move assignment?

<details>
<summary>answer</summary>

For the copy assignment it is only an optimization. Because it allocates and copies into `fresh` before deleting the old buffer, self-assignment copies the data into a new block, frees the old one, and ends up with an equal value. The check just skips a pointless allocation.

For the move assignment it is required for correctness as written. Without it, `b = std::move(b)` runs `delete[] data_`, and then `data_ = std::exchange(o.data_, nullptr)` reads the freed pointer out of the same object (briefly setting it to null) and stores it straight back. `b` now holds a dangling pointer with its old size, and its destructor will `delete[]` the block a second time: undefined behavior. Self-move is rare in direct code but appears through aliasing: `std::swap(x, x)` performs `x = std::move(x)` internally, and so does `v[i] = std::move(v[j])` when `i == j`.

</details>
