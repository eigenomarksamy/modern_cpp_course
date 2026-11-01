---
title: maps, sets, and node handles
standard: C++17
objective: choose between ordered, hashed, and flat associative containers, and use the C++17 insertion functions and node handles
prerequisites: sequence-containers
difficulty: 2
---

### the idea

you need to keep the live tracks of a radar tracker: a few hundred entries, looked up by track id, updated every frame, occasionally created and deleted. `std::map`, `std::unordered_map`, a sorted `std::vector`? most engineers answer from habit. the better answer starts from three questions: how is the data accessed, what does each operation cost in complexity *and* in memory traffic, and which guarantees (ordering, reference stability) does the rest of the code silently rely on?

### understanding the concept

`std::map` and `std::set` are ordered: usually a red-black tree with one heap node per element, O(log n) lookup, iteration in key order, and references that stay valid until the element is erased. `std::unordered_map` and `std::unordered_set` are hash tables: one node per element plus a bucket array, O(1) lookup on average (O(n) in the worst case), no useful order, and a rehash on growth that invalidates iterators but never references. the unordered containers need a hash function and an equality comparison for the key, and they pay for hashing on every lookup.

a third option is not a node container at all: a sorted `std::vector` searched with `std::lower_bound`. it gives up cheap insertion in the middle and in exchange has contiguous memory, no per-element allocation, and the smallest footprint. for data that is built once and read often, it is frequently the fastest of the three. (C++23 standardizes the idea as `std::flat_map`.)

C++17 gave the associative containers better insertion functions and node handles. `try_emplace` constructs the value only if the key is absent, and does not move from its arguments when the key already exists. `insert_or_assign` says what `operator[]` plus assignment means, without requiring a default-constructible mapped type and while telling you which case happened.

### in code

```cpp complete
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

`extract` and `merge` relink existing nodes, so no element is copied, moved, or reallocated, and pointers to the elements remain valid (they now refer into the other container). that makes them the right tool for move-only values and for rekeying, which used to require erase plus a fresh insert.

### in practice

a lookup table built at startup and read every cycle, such as per-channel calibration for a few hundred radar channels, is the textbook case for the sorted vector:

```cpp complete
#include <algorithm>
#include <vector>

struct ChannelCal { int channel; double gain; double offset_m; };

const ChannelCal* find_cal(const std::vector<ChannelCal>& sorted, int channel) {
    auto it = std::lower_bound(sorted.begin(), sorted.end(), channel,
                               [](const ChannelCal& c, int ch) { return c.channel < ch; });
    return (it != sorted.end() && it->channel == channel) ? &*it : nullptr;
}
```

the table is sorted once after loading; every lookup is a binary search over contiguous memory with no allocation. whether this beats `std::unordered_map<int, ChannelCal>` at your size is a measurement question ([[benchmarking]]), but it is a strong default for read-mostly data, and it never has a rehash pause in the middle of a control cycle.

### watch out for

`operator[]` on `std::map` and `std::unordered_map` inserts a default-constructed value when the key is missing. a "read" such as `if (tracks[id]) ...` grows the table, may allocate, and for `unordered_map` may rehash and invalidate every iterator you hold. it also cannot be called on a `const` map. use `find` (or C++20 `contains`) to query, `try_emplace` or `insert_or_assign` to write.

### the takeaway

use an ordered map when you need order or stable references, a hash map when lookups dominate and keys hash cheaply, and a sorted vector when the data is read far more often than it changes; query with `find`, write with `try_emplace` and `insert_or_assign`.

### optional challenge

what does this print, and which line does not compile?

```cpp
std::map<std::string, int> counts;
if (counts["lidar"] > 0) { /* ... */ }
std::cout << counts.size() << '\n';
const auto& view = counts;
std::cout << view["radar"] << '\n';
```

<details>
<summary>answer</summary>

the first output line prints `1`: `counts["lidar"]` inserted a value-initialized `int` for the missing key, so the "read" grew the map. the last line does not compile, because `operator[]` may insert and therefore has no `const` overload. use `view.find("radar")`, `view.count("radar")`, or C++20's `view.contains("radar")` to query, and `view.at("radar")` if a missing key is an error (it throws `std::out_of_range`).

</details>
