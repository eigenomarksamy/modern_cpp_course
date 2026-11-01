---
title: patterns in modern C++: strategy
standard: C++17
objective: make an algorithm a replaceable part with a virtual interface, `std::function`, or a template parameter, and choose by when and how often it varies
prerequisites: test-seams, variant-design
difficulty: 2
---

### the idea

the classic pattern catalogue was written for C++98 and Smalltalk, before lambdas, `std::function`, `std::variant`, and smart pointers. some patterns survive unchanged, some shrink to a single line, and some need modern care that the original books never mentioned, such as who owns an observer and which thread calls it. the simplest one to start with is strategy: an algorithm that should be a replaceable part.

### understanding the concept

a pattern is a name for a recurring solution, not a goal. its main value is vocabulary: "the planner takes a cost strategy" tells a reviewer a lot in six words. the risk is building the pattern because it is a pattern.

- **strategy** makes an algorithm a replaceable part. in C++ you have three ways to plug it in, with different tradeoffs (the table below).

several other classic patterns collapse into language features. command is usually a lambda stored in a `std::function` or a queue. visitor over a closed set of types is `std::visit` on a `std::variant` ([[variant]]). template method is often better served by passing a callable than by inheritance.

### in code

**strategy, three ways.** an exponential moving average smooths radar range measurements inside a tracker.

```cpp complete
#include <functional>
#include <memory>

struct Ema {                                    // the algorithm as a plain value type
    double alpha;
    double y = 0.0;
    bool primed = false;
    double operator()(double x) {
        y = primed ? alpha * x + (1.0 - alpha) * y : x;
        primed = true;
        return y;
    }
};

// (a) virtual interface: strategies must inherit
class Smoother {
public:
    virtual ~Smoother() = default;
    virtual double operator()(double x) = 0;
};
class EmaSmoother final : public Smoother {
public:
    explicit EmaSmoother(double alpha) : ema_{alpha} {}
    double operator()(double x) override { return ema_(x); }
private:
    Ema ema_;
};
struct TrackerV { std::unique_ptr<Smoother> smooth; };

// (b) std::function: any callable with the right signature
struct TrackerF { std::function<double(double)> smooth; };

// (c) template parameter: fixed at compile time
template <typename Smooth>
struct TrackerT { Smooth smooth; };

// TrackerV v{std::make_unique<EmaSmoother>(0.3)};
// TrackerF f{Ema{0.3}};
// TrackerT<Ema> t{Ema{0.3}};
```

| | virtual interface | `std::function` | template parameter |
|---|---|---|---|
| chosen at | run time | run time | compile time |
| strategy types | must derive from `Smoother` | any copyable callable | any type the code compiles with (use a concept in C++20) |
| call mechanism | indirect call, rarely inlined | indirect call through type erasure; construction may allocate | direct call, inlinable |
| copying the owner | needs a `clone()` | value semantics | value semantics |
| mixed strategies in one container | yes | yes | no, each is a distinct type |
| best for | several related operations per strategy | one operation, callbacks | hot inner loops, per-build choice |

### in practice

a tracker library usually needs more than one of these at once. the smoothing filter for each track is chosen per build and runs for every measurement, so it is a template parameter (or a concrete type) and inlines into the update loop. the gating policy is chosen per deployment from a configuration file and runs once per frame, so a `std::function` or a small virtual interface is the honest choice. the cost model for association needs three related operations that must agree with each other (cost, gate size, and a debugging description), which is the case a virtual interface handles best: the operations travel together as one object. picking per call site, rather than one mechanism for the whole library, is what keeps both the hot path and the configuration flexible.

### watch out for

**a stateful strategy is copied, not shared.** `Ema` carries state (`y` and `primed`), and every mechanism above stores its own copy:

```cpp
Ema shared{0.3};
TrackerF a{shared};
TrackerF b{shared};    // a and b each smooth independently; shared is never updated
```

that is usually right (each track needs its own filter state), but it surprises code that expects to reset or inspect "the" strategy through the original object. the standard algorithms copy function objects freely too. when state really must be shared, make that explicit with a reference or pointer member, and decide who owns the shared state.

### the takeaway

a strategy is a replaceable algorithm: plug it in as a template parameter for hot, per-build choices, as a `std::function` for single operations chosen at run time, and as a virtual interface when several related operations travel together.

### optional challenge

pick a mechanism for each: (a) a path cost function selected from a configuration file at startup; (b) a per-pixel kernel in an image filter; (c) a planner policy that provides a cost, a heuristic, and a neighbor generator that must stay consistent.

<details>
<summary>answer</summary>

(a) `std::function<double(const Edge&)>` (or a virtual interface): chosen at run time from data, and called often enough to matter only if profiling says so. (b) a template parameter: called millions of times per image, so inlining and vectorization matter, and the choice is known at compile time. (c) a virtual interface (or a template constrained by a concept, if the choice is per build): three operations that must agree belong in one object, and a single interface keeps them from being mixed and matched by accident.

</details>
