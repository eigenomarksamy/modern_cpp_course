---
title: choosing an error-handling strategy
standard: C++17
objective: choose between exceptions, error codes, optional values, and result types per API, based on how expected a failure is and who can act on it
prerequisites: exception-safety
difficulty: 2
---

### the idea

every function that can fail answers a question it rarely states out loud: how does the caller find out? an exception, an error code, an empty `std::optional`, a result that holds either a value or a reason. each is right somewhere, and a codebase that picks at random per function is harder to use correctly than one that consistently uses any of them. choosing an error channel is an API design decision, made per layer and written down.

### understanding the concept

exceptions are not the only error channel, and choosing one is an API decision:

| mechanism | fits when | costs and limits |
|---|---|---|
| exceptions | failure is rare and the immediate caller can't handle it; constructors | throwing is slow and its latency hard to bound; unwind tables add binary size; invisible in signatures |
| error codes (`enum`, `std::error_code`) | failure is expected and handled close by; C interop; `-fno-exceptions` builds | easy to ignore (use `[[nodiscard]]`); constructors can't return them |
| `std::optional<T>` | "no result" needs no explanation ([[optional]]) | carries no reason |
| result types (`std::variant<T, Error>`, [[variant]]) | value or a reason, checked by the caller | more verbose call sites; `std::expected` is C++23 only |

on mainstream ABIs (Itanium-style table-based unwinding, used by GCC and Clang on Linux), a `try` block adds essentially no work to the non-throwing path (it can still constrain some optimizations). throwing, though, allocates the exception object and searches unwind tables, so its cost is high and hard to bound. that is the honest basis for banning exceptions in hard real-time loops: not "exceptions are slow", but "a throw has no bounded latency". many embedded projects go further and compile with `-fno-exceptions`, where `throw` and `try` in your code fail to compile, and failures the standard library reports by throwing (`std::bad_alloc`, `at()` out of range) end the program instead, because no handler can exist. the exact mechanism depends on how the library was built.

### in code

the same operation with three different error channels, each a reasonable choice in a different context:

```cpp complete
#include <optional>
#include <string_view>
#include <system_error>

struct RangeGate { double min_m, max_m; };

// exception: failure is rare, and the caller cannot fix it locally
RangeGate parse_gate(std::string_view text);                               // throws on bad input

// error code: failure is expected and handled right here; usable with -fno-exceptions
[[nodiscard]] std::errc parse_gate(std::string_view text, RangeGate& out) noexcept;

// optional: "no result" needs no further explanation
std::optional<RangeGate> try_parse_gate(std::string_view text) noexcept;
```

the call sites read differently, and that difference is the point:

```cpp
RangeGate g = parse_gate(config_line);                     // the happy path stays linear

RangeGate g2;
if (parse_gate(user_line, g2) != std::errc{}) { /* report, re-prompt */ }

if (auto g3 = try_parse_gate(cached_line)) { /* use *g3 */ }
```

the exception version keeps the normal path free of checks and pushes failure to whoever can handle it. the error-code version forces handling at the call site, costs nothing when no exception machinery is available, and says *why* through the enum. the optional version is the lightest, and the least informative.

### in practice

a robot arm driver library had one error convention everywhere: throw. that was right for `Arm::connect()`, called once at startup, where failure means the process cannot do its job and a clear exception with context is the best report. it was wrong for `Arm::read_joint_states()`, called at 1 kHz from the control loop, where a dropped packet is an expected event and the loop must decide within its cycle budget whether to hold position.

the revised API used a different channel per situation: `connect()` throws, the cyclic read returns a `[[nodiscard]]` status plus data, and constructors establish their invariants or throw. the rule behind it: decide by how expected the failure is, who can act on it, and the latency budget, then document the choice and apply it consistently per layer. two habits to avoid while you are at it: using exceptions for ordinary control flow (ending a parse loop by catching), and `catch (...) {}` that swallows a failure nobody will ever see. also avoid catching, logging, and rethrowing at every layer, which produces five log lines for one error.

### watch out for

**error codes are easy to ignore, so make ignoring them visible.** a status return that the caller drops silently is worse than an exception, because the failure leaves no trace at all. `[[nodiscard]]` ([[init-statements]]) on the function (or on the error type itself, `enum class [[nodiscard]] Status { ... };`) makes the compiler warn when a call's result is discarded:

```cpp
parse_gate(user_line, g2);                  // warning: ignoring return value
static_cast<void>(parse_gate(user_line, g2));   // explicit, reviewable "I do not care"
```

a codebase that uses status returns should build with that warning treated as an error, or the channel is only as reliable as every caller's discipline.

### the takeaway

choose the error channel per API from how expected the failure is, who can act on it, and how quickly they must react; then apply the choice consistently within a layer and make ignoring an error something the compiler notices.

### optional challenge

pick an error channel for each: (a) opening the main configuration file at startup; (b) parsing 10,000 log lines a second, about 1% of them malformed; (c) a 1 kHz control loop reading a sensor that occasionally times out; (d) looking up a key in a cache that may not contain it.

<details>
<summary>answer</summary>

(a) an exception: it happens once, the process cannot do its job without the file, and a clear exception with context is the best report. (b) `std::optional` or an error code: malformed lines are expected, and throwing 100 exceptions a second for an ordinary outcome turns exceptions into control flow. (c) a `[[nodiscard]]` status (or a result type): the loop must decide within its cycle budget, and a throw has no bounded latency; such code is often built with `-fno-exceptions` anyway. (d) `std::optional` (or a pointer that may be null): a miss is a normal answer that needs no explanation.

</details>
