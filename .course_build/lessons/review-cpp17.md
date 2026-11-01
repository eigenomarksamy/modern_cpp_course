---
title: review: the C++17 vocabulary, and a complete refresher
kind: review
standard: C++17
objective: consolidate variant, string_view, from_chars, filesystem, and modernization practice, and check the standalone C++17 refresher
prerequisites: variant, variant-design, string-view, parsing-with-views, filesystem, cpp17-refactoring
difficulty: 1
---

### recap

| lesson | key idea |
|---|---|
| [[variant]] | a value-semantic sum type with inline storage; `std::visit` with per-type lambdas checks exhaustiveness. |
| [[variant-design]] | variants for closed sets you own, virtual functions for open sets, `std::any` only when the code must not know the type. |
| [[string-view]] | a borrowed pointer and length: great for parameters, dangerous anywhere it can outlive its owner, and not null-terminated. |
| [[parsing-with-views]] | slice with views, convert with `from_chars` and `to_chars`, check both the error code and the end pointer. |
| [[filesystem]] | portable paths and directory iteration with a per-call choice of exceptions or `error_code`; checks do not prevent races. |
| [[cpp17-refactoring]] | modernize in small, justified steps; state behavior changes; keep owning types at ownership boundaries. |

#### checkpoint: the refresher is complete

this is the end of the course's standalone refresher. if you stopped here, you would have the full working model of modern C++17: how source becomes a program and what the standard does and does not promise, who owns every resource and how objects move, the library and template machinery the standard library is built from, and the C++17 vocabulary types that make interfaces say what they mean. a quick self-test: can you explain, without notes, why a `std::string_view` member is riskier than a `std::string` member, why `std::vector` cares whether your move constructor is `noexcept`, and why an unconstrained template's error messages are so long? if yes, the rest of the course will feel like extensions of things you already understand: C++20, concurrency, design, and production engineering.

### review questions

1. your team is designing the message type for a planner that receives `Goal`, `Cancel`, and `MapUpdate` messages, all defined by your team. a colleague proposes a `Message` base class with virtual `apply()`. make the case for `std::variant` instead, and name one situation where the base class would be the better choice.
2. what is wrong with this member function, and what is the smallest fix?

   ```cpp
   class Frame {
       std::string prefix_ = "base";
       std::string id_ = "link";
   public:
       std::string_view name() const { return prefix_ + "_" + id_; }
   };
   ```
3. from [[temporaries-dangling]]: `const std::string& a = std::string("x") + "y";` and `std::string_view b = std::string("x") + "y";` look alike. which one is safe to use on the next line, and why does the lifetime rule treat them differently?

### mini exercise

modernize this pre-C++17 parser using at least three features from the last two modules. keep the caller working, and decide which behavior changes you are willing to accept.

```cpp complete
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
<summary>answer 1: variant versus a base class</summary>

the set of message types is closed and owned by the team, which is exactly where a variant shines: values stored inline (no allocation per message), copyable and storable in containers, no `dynamic_cast`, and every `std::visit` with explicit per-type handlers fails to compile until it handles a newly added message type. adding new *operations* (logging, serialization, metrics) is a new visitor rather than a change to every class. the base class wins when the set must be open: plugins or other teams adding message types without recompiling your code, or when message types are large and you want each one to own its behavior.

</details>

<details>
<summary>answer 2: the dangling name()</summary>

`prefix_ + "_" + id_` creates a temporary `std::string`; the returned view points into it, and the temporary is destroyed at the end of the `return` statement. every use of the result is undefined behavior. the smallest fix is to return `std::string`. a view is only appropriate when it refers to storage that outlives the call, for example `std::string_view id() const { return id_; }`, which is valid as long as the `Frame` lives and `id_` is not modified.

</details>

<details>
<summary>answer 3: reference versus view</summary>

`a` is safe: binding a `const&` directly to a temporary extends the temporary's lifetime to the reference's ([[temporaries-dangling]]). `b` dangles: `std::string_view` is not a reference but an object that holds a pointer, initialized through `std::string`'s conversion operator. the temporary string is not bound to any reference, so it dies at the end of the full-expression, and reading `b` is undefined behavior. lifetime extension follows the language's reference-binding rules, not "anything that refers to something".

</details>

<details>
<summary>mini exercise answer</summary>

```cpp complete
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

C++17 features used: `std::string_view` parameters and slicing, `std::optional` instead of the `bool` plus out-parameters, an `if` with an initializer around a structured binding of the `from_chars` result, and `[[nodiscard]]`. the `Limit::name` view is safe only as long as the line lives, which is why `load` copies it into the map immediately.

behavior changes to accept consciously: `std::strtod` skipped leading whitespace, accepted a leading `+`, and depended on the current C locale's decimal point; `std::from_chars` does none of these, so `"max_vel= 1.5"` and `"max_vel=+1.5"` are now rejected. that is usually what you want in a config format, but it is a change and belongs in the commit message. (floating-point `from_chars` needs GCC 11 or later with libstdc++; check other toolchains.)

</details>

### connections

the C++20 modules that follow sharpen tools you now know: concepts replace `enable_if` and give templates readable errors ([[concepts]]), ranges turn iterator pairs into composable pipelines ([[range-algorithms]]), `std::span` does for arrays what `std::string_view` did for text ([[span]]), and defaulted comparisons and `consteval` remove boilerplate you have been writing by hand.
