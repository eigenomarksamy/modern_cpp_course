<a id="day-20"></a>

## day 20: exception safety and error handling strategy

**reading time:** about 10 minutes · **standard:** C++17 · **builds on:** days 08, 10, 11

### the idea

"Is this function exception-safe?" is the wrong question, because it has no yes-or-no answer. The useful question is: if something in here throws halfway through, what state is the object left in? A tracker whose index map disagrees with its track list, a config that is half old and half new, a robot with half of a new trajectory: these are not crashes, they are worse. They are valid-looking objects that lie. Exception safety is about making that question answerable, and an error-handling strategy is about deciding, per API, how failure is reported at all.

### understanding the concept

There are three useful guarantees (Dave Abrahams' formulation, which the standard library documents its operations against):

| guarantee | promise if an exception escapes | example |
|---|---|---|
| **basic** | no leaks, all invariants hold, but the state may have changed | `std::vector::insert` in the middle |
| **strong** | commit or rollback: the state is as if the call never happened | `std::vector::push_back` (when the element's move is `noexcept` or it is copyable) |
| **nothrow** | the operation never fails | destructors, `swap`, `pop_back`, move constructors of most standard types |

Anything below basic (a broken invariant or a leak) is simply a bug. RAII (day 08) is what makes the basic guarantee cheap: if every resource is owned by an object, unwinding releases it without any `catch` blocks. The strong guarantee usually needs one more technique: **do all the work that can throw on the side, then commit with operations that cannot throw**. Copy-and-swap (day 11) is the classic form.

That commit step is why the nothrow guarantee matters, and why `noexcept` is a contract rather than an optimization hint. A function declared `noexcept` promises not to let an exception escape; if one tries, `std::terminate` is called, and whether the stack is unwound first is implementation-defined (with GCC 12, a local's destructor did not run before termination in a quick test). Callers can query the promise at compile time with the `noexcept(expr)` operator, and the library does: `std::vector` reallocation uses `std::move_if_noexcept`, so it moves elements only if their move constructor is `noexcept` (or the type cannot be copied), otherwise it copies to keep `push_back` strong (day 10).

Exceptions are not the only error channel, and choosing one is an API decision:

| mechanism | fits when | costs and limits |
|---|---|---|
| exceptions | failure is rare and the immediate caller can't handle it; constructors | throwing is slow and its latency hard to bound; unwind tables add binary size; invisible in signatures |
| error codes (`enum`, `std::error_code`) | failure is expected and handled close by; C interop; `-fno-exceptions` builds | easy to ignore (use `[[nodiscard]]`); constructors can't return them |
| `std::optional<T>` | "no result" needs no explanation (day 24) | carries no reason |
| result types (`std::variant<T, Error>`, day 25) | value or a reason, checked by the caller | more verbose call sites; `std::expected` is C++23 only |

On mainstream ABIs (Itanium-style table-based unwinding, used by GCC and Clang on Linux), a `try` block adds essentially no work to the non-throwing path (it can still constrain some optimizations). Throwing, though, allocates the exception object and searches unwind tables, so its cost is high and hard to bound. That is the honest basis for banning exceptions in hard real-time loops: not "exceptions are slow", but "a throw has no bounded latency". Many embedded projects go further and compile with `-fno-exceptions`, where `throw` and `try` in your code fail to compile, and failures the standard library reports by throwing (`std::bad_alloc`, `at()` out of range) end the program instead, because no handler can exist. The exact mechanism depends on how the library was built.

### in code

A track table with two structures that must agree. The first version leaves a broken invariant if the second step throws.

```cpp
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

The `try`/`catch` rollback is fine for one step. With more steps, a scope guard (day 08) that undoes on destruction unless dismissed keeps the code linear. A tempting alternative, `tracks_.reserve(tracks_.size() + 1)` before both steps, is a trap: calling it on every insert defeats geometric growth, because `reserve` may allocate exactly what you ask for, turning n inserts into O(n²) copying.

Do-the-work-then-commit, for a configuration reload:

```cpp
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

The strong guarantee costs a second object alive during the reload. That is cheap for a config and expensive for a 50 MB map, which is why the standard library gives only the basic guarantee for some operations: it refuses to charge every caller for rollback that most don't need.

### in practice

A robot arm driver library had one error convention everywhere: throw. That was right for `Arm::connect()`, called once at startup, where failure means the process cannot do its job and a clear exception with context is the best report. It was wrong for `Arm::read_joint_states()`, called at 1 kHz from the control loop, where a dropped packet is an expected event and the loop must decide within its cycle budget whether to hold position.

The revised API used a different channel per situation: `connect()` throws, the cyclic read returns a `[[nodiscard]]` status plus data, and constructors establish their invariants or throw. The rule behind it: decide by how expected the failure is, who can act on it, and the latency budget, then document the choice and apply it consistently per layer. Two habits to avoid while you are at it: using exceptions for ordinary control flow (ending a parse loop by catching), and `catch (...) {}` that swallows a failure nobody will ever see. Also avoid catching, logging, and rethrowing at every layer, which produces five log lines for one error.

### watch out for

Throw by value, catch by `const&`, and rethrow with a bare `throw;`:

```cpp
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

Catching by value slices the derived exception (day 13) and loses its message; `throw e;` then throws that sliced copy, so callers catching `std::out_of_range` miss it. `catch (const std::exception& e)` and `throw;` preserve the original object and its dynamic type.

### the takeaway

Every operation should give at least the basic guarantee, and RAII makes that nearly free. Pay for the strong guarantee where callers need commit-or-rollback, and build it from throwing work done on the side plus a `noexcept` commit. Choose the error channel per API from how expected the failure is and how quickly someone must react.

### optional challenge

Which guarantee does this give, and how would you make it strong?

```cpp
void Planner::set_waypoints(const std::vector<Pose>& w) {
    waypoints_.clear();
    for (const auto& p : w) waypoints_.push_back(p);
}
```

<details>
<summary>answer</summary>

Basic only. If a `push_back` throws partway, `waypoints_` holds a prefix of the new path: valid, no leaks, but neither the old nor the new state, which for a robot is the dangerous kind of valid. `waypoints_ = w;` looks like the fix but is not guaranteed to be strong either, because vector copy assignment may reuse its existing storage element by element. The strong version copies first and commits with a non-throwing swap: `std::vector<Pose> next(w); waypoints_.swap(next);`. The price is holding both vectors briefly.

</details>
