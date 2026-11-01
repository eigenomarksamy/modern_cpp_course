<a id="day-25"></a>

## day 25: `std::variant` and `std::any`: sum types and type-erased values

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 13, 17, 20, 24

### the idea

A radar front end emits three kinds of messages: raw detections, track updates, and heartbeats. The pre-C++17 options were all uncomfortable. A C `union` plus a tag `enum` is fast but nothing stops you reading the wrong member (undefined behavior) or forgetting to destroy a `std::string` member. A `Message` base class with three subclasses (day 13) is safe but heap-allocates every message, adds pointer chasing, and invites `dynamic_cast` ladders in the consumer. Day 24's `std::optional` was "a `T` or nothing". Today is the generalization: "exactly one of these types", with the compiler keeping track of which.

### understanding the concept

`std::variant<A, B, C>` (header `<variant>`) holds exactly one value of one of its alternative types, stored inline (no heap allocation by the variant itself), plus an index saying which one. Its size is at least that of the largest alternative plus room for the index. Assigning a different alternative destroys the old value and constructs the new one, so the lifetime bugs of a raw union cannot happen.

Access comes in three strengths:

- `std::holds_alternative<T>(v)` and `v.index()` ask what is there.
- `std::get<T>(v)` (or `std::get<I>(v)`) returns a reference and throws `std::bad_variant_access` on a mismatch.
- `std::get_if<T>(&v)` returns a pointer, `nullptr` on a mismatch. This is the non-throwing "check and use" form.

The idiomatic way to consume a variant, though, is `std::visit(f, v)`, which calls `f` with the active alternative. If `f` cannot be called with one of the alternatives, the program does not compile, which gives you exhaustiveness checking for free. The usual way to build `f` from several lambdas (day 17) is the `overloaded` helper:

```cpp
template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };
template <class... Fs> overloaded(Fs...) -> overloaded<Fs...>;   // needed in C++17 only
```

It inherits from every lambda's closure type and pulls in all their call operators, so normal overload resolution picks the right one. In C++17 the deduction guide is required; C++20 lets CTAD deduce template arguments for aggregates directly, so the second line becomes unnecessary (though harmless).

Three details complete the picture. A default-constructed variant holds a value-initialized first alternative, so the first type must be default constructible, or you put `std::monostate` first as an explicit "empty" alternative. If constructing the new alternative throws after the old one was destroyed, the variant becomes `valueless_by_exception()`: `index()` returns `std::variant_npos` and `visit` throws `bad_variant_access`. This needs a throwing constructor or move to occur mid-assignment, which is rare, but it means a variant's "always one of the types" invariant has one documented escape hatch. Finally, the set of alternatives is fixed at compile time, which is the design decision that matters most.

**Closed versus open.** With inheritance, adding a new message type means writing one new class, but adding a new operation means touching every class (or adding a virtual function to the base). With a variant, adding an operation is one new visitor, but adding a type means updating every visitor, and the compiler will point at each one. This is the "expression problem" in one paragraph. Use a variant when the set of types is small, known, and owned by you (protocol messages, states, parse results). Use virtual functions when the set must be open to code you do not control (plugins, user-supplied sensors). Variants also give you value semantics: they copy, compare, and live in a `std::vector` contiguously.

`std::any` (header `<any>`) is the other end of the spectrum: it holds a single value of *any* copy-constructible type, with the type erased. You get it back with `std::any_cast<T>`, which must name the exact stored type (no conversions, no base classes). Small objects may be stored inline; whether and how much is implementation-specific, and larger types are heap-allocated. Because the type information is gone from the interface, every reader has to guess and check. Legitimate uses are narrow: a framework that carries a user's context object through code that never looks inside it, or a heterogeneous property bag at a plugin boundary. If you can list the possible types, you want a variant.

### in code

The radar messages as a variant, with an exhaustive visitor:

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

Delete the `Heartbeat` lambda and `std::visit` fails to compile: no call operator accepts a `Heartbeat`. That error is the feature. (A generic `[](const auto&) {}` catch-all silences it, and with it, the exhaustiveness check.)

A variant as a result type, the error-handling option promised on day 20. It carries the reason that `std::optional` could not:

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

This works, but it is clunky: nothing in the type says which alternative is the success case. C++23's `std::expected<T, E>` is the purpose-built version; on C++17 many code bases use a small `Result<T, E>` wrapper or a library such as `tl::expected`.

And `std::any`, to see why it is the last resort:

```cpp
#include <any>

std::any a = 42;
int*  p = std::any_cast<int>(&a);    // ok: pointer form, exact type
long* q = std::any_cast<long>(&a);   // nullptr: int is not long, no conversion
double d = std::any_cast<double>(a); // throws std::bad_any_cast
```

### in practice

Variants make good state machines because each state carries only the data that is meaningful in that state. A robot arm controller:

```cpp
struct Idle   {};
struct Moving { double target_rad; double started_s; };
struct Fault  { std::string reason; };
using ArmState = std::variant<Idle, Moving, Fault>;

ArmState step(const ArmState& s, double now_s, double pos_rad) {
    return std::visit(overloaded{
        [](const Idle&) -> ArmState { return Idle{}; },
        [&](const Moving& m) -> ArmState {
            if (std::abs(pos_rad - m.target_rad) < 1e-3) return Idle{};
            if (now_s - m.started_s > 5.0)               return Fault{"move timeout"};
            return m;
        },
        [](const Fault& f) -> ArmState { return f; },   // only an explicit reset leaves Fault
    }, s);
}
```

Compare the usual alternative: one struct with a `state` enum plus `target_rad`, `started_s`, and `reason` fields, all present all the time. There, nothing stops code from reading `reason` while `Idle` or forgetting to clear `started_s`. With the variant, those states are unrepresentable. The explicit `-> ArmState` return types matter: without them, the lambdas would return `Idle`, `Moving`, and so on, and `visit` requires every call to return the same type.

### watch out for

The converting constructor picks an alternative by overload resolution, and implicit conversions can surprise you:

```cpp
std::variant<std::string, bool> v = "abc";   // which alternative?
```

Under the original C++17 wording this stored `bool`: `const char*` to `bool` is a standard conversion and beat the user-defined conversion to `std::string`. C++20 (paper P0608) excluded narrowing and boolean conversions from this selection, so it now stores the `std::string`. GCC 12's libstdc++ applies the fix even with `-std=c++17` (index 0, checked), but older standard libraries do not. The robust habits: avoid alternatives that convert into each other (`bool`, `int`, `double` together is asking for trouble), and when in doubt, say what you mean with `std::in_place_type<std::string>` or by constructing the alternative explicitly.

### the takeaway

`std::variant` is a closed, value-semantic sum type: inline storage, an exhaustive `visit`, and unrepresentable invalid states. Reach for it when you own a small, fixed set of types, keep virtual functions for open sets, and treat `std::any` as a tool for code that genuinely must not know the type.

### optional challenge

Your team adds a fourth radar message, `Calibration`. With the variant design, what does the compiler do for you, and what does it not do? What would the answer be with a `Message` base class and virtual `handle()`?

<details>
<summary>answer</summary>

With the variant, every `std::visit` built from explicit per-type lambdas stops compiling until it handles `Calibration`, so the compiler hands you a list of places to update. It does not help where someone used a generic `auto` catch-all lambda or `get_if` checks, which silently ignore the new type. With the base class, adding `Calibration` means writing one class and implementing the pure virtuals; existing consumers compile unchanged, which is great if they never need to know, and a silent gap if some of them should have treated calibration specially. Closed sets trade "edit many places" for "the compiler finds them"; open sets trade the opposite way.

</details>
