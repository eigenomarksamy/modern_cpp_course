---
title: containers and what they cost
standard: C++17
objective: choose a sequence container by access pattern, memory layout, and invalidation rules, starting from `std::vector`
prerequisites: noexcept-moves, unique-ptr
difficulty: 2
---

### the idea

`std::vector` is the default container in modern C++, and the reason has less to do with big-O than with memory. the standard's complexity guarantees tell you how the cost of an operation grows; they say nothing about the cache misses, allocations, and pointer chasing that decide what it costs at the sizes you actually have. and every container also makes promises about which references survive an insertion, which code tends to rely on without ever writing it down.

### understanding the concept

a container is a contract about three things: complexity of operations, memory layout, and invalidation rules. the complexity is what the standard promises. the layout is what your cache experiences. the invalidation rules are what turn a refactor into a use-after-free.

`std::vector` is the default for good reasons. elements are contiguous, so iteration walks memory linearly and the hardware prefetcher can keep up. `push_back` is amortized O(1) because capacity grows geometrically; the standard only requires the amortized bound, and the growth factor is a library choice (libstdc++ doubles, MSVC grows by 1.5x). `reserve(n)` lets you pay for that growth once. the price: inserting in the middle is O(n), and growth beyond capacity moves every element to a new buffer, which is why [[noexcept-moves]]'s `noexcept` move constructor matters.

the rest of the family, briefly:

| container | layout | lookup | insert / erase | what an insert invalidates |
|---|---|---|---|---|
| `vector` | one contiguous block | O(1) index | O(1) amortized at end, O(n) elsewhere | everything if it reallocates, else iterators at or after the insertion point |
| `array<T, N>` | inline, no heap | O(1) index | fixed size | n/a |
| `deque` | blocks of elements plus an index map | O(1) index | O(1) at both ends | at either end: all iterators, but no references |
| `list` | one node per element | O(n) | O(1) given an iterator | nothing |
| `map` / `set` | one node per element, usually a red-black tree | O(log n) | O(log n) | nothing |
| `unordered_map` | node per element plus a bucket array | O(1) average, O(n) worst | O(1) average | iterators if it rehashes, never references |

big-O hides the constant factors that often dominate at realistic sizes. every `map` or `unordered_map` insertion is a separate heap allocation, and every lookup chases pointers through nodes that may sit anywhere in memory. an `unordered_map` lookup also pays for hashing the key (cheap for an integer, real work for a long string) and for at least one indirection through the bucket array. for a few hundred small elements, a linear scan or binary search over a contiguous `vector` can win against a "faster" structure, and it can also lose. you don't know until you measure with realistic sizes and access patterns, which [[benchmarking]] covers, and [[cache-locality]] explains why memory layout moves the numbers so much.

`std::list` rarely wins on traversal speed, but it has two real advantages: insertion and erasure never invalidate references to other elements, and `splice` moves nodes between lists without copying or allocating. splicing one element or a whole list is O(1); splicing a range from a *different* list is linear in the range length, because `size()` must stay O(1).

### in code

the classic invalidation bug. it passes tests for months because small test inputs happen to fit in the existing capacity.

```cpp ub
#include <vector>
#include <string>

struct Detection { float range_m; float doppler; std::string label; };

void annotate(std::vector<Detection>& dets) {
    Detection& first = dets.front();
    dets.push_back({0.0f, 0.0f, "synthetic"});  // may reallocate
    first.label = "reference";  // BUG: UB if push_back reallocated; 'first' dangles
}

void annotate_fixed(std::vector<Detection>& dets) {
    const std::size_t first = 0;  // indices survive reallocation, references do not
    dets.push_back({0.0f, 0.0f, "synthetic"});
    dets[first].label = "reference";
}
```

calling `reserve` before taking the reference would also fix it, but that couples correctness to a capacity calculation somebody will change later. an index (or a stable id) states the intent directly.

`emplace_back` versus `push_back` is the third everyday decision:

```cpp complete
#include <vector>
#include <memory>

struct Widget { };

void fill(std::vector<std::unique_ptr<Widget>>& v, std::vector<std::vector<int>>& rows) {
    v.push_back(std::make_unique<Widget>());  // fine: object built first, then moved in
    v.emplace_back(new Widget);  // BUG: if growth throws, the raw pointer leaks

    rows.emplace_back(1'000'000);  // compiles: a row of one million zeros, via an explicit ctor
    // rows.push_back(1'000'000);  // error: no implicit conversion int -> vector<int>
}
```

`emplace_back` forwards its arguments to a constructor ([[variadic-templates]] shows how), which means it happily calls `explicit` constructors that `push_back` would refuse. use it when you are constructing from constructor arguments; when you already have an object, `push_back` says the same thing and is equivalent. since C++17, `emplace_back` returns a reference to the new element.

### in practice

back to the radar tracker. the first version stores tracks in `std::unordered_map<TrackId, Track>`, and the association stage keeps `Track*` pointers into it across frames. that works, quietly, because `unordered_map` never invalidates references, even on rehash. a later profiling session suggests a `std::vector<Track>` for faster per-frame updates. the swap compiles cleanly and then corrupts memory on the first frame that adds enough tracks to reallocate, because the code was depending on a guarantee that was never written down.

the design lesson: reference stability is part of a container's contract, and code that stores pointers or iterators into a container depends on it. if you want freedom to change containers later, hand out stable identifiers (a track id, or an index plus generation counter) instead of addresses. then the layout decision becomes a measurement question again rather than a correctness question.

### watch out for

**`reserve` changes capacity, not size.**

```cpp ub
#include <vector>

void load(std::vector<float>& samples) {
    samples.reserve(1024);
    samples[0] = 1.0f;          // BUG: size() is still 0, so this is out of bounds
}
```

`reserve` allocates room for future elements without creating any; indexing them is undefined behavior, and on most implementations it "works" until a debug build or a sanitizer notices. after `reserve`, add elements with `push_back` or `emplace_back`. if you want 1024 value-initialized elements to index into, `resize(1024)` (or construct the vector with that size) is the call you meant.

### the takeaway

pick the container by access pattern, then check the invalidation rules, then measure; start with `std::vector`, and treat reference stability as part of the interface, because whoever depends on it is coupled to your container choice.

### optional challenge

what does this guarantee, and what doesn't it?

```cpp
std::vector<int> v{1, 2, 3};
v.reserve(4);
int& r = v[0];
v.push_back(4);
v.push_back(5);
int x = r;
```

<details>
<summary>answer</summary>

`reserve(4)` guarantees `capacity() >= 4`, so the first `push_back` (size 3 to 4) cannot reallocate and `r` is still valid after it. the exact capacity after `reserve` is not specified; an implementation may allocate more than you asked for. so whether the second `push_back` (size 4 to 5) reallocates depends on the library. if it does, `r` dangles and `int x = r;` is undefined behavior. with libstdc++, `reserve(4)` on this vector yields exactly 4, so the second `push_back` reallocates. portable code cannot rely on either outcome; if it must keep `r`, it needs `reserve(5)` or an index.

</details>
