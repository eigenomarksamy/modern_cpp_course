---
title: exception safety guarantees
standard: C++17
objective: state which guarantee (basic, strong, nothrow) an operation gives, and build the strong guarantee from work on the side plus a noexcept commit
prerequisites: rule-of-zero, scope-guards
difficulty: 2
---

### the idea

"is this function exception-safe?" is the wrong question, because it has no yes-or-no answer. the useful question is: if something in here throws halfway through, what state is the object left in? a tracker whose index map disagrees with its track list, a config that is half old and half new, a robot with half of a new trajectory: these are not crashes, they are worse. they are valid-looking objects that lie. exception safety is about making that question answerable, and an error-handling strategy is about deciding, per API, how failure is reported at all.

### understanding the concept

there are three useful guarantees (Dave Abrahams' formulation, which the standard library documents its operations against):

| guarantee | promise if an exception escapes | example |
|---|---|---|
| **basic** | no leaks, all invariants hold, but the state may have changed | `std::vector::insert` in the middle |
| **strong** | commit or rollback: the state is as if the call never happened | `std::vector::push_back` (when the element's move is `noexcept` or it is copyable) |
| **nothrow** | the operation never fails | destructors, `swap`, `pop_back`, move constructors of most standard types |

anything below basic (a broken invariant or a leak) is simply a bug. RAII ([[raii]]) is what makes the basic guarantee cheap: if every resource is owned by an object, unwinding releases it without any `catch` blocks. the strong guarantee usually needs one more technique: **do all the work that can throw on the side, then commit with operations that cannot throw**. copy-and-swap ([[rule-of-zero]]) is the classic form.

that commit step is why the nothrow guarantee matters, and why `noexcept` is a contract rather than an optimization hint. a function declared `noexcept` promises not to let an exception escape; if one tries, `std::terminate` is called, and whether the stack is unwound first is implementation-defined (with GCC 12, a local's destructor did not run before termination in a quick test). callers can query the promise at compile time with the `noexcept(expr)` operator, and the library does: `std::vector` reallocation uses `std::move_if_noexcept`, so it moves elements only if their move constructor is `noexcept` (or the type cannot be copied), otherwise it copies to keep `push_back` strong ([[noexcept-moves]]).

### in code

a track table with two structures that must agree. the first version leaves a broken invariant if the second step throws.

```cpp complete
#include <stdexcept>
#include <unordered_map>
#include <vector>

struct Track { int id; double range_m; };

class TrackTable {
    std::vector<Track> tracks_;
    std::unordered_map<int, std::size_t> index_;   // invariant: index_[t.id] == position of t
public:
    void add_broken(Track t) {
        tracks_.push_back(t);                                 // may throw: fine, nothing changed
        index_.emplace(t.id, tracks_.size() - 1);             // may throw: BUG, track without index
    }

    void add(Track t) {                                       // strong guarantee
        if (index_.count(t.id)) throw std::invalid_argument("duplicate track id");
        tracks_.push_back(t);                                 // strong on its own
        try {
            index_.emplace(t.id, tracks_.size() - 1);
        } catch (...) {
            tracks_.pop_back();                               // rollback cannot throw
            throw;                                            // rethrow the original exception
        }
    }
};
```

the `try`/`catch` rollback is fine for one step. with more steps, a scope guard ([[scope-guards]]) that undoes on destruction unless dismissed keeps the code linear. a tempting alternative, `tracks_.reserve(tracks_.size() + 1)` before both steps, is a trap: calling it on every insert defeats geometric growth, because `reserve` may allocate exactly what you ask for, turning n inserts into O(n²) copying.

do-the-work-then-commit, for a configuration reload:

```cpp complete
#include <string>
#include <utility>
#include <vector>

class ControllerConfig {
    std::vector<double> gains_;
    std::string profile_;
public:
    static ControllerConfig parse(const std::string& text);   // may throw on bad input

    void reload(const std::string& text) {
        ControllerConfig next = parse(text);   // all failure-prone work happens on the side
        swap(next);                            // commit: cannot throw
    }                                          // old state is destroyed with 'next'

    void swap(ControllerConfig& other) noexcept {
        gains_.swap(other.gains_);
        profile_.swap(other.profile_);
    }
};
```

the strong guarantee costs a second object alive during the reload. that is cheap for a config and expensive for a 50 MB map, which is why the standard library gives only the basic guarantee for some operations: it refuses to charge every caller for rollback that most don't need.

### in practice

the strong guarantee is worth its price where a half-applied change is dangerous: a robot's trajectory, a controller's configuration, a ledger, anything another component will act on as if it were complete. it is often not worth it for state that is merely a cache, a log buffer, or a working set the next cycle rebuilds anyway; there the basic guarantee (no leaks, invariants hold) is enough, and paying for a second copy of the data on every call would be waste. the useful habit is to decide per operation and write the decision into the API documentation ("`set_trajectory`: strong; `append_samples`: basic"), the way the standard library documents its own operations. callers can then reason about failure without reading your implementation.

### watch out for

throw by value, catch by `const&`, and rethrow with a bare `throw;`:

```cpp complete
#include <cstdio>
#include <stdexcept>

void handle() {
    try {
        throw std::out_of_range("joint index 7");
    } catch (std::exception e) {   // BUG: copies and slices to std::exception (GCC: -Wcatch-value)
        std::puts(e.what());       // prints implementation-defined text; libstdc++: "std::exception"
        throw e;                   // throws a new std::exception: the out_of_range is gone
    }
}
```

catching by value slices the derived exception ([[virtual-destructors-slicing]]) and loses its message; `throw e;` then throws that sliced copy, so callers catching `std::out_of_range` miss it. `catch (const std::exception& e)` and `throw;` preserve the original object and its dynamic type.

### the takeaway

every operation should give at least the basic guarantee, and RAII makes that nearly free; pay for the strong guarantee where callers need commit-or-rollback, and build it from throwing work done on the side plus a `noexcept` commit.

### optional challenge

which guarantee does this give, and how would you make it strong?

```cpp
void Planner::set_waypoints(const std::vector<Pose>& w) {
    waypoints_.clear();
    for (const auto& p : w) waypoints_.push_back(p);
}
```

<details>
<summary>answer</summary>

basic only. if a `push_back` throws partway, `waypoints_` holds a prefix of the new path: valid, no leaks, but neither the old nor the new state, which for a robot is the dangerous kind of valid. `waypoints_ = w;` looks like the fix but is not guaranteed to be strong either, because vector copy assignment may reuse its existing storage element by element. the strong version copies first and commits with a non-throwing swap: `std::vector<Pose> next(w); waypoints_.swap(next);`. the price is holding both vectors briefly.

</details>
