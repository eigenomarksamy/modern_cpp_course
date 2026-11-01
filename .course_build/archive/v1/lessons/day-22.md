<a id="day-22"></a>

## day 22: structured bindings, init-statements, and helpful attributes

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days 03, 15

### the idea

Look at a typical pre-C++17 map lookup: an iterator declared at function scope, a comparison against `end()`, then `it->first` and `it->second` sprinkled through the body. Nothing is wrong with it, but the names say nothing (`first` of what?), and `it` stays in scope long after it stopped being meaningful. Week 4 opens with the small C++17 features that fix exactly this kind of noise. None of them is deep on its own; together they change how ordinary code reads, and the next six days build on them.

### understanding the concept

**Structured bindings** let you give names to the parts of an object:

```cpp
auto [it, inserted] = counters.try_emplace(topic);
```

The mechanics matter more than the syntax. The compiler introduces a hidden variable, call it `e`, initialized from the right-hand side exactly as if you had written `auto e = counters.try_emplace(topic);`. The names `it` and `inserted` then refer to parts of `e`. Everything written before the brackets (`auto`, `const auto&`, `auto&&`) applies to `e`, not to the individual names. (C++17 also forbids `static`, `thread_local`, and `constexpr` on a structured binding; C++20 allows the first two.)

There are three ways a type can be decomposed:

| kind | example | what the names refer to |
|---|---|---|
| array | `int a[3]` | the elements of `e` |
| tuple-like | `std::pair`, `std::tuple`, `std::array` | the results of `get<i>(e)`, via the tuple protocol |
| aggregate-ish class | `struct Pose { double x, y, theta; };` | the non-static data members of `e`, in declaration order |

The class case requires all non-static data members to be public and declared in the same class (or the same base). Your own non-aggregate types can opt in by specializing `std::tuple_size`, `std::tuple_element`, and providing `get`; that is rarely worth the boilerplate.

Two consequences follow from "names for parts of a hidden object":

- `auto [a, b] = obj;` copies the whole of `obj` into `e`. `auto& [a, b] = obj;` binds `e` to `obj`. And because `e` follows the normal rules from day 03, `const auto& [a, b] = make_pair_func();` extends the temporary's lifetime for as long as `e` lives.
- The names are not variables in the usual sense. `decltype(a)` yields the declared type of the member (`double`, not `double&`), and in C++17 a lambda cannot capture a structured binding. C++20 lifted that restriction. GCC 12 quietly accepts the capture even in `-std=c++17 -pedantic` mode, and other compilers in C++17 mode reject it or warn, so portable C++17 code uses an init-capture: `[a = a]`.

**Init-statements** for `if` and `switch` (also C++17) let you declare a variable whose scope is the whole statement, including the `else` branch:

```cpp
if (auto it = m.find(key); it != m.end()) { /* use it */ } else { /* it is still in scope */ }
```

It is the same scoping rule `for` always had. The point is not saving a line; it is that a reader knows `it` cannot affect anything after the closing brace.

Finally, three **standard attributes** became part of daily use in C++17. `[[nodiscard]]` asks the compiler to warn when a return value is ignored; it can go on a function or on a type, in which case every function returning that type by value is covered. `[[maybe_unused]]` silences unused warnings on a variable, parameter, or function. `[[fallthrough]]` documents an intentional fall-through in a `switch`. All three are hints: the standard only encourages a diagnostic, and the program's meaning never changes.

### in code

First, predict the output. The binding names look like independent variables, but they are not.

```cpp
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

Second, a before/after modernization of a lookup in a joint-gain table.

```cpp
#include <cstdio>
#include <map>
#include <string>

// before: C++03 style
bool find_gain(const std::map<std::string, double>& gains,
               const std::string& joint, double& out) {
    std::map<std::string, double>::const_iterator it = gains.find(joint);
    if (it == gains.end())
        return false;
    out = it->second;
    return true;
}

// after: C++17
[[nodiscard]] bool find_gain(const std::map<std::string, double>& gains,
                             const std::string& joint, double& out) {
    if (auto it = gains.find(joint); it != gains.end()) {
        out = it->second;
        return true;
    }
    return false;
}

void dump(const std::map<std::string, double>& gains) {
    for (const auto& [joint, gain] : gains)          // instead of p.first, p.second
        std::printf("%s: %.3f\n", joint.c_str(), gain);
}
```

The `[[nodiscard]]` is the most valuable change here: with an out-parameter, a caller who ignores the `bool` and uses `out` anyway may read an uninitialized `double`, which is undefined behavior (day 06). Now they at least get a warning. The out-parameter itself is still awkward; day 24 replaces it with `std::optional<double>`.

Third, `switch` with an initializer plus the other two attributes:

```cpp
#include <cassert>

enum class Mode { idle, homing, tracking, fault };

struct Controller {
    Mode mode() const;
    void zero_encoders();
    void run_loop();
    [[nodiscard]] bool push(double sample);
};

void step(Controller& c, double sample) {
    switch (auto m = c.mode(); m) {
    case Mode::homing:
        c.zero_encoders();
        [[fallthrough]];               // deliberate: homing also runs the loop
    case Mode::tracking:
        c.run_loop();
        break;
    case Mode::idle:
    case Mode::fault:
        break;
    }
    [[maybe_unused]] const bool ok = c.push(sample);
    assert(ok);                        // with NDEBUG, ok would otherwise be "unused"
}
```

Without `[[fallthrough]]`, GCC and Clang warn under `-Wimplicit-fallthrough` (enabled by `-Wextra` in GCC). Empty case labels stacked together, like `idle` and `fault`, never need it.

### in practice

A telemetry aggregator receives messages tagged with a topic string and keeps per-topic statistics. The hot path is "find or create the entry, then update it", and C++17 lets that read as one thought:

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

`try_emplace` (day 15) returns `pair<iterator, bool>`; naming those parts `it` and `inserted` removes a whole category of `.first.second` confusion. The second binding uses `auto&` so updates land in the map rather than in a copy. Note the design aspect: the binding names are local documentation, but they are not part of `Stats`'s interface. Rename a member and nothing breaks here; reorder members and something does, which brings us to the trap.

### watch out for

Bindings to a class are **positional**. They follow member declaration order, not names:

```cpp
struct Range { double min_m, max_m; };
auto [lo, hi] = gate.range;          // lo = min_m, hi = max_m

// six months later someone "tidies" the struct:
struct Range { double max_m, min_m; };   // BUG: lo and hi silently swap
```

Because both members are `double`, every use still compiles and no warning fires. Field access by name (`r.min_m`) is immune. So use structured bindings freely for `pair`, `tuple`, map entries, and small local aggregates whose layout is effectively fixed (a 2D point). For a struct that lives in a widely used header and may evolve, member access is the more robust coupling. The same applies to returning a `std::tuple<double, double, double>` from an API: the bindings at the call site are only as good as everyone's memory of the order. A named struct is usually the better contract.

### the takeaway

A structured binding names the parts of one hidden object; the qualifiers apply to that object, and the names follow member order. Pair it with `if`/`switch` initializers to keep helper variables scoped to the decision they serve, and use `[[nodiscard]]` on anything whose result must not be dropped.

### optional challenge

What does this print, and why does the second loop compile even though `k` would have to be a `const std::string`?

```cpp
std::map<std::string, int> m{{"a", 1}};
for (auto [k, v] : m) v += 10;
std::printf("%d\n", m["a"]);
for (auto& [k, v] : m) v += 10;
std::printf("%d\n", m["a"]);
```

<details>
<summary>answer</summary>

It prints `1`, then `11`. In the first loop the hidden object is a copy of each `std::pair<const std::string, int>`, so `v += 10` modifies the copy. In the second loop the hidden object is an `auto&` bound to the map's element. The `auto&` deduces `std::pair<const std::string, int>&`, so `k` names a `const std::string` member and `v` names a mutable `int`. The `const` comes from the element type, not from the binding, which is why `auto&` works here without any `const` written by you.

</details>
