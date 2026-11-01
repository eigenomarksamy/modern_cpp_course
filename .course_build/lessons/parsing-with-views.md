---
title: parsing without allocation: views and from_chars
standard: C++17
objective: parse and format text without allocating, using string_view slicing with `std::from_chars` and `std::to_chars`
prerequisites: string-view, structured-bindings
difficulty: 2
---

### the idea

a log-analysis tool ingests hours of GNSS data: millions of short comma-separated NMEA sentences. the obvious parser splits each line into `std::string` fields and calls `std::stod` on the ones it needs, allocating and copying for every field of every line, and consulting the global locale on every number. none of that work is needed to read a few digits out of a buffer you already hold. views for slicing and `<charconv>` for numbers do the same job touching each byte once.

### understanding the concept

the parsing partners are `std::from_chars` and `std::to_chars` (header `<charconv>`, C++17). unlike `std::stod` or `strtod`, they take a `[first, last)` character range (perfect for a view), never allocate, never throw, ignore the locale, and report errors through a returned `{ptr, ec}` struct, which unpacks neatly with a structured binding ([[structured-bindings]]). `from_chars` does not skip leading whitespace or accept a leading `+`. integer support is universal; floating-point support arrived later in some standard libraries (libstdc++ has it from GCC 11), so check your toolchain before relying on it.

the slicing half of the toolkit is `std::string_view` itself: a tokenizer holds the unparsed remainder as a view, finds the next delimiter, returns the field as a view, and shortens the remainder with `remove_prefix`. nothing is copied, and every field is a window into the original line, so the whole parse is valid exactly as long as that line is.

### in code

NMEA 0183 sentences from a GNSS receiver are short comma-separated ASCII lines. a tool that ingests hours of logs parses millions of them, and the naive version allocates a `std::string` per field. with views, the parser touches each byte once and allocates nothing:

```cpp complete
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

notice how the C++17 vocabulary composes: views for the slices, a structured binding for the `from_chars` result, `std::optional` for "this field may be empty or garbage". whether it is measurably faster than a `std::string`-based parser depends on line lengths and the allocator; count allocations ([[allocation-costs]] shows how) and profile before claiming a speedup. the design gain is certain either way: the parser's signature says it borrows the line and keeps nothing.

### in practice

`std::to_chars` is the formatting half, for producing telemetry lines without allocating:

```cpp complete
#include <charconv>
#include <string_view>

std::string_view format_altitude(char (&buf)[32], double altitude_m) {
    auto [end, ec] = std::to_chars(buf, buf + sizeof buf, altitude_m);
    if (ec != std::errc{}) return {};               // buffer too small
    return std::string_view(buf, end - buf);       // a view into the caller's buffer
}
```

with no precision argument, floating-point `to_chars` produces the *shortest* text that reads back to exactly the same `double` through `from_chars`, which makes round-tripping values through text lossless without guessing a precision. the returned view borrows the caller's buffer, so the caller decides how long the text lives; formatting into a `std::string` is one explicit copy away when it must be kept.

### watch out for

**`from_chars` parses a prefix and stops.** it reports success as long as it could read *something*, and tells you where it stopped:

```cpp
double v{};
std::string_view s = "12.5abc";
auto [ptr, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
// ec == std::errc{}, v == 12.5, ptr points at 'a'
```

checking only `ec` accepts `"12.5abc"` as 12.5, which is why `to_double` also compares `ptr` with the end of the input. the other differences from `strtod` and `std::stod` matter just as much when porting a parser: no leading whitespace is skipped, a leading `+` is rejected, and an out-of-range value reports `std::errc::result_out_of_range` instead of returning infinity.

### the takeaway

slice with `std::string_view`, convert numbers with `from_chars` and `to_chars`, and check both the error code and the end pointer; the parse is then allocation-free and locale-free, and valid exactly as long as the buffer it borrows.

### optional challenge

using `to_double` from the code above, what do these return: `to_double("545.4")`, `to_double(" 12")`, `to_double("+5")`, `to_double("1e3")`, `to_double("")`?

<details>
<summary>answer</summary>

`545.4`, empty, empty, `1000`, and empty. `" 12"` fails because `from_chars` does not skip whitespace; `"+5"` fails because a leading plus sign is not accepted; `"1e3"` is valid scientific notation in the default general format; and an empty range reports `std::errc::invalid_argument`. if the input really can contain leading spaces or a plus sign, strip them explicitly before calling `from_chars`, so the accepted format is written down in your code.

</details>
