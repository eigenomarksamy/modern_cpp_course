---
title: `std::optional`: modeling "maybe"
standard: C++17
objective: use `std::optional` for values whose absence is a normal outcome, and avoid its unchecked access, comparison, and bool traps
prerequisites: error-strategy, init-statements
difficulty: 2
---

### the idea

every code base has its own dialect for "there might not be a value": `-1` for "not found", `NaN` for "no reading", a `bool` return plus an out-parameter, a null pointer to a heap object that did not need to be on the heap. each dialect has a failure mode. `-1` is a valid value for some other caller, `NaN` poisons arithmetic silently, and the out-parameter ([[init-statements]]'s `find_gain`) leaves the caller holding an uninitialized `double` if they forget the check. C++17's `std::optional<T>` gives "maybe a `T`" a single, typed spelling that the compiler understands.

### understanding the concept

`std::optional<T>` (header `<optional>`) holds either a `T` or nothing. the storage for the `T` lives *inside* the optional object, next to a flag: no heap allocation, and an empty optional has not constructed a `T` at all. the size is implementation-specific; it is at least `sizeof(T)` plus room for the flag, rounded up for alignment (`sizeof(std::optional<double>)` is 16 on mainstream 64-bit ABIs).

the access API is small, and the differences between its members are the whole point:

| expression | if engaged | if empty |
|---|---|---|
| `o.has_value()`, `if (o)` | `true` | `false` |
| `*o`, `o->m` | the value | undefined behavior |
| `o.value()` | the value | throws `std::bad_optional_access` |
| `o.value_or(d)` | a copy of the value | `d` converted to `T` |

`*o` is unchecked by design, like `vector::operator[]`; use it right after you have tested the optional. `value()` is the checked version, and `value_or` is for the common case of a sensible fallback. note that `value_or`'s argument is always evaluated, so `o.value_or(load_default_from_disk())` does the I/O even when `o` is engaged.

you create an empty optional with `std::nullopt` (or `{}`), and an engaged one by assigning a `T` or constructing in place: `o.emplace(args...)` and `std::optional<T> o(std::in_place, args...)` construct the `T` directly in the optional's storage, which matters for types that are expensive or impossible to move.

there is no `std::optional<T&>` in C++17 (it is ill-formed; C++26 adds it). for "maybe refers to an existing object", a `T*` is the idiomatic answer and already means exactly that ([[pointers-references]]).

comparisons are defined between optionals, against `std::nullopt`, and against plain `T` values, with one rule to remember: an empty optional compares less than any engaged one.

finally, the design meaning. returning `std::optional<T>` is a contract: "absence is a normal outcome and you must handle it". that is different from an exception ([[error-strategy]]), which says "this should not happen in normal operation". what optional cannot say is *why* the value is missing; when callers need the reason, use a result type ([[variant]]) or an exception.

### in code

[[init-statements]]'s out-parameter lookup, finished:

```cpp complete
#include <map>
#include <optional>
#include <string>

[[nodiscard]] std::optional<double>
find_gain(const std::map<std::string, double>& gains, const std::string& joint) {
    if (auto it = gains.find(joint); it != gains.end())
        return it->second;
    return std::nullopt;
}

void apply_gain(double);

void configure(const std::map<std::string, double>& gains) {
    if (auto kp = find_gain(gains, "elbow"))      // kp is scoped to the if
        apply_gain(*kp);                          // checked just above: * is fine
    double kd = find_gain(gains, "wrist").value_or(0.1);
    apply_gain(kd);
}
```

the caller cannot read the value without going through the optional, and the type says "may be missing" in the signature instead of in a comment.

now predict the output. two of these surprise most people.

```cpp complete
#include <iostream>
#include <optional>
#include <string>

int main() {
    std::optional<int> a;            // empty
    std::optional<int> b = 0;
    std::cout << (a < b) << (a < -100) << (b == 0) << '\n';   // prints: 111

    try {
        std::cout << a.value() << '\n';
    } catch (const std::bad_optional_access& e) {
        std::cout << "empty\n";                                // prints: empty
    }

    std::optional<std::string> s = "fix";
    auto t = std::move(s);
    std::cout << s.has_value() << '\n';                        // prints: 1
}
```

`a < -100` is `true` because empty is less than every value, including negative ones; a range check like `if (reading < limit)` on an optional quietly passes when there is no reading. and moving from an optional does not make it empty: `s` is still engaged and holds a moved-from string (valid but unspecified, [[move-semantics]]). if you need it empty, call `s.reset()`.

### in practice

in a localization node, a GNSS fix is genuinely optional: you may not have one yet, or it may be too old to trust. that is exactly what a member should model:

```cpp
class Localizer {
public:
    void on_gnss(const GnssFix& fix) { last_fix_ = fix; }
    [[nodiscard]] std::optional<Pose> pose_at(Timestamp t) const;  // empty if no usable fix
private:
    std::optional<GnssFix> last_fix_;        // "never received" is distinct from any fix value
};
```

compare the alternatives. a `GnssFix` with a `valid` flag lets every reader forget to check it. a `std::unique_ptr<GnssFix>` adds a heap allocation and pointer semantics for no ownership benefit. the optional keeps the data inline and makes the check visible.

### watch out for

`std::optional<bool>` and `std::optional<T*>` turn a one-character mistake into a logic bug:

```cpp
std::optional<bool> brake_engaged = read_brake_sensor();   // empty on sensor timeout

if (brake_engaged)                 // BUG: means "we got a reading", not "brake is on"
    release_parking_hold();

if (brake_engaged.value_or(true))  // fixed, and the fallback is a safety decision:
    release_parking_hold();        // treat "unknown" as "engaged"
```

the contextual conversion to `bool` tests engagement, whatever `T` is. with `std::optional<bool>`, `if (o == true)` or `value_or` make the intent explicit, and the fallback value deserves a comment because it encodes policy. with `std::optional<Sensor*>` you have two kinds of nothing (`nullopt` and `nullptr`); unless those genuinely mean different things in your domain, a plain pointer is simpler. some static analyzers flag these patterns; compilers generally do not.

### the takeaway

use `std::optional<T>` when absence is a normal, expected outcome: it stores the value inline, puts "maybe" in the type, and makes the check hard to skip. remember that `*` is unchecked, empty compares less than everything, moved-from optionals stay engaged, and `if (o)` never looks at the value inside.

### optional challenge

a radar driver exposes `std::optional<std::vector<Detection>> detections()`. a reviewer suggests returning a plain `std::vector<Detection>` and using an empty vector for "nothing". when is the reviewer right, and when is the optional worth keeping?

<details>
<summary>answer</summary>

if "no scan happened" and "the scan found no targets" are handled the same way by every caller, the empty vector is simpler and the optional is just an extra layer to unwrap. if they mean different things (a tracker should coast tracks through a missing scan but may delete them after a genuinely empty scan), then the distinction is real information and the optional is the honest return type. and if callers need to know *why* there was no scan (timeout, CRC error, blanking interval), neither is enough: that is a job for a result type ([[variant]]) or an exception.

</details>

### going deeper

#### in-place construction

in-place construction for a type that should not be copied around:

```cpp complete
#include <optional>

struct Track {
    Track(int id, double range_m, double vel_mps) : id(id), range_m(range_m), vel_mps(vel_mps) {}
    Track(const Track&) = delete;            // tracks have identity; no accidental copies
    Track& operator=(const Track&) = delete;
    int id; double range_m; double vel_mps;
};

std::optional<Track> lead;                   // no Track constructed yet
void on_new_target(int id, double r, double v) {
    lead.emplace(id, r, v);                  // destroys any old Track, builds the new one in place
}
```

#### optional parameters

parameters are a different story. `void configure(std::optional<Limits> limits = std::nullopt)` constructs an optional (and copies the `Limits`) at every call, and the function body is one big `if`. two overloads, `configure()` and `configure(const Limits&)`, are usually clearer. if the argument is a borrowed object that may be absent, `const Limits*` says that with no copy at all.

#### C++23 monadic operations

C++23 note: `and_then`, `transform`, and `or_else` (the "monadic" operations) let you chain optional-returning steps without nested `if`s. they are not in C++17 or C++20.
