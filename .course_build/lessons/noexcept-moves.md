---
title: noexcept moves and the strong guarantee
standard: C++17
objective: explain why containers copy instead of moving when a move constructor may throw, and make move operations noexcept correctly
prerequisites: move-semantics
difficulty: 2
---

### the idea

a `std::vector<Track>` grows past its capacity and reallocates. `Track` has a perfectly good move constructor, and the vector copies every element anyway. nothing is broken; the vector is keeping a promise you probably did not know it made, and one missing keyword on your move constructor decides which way it keeps it.

### understanding the concept

when `push_back` needs more room, the vector allocates a new block, transfers the old elements into it, and frees the old block. the standard promises the **strong guarantee** for this: if an exception escapes, the vector is unchanged. with copies that is easy, because the originals are untouched until the end. with moves it is not: if the fifth move throws, the first four elements have already been gutted, and there is no reliable way to move them back.

so the vector uses `std::move_if_noexcept`: it moves elements only if the move constructor is declared `noexcept`, and otherwise copies them. (if the type cannot be copied at all, it moves anyway and the guarantee is weakened.) `noexcept` is part of a function's type-level contract: it is visible to code like this at compile time, through traits such as `std::is_nothrow_move_constructible_v<T>`. if a `noexcept` function does throw, the exception does not propagate: `std::terminate` is called.

### in code

now predict the output. `Track` has a hand-written move constructor that is not `noexcept`:

```cpp complete
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

it prints `copy`. when `push_back` or `emplace_back` reallocates, `std::vector` promises the strong guarantee: if an exception escapes, the vector is unchanged. moving the old elements to the new block would gut them, so a move that throws halfway through leaves no way back. the vector therefore uses `std::move_if_noexcept`: it moves only if the move constructor is `noexcept` (or the type cannot be copied at all, in which case the effects of a throwing move are unspecified). add `noexcept` to the move constructor and the program prints `move`.

implicitly generated and `= default` move constructors are `noexcept` automatically when every member's move is. the trap is the hand-written one.

### in practice

a move constructor that only transfers pointers and integers cannot fail, so it should say so. the same holds for move assignment and `swap`. in practice the rule is simple: let the compiler generate moves whenever you can (they are `noexcept` exactly when every member's move is), and when you write them by hand, add `noexcept` and keep the bodies to operations that cannot throw. you can lock the property in where it matters:

```cpp
#include <type_traits>

static_assert(std::is_nothrow_move_constructible_v<Track>,
              "Track is stored in vectors; a throwing move would make them copy");
```

that assertion turns "someone added a `std::string` member with a throwing constructor call to the move constructor" from a silent slowdown into a build error.

### watch out for

**do not promise what a member cannot keep.** a hand-written move constructor that calls something that can throw, such as allocating a fresh buffer for the source to keep, must not be marked `noexcept`, because a throw would terminate the program. moving a member that is itself not nothrow-movable has the same problem. for class templates, write the condition instead of guessing: `noexcept(std::is_nothrow_move_constructible_v<T>)` makes the wrapper exactly as `noexcept` as what it wraps.

### the takeaway

containers trust a move only if it is `noexcept`; let the compiler generate moves when you can, mark hand-written ones `noexcept`, and assert the property for types that live in containers.

### optional challenge

`Track` has a `std::string id` and a hand-written move constructor that is correctly `noexcept`. someone adds `~Track() { log("released"); }` to it. does a `std::vector<Track>` still move on reallocation?

<details>
<summary>answer</summary>

yes, in this case. the hand-written move constructor is still declared, and adding a destructor does not remove a user-declared move constructor, so the vector keeps moving. the trap from [[special-members]] applies only to *implicit* moves: had `Track` relied on the compiler-generated move constructor, declaring the destructor would have stopped it from being generated, and reallocation would silently fall back to copying.

</details>
