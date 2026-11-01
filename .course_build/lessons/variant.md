---
title: `std::variant` and `std::visit`
standard: C++17
objective: model "exactly one of these types" with `std::variant`, consume it with an exhaustive `std::visit`, and use it as a result type
prerequisites: optional, fold-expressions, lambdas
difficulty: 2
---

### the idea

a radar front end emits three kinds of messages: raw detections, track updates, and heartbeats. the pre-C++17 options were all uncomfortable. a C `union` plus a tag `enum` is fast but nothing stops you reading the wrong member (undefined behavior) or forgetting to destroy a `std::string` member. a `Message` base class with three subclasses ([[virtual-dispatch]]) is safe but heap-allocates every message, adds pointer chasing, and invites `dynamic_cast` ladders in the consumer. [[optional]]'s `std::optional` was "a `T` or nothing". today is the generalization: "exactly one of these types", with the compiler keeping track of which.

### understanding the concept

`std::variant<A, B, C>` (header `<variant>`) holds exactly one value of one of its alternative types, stored inline (no heap allocation by the variant itself), plus an index saying which one. its size is at least that of the largest alternative plus room for the index. assigning a different alternative destroys the old value and constructs the new one, so the lifetime bugs of a raw union cannot happen.

access comes in three strengths:

- `std::holds_alternative<T>(v)` and `v.index()` ask what is there.
- `std::get<T>(v)` (or `std::get<I>(v)`) returns a reference and throws `std::bad_variant_access` on a mismatch.
- `std::get_if<T>(&v)` returns a pointer, `nullptr` on a mismatch. this is the non-throwing "check and use" form.

the idiomatic way to consume a variant, though, is `std::visit(f, v)`, which calls `f` with the active alternative. if `f` cannot be called with one of the alternatives, the program does not compile, which gives you exhaustiveness checking for free. the usual way to build `f` from several lambdas ([[lambdas]]) is the `overloaded` helper:

```cpp complete
template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };
template <class... Fs> overloaded(Fs...) -> overloaded<Fs...>;   // needed in C++17 only
```

it inherits from every lambda's closure type and pulls in all their call operators, so normal overload resolution picks the right one. in C++17 the deduction guide is required; C++20 lets CTAD deduce template arguments for aggregates directly, so the second line becomes unnecessary (though harmless).

three details complete the picture. a default-constructed variant holds a value-initialized first alternative, so the first type must be default constructible, or you put `std::monostate` first as an explicit "empty" alternative. if constructing the new alternative throws after the old one was destroyed, the variant becomes `valueless_by_exception()`: `index()` returns `std::variant_npos` and `visit` throws `bad_variant_access`. this needs a throwing constructor or move to occur mid-assignment, which is rare, but it means a variant's "always one of the types" invariant has one documented escape hatch. finally, the set of alternatives is fixed at compile time, which is the design decision that matters most.

### in code

the radar messages as a variant, with an exhaustive visitor:

```cpp
#include <cstdint>
#include <cstdio>
#include <variant>

struct Detection   { float range_m, azimuth_deg, snr_db; };
struct TrackUpdate { int id; float range_m, vel_mps; };
struct Heartbeat   { std::uint32_t seq; };
using RadarMsg = std::variant<Detection, TrackUpdate, Heartbeat>;

void handle(const RadarMsg& m) {
    std::visit(overloaded{
        [](const Detection& d)   { std::printf("det %.1f m\n", d.range_m); },
        [](const TrackUpdate& t) { std::printf("trk %d\n", t.id); },
        [](const Heartbeat& h)   { std::printf("hb %u\n", static_cast<unsigned>(h.seq)); },
    }, m);
}

int main() {
    RadarMsg m = TrackUpdate{7, 1520.0f, -3.2f};
    handle(m);                                       // prints: trk 7
    if (auto* t = std::get_if<TrackUpdate>(&m))      // pointer form: no exception
        t->vel_mps = 0.0f;
    m = Heartbeat{42};                               // old TrackUpdate destroyed
    handle(m);                                       // prints: hb 42
}
```

delete the `Heartbeat` lambda and `std::visit` fails to compile: no call operator accepts a `Heartbeat`. that error is the feature. (a generic `[](const auto&) {}` catch-all silences it, and with it, the exhaustiveness check.)

### in practice

a variant as a result type, the error-handling option promised on [[error-strategy]]. it carries the reason that `std::optional` could not:

```cpp
#include <string>
#include <string_view>

struct ParseError { std::size_t column; std::string what; };
using ParseResult = std::variant<Detection, ParseError>;

ParseResult parse_detection(std::string_view line);

void ingest(std::string_view line) {
    auto r = parse_detection(line);
    if (auto* err = std::get_if<ParseError>(&r)) {
        std::printf("bad line at column %zu: %s\n", err->column, err->what.c_str());
        return;
    }
    const Detection& d = std::get<Detection>(r);
    std::printf("det %.1f m\n", d.range_m);
}
```

this works, but it is clunky: nothing in the type says which alternative is the success case. C++23's `std::expected<T, E>` is the purpose-built version; on C++17 many code bases use a small `Result<T, E>` wrapper or a library such as `tl::expected`.

### watch out for

the converting constructor picks an alternative by overload resolution, and implicit conversions can surprise you:

```cpp
std::variant<std::string, bool> v = "abc";   // which alternative?
```

under the original C++17 wording this stored `bool`: `const char*` to `bool` is a standard conversion and beat the user-defined conversion to `std::string`. C++20 (paper P0608) excluded narrowing and boolean conversions from this selection, so it now stores the `std::string`. GCC 12's libstdc++ applies the fix even with `-std=c++17` (index 0, checked), but older standard libraries do not. the robust habits: avoid alternatives that convert into each other (`bool`, `int`, `double` together is asking for trouble), and when in doubt, say what you mean with `std::in_place_type<std::string>` or by constructing the alternative explicitly.

### the takeaway

`std::variant` is a value-semantic sum type with inline storage: consume it with `std::visit` and explicit per-type lambdas, so the compiler checks that every alternative is handled.

### optional challenge

given `using Msg = std::variant<std::monostate, Detection, Heartbeat>;` and `Msg m;`, what do `m.index()`, `std::get_if<Detection>(&m)`, and `std::get<Detection>(m)` give, and what changes after `m = Heartbeat{1};`?

<details>
<summary>answer</summary>

a default-constructed variant holds a value-initialized first alternative, here `std::monostate`, so `m.index()` is 0, `std::get_if<Detection>(&m)` returns `nullptr`, and `std::get<Detection>(m)` throws `std::bad_variant_access`. after the assignment, `index()` is 2 and the `Detection` accessors behave the same way, while `std::get<Heartbeat>(m).seq` is 1. putting `std::monostate` first is the explicit way to give a variant an "empty" state when none of the real alternatives has a sensible default.

</details>
