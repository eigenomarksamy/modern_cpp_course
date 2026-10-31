<a id="day-28"></a>

## day 28: week 4 review: a complete C++17 refresher

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 22 to 27

### recap

| day | idea in one line |
|---|---|
| 22 | A structured binding names the parts of one hidden object; qualifiers apply to that object, names follow member order. `if`/`switch` initializers scope helpers to the decision; `[[nodiscard]]` makes ignored results visible. |
| 23 | `if constexpr` skips *instantiation* of the untaken branch, only inside templates. Folds apply an operator across a pack; only `&&`, `||`, and `,` accept an empty pack in unary form. Use a dependent false, not `static_assert(false)`, before C++23. |
| 24 | `std::optional<T>` stores "maybe a `T`" inline. `*` is unchecked, `value()` throws, empty compares less than everything, and `if (o)` tests engagement, never the value. |
| 25 | `std::variant` is a closed, value-semantic sum type with exhaustive `visit`; virtual functions suit open sets; `std::any` is for code that must not know the type. |
| 26 | `std::string_view` is a borrowed pointer and length: great for parameters and zero-copy parsing, dangerous anywhere it can outlive its owner, and not null-terminated. |
| 27 | `std::filesystem` gives portable paths and a per-call choice of exceptions or `error_code`. Modernize in small, justified steps; state behavior changes; keep owning types at ownership boundaries. |

#### checkpoint: the refresher is complete

This is the halfway mark, and the end of the course's standalone refresher. If you stopped here, you would have the full working model of modern C++17: how source becomes a program and what the standard does and does not promise (week 1), who owns every resource and how objects move (week 2), the library and template machinery that the standard library itself is built from (week 3), and the C++17 vocabulary types that make interfaces say what they mean (week 4). A quick self-test: can you explain, without notes, why a `std::string_view` member is riskier than a `std::string` member, why `std::vector` cares whether your move constructor is `noexcept`, and why an unconstrained template's error messages are so long? If yes, the second half will feel like extensions of things you already understand. Weeks 5 to 8 build on this base: the C++20 toolbox, concurrency, design, and production engineering.

### review questions

1. Does `auto& [id, range] = make_track();` compile if `make_track()` returns a `std::pair<int, double>` by value? What about `const auto&` and `auto&&`, and what happens to the pair's lifetime in those cases?

2. You write `else static_assert(false, "unsupported type");` as the last branch of an `if constexpr` chain in a function template. GCC 12 rejects the file even though no call ever reaches that branch. Why, and what is the C++17 fix?

3. A guard reads `if (latest_temp_c < max_temp_c) keep_running();` where `latest_temp_c` is `std::optional<double>` and `max_temp_c` is a `double`. What happens when no temperature has been received, and how would you rewrite it?

4. Your team is designing the message type for a planner that receives `Goal`, `Cancel`, and `MapUpdate` messages, all defined by your team. A colleague proposes a `Message` base class with virtual `apply()`. Make the case for `std::variant` instead, and name one situation where the base class would be the better choice.

5. What is wrong with this member function, and what is the smallest fix?

   ```cpp
   class Frame {
       std::string prefix_ = "base";
       std::string id_ = "link";
   public:
       std::string_view name() const { return prefix_ + "_" + id_; }
   };
   ```

6. **From week 1.** `const std::string& a = std::string("x") + "y";` and `std::string_view b = std::string("x") + "y";` look alike. Which one is safe to use on the next line, and why does the rule from day 03 treat them differently?

7. **From week 3.** In `template <class... Ts> void emit(Ts&&... xs)`, what kind of references are the parameters? Write one expression that passes every argument to `sink(...)`, one call per argument, in order, preserving each argument's value category.

### mini exercise

Modernize this pre-C++17 parser using at least three week 4 features. Keep the caller working, and decide which behavior changes you are willing to accept.

```cpp
#include <cstdlib>
#include <map>
#include <string>

// "max_vel=1.5" -> name "max_vel", value 1.5; false if malformed
bool parse_limit(const std::string& line, std::string& name, double& value) {
    std::string::size_type eq = line.find('=');
    if (eq == std::string::npos) return false;
    name = line.substr(0, eq);
    const char* begin = line.c_str() + eq + 1;
    char* end = 0;
    value = std::strtod(begin, &end);
    return end != begin && *end == '\0';
}

void load(std::map<std::string, double>& limits, const std::string& line) {
    std::string name;
    double v;
    if (parse_limit(line, name, v)) limits[name] = v;
}
```

### answers

<details>
<summary>1. binding a returned pair</summary>

`auto&` does not compile: the hidden object would be a non-const lvalue reference, which cannot bind to the prvalue `make_track()` (day 05). Both `const auto&` and `auto&&` compile: the hidden reference binds directly to the temporary, so its lifetime is extended to match the hidden reference, which lives as long as the bindings' scope (day 03). With `const auto&`, `id` and `range` are const; with `auto&&`, they are modifiable.

</details>

<details>
<summary>2. the eager static_assert</summary>

`false` does not depend on any template parameter, so the assertion is checked when the template is defined, not when a branch is chosen; no instantiation could ever satisfy it, which makes the template ill-formed under C++17 and C++20 rules. The fix is a dependent false: `template <class> inline constexpr bool always_false = false;` and `static_assert(always_false<T>, "...")`. C++23 (P2593) relaxed the rule, and GCC 13 and Clang 17 accept the plain form in C++23 mode.

</details>

<details>
<summary>3. comparing an empty optional</summary>

An empty optional compares less than any value, so the condition is `true` and the system keeps running with no temperature reading at all. That is a fail-open bug. Make the missing case explicit and choose the safe policy: `if (latest_temp_c && *latest_temp_c < max_temp_c) keep_running();`, which stops (or degrades) when there is no reading. The comparison operators are convenient for sorting; in guards, test engagement first.

</details>

<details>
<summary>4. variant versus a base class</summary>

The set of message types is closed and owned by the team, which is exactly where a variant shines: values stored inline (no allocation per message), copyable and storable in containers, no `dynamic_cast`, and every `std::visit` with explicit per-type handlers fails to compile until it handles a newly added message type. Adding new *operations* (logging, serialization, metrics) is a new visitor rather than a change to every class. The base class wins when the set must be open: plugins or other teams adding message types without recompiling your code, or when message types are large and you want each one to own its behavior.

</details>

<details>
<summary>5. the dangling name()</summary>

`prefix_ + "_" + id_` creates a temporary `std::string`; the returned view points into it, and the temporary is destroyed at the end of the `return` statement. Every use of the result is undefined behavior. The smallest fix is to return `std::string`. A view is only appropriate when it refers to storage that outlives the call, for example `std::string_view id() const { return id_; }`, which is valid as long as the `Frame` lives and `id_` is not modified.

</details>

<details>
<summary>6. from week 1: reference versus view</summary>

`a` is safe: binding a `const&` directly to a temporary extends the temporary's lifetime to the reference's (day 03). `b` dangles: `std::string_view` is not a reference but an object that holds a pointer, initialized through `std::string`'s conversion operator. The temporary string is not bound to any reference, so it dies at the end of the full-expression, and reading `b` is undefined behavior. Lifetime extension follows the language's reference-binding rules, not "anything that refers to something".

</details>

<details>
<summary>7. from week 3: forwarding a pack</summary>

They are forwarding references (day 19): `Ts&&` in a deduced context, with `Ts` deduced as an lvalue reference type for lvalue arguments. The expression is a comma fold (day 23): `(sink(std::forward<Ts>(xs)), ...);`. The built-in comma operator guarantees left-to-right order, and `std::forward<Ts>` restores each argument's original value category. (If `sink` returned a type that overloads `operator,`, cast each call to `void`.)

</details>

<details>
<summary>mini exercise: one possible answer</summary>

```cpp
#include <charconv>
#include <map>
#include <optional>
#include <string>
#include <string_view>

struct Limit { std::string_view name; double value; };   // name borrows from the line

[[nodiscard]] std::optional<Limit> parse_limit(std::string_view line) {
    const auto eq = line.find('=');
    if (eq == std::string_view::npos) return std::nullopt;
    const auto text = line.substr(eq + 1);
    double value{};
    if (auto [ptr, ec] = std::from_chars(text.data(), text.data() + text.size(), value);
        ec != std::errc{} || ptr != text.data() + text.size())
        return std::nullopt;
    return Limit{line.substr(0, eq), value};
}

void load(std::map<std::string, double>& limits, std::string_view line) {
    if (auto lim = parse_limit(line))
        limits.insert_or_assign(std::string(lim->name), lim->value);   // copy at the ownership boundary
}
```

Week 4 features used: `std::string_view` parameters and slicing, `std::optional` instead of the `bool` plus out-parameters, an `if` with an initializer around a structured binding of the `from_chars` result, and `[[nodiscard]]`. The `Limit::name` view is safe only as long as the line lives, which is why `load` copies it into the map immediately.

Behavior changes to accept consciously: `std::strtod` skipped leading whitespace, accepted a leading `+`, and depended on the current C locale's decimal point; `std::from_chars` does none of these, so `"max_vel= 1.5"` and `"max_vel=+1.5"` are now rejected. That is usually what you want in a config format, but it is a change and belongs in the commit message. (Floating-point `from_chars` needs GCC 11 or later with libstdc++; check other toolchains.)

</details>

### connections

Week 4 is mostly week 1 to 3 ideas packaged into types. `std::string_view` and `std::optional` are day 04's pointer-versus-reference-versus-value decision turned into vocabulary, and their traps are day 03's lifetime rules. `std::variant` is day 13's polymorphism question answered for closed sets, and `if constexpr` and folds are day 18 and day 19's template machinery with the SFINAE noise removed. The error-handling options of day 20 now have concrete shapes: exceptions, `std::optional`, variant results, and `std::error_code` overloads in `std::filesystem`.

Week 5 continues directly from here. Concepts (day 29) take over most of what `enable_if` and many `if constexpr` chains do, with better errors. Ranges and views (day 30) and `std::span` (day 31) generalize today's borrowing idea from strings to any sequence, with the same lifetime discipline. Three-way comparison (day 32), C++20 compile-time programming (day 33), and `std::format` (day 34) round out the everyday C++20 toolbox.
