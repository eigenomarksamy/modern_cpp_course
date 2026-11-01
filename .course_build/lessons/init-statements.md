---
title: if and switch initializers, and attributes that catch mistakes
standard: C++17
objective: scope helper variables to the decision they serve with if and switch initializers, and use nodiscard, maybe_unused, and fallthrough to make intent checkable
prerequisites: structured-bindings
difficulty: 1
---

### the idea

an iterator declared at function scope for one lookup stays in scope for the rest of the function, where it can be reused by mistake. a function whose result must be checked returns a `bool` that callers forget to look at. a `switch` case falls through to the next one, and nobody can tell whether that was intended. none of these is a bug yet; each is a place where intent lives in the author's head instead of in the code. C++17 added small features that move it into the code, where the compiler can check it.

### understanding the concept

**init-statements** for `if` and `switch` (also C++17) let you declare a variable whose scope is the whole statement, including the `else` branch:

```cpp
if (auto it = m.find(key); it != m.end()) { /* use it */ } else { /* it is still in scope */ }
```

it is the same scoping rule `for` always had. the point is not saving a line; it is that a reader knows `it` cannot affect anything after the closing brace.

finally, three **standard attributes** became part of daily use in C++17. `[[nodiscard]]` asks the compiler to warn when a return value is ignored; it can go on a function or on a type, in which case every function returning that type by value is covered. `[[maybe_unused]]` silences unused warnings on a variable, parameter, or function. `[[fallthrough]]` documents an intentional fall-through in a `switch`. all three are hints: the standard only encourages a diagnostic, and the program's meaning never changes.

### in code

second, a before/after modernization of a lookup in a joint-gain table.

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

the `[[nodiscard]]` is the most valuable change here: with an out-parameter, a caller who ignores the `bool` and uses `out` anyway may read an uninitialized `double`, which is undefined behavior ([[undefined-behavior]]). now they at least get a warning. the out-parameter itself is still awkward; [[optional]] replaces it with `std::optional<double>`.

third, `switch` with an initializer plus the other two attributes:

```cpp complete
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

without `[[fallthrough]]`, GCC and Clang warn under `-Wimplicit-fallthrough` (enabled by `-Wextra` in GCC). empty case labels stacked together, like `idle` and `fault`, never need it.

### in practice

`[[nodiscard]]` pays off most when it is applied consistently rather than occasionally. good candidates: functions that return an error code or status, functions with no side effects (computing a value and dropping it is always a bug), `try_`-style operations whose result says whether anything happened, and factories that return a resource the caller must own. C++20 applied the same reasoning to the standard library: `empty()` on every container is `[[nodiscard]]`, which turns the classic slip `v.empty();` (meant: `v.clear();`) into a warning. building with `-Werror=unused-result` (GCC) or treating the corresponding warning as an error makes the attribute a rule instead of a suggestion.

### watch out for

**an initializer lives for the whole statement, `else` included.** that is what makes it useful, and it also means a resource acquired there is held across every branch:

```cpp
#include <mutex>

void drain(std::mutex& m, bool& ready) {
    if (std::lock_guard lock{m}; ready) {
        ready = false;
    } else {
        slow_retry();      // still holding the lock: probably not what was meant
    }
}
```

the lock is released only at the end of the whole `if` statement. when a branch must run without the resource, keep the acquisition in a narrower scope of its own instead of the `if` initializer.

### the takeaway

declare helper variables in the `if` or `switch` that uses them, so a reader knows they cannot leak into the rest of the function, and mark results that must not be ignored with `[[nodiscard]]`.

### optional challenge

in which of the blocks `A`, `B`, `C`, and `D` are `it` and `jt` visible?

```cpp
if (auto it = m.find(k1); it != m.end()) { /* A */ }
else if (auto jt = m.find(k2); jt != m.end()) { /* B */ }
else { /* C */ }
/* D */
```

<details>
<summary>answer</summary>

`it` is visible in `A`, `B`, and `C`, because the `else if` is a nested `if` statement inside the first one's `else` branch. `jt` is visible in `B` and `C`. neither exists in `D`. that nesting is also why a chain of `else if` initializers can see all of the earlier ones.

</details>
