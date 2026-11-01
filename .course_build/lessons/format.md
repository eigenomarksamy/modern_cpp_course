---
title: `std::format`: type-safe formatting
standard: C++20
objective: format text with `std::format` and its spec mini-language, keep format strings compile-time checked in your own wrappers, and avoid allocation with format_to_n
prerequisites: consteval-constinit, variadic-templates, string-view
difficulty: 2
---

### the idea

every C++ codebase formats text, and until C++20 the standard offered two bad choices. `printf("%llu", frame_id)` is compact, but passing an argument whose type does not match the conversion specifier is undefined behavior, and `std::uint64_t` is `unsigned long` on LP64 Linux, so `%llu` is wrong there and right on Windows. iostreams are type-safe, but `std::cout << std::setw(8) << std::fixed << std::setprecision(3) << x` is verbose, and `std::fixed` and `setprecision` stay set on the stream for whoever prints next.

`std::format` (C++20, `<format>`) keeps printf's compact format strings, gets the type from the argument instead of the string, checks the string at compile time, and has no hidden stream state.

**library support:** `<format>` needs GCC 13+, Clang with libc++ 17+, or MSVC 19.29+ (Visual Studio 2019 16.10), and the compile-time checking described below needs a recent version of each. on older toolchains, the {fmt} library (`fmt::format`) offers the same syntax; `std::format` was standardized from it. GCC 12, used to check this course, has no `<format>`, so the `std::format` code in this lesson is written against the standard but **not compile-checked**. the tour at the end was compiled with GCC 12.

### understanding the concept

a replacement field is `{index:spec}`. both parts are optional; `{}` takes the next argument. the spec mini-language is `[[fill]align][sign][#][0][width][.precision][type]`: `{:>10.3f}` is right-aligned, width 10, three decimals, fixed; `{:#x}` is hex with a `0x` prefix; `{:*^9}` centers in nine characters, padded with `*`. each type defines which specs it accepts.

**compile-time checking.** in C++20 as amended by P2216 (a defect report, so it applies to C++20 mode), the format string parameter is not a plain `string_view`. it is `std::format_string<Args...>`, whose constructor is `consteval` ([[consteval-constinit]]): it parses the literal during compilation, against the actual argument types. a bad spec or a missing argument is a compile error at your call site. (P2508 made the name `std::format_string` public for user code; current versions of the implementations above provide it in C++20 mode.) the flip side: the format string must be a constant expression. for a string known only at runtime (a user-configurable log template), call `std::vformat(fmt, std::make_format_args(a, b))`, which throws `std::format_error` on a bad string.

**locale.** `std::format` is locale-independent unless you ask for it with the `L` option. `{:.2f}` always uses `.` as the decimal separator, which is what you want for telemetry and file formats; printf follows the C locale (`LC_NUMERIC`).

### in code

**the basics, and what the compiler rejects.**

```cpp complete
#include <cstdint>
#include <format>
#include <string>

std::uint64_t frame = 1234567;
double range_m = 1234.56789;
int status = 255;

std::string s = std::format("frame {} range {:>10.3f} m status {:#x}", frame, range_m, status);
// "frame 1234567 range   1234.568 m status 0xff"

std::string t = std::format("{0}->{1}, {1}->{0}", "a", "b");   // "a->b, b->a"

// std::format("{:d}", range_m);   compile error: 'd' is not a valid presentation type for double
// std::format("{} {}", frame);    compile error: the string refers to an argument that does not exist
```

### in practice

a joint-controller thread logs at 1 kHz and must not allocate in steady state ([[allocation-costs]] has the details). `std::format` returns a `std::string`, which can allocate. `std::format_to` writes to any output iterator, and `std::format_to_n` writes at most `n` characters, so a reusable fixed buffer avoids the result allocation:

```cpp
#include <algorithm>
#include <array>
#include <format>

std::array<char, 96> line;   // owned by the logger, reused every cycle

void log_cycle(long t_us, int joint, double err) {
    auto r = std::format_to_n(line.data(), line.size(),
                              "t={} joint={} err={:+.4f}", t_us, joint, err);
    // r.out: one past the last char written; r.size: the length *without* truncation
    auto len = std::min(static_cast<std::size_t>(r.size), line.size());
    bool truncated = static_cast<std::size_t>(r.size) > line.size();
    sink_write(line.data(), len, truncated);   // no null terminator was written
}
// log_cycle(1712, 3, -0.00123456) writes "t=1712 joint=3 err=-0.0012"
```

the standard does not promise that formatting performs no internal allocation, so verify with an allocation counter ([[allocation-costs]]) on your implementation before you rely on it in a real-time loop.

your own logging wrapper must keep the compile-time check. take `std::format_string<Args...>`, not `std::string_view`:

```cpp
template <typename... Args>
void log_info(std::format_string<Args...> fmt, Args&&... args) {
    write_line(std::format(fmt, std::forward<Args>(args)...));
}
// log_info("joint {} over limit by {:.2f}", id);   compile error at *this* call: missing argument
```

a `std::string_view fmt` parameter cannot be passed on to `std::format` at all (it is not a constant expression), and the usual "fix", switching to `std::vformat`, silently moves every format error from compile time to runtime.

### watch out for

**assuming `<format>` exists everywhere.**

the other trap is assuming `std::format` exists. libraries that must build on GCC 12 or older Clang often use {fmt} directly, or a thin wrapper that switches between `std::format` and `fmt::format`, rather than sprinkling feature tests (`__cpp_lib_format`) around the codebase.

### the takeaway

`std::format` combines printf's compact syntax with type safety, compile-time checked format strings, and no stream state; keep the check alive in your wrappers with `std::format_string`, and use `format_to_n` when allocation matters.

### optional challenge

a colleague writes `std::string msg = std::format(cfg.log_template, id, value);`, where `log_template` is a `std::string` loaded from a config file. does it compile? if not, what is the correct replacement, and what new failure mode does it introduce?

<details>
<summary>answer</summary>

it does not compile in C++20 (as amended by P2216): the format string is converted to `std::format_string<int, double>` through a `consteval` constructor, and a runtime `std::string` is not a constant expression. the replacement is `std::vformat(cfg.log_template, std::make_format_args(id, value))`, with `id` and `value` as lvalues (`make_format_args` stores references to them). the new failure mode is runtime: a template like `"{} {} {}"` or `"{:d}"` applied to a `double` throws `std::format_error`. validate the template once when the config is loaded (format it with representative values inside a `try`), not on every log call.

</details>

### going deeper

#### a formatter for your own types

**a formatter for a domain type.** specialize `std::formatter`. inheriting from `std::formatter<double>` reuses its `parse`, so the caller's spec (`{:.2f}`) applies to each number:

```cpp complete
#include <format>

struct Pose2D { double x, y, theta; };

template <>
struct std::formatter<Pose2D> : std::formatter<double> {
    // parse() inherited. format() is const: C++23 requires it (LWG 3636), C++20 libraries accept it
    auto format(const Pose2D& p, std::format_context& ctx) const {
        ctx.advance_to(std::format_to(ctx.out(), "(x="));
        ctx.advance_to(std::formatter<double>::format(p.x, ctx));
        ctx.advance_to(std::format_to(ctx.out(), ", y="));
        ctx.advance_to(std::formatter<double>::format(p.y, ctx));
        ctx.advance_to(std::format_to(ctx.out(), ", theta="));
        ctx.advance_to(std::formatter<double>::format(p.theta, ctx));
        return std::format_to(ctx.out(), ")");
    }
};

// std::format("{:.2f}", Pose2D{1.0, 2.5, 0.785398})  ->  "(x=1.00, y=2.50, theta=0.79)"
```

the `advance_to` calls matter: the base `format` writes at `ctx.out()`, so the context must know where the previous write ended.
