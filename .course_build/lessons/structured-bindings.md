---
title: structured bindings
standard: C++17
objective: name the parts of pairs, tuples, arrays, and aggregates with structured bindings, and know what the qualifiers and names really refer to
prerequisites: associative-containers, temporaries-dangling
difficulty: 2
---

### the idea

look at a typical pre-C++17 map loop or insertion: `it->first`, `it->second`, `result.first->second`, and `result.second` sprinkled through the body. nothing is wrong with it, but the names say nothing (`first` of what?), and every reader has to decode them again. structured bindings let you name the parts of a result where you receive it. the syntax is small; what it actually declares is less obvious than it looks.

### understanding the concept

**structured bindings** let you give names to the parts of an object:

```cpp
auto [it, inserted] = counters.try_emplace(topic);
```

the mechanics matter more than the syntax. the compiler introduces a hidden variable, call it `e`, initialized from the right-hand side exactly as if you had written `auto e = counters.try_emplace(topic);`. the names `it` and `inserted` then refer to parts of `e`. everything written before the brackets (`auto`, `const auto&`, `auto&&`) applies to `e`, not to the individual names. (C++17 also forbids `static`, `thread_local`, and `constexpr` on a structured binding; C++20 allows the first two.)

there are three ways a type can be decomposed:

| kind | example | what the names refer to |
|---|---|---|
| array | `int a[3]` | the elements of `e` |
| tuple-like | `std::pair`, `std::tuple`, `std::array` | the results of `get<i>(e)`, via the tuple protocol |
| aggregate-ish class | `struct Pose { double x, y, theta; };` | the non-static data members of `e`, in declaration order |

the class case requires all non-static data members to be public and declared in the same class (or the same base). your own non-aggregate types can opt in by specializing `std::tuple_size`, `std::tuple_element`, and providing `get`; that is rarely worth the boilerplate.

two consequences follow from "names for parts of a hidden object":

- `auto [a, b] = obj;` copies the whole of `obj` into `e`. `auto& [a, b] = obj;` binds `e` to `obj`. and because `e` follows the normal rules from [[temporaries-dangling]], `const auto& [a, b] = make_pair_func();` extends the temporary's lifetime for as long as `e` lives.
- the names are not variables in the usual sense. `decltype(a)` yields the declared type of the member (`double`, not `double&`), and in C++17 a lambda cannot capture a structured binding. C++20 lifted that restriction. GCC 12 quietly accepts the capture even in `-std=c++17 -pedantic` mode, and other compilers in C++17 mode reject it or warn, so portable C++17 code uses an init-capture: `[a = a]`.

### in code

first, predict the output. the binding names look like independent variables, but they are not.

```cpp complete
#include <cstdio>
#include <type_traits>

struct Pose { double x, y, theta; };

int main() {
    Pose p{1.0, 2.0, 0.5};

    auto [x, y, th] = p;       // hidden copy of p; x, y, th name its members
    x = 10.0;                  // modifies the copy

    auto& [rx, ry, rth] = p;   // hidden reference to p
    ry = 20.0;                 // modifies p.y

    std::printf("%.1f %.1f %.1f\n", x, p.x, p.y);         // prints: 10.0 1.0 20.0
    static_assert(std::is_same_v<decltype(ry), double>);   // not double&
}
```

### in practice

a telemetry aggregator receives messages tagged with a topic string and keeps per-topic statistics. the hot path is "find or create the entry, then update it", and C++17 lets that read as one thought:

```cpp
#include <cstdint>

struct Stats { std::uint64_t count = 0; double last = 0.0; };

void on_message(std::map<std::string, Stats>& stats, const std::string& topic, double value) {
    auto [it, inserted] = stats.try_emplace(topic);   // one lookup, no default-then-assign
    if (inserted)
        std::printf("new topic: %s\n", topic.c_str());
    auto& [count, last] = it->second;
    ++count;
    last = value;
}
```

`try_emplace` ([[associative-containers]]) returns `pair<iterator, bool>`; naming those parts `it` and `inserted` removes a whole category of `.first.second` confusion. the second binding uses `auto&` so updates land in the map rather than in a copy. note the design aspect: the binding names are local documentation, but they are not part of `Stats`'s interface. rename a member and nothing breaks here; reorder members and something does, which brings us to the trap.

### watch out for

bindings to a class are **positional**. they follow member declaration order, not names:

```cpp
struct Range { double min_m, max_m; };
auto [lo, hi] = gate.range;          // lo = min_m, hi = max_m

// six months later someone "tidies" the struct:
struct Range { double max_m, min_m; };   // BUG: lo and hi silently swap
```

because both members are `double`, every use still compiles and no warning fires. field access by name (`r.min_m`) is immune. so use structured bindings freely for `pair`, `tuple`, map entries, and small local aggregates whose layout is effectively fixed (a 2D point). for a struct that lives in a widely used header and may evolve, member access is the more robust coupling. the same applies to returning a `std::tuple<double, double, double>` from an API: the bindings at the call site are only as good as everyone's memory of the order. a named struct is usually the better contract.

### the takeaway

a structured binding names the parts of one hidden object: the qualifiers apply to that object, and the names follow member order, so use them freely for pairs, tuples, and map entries, and prefer member access for structs that may evolve.

### optional challenge

what does this print, and why does the second loop compile even though `k` would have to be a `const std::string`?

```cpp
std::map<std::string, int> m{{"a", 1}};
for (auto [k, v] : m) v += 10;
std::printf("%d\n", m["a"]);
for (auto& [k, v] : m) v += 10;
std::printf("%d\n", m["a"]);
```

<details>
<summary>answer</summary>

it prints `1`, then `11`. in the first loop the hidden object is a copy of each `std::pair<const std::string, int>`, so `v += 10` modifies the copy. in the second loop the hidden object is an `auto&` bound to the map's element. the `auto&` deduces `std::pair<const std::string, int>&`, so `k` names a `const std::string` member and `v` names a mutable `int`. the `const` comes from the element type, not from the binding, which is why `auto&` works here without any `const` written by you.

</details>
