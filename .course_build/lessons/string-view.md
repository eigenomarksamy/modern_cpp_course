---
title: `std::string_view`: borrowing characters
standard: C++17
objective: use `std::string_view` for read-only string parameters, and avoid the null-terminator and lifetime traps of a non-owning view
prerequisites: optional, temporaries-dangling
difficulty: 2
---

### the idea

`void log_topic(const std::string& topic)` looks like the efficient way to accept a read-only string. now call it with a literal, `log_topic("/robot/arm/joint_states")`. the parameter needs a `std::string`, so the compiler builds a temporary one, which allocates if the text is longer than the small-string buffer (an implementation-defined capacity, 15 characters in libstdc++). call it with a substring of a larger buffer and you must first copy that substring into a `std::string`. the function only wanted to *read* some characters. C++17's `std::string_view` lets it say exactly that.

### understanding the concept

a `std::string_view` (header `<string_view>`) is a pointer and a length, nothing more. it does not own the characters, never allocates, and is cheap to copy, so you pass it by value. three properties define how you use it:

- **it borrows.** the characters belong to someone else (a `std::string`, a literal, a receive buffer, a memory-mapped file). the view is valid only while that owner is alive and unmodified. this is the same contract as a reference or raw pointer ([[pointers-references]]), with the same failure mode: dangling.
- **it is not necessarily null-terminated.** a view of `"x=1,y=2"` from offset 0, length 3 sees `x=1`, but the byte after it is `,`. there is no `c_str()` for a reason.
- **slicing is free.** `substr`, `remove_prefix`, and `remove_suffix` just adjust the pointer and length: O(1), no allocation. (`std::string::substr` returns a new string; `std::string_view::substr` returns a new view.)

conversions are asymmetric, and that is good API design: `std::string` converts *implicitly* to `std::string_view` (cheap and safe while the string lives), while `std::string_view` converts to `std::string` only *explicitly* (`std::string(sv)`), because that allocates and you should see it.

### in code

before and after for a read-only parameter:

```cpp complete
#include <map>
#include <string>
#include <string_view>

// before: a literal or substring argument materializes a std::string first
bool is_tf_topic(const std::string& topic) { return topic.compare(0, 4, "/tf/") == 0; }

// after: accepts std::string, literals, and slices of other buffers, no allocation
bool has_prefix(std::string_view s, std::string_view prefix) {
    return s.substr(0, prefix.size()) == prefix;    // C++20 adds s.starts_with(prefix)
}

// bonus: heterogeneous lookup in an ordered map (C++14 std::less<>) takes a view directly
std::map<std::string, int, std::less<>> rates{{"imu", 200}, {"gnss", 10}};
int rate_of(std::string_view topic) {
    auto it = rates.find(topic);                   // no std::string temporary
    return it != rates.end() ? it->second : 0;
}
```

with the default `std::less<std::string>`, `rates.find(topic)` would not compile from a view; you would have to write `rates.find(std::string(topic))` and allocate. `std::unordered_map` gets the equivalent (a transparent hash plus `std::equal_to<>`) only in C++20.

the missing null terminator bites at C boundaries:

```cpp
#include <cstdio>

void open_log(std::string_view path) {
    std::FILE* f = std::fopen(path.data(), "r");   // BUG: data() need not be null-terminated
    // ...
}

void open_log_fixed(std::string_view path) {
    const std::string p(path);                     // one explicit copy, guaranteed terminator
    std::FILE* f = std::fopen(p.c_str(), "r");
    // ...
}
```

if `path` is a slice of `"a.log,b.log"`, the buggy version passes `fopen` a pointer whose string continues past `a.log` to the comma and beyond. that is not even a clean failure: `fopen` reads until it happens to find a zero byte. when an API needs a C string, either take `const std::string&` (or `const char*`) in the signature, or make the copy explicit as above.

### in practice

moving an existing library to `std::string_view` parameters is a mechanical change with one judgment call per function. a function that only reads its argument during the call (`has_prefix`, `log_topic`, a lookup key) takes `std::string_view`, and every caller that passed a literal or a slice stops allocating. a function that *stores* the string (a setter, a constructor that keeps a name) should take `std::string` by value and move it into the member, so the class owns its characters. a function that hands the text to a C API that needs a terminator keeps `const std::string&` or `const char*`. changing a parameter from `const std::string&` to `std::string_view` is source compatible for callers, because `std::string` converts implicitly; it is not ABI compatible, so a shared library changing its exported functions needs a new version.

### watch out for

every `string_view` bug is a lifetime bug, and none of these produce a warning from GCC 12 at `-Wall -Wextra`:

```cpp
std::string_view sv = std::string("base") + "_link";  // BUG: the temporary string dies at the ';'

std::string_view make_name(int id) {
    std::string s = "trk_" + std::to_string(id);
    return s;                                         // BUG: view into a destroyed local
}

class Topic {
    std::string_view name_;                           // borrowed: who keeps the characters alive?
public:
    explicit Topic(std::string_view n) : name_(n) {}
};
Topic t{std::string("imu")};                          // BUG: name_ dangles immediately
```

reading through any of these views is undefined behavior. [[temporaries-dangling]]'s lifetime-extension rule does not rescue you: extension applies when a *reference* binds directly to a temporary, but a `string_view` is an object that merely holds a pointer into it. Clang flags some of these patterns with its `-Wdangling` family of warnings, and AddressSanitizer catches the reads at runtime, but the reliable defense is a rule: use `string_view` for parameters and for short-lived locals, and store `std::string` in members unless the class is explicitly a borrowing view type with a documented lifetime contract. also remember that a view into a `std::string` is invalidated by anything that may reallocate that string, just like a vector iterator ([[sequence-containers]]).

`std::string_view` is the first of the standard's **non-owning views**. [[span]]'s `std::span` does the same for contiguous arrays of any type, and C++20 ranges views ([[views]]) generalize the idea. the design question is always the same: does this component *own* the data, or *borrow* it for the duration of a call?

### the takeaway

`std::string_view` is a borrowed pointer and length: ideal for read-only parameters and zero-copy parsing, wrong for anything that outlives the call unless the owner provably outlives it. make copies to `std::string` explicit, and never hand `data()` to a function that expects a null terminator.

### optional challenge

is there a lifetime bug here? would changing the parameter to `std::string_view` fix it or make it worse?

```cpp
std::vector<std::string_view> split(const std::string& line);   // views into line
auto parts = split(read_line());                                // read_line() returns std::string
for (auto p : parts) use(p);
```

<details>
<summary>answer</summary>

yes. `read_line()` returns a temporary `std::string`; it binds to the `const std::string&` parameter and dies at the end of the full-expression, so every view in `parts` dangles before the loop starts (undefined behavior to read). changing the parameter to `std::string_view` does not fix it and arguably hides it better, because the signature now advertises "I accept anything" while returning views into whatever you passed. fixes: keep the line in a named variable that outlives `parts` (`const auto line = read_line(); auto parts = split(line);`), or have `split` return `std::vector<std::string>` when callers cannot be trusted with the lifetime. some code bases also add a deleted overload `split(std::string&&) = delete;` to reject temporaries at compile time.

</details>
