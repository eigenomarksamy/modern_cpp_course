<a id="day-15"></a>

## day 15: containers and what they cost

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 10, 12

### the idea

You need to keep the live tracks of a radar tracker: a few hundred entries, looked up by track id, updated every frame, occasionally created and deleted. `std::map`, `std::unordered_map`, a sorted `std::vector`? Most engineers answer from habit. The better answer starts from three questions: how is the data accessed, what does each operation cost in complexity *and* in memory traffic, and which guarantees (ordering, reference stability) does the rest of the code silently rely on?

### understanding the concept

A container is a contract about three things: complexity of operations, memory layout, and invalidation rules. The complexity is what the standard promises. The layout is what your cache experiences. The invalidation rules are what turn a refactor into a use-after-free.

`std::vector` is the default for good reasons. Elements are contiguous, so iteration walks memory linearly and the hardware prefetcher can keep up. `push_back` is amortized O(1) because capacity grows geometrically; the standard only requires the amortized bound, and the growth factor is a library choice (libstdc++ doubles, MSVC grows by 1.5x). `reserve(n)` lets you pay for that growth once. The price: inserting in the middle is O(n), and growth beyond capacity moves every element to a new buffer, which is why day 10's `noexcept` move constructor matters.

The rest of the family, briefly:

| container | layout | lookup | insert / erase | what an insert invalidates |
|---|---|---|---|---|
| `vector` | one contiguous block | O(1) index | O(1) amortized at end, O(n) elsewhere | everything if it reallocates, else iterators at or after the insertion point |
| `array<T, N>` | inline, no heap | O(1) index | fixed size | n/a |
| `deque` | blocks of elements plus an index map | O(1) index | O(1) at both ends | at either end: all iterators, but no references |
| `list` | one node per element | O(n) | O(1) given an iterator | nothing |
| `map` / `set` | one node per element, usually a red-black tree | O(log n) | O(log n) | nothing |
| `unordered_map` | node per element plus a bucket array | O(1) average, O(n) worst | O(1) average | iterators if it rehashes, never references |

Big-O hides the constant factors that often dominate at realistic sizes. Every `map` or `unordered_map` insertion is a separate heap allocation, and every lookup chases pointers through nodes that may sit anywhere in memory. An `unordered_map` lookup also pays for hashing the key (cheap for an integer, real work for a long string) and for at least one indirection through the bucket array. For a few hundred small elements, a linear scan or binary search over a contiguous `vector` can win against a "faster" structure, and it can also lose. You don't know until you measure with realistic sizes and access patterns, which day 50 covers, and day 51 explains why memory layout moves the numbers so much.

`std::list` rarely wins on traversal speed, but it has two real advantages: insertion and erasure never invalidate references to other elements, and `splice` moves nodes between lists without copying or allocating. Splicing one element or a whole list is O(1); splicing a range from a *different* list is linear in the range length, because `size()` must stay O(1).

### in code

The classic invalidation bug. It passes tests for months because small test inputs happen to fit in the existing capacity.

```cpp
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

Calling `reserve` before taking the reference would also fix it, but that couples correctness to a capacity calculation somebody will change later. An index (or a stable id) states the intent directly.

C++17 gave the associative containers better insertion functions and node handles. `try_emplace` constructs the value only if the key is absent, and does not move from its arguments when the key already exists. `insert_or_assign` says what `operator[]` plus assignment means, without requiring a default-constructible mapped type and while telling you which case happened.

```cpp
#include <map>
#include <memory>
#include <string>
#include <iostream>

struct Track { explicit Track(int id) : id{id} {} int id; };  // no default constructor

int main() {
    std::map<int, std::unique_ptr<Track>> tracks;
    auto p = std::make_unique<Track>(7);

    tracks.try_emplace(7, std::move(p));
    auto q = std::make_unique<Track>(7);
    auto [it, inserted] = tracks.try_emplace(7, std::move(q));
    std::cout << inserted << ' ' << (q != nullptr) << '\n';  // prints: 0 1  (q not consumed)

    auto [it2, ins2] = tracks.insert_or_assign(7, std::make_unique<Track>(70));
    std::cout << ins2 << ' ' << it2->second->id << '\n';      // prints: 0 70

    // Rekey a node without reallocating it: extract, edit the key, reinsert.
    auto node = tracks.extract(7);
    node.key() = 8;
    tracks.insert(std::move(node));

    std::map<int, std::unique_ptr<Track>> retired;
    retired.try_emplace(8, std::make_unique<Track>(800));
    retired.try_emplace(9, std::make_unique<Track>(9));
    tracks.merge(retired);  // moves node 9 across; key 8 already exists, so it stays behind
    std::cout << tracks.size() << ' ' << retired.size() << '\n';  // prints: 2 1
}
```

`extract` and `merge` relink existing nodes, so no element is copied, moved, or reallocated, and pointers to the elements remain valid (they now refer into the other container). That makes them the right tool for move-only values and for rekeying, which used to require erase plus a fresh insert.

`emplace_back` versus `push_back` is the third everyday decision:

```cpp
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

`emplace_back` forwards its arguments to a constructor (day 19 shows how), which means it happily calls `explicit` constructors that `push_back` would refuse. Use it when you are constructing from constructor arguments; when you already have an object, `push_back` says the same thing and is equivalent. Since C++17, `emplace_back` returns a reference to the new element.

### in practice

Back to the radar tracker. The first version stores tracks in `std::unordered_map<TrackId, Track>`, and the association stage keeps `Track*` pointers into it across frames. That works, quietly, because `unordered_map` never invalidates references, even on rehash. A later profiling session suggests a `std::vector<Track>` for faster per-frame updates. The swap compiles cleanly and then corrupts memory on the first frame that adds enough tracks to reallocate, because the code was depending on a guarantee that was never written down.

The design lesson: reference stability is part of a container's contract, and code that stores pointers or iterators into a container depends on it. If you want freedom to change containers later, hand out stable identifiers (a track id, or an index plus generation counter) instead of addresses. Then the layout decision becomes a measurement question again rather than a correctness question.

### watch out for

`operator[]` on `std::map` and `std::unordered_map` inserts a default-constructed value when the key is missing. A "read" such as `if (tracks[id]) ...` grows the table, may allocate, and for `unordered_map` may rehash and invalidate every iterator you hold. It also cannot be called on a `const` map. Use `find` (or C++20 `contains`) to query, `try_emplace` or `insert_or_assign` to write.

### the takeaway

Pick the container by access pattern, then check the invalidation rules, then measure. Start with `std::vector`, and treat reference stability as part of the interface: whoever depends on it is coupled to your container choice.

### optional challenge

What does this guarantee, and what doesn't it?

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

`reserve(4)` guarantees `capacity() >= 4`, so the first `push_back` (size 3 to 4) cannot reallocate and `r` is still valid after it. The exact capacity after `reserve` is not specified; an implementation may allocate more than you asked for. So whether the second `push_back` (size 4 to 5) reallocates depends on the library. If it does, `r` dangles and `int x = r;` is undefined behavior. With libstdc++, `reserve(4)` on this vector yields exactly 4, so the second `push_back` reallocates. Portable code cannot rely on either outcome; if it must keep `r`, it needs `reserve(5)` or an index.

</details>
