---
title: closed sets and open sets: variant state machines and `std::any`
standard: C++17
objective: choose between `std::variant`, virtual functions, and `std::any` by whether the set of types is closed, open, or unknowable
prerequisites: variant, composition-over-inheritance
difficulty: 2
---

### the idea

a radar library has two kinds of polymorphism. its message types (detection, track update, heartbeat) are defined by the protocol and change only when the protocol does. its detectors are written by users, in code the library has never seen. a single mechanism cannot serve both well. the choice between a variant and a virtual interface is not a matter of taste; it follows from one question: who gets to add new types?

### understanding the concept

**closed versus open.** with inheritance, adding a new message type means writing one new class, but adding a new operation means touching every class (or adding a virtual function to the base). with a variant, adding an operation is one new visitor, but adding a type means updating every visitor, and the compiler will point at each one. this is the "expression problem" in one paragraph. use a variant when the set of types is small, known, and owned by you (protocol messages, states, parse results). use virtual functions when the set must be open to code you do not control (plugins, user-supplied sensors). variants also give you value semantics: they copy, compare, and live in a `std::vector` contiguously.

`std::any` (header `<any>`) is the other end of the spectrum: it holds a single value of *any* copy-constructible type, with the type erased. you get it back with `std::any_cast<T>`, which must name the exact stored type (no conversions, no base classes). small objects may be stored inline; whether and how much is implementation-specific, and larger types are heap-allocated. because the type information is gone from the interface, every reader has to guess and check. legitimate uses are narrow: a framework that carries a user's context object through code that never looks inside it, or a heterogeneous property bag at a plugin boundary. if you can list the possible types, you want a variant.

### in code

variants make good state machines because each state carries only the data that is meaningful in that state. a robot arm controller:

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

compare the usual alternative: one struct with a `state` enum plus `target_rad`, `started_s`, and `reason` fields, all present all the time. there, nothing stops code from reading `reason` while `Idle` or forgetting to clear `started_s`. with the variant, those states are unrepresentable. the explicit `-> ArmState` return types matter: without them, the lambdas would return `Idle`, `Moving`, and so on, and `visit` requires every call to return the same type.

and `std::any`, to see why it is the last resort:

```cpp complete
#include <any>

std::any a = 42;
int*  p = std::any_cast<int>(&a);    // ok: pointer form, exact type
long* q = std::any_cast<long>(&a);   // nullptr: int is not long, no conversion
double d = std::any_cast<double>(a); // throws std::bad_any_cast
```

### in practice

the radar library uses both mechanisms, each where it fits. `RadarMsg` is a `std::variant`: the library owns the protocol, consumers visit messages by value in tight loops, and adding a message type is a deliberate protocol change whose consequences the compiler enumerates. `Detector` is an abstract class with a virtual `detect()`: users ship new detectors without touching the library, and the library calls them once per frame through `std::unique_ptr<Detector>`. a project that forced messages into a class hierarchy would pay for heap allocation per message and lose exhaustiveness checking; one that forced detectors into a variant would make every user edit the library to add a type. the design question is the same one in both cases, and the answers differ because the owners differ.

### watch out for

**a catch-all lambda turns off exhaustiveness checking.** a generic lambda accepts every alternative, including ones added later:

```cpp
std::visit(overloaded{
    [](const Detection& d) { record(d); },
    [](const auto&) {},                  // "ignore everything else"
}, msg);
```

when `Calibration` joins the variant, this visit compiles unchanged and silently drops calibration messages. sometimes that is exactly right; often it is a bug that the variant would otherwise have caught. prefer one explicit lambda per alternative in code that must react to every message type, and reserve catch-alls for visitors that genuinely care about only one or two.

### the takeaway

use a variant when you own a small, fixed set of types, virtual functions when the set must stay open to code you do not control, and `std::any` only where the code genuinely must not know the type.

### optional challenge

your team adds a fourth radar message, `Calibration`. with the variant design, what does the compiler do for you, and what does it not do? what would the answer be with a `Message` base class and virtual `handle()`?

<details>
<summary>answer</summary>

with the variant, every `std::visit` built from explicit per-type lambdas stops compiling until it handles `Calibration`, so the compiler hands you a list of places to update. it does not help where someone used a generic `auto` catch-all lambda or `get_if` checks, which silently ignore the new type. with the base class, adding `Calibration` means writing one class and implementing the pure virtuals; existing consumers compile unchanged, which is great if they never need to know, and a silent gap if some of them should have treated calibration specially. closed sets trade "edit many places" for "the compiler finds them"; open sets trade the opposite way.

</details>
