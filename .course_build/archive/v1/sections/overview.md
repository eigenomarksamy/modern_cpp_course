<a id="course-overview"></a>

## course overview

```text
 weeks 1 to 4: a complete C++17 refresher

 [1 fundamentals] ─▶ [2 ownership] ─▶ [3 library, templates] ─▶ [4 C++17 in practice]
                                                                          │
 [8 production] ◀─ [7 design] ◀─ [6 concurrency] ◀─ [5 C++20 toolbox] ◀───┘

 weeks 5 to 8: C++20 and production engineering
```

| week | theme | what you will be able to do by the end |
| --- | --- | --- |
| [1](#week-1) | rediscovering C++ fundamentals | explain how source becomes a binary, pick the right initialization, reason about lifetimes and value categories, and recognize undefined behavior |
| [2](#week-2) | ownership and object-oriented C++ | build resource-safe types with RAII, apply the rule of zero, implement and reason about moves, express ownership with smart pointers, and choose composition over inheritance |
| [3](#week-3) | standard library and generic programming | choose containers by cost, write intent-revealing code with algorithms and lambdas, write templates with perfect forwarding, and design for exception safety |
| [4](#week-4) | modernizing with C++17 | use structured bindings, `if constexpr`, `optional`, `variant`, `string_view`, folds, and `filesystem`, and refactor legacy code with them |
| [5](#week-5) | the C++20 toolbox | constrain templates with concepts, build lazy pipelines with ranges, pass buffers as `span`, default comparisons, compute at compile time, and format with `std::format` |
| [6](#week-6) | concurrency and multithreading | run and stop threads with `jthread`, protect state with mutexes, coordinate with condition variables and futures, use atomics with a correct memory model, and avoid deadlocks |
| [7](#week-7) | software design and deeper C++ | apply SOLID with judgment, inject dependencies for testing, use patterns idiomatically, choose between static, dynamic, and type-erased polymorphism, design hard-to-misuse APIs, and get started with modules and coroutines |
| [8](#week-8) | production engineering and integration | benchmark honestly, design for cache locality, control allocations, test and observe production code, refactor legacy code incrementally, and combine it all in one small system |

### the threads that run through every week

Some ideas are not confined to one week; they come back repeatedly, each time with more depth:

- **lifetime and ownership:** days 03, 08, 10 to 12, 17, 26, 31, 36, 45, 47, 48.
- **error handling:** days 20, 24, 25, 27, 39, 47, 53.
- **compile time versus run time:** days 18, 23, 29, 33, 46.
- **design judgment** (coupling, cohesion, abstraction cost): days 09, 13, 17, 25, 37, 43 to 47, 54.
- **performance and measurement:** days 15, 16, 40, 50 to 52.

### pacing

Each day takes 5 to 10 minutes. If you miss a day, read two the next day, or use the review day to catch up; the reviews are deliberately light. If a topic hooks you, the [references](#references) at the end point to the best places to go deeper.
