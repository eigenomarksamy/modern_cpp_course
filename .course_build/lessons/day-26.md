<a id="day-26"></a>

## day 26: `std::string_view` and non-owning views

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 03, 04, 22, 24

### the idea

`void log_topic(const std::string& topic)` looks like the efficient way to accept a read-only string. Now call it with a literal, `log_topic("/robot/arm/joint_states")`. The parameter needs a `std::string`, so the compiler builds a temporary one, which allocates if the text is longer than the small-string buffer (an implementation-defined capacity, 15 characters in libstdc++). Call it with a substring of a larger buffer and you must first copy that substring into a `std::string`. The function only wanted to *read* some characters. C++17's `std::string_view` lets it say exactly that.

### understanding the concept

A `std::string_view` (header `<string_view>`) is a pointer and a length, nothing more. It does not own the characters, never allocates, and is cheap to copy, so you pass it by value. Three properties define how you use it:

- **It borrows.** The characters belong to someone else (a `std::string`, a literal, a receive buffer, a memory-mapped file). The view is valid only while that owner is alive and unmodified. This is the same contract as a reference or raw pointer (day 04), with the same failure mode: dangling.
- **It is not necessarily null-terminated.** A view of `"x=1,y=2"` from offset 0, length 3 sees `x=1`, but the byte after it is `,`. There is no `c_str()` for a reason.
- **Slicing is free.** `substr`, `remove_prefix`, and `remove_suffix` just adjust the pointer and length: O(1), no allocation. (`std::string::substr` returns a new string; `std::string_view::substr` returns a new view.)

Conversions are asymmetric, and that is good API design: `std::string` converts *implicitly* to `std::string_view` (cheap and safe while the string lives), while `std::string_view` converts to `std::string` only *explicitly* (`std::string(sv)`), because that allocates and you should see it.

The parsing partners are `std::from_chars` and `std::to_chars` (header `<charconv>`, C++17). Unlike `std::stod` or `strtod`, they take a `[first, last)` character range (perfect for a view), never allocate, never throw, ignore the locale, and report errors through a returned `{ptr, ec}` struct, which unpacks neatly with a structured binding (day 22). `from_chars` does not skip leading whitespace or accept a leading `+`. Integer support is universal; floating-point support arrived later in some standard libraries (libstdc++ has it from GCC 11), so check your toolchain before relying on it.

### in code

Before and after for a read-only parameter:

```cpp
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

With the default `std::less<std::string>`, `rates.find(topic)` would not compile from a view; you would have to write `rates.find(std::string(topic))` and allocate. `std::unordered_map` gets the equivalent (a transparent hash plus `std::equal_to<>`) only in C++20.

The missing null terminator bites at C boundaries:

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

If `path` is a slice of `"a.log,b.log"`, the buggy version passes `fopen` a pointer whose string continues past `a.log` to the comma and beyond. That is not even a clean failure: `fopen` reads until it happens to find a zero byte. When an API needs a C string, either take `const std::string&` (or `const char*`) in the signature, or make the copy explicit as above.

### in practice

NMEA 0183 sentences from a GNSS receiver are short comma-separated ASCII lines. A tool that ingests hours of logs parses millions of them, and the naive version allocates a `std::string` per field. With views, the parser touches each byte once and allocates nothing:

```cpp
#include <charconv>
#include <optional>
#include <string_view>

std::string_view next_field(std::string_view& rest) {
    const auto comma = rest.find(',');
    const auto field = rest.substr(0, comma);          // npos: the whole remainder
    rest.remove_prefix(comma == std::string_view::npos ? rest.size() : comma + 1);
    return field;
}

std::optional<double> to_double(std::string_view s) {
    double v{};
    auto [ptr, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
    if (ec != std::errc{} || ptr != s.data() + s.size())   // reject "12.5abc" and ""
        return std::nullopt;
    return v;
}

// "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
std::optional<double> gga_altitude_m(std::string_view sentence) {
    for (int i = 0; i < 9; ++i) next_field(sentence);  // skip to field 9
    return to_double(next_field(sentence));            // 545.4
}
```

Notice how week 4 is composing: views for the slices, a structured binding for the `from_chars` result, `std::optional` for "this field may be empty or garbage". Whether it is measurably faster than a `std::string`-based parser depends on line lengths and the allocator; count allocations (day 52 shows how) and profile before claiming a speedup. The design gain is certain either way: the parser's signature says it borrows the line and keeps nothing.

### watch out for

Every `string_view` bug is a lifetime bug, and none of these produce a warning from GCC 12 at `-Wall -Wextra`:

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

Reading through any of these views is undefined behavior. Day 03's lifetime-extension rule does not rescue you: extension applies when a *reference* binds directly to a temporary, but a `string_view` is an object that merely holds a pointer into it. Clang flags some of these patterns with its `-Wdangling` family of warnings, and AddressSanitizer catches the reads at runtime, but the reliable defense is a rule: use `string_view` for parameters and for short-lived locals, and store `std::string` in members unless the class is explicitly a borrowing view type with a documented lifetime contract. Also remember that a view into a `std::string` is invalidated by anything that may reallocate that string, just like a vector iterator (day 15).

`std::string_view` is the first of the standard's **non-owning views**. Day 31's `std::span` does the same for contiguous arrays of any type, and C++20 ranges views (day 30) generalize the idea. The design question is always the same: does this component *own* the data, or *borrow* it for the duration of a call?

### the takeaway

`std::string_view` is a borrowed pointer and length: ideal for read-only parameters and zero-copy parsing, wrong for anything that outlives the call unless the owner provably outlives it. Make copies to `std::string` explicit, and never hand `data()` to a function that expects a null terminator.

### optional challenge

Is there a lifetime bug here? Would changing the parameter to `std::string_view` fix it or make it worse?

```cpp
std::vector<std::string_view> split(const std::string& line);   // views into line
auto parts = split(read_line());                                // read_line() returns std::string
for (auto p : parts) use(p);
```

<details>
<summary>answer</summary>

Yes. `read_line()` returns a temporary `std::string`; it binds to the `const std::string&` parameter and dies at the end of the full-expression, so every view in `parts` dangles before the loop starts (undefined behavior to read). Changing the parameter to `std::string_view` does not fix it and arguably hides it better, because the signature now advertises "I accept anything" while returning views into whatever you passed. Fixes: keep the line in a named variable that outlives `parts` (`const auto line = read_line(); auto parts = split(line);`), or have `split` return `std::vector<std::string>` when callers cannot be trusted with the lifetime. Some code bases also add a deleted overload `split(std::string&&) = delete;` to reject temporaries at compile time.

</details>
