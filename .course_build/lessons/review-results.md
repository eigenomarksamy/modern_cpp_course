---
title: review: results and failure
kind: review
standard: C++17
objective: consolidate structured bindings, if and switch initializers, exception safety, error-handling strategy, and `std::optional`
prerequisites: structured-bindings, init-statements, exception-safety, error-strategy, optional
difficulty: 1
---

### recap

| lesson | key idea |
|---|---|
| [[structured-bindings]] | a structured binding names the parts of one hidden object; qualifiers apply to that object, names follow member order. |
| [[init-statements]] | `if`/`switch` initializers scope helpers to the decision; `[[nodiscard]]` makes ignored results visible. |
| [[exception-safety]] | basic, strong, nothrow: RAII makes basic nearly free, and strong comes from work on the side plus a `noexcept` commit. |
| [[error-strategy]] | choose exceptions, error codes, optional, or result types per API from how expected the failure is and who can act on it. |
| [[optional]] | "maybe a `T`", stored inline: `*` is unchecked, `value()` throws, empty compares less than everything, `if (o)` tests engagement. |

the thread through the module: **a function's result is part of its contract**, including the results it produces when something goes wrong.

### review questions

1. does `auto& [id, range] = make_track();` compile if `make_track()` returns a `std::pair<int, double>` by value? what about `const auto&` and `auto&&`, and what happens to the pair's lifetime in those cases?
2. `Planner::set_waypoints` clears its vector and then pushes the new waypoints one by one. which guarantee does it give, and why is `waypoints_ = w;` not automatically the fix?
3. a guard reads `if (latest_temp_c < max_temp_c) keep_running();` where `latest_temp_c` is `std::optional<double>` and `max_temp_c` is a `double`. what happens when no temperature has been received, and how would you rewrite it?
4. a 1 kHz control loop calls a function that throws on a sensor timeout, which happens a few times a minute. what is wrong with that, and what would you change?
5. from [[forwarding-references]]: in `template <class... Ts> void emit(Ts&&... xs)`, what kind of references are the parameters? write one expression that passes every argument to `sink(...)`, one call per argument, in order, preserving each argument's value category.

### mini exercise

`find_gain` from [[init-statements]] still uses an out-parameter. rewrite it to return `std::optional<double>`, then write the call site that applies a default gain of 0.1 when the joint is missing.

### answers

<details>
<summary>answer 1: binding a returned pair</summary>

`auto&` does not compile: the hidden object would be a non-const lvalue reference, which cannot bind to the prvalue `make_track()` ([[value-categories]]). both `const auto&` and `auto&&` compile: the hidden reference binds directly to the temporary, so its lifetime is extended to match the hidden reference, which lives as long as the bindings' scope ([[temporaries-dangling]]). with `const auto&`, `id` and `range` are const; with `auto&&`, they are modifiable.

</details>

<details>
<summary>answer 2: which guarantee</summary>

basic only: if a `push_back` throws partway, `waypoints_` holds a prefix of the new path, which is valid but neither old nor new. vector copy assignment may reuse the existing storage element by element, so it is not guaranteed to be strong either. the strong version copies on the side and commits with a non-throwing swap: `std::vector<Pose> next(w); waypoints_.swap(next);`.

</details>

<details>
<summary>answer 3: comparing an empty optional</summary>

an empty optional compares less than any value, so the condition is `true` and the system keeps running with no temperature reading at all. that is a fail-open bug. make the missing case explicit and choose the safe policy: `if (latest_temp_c && *latest_temp_c < max_temp_c) keep_running();`, which stops (or degrades) when there is no reading. the comparison operators are convenient for sorting; in guards, test engagement first.

</details>

<details>
<summary>answer 4: exceptions in a control loop</summary>

the timeout is an expected outcome, not an exceptional one, so throwing turns exceptions into control flow; and a throw has no bounded latency, which a 1 kHz loop cannot afford. return a `[[nodiscard]]` status or a `std::optional` reading instead, so the loop can decide within its cycle budget (hold the last value, or command a safe stop), and keep exceptions for failures that end the loop's usefulness.

</details>

<details>
<summary>answer 5: forwarding a pack</summary>

they are forwarding references ([[forwarding-references]]): `Ts&&` in a deduced context, with `Ts` deduced as an lvalue reference type for lvalue arguments. the expression is a comma fold ([[fold-expressions]]): `(sink(std::forward<Ts>(xs)), ...);`. the built-in comma operator guarantees left-to-right order, and `std::forward<Ts>` restores each argument's original value category. (if `sink` returned a type that overloads `operator,`, cast each call to `void`.)

</details>

<details>
<summary>mini exercise answer</summary>

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

double wrist_gain(const std::map<std::string, double>& gains) {
    return find_gain(gains, "wrist").value_or(0.1);
}
```

the caller can no longer read an uninitialized `double` by forgetting a check, and the default is stated where it is applied. if the default were expensive to compute, `value_or` would compute it even when the gain exists, so a branch on the optional would be better.

</details>

### connections

this module was about the edges of a function: what comes out, how it is unpacked, and what happens when it fails. the next one finishes the C++17 vocabulary with types that model "one of several" (`std::variant`), "borrowed text" (`std::string_view`), and "a path" (`std::filesystem::path`), and then uses all of it in a realistic refactoring.
