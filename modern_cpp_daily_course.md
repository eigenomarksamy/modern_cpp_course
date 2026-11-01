# modern c++ daily course

*version 2.0: 119 days of C++17 and C++20 in 17 modules. generated from `.course_build/` by `course.py assemble`; edit the lesson and section sources there, then reassemble.*

<a id="introduction"></a>

## introduction and learning philosophy

you already write C++ for a living. you have shipped code that runs on robots, servers, or build farms, and you have debugged the kind of crash that only happens in release builds on a Tuesday. this course isn't here to teach you C++ from scratch. it is a structured way to revisit the parts of the language you use every day, understand the mechanics underneath them, and get fluent with the C++17 and C++20 features that make production code safer and clearer.

the course has 119 daily lessons in 17 modules: 102 lessons that teach one idea each, and 17 short reviews, one at the end of every module. each day takes about 5 to 10 minutes of focused reading, code included. the length of the course follows from the material: a dense topic gets several days, each with one clear objective, rather than one day that tries to cover everything.

### how this course thinks

- **mechanics before features.** move semantics make sense once value categories do. `std::string_view` is obvious once lifetime is. so the first modules rebuild the foundations, and later features are explained in terms of them.
- **one idea per day.** each lesson has one primary objective, stated at the top. difficult topics are spread over consecutive days: the problem, the mechanism, the implementation, and the pitfalls.
- **examples over prose.** every lesson leans on small, purposeful code: naive version, then improved version; buggy version, then fixed version; "predict the output" puzzles. read the code as carefully as the text.
- **judgment over rules.** "never use raw pointers", "always use algorithms", "SOLID everything": rules like these are compressed experience, and they leak. each lesson tries to say when a feature is the right tool, when it is not, and what it costs.
- **design is everywhere.** ownership, coupling, error handling, testability, and compile-time versus runtime tradeoffs show up in every module, not only in the design modules.
- **honesty about performance.** you will not find "X is 3x faster" here. you will find complexity, mechanisms (allocations, cache lines, indirections), and how to measure.

### how each day is structured

instructional days follow the same shape, so you always know where you are:

| section | what it gives you |
| --- | --- |
| the idea | a question, a bug, or a misconception that motivates the topic |
| understanding the concept | the mechanics and the relevant rules |
| in code | one to three short examples, often before/after or buggy/fixed |
| in practice | where it matters in real systems |
| watch out for | the most common trap or tradeoff |
| the takeaway | one sentence worth remembering |
| optional challenge | a short puzzle, with a collapsed answer |
| going deeper | optional extra rules, edge cases, and longer examples (collapsed on the website) |

the core reading is everything before "going deeper". the optional sections never hold anything you need for correctness; they hold the detail you may want on a second pass.

review days have a recap, review questions (including spaced-repetition questions from earlier modules), a mini exercise, collapsed answers, and a note on how the module connects to the rest.

### conventions used in the lessons

- each day lists its **standard** (`C++17` or `C++20`): the minimum language version its examples need. if a single snippet needs something newer, it says so. C++23 features appear only as clearly labelled forward notes.
- each day lists an approximate **reading time**. it is an estimate from the amount of prose, the amount and density of code, and the lesson's difficulty; your pace will differ, and the estimate is most useful for comparing days with each other.
- `// prints: ...` shows expected output. `// BUG:` marks code that is wrong on purpose.
- on the website, every C++ example is labelled: a complete example compiles on its own, a snippet is a fragment of a larger program, and examples that do not compile on purpose or contain undefined behavior say so. complete examples link to Compiler Explorer with the right standard selected.
- three terms are used precisely, because the difference matters:
  - **undefined behavior (UB):** the standard places no requirements on the program. the optimizer is allowed to assume it never happens, which is why UB bugs can look like time travel.
  - **unspecified behavior:** the program does one of several permitted things, and the implementation doesn't have to tell you which (for example, the order in which function arguments are evaluated).
  - **implementation-defined behavior:** unspecified, but the implementation must document its choice (for example, `sizeof(long)`).
- cross references look like [day 01](#day-01) and jump to that lesson.

### setting up a playground

any recent compiler works. a reasonable baseline:

```sh
# GCC 13+ or Clang 17+ for full C++20 library coverage including <format>
g++ -std=c++20 -Wall -Wextra -pedantic -g -fsanitize=address,undefined main.cpp -o main
./main
```

sanitizers are available with GCC and Clang on Linux and macOS (MSVC supports AddressSanitizer). [Compiler Explorer](https://godbolt.org) is ideal for the short examples, and it lets you compare compilers and look at the generated assembly when a lesson talks about what the compiler does.

### how to use it

read one day at a time, ideally with a compiler open. do the optional challenge if it catches your interest, and don't skip the review days: they are short, and retrieval practice is what makes the material stick. lessons are never locked, so you can jump to any topic, but the order is deliberate: each lesson lists what it builds on.

the modules through [day 59](#day-59) form a complete, standalone C++17 refresher. the rest builds on it with C++20, concurrency, design, and production engineering, ending with a small program that brings the pieces together.

this is version 2.0 of the course. each day is its own source file, so lessons can be expanded, corrected, split, or updated for newer standards one at a time.

<a id="course-overview"></a>

## course overview

the modules build on each other in order. the first nine rebuild the foundations and finish with a complete C++17 refresher; the rest add C++20, concurrency, design, and production engineering.

```text
 foundations -> values -> lifecycle -> ownership -> polymorphism -> library -> generic
      -> results -> variants, views, files              (a complete C++17 refresher)
      -> C++20 generic -> C++20 everyday
      -> threads -> futures and atomics
      -> design -> abstractions -> performance -> production
```

the curriculum map below lists every day: its module, its title, the standard its examples need, and its approximate core reading time. each lesson page also states its objective and the lessons it builds on.

### the threads that run through every module

some ideas are not confined to one module; they come back repeatedly, each time with more depth:

- **lifetime and ownership:** [day 06](#day-06), [day 08](#day-08), [day 16](#day-16), [day 21](#day-21), [day 28](#day-28), [day 38](#day-38), [day 55](#day-55), [day 64](#day-64), [day 65](#day-65), [day 75](#day-75), [day 95](#day-95), [day 100](#day-100), [day 102](#day-102).
- **error handling:** [day 49](#day-49), [day 50](#day-50), [day 51](#day-51), [day 53](#day-53), [day 57](#day-57), [day 81](#day-81), [day 99](#day-99), [day 112](#day-112).
- **compile time versus run time:** [day 40](#day-40), [day 44](#day-44), [day 60](#day-60), [day 69](#day-69), [day 70](#day-70), [day 92](#day-92), [day 97](#day-97).
- **design judgment** (coupling, cohesion, abstraction cost): [day 18](#day-18), [day 32](#day-32), [day 38](#day-38), [day 54](#day-54), [day 77](#day-77), [day 89](#day-89), [day 90](#day-90), [day 91](#day-91), [day 93](#day-93), [day 115](#day-115).
- **performance and measurement:** [day 05](#day-05), [day 34](#day-34), [day 36](#day-36), [day 85](#day-85), [day 105](#day-105), [day 107](#day-107), [day 109](#day-109).

### pacing

each day takes about 5 to 10 minutes. if you miss a day, read two the next day, or use the review day to catch up; the reviews are deliberately light. if a topic hooks you, open the lesson's "going deeper" section, or the [references](#references) at the end.

<a id="table-of-contents"></a>

## table of contents

- [introduction and learning philosophy](#introduction)
- [course overview](#course-overview)
- [curriculum map](#curriculum)
- [progress checklist](#progress-checklist)
- [module 1: how programs and objects come to be](#module-foundations)
- [module 2: references, values, and the language contract](#module-values)
- [module 3: resources and the object lifecycle](#module-lifecycle)
- [module 4: moves and ownership](#module-ownership)
- [module 5: inheritance and polymorphism](#module-polymorphism)
- [module 6: containers, algorithms, and lambdas](#module-library)
- [module 7: templates and generic programming](#module-generic)
- [module 8: results and failure](#module-results)
- [module 9: variants, views, and files](#module-cpp17)
- [module 10: C++20: concepts, ranges, and span](#module-cpp20-generic)
- [module 11: C++20: comparisons, compile time, and formatting](#module-cpp20-everyday)
- [module 12: threads and synchronization](#module-threads)
- [module 13: futures, atomics, and concurrency design](#module-async)
- [module 14: design principles and patterns](#module-design)
- [module 15: polymorphism choices, APIs, modules, and coroutines](#module-abstractions)
- [module 16: performance](#module-performance)
- [module 17: production engineering and integration](#module-production)
- [modern C++17/20 cheat sheet](#cheat-sheet)
- [references for deeper study](#references)

<a id="curriculum"></a>

## curriculum map

**[module 1: how programs and objects come to be](#module-foundations)**: how source becomes a program, how objects get their first values, how big they are, and how long they live.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 01 | [from source file to running program](#day-01) | C++17 | 7 |  |
| 02 | [linkage and the one definition rule](#day-02) | C++17 | 9 |  |
| 03 | [the many faces of initialization](#day-03) | C++17 | 10 | what exactly counts as an aggregate |
| 04 | [integer types, promotions, and conversions](#day-04) | C++17 | 7 |  |
| 05 | [objects in memory: size, alignment, and padding](#day-05) | C++17 | 7 | empty classes and the empty base optimization; standard-layout types and `offsetof` |
| 06 | [storage duration and object lifetime](#day-06) | C++17 | 8 | shutdown order and leaky singletons |
| 07 | [review: how programs and objects come to be](#day-07) | C++17 | 7 |  |

**[module 2: references, values, and the language contract](#module-values)**: what you can safely refer to, what an expression's category decides, and what the standard leaves undefined.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 08 | [temporaries, lifetime extension, and dangling references](#day-08) | C++17 | 6 |  |
| 09 | [pointers and references](#day-09) | C++17 | 8 |  |
| 10 | [const as a contract](#day-10) | C++17 | 8 |  |
| 11 | [value categories without the headache](#day-11) | C++17 | 7 | `decltype` and value categories |
| 12 | [copy elision and temporary materialization](#day-12) | C++17 | 8 |  |
| 13 | [undefined behavior and the optimizer](#day-13) | C++17 | 6 |  |
| 14 | [the usual suspects: aliasing, punning, and evaluation order](#day-14) | C++17 | 7 |  |
| 15 | [review: references, values, and the language contract](#day-15) | C++17 | 8 |  |

**[module 3: resources and the object lifecycle](#module-lifecycle)**: RAII, constructors and invariants, construction order, and what copying and moving an object really mean.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 16 | [RAII: let scope do the cleanup](#day-16) | C++17 | 10 |  |
| 17 | [scope guards: cleanup without a new class](#day-17) | C++17 | 5 |  |
| 18 | [constructors that establish invariants](#day-18) | C++17 | 7 |  |
| 19 | [construction and destruction order](#day-19) | C++17 | 9 |  |
| 20 | [copying: deep, shallow, and the double free](#day-20) | C++17 | 7 |  |
| 21 | [moving: transferring resources instead of copying them](#day-21) | C++17 | 8 |  |
| 22 | [review: resources and the object lifecycle](#day-22) | C++17 | 8 |  |

**[module 4: moves and ownership](#module-ownership)**: when moves are trusted, which special members the compiler writes, the rule of zero, and ownership written into types.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 23 | [noexcept moves and the strong guarantee](#day-23) | C++17 | 5 |  |
| 24 | [the special member functions and when the compiler writes them](#day-24) | C++17 | 7 |  |
| 25 | [the rule of zero](#day-25) | C++17 | 7 | copy-and-swap |
| 26 | [exclusive ownership with `std::unique_ptr`](#day-26) | C++17 | 5 |  |
| 27 | [shared ownership with `std::shared_ptr` and `std::weak_ptr`](#day-27) | C++17 | 9 |  |
| 28 | [ownership in function signatures](#day-28) | C++17 | 6 |  |
| 29 | [review: moves and ownership](#day-29) | C++17 | 9 |  |

**[module 5: inheritance and polymorphism](#module-polymorphism)**: how virtual dispatch works, the two rules that protect polymorphic objects, and composition as the default.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 30 | [virtual functions and dynamic dispatch](#day-30) | C++17 | 7 |  |
| 31 | [virtual destructors and object slicing](#day-31) | C++17 | 7 |  |
| 32 | [composition, interfaces, and substitutability](#day-32) | C++17 | 5 |  |
| 33 | [review: inheritance and polymorphism](#day-33) | C++17 | 7 |  |

**[module 6: containers, algorithms, and lambdas](#module-library)**: the standard library as a vocabulary: containers by cost, algorithms over iterator ranges, and lambdas as objects.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 34 | [containers and what they cost](#day-34) | C++17 | 9 |  |
| 35 | [maps, sets, and node handles](#day-35) | C++17 | 7 |  |
| 36 | [iterators and algorithms over raw loops](#day-36) | C++17 | 10 | partition and stable sort; parallel execution policies |
| 37 | [lambdas are objects: closures and captures](#day-37) | C++17 | 9 |  |
| 38 | [lambdas that outlive their scope: callbacks and `std::function`](#day-38) | C++17 | 9 |  |
| 39 | [review: containers, algorithms, and lambdas](#day-39) | C++17 | 9 |  |

**[module 7: templates and generic programming](#module-generic)**: deduction, class templates, perfect forwarding, and the C++17 tools that replace template tricks.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 40 | [function templates and argument deduction](#day-40) | C++17 | 8 | before concepts: SFINAE and `std::enable_if` |
| 41 | [class templates, CTAD, and specialization](#day-41) | C++17 | 9 |  |
| 42 | [forwarding references and `std::forward`](#day-42) | C++17 | 9 |  |
| 43 | [variadic templates and perfect-forwarding factories](#day-43) | C++17 | 7 |  |
| 44 | [compile-time branching with if constexpr](#day-44) | C++17 | 8 | what a `constexpr` function may do in C++17 |
| 45 | [fold expressions](#day-45) | C++17 | 8 |  |
| 46 | [review: templates and generic programming](#day-46) | C++17 | 7 |  |

**[module 8: results and failure](#module-results)**: how functions hand back results and failures: unpacking, scoping, exception safety, error channels, and std::optional.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 47 | [structured bindings](#day-47) | C++17 | 8 |  |
| 48 | [if and switch initializers, and attributes that catch mistakes](#day-48) | C++17 | 8 |  |
| 49 | [exception safety guarantees](#day-49) | C++17 | 9 |  |
| 50 | [choosing an error-handling strategy](#day-50) | C++17 | 6 |  |
| 51 | [`std::optional`: modeling "maybe"](#day-51) | C++17 | 9 | in-place construction; optional parameters; C++23 monadic operations |
| 52 | [review: results and failure](#day-52) | C++17 | 6 |  |

**[module 9: variants, views, and files](#module-cpp17)**: the rest of the C++17 vocabulary, used together in a realistic refactoring; the end of the standalone refresher.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 53 | [`std::variant` and `std::visit`](#day-53) | C++17 | 8 |  |
| 54 | [closed sets and open sets: variant state machines and `std::any`](#day-54) | C++17 | 7 |  |
| 55 | [`std::string_view`: borrowing characters](#day-55) | C++17 | 9 |  |
| 56 | [parsing without allocation: views and from_chars](#day-56) | C++17 | 7 |  |
| 57 | [`std::filesystem`: portable paths and directories](#day-57) | C++17 | 7 |  |
| 58 | [a practical C++17 refactoring](#day-58) | C++17 | 9 |  |
| 59 | [review: the C++17 vocabulary, and a complete refresher](#day-59) | C++17 | 9 |  |

**[module 10: C++20: concepts, ranges, and span](#module-cpp20-generic)**: constrained templates, range algorithms and lazy views, and std::span for borrowing contiguous data.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 60 | [concepts: constraining templates](#day-60) | C++20 | 8 |  |
| 61 | [writing your own concepts](#day-61) | C++20 | 8 |  |
| 62 | [range algorithms and projections](#day-62) | C++20 | 5 |  |
| 63 | [views: lazy pipelines](#day-63) | C++20 | 9 | sorting before filtering |
| 64 | [views and lifetimes: what a pipeline refers to](#day-64) | C++20 | 5 |  |
| 65 | [`std::span`: views over contiguous memory](#day-65) | C++20 | 10 | bytes for serialization; span, string_view, and range views; a `const` span is not a span of `const` |
| 66 | [review: concepts, ranges, and span](#day-66) | C++20 | 9 |  |

**[module 11: C++20: comparisons, compile time, and formatting](#module-cpp20-everyday)**: the spaceship operator, compile-time evaluation, std::format, and small additions that remove bug patterns.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 67 | [defaulted comparisons and the spaceship operator](#day-67) | C++20 | 6 |  |
| 68 | [comparison categories and custom orderings](#day-68) | C++20 | 9 |  |
| 69 | [constexpr in C++20: computing at compile time](#day-69) | C++20 | 8 |  |
| 70 | [consteval and constinit](#day-70) | C++20 | 6 | class types as template arguments |
| 71 | [`std::format`: type-safe formatting](#day-71) | C++20 | 8 | a formatter for your own types |
| 72 | [small C++20 features that remove bug patterns](#day-72) | C++20 | 6 |  |
| 73 | [review: comparisons, compile time, and formatting](#day-73) | C++20 | 8 |  |

**[module 12: threads and synchronization](#module-threads)**: owning threads, data races, mutexes, condition variables, and a bounded queue with clean shutdown.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 74 | [`std::thread`: starting, joining, and passing arguments](#day-74) | C++17 | 8 |  |
| 75 | [`std::jthread` and cooperative cancellation](#day-75) | C++20 | 7 |  |
| 76 | [data races and race conditions](#day-76) | C++17 | 8 |  |
| 77 | [mutexes, locks, and thread-safe classes](#day-77) | C++17 | 6 |  |
| 78 | [condition variables: sleeping until state changes](#day-78) | C++17 | 8 |  |
| 79 | [a bounded producer-consumer queue](#day-79) | C++17 | 6 |  |
| 80 | [review: threads and synchronization](#day-80) | C++20 | 9 |  |

**[module 13: futures, atomics, and concurrency design](#module-async)**: one-shot results, atomics and the memory model, deadlocks, and the C++20 coordination primitives.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 81 | [promises and futures: one-shot results across threads](#day-81) | C++17 | 7 |  |
| 82 | [`std::async` and its traps](#day-82) | C++17 | 7 |  |
| 83 | [`std::atomic`: indivisible operations](#day-83) | C++17 | 5 |  |
| 84 | [happens-before and memory orders](#day-84) | C++20 | 7 |  |
| 85 | [atomic waits, false sharing, and lock-freedom](#day-85) | C++20 | 5 |  |
| 86 | [deadlocks: breaking the cycle](#day-86) | C++17 | 8 |  |
| 87 | [latches, barriers, semaphores, and thread pools](#day-87) | C++20 | 7 |  |
| 88 | [review: futures, atomics, and concurrency design](#day-88) | C++20 | 10 |  |

**[module 14: design principles and patterns](#module-design)**: SOLID and coupling as predictions about change, dependency injection and seams, and patterns written with modern tools.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 89 | [SOLID as heuristics, not rules](#day-89) | C++17 | 7 |  |
| 90 | [coupling, cohesion, and physical design](#day-90) | C++17 | 7 |  |
| 91 | [dependency injection: passing collaborators in](#day-91) | C++17 | 10 |  |
| 92 | [choosing a seam: interfaces, templates, functions, and the linker](#day-92) | C++20 | 7 |  |
| 93 | [patterns in modern C++: strategy](#day-93) | C++17 | 6 |  |
| 94 | [patterns in modern C++: factories and registries](#day-94) | C++17 | 5 |  |
| 95 | [patterns in modern C++: observer and subscriptions](#day-95) | C++17 | 8 |  |
| 96 | [review: design principles and patterns](#day-96) | C++17 | 8 | the uploader, refactored and tested |

**[module 15: polymorphism choices, APIs, modules, and coroutines](#module-abstractions)**: choosing a polymorphism mechanism, type erasure, interfaces that stay correct and stable, modules, and coroutines.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 97 | [one call, many types: choosing a polymorphism mechanism](#day-97) | C++20 | 7 |  |
| 98 | [type erasure: value semantics without inheritance](#day-98) | C++20 | 9 |  |
| 99 | [designing APIs that are hard to misuse](#day-99) | C++20 | 6 |  |
| 100 | [API and ABI stability: pimpl and deprecation](#day-100) | C++20 | 8 |  |
| 101 | [C++20 modules: a practical first look](#day-101) | C++20 | 5 |  |
| 102 | [coroutines: functions that suspend](#day-102) | C++20 | 5 |  |
| 103 | [inside a coroutine: writing a generator type](#day-103) | C++20 | 5 |  |
| 104 | [review: polymorphism choices, APIs, modules, and coroutines](#day-104) | C++20 | 8 |  |

**[module 16: performance](#module-performance)**: honest measurement, the memory hierarchy, data layout, and the cost of allocation.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 105 | [measure first: honest benchmarks](#day-105) | C++17 | 8 | using a benchmark library |
| 106 | [profiling: finding where the time goes](#day-106) | C++17 | 5 |  |
| 107 | [cache locality: why the same loop can be slower](#day-107) | C++17 | 5 |  |
| 108 | [data-oriented design: arrays of structs and structs of arrays](#day-108) | C++17 | 6 |  |
| 109 | [the cost of allocation](#day-109) | C++17 | 8 |  |
| 110 | [arenas and pools with `std::pmr`](#day-110) | C++17 | 5 |  |
| 111 | [review: performance](#day-111) | C++17 | 7 |  |

**[module 17: production engineering and integration](#module-production)**: testing, observability, safe change in legacy code, and one small program that puts the course together.

| day | lesson | standard | minutes | going deeper |
| --- | --- | --- | --- | --- |
| 112 | [testing that catches real bugs](#day-112) | C++20 | 8 |  |
| 113 | [observability: logs, metrics, and traces](#day-113) | C++20 | 8 |  |
| 114 | [refactoring legacy code safely](#day-114) | C++17 | 10 |  |
| 115 | [architectural decisions and their tradeoffs](#day-115) | C++17 | 4 |  |
| 116 | [putting it together, part 1: values, messages, and the queue](#day-116) | C++20 | 7 |  |
| 117 | [putting it together, part 2: the processing stage](#day-117) | C++20 | 5 |  |
| 118 | [putting it together, part 3: wiring, shutdown, and testing](#day-118) | C++20 | 10 |  |
| 119 | [review: production engineering, and the road ahead](#day-119) | C++20 | 10 |  |

<a id="progress-checklist"></a>

## progress checklist

tick a box as you finish each day (in an editor, or on a printed copy). the website tracks progress for you.

**module 1: how programs and objects come to be**

- [ ] [day 01: from source file to running program](#day-01)
- [ ] [day 02: linkage and the one definition rule](#day-02)
- [ ] [day 03: the many faces of initialization](#day-03)
- [ ] [day 04: integer types, promotions, and conversions](#day-04)
- [ ] [day 05: objects in memory: size, alignment, and padding](#day-05)
- [ ] [day 06: storage duration and object lifetime](#day-06)
- [ ] [day 07: review: how programs and objects come to be](#day-07)

**module 2: references, values, and the language contract**

- [ ] [day 08: temporaries, lifetime extension, and dangling references](#day-08)
- [ ] [day 09: pointers and references](#day-09)
- [ ] [day 10: const as a contract](#day-10)
- [ ] [day 11: value categories without the headache](#day-11)
- [ ] [day 12: copy elision and temporary materialization](#day-12)
- [ ] [day 13: undefined behavior and the optimizer](#day-13)
- [ ] [day 14: the usual suspects: aliasing, punning, and evaluation order](#day-14)
- [ ] [day 15: review: references, values, and the language contract](#day-15)

**module 3: resources and the object lifecycle**

- [ ] [day 16: RAII: let scope do the cleanup](#day-16)
- [ ] [day 17: scope guards: cleanup without a new class](#day-17)
- [ ] [day 18: constructors that establish invariants](#day-18)
- [ ] [day 19: construction and destruction order](#day-19)
- [ ] [day 20: copying: deep, shallow, and the double free](#day-20)
- [ ] [day 21: moving: transferring resources instead of copying them](#day-21)
- [ ] [day 22: review: resources and the object lifecycle](#day-22)

**module 4: moves and ownership**

- [ ] [day 23: noexcept moves and the strong guarantee](#day-23)
- [ ] [day 24: the special member functions and when the compiler writes them](#day-24)
- [ ] [day 25: the rule of zero](#day-25)
- [ ] [day 26: exclusive ownership with `std::unique_ptr`](#day-26)
- [ ] [day 27: shared ownership with `std::shared_ptr` and `std::weak_ptr`](#day-27)
- [ ] [day 28: ownership in function signatures](#day-28)
- [ ] [day 29: review: moves and ownership](#day-29)

**module 5: inheritance and polymorphism**

- [ ] [day 30: virtual functions and dynamic dispatch](#day-30)
- [ ] [day 31: virtual destructors and object slicing](#day-31)
- [ ] [day 32: composition, interfaces, and substitutability](#day-32)
- [ ] [day 33: review: inheritance and polymorphism](#day-33)

**module 6: containers, algorithms, and lambdas**

- [ ] [day 34: containers and what they cost](#day-34)
- [ ] [day 35: maps, sets, and node handles](#day-35)
- [ ] [day 36: iterators and algorithms over raw loops](#day-36)
- [ ] [day 37: lambdas are objects: closures and captures](#day-37)
- [ ] [day 38: lambdas that outlive their scope: callbacks and `std::function`](#day-38)
- [ ] [day 39: review: containers, algorithms, and lambdas](#day-39)

**module 7: templates and generic programming**

- [ ] [day 40: function templates and argument deduction](#day-40)
- [ ] [day 41: class templates, CTAD, and specialization](#day-41)
- [ ] [day 42: forwarding references and `std::forward`](#day-42)
- [ ] [day 43: variadic templates and perfect-forwarding factories](#day-43)
- [ ] [day 44: compile-time branching with if constexpr](#day-44)
- [ ] [day 45: fold expressions](#day-45)
- [ ] [day 46: review: templates and generic programming](#day-46)

**module 8: results and failure**

- [ ] [day 47: structured bindings](#day-47)
- [ ] [day 48: if and switch initializers, and attributes that catch mistakes](#day-48)
- [ ] [day 49: exception safety guarantees](#day-49)
- [ ] [day 50: choosing an error-handling strategy](#day-50)
- [ ] [day 51: `std::optional`: modeling "maybe"](#day-51)
- [ ] [day 52: review: results and failure](#day-52)

**module 9: variants, views, and files**

- [ ] [day 53: `std::variant` and `std::visit`](#day-53)
- [ ] [day 54: closed sets and open sets: variant state machines and `std::any`](#day-54)
- [ ] [day 55: `std::string_view`: borrowing characters](#day-55)
- [ ] [day 56: parsing without allocation: views and from_chars](#day-56)
- [ ] [day 57: `std::filesystem`: portable paths and directories](#day-57)
- [ ] [day 58: a practical C++17 refactoring](#day-58)
- [ ] [day 59: review: the C++17 vocabulary, and a complete refresher](#day-59)

**module 10: C++20: concepts, ranges, and span**

- [ ] [day 60: concepts: constraining templates](#day-60)
- [ ] [day 61: writing your own concepts](#day-61)
- [ ] [day 62: range algorithms and projections](#day-62)
- [ ] [day 63: views: lazy pipelines](#day-63)
- [ ] [day 64: views and lifetimes: what a pipeline refers to](#day-64)
- [ ] [day 65: `std::span`: views over contiguous memory](#day-65)
- [ ] [day 66: review: concepts, ranges, and span](#day-66)

**module 11: C++20: comparisons, compile time, and formatting**

- [ ] [day 67: defaulted comparisons and the spaceship operator](#day-67)
- [ ] [day 68: comparison categories and custom orderings](#day-68)
- [ ] [day 69: constexpr in C++20: computing at compile time](#day-69)
- [ ] [day 70: consteval and constinit](#day-70)
- [ ] [day 71: `std::format`: type-safe formatting](#day-71)
- [ ] [day 72: small C++20 features that remove bug patterns](#day-72)
- [ ] [day 73: review: comparisons, compile time, and formatting](#day-73)

**module 12: threads and synchronization**

- [ ] [day 74: `std::thread`: starting, joining, and passing arguments](#day-74)
- [ ] [day 75: `std::jthread` and cooperative cancellation](#day-75)
- [ ] [day 76: data races and race conditions](#day-76)
- [ ] [day 77: mutexes, locks, and thread-safe classes](#day-77)
- [ ] [day 78: condition variables: sleeping until state changes](#day-78)
- [ ] [day 79: a bounded producer-consumer queue](#day-79)
- [ ] [day 80: review: threads and synchronization](#day-80)

**module 13: futures, atomics, and concurrency design**

- [ ] [day 81: promises and futures: one-shot results across threads](#day-81)
- [ ] [day 82: `std::async` and its traps](#day-82)
- [ ] [day 83: `std::atomic`: indivisible operations](#day-83)
- [ ] [day 84: happens-before and memory orders](#day-84)
- [ ] [day 85: atomic waits, false sharing, and lock-freedom](#day-85)
- [ ] [day 86: deadlocks: breaking the cycle](#day-86)
- [ ] [day 87: latches, barriers, semaphores, and thread pools](#day-87)
- [ ] [day 88: review: futures, atomics, and concurrency design](#day-88)

**module 14: design principles and patterns**

- [ ] [day 89: SOLID as heuristics, not rules](#day-89)
- [ ] [day 90: coupling, cohesion, and physical design](#day-90)
- [ ] [day 91: dependency injection: passing collaborators in](#day-91)
- [ ] [day 92: choosing a seam: interfaces, templates, functions, and the linker](#day-92)
- [ ] [day 93: patterns in modern C++: strategy](#day-93)
- [ ] [day 94: patterns in modern C++: factories and registries](#day-94)
- [ ] [day 95: patterns in modern C++: observer and subscriptions](#day-95)
- [ ] [day 96: review: design principles and patterns](#day-96)

**module 15: polymorphism choices, APIs, modules, and coroutines**

- [ ] [day 97: one call, many types: choosing a polymorphism mechanism](#day-97)
- [ ] [day 98: type erasure: value semantics without inheritance](#day-98)
- [ ] [day 99: designing APIs that are hard to misuse](#day-99)
- [ ] [day 100: API and ABI stability: pimpl and deprecation](#day-100)
- [ ] [day 101: C++20 modules: a practical first look](#day-101)
- [ ] [day 102: coroutines: functions that suspend](#day-102)
- [ ] [day 103: inside a coroutine: writing a generator type](#day-103)
- [ ] [day 104: review: polymorphism choices, APIs, modules, and coroutines](#day-104)

**module 16: performance**

- [ ] [day 105: measure first: honest benchmarks](#day-105)
- [ ] [day 106: profiling: finding where the time goes](#day-106)
- [ ] [day 107: cache locality: why the same loop can be slower](#day-107)
- [ ] [day 108: data-oriented design: arrays of structs and structs of arrays](#day-108)
- [ ] [day 109: the cost of allocation](#day-109)
- [ ] [day 110: arenas and pools with `std::pmr`](#day-110)
- [ ] [day 111: review: performance](#day-111)

**module 17: production engineering and integration**

- [ ] [day 112: testing that catches real bugs](#day-112)
- [ ] [day 113: observability: logs, metrics, and traces](#day-113)
- [ ] [day 114: refactoring legacy code safely](#day-114)
- [ ] [day 115: architectural decisions and their tradeoffs](#day-115)
- [ ] [day 116: putting it together, part 1: values, messages, and the queue](#day-116)
- [ ] [day 117: putting it together, part 2: the processing stage](#day-117)
- [ ] [day 118: putting it together, part 3: wiring, shutdown, and testing](#day-118)
- [ ] [day 119: review: production engineering, and the road ahead](#day-119)

<a id="module-foundations"></a>

## module 1: how programs and objects come to be

how source becomes a program, how objects get their first values, how big they are, and how long they live.

<a id="day-01"></a>

### day 01: from source file to running program

**module 1:** how programs and objects come to be · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** trace how source files become a program, and tell which build stage produced an error

#### the idea

you add a call to a function declared in a header, the file compiles without a murmur, and the build fails at the very last step: `undefined reference to 'calibrate(Sensor&)'`. the compiler was satisfied and the linker was not, because they answer different questions. most build errors that feel mysterious stop being mysterious once you know which stage produced them and how little each stage can see.

#### understanding the concept

a C++ build is a pipeline, and each stage sees less than you might think.

```text
widget.cpp --preprocess--> translation unit --compile--> assembly --assemble--> widget.o
                                                                                    |
       other .o files and libraries ------------------------------------------> link --> program
```

1. **preprocessing** (`g++ -E`) is text substitution. `#include` pastes a file in, macros expand, `#if` removes text. the result is a **translation unit**: one source file plus everything it transitively included. a header is not a module or an interface in any formal sense; it is text that ends up copied into every translation unit that includes it.
2. **compilation** (`g++ -S`) turns one translation unit into assembly. the compiler sees exactly one translation unit at a time. it has no idea what any other `.cpp` file contains.
3. **assembly** (`g++ -c`) produces an object file: machine code plus a symbol table listing what this file *defines* and what it *references but does not define*.
4. **linking** combines object files and libraries, matches every undefined reference to exactly one definition, and patches addresses.

you can see the symbol table with `nm -C`. `U` means "I need this from someone else", `T` means "I define this in my code section":

```sh
$ g++ -std=c++17 -c main.cpp && nm -C main.o
                 U report_a()
                 U report_b()
0000000000000000 T main
```

the linker matches **names**, not types or meaning. the mangled name of `report_a()` encodes its namespace and parameter types, which is why a missing overload shows up as an "undefined reference" rather than a type error. return types and class layouts are not checked at link time at all.

**declarations versus definitions.** a declaration introduces a name (`double scale(double);`, `extern int count;`, `struct Pose;`). a definition creates the thing (the function body, the storage for the variable, the full class). you may declare something as often as you like; definitions are restricted.

**include guards and `#pragma once`** stop a header from being pasted twice into the *same* translation unit. they do nothing across translation units, which is the source of most confusion about duplicate symbols. `#pragma once` is not in the standard but every mainstream compiler supports it; its weakness is that "the same file" is decided by the compiler, which can be fooled by copies of a header reached through different paths. classic `#ifndef` guards are decided by the macro name, which you control.

#### in code

**a missing definition.** a declaration is all the compiler needs to emit a call:

```cpp external
// calib.h
struct Sensor;
void calibrate(Sensor& s);               // declaration only

// main.cpp
#include "calib.h"
void run(Sensor& s) { calibrate(s); }    // compiles: the declaration is enough
```

```text
main.o: in function `run(Sensor&)': undefined reference to `calibrate(Sensor&)'
```

the compiler emitted a call to a symbol named `calibrate(Sensor&)` (mangled as `_Z9calibrateR6Sensor`) and moved on. the linker searched every object file and library on its command line and found no definition. it cannot tell you why, only that the name is missing.

**a duplicate symbol.** a helper defined in a header, included by two files:

```cpp external
// scale.h
#pragma once
double scale(double x) { return x * 2.0; }   // BUG: a definition with external linkage

// a.cpp: #include "scale.h"     b.cpp: #include "scale.h"
```

```text
ld: b.cpp:(.text+0x0): multiple definition of `scale(double)'; a.cpp:(.text+0x0): first defined here
collect2: error: ld returned 1 exit status
```

the guard did its job (one copy per translation unit), and the result is still two definitions in the program. the plain fix is to declare the function in the header and define it in one `.cpp`. the other fixes, `inline` and `static`, change the function's linkage, which is the subject of [day 02](#day-02).

#### in practice

in a CMake project, the link errors you meet most often point at build configuration rather than code. "undefined reference" usually means a source file or library is missing from a target: a `.cpp` left out of `add_library`, or a forgotten `target_link_libraries`. "multiple definition" usually means a header defines something it should only declare. and an undefined reference to a function you can *see* defined usually means the declaration and the definition disagree: a missing `const` on a reference parameter, a different namespace, or C code called without `extern "C"`. in each case the two mangled names differ, so to the linker they are unrelated. read the demangled name in the error character by character (`c++filt` turns `_Z9calibrateR6Sensor` back into `calibrate(Sensor&)`) and compare it with the definition; that answers most of these in seconds.

#### watch out for

**the linker checks names, not types.** declaring someone else's function by hand instead of including its header can link and still be wrong:

```cpp external
// parse.cpp
#include <cstdlib>
long parse_count(const char* text) { return std::strtol(text, nullptr, 10); }

// main.cpp: declares it by hand instead of including a header
int parse_count(const char* text);       // BUG: wrong return type, links anyway
```

on the Itanium C++ ABI used by GCC and Clang on Linux and macOS, the mangled name of an ordinary function encodes its name, namespace, and parameter types, but not its return type. both declarations produce the same symbol, so the program links, and every call reads an `int` where the function returned a `long`. the standard calls this ill-formed, no diagnostic required: the program has no defined meaning, and nothing is obliged to tell you. the defense is a habit. declare each function in exactly one header, include that header in the `.cpp` that defines it (so the compiler compares the two), and never re-declare a function by hand.

#### the takeaway

the compiler checks one translation unit against the declarations it can see; the linker only matches names. a link error is a question about which definitions are in the program, not about your code's logic.

#### optional challenge

`sensors.h` declares `namespace sensors { void reset_all(); }`. `sensors.cpp` includes it and defines `void reset_all() { /* ... */ }`. `main.cpp` calls `sensors::reset_all()`. every file compiles. what does the linker report, and why did the compiler not catch the mistake?

<details>
<summary>answer</summary>

`undefined reference to 'sensors::reset_all()'`. `sensors.cpp` defined a different function, `::reset_all()` in the global namespace. that is a perfectly legal new function, so the compiler had nothing to complain about, and the symbol `main.o` needs is defined nowhere.

writing the definition with a qualified name, `void sensors::reset_all() { ... }`, makes the compiler check that a matching declaration exists in `sensors`, which turns this whole class of mistake into a compile error in the file that made it.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-02"></a>

### day 02: linkage and the one definition rule

**module 1:** how programs and objects come to be · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** predict whether a name in two translation units is one entity or two, and keep header definitions ODR-safe  
**builds on:** [day 01](#day-01) (from source file to running program)

#### the idea

two files in the same robot driver each contain `inline int gain() { ... }`. one returns 2, the other returns 3. the build is clean, no warnings, and the program prints a different answer depending on whether you built with `-O0` or `-O2`. nothing about this is a compiler bug. it follows directly from how C++ turns source files into a program, and from a rule that the toolchain is allowed to leave completely unchecked.

#### understanding the concept

**linkage** decides whether the same name in different translation units refers to the same entity:

| linkage | meaning | how you get it |
|---|---|---|
| external | one entity shared across translation units | non-`static` functions and variables at namespace scope |
| internal | private to this translation unit | `static` at namespace scope, anything in an anonymous namespace, non-`inline` `const` variables at namespace scope |
| none | local to a scope | local variables |

**the one definition rule (ODR)** has two halves. non-inline functions and variables with external linkage must be defined exactly once in the whole program; break this and you usually get a link error. classes, inline functions, inline variables, and templates may be defined in several translation units (that is how headers work), but every definition must be identical: the same token sequence with the same meaning. break *that* half and the program is ill-formed, no diagnostic required. the compiler cannot see it (one translation unit at a time) and the linker typically keeps one copy of each inline function and throws the rest away without comparing them.

**templates live in headers** for the same reason. the compiler generates `std::vector<Detection>` code in the translation unit that uses it, so it must see the template's definition there. the alternative is explicit instantiation (`template class Filter<float>;` in one `.cpp`), which works when the set of types is closed.

#### in code

**a silent ODR violation.** two translation units, two different bodies for the same inline function:

```cpp external
// g1.cpp
#include <cstdio>
inline int gain() { return 2; }
void report_a() { std::printf("a: %d\n", gain()); }

// g2.cpp
#include <cstdio>
inline int gain() { return 3; }   // BUG: ODR violation, no diagnostic required
void report_b() { std::printf("b: %d\n", gain()); }

// main.cpp
void report_a();
void report_b();
int main() { report_a(); report_b(); }
```

with GCC 12 on our test machine, `g++ g1.cpp g2.cpp main.cpp` at `-O0` printed `a: 2` and `b: 2`; swapping the file order printed `3` and `3`. at `-O2` both orders printed `a: 2` and `b: 3`, because each call was inlined before the linker ever chose a copy. none of these outputs is "the right one": the program is ill-formed and the standard does not say what it does. in real code this happens when two files define a helper with a common name, or when a header's content depends on a macro (`#ifdef DEBUG_POSE`) that is set differently in different targets.

**one object, defined in a header (C++17).** before C++17, a global shared by several translation units needed an `extern` declaration in the header and a definition in exactly one `.cpp`. inline variables remove that ceremony:

```cpp complete
// config.h
#pragma once
#include <string_view>

const int kLimit = 10;                       // internal linkage: a separate copy per TU
inline constexpr double kMaxRangeM = 250.0;  // C++17: one entity program-wide
inline constexpr std::string_view kFrameId = "base_link";
inline int g_instances = 0;                  // one mutable object, no .cpp needed

namespace {                                  // in a .cpp, never in a header
int local_helper() { return 42; }           // internal linkage
}
```

`kLimit` links fine because namespace-scope `const` implies internal linkage, but every translation unit gets its own object, so `&kLimit` differs between files (we checked: comparing addresses across two files gave `false`). for a value that is usually harmless. for something whose identity matters, or a non-trivial type like `const std::string`, each copy also has its own constructor running at startup. `inline constexpr` gives you one entity with no startup cost, and is the idiomatic way to define header constants in C++17.

#### in practice

the ODR bites hardest at the boundaries of a large build. a robotics stack pulls in a header-only math library through two dependencies pinned to different versions, so `struct Pose` has two fields in one library and three in the other. or a perception library is built with a compile definition that adds a debug member to a struct, while the planner that uses it is not. every translation unit compiles cleanly. at run time one side writes 24 bytes where the other allocated 16, and the crash happens far from the cause.

your defenses are mostly process: one version of each dependency per binary, compile definitions that change layout applied consistently (or not used in public headers at all), and a link-time check. GCC with link-time optimization does compare type definitions across translation units:

```text
$ g++ -O2 -flto s1.cpp s2.cpp
s1.cpp:1:8: warning: type 'struct Pose' violates the C++ One Definition Rule [-Wodr]
s2.cpp:1:28: note: the first difference of corresponding definitions is field 'theta'
```

it caught the mismatched struct in our test; it did not flag the two `gain()` bodies above. treat it as a net, not a guarantee. keeping headers small and their contents unconditional is the design-level fix: every line in a header is a promise made, identically, to every file that includes it.

#### watch out for

`static` in a header "fixes" a duplicate-symbol error by giving every translation unit its own private copy. for a function that is merely code bloat. for a variable it is a logic bug waiting to happen:

```cpp complete
// counters.h
static int s_dropped_frames = 0;   // BUG: one counter per .cpp file, not one per program
```

every file that increments `s_dropped_frames` updates its own counter, and the telemetry thread that reads it sees only the copy in its own translation unit. in our test, a `static int` incremented twice in one file and once in another read as 2 and 1, while an `inline int` declared next to it read 3 everywhere. if you want one object, write `inline`. if you want one per file, put it in an anonymous namespace in the `.cpp`, not in a header.

#### the takeaway

the compiler sees one translation unit, the linker sees names, and the ODR is a promise that nobody is obliged to check; keep header contents identical everywhere, and use `inline` (C++17 variables included) when you mean "one entity, defined in a header".

#### optional challenge

this header is included by `lidar.cpp` and `radar.cpp`, which are linked into one program. which lines cause a link error, and which compile and link but might not do what the author intended?

```cpp complete
// limits.h
#pragma once
const int kMaxTargets = 64;
int g_target_count;
inline int g_frame_count = 0;
static double s_last_stamp = 0.0;
```

<details>
<summary>answer</summary>

`int g_target_count;` is the link error. in C++ it is a definition with external linkage (C's "tentative definitions" do not exist in C++), so two translation units means two definitions: `multiple definition of 'g_target_count'`. fix it with `inline int g_target_count = 0;` or with `extern` in the header and a definition in one `.cpp`.

`kMaxTargets` links fine because `const` gives it internal linkage; each file has its own copy, which is harmless for a value. `g_frame_count` is one shared object (C++17 inline variable). `s_last_stamp` links fine but is the trap: `lidar.cpp` and `radar.cpp` each get their own `s_last_stamp`, so a write in one is invisible in the other. `#pragma once` is irrelevant to all of this; it only prevents double inclusion within a single translation unit.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-03"></a>

### day 03: the many faces of initialization

**module 1:** how programs and objects come to be · **reading time:** about 10 minutes · **standard:** C++17  
**objective:** choose the initialization syntax that says what you mean, and know which forms leave a value indeterminate  
**builds on:** [day 01](#day-01) (from source file to running program)

#### the idea

a colleague modernizes a radar module and changes `std::vector<float> gains(8, 0.5f);` to `std::vector<float> gains{8, 0.5f};` because "braces are the modern way". the code compiles. the vector now has two elements, 8.0 and 0.5, and the beamformer reads past the gains it expected. C++ has roughly half a dozen ways to initialize an object, they differ in real ways, and the one advertised as "uniform" is not uniform at all.

#### understanding the concept

the forms, from least to most initialized:

| syntax | name | what happens |
|---|---|---|
| `T x;` | default-initialization | class types: default constructor runs. scalars and aggregates of scalars with automatic storage: **indeterminate** value |
| `T x{};` or `T()` | value-initialization | scalars: zero. class with a user-provided default constructor: that constructor runs. otherwise: zeroed, then any non-trivial default construction |
| `T x(a);` | direct-initialization | all constructors considered, including `explicit` ones |
| `T x = a;` | copy-initialization | `explicit` constructors are not considered |
| `T x{a};` / `T x = {a};` | direct/copy-list-initialization | as above, but narrowing is rejected and `std::initializer_list` constructors win |
| `S s{1, 2.0};` | aggregate initialization | members initialized in declaration order; omitted members from their default member initializer, otherwise as if from `{}` |

objects with **static or thread storage duration** are different: they are zero-initialized before anything else happens, so a global `int counter;` is reliably 0. only automatic (and dynamically allocated) scalars start indeterminate, and reading an indeterminate value is undefined behavior ([day 13](#day-13) will show why the optimizer makes that worse than "you get garbage").

**list-initialization has two special rules.** first, it rejects *narrowing* conversions: floating to integer, `double` to `float` (unless the source is a constant that fits), and integer to a type that cannot represent the value. second, if the class has a constructor taking `std::initializer_list`, a non-empty braced list strongly prefers it over every other constructor, even when another one is a better match. empty braces are the exception: `{}` means the default constructor.

**`auto` with braces** changed in C++17 (compilers also apply the fix in C++14 mode): `auto a{1};` is `int`, `auto b = {1};` is `std::initializer_list<int>`, and `auto c{1, 2};` is ill-formed. the `=` changes the meaning, which is reason enough to write `auto x = 1;` and keep braces for objects.

#### in code

**predict the output.** cover the comments and work out each line.

```cpp complete
#include <iostream>
#include <string>
#include <vector>

struct Pose { double x = 0.0, y = 0.0, theta = 0.0; };

int main() {
    std::vector<int> a(3, 1);   // constructor (count, value)
    std::vector<int> b{3, 1};   // initializer_list constructor wins
    std::vector<int> c{};       // empty braces: default constructor
    std::cout << a.size() << ' ' << b.size() << ' ' << c.size() << '\n';
    // prints: 3 2 0

    std::string s(3, 'a');      // "aaa"
    std::string t{3, 'a'};      // two chars: '\x03' and 'a'
    std::cout << s.size() << ' ' << t.size() << '\n';   // prints: 3 2

    Pose p{};                   // all members from their initializers
    Pose q{1.0, 2.0};           // aggregate init: theta keeps 0.0
    std::cout << p.x << ' ' << q.theta << '\n';         // prints: 0 0
}
```

the rule for library types: if the class has an `initializer_list` constructor (containers, `std::string`), braces mean "these are the elements". use parentheses when you mean "call the sizing constructor".

**braces as a narrowing guard, and the most vexing parse.**

```cpp fails
#include <cstdint>

struct RadarConfig { float max_range_m; std::uint16_t num_bins; };

int truncate(double measured) {
    int a = measured;               // compiles: silently truncates toward zero
    int b{measured};                // ill-formed: narrowing double -> int
    RadarConfig cfg{250.0, 70000};  // ill-formed: 70000 does not fit uint16_t
    return a + b + cfg.num_bins;
}

struct Clock {};
struct Timer { explicit Timer(Clock) {} void start() {} };

void vexing() {
    Timer t(Clock());   // BUG: declares a function t taking a function, returning Timer
    t.start();          // error: t is not an object
    Timer u{Clock{}};   // an object, as intended
}
```

the standard makes narrowing in list-initialization ill-formed. GCC 12 reports constants that do not fit (`70000`, `char c{300}`) as errors, but reports the non-constant `int b{measured}` only as a `-Wnarrowing` warning; Clang rejects both. add `-Werror=narrowing` (or `-pedantic-errors`) to get the standard's behavior on GCC. the vexing parse comes from the grammar rule "anything that can be a declaration is a declaration"; GCC 11 and later warn with `-Wvexing-parse`, and braces remove the ambiguity entirely.

#### in practice

configuration structs are where initialization style pays off. a telemetry packet header or a sensor configuration as an aggregate with default member initializers gives you three properties at once: every field has a defined value even when the caller forgets one, brace initialization rejects narrowing such as a `double` squeezed into a `std::uint16_t` field, and the type stays trivially copyable for serialization:

```cpp
struct ImuConfig {
    std::uint16_t rate_hz = 200;
    float accel_range_g = 8.0f;
    bool  enable_fifo = true;
};

ImuConfig cfg{400};   // rate_hz = 400, the rest keep their defaults
```

the weakness is that positional aggregate initialization ties every call site to member order; inserting a field in the middle silently shifts meanings when the types are compatible. C++20 designated initializers ([day 72](#day-72)) fix that. choosing an aggregate over a class with a constructor is a design decision: an aggregate says "this is plain data with no invariant", which is exactly right for configuration and wrong for anything that must validate its fields.

#### watch out for

value-initialization only zeroes members when the compiler supplies the constructor. a user-provided default constructor that forgets a member defeats `{}`:

```cpp complete
struct Raw    { double x, y; };                 // no constructor
struct Sensor { Sensor() {} int id; };          // user-provided, does not set id

Raw r{};       // r.x and r.y are 0.0
Sensor s{};    // s.id is indeterminate: the constructor runs and that is all
Raw r2;        // r2.x is indeterminate (automatic storage)
```

GCC flagged a read of `s.id` with `-Wuninitialized` at `-O2`, but such warnings depend on optimization level and inlining, so do not rely on them. the robust habit is a default member initializer on every scalar member (`int id = 0;`); then every form of initialization, including plain `Sensor s;`, produces a defined value.

#### the takeaway

use braces for objects you build from values (they reject narrowing), parentheses when you call a sizing constructor on a container, and a default member initializer on every scalar member.

#### optional challenge

what does each object hold? assume the code is inside a function, except where marked.

```cpp complete
struct Gains { float kp = 1.0f; float ki; float kd = 0.0f; };

Gains a;          // (1)
Gains b{};        // (2)
Gains c{2.0f};    // (3)
static Gains d;   // (4)
```

<details>
<summary>answer</summary>

1. `kp` is 1 and `kd` is 0 from their default member initializers, but `ki` is indeterminate: default-initialization of an automatic aggregate leaves scalars without an initializer alone, and reading `a.ki` is undefined behavior.
2. aggregate initialization from an empty list: members with a default member initializer use it, and the rest are initialized as if from `{}`, so `ki` is 0. result: 1, 0, 0.
3. the first member comes from the list (`kp` is 2), the rest as in (2): 2, 0, 0.
4. static storage is zero-initialized before anything else, then default-initialized: 1, 0, 0. the same declaration gives a defined `ki` here and an indeterminate one in (1), which is exactly why "add `= 0.0f` to `ki`" is the robust fix.

</details>

#### going deeper (optional)

##### what exactly counts as an aggregate

an aggregate (C++17) is an array or a class with no user-provided, `explicit`, or inherited constructors, no private or protected non-static data members, no virtual functions, and no virtual, private, or protected bases. C++20 tightens "user-provided" to "user-declared", so a struct with `S() = default;` stops being an aggregate.

[back to the curriculum map](#curriculum)

---

<a id="day-04"></a>

### day 04: integer types, promotions, and conversions

**module 1:** how programs and objects come to be · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** predict the type and value of mixed integer arithmetic, and choose integer types whose width and signedness match the contract  
**builds on:** [day 03](#day-03) (the many faces of initialization)

#### the idea

`readings.size() - 1` is not -1 when `readings` is empty. `std::uint8_t id = 65;` prints as `A`. multiplying two `std::uint16_t` values can be undefined behavior even though every type in sight is unsigned. integer arithmetic in C++ happens in types you never wrote, converts signed values to unsigned without asking, and the width of `long` depends on the operating system. none of it is hard, but none of it is what intuition suggests.

#### understanding the concept

**types and sizes.** `sizeof(char)` is 1 by definition; everything else is implementation-defined within minimums (`int` at least 16 bits, `long` at least 32, `long long` at least 64). `long` is 64 bits on x86-64 Linux and 32 bits on Windows, including MinGW; our test machine printed `sizeof(long) == 4`. when the width matters (wire formats, registers, file headers), use `<cstdint>`: `std::int32_t`, `std::uint64_t`. the exact-width types are technically optional but exist on every mainstream platform; `std::int_least32_t` and `std::int_fast32_t` always exist.

**promotions and conversions.** arithmetic never happens in types narrower than `int`: `char`, `short`, `std::uint8_t`, and `std::uint16_t` are promoted to `int` first. when a signed and an unsigned operand of the same rank meet, the *signed one is converted to unsigned*. that rule produces most of the surprises.

the full set of "usual arithmetic conversions" is longer, but three outcomes cover nearly every real case:

- both operands are promoted to at least `int`, then the narrower one is converted to the wider type;
- if one operand is unsigned and the other is a signed type of the same or lower rank, the signed one becomes unsigned (`-1 < 1u` is false);
- if the signed type can represent every value of the unsigned one (for example `long long` and `unsigned int` on a typical 64-bit platform), the unsigned one becomes signed instead.

what happens when a result does not fit depends on the signedness. unsigned arithmetic wraps modulo 2^N by definition. signed overflow is undefined behavior (the optimizer assumes it never happens, which [day 13](#day-13) explores). converting an out-of-range value *to* a signed type was implementation-defined until C++20, which made it modular.

#### in code

**integer promotion and signed/unsigned comparison.**

```cpp complete
#include <cstdint>
#include <iostream>
#include <vector>

int main() {
    std::uint8_t a = 200, b = 100;
    auto sum = a + b;                 // both promoted to int; sum is int
    std::cout << sum << '\n';         // prints: 300

    int i = -1;
    unsigned u = 1;
    std::cout << (i < u) << '\n';     // prints: 0, because -1 becomes UINT_MAX

    std::vector<int> readings;        // empty
    std::cout << readings.size() - 1 << '\n';
    // prints: 18446744073709551615 with a 64-bit size_t (unsigned wraparound, well defined)

    std::uint8_t id = 65;
    std::cout << id << '\n';          // prints: A (uint8_t is usually unsigned char)
}
```

`-Wall` includes `-Wsign-compare` in C++ and flags the `i < u` line. unsigned arithmetic wraps modulo 2^N by definition, so `size() - 1` is not undefined; it is simply a huge number, and a loop `for (std::size_t k = 0; k <= v.size() - 1; ++k)` on an empty vector runs off the end. C++20 adds `std::cmp_less` and friends in `<utility>` for comparisons that are correct across signedness.

#### in practice

wire formats are where the width and signedness of every field is part of the contract. decoding a 16-bit signed range-rate field from a radar packet, the arithmetic happens in `int`, so the result has to be converted back explicitly:

```cpp complete
#include <cstdint>

std::int16_t decode_i16(const std::uint8_t* p) {
    // p[0] << 8 is computed in int; the cast says "these 16 bits are a signed value"
    return static_cast<std::int16_t>((p[0] << 8) | p[1]);
}
```

before C++20 that final conversion of a value above 32767 was implementation-defined (every mainstream compiler wraps it); since C++20 it is defined to wrap. the habits that keep this code honest: fixed-width types in every struct that mirrors bytes on a wire or in a register, an explicit `static_cast` wherever a value changes width or signedness, and `-Wconversion -Wsign-conversion` turned on for the modules that do this kind of work (they are noisy in general code, valuable here).

#### watch out for

**subtracting unsigned values.** sizes and indices are unsigned, so their difference is too:

```cpp complete
#include <cstddef>

bool lagging(std::size_t expected, std::size_t received) {
    return expected - received > 3;   // BUG: 10 - 12 wraps to a huge number: true
}
```

the subtraction is well defined and wrong. compare without subtracting (`expected > received + 3`), or convert to a signed type first (`std::ptrdiff_t`, or C++20's `std::ssize(container)`) when a negative difference is meaningful. the same trap hides in `for (std::size_t k = 0; k <= v.size() - 1; ++k)`.

#### the takeaway

arithmetic happens in `int` or wider, mixed signedness converts to unsigned, and only unsigned wraparound is defined; use fixed-width types where the width is part of a contract, and never subtract sizes without asking what happens when the result is negative.

#### optional challenge

assuming a typical platform with a 32-bit `int`, what does this function return for `a = b = 65535`, and is the result even defined?

```cpp complete
#include <cstdint>
std::uint32_t area(std::uint16_t a, std::uint16_t b) { return a * b; }
```

<details>
<summary>answer</summary>

both operands are promoted to `int` (signed, 32 bits) before the multiplication, because `int` can represent every `std::uint16_t` value. 65535 * 65535 = 4,294,836,225, which exceeds `INT_MAX` (2,147,483,647). signed overflow is undefined behavior, so the function has no defined result for those inputs, even though every type in the signature is unsigned. the fix is to convert before multiplying: `return std::uint32_t{a} * b;`, which makes the arithmetic happen in `std::uint32_t` (the other operand is converted to unsigned) where wraparound is defined and, here, there is no overflow at all.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-05"></a>

### day 05: objects in memory: size, alignment, and padding

**module 1:** how programs and objects come to be · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** predict an object's size and alignment, explain where padding comes from, and know which layout facts are guaranteed  
**builds on:** [day 04](#day-04) (integer types, promotions, and conversions)

#### the idea

`struct Detection { bool valid; double range; bool tracked; double doppler; };` holds 18 bytes of data and occupies 32 bytes on a typical 64-bit platform. reorder the members and it occupies 24. send it over a socket with `write(fd, &d, sizeof d)` and 14 of the bytes you ship are whatever happened to be in memory. an object is a region of storage with a type, and the type decides more about that storage than its list of members suggests.

#### understanding the concept

every object has a **size** (`sizeof`) and an **alignment** (`alignof`): its address must be a multiple of its alignment. the values are implementation-defined. on mainstream 64-bit platforms `char` has alignment 1, `int` 4, and `double` and pointers 8, and `alignof(T)` never exceeds `sizeof(T)` for scalar types.

a class lays out its non-static data members in declaration order (strictly, members with the same access control; mixing `public:` and `private:` sections loosens even that). to keep each member aligned, the compiler inserts **padding** between members where needed. it also adds **tail padding** at the end, so that `sizeof` is a multiple of the class's alignment, which is the largest alignment among its members. tail padding is what keeps the second element of an array correctly aligned.

```text
Loose { bool valid; double range; bool tracked; double doppler; }
|v|.......|range...|t|.......|doppler.|     32 bytes, 14 of them padding

Tight { double range; double doppler; bool valid; bool tracked; }
|range...|doppler.|v|t|......|              24 bytes, 6 of them tail padding
```

two more facts complete the picture. the bytes of padding belong to the object's *representation* but not its *value*: their contents are unspecified, and copying the object member by member need not preserve them. and some types can be treated as plain bytes: a **trivially copyable** type (no user-provided copy, move, or destructor) may be copied with `std::memcpy`, which is why [day 14](#day-14) could `memcpy` a frame header out of a buffer.

#### in code

**measuring layout.**

```cpp complete
#include <cstddef>
#include <cstdio>

struct Loose { bool valid; double range; bool tracked; double doppler; };
struct Tight { double range; double doppler; bool valid; bool tracked; };

int main() {
    std::printf("%zu %zu\n", sizeof(Loose), alignof(Loose));  // prints: 32 8 (typical 64-bit)
    std::printf("%zu %zu\n", sizeof(Tight), alignof(Tight));  // prints: 24 8
    std::printf("%zu\n", offsetof(Loose, range));             // prints: 8
}
```

**pinning layout assumptions.** when a struct mirrors a wire format or a hardware register block, its layout is part of a contract, and the contract rests on implementation-defined facts. make the compiler check them:

```cpp complete
#include <cstdint>
#include <type_traits>

struct WireHeader {
    std::uint32_t seq;
    std::uint16_t magic;
    std::uint16_t count;
};

static_assert(sizeof(WireHeader) == 8, "no padding expected");
static_assert(alignof(WireHeader) == 4);
static_assert(std::is_trivially_copyable_v<WireHeader>, "must stay memcpy-able");
```

on the day someone adds a `bool` in the middle, or the code is built for a platform with different alignment rules, the build fails in this file instead of corrupting packets at run time.

#### in practice

layout matters most for objects you store by the million. a radar pipeline that keeps one `Loose` detection per reflection in a `std::vector` moves 32 MB through the memory system for every million detections; the same data as `Tight` is 24 MB, a quarter fewer cache lines per pass over the data. a common rule of thumb for structs stored in bulk is to order members from the largest alignment to the smallest. for a one-off configuration object, grouping members by meaning is worth more than a few bytes. [day 107](#day-107) comes back to how layout affects speed, and how to measure it rather than guess.

compilers offer `#pragma pack` to remove padding. it produces misaligned members: reading them through the struct works on the compilers that support it, but taking a pointer or reference to a packed member and using it elsewhere is not portable and faults on some architectures. for wire formats, explicit serialization (copying each field to and from a byte buffer) is the robust alternative.

#### watch out for

**padding bytes are not zero, so do not compare or hash raw bytes.**

```cpp
#include <cstring>

bool same(const Loose& a, const Loose& b) {
    return std::memcmp(&a, &b, sizeof a) == 0;   // BUG: compares padding too
}
```

two `Loose` objects with identical members can differ in their padding, so `same` may return `false` for equal values. the same bug appears when hashing an object's bytes or using them as a cache key, and sending raw structs over the network can leak stale memory contents through the padding. compare members, not bytes; C++20 can generate the member-wise comparison for you ([day 67](#day-67)).

#### the takeaway

size and alignment are properties of the type, padding is the price of alignment, and almost every layout fact beyond "declared order, aligned members" is implementation-defined, so `static_assert` the ones your code relies on.

#### optional challenge

on a platform where `int` has size and alignment 4, what are `sizeof` and `alignof` for these two types, and why is `sizeof(S)` not 6?

```cpp complete
struct S { char c; int i; char d; };
struct T { int i; char c; char d; };
```

<details>
<summary>answer</summary>

`S`: `c` at offset 0, three bytes of padding, `i` at 4, `d` at 8, then three bytes of tail padding: `sizeof(S) == 12`, `alignof(S) == 4`. `T`: `i` at 0, `c` at 4, `d` at 5, two bytes of tail padding: `sizeof(T) == 8`, `alignof(T) == 4`.

`sizeof(S)` cannot be 6 because `i` must sit at a multiple of 4, and the tail padding is needed for arrays: in `S arr[2]`, the second element starts at `arr + sizeof(S)`, and its `i` is only aligned if `sizeof(S)` is a multiple of 4.

</details>

#### going deeper (optional)

##### empty classes and the empty base optimization

an object of an empty class still has a size of at least 1, because distinct objects of the same type must have distinct addresses. as a base class, though, an empty class may occupy no space at all (the *empty base optimization*). that is how `std::unique_ptr` with a stateless deleter stays the size of a raw pointer: implementations store the deleter so that it takes no room. C++20 adds `[[no_unique_address]]`, which grants the same freedom to a data member, so a class can hold an empty policy or allocator member without paying a byte plus padding for it.

##### standard-layout types and `offsetof`

`offsetof` is only guaranteed to work for *standard-layout* classes: roughly, all non-static data members have the same access control, there are no virtual functions or virtual bases, and base classes do not also declare data members. for other classes it is conditionally-supported since C++17, which means a compiler may reject it. GCC accepts it with a warning (`-Winvalid-offsetof`). the type trait `std::is_standard_layout_v<T>` tells you which side of the line a type is on.

[back to the curriculum map](#curriculum)

---

<a id="day-06"></a>

### day 06: storage duration and object lifetime

**module 1:** how programs and objects come to be · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** separate a name's scope from an object's lifetime, and predict construction and destruction order for every storage duration  
**builds on:** [day 03](#day-03) (the many faces of initialization)

#### the idea

"the variable is still in scope, so the object is still alive." that sentence is behind a surprising share of dangling-reference bugs. scope is a compile-time property of a *name*: the region of source text where the name can be used. lifetime is a run-time property of an *object*: the interval during which it exists and may be accessed. they often coincide, which is why we conflate them. a reference can be perfectly in scope while the object it names is long gone, and a function-local `static` is out of scope almost everywhere while its object lives until the program exits.

#### understanding the concept

every object has a **storage duration**, which bounds how long its storage exists:

| storage duration | objects | storage lasts |
|---|---|---|
| automatic | block-scope locals, parameters | until the enclosing block exits |
| static | namespace-scope variables, `static` locals, `static` data members | the whole program |
| thread | `thread_local` variables | the lifetime of each thread (one object per thread) |
| dynamic | objects from `new` (and allocator-based containers) | until you `delete` them |

temporaries are a fifth case: a temporary object is destroyed at the end of the **full-expression** that created it, which in practice usually means at the `;`.

an object's **lifetime** begins when its storage is obtained and its initialization is complete, and ends when its destructor call starts (or, for types with trivial destructors, when its storage is released or reused). touching an object outside its lifetime through a pointer or reference is undefined behavior, even if the bytes are still there and still look right.

**static initialization.** objects with static storage duration are first zero-initialized or constant-initialized (no code runs; the values are in the binary). anything else is *dynamic* initialization, which runs before `main` (strictly, before first use of something in that translation unit, but mainstream implementations do it at startup). within one translation unit, dynamic initialization follows definition order. across translation units, the order is unspecified. that gap is the **static initialization order fiasco**: if a global's initializer reads a global from another file, it may read an object whose lifetime has not begun.

a **function-local static** fixes this: it is initialized the first time control passes through its declaration, and since C++11 that initialization is thread-safe (concurrent callers wait for it to finish). destruction runs in reverse order of construction completion, for locals and statics alike.

#### in code

**predict the output.** construction and destruction across all the durations above:

```cpp complete
#include <cstdio>

struct Tracer {
    const char* name;
    explicit Tracer(const char* n) : name(n) { std::printf("+%s ", name); }
    ~Tracer() { std::printf("-%s ", name); }
};

Tracer global("global");                        // static storage duration
Tracer make(const char* n) { return Tracer(n); }
void tick() { static Tracer once("static"); }   // block scope, static storage

int main() {
    std::printf("main ");
    Tracer a("a");
    tick();
    tick();                                      // already constructed: nothing printed
    { Tracer b("b"); }
    std::printf("use:%s ", make("temp").name);   // temporary dies at the ';'
    const Tracer& ext = make("ext");             // lifetime extended to ext's scope
    Tracer c("c");
    std::printf("return ");
}
// prints: +global main +a +static +b -b +temp use:temp -temp +ext +c return -c -ext -a -static -global
```

note that `-static` comes after `-a` but before `-global`: statics die after `main` returns, in reverse order of construction, and `once` finished constructing after `global`.

`ext` survives its `;` because a temporary bound directly to a local `const&` lives as long as the reference; [day 08](#day-08) covers exactly when that rule applies and when it does not.

**the static initialization order fiasco and its fix.**

```cpp external
// prefix.cpp
std::string g_prefix = "radar/";

// topic.cpp
extern std::string g_prefix;
std::string g_topic = g_prefix + "tracks";   // BUG: g_prefix may not be constructed yet

// fixed: prefix.cpp
const std::string& prefix() {
    static const std::string p = "radar/";   // constructed on first call, thread-safe
    return p;
}
// fixed: topic.cpp
std::string g_topic = prefix() + "tracks";
```

on our MinGW build, one link order printed `[radar/tracks]` and the other printed `[tracks]`: `g_prefix` was read while its storage was still only zero-initialized. that output is luck, not a guarantee; reading an object before its lifetime begins is undefined behavior and could as easily crash. the fixed version printed `[radar/tracks]` in both orders. if the value is a compile-time constant, an even better fix is to make it one: `inline constexpr std::string_view kPrefix = "radar/";` is constant-initialized and has no order at all (C++20 adds `constinit` to require constant initialization of a non-`const` variable).

#### in practice

plugin registries in robotics and tooling frameworks are where the fiasco lives in the wild. each driver file contains a static registrar, something like `static const bool registered = SensorRegistry::add("velodyne", &make_velodyne);`, so that linking a driver is enough to make it available. those registrars run during dynamic initialization of their own translation units, in unspecified order. if the registry is a global `std::map`, a registrar can insert into a map whose constructor has not run yet. the standard pattern is a function-local static: `static SensorRegistry& instance() { static SensorRegistry r; return r; }`.

#### watch out for

**thread-safe initialization is not thread-safe use.** the function-local static fix makes construction safe when several threads call `instance()` at once. it says nothing about what happens afterwards:

```cpp complete
#include <vector>

std::vector<int>& scratch() {
    static std::vector<int> buffer;   // constructed once, safely
    return buffer;                    // BUG if two threads use it: a data race
}
```

a static local is one object shared by every call on every thread, which is a global with better manners about initialization. when it is mutable, it still needs a mutex or a `thread_local` instead of `static`.

#### the takeaway

ask "who owns this object and when does it die?" rather than "is this name in scope?"; objects die in reverse order of construction, and anything shared between translation units at startup belongs behind a function-local static or a `constexpr` constant.

#### optional challenge

`log()` and `registry()` each return a function-local static. the registry's destructor writes a final message through `log()`. is shutdown safe if the program first calls `registry()` and only later calls `log()`? what if the registry's constructor calls `log()`?

<details>
<summary>answer</summary>

statics are destroyed in reverse order of the *completion* of their construction. in the first scenario the registry finishes constructing first and the logger second, so the logger is destroyed first, and the registry's destructor then uses a dead logger: undefined behavior that typically shows up as a crash or lost output at exit.

if the registry's constructor calls `log()`, the logger finishes constructing *before* the registry does (it completes inside the registry's constructor), so it is destroyed *after* the registry. touching a dependency in your constructor is the standard trick for making the shutdown order follow the dependency order.

</details>

#### going deeper (optional)

##### shutdown order and leaky singletons

the mirror image happens at shutdown. a static object whose destructor logs through a global logger may run after the logger has been destroyed. a common, deliberate escape hatch is a "leaky" singleton, `static Logger* l = new Logger;`, which is never destroyed; the operating system reclaims the memory, at the price of no destructor running (so flush explicitly). global mutable state is a coupling problem before it is an ordering problem: every object with static storage that reads another is a hidden dependency, and fewer globals means fewer of these puzzles.

[back to the curriculum map](#curriculum)

---

<a id="day-07"></a>

### day 07: review: how programs and objects come to be

**module 1:** how programs and objects come to be · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** consolidate the build model, linkage, initialization, integer arithmetic, object layout, and storage duration  
**covers:** [day 01](#day-01) to [day 06](#day-06)

#### recap

| lesson | key idea |
|---|---|
| [day 01](#day-01) | the compiler sees one translation unit and checks it against the declarations it can see; the linker only matches names. |
| [day 02](#day-02) | external linkage means one entity program-wide. classes, inline functions, and templates may be defined in many translation units only if every definition is identical, and nobody has to check. C++17 `inline` variables give one object defined in a header. |
| [day 03](#day-03) | braces reject narrowing but prefer `std::initializer_list` constructors; automatic scalars start indeterminate, statics start zeroed. |
| [day 04](#day-04) | arithmetic happens in at least `int`, signed meets unsigned as unsigned, and only unsigned wraparound is defined. |
| [day 05](#day-05) | size and alignment belong to the type; padding keeps members aligned and its bytes have no defined value. |
| [day 06](#day-06) | scope belongs to names, lifetime to objects; cross-file static initialization order is unspecified, and a function-local static fixes it. |

#### review questions

1. a header included by `planner.cpp` and `controller.cpp` contains `int g_cycle_count;`, `const double kDt = 0.01;`, and `inline double clamp01(double x) { ... }`. which of these links, which does not, and what single C++17 change gives one shared, mutable `g_cycle_count` without touching any `.cpp` file?
2. predict the sizes: `std::vector<int> a{10, 0};`, `std::vector<int> b(10, 0);`, `std::vector<int> c{};`. why does the guideline "use braces everywhere" need an exception for containers?
3. `for (int i = 0; i < v.size() - 1; ++i)` draws a `-Wsign-compare` warning and misbehaves when `v` is empty. explain both, using the conversion rules.
4. two objects of the same struct have equal members, yet `std::memcmp` says they differ. how is that possible, and what should the code compare instead?
5. looking ahead: a `LogFile` class opens a `FILE*` in its constructor. where should `fclose` go so that every way out of a scope, including an exception, closes the file? what goes wrong if a `LogFile` is copied with the compiler-generated copy constructor?

#### mini exercise

this header is included by several `.cpp` files of one program. find four problems (two stop the build, two are silent), then fix them.

```cpp complete
// telemetry.h
#pragma once
#include <cstdint>
#include <vector>

struct Sample { bool valid; double value; std::uint8_t channel; };   // stored by the million
int g_samples_dropped;
std::vector<int> g_channel_map{16, -1};                              // intended: 16 entries of -1
inline std::uint32_t scale(std::uint16_t raw, std::uint16_t gain) { return raw * gain; }
```

#### answers

<details>
<summary>answer 1: linkage and the ODR</summary>

`int g_cycle_count;` fails: it is a definition with external linkage in two translation units (`multiple definition of 'g_cycle_count'`). `const double kDt` links, because a namespace-scope `const` without `inline` or `extern` has internal linkage: each file gets its own copy, harmless for a value. `inline double clamp01` links, because inline functions may be defined in every translation unit as long as the definitions are identical. `inline int g_cycle_count = 0;` makes it a C++17 inline variable: one object for the whole program, defined in the header.

</details>

<details>
<summary>answer 2: braces and containers</summary>

`a` has 2 elements (10 and 0), `b` has 10 zeros, `c` is empty. a non-empty braced list strongly prefers an `std::initializer_list` constructor; empty braces mean value-initialization. braces are a good default because they reject narrowing and avoid the most vexing parse, but for any class with an `initializer_list` constructor (all standard containers, `std::string`) braces mean "these are the elements", so use parentheses for sizing and fill constructors.

</details>

<details>
<summary>answer 3: signed meets unsigned</summary>

`v.size()` is `std::size_t`, so in `i < v.size() - 1` the `int` is converted to unsigned for the comparison; a negative `i` would compare as a huge value, which is what the warning is about. the real bug is `v.size() - 1`: for an empty vector it wraps to the largest `std::size_t` (well defined, and wrong), so the loop runs far past the end. write `i + 1 < v.size()` with an unsigned `i`, or use `std::ssize(v)` (C++20) and signed arithmetic throughout.

</details>

<details>
<summary>answer 4: padding</summary>

`memcmp` compares the whole object representation, padding included, and padding bytes have unspecified contents: two objects with identical members can carry different leftovers between them. compare member by member (write `operator==`, or default it in C++20). the same reasoning rules out hashing or serializing an object's raw bytes.

</details>

<details>
<summary>answer 5: looking ahead</summary>

`fclose` belongs in the destructor. automatic objects are destroyed when their scope exits by any route: normal flow, `return`, `break`, or stack unwinding from an exception. tying the release to the object's lifetime is RAII ([day 16](#day-16)). the generated copy constructor copies the `FILE*`, so two objects hold one handle and both destructors close it: a double close, which is undefined behavior. the class must forbid copying or define what a copy means ([day 20](#day-20)), and it can support *moving* ownership instead ([day 21](#day-21)).

</details>

<details>
<summary>mini exercise answer</summary>

- **link error:** `int g_samples_dropped;` is a definition with external linkage in every including file. write `inline int g_samples_dropped = 0;`.
- **link error:** `g_channel_map` is also a non-`inline`, non-`const` variable defined in a header. make it `inline`.
- **silent:** `{16, -1}` builds a two-element vector. with `inline` added, write `inline std::vector<int> g_channel_map(16, -1);`.
- **silent:** `raw * gain` promotes both operands to `int`, and 65535 * 65535 overflows `int`: undefined behavior, despite the unsigned types. write `return std::uint32_t{raw} * gain;`.

a fifth, optional improvement: `Sample` is 24 bytes on a typical 64-bit platform because of padding; ordering the members `double value; bool valid; std::uint8_t channel;` makes it 16, which matters for something stored by the million.

</details>

#### connections

this module was about what exists before any of your logic runs: which definitions make up the program, how objects get their first values, how big they are, and how long they live. the next module stays at that level and asks what you can safely *refer to*: temporaries, references, `const`, value categories, and the behavior the standard leaves undefined. after that, [day 16](#day-16) turns the destruction order from [day 06](#day-06) into the central resource-management technique of the language.

[back to the curriculum map](#curriculum)

---

<a id="module-values"></a>

## module 2: references, values, and the language contract

what you can safely refer to, what an expression's category decides, and what the standard leaves undefined.

<a id="day-08"></a>

### day 08: temporaries, lifetime extension, and dangling references

**module 2:** references, values, and the language contract · **reading time:** about 6 minutes · **standard:** C++17  
**objective:** predict when a temporary dies, apply the one rule that extends its life, and spot references that outlive their objects  
**builds on:** [day 06](#day-06) (storage duration and object lifetime)

#### the idea

`for (int d : load_frame().detections())` compiles cleanly, passes code review, and iterates a vector that has already been destroyed. temporaries are the objects you never named: function results, conversions, the result of `a + b`. their lifetime rule is short enough to memorize, and its one exception is narrower than most people assume.

#### understanding the concept

a temporary object is destroyed at the end of the **full-expression** that created it: the outermost expression that is not part of another one, which in practice usually means at the `;`. everything inside the expression can use the temporary safely; a reference or pointer that escapes the expression cannot.

**lifetime extension.** when a temporary is bound *directly* to a `const T&` or `T&&` local reference, the temporary lives as long as the reference. "directly" includes a member accessed on a temporary (`make_frame().ids`). it does not include anything that passes through a function returning a reference, because the compiler cannot see what that reference refers to. also, a temporary bound to a function's reference parameter only lives until the end of the full-expression containing the call, and a temporary bound to the return value in a `return` statement is not extended at all.

#### in code

**dangling: a reference to a local, and a range-for over a temporary.**

```cpp ub
#include <string>
#include <vector>

const std::string& frame_id() {
    std::string id = "base_link";
    return id;                // BUG: the reference outlives id (GCC: -Wreturn-local-addr)
}

struct Frame {
    std::vector<int> ids;
    const std::vector<int>& detections() const { return ids; }
};
Frame load_frame();
void consume(int);

void process() {
    for (int d : load_frame().detections()) consume(d);   // BUG: UB in C++17 and C++20
    for (int d : load_frame().ids) consume(d);            // fine: member of a temporary, extended
}
```

the range-for is the subtle one. it expands to roughly `auto&& range = load_frame().detections();` followed by the loop. `detections()` returns a reference, so the `Frame` temporary is not extended; it dies at the end of that hidden declaration and the loop iterates a destroyed vector. GCC 12 gave no warning for it. C++23 extends the lifetime of all temporaries in the range-for initializer, which fixes this exact case, but in C++17 and C++20 it is undefined behavior. the portable fix is to name the object first: `auto frame = load_frame(); for (int d : frame.detections())`.

#### in practice

getters that return references are a common performance habit, and they are only safe when the caller holds the object they point into. in a robotics stack, `robot_state()` might return a snapshot *by value*, copied out from under a mutex. then `const Pose& pose = robot_state().pose();` binds to a member of a temporary that dies at the `;`, and every later read of `pose` is undefined behavior that usually still "works" in tests. the fix at the call site is to name the snapshot: `auto state = robot_state();` and read `state.pose()` from it. the design rule behind it: functions that produce a new object return it by value; only accessors on objects the caller already owns return references. AddressSanitizer (`-fsanitize=address`) reports most of these as `heap-use-after-free` or `stack-use-after-scope` the first time a test exercises the path.

#### watch out for

lifetime extension does not pass through function calls, and the classic victim is a standard algorithm returning a reference:

```cpp ub
#include <algorithm>

int lo();
int hi();

const int& m = std::max(lo(), hi());   // BUG: dangles
int v = std::max(lo(), hi());          // fine: copied before the ';'
```

`std::max` takes `const int&` parameters and returns one of them. the two temporaries are bound to its parameters, so they live only until the end of the full-expression, and `m` is left referring to a dead temporary. in our test at `-O2`, GCC printed `0` for `m` (and, by luck, warned about an uninitialized read). GCC 13 added `-Wdangling-reference` for this pattern; GCC 12 has nothing specific. the defense is a habit: bind function results by value unless you know the function returns a reference to something that outlives your reference.

#### the takeaway

temporaries die at the `;` unless they are bound *directly* to a local reference; a reference that comes back out of a function call extends nothing, so bind function results by value unless you know what the reference points into.

#### optional challenge

`load()` returns a `Frame` by value. which of these three lines leave a dangling reference?

```cpp
struct Frame {
    std::vector<int> ids;
    const std::vector<int>& get() const { return ids; }
};
Frame load();

const auto& a = load().ids;     // (1)
const auto& b = load().get();   // (2)
auto c = load().get();          // (3)
```

<details>
<summary>answer</summary>

only (2). in (1) the reference binds directly to a member subobject of the temporary, so the whole `Frame` temporary is extended to `a`'s lifetime. in (2) the reference comes back through a member function; the compiler does not extend anything, the `Frame` dies at the `;`, and `b` dangles. in (3) `c` is a copy of the vector (`auto` deduces `std::vector<int>`), made while the temporary is still alive, so it is safe and owns its own data.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-09"></a>

### day 09: pointers and references

**module 2:** references, values, and the language contract · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** choose between a pointer and a reference by what each can express (null, rebinding, arithmetic), and avoid losing an array's size  
**builds on:** [day 06](#day-06) (storage duration and object lifetime), [day 08](#day-08) (temporaries, lifetime extension, and dangling references)

#### the idea

`float mean(const float samples[64])` looks like a function that takes 64 floats. it takes a pointer, and inside it `sizeof(samples)` is 8. pointers and references look like small syntax variations on "refer to something elsewhere", but they follow different rules about null, rebinding, arithmetic, and how much of the original type they remember. choosing well starts with knowing those rules precisely.

#### understanding the concept

**a reference is an alias.** once bound, it names the same object for its whole life; there is no syntax to rebind it. `r = b;` assigns `b`'s value to whatever `r` refers to. a reference must be initialized, and in a valid program it always refers to an object or function, because the only way to make a "null reference" is to dereference a null pointer first, which is already undefined behavior. a reference can still dangle ([day 08](#day-08)), so "never null" does not mean "always valid".

**a pointer is an object holding an address.** it can be null, it can be reassigned, it can be compared, and it supports arithmetic within an array. that flexibility is exactly what makes it the right tool for "optional" and "may change what it points to", and the wrong tool when neither applies.

**`nullptr`, not `NULL` or `0`.** `NULL` is an implementation-defined null pointer constant: it might be `0`, `0L`, or a compiler intrinsic like GCC's `__null`. its type is an integer type in practice, so it can select an integer overload. `nullptr` has type `std::nullptr_t`, which converts to any pointer type and to no integer type.

**arrays decay.** an array expression converts to a pointer to its first element in most contexts, and a function parameter declared as `T a[N]` is really `T* a`; the `N` is ignored. pointer arithmetic is defined only within one array: you may form pointers to any element and to *one past the end*, but you may not dereference the one-past-the-end pointer, and merely computing a pointer further out (or before the first element) is undefined behavior. relational comparison (`<`) of pointers into unrelated objects gives an unspecified result; `std::less<T*>` is guaranteed to give a consistent total order if you need one, for example as a map key.

#### in code

**rebinding that is not rebinding, and an overload that picks the wrong side.**

```cpp complete
#include <cstddef>
#include <cstdio>

void log_value(int)         { std::puts("int"); }
void log_value(const char*) { std::puts("const char*"); }

int main() {
    int a = 1, b = 2;
    int& r = a;
    r = b;                      // assigns 2 to a; r still refers to a
    b = 7;
    std::printf("%d %d\n", a, r);   // prints: 2 2

    log_value(0);               // prints: int
    log_value(nullptr);         // prints: const char*
    // log_value(NULL);         // GCC 12: error, ambiguous call. With NULL defined as 0
                                // (as some implementations do), it silently prints: int
}
```

the `NULL` line is the interesting one. which behavior you get depends on the implementation's definition of `NULL`, so the same source can be an error on one toolchain and a silent wrong call on another. `nullptr` removes the question.

**decay loses the size; pointer arithmetic has hard edges.**

```cpp ub
#include <cstddef>
#include <cstdint>

// BUG: the 64 is decoration; samples is const float*
float mean_bad(const float samples[64]) {
    const std::size_t n = sizeof(samples) / sizeof(samples[0]);  // 8 / 4 == 2 on x86-64
    float sum = 0;
    for (std::size_t i = 0; i < n; ++i) sum += samples[i];
    return sum / n;
}

// fixed: a reference to an array keeps N as part of the type
template <std::size_t N>
float mean(const float (&samples)[N]) {
    float sum = 0;
    for (float s : samples) sum += s;
    return sum / N;
}

void edges() {
    std::int16_t buf[256] = {};
    std::int16_t* end = buf + 256;   // fine: one past the end may be formed and compared
    // *end = 0;                     // UB: one-past-the-end must not be dereferenced
    // std::int16_t* p = buf + 257;  // UB: computing it is already undefined
    (void)end;
}
```

GCC warns about the first version (`-Wsizeof-array-argument`, on by default), and with a 64-element buffer whose first value is 64, our test printed 32 for `mean_bad` (two elements averaged) and 1 for the reference version. when the array size is not a compile-time constant, the classic pair is pointer plus length; C++20's `std::span` ([day 65](#day-65)) packages that pair into one parameter.

#### in practice

C APIs and hardware drivers speak in pointers and lengths: `read(fd, buf, len)`, a DMA descriptor's base address and byte count, a callback that receives `void* user_data`. keep that style at the boundary and convert to sized types as soon as you are inside your own code. a fixed buffer is better as `std::array<std::uint8_t, 256>` than as a C array, because `std::array` does not decay, can be passed by reference or returned by value, and knows its `size()`. when you do need the length of a built-in array, C++17's `std::size(arr)` refuses to compile on a decayed pointer, where `sizeof(arr) / sizeof(arr[0])` silently computes nonsense. the pointer-plus-length pair that is left over at the boundary is exactly what C++20's `std::span` ([day 65](#day-65)) packages into one parameter.

#### watch out for

**reference members make a class awkward to copy and easy to dangle.** a reference cannot be rebound, so a class that stores one gets no copy assignment:

```cpp complete
struct Sensor { int id = 0; };

struct Filter {
    Sensor& sensor;                 // must be bound at construction, forever
};

void reassign(Filter& a, const Filter& b) {
    // a = b;                       // error: copy assignment is implicitly deleted
}
```

such a class cannot be reassigned, sorted in a `std::vector`, or reset, and it silently relies on the referenced object outliving it. if the relationship can change or the object must be assignable, store a pointer (`Sensor*`, documented as non-owning) or `std::reference_wrapper<Sensor>` instead. reference members are fine for short-lived helper objects that live entirely inside one function call.

#### the takeaway

a reference is a non-null, non-rebindable alias; a pointer is a nullable, rebindable object that may do arithmetic within one array. pick the one whose rules match what you mean, keep sizes in the type where you can, and write `nullptr`.

#### optional challenge

which of these lines have undefined behavior?

```cpp complete
int a[4] = {};
int* p = a + 4;             // (1)
bool at_end = (p == a + 4); // (2)
int x = *(a + 4);           // (3)
int* q = a - 1;             // (4)
```

<details>
<summary>answer</summary>

(3) and (4). forming the one-past-the-end pointer (1) is allowed, and so is comparing it (2), which yields `true`. dereferencing it (3) is undefined behavior. computing `a - 1` (4) is undefined even if `q` is never used, because pointer arithmetic is only defined from the first element to one past the last. in practice (4) "works" almost everywhere, which is why sanitizers and compiler warnings matter more than intuition here.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-10"></a>

### day 10: const as a contract

**module 2:** references, values, and the language contract · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** read and apply const on pointers, references, and member functions, and choose parameter types that state a function's contract  
**builds on:** [day 09](#day-09) (pointers and references)

#### the idea

read this declaration from a tracking library: `void update(Track* t, Detection* d);`. can `t` be null? will `update` modify `d`? will it keep either pointer after it returns? the signature answers none of these questions. now compare `void update(Track& t, const Detection& d);`: both must exist, only `t` changes, and nothing in the types suggests the function holds on to them. pointers, references, and `const` are not only about mechanics. they are the cheapest documentation you will ever write, and the compiler checks it.

#### understanding the concept

**reading `const`.** `const` applies to whatever is immediately to its left, or to the right if nothing is on its left. reading right to left works well:

| declaration | read as | can change pointer | can change pointee |
|---|---|---|---|
| `const T* p` (same as `T const* p`) | pointer to const T | yes | no |
| `T* const p` | const pointer to T | no | yes |
| `const T* const p` | const pointer to const T | no | no |
| `const T& r` | reference to const T | (never) | no |

`const T&` means "read-only access through this name", not "this object is immutable". someone else holding a non-const path to the same object can change it under you.

**const member functions.** in a member function marked `const`, `this` has type `const T*`, so data members are treated as `const`. that lets you call the function on `const` objects and through `const&` parameters, and it is a promise: calling it does not change the object's observable state. that is *logical* constness. sometimes the bits must change while the observable state does not (a cache, a mutex, a statistics counter); `mutable` exempts a member from the rule.

#### in code

**logical constness with `mutable`.**

```cpp complete
#include <mutex>
#include <optional>
#include <utility>
#include <vector>

class Calibration {
public:
    explicit Calibration(std::vector<double> raw) : raw_(std::move(raw)) {}

    double offset() const {                      // same answer every call: logically const
        std::lock_guard<std::mutex> lock(mutex_);
        if (!cached_) cached_ = compute();       // allowed: cached_ is mutable
        return *cached_;
    }

private:
    double compute() const {
        double s = 0;
        for (double r : raw_) s += r;
        return s / raw_.size();
    }
    std::vector<double> raw_;
    mutable std::optional<double> cached_;
    mutable std::mutex mutex_;
};
```

the mutex is not decoration. the standard library guarantees that its own `const` member functions can be called concurrently on the same object, and generic code and your colleagues will assume the same of your types. a `mutable` member written from a `const` function breaks that assumption unless it is synchronized (data races are [day 76](#day-76)). if you add `mutable`, you own the thread-safety of that member.

#### in practice

here is the tracker API from the opening, written so the signature carries the contract:

```cpp
class Tracker {
public:
    void set_gate(double gate_m);                      // cheap type: by value
    void ingest(const DetectionBatch& batch);          // large, read-only: const&
    void predict(Track& track, double dt) const;       // in/out parameter: non-const&
    const Track* find(TrackId id) const;               // may be absent: pointer, nullptr if not found
    void add(Track track);                             // sink: take by value, move inside
};
```

the guidelines behind it: pass cheap-to-copy types (roughly, a couple of machine words: integers, doubles, small structs, iterators, `std::string_view`) by value, because a reference forces an indirection and lets the compiler assume less about aliasing. pass larger read-only objects by `const&`. use a non-const reference for an in/out parameter, and prefer returning a value over an "out" parameter when you can. use a pointer when "nothing" is a legitimate value. none of these says anything about ownership; that is what smart pointers in signatures are for ([day 28](#day-28)). a `const Track*` from `find` is a borrowed view, valid until the tracker changes, and that limit belongs in a comment because the type cannot express it.

#### watch out for

`const` on a member function is shallow. it makes the *pointer member* const, not what it points to:

```cpp complete
#include <vector>

struct Joint { double angle = 0.0; };

class Arm {
public:
    void reset_view() const {
        joints_[0].angle = 0.0;     // compiles: joints_ is Joint* const here, joints are not const
        // spare_[0].angle = 0.0;   // error: spare_ is a const vector inside a const function
    }
private:
    Joint* joints_ = nullptr;
    std::vector<Joint> spare_;
};
```

a `std::vector` member propagates constness to its elements because its `operator[] const` returns `const T&`. a raw pointer member (and, for the same reason, a smart pointer member) does not. if an object conceptually owns what a pointer member points to, its `const` functions must enforce that themselves; the compiler will not.

#### the takeaway

make the signature say it: value for cheap inputs, `const&` for large read-only ones, `&` for in/out, pointer for "might be nothing", and `nullptr` always; then treat `const` as a promise about observable state that you must keep, especially across threads.

#### optional challenge

which numbered lines fail to compile? with those lines deleted, what does the program print?

```cpp fails
#include <iostream>

int main() {
    int a = 1, b = 2;
    const int* p = &a;
    int* const q = &a;
    const int& r = a;
    p = &b;   // (1)
    *q = 3;   // (2)
    *p = 4;   // (3)
    q = &b;   // (4)
    a = 5;    // (5)
    std::cout << r << '\n';
}
```

<details>
<summary>answer</summary>

lines (3) and (4) fail. `p` is a pointer to `const int`, so `*p = 4` assigns through a read-only path; `q` is a `const` pointer, so it cannot be reseated. line (1) is fine (the pointer itself is not const), and (2) is fine (the pointee of `q` is not const).

with them removed, it prints `5`. `r` is a read-only view of `a`, not a snapshot and not a promise that `a` never changes: `a` was set to 3 through `q` and then to 5 directly, and `r` sees the current value.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-11"></a>

### day 11: value categories without the headache

**module 2:** references, values, and the language contract · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** classify expressions as lvalues, xvalues, or prvalues, and use the binding rules to predict which overload is called  
**builds on:** [day 08](#day-08) (temporaries, lifetime extension, and dangling references), [day 10](#day-10) (const as a contract)

#### the idea

here is a function that looks like it moves a string into a container:

```cpp
void Registry::store(std::string&& name) {
    names_.push_back(name);   // copies
}
```

it copies. `name` has type "rvalue reference to `std::string`", but the *expression* `name` is an lvalue, so `push_back(const std::string&)` is chosen. the confusion comes from mixing up two independent properties that every expression has: a **type** and a **value category**. once you keep them apart, overload resolution, moves, and copy elision stop being folklore.

#### understanding the concept

value categories classify **expressions**, not variables or objects. since C++11 there are three leaf categories, and C++17 sharpened what they mean:

```text
                 expression
                /          \
          glvalue           rvalue
         /       \         /      \
     lvalue        xvalue          prvalue
  (identity,     (identity,      (no identity:
   not movable)   movable)        a recipe for a value)
```

- an **lvalue** designates an object or function with an identity you can refer to again: a variable name (of *any* type, including `T&&`), `*p`, `a[i]`, `++x`, a call to a function returning `T&`, a string literal.
- an **xvalue** ("expiring") designates an object whose resources may be reused: `std::move(x)`, a call to a function returning `T&&`, a member access on an xvalue.
- a **prvalue** ("pure") has no identity yet. in C++17 it is not an object at all but an *initializer*: `42`, `x + 1`, `x++`, `Frame{}`, a call to a function returning by value.

a **glvalue** is an lvalue or xvalue (it has identity); an **rvalue** is an xvalue or prvalue (it may be moved from).

**binding rules** decide which overload wins:

| parameter | lvalue | xvalue | prvalue |
|---|---|---|---|
| `T&` | yes | no | no |
| `const T&` | yes | yes | yes |
| `T&&` | no | yes | yes |

when both `const T&` and `T&&` accept an rvalue, `T&&` is the better match. `std::move` does not move anything: it is a cast that turns its argument into an xvalue so that the `T&&` overload is selected. what the move then does is [day 21](#day-21)'s subject.

#### in code

**predict which overload is called.**

```cpp complete
#include <cstdio>
#include <utility>

struct Frame { int id = 0; };

void take(Frame&)       { std::puts("Frame&"); }
void take(const Frame&) { std::puts("const Frame&"); }
void take(Frame&&)      { std::puts("Frame&&"); }

Frame make() { return Frame{}; }

int main() {
    Frame f;
    const Frame cf;
    Frame&& r = make();   // lifetime-extended temporary

    take(f);              // 1
    take(cf);             // 2
    take(Frame{});        // 3
    take(make());         // 4
    take(std::move(f));   // 5
    take(r);              // 6
    take(std::move(cf));  // 7
}
```

<details>
<summary>output</summary>

```text
Frame&
const Frame&
Frame&&
Frame&&
Frame&&
Frame&
const Frame&
```

lines 3 and 4 are prvalues, line 5 is an xvalue. line 6 is the headline: `r` is declared as `Frame&&`, but the expression `r` is an lvalue, so `Frame&` wins. line 7: `std::move(cf)` is an xvalue of type `const Frame`; `Frame&&` cannot bind to a const object, so `const Frame&` is chosen. moving from a `const` object silently copies.

</details>

#### in practice

the standard library is built on these binding rules. `std::vector::push_back` has two overloads: `push_back(const T&)`, which copies, and `push_back(T&&)`, which moves. as a caller you never pick one explicitly; the category of your argument does. a temporary (`push_back(Frame{})`) or an explicitly expiring object (`push_back(std::move(frame))`) takes the cheap path, and an ordinary named object is copied because you might still use it. in a telemetry pipeline that hands large message buffers from stage to stage, reading a call site with categories in mind tells you exactly where the copies are: every argument that is a plain name and not wrapped in `std::move` is one. your own interfaces can offer the same pair of overloads when copying is expensive, or take the parameter by value and let the caller's category decide, which [day 23](#day-23) discusses.

#### watch out for

**if it has a name, it is an lvalue.** every function parameter, including one declared `T&&`, is an lvalue inside the function body. the fix in the opening example is to say what you mean:

```cpp
void Registry::store(std::string&& name) {
    names_.push_back(std::move(name));   // xvalue: selects push_back(std::string&&)
}
```

the rule exists for safety: a name can be used more than once, and silently moving on first use would leave later uses looking at a gutted object. moving is therefore always an explicit decision at the point of last use. the opposite mistake is also common: `std::move` on a `const` object (line 7 above), or on an object you read again later.

#### the takeaway

every expression has a type and a value category; overload resolution picks by category, and a named variable, even one declared `T&&`, is always an lvalue.

#### optional challenge

classify each expression as lvalue, xvalue, or prvalue, given `int x = 0; int& f(); int g(); std::string s;`:
`x`, `x + 1`, `f()`, `g()`, `std::move(x)`, `"abc"`, `x++`, `++x`, `std::move(s).size()`.

<details>
<summary>answer</summary>

- `x`: lvalue (a name).
- `x + 1`: prvalue (built-in arithmetic yields a value).
- `f()`: lvalue (returns `int&`).
- `g()`: prvalue (returns by value).
- `std::move(x)`: xvalue (returns `int&&`).
- `"abc"`: lvalue. string literals are arrays with static storage duration, so they have identity; it is the only literal that is an lvalue.
- `x++`: prvalue (the old value, a copy). `++x`: lvalue (the variable itself, after incrementing).
- `std::move(s).size()`: prvalue. the object expression is an xvalue, but `size()` returns `std::size_t` by value, and the category of a call depends only on the function's return type.

</details>

#### going deeper (optional)

##### `decltype` and value categories

**`decltype` sees both the name and the expression.** `decltype(name)` gives the declared type of the entity. `decltype(expression)` encodes the category: `T&` for an lvalue, `T&&` for an xvalue, `T` for a prvalue. parentheses turn a name into an expression:

```cpp ub
#include <type_traits>
#include <utility>

int x = 0;
static_assert(std::is_same_v<decltype(x), int>);                 // the entity
static_assert(std::is_same_v<decltype((x)), int&>);              // lvalue expression
static_assert(std::is_same_v<decltype(std::move(x)), int&&>);    // xvalue
static_assert(std::is_same_v<decltype(x + 1), int>);             // prvalue
static_assert(std::is_same_v<decltype(x++), int>);               // prvalue
static_assert(std::is_same_v<decltype(++x), int&>);              // lvalue

decltype(auto) value()  { int local = 1; return local; }    // returns int
decltype(auto) dangle() { int local = 1; return (local); }  // BUG: returns int&, dangling
```

the last pair is why `decltype(auto)` (C++14) deserves care: an innocent pair of parentheses changes the return type to a reference to a dead local. GCC flags it with `-Wreturn-local-addr`.

[back to the curriculum map](#curriculum)

---

<a id="day-12"></a>

### day 12: copy elision and temporary materialization

**module 2:** references, values, and the language contract · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** explain why returning a prvalue never copies in C++17, when NRVO applies, and why `return std::move(local)` is a pessimization  
**builds on:** [day 11](#day-11) (value categories without the headache)

#### the idea

in C++14 you could not return a type with deleted copy and move constructors from a factory function. in C++17 you can. compilers did not get smarter; the language changed what `return T{...};` *means*. knowing what changed tells you which returns are free by definition, which are free in practice, and which quietly cost a move.

#### understanding the concept

**temporary materialization.** a prvalue becomes an actual object only when it has to: when a reference binds to it, when you access a member of it, or when it is discarded. at that point a temporary is created and the expression becomes an xvalue. otherwise the prvalue directly initializes its final destination. that is the mechanism behind C++17's **guaranteed copy elision**: `T x = T{...};` and `return T{...};` initialize the target in place. no copy or move constructor is called, and none needs to exist.

returning a *named* local is different. named return value optimization (NRVO) lets the compiler construct the local directly in the return slot, but it is permitted, not required, and the copy or move constructor must still be accessible. when NRVO does not happen, a returned local is treated as an rvalue first, so it is moved if it can be.

#### in code

**guaranteed elision versus NRVO.** a type that logs its special members:

```cpp complete
#include <cstdio>

struct Big {
    Big() { std::puts("ctor"); }
    Big(const Big&) { std::puts("copy"); }
    Big(Big&&) noexcept { std::puts("move"); }
};

Big make_prvalue() { return Big{}; }                     // guaranteed elision (C++17)
Big make_named()   { Big b; return b; }                  // NRVO: allowed, not required
Big make_either(bool c) { Big a, b; return c ? a : b; }  // not a plain name: copied

int main() {
    Big x = make_prvalue();   // prints: ctor
    Big y = make_named();     // prints: ctor (with NRVO), or ctor move (without)
    Big z = make_either(true);// prints: ctor ctor copy
    (void)x; (void)y; (void)z;
}
```

with GCC 12 at default settings we saw `ctor`, `ctor`, and `ctor ctor copy`. with `-fno-elide-constructors`, which disables optional elision, `make_named` printed `ctor move` while `make_prvalue` still printed only `ctor`: in C++17 that elision is part of the language, not an optimization. `make_either` copies because the conditional expression is an lvalue that is not simply the name of a local, so neither NRVO nor the implicit move applies. write `if (c) return a; return b;` and each branch qualifies again.

#### in practice

guaranteed elision changes what you can design, not only how fast it runs. consider a handle to a memory-mapped device register block in a motor controller. other components cache its address, so it must never move, and you want no "moved-from" state to reason about:

```cpp
#include <cstdint>

class RegisterBlock {
public:
    explicit RegisterBlock(std::uintptr_t base);
    RegisterBlock(const RegisterBlock&) = delete;
    RegisterBlock& operator=(const RegisterBlock&) = delete;
    // no move operations are declared: deleting copy suppresses them
};

RegisterBlock open_block(std::uintptr_t base) {
    validate(base);                // checks before construction
    return RegisterBlock{base};    // C++17: compiles; C++14: error, deleted copy constructor
}

RegisterBlock motor = open_block(0x4000'0000);   // constructed in place
```

before C++17 you had to return such a type through `std::unique_ptr` or use a two-phase `init()`, both of which leak complexity into every caller. now a factory function can return a non-movable type by value, which keeps the class invariant ("if it exists, it is pinned and valid") without a heap allocation. note the limit: a factory that builds a named local and returns it still fails to compile for this type, because NRVO is optional and needs an accessible constructor.

#### watch out for

**`return std::move(local);` is a pessimization.** it looks like a helpful hint and does the opposite:

```cpp complete
#include <utility>
#include <vector>

std::vector<int> collect() {
    std::vector<int> ids(1000);
    return std::move(ids);   // operand is no longer a plain name: NRVO is impossible
}
```

NRVO applies only when the return operand is the plain name of a local. `std::move(ids)` is an xvalue expression, so the compiler must construct the result by moving. a plain `return ids;` would either be elided or, failing that, moved anyway, because a returned local is treated as an rvalue first. the explicit `std::move` removes only the best case. GCC and Clang flag it with `-Wpessimizing-move`, which is part of `-Wall`. use `std::move` in a `return` only for things that are not locals or by-value parameters, such as a data member you are handing out.

#### the takeaway

since C++17 a prvalue is an initializer that builds its object in place, so returning `T{...}` never copies or moves; returning a named local usually does not either, as long as you leave it a plain name.

#### optional challenge

`make_big()` returns `Big` by value. which functions are *guaranteed* to call no copy or move constructor, and what happens in the others?

```cpp
Big a()      { return Big{}; }                 // (1)
Big b()      { Big x; return x; }              // (2)
Big c()      { return make_big(); }            // (3)
Big d(Big p) { return p; }                     // (4)
Big e()      { Big x; return std::move(x); }   // (5)
```

<details>
<summary>answer</summary>

(1) and (3) are guaranteed: both return a prvalue, which initializes the caller's object directly, and a chain of prvalue returns stays a chain of initializers.

(2) is NRVO: allowed and almost always done, but if it does not happen the local is moved. (4) can never use NRVO, because a parameter is not constructed in the function's return slot; it is moved (a returned by-value parameter is treated as an rvalue first). (5) always moves: the operand is not a plain name, so elision is impossible.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-13"></a>

### day 13: undefined behavior and the optimizer

**module 2:** references, values, and the language contract · **reading time:** about 6 minutes · **standard:** C++17  
**objective:** tell undefined, unspecified, and implementation-defined behavior apart, and explain how the optimizer turns UB into deleted checks  
**builds on:** [day 04](#day-04) (integer types, promotions, and conversions), [day 09](#day-09) (pointers and references)

#### the idea

a telemetry service guards a counter with `if (total + delta < total) reset();`. it works in debug builds. in release builds the reset never fires, the counter goes negative, and dashboards show nonsense. nobody touched the code; the optimizer read it more carefully than we did. undefined behavior is not "the hardware does something weird". it is a contract: you promise certain things never happen, and the compiler is entitled to generate code that is only correct if you kept that promise.

#### understanding the concept

the standard describes three different kinds of looseness, and mixing them up leads to bad decisions:

| category | what the standard says | examples |
|---|---|---|
| implementation-defined | one of several outcomes; the implementation must document which | `sizeof(long)`, whether plain `char` is signed, the definition of `NULL`, right-shifting a negative `int` (until C++20) |
| unspecified | one of several outcomes; no documentation required, may vary call to call | order of evaluation of function arguments, whether identical string literals share storage, `<` on pointers to unrelated objects |
| undefined (UB) | no requirements at all | signed overflow, out-of-bounds access, use after free, reading an uninitialized `int`, data races |

implementation-defined behavior is portable *with a check* (a `static_assert` on `sizeof`, for example). unspecified behavior is safe as long as your program is correct for every allowed outcome. undefined behavior is never safe, and the standard explicitly places no requirement on an execution that contains it, *not even on operations before the undefined one*. ([day 02](#day-02)'s "ill-formed, no diagnostic required" is a fourth, compile-time cousin: the program is broken and nobody has to tell you.)

**why the optimizer makes UB dangerous.** optimizers transform code under the assumption that the program is valid. if signed overflow cannot happen, then `a + b < a` with `b > 0` is always false, and a loop counter `int i` that only increases can never wrap. if dereferencing a null pointer cannot happen, then a pointer that was dereferenced is non-null and a later null check is dead code. each step is a sound deduction from the rules; the result is that a bug can delete your safety checks.

#### in code

**signed overflow: the check that is not there.**

```cpp ub
#include <climits>

bool will_overflow(int a, int b) {     // intended for b > 0
    return a + b < a;                  // BUG: relies on signed overflow (UB)
}

bool will_overflow_fixed(int a, int b) {
    return b > 0 && a > INT_MAX - b;   // decide before doing the arithmetic
}
```

GCC 12 at `-O2` compiled `will_overflow` to a single shift that tests the sign of `b`: it rewrote `a + b < a` as `b < 0`, which is exactly what the expression means when overflow is impossible. the same reasoning shows up in loops. `for (int i = 1; i > 0; i *= 2) ++count;` printed `31` at `-O0` in our test and ran forever at `-O2`, because "a positive `int` doubled stays positive" is true in every program without UB. if you need wraparound, use unsigned types (where it is defined, modulo 2^N); if you need detection, check first, or use your compiler's checked-arithmetic builtins (`__builtin_add_overflow` in GCC and Clang, a non-standard extension).

**a null check deleted because of an earlier dereference.**

```cpp ub
struct Device { int status; };

int read_status(const Device* d) {
    int s = d->status;     // BUG: dereference before the check
    if (!d) return -1;     // GCC -O2: removed, since d cannot be null here
    return s;
}
```

at `-O0` our build contained the comparison against zero; at `-O2` the whole function was one load and a return. this exact pattern caused a Linux kernel vulnerability in 2009 (the TUN driver), and the kernel has built with `-fno-delete-null-pointer-checks` ever since. the fix is ordinary: check, then dereference.

#### in practice

because UB is invisible in testing until it is not, the defense is tooling in CI, not vigilance:

```sh
# compiler diagnostics on every build
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror ...

# a sanitizer job running the test suite (GCC or Clang)
g++ -std=c++17 -O1 -g -fno-omit-frame-pointer \
    -fsanitize=address,undefined -fno-sanitize-recover=undefined tests.cpp -o tests_asan

# data races need a separate build: ThreadSanitizer cannot be combined with ASan
g++ -std=c++17 -O1 -g -fsanitize=thread tests.cpp -o tests_tsan
```

sanitizers cost run time and memory (ASan's own documentation cites a typical slowdown of about 2x), so they live in test jobs, not release builds. sanitizers only see the paths your tests execute, which is one more argument for tests that exercise edge values.

#### watch out for

**"it works on my machine" is the defining property of UB, not a defense against it.** a program with undefined behavior can produce the right answer in every test, then change behavior after a compiler upgrade, a new optimization level, or an unrelated edit that changes inlining. passing tests prove that the paths you ran did what you expected, on that build. they say nothing about what the program means.

two more misconceptions. `volatile` is for memory-mapped I/O and similar "every access is observable" cases; it makes nothing atomic and orders nothing between threads, so a race on a `volatile int` is still UB (atomics are [day 83](#day-83)). and "it works on my machine" is the defining property of UB, not a defense against it.

#### the takeaway

implementation-defined means "check the documentation", unspecified means "be correct for every outcome", and undefined means "the compiler assumes it never happens"; write code that never relies on UB, and let warnings and sanitizers find the places where you did by accident.

#### optional challenge

classify each as well-defined, implementation-defined, unspecified, or undefined in C++17, and note any that changed in C++20.

1. `sizeof(int) == 4`
2. which of `f(a(), b())`'s arguments is evaluated first
3. `int x = INT_MAX; ++x;`
4. `signed char c = 200;` (with 8-bit `signed char`)
5. `int y = -8 >> 1;`
6. `int i = 0; i = i++;`

<details>
<summary>answer</summary>

1. implementation-defined. only minimum ranges are guaranteed; `static_assert` it if your code depends on it.
2. unspecified. each argument is fully evaluated before the next begins, but the order may differ between compilers or even call sites.
3. undefined: signed overflow.
4. implementation-defined in C++17 (converting an out-of-range value to a signed type). since C++20 it is defined as modulo 2^N, giving -56.
5. implementation-defined in C++17 (right shift of a negative value; GCC documents an arithmetic shift, giving -4). C++20 requires two's complement and defines it as an arithmetic shift.
6. well-defined since C++17: the right operand is sequenced before the assignment, so `i` ends up 0. in C++14 it was undefined.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-14"></a>

### day 14: the usual suspects: aliasing, punning, and evaluation order

**module 2:** references, values, and the language contract · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** recognize the everyday patterns that cause undefined or unspecified behavior, and use the safe spelling of each  
**builds on:** [day 13](#day-13) (undefined behavior and the optimizer)

#### the idea

most undefined behavior in production code comes from a handful of patterns that look completely ordinary: a cast that reinterprets a byte buffer as a struct, an index one past the end, an argument list with two calls that touch the same state. you do not need to memorize the standard's whole list. you need to recognize these patterns on sight and know the safe way to write each one.

#### understanding the concept

**the usual suspects**, and what catches them:

| UB | typical form | practical defense |
|---|---|---|
| signed overflow | `INT_MAX + 1`, `a * b` on promoted `uint16_t` ([day 04](#day-04)) | check before computing; UBSan |
| out of bounds | `v[v.size()]`, pointer arithmetic past the end ([day 09](#day-09)) | `.at()` in non-hot code, `-D_GLIBCXX_ASSERTIONS` (libstdc++), ASan |
| use after free / dangling | [day 08](#day-08)'s references to dead objects | ownership discipline ([day 16](#day-16), [day 26](#day-26)), ASan |
| uninitialized read | `int n; return n;` ([day 03](#day-03)) | default member initializers, `-Wuninitialized`, MSan (Clang), Valgrind |
| strict aliasing | `*reinterpret_cast<std::uint32_t*>(&f)` | `std::memcpy`, C++20 `std::bit_cast` |
| data race | two threads, one non-atomic object, at least one writer | mutexes and atomics ([day 76](#day-76), [day 83](#day-83)), TSan |
| modifying a string literal | `const_cast<char*>("abc")[0] = 'x'` | do not cast away `const` from data you do not own |

the **strict aliasing rule** says you may access an object only through its own type (give or take signedness and cv-qualification) or through `char`, `unsigned char`, or `std::byte`. that lets the compiler assume a write through a `float*` cannot change an `int` it has cached in a register. `bits_bad` printed the right answer (`3f800000` for 1.0f) in our test, with a `-Wstrict-aliasing` warning at `-O2`. correct output today is not evidence of a correct program. `std::memcpy` of a few bytes is generally compiled to a register move by mainstream optimizers; check the generated code if it matters. `std::bit_cast` (C++20) does the same thing as an expression and is `constexpr`.

#### in code

**type punning: three ways to read a float's bits** (the last one, commented out, needs C++20).

```cpp ub
#include <cstdint>
#include <cstring>

std::uint32_t bits_bad(float f) {
    return *reinterpret_cast<std::uint32_t*>(&f);  // BUG: UB, accesses a float as uint32_t
}

std::uint32_t bits_ok(float f) {                    // C++17
    static_assert(sizeof(float) == sizeof(std::uint32_t));
    std::uint32_t u;
    std::memcpy(&u, &f, sizeof u);                  // copies bytes: always allowed
    return u;
}

// C++20:
// #include <bit>
// std::uint32_t bits(float f) { return std::bit_cast<std::uint32_t>(f); }
```

#### in practice

radar and telemetry code is full of the third pattern: a byte buffer arrives from a socket and gets cast to a header struct.

```cpp complete
#include <cstdint>
#include <cstring>

struct FrameHeader { std::uint16_t magic; std::uint16_t count; std::uint32_t seq; };

FrameHeader parse(const unsigned char* buf) {
    // BUG: return *reinterpret_cast<const FrameHeader*>(buf);
    //      aliasing violation, and buf + offset may be misaligned for uint32_t
    FrameHeader h;
    std::memcpy(&h, buf, sizeof h);   // FrameHeader is trivially copyable
    return h;
}
```

the cast version "works" on x86, which tolerates misaligned loads, and then faults on an ARM controller or gets miscompiled after an unrelated inlining change. the `memcpy` version is correct everywhere (byte order and padding are still your job: those are implementation-defined layout questions, not UB).

#### watch out for

**order of evaluation** is the area where folklore lags the standard. C++17 fixed several cases: in `a << b`, `a >> b`, `a[b]`, `a.b`, and `a->b` the left side is evaluated first, and in `a = b` (and `a += b`) the right side is evaluated first. so `std::cout << next() << next();` is now left to right, and `i = i++ + 1;` is well defined (it sets `i` to 1 when `i` starts at 0). GCC 12 still emits `-Wsequence-point` for that line even in C++17 mode, a stale warning worth knowing about.

function arguments did not get an order. in `log_pair(next_id(), next_id())` the two calls are indeterminately sequenced: each runs completely before the other starts (which, since C++17, makes `f(i++, i++)` unspecified rather than undefined), but which one goes first is unspecified. our GCC build printed `2 1`. any code whose result depends on that order is a portability bug; give the values names on separate lines.

#### the takeaway

reinterpret bytes with `std::memcpy` or `std::bit_cast`, never through a cast pointer; never let a result depend on the order in which function arguments are evaluated; and for every other suspect, know which sanitizer catches it.

#### optional challenge

classify each line as well-defined, unspecified, or undefined. `v` is a `std::vector<int>` holding three elements and `next()` returns an increasing counter.

```cpp
int a = v[v.size()];                                      // (1)
float f = 1.0f;
unsigned char b = *reinterpret_cast<unsigned char*>(&f);  // (2)
std::printf("%d %d\n", next(), next());                   // (3)
int* p = new int[4];
delete p;                                                 // (4)
```

<details>
<summary>answer</summary>

1. undefined: `operator[]` does not check bounds, and index 3 is past the end. `v.at(v.size())` would throw `std::out_of_range` instead.
2. well-defined: any object may be read through `char`, `unsigned char`, or `std::byte`. *which* byte you get depends on the platform's byte order, which is implementation-defined, but the access itself is fine.
3. unspecified: the two calls happen in some order, each completely before the other, so the program may print `1 2` or `2 1`, but nothing worse.
4. undefined: memory from `new[]` must be released with `delete[]`. this "works" on many allocators for `int`, and corrupts the heap for types with destructors.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-15"></a>

### day 15: review: references, values, and the language contract

**module 2:** references, values, and the language contract · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** consolidate temporaries and dangling, pointers and references, const, value categories, copy elision, and undefined behavior  
**covers:** [day 08](#day-08) to [day 14](#day-14)

#### recap

| lesson | key idea |
|---|---|
| [day 08](#day-08) | temporaries die at the end of the full-expression unless bound *directly* to a local reference; nothing extends through a function call. |
| [day 09](#day-09) | references are non-null, non-rebindable aliases; pointers are nullable, rebindable, and do arithmetic within one array. |
| [day 10](#day-10) | `const` is a read-only view and an API contract, shallow on pointer members, and something callers and threads rely on. |
| [day 11](#day-11) | every expression has a type and a value category; named variables are lvalues, even `T&&` ones. |
| [day 12](#day-12) | in C++17 a prvalue is an initializer, so returning one needs no copy or move constructor; NRVO is still optional. |
| [day 13](#day-13) | implementation-defined, unspecified, undefined: the optimizer assumes UB never happens, so a bug can delete your checks. |
| [day 14](#day-14) | reinterpret bytes with `memcpy` or `bit_cast`, never depend on argument evaluation order, and let sanitizers find the rest. |

the thread through the module: the standard defines an abstract machine, and most surprises come from the gap between that machine and "it is just memory and instructions".

#### review questions

1. one of these lines dangles and the other is fine. explain the difference in terms of value categories and lifetime extension.

   ```cpp
   const Frame& f = make_frame();            // make_frame returns Frame by value
   const int&   m = std::max(lo(), hi());    // lo and hi return int by value
   ```

2. a colleague says "the order in which `f(read_header(), read_body())` evaluates its arguments is undefined behavior, just like signed overflow." what is right and wrong about that, and why does the difference matter?
3. a `const` member function fills a `mutable` cache without taking a lock. it compiles and passes single-threaded tests. why is it still a bug, and under what condition would it be fine?
4. `RegisterBlock` has deleted copy and move constructors. does `return RegisterBlock{base};` compile in C++17? does `RegisterBlock b{base}; return b;`?
5. from [day 02](#day-02): why does marking a header variable `static` make a duplicate-symbol error go away, and why is that usually the wrong fix?

#### mini exercise

this helper has three bugs from this module: one lifetime bug and two kinds of undefined behavior. one line that looks suspicious is fine. find all four, then rewrite the function.

```cpp complete
#include <vector>

struct Track { int id = 0; std::vector<float> ranges; };
std::vector<Track> load_tracks();

const float& latest_range(int id) {
    const auto& tracks = load_tracks();
    int index;
    for (std::size_t i = 0; i < tracks.size(); ++i)
        if (tracks[i].id == id) index = i;
    const Track& t = tracks[index];
    return t.ranges[t.ranges.size() - 1];
}
```

#### answers

<details>
<summary>answer 1: lifetime extension</summary>

`make_frame()` is a prvalue; binding it directly to `const Frame&` materializes a temporary and extends its life to `f`'s. `std::max(lo(), hi())` is an lvalue (it returns `const int&`): the temporaries from `lo()` and `hi()` were bound to `std::max`'s parameters, which keeps them alive only until the end of the full-expression. extension never passes through a function returning a reference, so `m` dangles at the `;`. `int m = std::max(lo(), hi());` copies the value in time.

</details>

<details>
<summary>answer 2: unspecified versus undefined</summary>

the order is *unspecified*: since C++17 each argument is evaluated completely before the next starts, and either order is a valid execution, so a program correct for both orders is correct. signed overflow is *undefined*: there is no valid execution, and the optimizer may delete code on the assumption it never happens. unspecified order is a portability bug (here, possibly reading the body before the header), fixed by naming intermediate results; UB can corrupt unrelated logic and must be removed.

</details>

<details>
<summary>answer 3: logical constness and threads</summary>

callers, generic code, and the standard library assume that `const` member functions can be called concurrently on the same object. two threads calling the function at once both write the cache: a data race, which is undefined behavior. it is fine only if the object is never shared between threads, or if the `mutable` member is synchronized (a mutex, or an atomic for a simple flag). adding `mutable` makes you responsible for that member's thread safety.

</details>

<details>
<summary>answer 4: guaranteed elision</summary>

`return RegisterBlock{base};` compiles: the prvalue initializes the caller's object directly, and no copy or move constructor is needed or even looked up. `RegisterBlock b{base}; return b;` does not: NRVO is optional, so the language still requires an accessible copy or move constructor, and both are deleted.

</details>

<details>
<summary>answer 5: static in a header</summary>

`static` gives the variable internal linkage, so each translation unit gets its own private object and the linker has nothing to collide. the program now has several variables where the author meant one: an increment in one file is invisible in another. for one shared object, use an `inline` variable (C++17); for one per file, use an anonymous namespace in the `.cpp`.

</details>

<details>
<summary>mini exercise answer</summary>

- **fine (the decoy):** `const auto& tracks = load_tracks();` binds a prvalue directly to a `const&`, so the vector lives until the function returns.
- **UB, uninitialized read:** if no track has the requested `id`, `index` is never assigned and `tracks[index]` reads an indeterminate value.
- **UB, out of bounds:** if the track has no ranges, `t.ranges.size() - 1` wraps to the largest `std::size_t`, and indexing with it is out of bounds.
- **lifetime:** the returned reference points into `tracks`, which is destroyed when the function returns, so every caller gets a dangling reference.

```cpp
#include <optional>
#include <vector>

std::optional<float> latest_range(int id) {
    const auto tracks = load_tracks();        // owned locally, by value
    for (const Track& t : tracks)
        if (t.id == id && !t.ranges.empty())
            return t.ranges.back();           // copy the float out while tracks is alive
    return std::nullopt;                      // not found, or no ranges yet
}
```

`std::optional` gets its own lesson in [day 51](#day-51). if loading every track is expensive, the deeper fix is an API change: the caller owns the track list and passes it in by `const&`.

</details>

#### connections

the first two modules described what the language guarantees and what it leaves to you. the next one turns those guarantees into design techniques: [day 16](#day-16) relies on deterministic destruction, [day 18](#day-18) is where initialization meets class invariants, and the value categories from [day 11](#day-11) are the entire mechanism behind [day 21](#day-21). undefined behavior returns whenever threads share data, in [day 76](#day-76).

[back to the curriculum map](#curriculum)

---

<a id="module-lifecycle"></a>

## module 3: resources and the object lifecycle

RAII, constructors and invariants, construction order, and what copying and moving an object really mean.

<a id="day-16"></a>

### day 16: RAII: let scope do the cleanup

**module 3:** resources and the object lifecycle · **reading time:** about 10 minutes · **standard:** C++17  
**objective:** tie a resource's lifetime to an object so every exit path releases it, and know which exits skip destructors  
**builds on:** [day 06](#day-06) (storage duration and object lifetime), [day 13](#day-13) (undefined behavior and the optimizer)

#### the idea

here is a function that reads a calibration header from a file. it has three exits, and every one of them must remember `fclose`. six months later someone adds a call that can throw, and now there is a fourth exit that nobody wrote down.

that is the whole problem RAII solves. cleanup that depends on every author remembering every exit path will eventually be forgotten. cleanup that the language performs whenever a scope ends cannot be forgotten, because nobody has to remember it.

#### understanding the concept

RAII (resource acquisition is initialization; the name is famously bad) means: tie a resource to the lifetime of an object. the constructor acquires the resource, or throws if it cannot. the destructor releases it. you then lean on the lifetime rules from [day 06](#day-06): an object with automatic storage duration is destroyed when control leaves its scope, in reverse order of construction, however control leaves.

"however control leaves" is the important part. normal fall-through, `return`, `break`, `continue`, `goto` out of a block, and an exception propagating to a handler all run the destructors of the automatic objects being left. during exception propagation this is called stack unwinding: each frame between the `throw` and the matching `catch` is torn down, destructors included.

a few exits do not run destructors, and you should know them:

- `std::exit` destroys static objects but not the automatic objects on the stack.
- `std::abort`, `std::_Exit`, a crash, and `kill -9` destroy nothing.
- if an exception is never caught, `std::terminate` is called, and **whether the stack is unwound first is implementation-defined**. GCC and Clang typically do not unwind in that case, so your destructors may not run.

the deeper idea is an invariant: **if the object exists, the resource is valid**. a `File` object that exists holds an open file. there is no "not yet opened" or "already closed" state for every caller to check. that is encapsulation in its most useful form: the class owns a rule, and no caller can break it.

#### in code

first, the naive version. it is correct today and fragile tomorrow.

```cpp
#include <cstdio>
#include <optional>

struct Header { char magic[4]; unsigned version; };

std::optional<Header> read_header(const char* path) {
    std::FILE* f = std::fopen(path, "rb");
    if (!f) return std::nullopt;

    Header h{};
    if (std::fread(&h, sizeof h, 1, f) != 1) {
        std::fclose(f);                  // exit 1: remembered
        return std::nullopt;
    }
    if (h.version > 3) {
        return std::nullopt;             // BUG: exit 2 leaks the FILE*
    }
    validate(h);                         // BUG: if this throws, f leaks too
    std::fclose(f);
    return h;
}
```

the RAII version moves the cleanup into a type. you rarely need a hand-written class for a C handle: `std::unique_ptr` with a custom deleter is already a general RAII wrapper.

```cpp
#include <cstdio>
#include <memory>
#include <optional>

struct FileCloser {
    void operator()(std::FILE* f) const noexcept { std::fclose(f); }
};
using FilePtr = std::unique_ptr<std::FILE, FileCloser>;

std::optional<Header> read_header(const char* path) {
    FilePtr f{std::fopen(path, "rb")};
    if (!f) return std::nullopt;

    Header h{};
    if (std::fread(&h, sizeof h, 1, f.get()) != 1) return std::nullopt;
    if (h.version > 3) return std::nullopt;
    validate(h);                         // may throw: f is still closed
    return h;                            // every path closes exactly once
}
```

two details. `unique_ptr` never calls the deleter on a null pointer, so a failed `fopen` is handled for free. and the deleter is a function object rather than `&std::fclose`: since C++20, forming a pointer to most standard library functions is unspecified (possibly ill-formed), and an empty function object also lets the `unique_ptr` stay pointer-sized (more on that on [day 26](#day-26)).

#### in practice

a joint controller enables motor torque before running a trajectory. if the trajectory code throws (a planner exception, a bad sensor reading, an allocation failure), the motors must not be left energized.

```cpp
class TorqueEnable {
public:
    explicit TorqueEnable(MotorBus& bus) : bus_(bus) { bus_.enable_all(); }
    ~TorqueEnable() { bus_.disable_all(); }   // must not throw
    TorqueEnable(const TorqueEnable&) = delete;
    TorqueEnable& operator=(const TorqueEnable&) = delete;
private:
    MotorBus& bus_;
};

void run_trajectory(MotorBus& bus, const Trajectory& t) {
    TorqueEnable power{bus};
    for (const auto& setpoint : t) step(bus, setpoint);   // may throw
}   // torque off on every exit path that unwinds
```

notice what RAII does not cover. if the process segfaults, is killed, or hits an uncaught exception on an implementation that does not unwind, `disable_all` never runs. for anything safety-relevant, RAII is the software layer; a hardware watchdog that cuts torque when the heartbeat stops is the layer below it. good engineering uses both, and knows which failure each one handles.

copying is deleted here deliberately. two `TorqueEnable` objects for one bus would disable it twice, the first time too early. whether an RAII type should be copyable, movable, or neither is a design decision about ownership; [day 20](#day-20) and [day 24](#day-24) cover how to make it.

#### watch out for

**destructors must not throw, and release can fail anyway.**

destructors are implicitly `noexcept` (since C++11), unless a base or member has a potentially-throwing destructor. if an exception escapes a `noexcept` destructor, `std::terminate` is called. even a destructor explicitly marked `noexcept(false)` that throws while the stack is already unwinding because of another exception calls `std::terminate`. treat "destructors do not throw" as a hard rule.

**release can fail, and a destructor cannot report it.** `fclose` on a file you wrote may flush buffered data and fail (disk full, network filesystem gone). the `FileCloser` above silently drops that error. for read-only handles that is fine. for writes, give the class an explicit `close()` that returns or throws an error, call it on the success path, and let the destructor be the fallback that cleans up quietly (perhaps logging) when an earlier failure already happened.

#### the takeaway

if something must happen when a scope ends, put it in a destructor. then every exit path, including the ones someone adds next year, gets it for free.

#### optional challenge

predict the output, then predict what changes if you delete the `try`/`catch` in `main`.

```cpp complete
#include <cstdio>
#include <stdexcept>

struct Noisy {
    const char* name;
    ~Noisy() { std::puts(name); }
};

void work() {
    Noisy a{"a"};
    Noisy b{"b"};
    throw std::runtime_error("sensor timeout");
}

int main() {
    try { work(); }
    catch (const std::exception& e) { std::puts(e.what()); }
}
```

<details>
<summary>answer</summary>

with the handler, the stack unwinds to `main` before the `catch` body runs, so you see `b`, `a`, then `sensor timeout`. destruction is in reverse order of construction, and the destructors run before the handler.

without the handler, no matching `catch` exists, so `std::terminate` is called. whether `b` and `a` are destroyed first is implementation-defined. with GCC on Linux and MinGW you typically see neither line, just the terminate message and an abort. this is one reason long-running services catch exceptions at the top of `main` and at the top of every thread function: it guarantees that unwinding, and therefore your RAII cleanup, actually happens.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-17"></a>

### day 17: scope guards: cleanup without a new class

**module 3:** resources and the object lifecycle · **reading time:** about 5 minutes · **standard:** C++17  
**objective:** use a scope guard for one-off cleanup and commit-or-rollback logic, and avoid the unnamed-guard trap  
**builds on:** [day 16](#day-16) (RAII: let scope do the cleanup)

#### the idea

not every cleanup deserves its own class. restoring a flag after a calibration routine, unregistering a callback, rolling back the first two steps of a three-step configuration change when the third fails: each happens once, in one function, and still has to happen on every exit path. writing a dedicated RAII type for each is ceremony; writing the cleanup by hand at every `return` is the bug RAII exists to prevent. a scope guard sits in between.

#### understanding the concept

you already use this pattern every day: `std::lock_guard` locks in its constructor and unlocks in its destructor, `std::vector` frees its buffer, `std::ifstream` closes its file. for one-off cleanup that does not deserve its own type, a scope guard turns any callable into a destructor. C++17 class template argument deduction (CTAD) means you never spell out the lambda's type:

a scope guard is a tiny RAII type whose "resource" is an arbitrary callable. its destructor runs the callable unless the guard has been *dismissed*. that one extra bit of state gives two useful shapes:

- **always run:** arm the guard right after acquiring something, and the cleanup runs however the scope ends.
- **commit or roll back:** arm a rollback before a multi-step change, and dismiss it after the last step succeeds. if anything throws or returns early, the destructor undoes the partial work.

#### in code

```cpp complete
#include <cstdio>
#include <utility>

template <typename F>
class ScopeGuard {
public:
    explicit ScopeGuard(F f) : f_(std::move(f)) {}
    ~ScopeGuard() { if (active_) f_(); }
    void dismiss() noexcept { active_ = false; }

    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;
private:
    F f_;
    bool active_ = true;
};

int main() {
    ScopeGuard a{[] { std::puts("release a"); }};   // CTAD deduces F
    ScopeGuard b{[] { std::puts("release b"); }};
    ScopeGuard c{[] { std::puts("rollback c"); }};
    c.dismiss();                                    // commit: skip rollback
    std::puts("body done");
}
// prints:
// body done
// release b
// release a
```

reverse order of construction, as [day 06](#day-06) promised. `dismiss` gives you the commit-or-rollback shape: arm a rollback before a multi-step operation and disarm it once the last step succeeds. the library fundamentals TS has `scope_exit`, `scope_fail`, and `scope_success`, but they are not in the C++17 or C++20 standard library, so most codebases carry a guard like this one.

#### in practice

applying a new configuration to a running sensor driver touches several pieces of state, and a half-applied configuration is worse than the old one:

```cpp
void Driver::apply(const Config& next) {
    const Config previous = config_;
    ScopeGuard rollback{[&] { config_ = previous; push_to_hardware(config_); }};

    config_ = next;
    push_to_hardware(config_);   // may throw: device rejected a register write
    restart_streams();           // may throw: stream did not come back
    rollback.dismiss();          // every step succeeded: keep the new config
}
```

the rollback lambda captures by reference, which is safe here because the guard cannot outlive the function's locals. the order of the code now reads like the intent: remember, arm the undo, do the work, commit. note that the rollback itself calls `push_to_hardware`, which can throw; a destructor that throws during unwinding terminates the program, so a production guard would catch and log inside the rollback.

#### watch out for

**an unnamed guard guards nothing.**

```cpp
std::lock_guard<std::mutex>{mtx_};           // BUG: temporary, unlocked at the ;
std::lock_guard<std::mutex> lock{mtx_};      // held until end of scope
```

the first line creates a temporary that dies at the end of the full-expression ([day 06](#day-06)), so the critical section is empty. GCC 12 compiles it without a word under `-Wall -Wextra`. the same applies to `ScopeGuard{...};`. always give guards a name.

#### the takeaway

when cleanup or rollback is needed once, in one place, arm a named scope guard next to the code that creates the need, and dismiss it at the point of commit.

#### optional challenge

a function locks a mutex with `std::lock_guard<std::mutex> lock{m};` and then arms `ScopeGuard g{[&] { log_state(); }};`, where `log_state()` reads data protected by `m`. when the function returns, is the data still protected while `log_state()` runs?

<details>
<summary>answer</summary>

yes. automatic objects are destroyed in reverse order of construction, so `g` (constructed second) runs its callable first, while `lock` still holds the mutex, and only then is `lock` destroyed. if the declarations were swapped, the mutex would be released before `log_state()` ran, and the read would race with other threads. with several guards in one scope, the declaration order *is* the cleanup order, so declare them in the order of acquisition.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-18"></a>

### day 18: constructors that establish invariants

**module 3:** resources and the object lifecycle · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** write constructors that make an invalid object impossible, using initializer lists, validation, delegation, and explicit  
**builds on:** [day 16](#day-16) (RAII: let scope do the cleanup), [day 03](#day-03) (the many faces of initialization)

#### the idea

a radar range gate has two numbers and one rule: `0 <= min < max`. a class with a default constructor plus `set_min()` and `set_max()` lets every caller build a gate that breaks the rule, if only between two calls, so every function that receives a gate has to check it again. a constructor exists to make that impossible: if the object exists, its invariant holds.

#### understanding the concept

a constructor's job is to turn raw storage into an object whose invariant holds. [day 16](#day-16) put that in RAII terms: if the object exists, the resource is valid. the mechanics:

- **members are initialized before the body runs.** anything you do not name in the member initializer list is default-initialized (or uses its default member initializer). assigning in the body is therefore a second step: construct, then overwrite. for `const` members, references, and types without a default constructor, there is no second step; the initializer list is the only option.

two conveniences round it out. default member initializers (`float gain_ = 1.0f;`) give every constructor a sensible starting value. delegating constructors (`Window() : Window(256) {}`) let one constructor reuse another's work.

#### in code

**validate once, in the constructor.**

```cpp complete
#include <stdexcept>

class RangeGate {
public:
    RangeGate(double min_m, double max_m) : min_(min_m), max_(max_m) {
        if (!(min_ >= 0.0 && min_ < max_))        // also rejects NaN
            throw std::invalid_argument("RangeGate: need 0 <= min < max");
    }
    bool contains(double r) const { return r >= min_ && r < max_; }
private:
    double min_, max_;
};
```

every member function can now assume the invariant, and there is no `is_valid()` for callers to forget. in a codebase built with exceptions disabled, the same idea becomes a private constructor plus `static std::optional<RangeGate> make(double, double)`: the invariant still lives in one place, and the failure is still impossible to ignore.

**delegating constructors and default member initializers.**

```cpp
class SampleWindow {
public:
    explicit SampleWindow(std::size_t n) : samples_(n) {}
    SampleWindow() : SampleWindow(default_size) {}   // delegating constructor
    std::size_t size() const { return samples_.size(); }
private:
    static constexpr std::size_t default_size = 256;
    std::vector<float> samples_;
    float gain_ = 1.0f;                              // default member initializer
};
```

each constructor states only what differs, and `gain_` has a sensible value however the object was built. notice also what the class does *not* store: a separate `size_` member would have to agree with `samples_.size()` forever. state you can derive is better derived than stored, because duplicated state is an invariant you must maintain by hand ([day 19](#day-19) shows how that particular duplicate goes wrong).

#### in practice

the payoff of validating in constructors grows with the size of the system. parse configuration, network messages, and user input into types like `RangeGate` at the boundary, and the code behind the boundary never re-checks: it cannot receive an invalid gate, because none can be built. invariants enforced by types travel with the data, while checks scattered through call sites erode one refactor at a time.

contrast `struct Detection { double range_m, azimuth_rad, snr_db; };`. any combination of values is a valid detection, so there is nothing to protect: a plain aggregate with public members is the honest design. the Core Guidelines put it as "use `class` if the class has an invariant; use `struct` if the data members can vary independently." wrapping independent fields in getters and setters adds ceremony without adding safety.

#### watch out for

a single-argument constructor that is not `explicit` is also an implicit conversion.

```cpp
struct Timeout {
    Timeout(int ms) : ms(ms) {}            // implicit: int converts to Timeout
    int ms;
};
void arm_watchdog(Timeout t);

arm_watchdog(5);                           // compiles. 5 ms? 5 s? 5 retries?
```

mark it `explicit` and the call site must say `arm_watchdog(Timeout{5})`; copy-list-initialization (`Timeout t = {5};`) is rejected too. make single-argument constructors `explicit` by default, and drop it only when the conversion is genuinely lossless and unsurprising (`std::string` from a string literal, a wider duration from a narrower one). the same applies to conversion operators: write `explicit operator bool()`, which still works in `if (x)` but not in `int n = x;`. better still, for durations, use `std::chrono` and let the type carry the unit.

#### the takeaway

a constructor's job is to establish the invariant: initialize members in the initializer list, validate once, derive what you can instead of storing it, and make single-argument constructors `explicit`.

#### optional challenge

which of the numbered lines compile?

```cpp
struct Meters { explicit Meters(double v) : value(v) {} double value; };
void set_range(Meters m);

set_range(5.0);           // (1)
set_range(Meters{5.0});   // (2)
Meters a = 5.0;           // (3)
Meters b{5.0};            // (4)
Meters c = {5.0};         // (5)
```

<details>
<summary>answer</summary>

only (2) and (4). an `explicit` constructor is not used for implicit conversions, so (1) fails, and copy-initialization (3) does not consider it at all. (5) is copy-list-initialization: overload resolution does find the `explicit` constructor, and choosing it makes the program ill-formed. direct forms (2) and (4) name the type and are fine.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-19"></a>

### day 19: construction and destruction order

**module 3:** resources and the object lifecycle · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** predict the order in which bases and members are built and destroyed, and what that means for virtual calls and constructors that throw  
**builds on:** [day 18](#day-18) (constructors that establish invariants)

#### the idea

a colleague reorders two members in a header to "group related fields". nothing else changes. the next build passes, the unit tests pass, and a sample buffer in the radar front end is now sized from garbage. the constructor's initializer list looked perfectly correct; it was the class declaration that changed.

constructors are where invariants are born, and the rules that govern them (order, partial construction, dispatch) are stricter and less intuitive than they look.

#### understanding the concept

- **order is fixed by the class definition, not by the initializer list.** for a non-virtual hierarchy: direct bases in declaration order, then non-static members in declaration order, then the constructor body. (virtual bases come first of all, constructed by the most derived class.) destruction is the exact reverse. the order you write in the initializer list is ignored, which is why GCC and Clang have `-Wreorder` (enabled by `-Wall`).
- **during construction and destruction, an object is only as derived as the constructor or destructor currently running.** inside `Base::Base()`, the derived members do not exist yet, so a virtual call dispatches to `Base`'s version, not the override. calling a *pure* virtual function this way is undefined behavior.
- **if a constructor throws, the object never existed.** its destructor does not run. every base and member that *was* fully constructed is destroyed, in reverse order. raw resources acquired in the body are on their own.

#### in code

first, the reorder bug and its real fix.

```cpp ub
#include <cstddef>
#include <vector>

class SampleWindow {
public:
    explicit SampleWindow(std::size_t n)
        : size_(n), samples_(size_) {}   // BUG: samples_ is initialized first
private:
    std::vector<float> samples_;          // declared first, so constructed first
    std::size_t size_;
};
```

`samples_(size_)` reads `size_` before it is initialized. that is a read of an indeterminate value: undefined behavior, which in practice means a vector of some arbitrary size, or a `std::length_error`, or a huge allocation. GCC 12 reports it twice under `-Wall`: `-Wreorder` for the list order and `-Wuninitialized` ("member is used uninitialized"). matching the list order to the declaration silences the warnings, but the better fix removes the duplicated state:

the robust fix is the one from [day 18](#day-18): remove `size_` and ask `samples_.size()`, so there is no second value to get out of order.

second, predict the output. this one shows construction order and the "only as derived as the running constructor" rule.

```cpp complete
#include <cstdio>

struct Part {
    const char* n;
    explicit Part(const char* name) : n(name) { std::printf("part %s\n", n); }
    ~Part() { std::printf("~part %s\n", n); }
};

struct Sensor {
    Sensor() { std::puts("Sensor()"); describe(); }
    virtual ~Sensor() { std::puts("~Sensor()"); describe(); }
    virtual void describe() const { std::puts("  I am a Sensor"); }
};

struct Lidar : Sensor {
    Part optics{"optics"};
    Part driver{"driver"};
    Lidar() { std::puts("Lidar()"); describe(); }
    ~Lidar() override { std::puts("~Lidar()"); }
    void describe() const override { std::puts("  I am a Lidar"); }
};

int main() { Lidar l; }
```

```text
Sensor()
  I am a Sensor
part optics
part driver
Lidar()
  I am a Lidar
~Lidar()
~part driver
~part optics
~Sensor()
  I am a Sensor
```

the `Sensor` constructor cannot call `Lidar::describe`: `optics` and `driver` have not been constructed yet, and an override is entitled to use them. the same logic applies in reverse in `~Sensor`. if a base class needs derived-specific setup, it cannot get it through a virtual call in its constructor; use a factory function that constructs and then initializes, or pass the information into the base constructor.

#### in practice

third, partial construction. a class that owns two raw resources leaks the first when acquiring the second fails.

```cpp
class Pipeline {                            // BUG: leaks buf_ if open_device throws
public:
    Pipeline() : buf_(new float[4096]), dev_(open_device()) {}
    ~Pipeline() { close_device(dev_); delete[] buf_; }   // never runs if ctor throws
private:
    float* buf_;
    Device* dev_;
};

class Pipeline2 {                           // fixed: each member cleans up itself
    std::unique_ptr<float[]> buf_ = std::make_unique<float[]>(4096);
    DevicePtr dev_{open_device()};          // unique_ptr with a closing deleter
};
```

in `Pipeline2`, if `open_device` throws, `buf_` is a fully constructed member and is destroyed during unwinding. there is no user-written destructor at all. this is the seed of the rule of zero ([day 25](#day-25)). one aside: `make_unique<float[]>(n)` value-initializes, so it zeroes the buffer; C++20's `std::make_unique_for_overwrite` skips that when you are about to fill it anyway.

#### watch out for

**do not publish `this` from a constructor.** registering the object with a registry, a timer, or another thread inside a base class constructor hands out a pointer to an object that is not finished:

```cpp
struct Sensor {
    explicit Sensor(Scheduler& s) { s.add(this); }   // BUG: derived part not built yet
    virtual void poll() = 0;
    virtual ~Sensor() = default;
};
```

if the scheduler runs on another thread, it can call `poll()` before the derived constructor finishes: during base construction that is a call to a pure virtual function (undefined behavior), and later it races with the rest of construction. register from a factory function after the object is fully constructed, and unregister before destruction begins.

#### the takeaway

members are built in declaration order, the body runs last, and a constructor that throws leaves no object behind. design so that each member cleans up after itself, and those rules work for you instead of against you.

#### optional challenge

the target constructor finishes, and then the delegating constructor's body throws. does `~Probe()` run?

```cpp
struct Probe {
    explicit Probe(int id) { std::printf("Probe(%d)\n", id); }
    Probe() : Probe(0) { throw std::runtime_error("calibration failed"); }
    ~Probe() { std::puts("~Probe()"); }
};
```

<details>
<summary>answer</summary>

yes. once a delegating constructor's target constructor completes, the object counts as constructed, so if the delegating constructor's body then exits via an exception, the destructor is invoked. constructing `Probe p;` inside a `try` prints `Probe(0)`, then `~Probe()`, then whatever the handler prints. this is the one case where a constructor throwing still runs the class's own destructor, and it is why a target constructor should leave the object fully valid: the destructor may have to clean it up.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-20"></a>

### day 20: copying: deep, shallow, and the double free

**module 3:** resources and the object lifecycle · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** explain what a copy must produce, why the generated copy is wrong for a class that owns a resource through a pointer, and write a correct deep copy  
**builds on:** [day 16](#day-16) (RAII: let scope do the cleanup), [day 19](#day-19) (construction and destruction order)

#### the idea

every class you write can be copied unless you say otherwise, because the compiler generates a copy constructor that copies each member in turn. for a `std::vector` member that is exactly right. for a raw pointer to memory the class owns, it produces two objects that both believe they own the same block, and the program finds out when the second destructor runs.

#### understanding the concept

copying gives the destination its own independent value; the source is untouched. for a type that owns a resource through a pointer, that means duplicating the resource (a deep copy). copying just the pointer (a shallow copy) leaves two owners, and [day 16](#day-16)'s destructor will release the same resource twice.

a copy is supposed to produce an *independent value*: after `b = a`, changing `b` must not change `a`, and destroying one must not affect the other. that is what makes value types easy to reason about. the compiler-generated copy constructor and copy assignment copy each base and member with *its* copy operation. for members that are themselves values (`int`, `std::string`, `std::vector`), the result is a correct deep copy for free. for a member that is a handle to something else (a raw pointer, a file descriptor, an index into a global table), copying the handle is a shallow copy, and whether that is right depends entirely on who owns the thing it refers to.

#### in code

the bug that motivates all of this. a class owns a raw buffer and relies on the implicitly generated copy:

```cpp
class Frame {
public:
    explicit Frame(std::size_t n) : size_(n), data_(new float[n]{}) {}
    ~Frame() { delete[] data_; }
private:
    std::size_t size_;
    float* data_;
};

void f() {
    Frame a(1024);
    Frame b = a;        // BUG: implicit copy duplicates the pointer
}                       // double delete[]: undefined behavior
```

the fix spells out what copying means for this resource:

```cpp complete
#include <algorithm>
#include <cstddef>

class Buffer {
public:
    explicit Buffer(std::size_t n) : size_(n), data_(new float[n]{}) {}
    ~Buffer() { delete[] data_; }

    Buffer(const Buffer& o) : size_(o.size_), data_(new float[o.size_]) {
        std::copy(o.data_, o.data_ + size_, data_);           // deep copy
    }
    Buffer& operator=(const Buffer& o) {
        if (this != &o) {
            float* fresh = new float[o.size_];                // may throw: do it first
            std::copy(o.data_, o.data_ + o.size_, fresh);
            delete[] data_;                                   // only now touch *this
            data_ = fresh;
            size_ = o.size_;
        }
        return *this;
    }
private:
    std::size_t size_;
    float* data_;
};
```

the copy assignment allocates before it releases, so if `new` throws, `*this` is unchanged: the strong exception-safety guarantee, which [day 49](#day-49) defines properly. the self-assignment check is only an optimization here; because the data is copied into `fresh` first, `b = b` would still end with an equal value.

#### in practice

value semantics is a design tool, not only a mechanism. a motion planner that takes a *copy* of the world model at the start of each planning cycle can work on it for 50 ms without locks, while the perception thread keeps updating the live model; the copy is the snapshot. the price is the copy itself, which is why the next lessons care so much about avoiding unnecessary ones. the decision for each type you write is therefore explicit: copyable with a deep copy (values like `Buffer`), not copyable at all (unique handles like a serial port), or shared deliberately (a later lesson's `std::shared_ptr`). the generated copy is only correct when every member already made that decision correctly.

#### watch out for

**the "obvious" copy assignment is wrong twice.**

```cpp
Buffer& Buffer::operator=(const Buffer& o) {
    delete[] data_;                          // BUG 1: if o is *this, the source is gone
    size_ = o.size_;
    data_ = new float[size_];                // BUG 2: if this throws, data_ dangles
    std::copy(o.data_, o.data_ + size_, data_);
    return *this;
}
```

for `b = b`, the first line frees the very data it is about to copy. and if `new` throws, the object is left holding a pointer to freed memory, which its destructor will free again. "acquire the new state first, then release the old one" fixes both, which is why the version above is written in that order.

#### the takeaway

a copy must produce an independent value; when a class owns a resource through a handle, the generated memberwise copy creates two owners instead, so either write a deep copy or forbid copying.

#### optional challenge

which of these types can safely use the compiler-generated copy constructor?

```cpp
struct A { std::vector<double> samples; };
struct B { double* samples; ~B() { delete[] samples; } };
struct C { const Config* config; };        // points to a config owned elsewhere
struct D { std::FILE* log; ~D() { std::fclose(log); } };
```

<details>
<summary>answer</summary>

`A` is safe: `std::vector` deep-copies itself. `C` is safe as long as the pointer is genuinely non-owning, since two objects observing the same config is the intended meaning. `B` and `D` are not: each copy would share the handle, and both destructors would release it (a double `delete[]` and a double `fclose`). `B` needs a deep copy or, better, a `std::vector<double>` member; `D` should be non-copyable, since duplicating an open file has no sensible meaning.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-21"></a>

### day 21: moving: transferring resources instead of copying them

**module 3:** resources and the object lifecycle · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** implement move operations, explain why `std::move` is only a cast, and state what a moved-from object promises  
**builds on:** [day 20](#day-20) (copying: deep, shallow, and the double free), [day 11](#day-11) (value categories without the headache)

#### the idea

`std::move` does not move anything. it compiles to no instructions at all. whether a move happens, and what it costs, is decided entirely by which constructor or assignment operator overload resolution picks afterwards, and that is code you (or the compiler) wrote.

once you see moves as "an overload that is allowed to steal, selected by value category", the surprising cases stop being surprising: the `std::move` that copies, the vector that copies when you expected moves, and the `return std::move(x)` that makes code slower.

#### understanding the concept

moving gives the destination the source's value and permits the source to be left in a cheaper, emptier state. for a pointer-owning type that means taking the pointer and nulling the source: O(1), no allocation, usually no way to fail.

the selection is plain overload resolution on [day 11](#day-11)'s value categories. a `T&&` parameter binds to rvalues (prvalues and xvalues); a `const T&` binds to anything. given both, an rvalue argument prefers `T&&`. and `std::move` is just a cast that turns an lvalue into an xvalue:

```cpp
template <typename T>
constexpr std::remove_reference_t<T>&& move(T&& t) noexcept {
    return static_cast<std::remove_reference_t<T>&&>(t);
}
```

what state does the source end up in? for standard library types the rule is "valid but unspecified": the object still satisfies its invariants, so you can destroy it, assign to it, or call functions without preconditions (`size()`, `clear()`), but you must not assume a particular value. a moved-from `std::vector` is empty on every mainstream implementation, but that is not a guarantee you should build on. for your own types, the moved-from state is part of your contract: decide it and document it.

#### in code

adding move operations to the `Buffer` from [day 20](#day-20):

```cpp complete
#include <cstddef>
#include <utility>

class Buffer {
public:
    // constructor, destructor, and copy operations as before
    Buffer(Buffer&& o) noexcept                               // steal, leave o empty
        : size_(std::exchange(o.size_, 0)), data_(std::exchange(o.data_, nullptr)) {}
    Buffer& operator=(Buffer&& o) noexcept {
        if (this != &o) {                                     // survive b = std::move(b)
            delete[] data_;
            size_ = std::exchange(o.size_, 0);
            data_ = std::exchange(o.data_, nullptr);
        }
        return *this;
    }

    std::size_t size() const noexcept { return size_; }       // moved-from: size() == 0
private:
    std::size_t size_;
    float* data_;
};
```

the move constructor steals the pointer and leaves the source empty, so the source's destructor has nothing to free. the move assignment must check for self-assignment: without the check, `b = std::move(b)` would delete the buffer and then adopt the dangling pointer. `std::exchange` keeps "take the value, leave a replacement" on one line, which makes the moved-from contract visible: after a move, `size()` is 0.

that is a lot of code for one pointer, and it is easy to get subtly wrong. [day 25](#day-25) shows how to make almost all of it disappear.

#### in practice

a radar processing chain passes large frames between stages. a stage that keeps what it receives takes the frame by value (a "sink" parameter) and moves it into place:

```cpp
class Tracker {
public:
    void submit(RangeDopplerFrame frame) { pending_.push_back(std::move(frame)); }
private:
    std::vector<RangeDopplerFrame> pending_;
};

RangeDopplerFrame acquire(Receiver& rx) {
    RangeDopplerFrame f = rx.read_frame();
    apply_window(f);
    return f;                        // not std::move(f)
}

void loop(Receiver& rx, Tracker& tracker) {
    RangeDopplerFrame frame = acquire(rx);
    tracker.submit(std::move(frame));  // caller opts in to giving it away
    frame = acquire(rx);               // assigning to a moved-from object is fine
}
```

the signature tells the story: a by-value parameter, a caller that writes `std::move` when it is done with the object, and a copy only when the caller explicitly keeps one. inside `acquire`, `return f;` is deliberately not `return std::move(f);`, for the reasons in [day 12](#day-12).

#### watch out for

**`std::move` on a `const` object copies, silently.**

```cpp
const std::string config = load_config();
std::string owned = std::move(config);   // copies: const std::string&& binds to const&
```

`std::move(config)` produces `const std::string&&`. the move constructor wants `std::string&&`, which cannot bind to a const object, so overload resolution falls back to the copy constructor. no warning, no error, just a copy. the same applies to `const` data members: a class with a `const std::vector` member cannot be moved efficiently, because that member is copied every time. declare locals `const` freely, but not ones you intend to move from, and think twice about `const` members in types that will be moved.

**use after move is legal and still a bug.** reading `frame.size()` after `submit(std::move(frame))` is well-defined for a standard type and almost always a logic error. `clang-tidy`'s `bugprone-use-after-move` check finds most of these.

#### the takeaway

`std::move` only grants permission; the move constructor does the work, and the moved-from object is valid but promises nothing more than its type's contract says.

#### optional challenge

`Buffer`'s copy assignment uses `if (this != &o)`. is the check required for correctness, or only an optimization? what about the move assignment?

<details>
<summary>answer</summary>

for the copy assignment it is only an optimization. because it allocates and copies into `fresh` before deleting the old buffer, self-assignment copies the data into a new block, frees the old one, and ends up with an equal value. the check just skips a pointless allocation.

for the move assignment it is required for correctness as written. without it, `b = std::move(b)` runs `delete[] data_`, and then `data_ = std::exchange(o.data_, nullptr)` reads the freed pointer out of the same object (briefly setting it to null) and stores it straight back. `b` now holds a dangling pointer with its old size, and its destructor will `delete[]` the block a second time: undefined behavior. self-move is rare in direct code but appears through aliasing: `std::swap(x, x)` performs `x = std::move(x)` internally, and so does `v[i] = std::move(v[j])` when `i == j`.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-22"></a>

### day 22: review: resources and the object lifecycle

**module 3:** resources and the object lifecycle · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** consolidate RAII, scope guards, constructors, construction order, copying, and moving  
**covers:** [day 16](#day-16) to [day 21](#day-21)

#### recap

| lesson | key idea |
|---|---|
| [day 16](#day-16) | tie a resource to an object: acquire in the constructor, release in a destructor that never throws, and every exit path that unwinds cleans up. |
| [day 17](#day-17) | for one-off cleanup or rollback, arm a named guard and dismiss it at the point of commit. |
| [day 18](#day-18) | a constructor establishes the invariant: initializer lists, validation once, derived state not stored, `explicit` single-argument constructors. |
| [day 19](#day-19) | bases, then members in declaration order, then the body; destruction reverses it, and a constructor that throws leaves no object. |
| [day 20](#day-20) | a copy must be an independent value; the generated memberwise copy is wrong for a class that owns through a raw handle. |
| [day 21](#day-21) | `std::move` is a cast; the move constructor transfers the resource and leaves a valid, documented moved-from state. |

the thread through the module: **an object's lifetime is a tool**. constructors, destructors, copies, and moves are where a class decides what it owns, and the language runs that code at precisely defined moments.

#### review questions

1. which ways of leaving a scope run the destructors of its automatic objects, and which do not? why do long-running services catch exceptions at the top of every thread function?
2. a class has members `A a; B b; C c;` in that order, and its constructor's initializer list names them as `c(...), a(...), b(...)`. `B`'s constructor throws. which constructors and destructors run?
3. after `std::string b = std::move(a);`, which of these are fine: `a.size()`, `a.clear()`, `a = "x"`, `assert(a.empty())`, `a.front()`?
4. why does a correct copy assignment allocate the new buffer *before* releasing the old one? name the two failures the opposite order causes.
5. from [day 08](#day-08): is this safe? `const std::string& name = load_config().name();` where `Config::name()` returns `const std::string&` to a member.

#### mini exercise

this class has four bugs from this module. find them, then fix the class so it declares no destructor at all.

```cpp complete
#include <cstdio>

class Recorder {
public:
    Recorder(const char* path, std::size_t n)
        : count_(n), samples_(new double[count_]), file_(std::fopen(path, "w")) {}
    ~Recorder() { std::fclose(file_); delete[] samples_; }
private:
    std::FILE* file_;
    double* samples_;
    std::size_t count_;
};
```

#### answers

<details>
<summary>answer 1: which exits run destructors</summary>

normal fall-through, `return`, `break`, `continue`, `goto` out of a block, and an exception propagating to a matching handler all run them. `std::exit` runs static destructors but not the ones on the stack; `std::abort`, `std::_Exit`, crashes, and `kill -9` run nothing. an exception that is never caught calls `std::terminate`, and whether the stack is unwound first is implementation-defined (GCC and Clang typically do not unwind). catching at the top of `main` and of every thread function guarantees that unwinding, and therefore every RAII cleanup, actually happens.

</details>

<details>
<summary>answer 2: partial construction</summary>

the initializer list order is ignored: members are built in declaration order. `A` is constructed, then `B`'s constructor throws, so `C` is never constructed. the fully constructed `a` is destroyed during unwinding; the class's own destructor does not run, because the object never existed. any raw resource acquired in the constructor body would leak, which is why each member should clean up after itself.

</details>

<details>
<summary>answer 3: using a moved-from string</summary>

`a.size()`, `a.clear()`, and `a = "x"` are fine: they have no preconditions, and a moved-from standard type is valid but unspecified. `assert(a.empty())` compiles and will probably pass on your implementation, but nothing guarantees it, so it encodes a false assumption. `a.front()` has a precondition (`!a.empty()`); calling it on an empty string is undefined behavior, so it is only safe after you check. (`a[0]`, by contrast, is always valid on a `std::string`: at `size() == 0` it refers to the terminating null.) treat a moved-from object as "assign or destroy" unless its type documents more.

</details>

<details>
<summary>answer 4: acquire before release</summary>

if the old buffer is released first, self-assignment (`b = b`) frees the very data it is about to copy, and an exception from the allocation leaves the object holding a dangling pointer that its destructor frees a second time. allocating and copying into a fresh buffer first, then swapping it in, leaves `*this` untouched if anything throws (the strong guarantee) and makes self-assignment harmless.

</details>

<details>
<summary>answer 5: lifetime extension through a member function</summary>

not safe: `name` dangles. lifetime extension ([day 08](#day-08)) applies only when a reference binds directly to a temporary. here it binds to whatever `name()` returns, a reference into the temporary `Config`, and that temporary is destroyed at the end of the full-expression. using `name` afterwards is undefined behavior. fix: copy (`std::string name = load_config().name();`) or keep the `Config` alive in a named variable.

</details>

<details>
<summary>mini exercise answer</summary>

- **construction order:** members are initialized in declaration order: `file_`, then `samples_`, then `count_`. `samples_(new double[count_])` reads `count_` before it is initialized, which is undefined behavior.
- **unchecked open:** if `fopen` fails, `file_` is null and the destructor calls `fclose(nullptr)`, which is undefined behavior.
- **partial construction:** `file_` is opened first; if `new double[...]` then throws, the destructor never runs and the file leaks.
- **copying:** the generated copy constructor copies both raw pointers, so two objects close the same file and free the same buffer.

```cpp complete
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <vector>

struct FileCloser {
    void operator()(std::FILE* f) const noexcept { std::fclose(f); }
};

class Recorder {                                  // no destructor, no copy, safe moves
public:
    Recorder(const char* path, std::size_t n) : file_(std::fopen(path, "w")), samples_(n) {
        if (!file_) throw std::runtime_error("cannot open recording");
    }
private:
    std::unique_ptr<std::FILE, FileCloser> file_;
    std::vector<double> samples_;                 // knows its own size
};
```

each member now cleans up after itself, so a throw at any point releases exactly what was acquired, copying is implicitly deleted (a `unique_ptr` member is move-only), and the count is no longer stored twice.

</details>

#### connections

the previous modules supplied the mechanics this one relied on: deterministic destruction from [day 06](#day-06), value categories from [day 11](#day-11), and undefined behavior from [day 13](#day-13), which is what every double free and dangling handle above really is. the next module finishes the ownership story: when moves are trusted ([day 23](#day-23)), which special members the compiler writes ([day 24](#day-24)), how to need none of them ([day 25](#day-25)), and how smart pointers write ownership into types.

[back to the curriculum map](#curriculum)

---

<a id="module-ownership"></a>

## module 4: moves and ownership

when moves are trusted, which special members the compiler writes, the rule of zero, and ownership written into types.

<a id="day-23"></a>

### day 23: noexcept moves and the strong guarantee

**module 4:** moves and ownership · **reading time:** about 5 minutes · **standard:** C++17  
**objective:** explain why containers copy instead of moving when a move constructor may throw, and make move operations noexcept correctly  
**builds on:** [day 21](#day-21) (moving: transferring resources instead of copying them)

#### the idea

a `std::vector<Track>` grows past its capacity and reallocates. `Track` has a perfectly good move constructor, and the vector copies every element anyway. nothing is broken; the vector is keeping a promise you probably did not know it made, and one missing keyword on your move constructor decides which way it keeps it.

#### understanding the concept

when `push_back` needs more room, the vector allocates a new block, transfers the old elements into it, and frees the old block. the standard promises the **strong guarantee** for this: if an exception escapes, the vector is unchanged. with copies that is easy, because the originals are untouched until the end. with moves it is not: if the fifth move throws, the first four elements have already been gutted, and there is no reliable way to move them back.

so the vector uses `std::move_if_noexcept`: it moves elements only if the move constructor is declared `noexcept`, and otherwise copies them. (if the type cannot be copied at all, it moves anyway and the guarantee is weakened.) `noexcept` is part of a function's type-level contract: it is visible to code like this at compile time, through traits such as `std::is_nothrow_move_constructible_v<T>`. if a `noexcept` function does throw, the exception does not propagate: `std::terminate` is called.

#### in code

now predict the output. `Track` has a hand-written move constructor that is not `noexcept`:

```cpp complete
#include <cstdio>
#include <string>
#include <vector>

struct Track {
    std::string id;
    explicit Track(std::string s) : id(std::move(s)) {}
    Track(const Track& o) : id(o.id) { std::puts("copy"); }
    Track(Track&& o) : id(std::move(o.id)) { std::puts("move"); }   // not noexcept
};

int main() {
    std::vector<Track> tracks;
    tracks.reserve(1);
    tracks.emplace_back("T-001");
    tracks.emplace_back("T-002");   // exceeds capacity: reallocates
}
```

it prints `copy`. when `push_back` or `emplace_back` reallocates, `std::vector` promises the strong guarantee: if an exception escapes, the vector is unchanged. moving the old elements to the new block would gut them, so a move that throws halfway through leaves no way back. the vector therefore uses `std::move_if_noexcept`: it moves only if the move constructor is `noexcept` (or the type cannot be copied at all, in which case the effects of a throwing move are unspecified). add `noexcept` to the move constructor and the program prints `move`.

implicitly generated and `= default` move constructors are `noexcept` automatically when every member's move is. the trap is the hand-written one.

#### in practice

a move constructor that only transfers pointers and integers cannot fail, so it should say so. the same holds for move assignment and `swap`. in practice the rule is simple: let the compiler generate moves whenever you can (they are `noexcept` exactly when every member's move is), and when you write them by hand, add `noexcept` and keep the bodies to operations that cannot throw. you can lock the property in where it matters:

```cpp
#include <type_traits>

static_assert(std::is_nothrow_move_constructible_v<Track>,
              "Track is stored in vectors; a throwing move would make them copy");
```

that assertion turns "someone added a `std::string` member with a throwing constructor call to the move constructor" from a silent slowdown into a build error.

#### watch out for

**do not promise what a member cannot keep.** a hand-written move constructor that calls something that can throw, such as allocating a fresh buffer for the source to keep, must not be marked `noexcept`, because a throw would terminate the program. moving a member that is itself not nothrow-movable has the same problem. for class templates, write the condition instead of guessing: `noexcept(std::is_nothrow_move_constructible_v<T>)` makes the wrapper exactly as `noexcept` as what it wraps.

#### the takeaway

containers trust a move only if it is `noexcept`; let the compiler generate moves when you can, mark hand-written ones `noexcept`, and assert the property for types that live in containers.

#### optional challenge

`Track` has a `std::string id` and a hand-written move constructor that is correctly `noexcept`. someone adds `~Track() { log("released"); }` to it. does a `std::vector<Track>` still move on reallocation?

<details>
<summary>answer</summary>

yes, in this case. the hand-written move constructor is still declared, and adding a destructor does not remove a user-declared move constructor, so the vector keeps moving. the trap from [day 24](#day-24) applies only to *implicit* moves: had `Track` relied on the compiler-generated move constructor, declaring the destructor would have stopped it from being generated, and reallocation would silently fall back to copying.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-24"></a>

### day 24: the special member functions and when the compiler writes them

**module 4:** moves and ownership · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** predict which special members a class gets, and recognize when a declaration silently turns moves into copies  
**builds on:** [day 23](#day-23) (noexcept moves and the strong guarantee)

#### the idea

for every class you define, the compiler is prepared to write up to six member functions on your behalf. which ones it writes, and when it quietly stops, follows a short set of rules. they are worth learning once, because the most expensive mistake they allow (a move that has silently become a copy) produces no error, no warning, and correct output.

#### understanding the concept

there are six special member functions: the default constructor, the destructor, the copy constructor, copy assignment, the move constructor, and move assignment. the compiler declares the ones you do not, following rules that are worth having in front of you once:

| you declare | default ctor | destructor | copy ctor | copy assign | move ctor | move assign |
|---|---|---|---|---|---|---|
| nothing | defaulted | defaulted | defaulted | defaulted | defaulted | defaulted |
| another constructor | not declared | defaulted | defaulted | defaulted | defaulted | defaulted |
| destructor | defaulted | yours | defaulted (deprecated) | defaulted (deprecated) | not declared | not declared |
| copy ctor | not declared | defaulted | yours | defaulted (deprecated) | not declared | not declared |
| copy assign | defaulted | defaulted | defaulted (deprecated) | yours | not declared | not declared |
| move ctor | not declared | defaulted | deleted | deleted | yours | not declared |
| move assign | defaulted | defaulted | deleted | deleted | not declared | yours |

three things in that table matter in practice.

- **"declare" includes `= default` and `= delete`.** writing `~T() = default;` counts as declaring a destructor and suppresses the implicit moves.
- **"not declared" is not "deleted".** if there is no move constructor, an rvalue argument simply binds to the copy constructor's `const T&` parameter. moves silently become copies, and `std::is_move_constructible_v<T>` still reports `true`.
- **"defaulted" can still mean deleted.** a defaulted copy constructor is defined as deleted if some member cannot be copied. a class with a `std::unique_ptr` member is move-only without you writing anything.

#### in code

the type traits make the rules visible. a destructor written for logging removes the implicit move constructor, and the "move" that remains is the copy constructor:

```cpp complete
#include <type_traits>
#include <vector>

struct Plain  { std::vector<int> v; };
struct Logged { std::vector<int> v; ~Logged() {} };

static_assert(std::is_nothrow_move_constructible_v<Plain>);    // a real, noexcept move
static_assert(std::is_move_constructible_v<Logged>);           // true, but it is a copy
static_assert(!std::is_nothrow_move_constructible_v<Logged>);  // copying a vector can throw
```

`std::is_move_constructible_v` only asks whether an rvalue can construct the type, and the copy constructor's `const T&` parameter accepts one. the `nothrow` trait gives the game away, and it is exactly the property `std::vector` checks before deciding to move ([day 23](#day-23)).

#### in practice

the same rule bites polymorphic bases. `virtual ~Sensor() = default;` is a declared destructor, so `Sensor` and every class derived from it lose their implicit moves unless they declare them. the usual fix is to declare all five as `= default` in the base (making the copy operations `protected` if you also want to prevent slicing, which [day 31](#day-31) covers).

in the base class, that looks like this:

```cpp complete
class Sensor {
public:
    virtual ~Sensor() = default;
    Sensor() = default;
    Sensor(Sensor&&) = default;
    Sensor& operator=(Sensor&&) = default;
protected:
    Sensor(const Sensor&) = default;              // derived classes may copy their base part
    Sensor& operator=(const Sensor&) = default;   // but outside code cannot slice
};
```

writing all five explicitly costs five lines and documents a decision; leaving them implicit after declaring the destructor costs every derived class its moves.

#### watch out for

a destructor added "just for debugging" silently turns moves into copies:

```cpp complete
#include <cstdio>
#include <utility>
#include <vector>

struct Snapshot {
    std::vector<double> samples;
    ~Snapshot() { std::puts("snapshot released"); }   // added later
};

int main() {
    Snapshot a{std::vector<double>(100'000)};
    Snapshot b = std::move(a);                        // copy constructor!
    std::printf("%zu\n", a.samples.size());           // prints: 100000
}
```

remove the destructor and the same program prints `0` on mainstream implementations (the vector was moved; strictly, its moved-from state is unspecified). nothing warns. GCC and Clang have `-Wdeprecated-copy-dtor`, but it is not enabled by `-Wall` or `-Wextra`. Clang-tidy's `cppcoreguidelines-special-member-functions` catches the pattern.

#### the takeaway

declaring any of the destructor, copy, or move operations (even as `= default`) changes what else the compiler generates; when you declare one, decide about all five.

#### optional challenge

which special members does `Config` have, and which of these lines compile?

```cpp
struct Config {
    std::string name;
    std::unique_ptr<Parser> parser;
    explicit Config(std::string n);
};

Config a{"lidar"};                 // (1)
Config b = a;                      // (2)
Config c = std::move(a);           // (3)
std::vector<Config> v;
v.push_back(Config{"radar"});      // (4)
Config d;                          // (5)
```

<details>
<summary>answer</summary>

the user-declared constructor suppresses the default constructor. the destructor, copy operations, and move operations are all implicitly declared as defaulted, but the copy constructor and copy assignment are defined as deleted because `std::unique_ptr` is not copyable. the move operations work and are `noexcept`, since both members' moves are.

so (1) compiles, (2) fails (deleted copy constructor), (3) compiles, (4) compiles and the vector will move on reallocation, and (5) fails (no default constructor). `Config` is move-only without a single line of special-member code, which is exactly the behavior you want for something that owns a parser.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-25"></a>

### day 25: the rule of zero

**module 4:** moves and ownership · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** design classes that need no hand-written special members by composing types that manage themselves  
**builds on:** [day 24](#day-24) (the special member functions and when the compiler writes them)

#### the idea

[day 21](#day-21)'s `Buffer` needed about 35 lines of copy and move code to manage one pointer correctly, and every line was a chance to get it wrong. most classes in a healthy codebase have none of those lines. the rule of zero is not "be lazy"; it is a claim about design: managing a resource is one job, and a class that does that job should do nothing else.

#### understanding the concept

from those rules come three guidelines:

- **rule of three** (C++98): if you need a custom destructor, copy constructor, or copy assignment, you almost certainly need all three, because the custom one exists to manage a resource the defaults would mishandle.
- **rule of five** (C++11): same, plus the two move operations, since declaring any of the three suppresses the implicit moves.
- **rule of zero**: write classes that need none of them, by composing members that already manage themselves: `std::vector`, `std::string`, `std::unique_ptr`, and the few RAII types of your own.

#### in code

[day 21](#day-21)'s `Buffer`, refactored to the rule of zero:

```cpp complete
#include <cstddef>
#include <vector>

class Buffer {
public:
    explicit Buffer(std::size_t n) : data_(n) {}
    std::size_t size() const noexcept { return data_.size(); }
    float* data() noexcept { return data_.data(); }
    const float* data() const noexcept { return data_.data(); }
private:
    std::vector<float> data_;
};
```

copy is a deep copy, move steals the buffer, destruction frees it, and the move constructor is `noexcept` because `std::vector`'s is, so the reallocation trap from [day 23](#day-23) cannot happen. copy assignment is arguably better than the hand-written one, since `std::vector` can reuse existing capacity instead of always allocating.

one thing did change: the moved-from contract. the hand-written `Buffer` promised `size() == 0` after a move. this one inherits `std::vector`'s "valid but unspecified". if callers relied on the old promise, that is an API change, and it deserves a line in the review. if you want a move-only buffer instead, swap the member for `std::unique_ptr<float[]>` plus a size: copying is then implicitly deleted, and the class still declares no special members.

#### in practice

a lidar driver owns a file descriptor, a scratch buffer, a name, and a parser. only one of those is not already managed by a standard type, so only one class needs special members:

```cpp
#include <unistd.h>
#include <utility>

class UniqueFd {                       // the one class that manages a resource
public:
    UniqueFd() = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(UniqueFd&& o) noexcept : fd_(std::exchange(o.fd_, -1)) {}
    UniqueFd& operator=(UniqueFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = std::exchange(o.fd_, -1);
        }
        return *this;
    }
    UniqueFd(const UniqueFd&) = delete;             // already implied; say it anyway
    UniqueFd& operator=(const UniqueFd&) = delete;

    int get() const noexcept { return fd_; }
private:
    int fd_ = -1;
};

class LidarDriver {                    // rule of zero: move-only, correct, no special members
public:
    LidarDriver(std::string name, UniqueFd fd)
        : name_(std::move(name)), fd_(std::move(fd)) {}
private:
    std::string name_;
    UniqueFd fd_;
    std::vector<Point> scratch_;
    std::unique_ptr<PacketParser> parser_;
};
```

`std::unique_ptr` cannot manage a plain `int` handle without contortions (its deleter's `pointer` type must behave like a nullable pointer), so a small handle class is a legitimate place for hand-written members. the point is containment: one 25-line class with special members, tested once, and every class above it composes it and writes none. that is single responsibility applied to resource management, and it scales: a codebase with a handful of handle types and hundreds of rule-of-zero classes has very few places where a leak or double close can hide.

#### watch out for

**`const` and reference members quietly delete assignment.** a rule-of-zero class inherits its members' limitations:

```cpp complete
#include <vector>

struct Track {
    const int id;                    // looks like good hygiene
    std::vector<double> ranges;
};

void sort_by_id(std::vector<Track>& tracks);   // std::sort needs move assignment: does not compile
```

a `const` member cannot be assigned, so `Track` has no copy or move assignment, and anything that reassigns elements (`std::sort`, `std::remove_if`, `tracks[i] = other`) fails to compile. a type meant to behave like a value should keep its members non-`const` and private, and expose them through `const` accessors; the immutability belongs to the interface, not the storage.

#### the takeaway

write the special members in the few classes whose job is to own a resource, and in no others. everywhere else, the best special member function is the one you did not declare.

#### optional challenge

which special members does `LidarDriver` from the practice section have? can it be copied, moved, and stored in a `std::vector` that reallocates efficiently?

<details>
<summary>answer</summary>

it has a user-declared constructor, so no default constructor. the destructor and the move operations are implicitly defaulted, and the moves are `noexcept`, because every member (`std::string`, `UniqueFd`, `std::vector`, `std::unique_ptr`) has a `noexcept` move. the copy operations are implicitly deleted, because `UniqueFd` and `std::unique_ptr` are not copyable. so: not copyable, movable, and a `std::vector<LidarDriver>` moves its elements on reallocation. all of that without declaring a single special member.

</details>

#### going deeper (optional)

##### copy-and-swap

when you do write the special members, copy-and-swap is the classic way to get assignment right with little code:

```cpp complete
#include <algorithm>
#include <cstddef>
#include <utility>

class Buffer5 {                                   // rule of five, by hand
public:
    explicit Buffer5(std::size_t n) : size_(n), data_(new float[n]{}) {}
    ~Buffer5() { delete[] data_; }
    Buffer5(const Buffer5& o) : size_(o.size_), data_(new float[o.size_]) {
        std::copy(o.data_, o.data_ + size_, data_);
    }
    Buffer5(Buffer5&& o) noexcept
        : size_(std::exchange(o.size_, 0)), data_(std::exchange(o.data_, nullptr)) {}

    Buffer5& operator=(Buffer5 other) noexcept {  // one operator for copy and move
        swap(*this, other);
        return *this;
    }                                             // other's destructor frees the old buffer
    friend void swap(Buffer5& a, Buffer5& b) noexcept {
        std::swap(a.size_, b.size_);
        std::swap(a.data_, b.data_);
    }
private:
    std::size_t size_;
    float* data_;
};
```

the parameter is taken by value, so the copy (from an lvalue) or move (from an rvalue) happens at the call site, before the function body runs. if the copy throws, `*this` was never touched: the strong guarantee for free, self-assignment handled for free. the cost is real, though. copy assignment always allocates, even when the target already has enough room, and move assignment does a move plus a swap instead of a direct steal. that is why the standard containers do not use it. it is a good default for types where assignment is rare and correctness matters more than the last allocation.

[back to the curriculum map](#curriculum)

---

<a id="day-26"></a>

### day 26: exclusive ownership with `std::unique_ptr`

**module 4:** moves and ownership · **reading time:** about 5 minutes · **standard:** C++17  
**objective:** own heap objects with `std::unique_ptr`, transfer ownership with `std::move`, and know what it costs  
**builds on:** [day 25](#day-25) (the rule of zero)

#### the idea

`Detector* make_detector(const Config&);` hands the caller a heap object and an obligation: call `delete` exactly once, on every path, including the ones where an exception flies past. that is the same promise-everyone-must-keep that [day 16](#day-16) replaced for files. `std::unique_ptr` is RAII for heap objects, and in the common case it costs exactly as much as the raw pointer it replaces.

#### understanding the concept

**`std::unique_ptr<T>`** is sole ownership: move-only ([day 25](#day-25)), deletes the object in its destructor. with the default deleter, or any empty function-object deleter, it is typically the same size as a raw pointer, and `get()` and `operator->` compile down to the raw pointer. a stateful deleter costs its size: a function-pointer deleter typically doubles the `unique_ptr`. create one with `std::make_unique<T>(args...)` (C++14). before C++17, `make_unique` also prevented a leak in `f(std::unique_ptr<A>(new A), g())`, because the compiler could run `new A`, then `g()`, before constructing the `unique_ptr`. C++17 forbids that interleaving (each argument is fully evaluated before the next one starts), but `make_unique` is still the better spelling: no naked `new`, and the type is written once.

a `unique_ptr` converts to a `unique_ptr` of a base class, as long as the base has a virtual destructor, so a factory can return the concrete type and the caller can store it as the interface. `get()` lends the raw pointer without giving up ownership; `reset()` destroys the current object (and optionally adopts a new one); `release()` gives up ownership and returns the raw pointer, after which deleting it is your job again.

#### in code

```cpp complete
#include <memory>
#include <vector>

struct Detector { virtual ~Detector() = default; virtual void run() = 0; };
struct CfarDetector : Detector { void run() override {} };

std::unique_ptr<Detector> make_detector() {
    return std::make_unique<CfarDetector>();    // converts to unique_ptr<Detector>
}

int main() {
    std::vector<std::unique_ptr<Detector>> stages;
    auto d = make_detector();
    stages.push_back(std::move(d));             // ownership moves; d is now empty
    // stages.push_back(d);                     // error: unique_ptr cannot be copied
    for (auto& s : stages) s->run();
}   // the vector's destructor deletes every detector exactly once
```

the commented-out line is the point of the type: the compiler refuses to create a second owner. ownership can only *move*, and every move is visible in the code as a `std::move`.

for arrays, `std::unique_ptr<float[]>` calls `delete[]` and offers `operator[]`; `std::make_unique<float[]>(n)` value-initializes the elements. in most code a `std::vector<float>` is still the better owner of a buffer, because it also knows its size.

#### in practice

processing pipelines and plugin systems are full of objects with one obvious owner and a polymorphic type: stages built by a factory from a configuration file, drivers selected at startup, filters chosen per sensor. `std::vector<std::unique_ptr<Stage>>` holds them with no ceremony: the pipeline owns its stages, moving the pipeline moves the pointers (not the stages), and tearing it down deletes everything in reverse order of insertion. code that only *uses* a stage takes `Stage&`; nothing outside the pipeline ever sees a `unique_ptr`, which keeps the ownership decision in exactly one class.

#### watch out for

**`release()` is not `reset()`.**

```cpp
std::unique_ptr<Frame> f = acquire();
f.release();    // BUG: gives up ownership and discards the pointer: a leak
f.reset();      // what was meant: destroy the frame, leave f empty
```

`release()` exists for handing ownership to code that takes a raw owning pointer (typically a C API or an old interface). call it only as part of that hand-off, in the same expression, and never just to "clear" the pointer.

#### the takeaway

`std::unique_ptr` is sole ownership at the price of a raw pointer: create it with `make_unique`, transfer it with `std::move`, lend it with `*p` or `get()`, and let its destructor do the `delete`.

#### optional challenge

which lines compile, and which compile but are still wrong?

```cpp
auto a = std::make_unique<int>(1);
auto b = a;                          // (1)
auto c = std::move(a);               // (2)
std::unique_ptr<int> d{c.get()};     // (3)
```

<details>
<summary>answer</summary>

(1) does not compile: the copy constructor is deleted. (2) compiles and leaves `a` empty. (3) compiles and is a bug: `c` and `d` both own the same `int`, and both destructors delete it, which is undefined behavior. constructing a `unique_ptr` from a raw pointer means "I am the owner now", so only do it with a pointer nobody else owns, ideally straight from `new` or a C API that transfers ownership.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-27"></a>

### day 27: shared ownership with `std::shared_ptr` and `std::weak_ptr`

**module 4:** moves and ownership · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** use shared_ptr only for genuinely shared ownership, break cycles with weak_ptr, and know exactly what is and is not thread-safe  
**builds on:** [day 26](#day-26) (exclusive ownership with `std::unique_ptr`)

#### the idea

a map is loaded once and used by the planner, the visualizer, and a logging thread. any of them may be the last to finish with it, and the map must be freed exactly when that happens, not before and not never. when no single object can be the owner, ownership has to be counted. `std::shared_ptr` counts it for you, and in doing so introduces costs and failure modes that `std::unique_ptr` does not have.

#### understanding the concept

**`std::shared_ptr<T>`** is shared ownership via a reference count. the count lives in a separately allocated *control block* along with a weak count, the deleter, and the allocator. a `shared_ptr` object is typically two pointers (object and control block). copying it increments the strong count; the last owner to go away destroys the object. the counts are updated atomically, so different `shared_ptr` objects that share one control block may be copied and destroyed on different threads. that is the only thread-safety it gives you; more in "watch out for".

`std::make_shared<T>(args...)` puts the object and the control block in one allocation instead of two. the catch: the memory can only be freed when both counts reach zero, so a long-lived `weak_ptr` keeps a large object's storage allocated after its destructor has run. `make_shared` also cannot take a custom deleter.

**`std::weak_ptr<T>`** observes a shared object without owning it. it touches only the weak count. to use the object you call `lock()`, which returns a `shared_ptr` that is empty if the object is gone. that check-and-acquire is atomic, which is why `weak_ptr` has no `get()`.

**`std::enable_shared_from_this<T>`** lets an object that is already owned by a `shared_ptr` produce another `shared_ptr` to itself (`shared_from_this()`), sharing the existing control block. since C++17, calling it on an object no `shared_ptr` owns throws `std::bad_weak_ptr` (it used to be undefined behavior).

#### in code

shared ownership in both directions is a leak:

```cpp complete norun
#include <cstdio>
#include <memory>
#include <vector>

struct Joint;
struct Robot {
    std::vector<std::shared_ptr<Joint>> joints;
    ~Robot() { std::puts("~Robot"); }
};
struct Joint {
    std::shared_ptr<Robot> owner;          // BUG: cycle: Robot -> Joint -> Robot
    ~Joint() { std::puts("~Joint"); }
};

int main() {
    auto robot = std::make_shared<Robot>();
    auto j = std::make_shared<Joint>();
    j->owner = robot;
    robot->joints.push_back(j);
}   // prints nothing: both counts stay at 1, neither destructor runs
```

reference counting cannot collect cycles. each object keeps the other's count above zero, so when `robot` and `j` go out of scope, both objects leak. the fix is to decide which direction owns. a robot owns its joints; a joint merely refers back to its robot:

```cpp
struct Joint {
    std::weak_ptr<Robot> owner;            // back-reference: does not own
    void report() const {
        if (auto r = owner.lock()) { /* use *r */ }   // empty if the robot is gone
    }
    ~Joint() { std::puts("~Joint"); }
};
// now prints: ~Robot, then ~Joint
```

often the even simpler fix is better: if a joint can never outlive its robot, `Robot* owner` (or `Robot&`) states that precisely and costs nothing. `weak_ptr` is for when the referenced object really might disappear first.

#### in practice

a perception stack loads large meshes and maps on demand, and several subsystems may use the same one. you want each loaded once, shared while in use, and released when nobody needs it, without the cache itself keeping everything alive forever. that is exactly what `weak_ptr` expresses:

```cpp
#include <map>
#include <memory>
#include <mutex>
#include <string>

class MeshCache {
public:
    std::shared_ptr<const Mesh> get(const std::string& path) {
        std::lock_guard<std::mutex> lock(mtx_);
        if (auto alive = cache_[path].lock()) return alive;   // still in use somewhere
        auto fresh = std::make_shared<const Mesh>(load_mesh(path));
        cache_[path] = fresh;                                 // observe, do not own
        return fresh;
    }
private:
    std::mutex mtx_;
    std::map<std::string, std::weak_ptr<const Mesh>> cache_;
};
```

two design notes. `shared_ptr<const Mesh>` makes the shared object immutable, which is what makes sharing it across subsystems and threads safe. and `make_shared` is a questionable choice here: an expired entry's `weak_ptr` pins the whole allocation, mesh storage included, until the entry is overwritten or erased. with large objects and long-lived weak references, `std::shared_ptr<const Mesh>(new Mesh(...))` keeps the object and control block separate so the mesh memory goes back as soon as the last user lets go. (a production cache would also prune expired entries.)

#### watch out for

**thread-safe count, not thread-safe object.** two threads may each copy and destroy their own `shared_ptr` to the same object freely. but the pointee gets no protection at all: concurrent writes to `*p` are a data race unless you synchronize them. and one `shared_ptr` *instance* read and assigned by two threads at once is also a data race (undefined behavior); C++20's `std::atomic<std::shared_ptr<T>>` exists for that case.

**one raw pointer, two control blocks.**

```cpp
auto* raw = new Track{};
std::shared_ptr<Track> a(raw);
std::shared_ptr<Track> b(raw);   // BUG: second control block, double delete (UB)
```

each constructor from a raw pointer creates a fresh control block with its own count. the same bug hides in `std::shared_ptr<Session>(this)` inside a member function, which is exactly the problem `enable_shared_from_this` solves. create shared objects with `make_shared` at the point of allocation and never hand raw ownership around.

more broadly, treat widespread `shared_ptr` as a smell. "everything is shared" usually means nobody decided who owns what, and the cost shows up as unclear lifetimes, destructors running on whichever thread happened to drop the last reference, and cycles. most objects have one obvious owner.

#### the takeaway

`shared_ptr` is for ownership that is genuinely shared; its count is thread-safe and its pointee is not, reference cycles leak, and most objects have one owner and should say so with `unique_ptr`.

#### optional challenge

what does this print, and when is the `int`'s memory actually freed?

```cpp
auto a = std::make_shared<int>(7);
std::weak_ptr<int> w = a;
auto b = a;
std::printf("%ld ", a.use_count());
a.reset();
std::printf("%ld %d ", w.use_count(), w.expired());
b.reset();
std::printf("%d\n", w.expired());
```

<details>
<summary>answer</summary>

it prints `2 1 0 1`. after `b = a` there are two owners. `a.reset()` leaves one, so the object is alive (`expired()` is false). `b.reset()` drops the last strong reference: the `int` is destroyed and `w` reports expired.

the memory is not freed at that point. `make_shared` put the `int` and the control block in one allocation, and `w` still needs the control block (it holds the weak count). the block, including the dead `int`'s storage, is released when `w` is destroyed. for an `int` that is irrelevant; for a 200 MB point cloud observed by a long-lived `weak_ptr`, it is the difference between memory coming back now and memory coming back much later.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-28"></a>

### day 28: ownership in function signatures

**module 4:** moves and ownership · **reading time:** about 6 minutes · **standard:** C++17  
**objective:** choose parameter and return types that state whether a function borrows, takes, shares, or creates ownership  
**builds on:** [day 27](#day-27) (shared ownership with `std::shared_ptr` and `std::weak_ptr`), [day 10](#day-10) (const as a contract)

#### the idea

read this signature and tell me who deletes the track:

```cpp
void register_track(Track* t);
```

you cannot. maybe the registry keeps it and deletes it later, maybe it only reads it during the call, maybe it keeps it but expects you to keep it alive. the type says nothing, so the answer lives in a comment, a wiki, or someone's memory. smart pointers are RAII for heap objects, but their bigger contribution is that they turn ownership into part of the type, where the compiler can check it and a reviewer can see it.

#### understanding the concept

the C++ Core Guidelines turn ownership into a small vocabulary of types, and the rule behind it is simple: **a raw pointer or reference never owns**. it borrows, for at most as long as the call (or as long as a documented relationship lasts). everything that transfers or shares ownership says so with a smart pointer:

- **returning ownership:** factories return `std::unique_ptr<T>` (or a value). a caller that wants shared ownership can convert it: a `shared_ptr` constructs from a `unique_ptr&&`.
- **taking ownership:** a sink parameter is `std::unique_ptr<T>` by value. the caller must write `std::move`, so the transfer is visible at the call site.
- **sharing ownership:** `std::shared_ptr<T>` by value, only when the callee keeps a share beyond the call.
- **borrowing:** `T&` or `const T&` when the object must exist, `T*` when "nothing" is allowed. smart pointers in a parameter list for a function that merely uses the object add cost and constrain every caller.

#### in code

ownership written into signatures, following the C++ Core Guidelines:

```cpp complete
#include <memory>

struct Config; struct Map;
struct Detector { virtual ~Detector() = default; virtual void run() = 0; };

std::unique_ptr<Detector> make_detector(const Config& cfg);  // gives you ownership
void install(std::unique_ptr<Detector> d);                   // takes ownership
void share(std::shared_ptr<const Map> m);                    // keeps a share
void inspect(const Detector& d);                             // uses, never owns
void maybe_inspect(const Detector* d);                       // uses; may be null

void setup(const Config& cfg) {
    auto d = make_detector(cfg);
    inspect(*d);                 // borrow: no ownership in the signature
    install(std::move(d));       // transfer: visible at the call site
}
```

| parameter | meaning |
|---|---|
| `T&`, `const T&`, `T*` | borrows for the duration of the call; ownership untouched |
| `std::unique_ptr<T>` by value | sink: the callee now owns it |
| `std::unique_ptr<T>&` | the callee may reseat or reset your pointer (rare) |
| `std::shared_ptr<T>` by value | the callee keeps a share (stores it, or hands it to a thread) |
| `const std::shared_ptr<T>&` | the callee *might* keep a share; otherwise just use `T&` |

the most common mistake in that table is the last row used everywhere. a function that only reads a `Map` should take `const Map&`. taking `shared_ptr` by value costs an atomic increment and decrement per call, and worse, it couples every caller to one particular ownership strategy.

#### in practice

legacy interfaces rarely say who owns what, and changing their types is the cheapest documentation you can add. take `void register_track(Track* t);` from the opening. once you have established (by reading the implementation) that the registry keeps the track and deletes it later, change the signature to `void register_track(std::unique_ptr<Track> t);`. every caller that compiled before now fails to compile until it writes `register_track(std::move(track))` or `register_track(std::make_unique<Track>(...))`, which forces each one to show that it is handing the track over. the compiler does the audit you would otherwise do by reading every call site, and the result stays correct when new callers appear.

#### watch out for

**a borrowed pointer that is quietly stored.** a reference or raw pointer parameter promises "I only use this during the call". storing it breaks the promise without changing the signature:

```cpp
class Monitor {
public:
    void watch(const Detector& d) { watched_ = &d; }   // stores a borrow
    void tick() { if (watched_) report(*watched_); }   // may run after d is gone
private:
    const Detector* watched_ = nullptr;
};
```

if the function keeps the object, the parameter type should say how: a `shared_ptr` if it shares ownership, or a reference plus a documented lifetime rule ("the detector must outlive the monitor") enforced by the code that wires them together. a long-lived raw pointer with no stated lifetime is a dangling pointer waiting for a refactor.

#### the takeaway

default to `unique_ptr` for ownership and plain references for use; reach for `shared_ptr` only when ownership is genuinely shared, and let every signature say which one it is.

#### optional challenge

choose parameter types for each function: (a) logs a detector's name; (b) adds a detector to a registry that keeps it forever; (c) starts a background thread that reads a map for as long as the thread runs; (d) may replace the caller's detector with a recalibrated one.

<details>
<summary>answer</summary>

(a) `const Detector&`: it only reads during the call. (b) `std::unique_ptr<Detector>` by value: a sink, and the call site shows the transfer. (c) `std::shared_ptr<const Map>` by value: the thread keeps a share, so the map cannot disappear underneath it, and `const` makes the concurrent reads safe. (d) `std::unique_ptr<Detector>&`, the rare case where the callee reseats the caller's pointer; returning a new `std::unique_ptr<Detector>` is often clearer.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-29"></a>

### day 29: review: moves and ownership

**module 4:** moves and ownership · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** consolidate noexcept moves, special member generation, the rule of zero, smart pointers, and ownership in interfaces  
**covers:** [day 23](#day-23) to [day 28](#day-28)

#### recap

| lesson | key idea |
|---|---|
| [day 23](#day-23) | containers move elements only if the move constructor is `noexcept`; otherwise they copy to keep the strong guarantee. |
| [day 24](#day-24) | declaring a destructor or copy operation, even as `= default`, suppresses the implicit moves; then moves silently become copies. |
| [day 25](#day-25) | write special members only in the few classes that own a resource; compose everything else from members that manage themselves. |
| [day 26](#day-26) | sole ownership at the cost of a raw pointer; transfers are explicit `std::move`s. |
| [day 27](#day-27) | counted ownership for the genuinely shared case; the count is thread-safe, the pointee is not, and cycles leak. |
| [day 28](#day-28) | raw pointers and references borrow; `unique_ptr` by value takes, `shared_ptr` by value shares. |

the thread through the module: **ownership is a design decision, and C++ lets you write it into types**. once it is in the types, the compiler enforces it, destructors execute it, and reviewers can read it.

#### review questions

1. a class's destructor is declared as `~Telemetry() = default;` and nothing else special is declared. its members are a `std::string` and a `std::vector<Sample>`. when a `std::vector<Telemetry>` reallocates, are the elements moved or copied? why?
2. two threads each hold their own `std::shared_ptr<Stats>` to the same object. one calls `p->add(sample)`, the other `p->reset()`. the reference count is atomic; is this code safe?
3. looking ahead: a plugin interface has virtual functions but a public non-virtual destructor. `std::shared_ptr<Plugin> p = std::make_shared<Logger>(); p.reset();` works correctly. the same code with `std::unique_ptr` is undefined behavior. explain the difference, and why "use `shared_ptr`" is the wrong fix.
4. from [day 12](#day-12): C++17 guarantees elision for prvalues but not for named locals. how does that explain the advice against `return std::move(local);`?

#### mini exercise

this class works in the happy path and has at least four ownership bugs. find them, then rewrite it so it needs no user-declared special members (or, if it needs one, say why and handle the consequence).

```cpp complete
#include <cstdio>
#include <cstring>
#include <stdexcept>

class TelemetryLog {
public:
    TelemetryLog(const char* path, std::size_t capacity)
        : file_(std::fopen(path, "a")), buf_(new char[capacity]), cap_(capacity) {
        if (!file_) throw std::runtime_error("cannot open log");
    }
    ~TelemetryLog() { flush(); std::fclose(file_); delete[] buf_; }

    void write(const char* msg) {
        std::size_t n = std::strlen(msg);
        if (used_ + n > cap_) flush();
        if (n > cap_) { std::fwrite(msg, 1, n, file_); return; }
        std::memcpy(buf_ + used_, msg, n);
        used_ += n;
    }
    void flush() { std::fwrite(buf_, 1, used_, file_); used_ = 0; }
private:
    std::FILE* file_;
    char* buf_;
    std::size_t cap_, used_ = 0;
};
```

#### answers

<details>
<summary>answer 1: defaulted destructor and vector reallocation</summary>

copied. `= default` still counts as *declaring* the destructor ([day 24](#day-24)), so the implicit move constructor and move assignment are not declared. rvalues then bind to the copy constructor, `std::is_nothrow_move_constructible_v<Telemetry>` is false (the copy constructor can throw), and `std::vector` falls back to copying to keep its strong guarantee ([day 23](#day-23)). fix: delete the destructor declaration, or declare all five as `= default`.

</details>

<details>
<summary>answer 2: shared_ptr and threads</summary>

no. the atomic count makes it safe for each thread to copy and destroy *its own* `shared_ptr`; it does nothing for the `Stats` object. `add` and `reset` modify the same object concurrently, which is a data race and undefined behavior unless `Stats` synchronizes internally (or the threads share a mutex). sharing ownership and sharing mutable state are separate problems, and `shared_ptr` only solves the first.

</details>

<details>
<summary>answer 3: shared_ptr, unique_ptr, and the missing virtual destructor</summary>

`make_shared<Logger>()` creates a control block whose deleter destroys a `Logger`, and converting to `shared_ptr<Plugin>` keeps that control block, so the right destructor runs. `unique_ptr<Plugin>` uses `default_delete<Plugin>`, which does `delete` on a `Plugin*`; without a virtual destructor that is undefined behavior ([day 31](#day-31)). switching to `shared_ptr` papers over the defect for one creation path only: a `shared_ptr<Plugin>(raw_plugin_ptr)` or any plain `delete` brings it back, and it imposes shared ownership where none is needed. the fix is a public virtual destructor in the interface.

</details>

<details>
<summary>answer 4: elision and return std::move</summary>

`return local;` is eligible for NRVO, which compilers routinely perform but the standard does not require; if it does not happen, the local is still treated as an rvalue and moved. `return std::move(local);` turns the operand into an xvalue, which is no longer "the name of a local", so NRVO is off the table and you are guaranteed a move instead of possibly nothing. C++17's guaranteed elision applies to prvalues (`return Frame{n};`), where no copy or move constructor is even required. GCC warns with `-Wpessimizing-move`.

</details>

<details>
<summary>mini exercise answer</summary>

the bugs:

- if `new char[capacity]` throws `std::bad_alloc`, the destructor never runs ([day 19](#day-19)), and the `FILE*` leaks.
- if `fopen` fails, the body throws and `buf_` leaks for the same reason.
- the implicit copy operations copy both raw pointers: two objects, then a double `fclose` and double `delete[]` (UB).
- no moves: the class cannot be returned from a factory or stored in a vector without copying, which is itself the double-free bug.
- the destructor calls `flush()`, whose `fwrite` errors are silently lost ([day 16](#day-16)).

the neatest rewrite notices that the hand-made buffer duplicates what stdio already does. remove it, size the stdio buffer instead, and the class owns exactly one resource through a type that already manages it:

```cpp complete
#include <cstdio>
#include <memory>
#include <stdexcept>

struct FileCloser {
    void operator()(std::FILE* f) const noexcept { std::fclose(f); }  // fclose flushes
};

class TelemetryLog {                         // move-only, rule of zero
public:
    TelemetryLog(const char* path, std::size_t capacity)
        : file_(std::fopen(path, "a")) {
        if (!file_) throw std::runtime_error("cannot open log");
        std::setvbuf(file_.get(), nullptr, _IOFBF, capacity);
    }
    void write(const char* msg) { std::fputs(msg, file_.get()); }
    [[nodiscard]] bool flush() { return std::fflush(file_.get()) == 0; }  // reports errors
private:
    std::unique_ptr<std::FILE, FileCloser> file_;
};
```

copying is now implicitly deleted, moves are implicit and `noexcept`, both leak paths are gone, and callers who care about write errors call `flush()` and check it. document the moved-from state: `file_` is null, so only assignment and destruction are allowed.

if you must keep a custom buffer (say, to batch records into fixed-size packets), make it a `std::vector<char>` member. flushing it on destruction then needs a user-declared destructor, which suppresses the implicit moves: declare the move operations `= default` and the copy operations `= delete`, so the class states its ownership explicitly instead of losing it by accident.

</details>

#### connections

the last two modules turned the language rules from the first two into ownership, and that vocabulary is used everywhere from here on. the next module adds runtime polymorphism ([day 30](#day-30)), where virtual destructors and slicing are ownership questions again. after it, containers ([day 34](#day-34)) reward `noexcept` moves, lambdas ([day 37](#day-37)) capture `unique_ptr` with init-captures, and perfect forwarding ([day 43](#day-43)) is how `make_unique` and `emplace_back` pass arguments through.

[back to the curriculum map](#curriculum)

---

<a id="module-polymorphism"></a>

## module 5: inheritance and polymorphism

how virtual dispatch works, the two rules that protect polymorphic objects, and composition as the default.

<a id="day-30"></a>

### day 30: virtual functions and dynamic dispatch

**module 5:** inheritance and polymorphism · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** explain how a virtual call selects an override at run time, what it typically costs, and how override and final catch mistakes  
**builds on:** [day 19](#day-19) (construction and destruction order), [day 26](#day-26) (exclusive ownership with `std::unique_ptr`)

#### the idea

`s.describe()` runs different code depending on which object is behind the reference `s`, and the compiler that generated the call did not know which one it would be. that is the whole point of a virtual function, and it is also where its costs and its classic mistakes come from: a signature that is almost right silently stops overriding, and a call that cannot be inlined blocks optimizations you did not know you were relying on.

#### understanding the concept

a virtual function call through a reference or pointer selects the override for the object's *dynamic* type. the standard specifies only that behavior. every mainstream compiler implements it the same way, though, and knowing the mechanism makes the costs concrete:

```text
typical layout (Itanium C++ ABI: GCC and Clang on Linux, also MinGW;
MSVC differs in details; none of this is required by the standard)

  Lidar object                    vtable for Lidar (one per class, read-only)
 +------------------+            +------------------------------------+
 | vptr  -----------+----------> | &Lidar::~Lidar (two entries)       |
 | Sensor members   |            | &Lidar::describe     (overridden)  |
 | Lidar members    |            | &Sensor::calibrate   (inherited)   |
 +------------------+            +------------------------------------+
                                   (RTTI and offset data sit just before)
```

a call `s.describe()` becomes: load the vptr from the object, load the function pointer from a fixed slot, call indirectly. the constructor of each class in the chain sets the vptr to its own class's table, which is exactly why [day 19](#day-19)'s virtual call in a base constructor reached the base version.

the cost is an extra dependent load or two and an indirect branch, which modern branch predictors handle well when a call site keeps seeing the same type. the larger cost is usually what the compiler cannot do: it cannot inline a call whose target it does not know, so it also cannot optimize across it (constant propagation, vectorizing a loop that contains it). compilers devirtualize when they can prove the dynamic type, and `final` helps them. whether any of this matters depends on call frequency, so put virtual boundaries at a coarse grain (one call per frame or per batch, not per sample) and measure before contorting a design to avoid them.

#### in code

first, let the compiler check your overrides.

```cpp fails
struct Filter {
    virtual ~Filter() = default;
    virtual double apply(double x) const = 0;
};

struct LowPass : Filter {
    double apply(double x);               // BUG: missing const: a new function that
};                                        // hides Filter::apply; LowPass stays abstract

struct LowPass2 final : Filter {
    double apply(double x) override;      // error: marked 'override' but does not override
};

struct LowPass3 final : Filter {
    double apply(double x) const override { return 0.9 * x; }   // correct
};
```

without `override`, a signature mismatch (missing `const`, `float` versus `double`, a changed base signature after a refactor) silently declares a new function. here the mistake surfaces only because `LowPass` remains abstract; had the base function not been pure, the base version would run and nothing would complain. GCC 12's `-Woverloaded-virtual` would flag the hiding, but it is not part of `-Wall` in that version. write `override` on every override; `final` on a class or function says "no further overriding" and gives the optimizer a devirtualization hint.

#### in practice

put virtual boundaries where calls are rare relative to the work they do. a radar processing chain built from interchangeable stages pays one indirect call per *frame* if the interface is `virtual void process(Frame& f) = 0;`, and one per *sample* if it is `virtual float filter(float sample) = 0;`. the first is noise; the second can be the difference between a vectorized inner loop and a scalar one, because the compiler cannot see through the call. designing the interface at the coarse grain keeps the flexibility of runtime polymorphism without asking anyone to measure its cost in a hot loop. when the set of types is fixed and the call is fine-grained, the alternatives in [day 97](#day-97) fit better.

#### watch out for

**default arguments are bound statically, overrides dynamically.**

```cpp complete
#include <cstdio>

struct Base {
    virtual ~Base() = default;
    virtual void log(int level = 1) const { std::printf("base %d\n", level); }
};
struct Derived : Base {
    void log(int level = 2) const override { std::printf("derived %d\n", level); }
};

int main() {
    Derived d;
    const Base& b = d;
    b.log();   // prints: derived 1
}
```

the function is chosen by the dynamic type, but the default argument comes from the declaration the compiler sees, which is `Base::log`. the result mixes two classes' intentions. do not redefine default arguments in overrides; better, avoid default arguments on virtual functions entirely and provide a non-virtual overload in the base.

#### the takeaway

a virtual call picks the override from the object's dynamic type through an indirect call; mark every override `override`, keep virtual calls at a coarse grain, and treat their cost as something to measure, not fear.

#### optional challenge

`Base` has a non-virtual public function `void tick()` and `Derived` declares its own `void tick()`. given `Derived d; Base& b = d;`, which function do `d.tick()` and `b.tick()` call? would adding `override` to `Derived::tick` help?

<details>
<summary>answer</summary>

`d.tick()` calls `Derived::tick` and `b.tick()` calls `Base::tick`. without `virtual`, the call is resolved from the static type of the expression, so the same object behaves differently depending on how you name it. `Derived::tick` merely hides `Base::tick`.

adding `override` would not compile ("marked 'override', but does not override"), and that is the point: it turns the silent mistake into an error that tells you the base function is not virtual. the fix is then a deliberate choice: make `Base::tick` virtual, or rename the derived function so nobody expects dispatch.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-31"></a>

### day 31: virtual destructors and object slicing

**module 5:** inheritance and polymorphism · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** make polymorphic deletion safe with a virtual destructor, and avoid slicing by keeping polymorphic objects behind indirection  
**builds on:** [day 30](#day-30) (virtual functions and dynamic dispatch)

#### the idea

two rules protect every polymorphic object, and both are easy to break without a compiler error. deleting a derived object through a base pointer is only defined when the base destructor is virtual. and polymorphism only works through references and pointers: copy a derived object into a base object and the derived part is simply cut off. one rule is about destruction and one about copying, but they come from the same fact: the static type and the dynamic type are different things.

#### understanding the concept

a `delete` expression on a `Base*` calls the destructor through the static type. if that destructor is virtual, the call dispatches like any other virtual call and the whole `Derived` object is destroyed, members included. if it is not virtual, the behavior is undefined: in practice the derived members are not destroyed and the deallocation may use the wrong size, but the standard promises nothing at all.

slicing is the copying side. a `Base` object has room for a `Base` and nothing more, so initializing one from a `Derived` copies the `Base` subobject and discards the rest, including the vptr: the result really is a `Base`. this is not undefined behavior; it is well-defined and almost never what you meant.

#### in code

second, the virtual destructor, and a twist with smart pointers.

```cpp
struct Plugin { ~Plugin() {} virtual void run() {} };   // BUG: non-virtual destructor
struct Logger : Plugin { std::string path; };

void demo() {
    std::unique_ptr<Plugin> p = std::make_unique<Logger>();
    p.reset();           // UB: deletes a Logger through Plugin* without a virtual dtor

    std::shared_ptr<Plugin> s = std::make_shared<Logger>();
    s.reset();           // OK, by accident: the control block remembers ~Logger
}
```

deleting a derived object through a base pointer whose destructor is not virtual is undefined behavior, not merely "the derived destructor is skipped". `unique_ptr<Base>` calls `delete` on a `Base*`, so it inherits the bug. `shared_ptr` happens to survive because the control block captured a deleter for the real type at creation, but relying on that is fragile. the rule: a class meant to be deleted through a base pointer gets a public virtual destructor; otherwise make the destructor protected and non-virtual. GCC's `-Wdelete-non-virtual-dtor` (in `-Wall`) catches a direct `delete base_ptr;`, but GCC 12 stays silent on the `unique_ptr` version above, because the `delete` happens inside a system header. `-Wnon-virtual-dtor` (not in `-Wall`) flags the class definition itself and catches both.

third, predict the output.

```cpp complete
#include <cstdio>
#include <vector>

struct Sensor {
    virtual ~Sensor() = default;
    virtual const char* name() const { return "sensor"; }
};
struct Lidar : Sensor {
    const char* name() const override { return "lidar"; }
};

int main() {
    Lidar lidar;
    Sensor& ref = lidar;
    Sensor copy = lidar;                  // slicing
    std::vector<Sensor> rack{lidar};      // slicing, again
    std::printf("%s %s %s\n", ref.name(), copy.name(), rack[0].name());
}
// prints: lidar sensor sensor
```

copying a `Lidar` into a `Sensor` object constructs a `Sensor` from the `Sensor` part and discards the rest: the object's type is `Sensor`, vptr included. polymorphism needs indirection (references, pointers, or `std::vector<std::unique_ptr<Sensor>>`). to make slicing impossible, delete or protect the base's copy operations ([day 24](#day-24)); an abstract base cannot be sliced into at all.

#### in practice

a plugin interface should make both mistakes impossible rather than merely documented:

```cpp
class Plugin {
public:
    virtual ~Plugin() = default;                   // safe to delete through Plugin*
    virtual void run() = 0;                        // abstract: a Plugin cannot be sliced into
    Plugin(const Plugin&) = delete;                // no copying a plugin through its interface
    Plugin& operator=(const Plugin&) = delete;
protected:
    Plugin() = default;
};

std::unique_ptr<Plugin> load_plugin(const std::string& name);
```

the virtual destructor makes `std::unique_ptr<Plugin>` correct; the pure virtual function makes the class abstract, so no `Plugin` object can be created by slicing; and the deleted copy operations stop derived classes from being copied through the base by accident. whether plugins themselves should be copyable is a separate decision, made in the derived classes.

#### watch out for

**not every base class needs a virtual destructor.** a base that only shares implementation or a policy (and is never deleted through a base pointer) can instead have a *protected, non-virtual* destructor. then `delete base_ptr;` does not compile at all, so the undefined behavior is impossible, and the class pays for no vtable. the guideline from the C++ Core Guidelines (C.35) is: a base class destructor should be either public and virtual, or protected and non-virtual. a public, non-virtual destructor on a class with virtual functions is the combination to avoid, and `-Wnon-virtual-dtor` flags it.

#### the takeaway

a base class meant for deletion through a pointer gets a public virtual destructor, and polymorphic objects live behind references and pointers, never in base-class values.

#### optional challenge

given `struct Lidar : Sensor` with virtual functions, which of these lines slice?

```cpp
void f(Sensor s);                      // (1) called as f(lidar)
void g(const Sensor& s);               // (2) called as g(lidar)
Sensor* p = new Lidar;                 // (3)
Sensor s2 = *p;                        // (4)
std::vector<Sensor> v{Lidar{}};        // (5)
```

<details>
<summary>answer</summary>

(1), (4), and (5) slice: each creates a `Sensor` object from a `Lidar`, by-value parameter, copy, and container element alike. (2) binds a reference, and (3) points to the full `Lidar`, so dispatch still works through them. (4) is worth a second look: `*p` refers to a whole `Lidar`, but the declared type of `s2` decides what gets created. making `Sensor` abstract turns (1), (4), and (5) into compile errors.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-32"></a>

### day 32: composition, interfaces, and substitutability

**module 5:** inheritance and polymorphism · **reading time:** about 5 minutes · **standard:** C++17  
**objective:** use public inheritance only for substitutable interfaces, keep contracts in the base with the NVI idiom, and compose implementations instead of inheriting them  
**builds on:** [day 31](#day-31) (virtual destructors and object slicing)

#### the idea

inheritance is two features wearing one keyword. it gives you *subtyping* (a `Lidar` can be used wherever a `Sensor&` is expected) and *implementation reuse* (a `Lidar` gets `Sensor`'s members and code). you almost always want the first. the second is where class hierarchies go wrong: deep trees, fragile bases, and a `MecanumDriveLidarRobotWithArm` class that exists only because the hierarchy had nowhere else to put it.

#### understanding the concept

two more tools for designing hierarchies. an **abstract interface** is a class with only pure virtual functions and a virtual destructor: it carries a contract and no implementation. the **non-virtual interface (NVI)** idiom makes public functions non-virtual and the customization points private virtual, so the base class enforces the contract around every override:

```cpp
class RangeSensor {
public:
    virtual ~RangeSensor() = default;
    double read_m() {                                  // the contract lives here
        double r = do_read_m();
        if (!(r >= min_m() && r <= max_m())) throw SensorFault{"out of range"};
        return r;
    }
private:
    virtual double do_read_m() = 0;                    // what derived classes provide
    virtual double min_m() const = 0;
    virtual double max_m() const = 0;
};
```

overrides cannot skip the check, and the base can later add logging or timing in one place.

#### in code

a mobile robot has a drive system and a localizer. the inheritance version models variations as subclasses: `DiffDriveRobot`, then `DiffDriveLidarRobot`, then a mecanum variant that needs half of each. every new axis of variation multiplies the classes. composition models each variation as a part:

```cpp
#include <memory>

struct Drive {                                   // interface: inherited
    virtual ~Drive() = default;
    virtual void apply(const Twist& cmd) = 0;
};

class Robot {                                    // implementation: composed
public:
    Robot(std::unique_ptr<Drive> drive, std::unique_ptr<Localizer> loc)
        : drive_(std::move(drive)), loc_(std::move(loc)) {}
    void step(const Twist& cmd) { drive_->apply(cmd); }
private:
    std::unique_ptr<Drive> drive_;
    std::unique_ptr<Localizer> loc_;
};
```

inheritance has not disappeared; it is confined to small interfaces (`Drive`), where subtyping is what you want. the robot *has* a drive rather than *is* one, so drive and localizer vary independently, can be swapped at run time, and can be replaced by fakes in tests ([day 91](#day-91) builds on this). the `unique_ptr` members also make `Robot` a move-only, rule-of-zero class.

#### in practice

substitutability is the other half. the Liskov substitution principle says code written against the base must keep working with any derived class. suppose `RangeSensor`'s contract is "always returns a range in `[min, max]`", and a new `Sonar` returns `-1` when it hears no echo. it compiles, it overrides correctly, and it breaks every caller that trusted the contract. the fix is not a type check in the callers; it is either a contract that admits "no reading" (an `std::optional<double>` result, [day 51](#day-51)) or a `Sonar` that is not a `RangeSensor`. subtyping is a promise about behavior, not just signatures.

#### watch out for

inheriting for code reuse. if `TelemetryPublisher` derives from `std::vector<Message>` or from a `Socket` class to "get" its functions, every public member of the base becomes part of your interface, users can call `push_back` and bypass your invariants, and changing the base breaks your users. make the reused type a private member and expose only what your class means. public inheritance is a statement that the derived class *is substitutable for* the base; if you would not say that sentence out loud, use composition.

#### the takeaway

use public inheritance for substitutable interfaces, with `override`, a virtual destructor, and no slicing; for reuse and variation, compose.

#### optional challenge

a colleague proposes `template <typename T> class ThreadSafeQueue : public std::queue<T>`, adding a mutex and locked versions of `push` and `pop`. what is wrong with the design, and what would you suggest instead?

<details>
<summary>answer</summary>

public inheritance makes every public member of `std::queue<T>` part of `ThreadSafeQueue`'s interface, including the unlocked `push`, `pop`, `front`, and `size`. any caller can bypass the mutex, so the class cannot keep its one invariant. it is also not substitutable: code that takes a `std::queue<T>&` will happily use it without locking. make the `std::queue<T>` a private member and expose only the locked operations (ideally a combined `try_pop` that checks and removes in one step, since a separate `empty()` check is stale by the time you act on it).

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-33"></a>

### day 33: review: inheritance and polymorphism

**module 5:** inheritance and polymorphism · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** consolidate virtual dispatch, virtual destructors and slicing, and composition, with spaced repetition from the ownership modules  
**covers:** [day 30](#day-30) to [day 32](#day-32)

#### recap

| lesson | key idea |
|---|---|
| [day 30](#day-30) | a virtual call picks the override from the dynamic type through an indirect call; `override` turns near-miss signatures into errors, and coarse-grained interfaces keep the cost irrelevant. |
| [day 31](#day-31) | deleting through a base pointer needs a public virtual destructor (or a protected non-virtual one that forbids it); copying a derived object into a base object slices it. |
| [day 32](#day-32) | inherit interfaces, compose implementations; a derived class must keep the base's behavioral contract, not just its signatures. |

this module was short because its ideas are few and sharp; the questions below also revisit the ownership modules that make polymorphic objects safe to hold.

#### review questions

1. `Filter::apply(double) const` is pure virtual. a derived class declares `double apply(double x);` (no `const`, no `override`). what happens at compile time, and what would happen if the base function were not pure?
2. why does `std::vector<Sensor>` filled with `Lidar` objects compile, run, and still be wrong? what should the vector hold instead?
3. a `Sonar` derives from `RangeSensor`, whose contract says `read_m()` always returns a range in `[min, max]`. `Sonar` returns `-1` when it hears no echo. every override compiles. what principle does it break, and what are the two honest fixes?
4. from [day 25](#day-25): a polymorphic base declares `virtual ~Sensor() = default;` and nothing else. what does that do to the move operations of `Sensor` and of every class derived from it?
5. from [day 28](#day-28): a function that runs every stage of a pipeline once takes `const std::vector<std::shared_ptr<Stage>>&`. what would you change, and why?

#### mini exercise

the robot below inherits its capabilities. sketch a composed version with one small interface, and say which part of the design became testable that was not before.

```cpp complete
class DiffDriveRobot {
public:
    virtual ~DiffDriveRobot() = default;
    virtual void drive(double v, double w);   // talks to the motor controller
};

class LidarDiffDriveRobot : public DiffDriveRobot {
public:
    void scan();                               // talks to the lidar
};
```

#### answers

<details>
<summary>answer 1: the missing const</summary>

the derived function has a different signature, so it does not override; it declares a new function that hides `Filter::apply`. because the base function is pure, the derived class stays abstract, and the error appears only where someone tries to create an object of it. had the base function not been pure, every call through a `Filter&` would silently run the base version. `override` on the derived declaration turns either case into an immediate error at the declaration.

</details>

<details>
<summary>answer 2: slicing in a container</summary>

each element of `std::vector<Sensor>` *is* a `Sensor`; inserting a `Lidar` copies its `Sensor` part and discards the rest, including the vptr, so every virtual call runs `Sensor`'s version. nothing is undefined, which is why it compiles and runs. polymorphic objects need indirection: `std::vector<std::unique_ptr<Sensor>>` keeps each object whole and gives the vector ownership. making `Sensor` abstract would have turned the mistake into a compile error.

</details>

<details>
<summary>answer 3: substitutability</summary>

the Liskov substitution principle: code written against `RangeSensor` must keep working with any derived class, and `Sonar` violates the behavioral contract every caller relies on. the fixes are to change the contract so that "no reading" is representable (for example `std::optional<double>`, [day 51](#day-51)), or to stop pretending a `Sonar` is a `RangeSensor` and give it its own interface. adding `if (dynamic_cast<Sonar*>(...))` in callers is the dishonest third option.

</details>

<details>
<summary>answer 4: a defaulted virtual destructor</summary>

declaring the destructor, even as `= default`, suppresses the implicit move constructor and move assignment, so `Sensor` and every derived class that does not declare its own moves will copy when asked to move. declare all five special members `= default` in the base (with the copy operations `protected` if you also want to prevent slicing), as shown in [day 24](#day-24).

</details>

<details>
<summary>answer 5: borrowing, not sharing</summary>

the function only uses the stages during the call, so it should not mention ownership at all: take `const std::vector<Stage*>&`, or better, `std::span<Stage* const>` later in the course, or have the pipeline expose a loop over `Stage&`. taking `shared_ptr`s forces every caller to share ownership with them even when one object owns all the stages, and couples this function to that ownership strategy.

</details>

<details>
<summary>mini exercise answer</summary>

```cpp
struct Drive {                                // one small interface
    virtual ~Drive() = default;
    virtual void apply(double v, double w) = 0;
};

class Robot {
public:
    Robot(std::unique_ptr<Drive> drive, std::unique_ptr<Lidar> lidar)
        : drive_(std::move(drive)), lidar_(std::move(lidar)) {}
    void step(double v, double w) { drive_->apply(v, w); }
private:
    std::unique_ptr<Drive> drive_;
    std::unique_ptr<Lidar> lidar_;            // optional capability: may be null
};
```

the drive is now a part, not a base class: a mecanum drive or a simulated one plugs in without a new robot class, and a lidar is something a robot may or may not have, rather than a level in a hierarchy. the newly testable part is `Robot`'s own logic: a test can pass a fake `Drive` that records the commands it receives, with no motor controller attached. [day 91](#day-91) builds a whole technique on this.

</details>

#### connections

inheritance is where ownership and lifetime meet runtime polymorphism: virtual destructors, slicing, and the special members of a base class are all ownership questions in disguise. the alternatives to virtual functions come later, once templates are available: compile-time polymorphism and type erasure in [day 97](#day-97) and [day 98](#day-98), and closed sets of types with `std::variant` in [day 53](#day-53). next, the standard library: containers, algorithms, and lambdas.

[back to the curriculum map](#curriculum)

---

<a id="module-library"></a>

## module 6: containers, algorithms, and lambdas

the standard library as a vocabulary: containers by cost, algorithms over iterator ranges, and lambdas as objects.

<a id="day-34"></a>

### day 34: containers and what they cost

**module 6:** containers, algorithms, and lambdas · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** choose a sequence container by access pattern, memory layout, and invalidation rules, starting from `std::vector`  
**builds on:** [day 23](#day-23) (noexcept moves and the strong guarantee), [day 26](#day-26) (exclusive ownership with `std::unique_ptr`)

#### the idea

`std::vector` is the default container in modern C++, and the reason has less to do with big-O than with memory. the standard's complexity guarantees tell you how the cost of an operation grows; they say nothing about the cache misses, allocations, and pointer chasing that decide what it costs at the sizes you actually have. and every container also makes promises about which references survive an insertion, which code tends to rely on without ever writing it down.

#### understanding the concept

a container is a contract about three things: complexity of operations, memory layout, and invalidation rules. the complexity is what the standard promises. the layout is what your cache experiences. the invalidation rules are what turn a refactor into a use-after-free.

`std::vector` is the default for good reasons. elements are contiguous, so iteration walks memory linearly and the hardware prefetcher can keep up. `push_back` is amortized O(1) because capacity grows geometrically; the standard only requires the amortized bound, and the growth factor is a library choice (libstdc++ doubles, MSVC grows by 1.5x). `reserve(n)` lets you pay for that growth once. the price: inserting in the middle is O(n), and growth beyond capacity moves every element to a new buffer, which is why [day 23](#day-23)'s `noexcept` move constructor matters.

the rest of the family, briefly:

| container | layout | lookup | insert / erase | what an insert invalidates |
|---|---|---|---|---|
| `vector` | one contiguous block | O(1) index | O(1) amortized at end, O(n) elsewhere | everything if it reallocates, else iterators at or after the insertion point |
| `array<T, N>` | inline, no heap | O(1) index | fixed size | n/a |
| `deque` | blocks of elements plus an index map | O(1) index | O(1) at both ends | at either end: all iterators, but no references |
| `list` | one node per element | O(n) | O(1) given an iterator | nothing |
| `map` / `set` | one node per element, usually a red-black tree | O(log n) | O(log n) | nothing |
| `unordered_map` | node per element plus a bucket array | O(1) average, O(n) worst | O(1) average | iterators if it rehashes, never references |

big-O hides the constant factors that often dominate at realistic sizes. every `map` or `unordered_map` insertion is a separate heap allocation, and every lookup chases pointers through nodes that may sit anywhere in memory. an `unordered_map` lookup also pays for hashing the key (cheap for an integer, real work for a long string) and for at least one indirection through the bucket array. for a few hundred small elements, a linear scan or binary search over a contiguous `vector` can win against a "faster" structure, and it can also lose. you don't know until you measure with realistic sizes and access patterns, which [day 105](#day-105) covers, and [day 107](#day-107) explains why memory layout moves the numbers so much.

`std::list` rarely wins on traversal speed, but it has two real advantages: insertion and erasure never invalidate references to other elements, and `splice` moves nodes between lists without copying or allocating. splicing one element or a whole list is O(1); splicing a range from a *different* list is linear in the range length, because `size()` must stay O(1).

#### in code

the classic invalidation bug. it passes tests for months because small test inputs happen to fit in the existing capacity.

```cpp ub
#include <vector>
#include <string>

struct Detection { float range_m; float doppler; std::string label; };

void annotate(std::vector<Detection>& dets) {
    Detection& first = dets.front();
    dets.push_back({0.0f, 0.0f, "synthetic"});  // may reallocate
    first.label = "reference";  // BUG: UB if push_back reallocated; 'first' dangles
}

void annotate_fixed(std::vector<Detection>& dets) {
    const std::size_t first = 0;  // indices survive reallocation, references do not
    dets.push_back({0.0f, 0.0f, "synthetic"});
    dets[first].label = "reference";
}
```

calling `reserve` before taking the reference would also fix it, but that couples correctness to a capacity calculation somebody will change later. an index (or a stable id) states the intent directly.

`emplace_back` versus `push_back` is the third everyday decision:

```cpp complete
#include <vector>
#include <memory>

struct Widget { };

void fill(std::vector<std::unique_ptr<Widget>>& v, std::vector<std::vector<int>>& rows) {
    v.push_back(std::make_unique<Widget>());  // fine: object built first, then moved in
    v.emplace_back(new Widget);  // BUG: if growth throws, the raw pointer leaks

    rows.emplace_back(1'000'000);  // compiles: a row of one million zeros, via an explicit ctor
    // rows.push_back(1'000'000);  // error: no implicit conversion int -> vector<int>
}
```

`emplace_back` forwards its arguments to a constructor ([day 43](#day-43) shows how), which means it happily calls `explicit` constructors that `push_back` would refuse. use it when you are constructing from constructor arguments; when you already have an object, `push_back` says the same thing and is equivalent. since C++17, `emplace_back` returns a reference to the new element.

#### in practice

back to the radar tracker. the first version stores tracks in `std::unordered_map<TrackId, Track>`, and the association stage keeps `Track*` pointers into it across frames. that works, quietly, because `unordered_map` never invalidates references, even on rehash. a later profiling session suggests a `std::vector<Track>` for faster per-frame updates. the swap compiles cleanly and then corrupts memory on the first frame that adds enough tracks to reallocate, because the code was depending on a guarantee that was never written down.

the design lesson: reference stability is part of a container's contract, and code that stores pointers or iterators into a container depends on it. if you want freedom to change containers later, hand out stable identifiers (a track id, or an index plus generation counter) instead of addresses. then the layout decision becomes a measurement question again rather than a correctness question.

#### watch out for

**`reserve` changes capacity, not size.**

```cpp ub
#include <vector>

void load(std::vector<float>& samples) {
    samples.reserve(1024);
    samples[0] = 1.0f;          // BUG: size() is still 0, so this is out of bounds
}
```

`reserve` allocates room for future elements without creating any; indexing them is undefined behavior, and on most implementations it "works" until a debug build or a sanitizer notices. after `reserve`, add elements with `push_back` or `emplace_back`. if you want 1024 value-initialized elements to index into, `resize(1024)` (or construct the vector with that size) is the call you meant.

#### the takeaway

pick the container by access pattern, then check the invalidation rules, then measure; start with `std::vector`, and treat reference stability as part of the interface, because whoever depends on it is coupled to your container choice.

#### optional challenge

what does this guarantee, and what doesn't it?

```cpp
std::vector<int> v{1, 2, 3};
v.reserve(4);
int& r = v[0];
v.push_back(4);
v.push_back(5);
int x = r;
```

<details>
<summary>answer</summary>

`reserve(4)` guarantees `capacity() >= 4`, so the first `push_back` (size 3 to 4) cannot reallocate and `r` is still valid after it. the exact capacity after `reserve` is not specified; an implementation may allocate more than you asked for. so whether the second `push_back` (size 4 to 5) reallocates depends on the library. if it does, `r` dangles and `int x = r;` is undefined behavior. with libstdc++, `reserve(4)` on this vector yields exactly 4, so the second `push_back` reallocates. portable code cannot rely on either outcome; if it must keep `r`, it needs `reserve(5)` or an index.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-35"></a>

### day 35: maps, sets, and node handles

**module 6:** containers, algorithms, and lambdas · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** choose between ordered, hashed, and flat associative containers, and use the C++17 insertion functions and node handles  
**builds on:** [day 34](#day-34) (containers and what they cost)

#### the idea

you need to keep the live tracks of a radar tracker: a few hundred entries, looked up by track id, updated every frame, occasionally created and deleted. `std::map`, `std::unordered_map`, a sorted `std::vector`? most engineers answer from habit. the better answer starts from three questions: how is the data accessed, what does each operation cost in complexity *and* in memory traffic, and which guarantees (ordering, reference stability) does the rest of the code silently rely on?

#### understanding the concept

`std::map` and `std::set` are ordered: usually a red-black tree with one heap node per element, O(log n) lookup, iteration in key order, and references that stay valid until the element is erased. `std::unordered_map` and `std::unordered_set` are hash tables: one node per element plus a bucket array, O(1) lookup on average (O(n) in the worst case), no useful order, and a rehash on growth that invalidates iterators but never references. the unordered containers need a hash function and an equality comparison for the key, and they pay for hashing on every lookup.

a third option is not a node container at all: a sorted `std::vector` searched with `std::lower_bound`. it gives up cheap insertion in the middle and in exchange has contiguous memory, no per-element allocation, and the smallest footprint. for data that is built once and read often, it is frequently the fastest of the three. (C++23 standardizes the idea as `std::flat_map`.)

C++17 gave the associative containers better insertion functions and node handles. `try_emplace` constructs the value only if the key is absent, and does not move from its arguments when the key already exists. `insert_or_assign` says what `operator[]` plus assignment means, without requiring a default-constructible mapped type and while telling you which case happened.

#### in code

```cpp complete
#include <map>
#include <memory>
#include <string>
#include <iostream>

struct Track { explicit Track(int id) : id{id} {} int id; };  // no default constructor

int main() {
    std::map<int, std::unique_ptr<Track>> tracks;
    auto p = std::make_unique<Track>(7);

    tracks.try_emplace(7, std::move(p));
    auto q = std::make_unique<Track>(7);
    auto [it, inserted] = tracks.try_emplace(7, std::move(q));
    std::cout << inserted << ' ' << (q != nullptr) << '\n';  // prints: 0 1  (q not consumed)

    auto [it2, ins2] = tracks.insert_or_assign(7, std::make_unique<Track>(70));
    std::cout << ins2 << ' ' << it2->second->id << '\n';      // prints: 0 70

    // Rekey a node without reallocating it: extract, edit the key, reinsert.
    auto node = tracks.extract(7);
    node.key() = 8;
    tracks.insert(std::move(node));

    std::map<int, std::unique_ptr<Track>> retired;
    retired.try_emplace(8, std::make_unique<Track>(800));
    retired.try_emplace(9, std::make_unique<Track>(9));
    tracks.merge(retired);  // moves node 9 across; key 8 already exists, so it stays behind
    std::cout << tracks.size() << ' ' << retired.size() << '\n';  // prints: 2 1
}
```

`extract` and `merge` relink existing nodes, so no element is copied, moved, or reallocated, and pointers to the elements remain valid (they now refer into the other container). that makes them the right tool for move-only values and for rekeying, which used to require erase plus a fresh insert.

#### in practice

a lookup table built at startup and read every cycle, such as per-channel calibration for a few hundred radar channels, is the textbook case for the sorted vector:

```cpp complete
#include <algorithm>
#include <vector>

struct ChannelCal { int channel; double gain; double offset_m; };

const ChannelCal* find_cal(const std::vector<ChannelCal>& sorted, int channel) {
    auto it = std::lower_bound(sorted.begin(), sorted.end(), channel,
                               [](const ChannelCal& c, int ch) { return c.channel < ch; });
    return (it != sorted.end() && it->channel == channel) ? &*it : nullptr;
}
```

the table is sorted once after loading; every lookup is a binary search over contiguous memory with no allocation. whether this beats `std::unordered_map<int, ChannelCal>` at your size is a measurement question ([day 105](#day-105)), but it is a strong default for read-mostly data, and it never has a rehash pause in the middle of a control cycle.

#### watch out for

`operator[]` on `std::map` and `std::unordered_map` inserts a default-constructed value when the key is missing. a "read" such as `if (tracks[id]) ...` grows the table, may allocate, and for `unordered_map` may rehash and invalidate every iterator you hold. it also cannot be called on a `const` map. use `find` (or C++20 `contains`) to query, `try_emplace` or `insert_or_assign` to write.

#### the takeaway

use an ordered map when you need order or stable references, a hash map when lookups dominate and keys hash cheaply, and a sorted vector when the data is read far more often than it changes; query with `find`, write with `try_emplace` and `insert_or_assign`.

#### optional challenge

what does this print, and which line does not compile?

```cpp
std::map<std::string, int> counts;
if (counts["lidar"] > 0) { /* ... */ }
std::cout << counts.size() << '\n';
const auto& view = counts;
std::cout << view["radar"] << '\n';
```

<details>
<summary>answer</summary>

the first output line prints `1`: `counts["lidar"]` inserted a value-initialized `int` for the missing key, so the "read" grew the map. the last line does not compile, because `operator[]` may insert and therefore has no `const` overload. use `view.find("radar")`, `view.count("radar")`, or C++20's `view.contains("radar")` to query, and `view.at("radar")` if a missing key is an error (it throws `std::out_of_range`).

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-36"></a>

### day 36: iterators and algorithms over raw loops

**module 6:** containers, algorithms, and lambdas · **reading time:** about 10 minutes · **standard:** C++17  
**objective:** use standard algorithms over half-open iterator ranges to state intent, and apply the erase-remove idiom correctly  
**builds on:** [day 34](#day-34) (containers and what they cost)

#### the idea

here is a line that compiles, passes a quick test, and is wrong:

```cpp
v.erase(std::remove_if(v.begin(), v.end(), is_even));
```

it erases one element, not all the even ones. to see why, you need the model behind the standard algorithms: they see iterators, never containers. once that model clicks, the erase-remove idiom, the iterator categories, and the "use an algorithm instead of a loop" advice all follow from the same idea.

#### understanding the concept

an algorithm like `std::remove_if` receives a pair of iterators `[first, last)`. it can read and write elements through them, but it has no access to the container: it cannot allocate, cannot shrink, cannot erase. that decoupling is the design win of the STL: N algorithms times M containers needs N + M pieces of code, not N × M. the price is that some operations take two steps, one by the algorithm and one by the container.

the half-open range is what makes this compose. `end()` points one past the last element, so an empty range is `first == last`, the length is `last - first` for random-access iterators, and "not found" has a natural value: the algorithm returns `last`. subranges chain without plus-or-minus-one adjustments: `[first, mid)` and `[mid, last)` cover the whole range exactly once.

algorithms state what they need from iterators through categories. each category adds guarantees to the previous one:

| category | adds | typical source |
|---|---|---|
| input | read once, single pass | `std::istream_iterator` |
| forward | multi-pass, can revisit | `std::forward_list`, unordered containers |
| bidirectional | `--it` | `std::list`, `std::map`, `std::set` |
| random access | `it + n`, `it2 - it1`, `<` in O(1) | `std::deque` |
| contiguous (named in C++20) | elements adjacent in memory | `std::vector`, `std::array`, `std::string` |

in C++17 there is no tag for contiguous iterators; contiguity is a property of the container, and C++20 adds `std::contiguous_iterator_tag` and the `std::contiguous_iterator` concept. `std::sort` needs random access, so `std::sort(list.begin(), list.end())` fails to compile. GCC 12 reports it as `no match for 'operator-'` from deep inside `stl_algo.h`, which is the pre-concepts error experience that [day 60](#day-60) fixes. `std::list` has a member `sort()` for exactly this reason.

why prefer algorithms to hand-written loops? a named algorithm states intent (`any_of` reads as a question, a `for` loop with a `bool found` flag has to be simulated), it gets the boundary conditions right once, and it advertises its complexity. Sean Parent's "no raw loops" is a good default, not a law: when a loop does two things in one pass, or the algorithm version needs a contorted lambda, a plain loop is the clearer code.

#### in code

intent-revealing algorithms over a telemetry buffer. the lambdas are short on purpose; [day 37](#day-37) covers what they compile to.

```cpp complete
#include <algorithm>
#include <iterator>
#include <numeric>
#include <vector>

struct Sample { double value; bool valid; };

bool any_fault(const std::vector<Sample>& s) {
    return std::any_of(s.begin(), s.end(), [](const Sample& x) { return !x.valid; });
}

// Returns s.end() if nothing exceeds the limit: the half-open range gives "not found" a value.
auto first_over(const std::vector<Sample>& s, double limit) {
    return std::find_if(s.begin(), s.end(), [limit](const Sample& x) { return x.value > limit; });
}

std::vector<double> scaled(const std::vector<Sample>& s, double gain) {
    std::vector<double> out;
    out.reserve(s.size());
    std::transform(s.begin(), s.end(), std::back_inserter(out),
                   [gain](const Sample& x) { return x.value * gain; });
    return out;
}

double energy(const std::vector<double>& v) {
    return std::accumulate(v.begin(), v.end(), 0.0, [](double acc, double x) { return acc + x * x; });
}
```

`std::back_inserter` is an output iterator whose assignment calls `push_back`. that is how an algorithm that cannot touch the container still appends to it: the container is reached through an iterator adaptor that the caller chose.

now the erase-remove bug. predict the output:

```cpp complete
#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    auto is_even = [](int x) { return x % 2 == 0; };

    std::vector<int> v{1, 2, 3, 4, 5, 6};
    v.erase(std::remove_if(v.begin(), v.end(), is_even));  // BUG: single-iterator erase
    std::cout << v.size() << '\n';                          // prints: 5

    std::vector<int> w{1, 2, 3, 4, 5, 6};
    w.erase(std::remove_if(w.begin(), w.end(), is_even), w.end());  // erase-remove idiom
    std::cout << w.size() << '\n';                                  // prints: 3
}
```

`remove_if` shifts the kept elements (1, 3, 5) to the front and returns an iterator to the new logical end. the elements after it are valid but have unspecified values (with libstdc++ the first buggy vector ends as `1 3 5 5 6`, but don't depend on that). `erase(it)` removes one element; `erase(it, end())` removes the tail. C++20 wraps the idiom as `std::erase_if(w, is_even)`, which returns the number of elements removed.

#### in practice

a telemetry service computes the p99 latency of each one-second window. the first version copies the samples, calls `std::sort` (O(n log n)), and reads the element at index `0.99 * n`. `std::nth_element` places exactly that element where it would be after sorting, with everything smaller before it and everything larger after it, in O(n) on average. for a single percentile the full sort does work nobody uses. knowing the algorithm vocabulary (`nth_element`, `partial_sort`, `lower_bound` on sorted data, `minmax_element`) is often worth more than micro-tuning a loop. still measure: for a few hundred samples per window, both may be far below the noise floor of the service.

#### watch out for

`std::accumulate` uses the type of its initial value as the accumulator type:

```cpp
std::vector<double> v{0.5, 0.5, 0.5};
auto total = std::accumulate(v.begin(), v.end(), 0);  // BUG: int accumulator; total == 0
```

each step computes `int + double`, then converts the result back to `int`, truncating 0.5 to 0. GCC 12 gives no warning here even with `-Wconversion`, because the conversion happens inside a system header. write `0.0` (or `T{}`) and let the initial value carry the type you mean.

#### the takeaway

algorithms see iterators, not containers. that one fact explains the half-open range, the erase-remove idiom, `back_inserter`, and why `std::sort` cannot sort a list. reach for a named algorithm first because it says what you mean, and drop back to a loop when the loop is clearer.

#### optional challenge

what is wrong with this, and what are two correct fixes?

```cpp
std::vector<double> in{1.0, 2.0, 3.0};
std::vector<double> out;
std::transform(in.begin(), in.end(), out.begin(), [](double x) { return x * 2; });
```

<details>
<summary>answer</summary>

`out` is empty, so `out.begin()` is also `out.end()`, and `transform` writes three elements past the end: undefined behavior. the algorithm cannot grow `out` because it only has an iterator, not the container. fix it with `out.resize(in.size())` before the call (then writing through `out.begin()` is valid), or with `out.reserve(in.size())` plus `std::back_inserter(out)` as the destination. the second avoids value-initializing elements that are about to be overwritten, which matters for expensive element types and not at all for doubles.

</details>

#### going deeper (optional)

##### partition and stable sort

partition and stable sort express a common two-step "group, then order" job without index bookkeeping:

```cpp complete
#include <algorithm>
#include <vector>

struct Det { int id; float range_m; bool confirmed; };

void order_for_display(std::vector<Det>& dets) {
    // confirmed first, each group keeps its original order
    auto mid = std::stable_partition(dets.begin(), dets.end(),
                                     [](const Det& d) { return d.confirmed; });
    // confirmed detections by range; equal ranges keep their previous order
    std::stable_sort(dets.begin(), mid,
                     [](const Det& a, const Det& b) { return a.range_m < b.range_m; });
}
// input ids:  1(40m, conf) 2(12m) 3(12m, conf) 4(40m, conf) 5(7m)
// output ids: 3 1 4 2 5
```

the complexities are part of the choice. `std::partition` is O(n) and does not preserve relative order; `std::stable_partition` does, using a temporary buffer if it can get one (O(n)) and O(n log n) swaps if it cannot. `std::stable_sort` is O(n log n) comparisons with extra memory and O(n log² n) without. if order within groups does not matter, the unstable versions avoid that buffer.

##### parallel execution policies

C++17 also added execution policies: `std::sort(std::execution::par, v.begin(), v.end())`. treat them with care. the callable must not cause data races (locking inside it is allowed for `par`, not for `par_unseq`), an exception escaping an element access calls `std::terminate`, and whether you get parallelism at all depends on the library. MSVC ships a parallel implementation; libstdc++ uses Intel TBB as its parallel backend. on GCC 12 without TBB the code above still compiles and runs, but libstdc++ selects its serial backend, so you pay the policy's constraints without any speedup. parallel sorting also has a threshold below which the coordination costs more than it saves. benchmark on the target machine with production-sized inputs before committing to it.

[back to the curriculum map](#curriculum)

---

<a id="day-37"></a>

### day 37: lambdas are objects: closures and captures

**module 6:** containers, algorithms, and lambdas · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** explain what a lambda expression compiles to, and choose captures by what the closure should own or refer to  
**builds on:** [day 36](#day-36) (iterators and algorithms over raw loops), [day 26](#day-26) (exclusive ownership with `std::unique_ptr`)

#### the idea

a lambda looks like an inline function, which is exactly the wrong mental model. a lambda expression creates an *object*. that object has a type, a size, data members, and a lifetime, and every lambda bug you will meet in production (a dangling capture in a callback, a stateful predicate behaving oddly, a `std::function` that refuses to compile) follows from forgetting that.

#### understanding the concept

the compiler turns each lambda expression into a class with a unique, unnamed type (the closure type) and evaluates the expression to a prvalue of that type (the closure object). captures become data members, initialized when the lambda expression is evaluated. the body becomes `operator()`, which is `const` unless you write `mutable`.

```cpp complete
double gain = 2.0;
int calls = 0;
auto f = [gain, &calls](double x) { ++calls; return x * gain; };

// is roughly equivalent to:
struct Closure {
    double gain;   // copied when the lambda expression is evaluated
    int& calls;    // a reference: no lifetime extension, no ownership
    double operator()(double x) const { ++calls; return x * gain; }
};
auto g = Closure{gain, calls};
```

several rules fall out of this picture. a by-value capture is a snapshot taken at creation, not a live view. a `const` call operator can still modify what a reference capture refers to, because the constness applies to the member, not to the referent. two lambdas with identical text have different types, so you cannot assign one to a variable of the other's type. a lambda with no captures has no state and converts implicitly to a plain function pointer, which is how you pass one to a C API expecting `void(*)(int)`.

C++14 and C++17 added the pieces you use most:

- **init-captures** (`[p = std::move(ptr)]`, C++14) declare a member with any initializer. this is how you move a `std::unique_ptr` into a closure, or capture a computed value under a new name.
- **generic lambdas** (`[](const auto& a, const auto& b) {...}`, C++14) make `operator()` a template, instantiated per argument type.
- **`[*this]`** (C++17) copies the whole enclosing object into the closure, where `[this]` copies only the pointer.
- **constexpr lambdas** (C++17): a lambda's call operator is implicitly `constexpr` when it satisfies the requirements, so `constexpr auto sq = [](int x) { return x * x; }; static_assert(sq(4) == 16);` works.

#### in code

closures are values: copying one copies its state. predict the output.

```cpp complete
#include <iostream>

int main() {
    int n = 1;
    auto by_val = [n] { return n; };
    auto by_ref = [&n] { return n; };
    n = 2;
    std::cout << by_val() << by_ref() << '\n';    // prints: 12

    auto counter = [c = 0]() mutable { return ++c; };
    auto copy = counter;                           // copies the member c (still 0)
    counter();
    counter();
    std::cout << counter() << copy() << '\n';     // prints: 31

    // immediately invoked lambda: complex logic, but the result is const
    const auto mode = [&] {
        if (n > 1) return "fast";
        return "safe";
    }();
    std::cout << mode << '\n';                     // prints: fast
}
```

the last pattern deserves more use than it gets: when a `const` variable needs branching or a loop to compute, an immediately invoked lambda keeps it `const` instead of forcing a mutable variable with a delayed assignment.

#### in practice

capturing deliberately makes a lambda's dependencies as visible as a function's parameters. sorting detections by distance from the vehicle's current position is a one-liner, and the capture list documents exactly what the comparator depends on:

```cpp complete
#include <algorithm>
#include <vector>

struct Det { float x, y; };

void sort_by_distance(std::vector<Det>& dets, Det ego) {
    std::sort(dets.begin(), dets.end(), [ego](const Det& a, const Det& b) {
        auto d2 = [&ego](const Det& d) { return (d.x - ego.x) * (d.x - ego.x)
                                              + (d.y - ego.y) * (d.y - ego.y); };
        return d2(a) < d2(b);
    });
}
```

`ego` is captured by value: the comparator is a self-contained object that `std::sort` may copy as often as it likes. the inner helper captures by reference, which is safe because it never leaves the enclosing call. prefer explicit capture lists over `[=]` and `[&]` in anything longer than a line: they turn "what does this closure touch?" into something a reviewer can read instead of infer.

#### watch out for

`[=]` reads as "copy everything", but inside a member function it captures `this`, a pointer, not the members:

```cpp ub
#include <functional>

struct JointController {
    double kp = 1.5;
    std::function<double(double)> law() {
        return [=](double err) { return kp * err; };   // BUG risk: really this->kp
    }
};
// auto f = JointController{}.law(); f(0.1);   // UB: the temporary controller is gone
```

the closure stores `this`, so calling it after the controller is destroyed is undefined behavior. capture what you need explicitly (`[kp = kp]`), or copy the object with `[*this]` when it is small and copyable. C++20 deprecates the implicit capture of `this` through `[=]` for exactly this reason, and wants you to write `[=, this]` to say it out loud.

#### the takeaway

a lambda is a small class whose members are its captures; ask what it owns, what it points to, and how long it will live, exactly as you would for any other class.

#### optional challenge

on libstdc++, this removes two elements, not one. why is that allowed?

```cpp
std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8, 9};
v.erase(std::remove_if(v.begin(), v.end(),
                       [n = 0](int) mutable { return ++n == 3; }),
        v.end());
// libstdc++ result: 1 2 4 5 7 8 9
```

<details>
<summary>answer</summary>

the predicate is a closure object, and algorithms are allowed to copy their predicates. libstdc++'s `remove_if` first passes a copy to an internal `find_if` to locate the first element to remove: that copy counts to 3 and finds the element `3`. the algorithm then continues scanning with its own, still-unused copy, whose counter starts from 0 again and hits 3 at element `6`. the standard lets algorithms copy function objects freely and requires a predicate to give the same answer for the same element no matter which copy is called or how often. a counting predicate breaks that requirement, so no result is guaranteed (formally, violating a library requirement is undefined behavior; in practice you get results like this one). keep predicates stateless, or keep the state outside the closure and capture a reference to it when you truly need it.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-38"></a>

### day 38: lambdas that outlive their scope: callbacks and `std::function`

**module 6:** containers, algorithms, and lambdas · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** capture safely for lambdas that are stored or deferred, and choose between `std::function` and a template parameter  
**builds on:** [day 37](#day-37) (lambdas are objects: closures and captures)

#### the idea

a lambda passed to `std::sort` runs and is gone before the next line. a lambda passed to a timer, an event bus, or another thread runs *later*, after the function that created it may have returned. every capture is then a question about lifetime: does the object it refers to still exist when the callback finally fires? and once callbacks are stored, they need a type you can store them as, which brings type erasure and its costs.

#### understanding the concept

`[&]` is fine when the lambda runs before the enclosing scope ends: a predicate passed to `std::find_if`, a comparator for `std::sort`. it is a liability as soon as the lambda is stored, deferred, or handed to another thread. a useful rule: if the lambda leaves the scope, capture by value or by init-capture, and if it must refer to a shared object, capture something that tracks lifetime (a `std::weak_ptr`, [day 27](#day-27)) rather than a raw pointer or reference.

a stored callback also needs a type that can hold "any callable with this signature", because every lambda has its own unique type. `std::function<R(Args...)>` is that type. it is a value that owns a copy of the callable and erases the callable's concrete type behind an internal interface.

`std::function` stores the callable behind a type-erased interface ([day 98](#day-98) shows how). that costs an indirect call that the optimizer usually cannot inline, and possibly a heap allocation when the callable is too large for the internal buffer. the buffer size is a library detail: with libstdc++ in GCC 12, a lambda capturing two `double`s is stored inline and one capturing three `double`s allocates once. it also requires the callable to be copy-constructible, so closures owning a `unique_ptr` are rejected. (C++23 adds `std::move_only_function` for that case.) the template version has none of those costs, but it must be visible in a header and is instantiated once per callable type.

#### in code

the bug that matters most is a reference capture that outlives its referent. the lambda escapes the function, the stack frame goes away, and the closure holds a reference to nothing.

```cpp ub
#include <cstdio>
#include <functional>
#include <string>
#include <vector>

class Deferred {
    std::vector<std::function<void()>> tasks_;
public:
    void defer(std::function<void()> f) { tasks_.push_back(std::move(f)); }
    void flush() { for (auto& t : tasks_) t(); tasks_.clear(); }
};

void schedule_report(Deferred& d, const std::string& name) {
    std::string msg = "report: " + name;
    d.defer([&] { std::puts(msg.c_str()); });  // BUG: msg dies at return; flush() reads it: UB
}

void schedule_report_fixed(Deferred& d, const std::string& name) {
    std::string msg = "report: " + name;
    d.defer([msg = std::move(msg)] { std::puts(msg.c_str()); });  // the closure owns its data
}
```

now `std::function` versus a template parameter:

```cpp complete
#include <functional>
#include <memory>
#include <vector>

struct Point { float x, y, z; };

// Type-erased: one compiled function accepts any callable with this signature.
std::size_t count_if_erased(const std::vector<Point>& pts,
                            const std::function<bool(const Point&)>& keep) {
    std::size_t n = 0;
    for (const auto& p : pts) if (keep(p)) ++n;   // indirect call per point
    return n;
}

// Template: the callable's type is known, so the call can be inlined.
template <typename Pred>
std::size_t count_if_tmpl(const std::vector<Point>& pts, Pred&& keep) {
    std::size_t n = 0;
    for (const auto& p : pts) if (keep(p)) ++n;
    return n;
}

void demo() {
    auto owner = std::make_unique<float>(1.5f);
    auto in_range = [lim = std::move(owner)](const Point& p) { return p.z < *lim; };
    std::vector<Point> pts{{0, 0, 1}, {0, 0, 2}};
    count_if_tmpl(pts, in_range);                // fine
    // count_if_erased(pts, in_range);           // error: std::function needs a copyable callable
}
```

#### in practice

a point-cloud preprocessing library exposes a filter step that takes a user predicate. the first API used `std::function<bool(const Point&)>`, because it compiles into a single function in a `.cpp` file and accepts anything. profiling a 100,000-point cloud at 20 Hz showed the per-point indirect call in the hot loop, and the predicate's body could not be inlined or vectorized with the loop.

the fix is not "never use `std::function`". it is placing the type erasure where the call frequency is low. the library now takes a template parameter for the per-point predicate, and uses `std::function` for the per-frame "on cloud ready" callback, which fires twenty times a second and benefits from a stable, non-template, ABI-friendly signature. that is the general judgment: type erasure buys decoupling and a stable binary interface; templates buy inlining at the cost of compile time and header exposure. pick per call site, and confirm with a profiler ([day 106](#day-106)) that the hot path is really where you think it is.

#### watch out for

**an empty `std::function` throws when called.** a default-constructed or moved-from `std::function` holds nothing, and calling it throws `std::bad_function_call`. in an event loop that means an exception from deep inside dispatch, far from the code that forgot to set the handler. test before calling (`if (on_ready) on_ready(frame);`), or give the member a no-op default (`std::function<void(const Frame&)> on_ready = [](const Frame&) {};`) so the "not set" state cannot occur.

#### the takeaway

if a lambda leaves its scope, capture by value, by init-capture, or through a lifetime-tracking handle; use templates for hot-path callables and `std::function` at boundaries where flexibility and a stable signature are worth an indirect call.

#### optional challenge

`Bus::on_frame` stores its callback for as long as the bus lives, which is longer than `wire`. which subscriptions are safe?

```cpp
void wire(Bus& bus, Sensor& s, std::shared_ptr<Log> log) {
    int threshold = 5;
    bus.on_frame([&](const Frame& f) { if (f.count > threshold) s.update(f); });        // (1)
    bus.on_frame([threshold](const Frame& f) { /* uses threshold */ });                 // (2)
    bus.on_frame([&s](const Frame& f) { s.update(f); });                                // (3)
    bus.on_frame([log](const Frame& f) { log->write(f); });                             // (4)
    bus.on_frame([w = std::weak_ptr<Log>(log)](const Frame& f) {
        if (auto l = w.lock()) l->write(f);                                             // (5)
    });
}
```

<details>
<summary>answer</summary>

(1) is a bug: `threshold` is a local of `wire`, and every later frame reads a dead variable. (2) is safe: the closure owns a copy. (3) is safe only if the sensor outlives the subscription; that is a lifetime contract between the code that owns the sensor and the code that owns the bus, and it should be written down. (4) is safe, and it keeps the log alive as long as the bus holds the callback, which may be forever; if the log also refers back to the bus, that is a reference cycle. (5) is safe without extending the log's life: when the log is gone, `lock()` returns an empty pointer and the callback does nothing.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-39"></a>

### day 39: review: containers, algorithms, and lambdas

**module 6:** containers, algorithms, and lambdas · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** consolidate container choice and invalidation, algorithms over iterator ranges, and lambda captures and lifetimes  
**covers:** [day 34](#day-34) to [day 38](#day-38)

#### recap

| lesson | key idea |
|---|---|
| [day 34](#day-34) | start with `std::vector`; complexity, memory layout, and invalidation rules are all part of a container's contract. |
| [day 35](#day-35) | ordered map for order and stable references, hash map for fast lookups, sorted vector for read-mostly data; `operator[]` inserts. |
| [day 36](#day-36) | algorithms see iterators, never containers: half-open ranges, erase-remove, `back_inserter`, and why `std::sort` cannot sort a list. |
| [day 37](#day-37) | a lambda is an object whose members are its captures; by-value captures are snapshots. |
| [day 38](#day-38) | a stored lambda must not capture what it outlives; `std::function` erases the type at the cost of an indirect call and a copyable callable. |

#### review questions

1. you keep `Track*` pointers into a `std::unordered_map<int, Track>`. a burst of inserts triggers a rehash. which of your pointers and iterators are still valid? what changes if someone replaces the map with a `std::vector<Track>` kept sorted by id?
2. predict the output:

   ```cpp
   std::vector<int> v{5, 1, 4, 2, 3};
   int threshold = 2;
   auto above = [threshold](int x) { return x > threshold; };
   threshold = 4;
   std::cout << std::count_if(v.begin(), v.end(), above) << '\n';
   ```

3. why does `std::transform(in.begin(), in.end(), out.begin(), f)` with an empty `out` corrupt memory, while the same call with `std::back_inserter(out)` works?
4. a per-point filter in a hot loop takes `const std::function<bool(const Point&)>&`. a profiler shows the call overhead. what changes, and what do you give up?
5. from [day 24](#day-24): a teammate adds `~Telemetry() { log("closed"); }` to an otherwise rule-of-zero class holding a `std::vector<Sample>`. everything still compiles. what did that change cost?

#### mini exercise

this function is supposed to drop invalid detections, apply a range calibration, and return the ids of the three closest. it has two bugs, one of them undefined behavior. rewrite it with algorithms and lambdas, keep it correct for fewer than three detections, and decide where a plain loop is still the clearest choice.

```cpp complete
#include <algorithm>
#include <vector>

struct Detection { int id; float range_m; bool valid; };

std::vector<int> closest_ids(std::vector<Detection>& dets, float scale) {
    for (auto it = dets.begin(); it != dets.end(); ++it) {
        if (!it->valid) dets.erase(it);
        else it->range_m *= scale;
    }
    std::sort(dets.begin(), dets.end(),
              [](const Detection& a, const Detection& b) { return a.range_m < b.range_m; });
    std::vector<int> ids;
    for (std::size_t i = 0; i < 3; ++i) ids.push_back(dets[i].id);
    return ids;
}
```

#### answers

<details>
<summary>answer 1: rehash versus vector</summary>

pointers and references to elements of an `unordered_map` stay valid across a rehash, because elements live in separate nodes and only the bucket array is rebuilt. iterators are invalidated. with a sorted `std::vector<Track>`, any insertion invalidates references and iterators at or after the insertion point, and a reallocation invalidates all of them. the swap compiles, so the bug appears only at run time. stable ids instead of pointers keep the container choice free ([day 35](#day-35)).

</details>

<details>
<summary>answer 2: predict the output</summary>

it prints `3` (the elements 5, 4, and 3). `[threshold]` copies the value when the lambda expression is evaluated, so the closure holds 2; changing the local afterwards has no effect. with `[&threshold]` it would print `1` (only 5 exceeds 4). a by-value capture is a snapshot ([day 37](#day-37)).

</details>

<details>
<summary>answer 3: algorithms cannot grow containers</summary>

an algorithm only has iterators, so it cannot add elements. with an empty `out`, `out.begin()` equals `out.end()`, and `transform` writes past the end: undefined behavior. `std::back_inserter(out)` is an output iterator whose assignment calls `out.push_back`, so the container grows through an adaptor the caller chose. `out.resize(in.size())` before the call also works.

</details>

<details>
<summary>answer 4: std::function versus a template</summary>

make the filter a template parameter (`template <typename Pred> ... Pred&& keep`). the compiler then knows the callable's type, can inline it into the loop, and may vectorize the loop. you give up a single compiled function in a `.cpp` file: the template must live in a header, is instantiated per callable type, and adds compile time. keep `std::function` for low-frequency boundaries such as per-frame callbacks.

</details>

<details>
<summary>answer 5: a user-declared destructor</summary>

declaring a destructor suppresses the implicitly declared move constructor and move assignment. the copy operations are still generated (that generation is deprecated, but it happens), so every "move" of a `Telemetry` silently becomes a copy of the whole sample vector: when returned from some functions, when stored in containers, and on every reallocation. fix it by deleting the destructor and logging from a member whose own destructor does the work, or by defaulting all five special members explicitly ([day 24](#day-24)). this is the rule of zero protecting performance as well as correctness.

</details>

<details>
<summary>mini exercise answer</summary>

the bugs: `dets.erase(it)` invalidates `it`, so the `++it` that follows is undefined behavior (and, even if it worked, the element after an erased one would be skipped). and `dets[i]` reads past the end when fewer than three detections survive, which is also undefined behavior.

```cpp complete
#include <algorithm>
#include <cstddef>
#include <iterator>
#include <vector>

struct Detection { int id; float range_m; bool valid; };

std::vector<int> closest_ids(std::vector<Detection> dets, float scale, std::size_t k = 3) {
    dets.erase(std::remove_if(dets.begin(), dets.end(),
                              [](const Detection& d) { return !d.valid; }),
               dets.end());
    for (auto& d : dets) d.range_m *= scale;   // a plain loop is the clearest form here

    k = std::min(k, dets.size());
    const auto mid = dets.begin() + static_cast<std::ptrdiff_t>(k);
    std::partial_sort(dets.begin(), mid, dets.end(),
                      [](const Detection& a, const Detection& b) { return a.range_m < b.range_m; });

    std::vector<int> ids;
    ids.reserve(k);
    std::transform(dets.begin(), mid, std::back_inserter(ids),
                   [](const Detection& d) { return d.id; });
    return ids;
}
```

design notes: taking `dets` by value makes the mutation private (a caller that no longer needs its vector can `std::move` it in, and nobody is surprised by a reordered input). `std::partial_sort` orders only the first `k` elements, O(n log k) instead of O(n log n). the scaling loop stays a loop because `std::transform` in place, or `std::for_each`, would add syntax without adding meaning. in C++20, the first statement becomes `std::erase_if(dets, ...)`.

</details>

#### connections

this module put the first two modules to work: iterator invalidation is the lifetime rules of [day 08](#day-08) applied to containers, the vector's copy-or-move choice is [day 23](#day-23), and a lambda's captures are ownership decisions like any other members. the next module looks inside the machinery the library is built from: templates, deduction, and perfect forwarding, which is how `emplace_back` passes its arguments through.

[back to the curriculum map](#curriculum)

---

<a id="module-generic"></a>

## module 7: templates and generic programming

deduction, class templates, perfect forwarding, and the C++17 tools that replace template tricks.

<a id="day-40"></a>

### day 40: function templates and argument deduction

**module 7:** templates and generic programming · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** predict template argument deduction, explain why template definitions live in headers, and resolve dependent names  
**builds on:** [day 02](#day-02) (linkage and the one definition rule), [day 36](#day-36) (iterators and algorithms over raw loops)

#### the idea

```cpp fails
template <typename T>
T clamp_to(T v, T lo, T hi) { return v < lo ? lo : (hi < v ? hi : v); }

double speed = 12.5;
auto s = clamp_to(speed, 0, 10);  // error: deduced conflicting types for 'T' ('double' and 'int')
```

a function would have converted `0` and `10` to `double` without complaint. a template refuses. that refusal is the first rule of templates in action, and the rest of the model (instantiation, headers, specialization, the `typename` keyword nobody remembers to write) follows from taking templates for what they are: not functions or classes, but recipes the compiler uses to generate them.

#### understanding the concept

**deduction comes before conversion.** for a function template call, the compiler first deduces `T` from each argument independently, and every deduction must agree. implicit conversions are considered only after `T` is fixed. here the first argument says `double` and the others say `int`, so deduction fails before conversion is ever considered. the fixes say different things: `clamp_to<double>(speed, 0, 10)` fixes `T` explicitly and lets conversions happen; `clamp_to(speed, 0.0, 10.0)` makes the arguments agree; separate parameters `template <typename T, typename U>` accept the mix but must then define what mixing means. `std::max(1, 2.0)` fails for the same reason.

**instantiation happens where the template is used.** when the compiler sees `clamp_to<double>`, it stamps out a real function from the template body, which it can only do if the body is visible in that translation unit. that is why template definitions live in headers ([day 02](#day-02)): put the body in a `.cpp` and every other translation unit gets an `undefined reference` at link time. identical instantiations from different translation units are emitted as weak or COMDAT symbols and merged by the linker, so this does not violate the one definition rule. you can opt out with explicit instantiation: `template class RingBuffer<float, 64>;` in one `.cpp`, plus `extern template class RingBuffer<float, 64>;` in the header to stop every other translation unit from instantiating it again.

**two-phase lookup.** a template is checked twice. at its definition, names that do not depend on a template parameter are looked up and bound, and obvious errors are reported. at instantiation, dependent names (anything involving `T`) are resolved. because the compiler cannot know what `T::something` is before it knows `T`, you must tell it: `typename` marks a dependent name as a type, and `template` marks a dependent name as a member template.

#### in code

dependent names, the part of templates that produces the most confusing errors:

```cpp complete
template <typename T>
struct Base { void reset() {} };

template <typename T>
struct Filter : Base<T> {
    void clear() {
        // reset();       // error: not found; the base depends on T, so phase one doesn't look there
        this->reset();    // OK: 'this->' makes the name dependent, looked up at instantiation
    }
};

template <typename Container>
auto first_or(const Container& c, typename Container::value_type fallback) {
    typename Container::const_iterator it = c.begin();   // 'typename': this dependent name is a type
    return it != c.end() ? *it : fallback;
}
```

`Base<T>` could be specialized later so that it has no `reset` at all, which is why the compiler refuses to look inside a dependent base during the first phase. writing `this->` defers the lookup to instantiation, when the base is known. GCC 12's error says this almost directly: `there are no arguments to 'reset' that depend on a template parameter, so a declaration of 'reset' must be available`.

#### in practice

library authors design around deduction. `std::clamp(v, lo, hi)` deduces one `T` from all three arguments, so `std::clamp(speed, 0, 10)` fails exactly like `clamp_to`. when one argument should decide the type and the others should simply convert to it, put the others in a *non-deduced context*, where the compiler does not try to deduce from them at all:

```cpp complete
template <typename T> struct identity { using type = T; };   // C++20: std::type_identity

template <typename T>
T clamp_to(T v, typename identity<T>::type lo, typename identity<T>::type hi) {
    return v < lo ? lo : (hi < v ? hi : v);
}

double s = clamp_to(12.5, 0, 10);   // T = double from v alone; 0 and 10 convert
```

a type nested inside a template that depends on `T` (anything to the left of `::`) cannot be used to deduce `T`, so only `v` participates. the same idea explains why `std::function<void(T)>` parameters never deduce from a lambda: the lambda's type is not `std::function`, and conversions are not considered during deduction.

#### watch out for

explicit specializations of function templates do not take part in overload resolution; only primary templates do. the result can surprise you:

```cpp complete
#include <iostream>

template <typename T> void f(T)  { std::cout << "a\n"; }
template <> void f<int*>(int*)   { std::cout << "b\n"; }   // specializes the first template
template <typename T> void f(T*) { std::cout << "c\n"; }

int main() { int x = 0; f(&x); }   // prints: c
```

overload resolution picks between the two primary templates, chooses the more specialized `f(T*)`, and the specialization of `f(T)` is never considered. which template a specialization belongs to depends on what was declared before it and how it is spelled: written as `template <> void f(int*)` below the second template, it specializes `f(T*)` and the call prints `b`. prefer plain overloads for functions, and specialize class templates when you need per-type behavior that a function can forward to.

#### the takeaway

a function template is a recipe: deduction is exact and per argument, instantiation needs the definition in the translation unit, and dependent names need `typename` or `this->` from you.

#### optional challenge

given `template <typename T> void put(T a, T b);`, which calls compile?

```cpp
put(1, 2);            // (1)
put(1, 2u);           // (2)
put<long>(1, 2u);     // (3)
put("ab", "cd");      // (4)
put("ab", "abc");     // (5)
```

<details>
<summary>answer</summary>

(1), (3), (4), and (5) compile; (2) does not, because `int` and `unsigned int` deduce conflicting types. in (3) `T` is given, so both arguments convert to `long`. (4) and (5) are the subtle ones: by-value parameters decay arrays to pointers *before* deduction, so both arguments deduce `const char*` even though `"ab"` and `"abc"` have different array types (`const char[3]` and `const char[4]`). change the parameters to `const T&` and (5) stops compiling, because references do not decay.

</details>

#### going deeper (optional)

##### before concepts: SFINAE and `std::enable_if`

**before concepts, SFINAE.** if substituting a deduced type into a template's signature produces an invalid type or expression, that candidate silently drops out of overload resolution ("substitution failure is not an error"). `std::enable_if` exploits this to restrict a template:

```cpp complete
#include <type_traits>

template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
T half(T v) { return v / 2; }   // half(3.0) finds no viable function
```

it works, but the intent is buried in the syntax and the errors are poor. C++20 concepts ([day 60](#day-60)) state the same constraint as `template <std::integral T>`, and `if constexpr` ([day 44](#day-44)) replaces many overload-set tricks.

[back to the curriculum map](#curriculum)

---

<a id="day-41"></a>

### day 41: class templates, CTAD, and specialization

**module 7:** templates and generic programming · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** write class templates with type and non-type parameters, use class template argument deduction, and specialize where per-type behavior is needed  
**builds on:** [day 40](#day-40) (function templates and argument deduction)

#### the idea

`std::vector v{1, 2, 3};` names a class template without angle brackets, `std::array<float, 64>` puts a number in a type, and `std::vector<bool>` behaves differently from every other `std::vector`. those are three features of class templates: argument deduction from constructors, non-type parameters, and specialization. each is powerful, and each has a cost that shows up in compile times, binary size, or surprises.

#### understanding the concept

a class template generates a distinct class for every set of template arguments: `RingBuffer<float, 64>` and `RingBuffer<float, 128>` are unrelated types with separate code. a **non-type template parameter** puts a value (an integer, an enumerator, a pointer, and since C++17 any type deduced with `auto`) into the type, so the compiler can size storage, unroll loops, and check bounds at compile time.

CTAD reads the constructors and synthesizes deduction candidates from them, which is how `std::pair p{1, 2.0}`, `std::vector v{1, 2, 3}`, and `std::lock_guard lock{m}` work without angle brackets. a deduction guide adds a candidate when the constructor's parameter types do not say what you want deduced. note that CTAD from aggregate initialization without a guide arrived only in C++20.

specialization customizes a template for particular arguments. class templates allow full and partial specialization. function templates allow only full specialization, and even that is usually the wrong tool: overload instead.

#### in code

a class template, with a non-type parameter for capacity, and C++17 class template argument deduction (CTAD) with a deduction guide:

```cpp complete
#include <array>
#include <cstddef>
#include <string>

template <typename T, std::size_t N>
class RingBuffer {
    static_assert(N > 0, "capacity must be positive");
    std::array<T, N> buf_{};
    std::size_t next_ = 0, count_ = 0;
public:
    void push(const T& v) { buf_[next_] = v; next_ = (next_ + 1) % N; if (count_ < N) ++count_; }
    std::size_t size() const { return count_; }
    static constexpr std::size_t capacity() { return N; }
};

RingBuffer<float, 64> imu_window;   // N is part of the type: <float, 64> and <float, 128> are unrelated

template <typename T>
class Setting {
public:
    Setting(std::string name, T value) : name_(std::move(name)), value_(std::move(value)) {}
    const T& value() const { return value_; }
private:
    std::string name_;
    T value_;
};
Setting(std::string, const char*) -> Setting<std::string>;   // deduction guide

Setting gain{"gain", 2.5};     // CTAD: Setting<double>
Setting mode{"mode", "auto"};  // without the guide: Setting<const char*>, storing a pointer
                               // with the guide:    Setting<std::string>, owning its text

template <auto Value>          // C++17: the parameter's type is deduced from the argument
struct Constant { static constexpr auto value = Value; };
static_assert(Constant<'x'>::value == 'x' && Constant<42u>::value == 42u);
```

```cpp complete
#include <string>

template <typename T>
struct Serializer {                 // primary template
    static std::string to_text(const T& v) { return std::to_string(v); }
};

template <>
struct Serializer<bool> {           // full specialization
    static std::string to_text(bool b) { return b ? "true" : "false"; }
};

template <typename T>
struct Serializer<T*> {             // partial specialization: any pointer
    static std::string to_text(const T* p) { return p ? Serializer<T>::to_text(*p) : "null"; }
};

template <typename T> std::string describe(const T& v) { return Serializer<T>::to_text(v); }
// template <typename T> std::string describe<T*>(T* p);  // error: function templates cannot
                                                          // be partially specialized
template <typename T> std::string describe(T* p) { return "ptr:" + Serializer<T*>::to_text(p); }  // overload instead
```

#### in practice

a robotics middleware team templated its message buffers on both element type and capacity, `MessageQueue<T, N>`, and used it across 60 translation units with a dozen distinct `(T, N)` pairs. two costs showed up. compile time: every translation unit that touched a queue re-instantiated the same member functions, and the parser had to chew through the full implementation each time. binary size: `MessageQueue<Pose, 16>` and `MessageQueue<Pose, 32>` are entirely separate code even though only a constant differs.

the fixes were design decisions, not tricks. capacity moved to a constructor argument (allocated once at startup), because nothing needed it at compile time; that collapsed the instantiation count by type. the handful of remaining instantiations were declared `extern template` in the header and explicitly instantiated in a single `.cpp`. the rule of thumb: make something a template parameter when the compiler genuinely benefits from knowing it (inline storage, type safety, unrolling, compile-time checks), and a runtime value when it merely varies. measure the compile side with `-ftime-report` (GCC) or `-ftime-trace` (Clang), and the size side with `nm --size-sort` or a tool like Bloaty.

#### watch out for

**member functions of a class template are instantiated only when used.** that is what lets `std::vector<T>` work for types that support only some operations, and it also means untested members are uncompiled code:

```cpp
#include <memory>

RingBuffer<std::unique_ptr<int>, 4> owners;      // compiles: push() is not instantiated yet
// owners.push(std::make_unique<int>(1));        // error only now: push(const T&) copies
```

a template library can pass its own test suite and still fail to compile for a user's type the first time an untested member is called. test templates with the kinds of types users will actually bring: move-only, non-default-constructible, and expensive to copy.

#### the takeaway

every template parameter is a compile-time decision with compile-time and binary-size costs; make something a template parameter only when the compiler genuinely benefits from knowing it, and specialize class templates, not function templates.

#### optional challenge

what type does `v` have, and how many elements does it hold?

```cpp
std::vector<int> inner{1, 2};
std::vector v{inner};
```

<details>
<summary>answer</summary>

`std::vector<int>` with 2 elements: a copy of `inner`. you might expect braces to prefer the `std::initializer_list` constructor and produce `std::vector<std::vector<int>>` with one element. but CTAD has a special rule: when the braced list holds a single element whose type is a specialization of the class template being deduced, the copy deduction candidate wins. with two elements, `std::vector w{inner, inner}`, you do get `std::vector<std::vector<int>>`. if you mean a vector of vectors, spell the type out.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-42"></a>

### day 42: forwarding references and `std::forward`

**module 7:** templates and generic programming · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** recognize forwarding references, explain reference collapsing, and pass an argument's value category through with `std::forward`  
**builds on:** [day 40](#day-40) (function templates and argument deduction), [day 21](#day-21) (moving: transferring resources instead of copying them)

#### the idea

you write a thin wrapper: it logs, then passes its argument on to a function that has a copy overload and a move overload. callers hand it temporaries, so the move overload should run. it never does. then you "fix" it with `std::move`, and now it quietly steals strings from callers who passed a named variable they still need. the wrapper needs to pass along not just the value but its value category, and that is precisely what forwarding references and `std::forward` are for.

#### understanding the concept

`T&&` means two different things. when `T` is a template parameter deduced from the call, `T&&` is a **forwarding reference** (the standard's term; Scott Meyers popularized "universal reference"). anywhere else it is an ordinary rvalue reference.

```cpp
template <typename T> void f(T&& x);              // forwarding reference
auto&& r = make_value();                          // forwarding reference (auto deduces like T)
template <typename T> void g(std::vector<T>&& v); // rvalue reference: the parameter isn't exactly T&&
template <typename T> void h(const T&& x);        // rvalue reference: const disqualifies it
template <typename T> struct Box { void put(T&& x); };  // rvalue reference: T was fixed by the class
```

the trick is a special deduction rule plus reference collapsing. if the argument is an lvalue of type `U`, `T` is deduced as `U&`; if it is an rvalue, `T` is deduced as plain `U`. substituting gives `U& &&` or `U&&`, and since references to references can't exist in source code, the compiler collapses them:

| `T` | `T&&` becomes | meaning |
|---|---|---|
| `U&` | `U& &&` → `U&` | caller passed an lvalue |
| `U&&` | `U&& &&` → `U&&` | (via explicit arguments or aliases) |
| `U` | `U&&` | caller passed an rvalue |

any `&` in the mix wins; only `&& &&` stays `&&`. the upshot is that `T` *encodes* the caller's value category. inside the function, though, `x` is a named variable, and a named variable is always an lvalue ([day 11](#day-11)), whatever its declared type. to pass the caller's category on, you cast it back: `std::forward<T>(x)` is essentially `static_cast<T&&>(x)`. with `T = U&` that collapses to `U&` (an lvalue); with `T = U` it is `U&&` (an xvalue, so moves can happen). `std::move(x)` is the unconditional version: `static_cast<std::remove_reference_t<T>&&>(x)`, always an rvalue.

#### in code

the wrapper problem, three ways. predict the output.

```cpp complete
#include <cstdio>
#include <string>
#include <utility>

void consume(const std::string&) { std::puts("copy"); }
void consume(std::string&&)      { std::puts("move"); }

template <typename T> void relay_named(T&& s) { consume(s); }             // s is an lvalue
template <typename T> void relay_moved(T&& s) { consume(std::move(s)); }  // always an rvalue
template <typename T> void relay(T&& s)       { consume(std::forward<T>(s)); }

int main() {
    std::string name = "lidar_front";
    relay_named(std::string{"tmp"});  // prints: copy  (a missed move)
    relay_moved(name);                // prints: move  (BUG: consume may now steal the caller's 'name')
    relay(name);                      // prints: copy
    relay(std::string{"tmp"});        // prints: move
}
```

#### in practice

`auto&&` in a range-for is the forwarding reference you use most often without noticing:

```cpp complete
#include <vector>

void arm_all(std::vector<bool>& flags) {
    // for (auto& f : flags) f = true;   // error: *it is a prvalue proxy, not a bool&
    for (auto&& f : flags) f = true;     // OK: binds to the proxy, assignment writes through it
}
```

`auto&&` binds to whatever the iterator yields: an lvalue reference for ordinary containers, a temporary proxy for `std::vector<bool>` or for views that compute values. in generic code, `for (auto&& x : range)` is the form that always compiles; use `const auto&` when you mean read-only.

#### watch out for

a constructor template taking a forwarding reference is greedier than you think. it can beat the copy constructor:

```cpp
#include <string>
#include <utility>

class Sensor {
public:
    template <typename S>
    explicit Sensor(S&& name) : name_(std::forward<S>(name)) {}
    Sensor(const Sensor&) = default;
private:
    std::string name_;
};

Sensor a{"lidar"};
Sensor b{a};   // error: picks the template with S = Sensor&, then tries std::string(Sensor&)
```

`a` is a non-const lvalue. the copy constructor needs a `const` qualification added; the template deduces `S = Sensor&` and matches exactly, so it wins overload resolution. copying a `const Sensor` works; copying a non-const one fails to compile here, and in worse cases compiles into the wrong conversion. the same happens with classes derived from `Sensor`. constrain the template (`std::enable_if_t<!std::is_base_of_v<Sensor, std::decay_t<S>>, int> = 0` in C++17, a `requires` clause in C++20), or, often better, drop the template and take `std::string name` by value and move it into the member. that costs one extra move and removes the whole problem, which is a good trade for anything that is not a hot path.

#### the takeaway

`T&&` with a deduced `T` remembers whether the caller passed an lvalue or an rvalue, and `std::forward<T>` replays that choice; anywhere else, `T&&` is a plain rvalue reference.

#### optional challenge

for `template <typename T> void f(T&& x);`, what are `T` and the type of `x` in each call?

```cpp
int i = 0;
const int ci = 0;
f(i);
f(ci);
f(42);
f(std::move(ci));
```

<details>
<summary>answer</summary>

- `f(i)`: lvalue `int`, so `T = int&` and `x` is `int&`.
- `f(ci)`: lvalue `const int`, so `T = const int&` and `x` is `const int&`. constness is preserved, which is why forwarding never accidentally strips `const`.
- `f(42)`: prvalue, so `T = int` and `x` is `int&&`.
- `f(std::move(ci))`: xvalue of type `const int`, so `T = const int` and `x` is `const int&&`. you can't move from it in any useful way ([day 21](#day-21)): a move constructor taking `T&&` won't bind, so a copy happens.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-43"></a>

### day 43: variadic templates and perfect-forwarding factories

**module 7:** templates and generic programming · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** write variadic function templates that forward any number of arguments to a constructor, and know the costs of doing so  
**builds on:** [day 42](#day-42) (forwarding references and `std::forward`)

#### the idea

`std::make_unique<T>(args...)`, `emplace_back(args...)`, and `std::thread`'s constructor all accept any number of arguments of any types and hand them, unchanged, to something else. none of them is magic: each is a variadic template whose parameters are forwarding references, plus one expansion that forwards every argument at once. once you can read that pattern, you can write it, and you can see what it costs.

#### understanding the concept

variadic templates generalize this to any number of arguments. `typename... Args` declares a template parameter pack, `Args&&... args` a function parameter pack of forwarding references, and the pattern `std::forward<Args>(args)...` expands element-wise into a comma-separated list. `sizeof...(Args)` gives the count. that combination is the engine behind `std::make_unique`, `std::make_shared`, `std::thread`'s constructor, and every `emplace` function.

the `...` after a pattern expands the pattern once per element, so where you put it decides what gets repeated. with a pack `args` holding `a, b, c`:

| written | expands to |
|---|---|
| `f(args...)` | `f(a, b, c)` |
| `f(std::forward<Args>(args)...)` | `f(std::forward<A>(a), std::forward<B>(b), std::forward<C>(c))` |
| `f(g(args)...)` | `f(g(a), g(b), g(c))` |
| `f(g(args...))` | `f(g(a, b, c))` |

a pack can be empty, in which case `f(args...)` is simply `f()`. a pack cannot be indexed or iterated directly in C++17; you either expand it into a context that takes a list (function arguments, initializers, base classes) or, since C++17, reduce it with a fold expression ([day 45](#day-45)).

#### in code

a variadic factory that does some bookkeeping and then constructs in place. this is the shape of `make_unique` and of `emplace_back`, which forwards its arguments through the allocator to construct the element directly in the vector's storage.

```cpp complete
#include <memory>
#include <string>
#include <utility>

inline int g_created = 0;   // C++17 inline variable

template <typename T, typename... Args>
std::unique_ptr<T> make_tracked(Args&&... args) {
    static_assert(sizeof...(Args) <= 4, "keep constructors small");
    ++g_created;
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
    // expands to: new T(std::forward<A1>(a1), std::forward<A2>(a2), ...)
}

struct Joint {
    Joint(std::string name, double limit) : name(std::move(name)), limit(limit) {}
    std::string name;
    double limit;
};

void build() {
    std::string base = "elbow";
    auto a = make_tracked<Joint>(base, 2.6);           // base copied into Joint::name
    auto b = make_tracked<Joint>(base + "_2", 2.6);    // temporary moved into Joint::name
}
```

note the parentheses in `new T(...)`. in C++17, parentheses cannot initialize an aggregate, so `std::make_unique<Point>(1.0, 2.0)` fails for `struct Point { double x, y; };`. C++20 (P0960) allows parenthesized aggregate initialization, and the same call compiles there.

#### in practice

a robot's command queue offers `post<Cmd>(Args&&... args)`, which constructs the command inside the queue's preallocated slot instead of building a temporary and moving it in. for most command types the saving is one move construction, which is cheap, so the honest reasons to prefer it are different: it works for types that are neither copyable nor movable (a command holding a `std::mutex`, say), and it keeps the call site short.

two production costs come with it. first, every distinct combination of argument types is a separate instantiation, and forwarding references preserve exact types: `post<Log>("ok")` and `post<Log>("fail")` deduce `const char(&)[3]` and `const char(&)[5]`, two instantiations of the same function. in a header used everywhere, that shows up in compile time and binary size. second, a forwarded argument can be consumed only once. the bug looks innocent:

```cpp
template <typename... Args>
void post_and_log(Args&&... args) {
    log_args(std::forward<Args>(args)...);   // may move from the arguments...
    post(std::forward<Args>(args)...);       // BUG: ...so this may receive moved-from objects
}
```

pass by `const&` to everything except the last consumer, and forward only there.

#### watch out for

**a braced list cannot be forwarded.** template argument deduction has no type to deduce from `{1, 2, 3}`:

```cpp complete
#include <memory>
#include <vector>

// auto v = std::make_unique<std::vector<int>>({1, 2, 3});   // error: cannot deduce Args
auto w = std::make_unique<std::vector<int>>(std::initializer_list<int>{1, 2, 3});   // OK
```

the same is why `v.push_back({1, 2})` works for a vector of pairs (the parameter type is known, so the braces can initialize it) while `v.emplace_back({1, 2})` does not. with emplacement, pass the constructor arguments themselves (`v.emplace_back(1, 2)`) or name the type.

#### the takeaway

a variadic factory is a parameter pack of forwarding references plus one `std::forward<Args>(args)...` expansion; use it for factories, emplacement, and generic wrappers, forward each argument exactly once, and prefer pass-by-value for ordinary sink parameters.

#### optional challenge

`template <typename T, typename... Args> void post(Args&&... args);` is called five times. how many distinct instantiations of `post` does the compiler generate?

```cpp
std::string s = "x";
post<Log>("ok");
post<Log>("no");
post<Log>("fail");
post<Log>(std::string("x"));
post<Log>(s);
```

<details>
<summary>answer</summary>

four. `"ok"` and `"no"` both deduce `Args = const char(&)[3]`, so they share an instantiation; `"fail"` deduces `const char(&)[5]`, a different one. the temporary `std::string` deduces `Args = std::string` and the named `s` deduces `std::string&`, which are different again. forwarding references preserve exact types and value categories, which is what makes them perfect, and also what multiplies instantiations in a header used across a large codebase.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-44"></a>

### day 44: compile-time branching with if constexpr

**module 7:** templates and generic programming · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** replace SFINAE overload sets with if constexpr, and know exactly what a discarded branch skips  
**builds on:** [day 41](#day-41) (class templates, CTAD, and specialization), [day 43](#day-43) (variadic templates and perfect-forwarding factories)

#### the idea

you are writing a telemetry encoder that appends fields to a byte buffer. arithmetic values are copied as raw bytes, enums go out as their underlying integer, strings get a length prefix. before C++17, "do something different depending on the type" inside a template meant an overload set guarded by `std::enable_if` or a tag-dispatch helper, which scatters one decision across several functions and produces error messages nobody enjoys. C++17 lets you write the decision as a plain branch, evaluated at compile time, and lets you apply an operator across a whole parameter pack without recursion.

#### understanding the concept

`if constexpr (cond)` requires `cond` to be a constant expression convertible to `bool` (narrowing conversions are not allowed). its defining property is what happens to the branch that is not taken: **inside a template**, when the condition is known at instantiation, the discarded branch is not instantiated. code in it may be invalid for the current `T` (calling `v.size()` on an `int`, say) and that is fine, because it is never compiled for that `T`.

two limits follow from "not instantiated" rather than "not compiled at all":

- the discarded branch is still parsed. syntax errors and errors that do not depend on a template parameter are diagnosed.
- outside a template there is nothing to instantiate, so both branches are fully checked. `if constexpr` in a normal function behaves like `if` with a constant condition (with the minor difference that entities only used in the discarded branch need no definition).

a useful side effect: `return` statements in a discarded branch do not take part in return type deduction, so an `auto` function can return different types for different `T`.

#### in code

the encoder, before and after. the "before" splits one decision across three overloads:

```cpp complete
#include <cstdint>
#include <cstring>
#include <string>
#include <type_traits>
#include <vector>

using Buffer = std::vector<std::uint8_t>;

namespace before {   // C++14: SFINAE picks an overload
template <class T, std::enable_if_t<std::is_arithmetic<T>::value, int> = 0>
void put(Buffer& b, T v) {
    std::uint8_t raw[sizeof v];
    std::memcpy(raw, &v, sizeof v);        // native byte order
    b.insert(b.end(), raw, raw + sizeof v);
}
template <class T, std::enable_if_t<std::is_enum<T>::value, int> = 0>
void put(Buffer& b, T v) { put(b, static_cast<std::underlying_type_t<T>>(v)); }
inline void put(Buffer& b, const std::string& s) {
    put(b, static_cast<std::uint32_t>(s.size()));
    b.insert(b.end(), s.begin(), s.end());
}
}  // namespace before
```

after: one function, the decision in one place, and a deliberate error for anything else.

```cpp
template <class> inline constexpr bool always_false = false;

template <class T>
void put(Buffer& b, const T& v) {
    if constexpr (std::is_arithmetic_v<T>) {
        std::uint8_t raw[sizeof v];
        std::memcpy(raw, &v, sizeof v);    // native byte order
        b.insert(b.end(), raw, raw + sizeof v);
    } else if constexpr (std::is_enum_v<T>) {
        put(b, static_cast<std::underlying_type_t<T>>(v));
    } else if constexpr (std::is_same_v<T, std::string>) {
        put(b, static_cast<std::uint32_t>(v.size()));
        b.insert(b.end(), v.begin(), v.end());
    } else {
        static_assert(always_false<T>, "put: unsupported field type");
    }
}
```

with a plain `if`, every branch would be instantiated for every `T`: `put(b, 42)` would try to compile `v.size()` on an `int` and fail. with `if constexpr`, `put(b, 42)` instantiates only the first branch.

#### in practice

there is also a design judgment hiding here. the `if constexpr` chain is a **closed set**: supporting a new field type means editing `put`. that is a feature when the encoder owns the format and every type must be reviewed. if users of a library should be able to add their own types, an overload or a trait they can specialize is the better seam, because it is open for extension without touching your code. [day 53](#day-53) meets the same closed-versus-open tradeoff at runtime.

#### watch out for

the obvious way to write the "unsupported type" branch does not work:

```cpp
template <class T>
void put(Buffer& b, const T& v) {
    if constexpr (std::is_arithmetic_v<T>) { /* ... */ }
    else static_assert(false, "unsupported");   // BUG in C++17 and C++20
}
```

`false` does not depend on `T`, so the assertion can never succeed for any instantiation, and a non-dependent assertion is checked when the template is defined, not when a branch is chosen. under the C++17 and C++20 rules the template is ill-formed, and GCC 12 rejects it even if `put` is never called. the fix is to make the condition dependent, as in `always_false<T>` above. C++23 (paper P2593) changed the rule so that `static_assert(false)` is only evaluated when the branch is instantiated; GCC 13 and Clang 17 implement it, but on a C++17 or C++20 code base, keep the dependent-false helper.

#### the takeaway

`if constexpr` skips instantiation, not parsing, and only inside templates; it puts a closed set of type-dependent cases in one readable place, which is right when you own the set and wrong when users need to extend it.

#### optional challenge

with a plain `if`, does this compile for `T = int`? what changes with `if constexpr`?

```cpp complete
#include <type_traits>

template <class T>
auto count_of(const T& v) {
    if (std::is_integral_v<T>) return 1;
    else return v.size();
}
```

<details>
<summary>answer</summary>

with a plain `if` it fails twice for `int`: both branches are instantiated, so `v.size()` is compiled for an `int`, and the two `return` statements deduce different types (`int` and `std::size_t`) for one `auto` function. with `if constexpr`, the discarded branch is not instantiated and its `return` does not take part in return type deduction, so `count_of(42)` returns `int` and `count_of(std::string("ab"))` returns `std::size_t`. whether a function that returns different types per `T` is good API design is a separate question; here returning `std::size_t` from both branches would be kinder to callers.

</details>

#### going deeper (optional)

##### what a `constexpr` function may do in C++17

finally, `constexpr` functions. C++14 already allowed local variables, loops, and mutation inside them; C++17 added `constexpr` lambdas and `if constexpr`. still forbidden in C++17: `try` blocks, virtual calls, dynamic allocation, `static` locals, and uninitialized local variables (C++20 relaxes most of these; [day 69](#day-69)). a `constexpr` function is *allowed* to run at compile time; it is *required* to only where a constant expression is needed, such as a `static_assert`, an array bound, or a template argument. and in constant evaluation, core-language undefined behavior such as signed overflow is a compile error rather than a silent miscompile.

[back to the curriculum map](#curriculum)

---

<a id="day-45"></a>

### day 45: fold expressions

**module 7:** templates and generic programming · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** apply an operator across a parameter pack with the right fold form, and use the comma fold for ordered per-argument work  
**builds on:** [day 44](#day-44) (compile-time branching with if constexpr)

#### the idea

before C++17, doing something for every element of a parameter pack meant recursion: a function that handles the first argument and calls itself with the rest, plus a base case for the empty pack. it works, it instantiates one function per pack length, and it hides a one-line intent ("log each field", "check that all values are finite") in a small machine. fold expressions write that intent as one expression.

#### understanding the concept

**fold expressions** apply a binary operator across a parameter pack ([day 43](#day-43)). there are four forms, and the parentheses are part of the syntax:

| form | written | expands to (for `a, b, c`) |
|---|---|---|
| unary right | `(xs op ...)` | `a op (b op c)` |
| unary left | `(... op xs)` | `(a op b) op c` |
| binary right | `(xs op ... op init)` | `a op (b op (c op init))` |
| binary left | `(init op ... op xs)` | `((init op a) op b) op c` |

a unary fold over an empty pack is ill-formed except for three operators: `&&` gives `true`, `||` gives `false`, and the comma operator gives `void()`. for anything else, use a binary fold with an identity value. the comma fold is the workhorse for "do this for every argument": the built-in comma operator sequences its operands left to right, so `(f(xs), ...)` calls `f` in argument order. contrast that with function arguments, whose evaluation order is still unspecified ([day 14](#day-14)).

#### in code

now folds. predict the two results before reading the comments:

```cpp complete
#include <cmath>
#include <iostream>

template <class... Ts> int lsub(Ts... xs) { return (... - xs); }   // ((1 - 2) - 3)
template <class... Ts> int rsub(Ts... xs) { return (xs - ...); }   // (1 - (2 - 3))

template <class... Ts> auto sum(Ts... xs) { return (xs + ... + 0); }          // empty pack: 0
template <class... Ts> bool all_finite(Ts... xs) { return (std::isfinite(xs) && ...); }

template <class... Ts>
void log_line(const Ts&... xs) {
    ((std::cout << xs << ' '), ...);   // comma fold: guaranteed left to right
    std::cout << '\n';
}

int main() {
    std::cout << lsub(1, 2, 3) << ' ' << rsub(1, 2, 3) << '\n';   // prints: -4 2
    std::cout << sum() << ' ' << sum(1, 2.5) << '\n';             // prints: 0 3.5
    std::cout << all_finite(1.0, NAN) << '\n';                    // prints: 0
    log_line("imu", 3, 0.25);                                     // prints: imu 3 0.25
}
```

`&&` and `||` folds short-circuit just like the operators they expand to, so `all_finite` stops at the first non-finite value.

#### in practice

put the two together and a whole telemetry frame becomes one line per message type, with the type checks done by the compiler:

```cpp
enum class Mode : std::uint8_t { idle, tracking, fault };

template <class... Fields>
Buffer encode(std::uint16_t msg_id, const Fields&... fields) {
    Buffer b;
    put(b, msg_id);
    (put(b, fields), ...);               // one put per field, in order
    return b;
}

Buffer frame = encode(0x21, Mode::tracking, 12.5f, std::string("base_link"));
// 2 (id) + 1 (mode) + 4 (float) + 4 (length) + 9 (chars) = 20 bytes
```

passing a `std::vector<int>` as a field fails at compile time with the `static_assert` message rather than a page of overload-resolution notes. the costs are real but usually acceptable: every distinct list of field types instantiates a new `encode` (code size and compile time), and the format is native-endian, which is fine for same-host IPC and wrong for a wire protocol. measure compile time with `-ftime-report` (GCC) or `-ftime-trace` (Clang) if a header like this starts to dominate builds.

#### watch out for

**the operand of a fold must be a single cast-expression.** anything with a binary operator inside needs its own parentheses:

```cpp complete
template <class... Ts> auto doubled_sum(Ts... xs) {
    // return (xs * 2 + ...);      // error: binary expression in the fold operand
    return ((xs * 2) + ... + 0);   // OK: the operand is parenthesized
}
```

the outer parentheses belong to the fold syntax, and the inner ones make `xs * 2` one operand. the same applies to the comma fold, which is why the logging example writes `((std::cout << xs << ' '), ...)`. with mixed argument types, also check what type the accumulation runs in: in `(xs + ... + 0)` the first step adds the init value's type to the last element's type, and the usual arithmetic conversions from [day 04](#day-04) apply at every step.

#### the takeaway

a fold turns "for each argument" into one expression; choose left or right and unary or binary deliberately, give non-`&&`/`||`/comma folds an initial value, and use the comma fold when order matters.

#### optional challenge

which of these compile when called with no arguments, and what do they return?

```cpp complete
template <class... Ts> auto a(Ts... xs) { return (xs + ...); }
template <class... Ts> auto b(Ts... xs) { return (xs && ...); }
template <class... Ts> auto c(Ts... xs) { return (0 + ... + xs); }
```

<details>
<summary>answer</summary>

`a()` does not compile: a unary fold over `+` with an empty pack is ill-formed. `b()` compiles and returns `true` (type `bool`), because `&&` is one of the three operators with a defined empty value. `c()` compiles and returns `0` (type `int`), because a binary fold just yields its initial value when the pack is empty. note that `c` is a left fold; for `+` on numbers the direction does not change the value, but it does change the order of evaluation and, with mixed types, the intermediate types.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-46"></a>

### day 46: review: templates and generic programming

**module 7:** templates and generic programming · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** consolidate deduction, class templates, forwarding references, variadic templates, if constexpr, and fold expressions  
**covers:** [day 40](#day-40) to [day 45](#day-45)

#### recap

| lesson | key idea |
|---|---|
| [day 40](#day-40) | deduction is exact and per argument, instantiation needs the definition, dependent names need `typename` or `this->`. |
| [day 41](#day-41) | each argument set is a distinct class; CTAD deduces from constructors; specialize class templates, overload function templates. |
| [day 42](#day-42) | `T&&` with deduced `T` encodes the caller's value category; `std::forward<T>` replays it. |
| [day 43](#day-43) | a pack of forwarding references plus `std::forward<Args>(args)...` is the shape of every factory and `emplace`. |
| [day 44](#day-44) | the discarded branch is not instantiated (inside templates only); a closed set of cases lives in one place. |
| [day 45](#day-45) | one expression applies an operator across a pack; the comma fold runs in order. |

#### review questions

1. which of these parameters are forwarding references?

   ```cpp
   template <class T> void a(T&& x);
   template <class T> void b(const T&& x);
   template <class T> struct S { void c(T&& x); };
   template <class T> void e(std::vector<T>&& x);
   auto&& d = make_frame();
   ```

2. why does `std::max(1, 2.0)` fail to compile when `std::max(1.0, 2.0)` and `1 < 2.0` are fine?
3. a wrapper forwards its argument twice: first to a logging function, then to the real consumer. what can go wrong, and how do you fix it?
4. in an `if constexpr` chain, why must the final "unsupported type" branch use something like `static_assert(always_false<T>, ...)` instead of `static_assert(false, ...)` in C++17 and C++20?
5. from [day 38](#day-38): a function template takes `Pred&& keep` and calls it in a loop, while an older version took `const std::function<bool(const Point&)>&`. name one thing each version can do that the other cannot.

#### mini exercise

write `all_in_range(lo, hi, xs...)`, a variadic function template that returns `true` when every value in `xs` lies in `[lo, hi]`, works for any mix of arithmetic types, returns `true` for an empty pack, and stops evaluating at the first failure.

#### answers

<details>
<summary>answer 1: forwarding references</summary>

`a` and `d` only. a forwarding reference is exactly `T&&` (or `auto&&`) where `T` is deduced from that very argument. `b` adds `const`, `e` wraps `T` in another type, and in `S::c` the `T` was fixed when the class was instantiated, so nothing is deduced at the call: all three are plain rvalue references.

</details>

<details>
<summary>answer 2: deduction before conversion</summary>

`std::max` is `template <class T> const T& max(const T&, const T&)`. deduction runs per argument and must agree: the first says `int`, the second `double`, so deduction fails before any conversion is considered. the built-in `<` is not a template, so the usual arithmetic conversions apply. write `std::max<double>(1, 2.0)` or make the arguments agree.

</details>

<details>
<summary>answer 3: forwarding twice</summary>

`std::forward` on an rvalue argument produces an rvalue, so the logging function may move from it, and the real consumer then receives a moved-from object. forward only at the last use: pass the argument to the logger as an lvalue (or `const&`), and `std::forward` it to the consumer.

</details>

<details>
<summary>answer 4: dependent false</summary>

`static_assert(false)` does not depend on a template parameter, so under the C++17 and C++20 rules it is checked when the template is defined, and the template is ill-formed even if that branch is never chosen (GCC 12 rejects it outright). `always_false<T>` depends on `T`, so it is only evaluated when the branch is instantiated. C++23 relaxed the rule, but code targeting C++17 or C++20 needs the helper.

</details>

<details>
<summary>answer 5: templates versus std::function</summary>

the template can inline the predicate, accepts move-only callables (a closure owning a `unique_ptr`), and costs no allocation. the `std::function` version can be compiled once in a `.cpp` file, keeps a stable non-template signature (useful at library and ABI boundaries), and can be stored in a member or container of uniform type.

</details>

<details>
<summary>mini exercise answer</summary>

```cpp complete
template <class L, class H, class... Ts>
constexpr bool all_in_range(L lo, H hi, Ts... xs) {
    return ((lo <= xs && xs <= hi) && ...);
}

static_assert(all_in_range(0, 10));              // empty pack: true
static_assert(all_in_range(0, 10, 1, 2.5, 9u));
static_assert(!all_in_range(0.0, 1.0, 0.5, 2));
```

the unary `&&` fold gives `true` for an empty pack and short-circuits at the first `false`, so later elements are not evaluated. separate template parameters for `lo`, `hi`, and the pack let each argument keep its own type; the comparisons then use the usual arithmetic conversions, so mixing signed and unsigned integers would bring back the surprises from [day 04](#day-04). a production version might constrain the parameters to arithmetic types, which [day 60](#day-60) makes easy.

</details>

#### connections

templates are the machinery under the library modules: `emplace_back` and `make_unique` are variadic forwarding templates, and algorithms are function templates over iterator types. the error-handling module next uses `if constexpr` and `std::variant` together, and the C++20 modules replace `enable_if` with concepts ([day 60](#day-60)) and extend compile-time evaluation ([day 69](#day-69)). static polymorphism ([day 97](#day-97)) returns to templates as a design tool rather than a mechanism.

[back to the curriculum map](#curriculum)

---

<a id="module-results"></a>

## module 8: results and failure

how functions hand back results and failures: unpacking, scoping, exception safety, error channels, and std::optional.

<a id="day-47"></a>

### day 47: structured bindings

**module 8:** results and failure · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** name the parts of pairs, tuples, arrays, and aggregates with structured bindings, and know what the qualifiers and names really refer to  
**builds on:** [day 35](#day-35) (maps, sets, and node handles), [day 08](#day-08) (temporaries, lifetime extension, and dangling references)

#### the idea

look at a typical pre-C++17 map loop or insertion: `it->first`, `it->second`, `result.first->second`, and `result.second` sprinkled through the body. nothing is wrong with it, but the names say nothing (`first` of what?), and every reader has to decode them again. structured bindings let you name the parts of a result where you receive it. the syntax is small; what it actually declares is less obvious than it looks.

#### understanding the concept

**structured bindings** let you give names to the parts of an object:

```cpp
auto [it, inserted] = counters.try_emplace(topic);
```

the mechanics matter more than the syntax. the compiler introduces a hidden variable, call it `e`, initialized from the right-hand side exactly as if you had written `auto e = counters.try_emplace(topic);`. the names `it` and `inserted` then refer to parts of `e`. everything written before the brackets (`auto`, `const auto&`, `auto&&`) applies to `e`, not to the individual names. (C++17 also forbids `static`, `thread_local`, and `constexpr` on a structured binding; C++20 allows the first two.)

there are three ways a type can be decomposed:

| kind | example | what the names refer to |
|---|---|---|
| array | `int a[3]` | the elements of `e` |
| tuple-like | `std::pair`, `std::tuple`, `std::array` | the results of `get<i>(e)`, via the tuple protocol |
| aggregate-ish class | `struct Pose { double x, y, theta; };` | the non-static data members of `e`, in declaration order |

the class case requires all non-static data members to be public and declared in the same class (or the same base). your own non-aggregate types can opt in by specializing `std::tuple_size`, `std::tuple_element`, and providing `get`; that is rarely worth the boilerplate.

two consequences follow from "names for parts of a hidden object":

- `auto [a, b] = obj;` copies the whole of `obj` into `e`. `auto& [a, b] = obj;` binds `e` to `obj`. and because `e` follows the normal rules from [day 08](#day-08), `const auto& [a, b] = make_pair_func();` extends the temporary's lifetime for as long as `e` lives.
- the names are not variables in the usual sense. `decltype(a)` yields the declared type of the member (`double`, not `double&`), and in C++17 a lambda cannot capture a structured binding. C++20 lifted that restriction. GCC 12 quietly accepts the capture even in `-std=c++17 -pedantic` mode, and other compilers in C++17 mode reject it or warn, so portable C++17 code uses an init-capture: `[a = a]`.

#### in code

first, predict the output. the binding names look like independent variables, but they are not.

```cpp complete
#include <cstdio>
#include <type_traits>

struct Pose { double x, y, theta; };

int main() {
    Pose p{1.0, 2.0, 0.5};

    auto [x, y, th] = p;       // hidden copy of p; x, y, th name its members
    x = 10.0;                  // modifies the copy

    auto& [rx, ry, rth] = p;   // hidden reference to p
    ry = 20.0;                 // modifies p.y

    std::printf("%.1f %.1f %.1f\n", x, p.x, p.y);         // prints: 10.0 1.0 20.0
    static_assert(std::is_same_v<decltype(ry), double>);   // not double&
}
```

#### in practice

a telemetry aggregator receives messages tagged with a topic string and keeps per-topic statistics. the hot path is "find or create the entry, then update it", and C++17 lets that read as one thought:

```cpp
#include <cstdint>

struct Stats { std::uint64_t count = 0; double last = 0.0; };

void on_message(std::map<std::string, Stats>& stats, const std::string& topic, double value) {
    auto [it, inserted] = stats.try_emplace(topic);   // one lookup, no default-then-assign
    if (inserted)
        std::printf("new topic: %s\n", topic.c_str());
    auto& [count, last] = it->second;
    ++count;
    last = value;
}
```

`try_emplace` ([day 35](#day-35)) returns `pair<iterator, bool>`; naming those parts `it` and `inserted` removes a whole category of `.first.second` confusion. the second binding uses `auto&` so updates land in the map rather than in a copy. note the design aspect: the binding names are local documentation, but they are not part of `Stats`'s interface. rename a member and nothing breaks here; reorder members and something does, which brings us to the trap.

#### watch out for

bindings to a class are **positional**. they follow member declaration order, not names:

```cpp
struct Range { double min_m, max_m; };
auto [lo, hi] = gate.range;          // lo = min_m, hi = max_m

// six months later someone "tidies" the struct:
struct Range { double max_m, min_m; };   // BUG: lo and hi silently swap
```

because both members are `double`, every use still compiles and no warning fires. field access by name (`r.min_m`) is immune. so use structured bindings freely for `pair`, `tuple`, map entries, and small local aggregates whose layout is effectively fixed (a 2D point). for a struct that lives in a widely used header and may evolve, member access is the more robust coupling. the same applies to returning a `std::tuple<double, double, double>` from an API: the bindings at the call site are only as good as everyone's memory of the order. a named struct is usually the better contract.

#### the takeaway

a structured binding names the parts of one hidden object: the qualifiers apply to that object, and the names follow member order, so use them freely for pairs, tuples, and map entries, and prefer member access for structs that may evolve.

#### optional challenge

what does this print, and why does the second loop compile even though `k` would have to be a `const std::string`?

```cpp
std::map<std::string, int> m{{"a", 1}};
for (auto [k, v] : m) v += 10;
std::printf("%d\n", m["a"]);
for (auto& [k, v] : m) v += 10;
std::printf("%d\n", m["a"]);
```

<details>
<summary>answer</summary>

it prints `1`, then `11`. in the first loop the hidden object is a copy of each `std::pair<const std::string, int>`, so `v += 10` modifies the copy. in the second loop the hidden object is an `auto&` bound to the map's element. the `auto&` deduces `std::pair<const std::string, int>&`, so `k` names a `const std::string` member and `v` names a mutable `int`. the `const` comes from the element type, not from the binding, which is why `auto&` works here without any `const` written by you.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-48"></a>

### day 48: if and switch initializers, and attributes that catch mistakes

**module 8:** results and failure · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** scope helper variables to the decision they serve with if and switch initializers, and use nodiscard, maybe_unused, and fallthrough to make intent checkable  
**builds on:** [day 47](#day-47) (structured bindings)

#### the idea

an iterator declared at function scope for one lookup stays in scope for the rest of the function, where it can be reused by mistake. a function whose result must be checked returns a `bool` that callers forget to look at. a `switch` case falls through to the next one, and nobody can tell whether that was intended. none of these is a bug yet; each is a place where intent lives in the author's head instead of in the code. C++17 added small features that move it into the code, where the compiler can check it.

#### understanding the concept

**init-statements** for `if` and `switch` (also C++17) let you declare a variable whose scope is the whole statement, including the `else` branch:

```cpp
if (auto it = m.find(key); it != m.end()) { /* use it */ } else { /* it is still in scope */ }
```

it is the same scoping rule `for` always had. the point is not saving a line; it is that a reader knows `it` cannot affect anything after the closing brace.

finally, three **standard attributes** became part of daily use in C++17. `[[nodiscard]]` asks the compiler to warn when a return value is ignored; it can go on a function or on a type, in which case every function returning that type by value is covered. `[[maybe_unused]]` silences unused warnings on a variable, parameter, or function. `[[fallthrough]]` documents an intentional fall-through in a `switch`. all three are hints: the standard only encourages a diagnostic, and the program's meaning never changes.

#### in code

second, a before/after modernization of a lookup in a joint-gain table.

```cpp
#include <cstdio>
#include <map>
#include <string>

// before: C++03 style
bool find_gain(const std::map<std::string, double>& gains,
               const std::string& joint, double& out) {
    std::map<std::string, double>::const_iterator it = gains.find(joint);
    if (it == gains.end())
        return false;
    out = it->second;
    return true;
}

// after: C++17
[[nodiscard]] bool find_gain(const std::map<std::string, double>& gains,
                             const std::string& joint, double& out) {
    if (auto it = gains.find(joint); it != gains.end()) {
        out = it->second;
        return true;
    }
    return false;
}

void dump(const std::map<std::string, double>& gains) {
    for (const auto& [joint, gain] : gains)          // instead of p.first, p.second
        std::printf("%s: %.3f\n", joint.c_str(), gain);
}
```

the `[[nodiscard]]` is the most valuable change here: with an out-parameter, a caller who ignores the `bool` and uses `out` anyway may read an uninitialized `double`, which is undefined behavior ([day 13](#day-13)). now they at least get a warning. the out-parameter itself is still awkward; [day 51](#day-51) replaces it with `std::optional<double>`.

third, `switch` with an initializer plus the other two attributes:

```cpp complete
#include <cassert>

enum class Mode { idle, homing, tracking, fault };

struct Controller {
    Mode mode() const;
    void zero_encoders();
    void run_loop();
    [[nodiscard]] bool push(double sample);
};

void step(Controller& c, double sample) {
    switch (auto m = c.mode(); m) {
    case Mode::homing:
        c.zero_encoders();
        [[fallthrough]];               // deliberate: homing also runs the loop
    case Mode::tracking:
        c.run_loop();
        break;
    case Mode::idle:
    case Mode::fault:
        break;
    }
    [[maybe_unused]] const bool ok = c.push(sample);
    assert(ok);                        // with NDEBUG, ok would otherwise be "unused"
}
```

without `[[fallthrough]]`, GCC and Clang warn under `-Wimplicit-fallthrough` (enabled by `-Wextra` in GCC). empty case labels stacked together, like `idle` and `fault`, never need it.

#### in practice

`[[nodiscard]]` pays off most when it is applied consistently rather than occasionally. good candidates: functions that return an error code or status, functions with no side effects (computing a value and dropping it is always a bug), `try_`-style operations whose result says whether anything happened, and factories that return a resource the caller must own. C++20 applied the same reasoning to the standard library: `empty()` on every container is `[[nodiscard]]`, which turns the classic slip `v.empty();` (meant: `v.clear();`) into a warning. building with `-Werror=unused-result` (GCC) or treating the corresponding warning as an error makes the attribute a rule instead of a suggestion.

#### watch out for

**an initializer lives for the whole statement, `else` included.** that is what makes it useful, and it also means a resource acquired there is held across every branch:

```cpp
#include <mutex>

void drain(std::mutex& m, bool& ready) {
    if (std::lock_guard lock{m}; ready) {
        ready = false;
    } else {
        slow_retry();      // still holding the lock: probably not what was meant
    }
}
```

the lock is released only at the end of the whole `if` statement. when a branch must run without the resource, keep the acquisition in a narrower scope of its own instead of the `if` initializer.

#### the takeaway

declare helper variables in the `if` or `switch` that uses them, so a reader knows they cannot leak into the rest of the function, and mark results that must not be ignored with `[[nodiscard]]`.

#### optional challenge

in which of the blocks `A`, `B`, `C`, and `D` are `it` and `jt` visible?

```cpp
if (auto it = m.find(k1); it != m.end()) { /* A */ }
else if (auto jt = m.find(k2); jt != m.end()) { /* B */ }
else { /* C */ }
/* D */
```

<details>
<summary>answer</summary>

`it` is visible in `A`, `B`, and `C`, because the `else if` is a nested `if` statement inside the first one's `else` branch. `jt` is visible in `B` and `C`. neither exists in `D`. that nesting is also why a chain of `else if` initializers can see all of the earlier ones.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-49"></a>

### day 49: exception safety guarantees

**module 8:** results and failure · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** state which guarantee (basic, strong, nothrow) an operation gives, and build the strong guarantee from work on the side plus a noexcept commit  
**builds on:** [day 25](#day-25) (the rule of zero), [day 17](#day-17) (scope guards: cleanup without a new class)

#### the idea

"is this function exception-safe?" is the wrong question, because it has no yes-or-no answer. the useful question is: if something in here throws halfway through, what state is the object left in? a tracker whose index map disagrees with its track list, a config that is half old and half new, a robot with half of a new trajectory: these are not crashes, they are worse. they are valid-looking objects that lie. exception safety is about making that question answerable, and an error-handling strategy is about deciding, per API, how failure is reported at all.

#### understanding the concept

there are three useful guarantees (Dave Abrahams' formulation, which the standard library documents its operations against):

| guarantee | promise if an exception escapes | example |
|---|---|---|
| **basic** | no leaks, all invariants hold, but the state may have changed | `std::vector::insert` in the middle |
| **strong** | commit or rollback: the state is as if the call never happened | `std::vector::push_back` (when the element's move is `noexcept` or it is copyable) |
| **nothrow** | the operation never fails | destructors, `swap`, `pop_back`, move constructors of most standard types |

anything below basic (a broken invariant or a leak) is simply a bug. RAII ([day 16](#day-16)) is what makes the basic guarantee cheap: if every resource is owned by an object, unwinding releases it without any `catch` blocks. the strong guarantee usually needs one more technique: **do all the work that can throw on the side, then commit with operations that cannot throw**. copy-and-swap ([day 25](#day-25)) is the classic form.

that commit step is why the nothrow guarantee matters, and why `noexcept` is a contract rather than an optimization hint. a function declared `noexcept` promises not to let an exception escape; if one tries, `std::terminate` is called, and whether the stack is unwound first is implementation-defined (with GCC 12, a local's destructor did not run before termination in a quick test). callers can query the promise at compile time with the `noexcept(expr)` operator, and the library does: `std::vector` reallocation uses `std::move_if_noexcept`, so it moves elements only if their move constructor is `noexcept` (or the type cannot be copied), otherwise it copies to keep `push_back` strong ([day 23](#day-23)).

#### in code

a track table with two structures that must agree. the first version leaves a broken invariant if the second step throws.

```cpp complete
#include <stdexcept>
#include <unordered_map>
#include <vector>

struct Track { int id; double range_m; };

class TrackTable {
    std::vector<Track> tracks_;
    std::unordered_map<int, std::size_t> index_;   // invariant: index_[t.id] == position of t
public:
    void add_broken(Track t) {
        tracks_.push_back(t);                                 // may throw: fine, nothing changed
        index_.emplace(t.id, tracks_.size() - 1);             // may throw: BUG, track without index
    }

    void add(Track t) {                                       // strong guarantee
        if (index_.count(t.id)) throw std::invalid_argument("duplicate track id");
        tracks_.push_back(t);                                 // strong on its own
        try {
            index_.emplace(t.id, tracks_.size() - 1);
        } catch (...) {
            tracks_.pop_back();                               // rollback cannot throw
            throw;                                            // rethrow the original exception
        }
    }
};
```

the `try`/`catch` rollback is fine for one step. with more steps, a scope guard ([day 17](#day-17)) that undoes on destruction unless dismissed keeps the code linear. a tempting alternative, `tracks_.reserve(tracks_.size() + 1)` before both steps, is a trap: calling it on every insert defeats geometric growth, because `reserve` may allocate exactly what you ask for, turning n inserts into O(n²) copying.

do-the-work-then-commit, for a configuration reload:

```cpp complete
#include <string>
#include <utility>
#include <vector>

class ControllerConfig {
    std::vector<double> gains_;
    std::string profile_;
public:
    static ControllerConfig parse(const std::string& text);   // may throw on bad input

    void reload(const std::string& text) {
        ControllerConfig next = parse(text);   // all failure-prone work happens on the side
        swap(next);                            // commit: cannot throw
    }                                          // old state is destroyed with 'next'

    void swap(ControllerConfig& other) noexcept {
        gains_.swap(other.gains_);
        profile_.swap(other.profile_);
    }
};
```

the strong guarantee costs a second object alive during the reload. that is cheap for a config and expensive for a 50 MB map, which is why the standard library gives only the basic guarantee for some operations: it refuses to charge every caller for rollback that most don't need.

#### in practice

the strong guarantee is worth its price where a half-applied change is dangerous: a robot's trajectory, a controller's configuration, a ledger, anything another component will act on as if it were complete. it is often not worth it for state that is merely a cache, a log buffer, or a working set the next cycle rebuilds anyway; there the basic guarantee (no leaks, invariants hold) is enough, and paying for a second copy of the data on every call would be waste. the useful habit is to decide per operation and write the decision into the API documentation ("`set_trajectory`: strong; `append_samples`: basic"), the way the standard library documents its own operations. callers can then reason about failure without reading your implementation.

#### watch out for

throw by value, catch by `const&`, and rethrow with a bare `throw;`:

```cpp complete
#include <cstdio>
#include <stdexcept>

void handle() {
    try {
        throw std::out_of_range("joint index 7");
    } catch (std::exception e) {   // BUG: copies and slices to std::exception (GCC: -Wcatch-value)
        std::puts(e.what());       // prints implementation-defined text; libstdc++: "std::exception"
        throw e;                   // throws a new std::exception: the out_of_range is gone
    }
}
```

catching by value slices the derived exception ([day 31](#day-31)) and loses its message; `throw e;` then throws that sliced copy, so callers catching `std::out_of_range` miss it. `catch (const std::exception& e)` and `throw;` preserve the original object and its dynamic type.

#### the takeaway

every operation should give at least the basic guarantee, and RAII makes that nearly free; pay for the strong guarantee where callers need commit-or-rollback, and build it from throwing work done on the side plus a `noexcept` commit.

#### optional challenge

which guarantee does this give, and how would you make it strong?

```cpp
void Planner::set_waypoints(const std::vector<Pose>& w) {
    waypoints_.clear();
    for (const auto& p : w) waypoints_.push_back(p);
}
```

<details>
<summary>answer</summary>

basic only. if a `push_back` throws partway, `waypoints_` holds a prefix of the new path: valid, no leaks, but neither the old nor the new state, which for a robot is the dangerous kind of valid. `waypoints_ = w;` looks like the fix but is not guaranteed to be strong either, because vector copy assignment may reuse its existing storage element by element. the strong version copies first and commits with a non-throwing swap: `std::vector<Pose> next(w); waypoints_.swap(next);`. the price is holding both vectors briefly.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-50"></a>

### day 50: choosing an error-handling strategy

**module 8:** results and failure · **reading time:** about 6 minutes · **standard:** C++17  
**objective:** choose between exceptions, error codes, optional values, and result types per API, based on how expected a failure is and who can act on it  
**builds on:** [day 49](#day-49) (exception safety guarantees)

#### the idea

every function that can fail answers a question it rarely states out loud: how does the caller find out? an exception, an error code, an empty `std::optional`, a result that holds either a value or a reason. each is right somewhere, and a codebase that picks at random per function is harder to use correctly than one that consistently uses any of them. choosing an error channel is an API design decision, made per layer and written down.

#### understanding the concept

exceptions are not the only error channel, and choosing one is an API decision:

| mechanism | fits when | costs and limits |
|---|---|---|
| exceptions | failure is rare and the immediate caller can't handle it; constructors | throwing is slow and its latency hard to bound; unwind tables add binary size; invisible in signatures |
| error codes (`enum`, `std::error_code`) | failure is expected and handled close by; C interop; `-fno-exceptions` builds | easy to ignore (use `[[nodiscard]]`); constructors can't return them |
| `std::optional<T>` | "no result" needs no explanation ([day 51](#day-51)) | carries no reason |
| result types (`std::variant<T, Error>`, [day 53](#day-53)) | value or a reason, checked by the caller | more verbose call sites; `std::expected` is C++23 only |

on mainstream ABIs (Itanium-style table-based unwinding, used by GCC and Clang on Linux), a `try` block adds essentially no work to the non-throwing path (it can still constrain some optimizations). throwing, though, allocates the exception object and searches unwind tables, so its cost is high and hard to bound. that is the honest basis for banning exceptions in hard real-time loops: not "exceptions are slow", but "a throw has no bounded latency". many embedded projects go further and compile with `-fno-exceptions`, where `throw` and `try` in your code fail to compile, and failures the standard library reports by throwing (`std::bad_alloc`, `at()` out of range) end the program instead, because no handler can exist. the exact mechanism depends on how the library was built.

#### in code

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

#### in practice

a robot arm driver library had one error convention everywhere: throw. that was right for `Arm::connect()`, called once at startup, where failure means the process cannot do its job and a clear exception with context is the best report. it was wrong for `Arm::read_joint_states()`, called at 1 kHz from the control loop, where a dropped packet is an expected event and the loop must decide within its cycle budget whether to hold position.

the revised API used a different channel per situation: `connect()` throws, the cyclic read returns a `[[nodiscard]]` status plus data, and constructors establish their invariants or throw. the rule behind it: decide by how expected the failure is, who can act on it, and the latency budget, then document the choice and apply it consistently per layer. two habits to avoid while you are at it: using exceptions for ordinary control flow (ending a parse loop by catching), and `catch (...) {}` that swallows a failure nobody will ever see. also avoid catching, logging, and rethrowing at every layer, which produces five log lines for one error.

#### watch out for

**error codes are easy to ignore, so make ignoring them visible.** a status return that the caller drops silently is worse than an exception, because the failure leaves no trace at all. `[[nodiscard]]` ([day 48](#day-48)) on the function (or on the error type itself, `enum class [[nodiscard]] Status { ... };`) makes the compiler warn when a call's result is discarded:

```cpp
parse_gate(user_line, g2);                  // warning: ignoring return value
static_cast<void>(parse_gate(user_line, g2));   // explicit, reviewable "I do not care"
```

a codebase that uses status returns should build with that warning treated as an error, or the channel is only as reliable as every caller's discipline.

#### the takeaway

choose the error channel per API from how expected the failure is, who can act on it, and how quickly they must react; then apply the choice consistently within a layer and make ignoring an error something the compiler notices.

#### optional challenge

pick an error channel for each: (a) opening the main configuration file at startup; (b) parsing 10,000 log lines a second, about 1% of them malformed; (c) a 1 kHz control loop reading a sensor that occasionally times out; (d) looking up a key in a cache that may not contain it.

<details>
<summary>answer</summary>

(a) an exception: it happens once, the process cannot do its job without the file, and a clear exception with context is the best report. (b) `std::optional` or an error code: malformed lines are expected, and throwing 100 exceptions a second for an ordinary outcome turns exceptions into control flow. (c) a `[[nodiscard]]` status (or a result type): the loop must decide within its cycle budget, and a throw has no bounded latency; such code is often built with `-fno-exceptions` anyway. (d) `std::optional` (or a pointer that may be null): a miss is a normal answer that needs no explanation.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-51"></a>

### day 51: `std::optional`: modeling "maybe"

**module 8:** results and failure · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** use `std::optional` for values whose absence is a normal outcome, and avoid its unchecked access, comparison, and bool traps  
**builds on:** [day 50](#day-50) (choosing an error-handling strategy), [day 48](#day-48) (if and switch initializers, and attributes that catch mistakes)

#### the idea

every code base has its own dialect for "there might not be a value": `-1` for "not found", `NaN` for "no reading", a `bool` return plus an out-parameter, a null pointer to a heap object that did not need to be on the heap. each dialect has a failure mode. `-1` is a valid value for some other caller, `NaN` poisons arithmetic silently, and the out-parameter ([day 48](#day-48)'s `find_gain`) leaves the caller holding an uninitialized `double` if they forget the check. C++17's `std::optional<T>` gives "maybe a `T`" a single, typed spelling that the compiler understands.

#### understanding the concept

`std::optional<T>` (header `<optional>`) holds either a `T` or nothing. the storage for the `T` lives *inside* the optional object, next to a flag: no heap allocation, and an empty optional has not constructed a `T` at all. the size is implementation-specific; it is at least `sizeof(T)` plus room for the flag, rounded up for alignment (`sizeof(std::optional<double>)` is 16 on mainstream 64-bit ABIs).

the access API is small, and the differences between its members are the whole point:

| expression | if engaged | if empty |
|---|---|---|
| `o.has_value()`, `if (o)` | `true` | `false` |
| `*o`, `o->m` | the value | undefined behavior |
| `o.value()` | the value | throws `std::bad_optional_access` |
| `o.value_or(d)` | a copy of the value | `d` converted to `T` |

`*o` is unchecked by design, like `vector::operator[]`; use it right after you have tested the optional. `value()` is the checked version, and `value_or` is for the common case of a sensible fallback. note that `value_or`'s argument is always evaluated, so `o.value_or(load_default_from_disk())` does the I/O even when `o` is engaged.

you create an empty optional with `std::nullopt` (or `{}`), and an engaged one by assigning a `T` or constructing in place: `o.emplace(args...)` and `std::optional<T> o(std::in_place, args...)` construct the `T` directly in the optional's storage, which matters for types that are expensive or impossible to move.

there is no `std::optional<T&>` in C++17 (it is ill-formed; C++26 adds it). for "maybe refers to an existing object", a `T*` is the idiomatic answer and already means exactly that ([day 09](#day-09)).

comparisons are defined between optionals, against `std::nullopt`, and against plain `T` values, with one rule to remember: an empty optional compares less than any engaged one.

finally, the design meaning. returning `std::optional<T>` is a contract: "absence is a normal outcome and you must handle it". that is different from an exception ([day 50](#day-50)), which says "this should not happen in normal operation". what optional cannot say is *why* the value is missing; when callers need the reason, use a result type ([day 53](#day-53)) or an exception.

#### in code

[day 48](#day-48)'s out-parameter lookup, finished:

```cpp complete
#include <map>
#include <optional>
#include <string>

[[nodiscard]] std::optional<double>
find_gain(const std::map<std::string, double>& gains, const std::string& joint) {
    if (auto it = gains.find(joint); it != gains.end())
        return it->second;
    return std::nullopt;
}

void apply_gain(double);

void configure(const std::map<std::string, double>& gains) {
    if (auto kp = find_gain(gains, "elbow"))      // kp is scoped to the if
        apply_gain(*kp);                          // checked just above: * is fine
    double kd = find_gain(gains, "wrist").value_or(0.1);
    apply_gain(kd);
}
```

the caller cannot read the value without going through the optional, and the type says "may be missing" in the signature instead of in a comment.

now predict the output. two of these surprise most people.

```cpp complete
#include <iostream>
#include <optional>
#include <string>

int main() {
    std::optional<int> a;            // empty
    std::optional<int> b = 0;
    std::cout << (a < b) << (a < -100) << (b == 0) << '\n';   // prints: 111

    try {
        std::cout << a.value() << '\n';
    } catch (const std::bad_optional_access& e) {
        std::cout << "empty\n";                                // prints: empty
    }

    std::optional<std::string> s = "fix";
    auto t = std::move(s);
    std::cout << s.has_value() << '\n';                        // prints: 1
}
```

`a < -100` is `true` because empty is less than every value, including negative ones; a range check like `if (reading < limit)` on an optional quietly passes when there is no reading. and moving from an optional does not make it empty: `s` is still engaged and holds a moved-from string (valid but unspecified, [day 21](#day-21)). if you need it empty, call `s.reset()`.

#### in practice

in a localization node, a GNSS fix is genuinely optional: you may not have one yet, or it may be too old to trust. that is exactly what a member should model:

```cpp
class Localizer {
public:
    void on_gnss(const GnssFix& fix) { last_fix_ = fix; }
    [[nodiscard]] std::optional<Pose> pose_at(Timestamp t) const;  // empty if no usable fix
private:
    std::optional<GnssFix> last_fix_;        // "never received" is distinct from any fix value
};
```

compare the alternatives. a `GnssFix` with a `valid` flag lets every reader forget to check it. a `std::unique_ptr<GnssFix>` adds a heap allocation and pointer semantics for no ownership benefit. the optional keeps the data inline and makes the check visible.

#### watch out for

`std::optional<bool>` and `std::optional<T*>` turn a one-character mistake into a logic bug:

```cpp
std::optional<bool> brake_engaged = read_brake_sensor();   // empty on sensor timeout

if (brake_engaged)                 // BUG: means "we got a reading", not "brake is on"
    release_parking_hold();

if (brake_engaged.value_or(true))  // fixed, and the fallback is a safety decision:
    release_parking_hold();        // treat "unknown" as "engaged"
```

the contextual conversion to `bool` tests engagement, whatever `T` is. with `std::optional<bool>`, `if (o == true)` or `value_or` make the intent explicit, and the fallback value deserves a comment because it encodes policy. with `std::optional<Sensor*>` you have two kinds of nothing (`nullopt` and `nullptr`); unless those genuinely mean different things in your domain, a plain pointer is simpler. some static analyzers flag these patterns; compilers generally do not.

#### the takeaway

use `std::optional<T>` when absence is a normal, expected outcome: it stores the value inline, puts "maybe" in the type, and makes the check hard to skip. remember that `*` is unchecked, empty compares less than everything, moved-from optionals stay engaged, and `if (o)` never looks at the value inside.

#### optional challenge

a radar driver exposes `std::optional<std::vector<Detection>> detections()`. a reviewer suggests returning a plain `std::vector<Detection>` and using an empty vector for "nothing". when is the reviewer right, and when is the optional worth keeping?

<details>
<summary>answer</summary>

if "no scan happened" and "the scan found no targets" are handled the same way by every caller, the empty vector is simpler and the optional is just an extra layer to unwrap. if they mean different things (a tracker should coast tracks through a missing scan but may delete them after a genuinely empty scan), then the distinction is real information and the optional is the honest return type. and if callers need to know *why* there was no scan (timeout, CRC error, blanking interval), neither is enough: that is a job for a result type ([day 53](#day-53)) or an exception.

</details>

#### going deeper (optional)

##### in-place construction

in-place construction for a type that should not be copied around:

```cpp complete
#include <optional>

struct Track {
    Track(int id, double range_m, double vel_mps) : id(id), range_m(range_m), vel_mps(vel_mps) {}
    Track(const Track&) = delete;            // tracks have identity; no accidental copies
    Track& operator=(const Track&) = delete;
    int id; double range_m; double vel_mps;
};

std::optional<Track> lead;                   // no Track constructed yet
void on_new_target(int id, double r, double v) {
    lead.emplace(id, r, v);                  // destroys any old Track, builds the new one in place
}
```

##### optional parameters

parameters are a different story. `void configure(std::optional<Limits> limits = std::nullopt)` constructs an optional (and copies the `Limits`) at every call, and the function body is one big `if`. two overloads, `configure()` and `configure(const Limits&)`, are usually clearer. if the argument is a borrowed object that may be absent, `const Limits*` says that with no copy at all.

##### C++23 monadic operations

C++23 note: `and_then`, `transform`, and `or_else` (the "monadic" operations) let you chain optional-returning steps without nested `if`s. they are not in C++17 or C++20.

[back to the curriculum map](#curriculum)

---

<a id="day-52"></a>

### day 52: review: results and failure

**module 8:** results and failure · **reading time:** about 6 minutes · **standard:** C++17  
**objective:** consolidate structured bindings, if and switch initializers, exception safety, error-handling strategy, and `std::optional`  
**covers:** [day 47](#day-47) to [day 51](#day-51)

#### recap

| lesson | key idea |
|---|---|
| [day 47](#day-47) | a structured binding names the parts of one hidden object; qualifiers apply to that object, names follow member order. |
| [day 48](#day-48) | `if`/`switch` initializers scope helpers to the decision; `[[nodiscard]]` makes ignored results visible. |
| [day 49](#day-49) | basic, strong, nothrow: RAII makes basic nearly free, and strong comes from work on the side plus a `noexcept` commit. |
| [day 50](#day-50) | choose exceptions, error codes, optional, or result types per API from how expected the failure is and who can act on it. |
| [day 51](#day-51) | "maybe a `T`", stored inline: `*` is unchecked, `value()` throws, empty compares less than everything, `if (o)` tests engagement. |

the thread through the module: **a function's result is part of its contract**, including the results it produces when something goes wrong.

#### review questions

1. does `auto& [id, range] = make_track();` compile if `make_track()` returns a `std::pair<int, double>` by value? what about `const auto&` and `auto&&`, and what happens to the pair's lifetime in those cases?
2. `Planner::set_waypoints` clears its vector and then pushes the new waypoints one by one. which guarantee does it give, and why is `waypoints_ = w;` not automatically the fix?
3. a guard reads `if (latest_temp_c < max_temp_c) keep_running();` where `latest_temp_c` is `std::optional<double>` and `max_temp_c` is a `double`. what happens when no temperature has been received, and how would you rewrite it?
4. a 1 kHz control loop calls a function that throws on a sensor timeout, which happens a few times a minute. what is wrong with that, and what would you change?
5. from [day 42](#day-42): in `template <class... Ts> void emit(Ts&&... xs)`, what kind of references are the parameters? write one expression that passes every argument to `sink(...)`, one call per argument, in order, preserving each argument's value category.

#### mini exercise

`find_gain` from [day 48](#day-48) still uses an out-parameter. rewrite it to return `std::optional<double>`, then write the call site that applies a default gain of 0.1 when the joint is missing.

#### answers

<details>
<summary>answer 1: binding a returned pair</summary>

`auto&` does not compile: the hidden object would be a non-const lvalue reference, which cannot bind to the prvalue `make_track()` ([day 11](#day-11)). both `const auto&` and `auto&&` compile: the hidden reference binds directly to the temporary, so its lifetime is extended to match the hidden reference, which lives as long as the bindings' scope ([day 08](#day-08)). with `const auto&`, `id` and `range` are const; with `auto&&`, they are modifiable.

</details>

<details>
<summary>answer 2: which guarantee</summary>

basic only: if a `push_back` throws partway, `waypoints_` holds a prefix of the new path, which is valid but neither old nor new. vector copy assignment may reuse the existing storage element by element, so it is not guaranteed to be strong either. the strong version copies on the side and commits with a non-throwing swap: `std::vector<Pose> next(w); waypoints_.swap(next);`.

</details>

<details>
<summary>answer 3: comparing an empty optional</summary>

an empty optional compares less than any value, so the condition is `true` and the system keeps running with no temperature reading at all. that is a fail-open bug. make the missing case explicit and choose the safe policy: `if (latest_temp_c && *latest_temp_c < max_temp_c) keep_running();`, which stops (or degrades) when there is no reading. the comparison operators are convenient for sorting; in guards, test engagement first.

</details>

<details>
<summary>answer 4: exceptions in a control loop</summary>

the timeout is an expected outcome, not an exceptional one, so throwing turns exceptions into control flow; and a throw has no bounded latency, which a 1 kHz loop cannot afford. return a `[[nodiscard]]` status or a `std::optional` reading instead, so the loop can decide within its cycle budget (hold the last value, or command a safe stop), and keep exceptions for failures that end the loop's usefulness.

</details>

<details>
<summary>answer 5: forwarding a pack</summary>

they are forwarding references ([day 42](#day-42)): `Ts&&` in a deduced context, with `Ts` deduced as an lvalue reference type for lvalue arguments. the expression is a comma fold ([day 45](#day-45)): `(sink(std::forward<Ts>(xs)), ...);`. the built-in comma operator guarantees left-to-right order, and `std::forward<Ts>` restores each argument's original value category. (if `sink` returned a type that overloads `operator,`, cast each call to `void`.)

</details>

<details>
<summary>mini exercise answer</summary>

```cpp complete
#include <map>
#include <optional>
#include <string>

[[nodiscard]] std::optional<double>
find_gain(const std::map<std::string, double>& gains, const std::string& joint) {
    if (auto it = gains.find(joint); it != gains.end())
        return it->second;
    return std::nullopt;
}

double wrist_gain(const std::map<std::string, double>& gains) {
    return find_gain(gains, "wrist").value_or(0.1);
}
```

the caller can no longer read an uninitialized `double` by forgetting a check, and the default is stated where it is applied. if the default were expensive to compute, `value_or` would compute it even when the gain exists, so a branch on the optional would be better.

</details>

#### connections

this module was about the edges of a function: what comes out, how it is unpacked, and what happens when it fails. the next one finishes the C++17 vocabulary with types that model "one of several" (`std::variant`), "borrowed text" (`std::string_view`), and "a path" (`std::filesystem::path`), and then uses all of it in a realistic refactoring.

[back to the curriculum map](#curriculum)

---

<a id="module-cpp17"></a>

## module 9: variants, views, and files

the rest of the C++17 vocabulary, used together in a realistic refactoring; the end of the standalone refresher.

<a id="day-53"></a>

### day 53: `std::variant` and `std::visit`

**module 9:** variants, views, and files · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** model "exactly one of these types" with `std::variant`, consume it with an exhaustive `std::visit`, and use it as a result type  
**builds on:** [day 51](#day-51) (`std::optional`: modeling "maybe"), [day 45](#day-45) (fold expressions), [day 37](#day-37) (lambdas are objects: closures and captures)

#### the idea

a radar front end emits three kinds of messages: raw detections, track updates, and heartbeats. the pre-C++17 options were all uncomfortable. a C `union` plus a tag `enum` is fast but nothing stops you reading the wrong member (undefined behavior) or forgetting to destroy a `std::string` member. a `Message` base class with three subclasses ([day 30](#day-30)) is safe but heap-allocates every message, adds pointer chasing, and invites `dynamic_cast` ladders in the consumer. [day 51](#day-51)'s `std::optional` was "a `T` or nothing". today is the generalization: "exactly one of these types", with the compiler keeping track of which.

#### understanding the concept

`std::variant<A, B, C>` (header `<variant>`) holds exactly one value of one of its alternative types, stored inline (no heap allocation by the variant itself), plus an index saying which one. its size is at least that of the largest alternative plus room for the index. assigning a different alternative destroys the old value and constructs the new one, so the lifetime bugs of a raw union cannot happen.

access comes in three strengths:

- `std::holds_alternative<T>(v)` and `v.index()` ask what is there.
- `std::get<T>(v)` (or `std::get<I>(v)`) returns a reference and throws `std::bad_variant_access` on a mismatch.
- `std::get_if<T>(&v)` returns a pointer, `nullptr` on a mismatch. this is the non-throwing "check and use" form.

the idiomatic way to consume a variant, though, is `std::visit(f, v)`, which calls `f` with the active alternative. if `f` cannot be called with one of the alternatives, the program does not compile, which gives you exhaustiveness checking for free. the usual way to build `f` from several lambdas ([day 37](#day-37)) is the `overloaded` helper:

```cpp complete
template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };
template <class... Fs> overloaded(Fs...) -> overloaded<Fs...>;   // needed in C++17 only
```

it inherits from every lambda's closure type and pulls in all their call operators, so normal overload resolution picks the right one. in C++17 the deduction guide is required; C++20 lets CTAD deduce template arguments for aggregates directly, so the second line becomes unnecessary (though harmless).

three details complete the picture. a default-constructed variant holds a value-initialized first alternative, so the first type must be default constructible, or you put `std::monostate` first as an explicit "empty" alternative. if constructing the new alternative throws after the old one was destroyed, the variant becomes `valueless_by_exception()`: `index()` returns `std::variant_npos` and `visit` throws `bad_variant_access`. this needs a throwing constructor or move to occur mid-assignment, which is rare, but it means a variant's "always one of the types" invariant has one documented escape hatch. finally, the set of alternatives is fixed at compile time, which is the design decision that matters most.

#### in code

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

#### in practice

a variant as a result type, the error-handling option promised on [day 50](#day-50). it carries the reason that `std::optional` could not:

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

#### watch out for

the converting constructor picks an alternative by overload resolution, and implicit conversions can surprise you:

```cpp
std::variant<std::string, bool> v = "abc";   // which alternative?
```

under the original C++17 wording this stored `bool`: `const char*` to `bool` is a standard conversion and beat the user-defined conversion to `std::string`. C++20 (paper P0608) excluded narrowing and boolean conversions from this selection, so it now stores the `std::string`. GCC 12's libstdc++ applies the fix even with `-std=c++17` (index 0, checked), but older standard libraries do not. the robust habits: avoid alternatives that convert into each other (`bool`, `int`, `double` together is asking for trouble), and when in doubt, say what you mean with `std::in_place_type<std::string>` or by constructing the alternative explicitly.

#### the takeaway

`std::variant` is a value-semantic sum type with inline storage: consume it with `std::visit` and explicit per-type lambdas, so the compiler checks that every alternative is handled.

#### optional challenge

given `using Msg = std::variant<std::monostate, Detection, Heartbeat>;` and `Msg m;`, what do `m.index()`, `std::get_if<Detection>(&m)`, and `std::get<Detection>(m)` give, and what changes after `m = Heartbeat{1};`?

<details>
<summary>answer</summary>

a default-constructed variant holds a value-initialized first alternative, here `std::monostate`, so `m.index()` is 0, `std::get_if<Detection>(&m)` returns `nullptr`, and `std::get<Detection>(m)` throws `std::bad_variant_access`. after the assignment, `index()` is 2 and the `Detection` accessors behave the same way, while `std::get<Heartbeat>(m).seq` is 1. putting `std::monostate` first is the explicit way to give a variant an "empty" state when none of the real alternatives has a sensible default.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-54"></a>

### day 54: closed sets and open sets: variant state machines and `std::any`

**module 9:** variants, views, and files · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** choose between `std::variant`, virtual functions, and `std::any` by whether the set of types is closed, open, or unknowable  
**builds on:** [day 53](#day-53) (`std::variant` and `std::visit`), [day 32](#day-32) (composition, interfaces, and substitutability)

#### the idea

a radar library has two kinds of polymorphism. its message types (detection, track update, heartbeat) are defined by the protocol and change only when the protocol does. its detectors are written by users, in code the library has never seen. a single mechanism cannot serve both well. the choice between a variant and a virtual interface is not a matter of taste; it follows from one question: who gets to add new types?

#### understanding the concept

**closed versus open.** with inheritance, adding a new message type means writing one new class, but adding a new operation means touching every class (or adding a virtual function to the base). with a variant, adding an operation is one new visitor, but adding a type means updating every visitor, and the compiler will point at each one. this is the "expression problem" in one paragraph. use a variant when the set of types is small, known, and owned by you (protocol messages, states, parse results). use virtual functions when the set must be open to code you do not control (plugins, user-supplied sensors). variants also give you value semantics: they copy, compare, and live in a `std::vector` contiguously.

`std::any` (header `<any>`) is the other end of the spectrum: it holds a single value of *any* copy-constructible type, with the type erased. you get it back with `std::any_cast<T>`, which must name the exact stored type (no conversions, no base classes). small objects may be stored inline; whether and how much is implementation-specific, and larger types are heap-allocated. because the type information is gone from the interface, every reader has to guess and check. legitimate uses are narrow: a framework that carries a user's context object through code that never looks inside it, or a heterogeneous property bag at a plugin boundary. if you can list the possible types, you want a variant.

#### in code

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

#### in practice

the radar library uses both mechanisms, each where it fits. `RadarMsg` is a `std::variant`: the library owns the protocol, consumers visit messages by value in tight loops, and adding a message type is a deliberate protocol change whose consequences the compiler enumerates. `Detector` is an abstract class with a virtual `detect()`: users ship new detectors without touching the library, and the library calls them once per frame through `std::unique_ptr<Detector>`. a project that forced messages into a class hierarchy would pay for heap allocation per message and lose exhaustiveness checking; one that forced detectors into a variant would make every user edit the library to add a type. the design question is the same one in both cases, and the answers differ because the owners differ.

#### watch out for

**a catch-all lambda turns off exhaustiveness checking.** a generic lambda accepts every alternative, including ones added later:

```cpp
std::visit(overloaded{
    [](const Detection& d) { record(d); },
    [](const auto&) {},                  // "ignore everything else"
}, msg);
```

when `Calibration` joins the variant, this visit compiles unchanged and silently drops calibration messages. sometimes that is exactly right; often it is a bug that the variant would otherwise have caught. prefer one explicit lambda per alternative in code that must react to every message type, and reserve catch-alls for visitors that genuinely care about only one or two.

#### the takeaway

use a variant when you own a small, fixed set of types, virtual functions when the set must stay open to code you do not control, and `std::any` only where the code genuinely must not know the type.

#### optional challenge

your team adds a fourth radar message, `Calibration`. with the variant design, what does the compiler do for you, and what does it not do? what would the answer be with a `Message` base class and virtual `handle()`?

<details>
<summary>answer</summary>

with the variant, every `std::visit` built from explicit per-type lambdas stops compiling until it handles `Calibration`, so the compiler hands you a list of places to update. it does not help where someone used a generic `auto` catch-all lambda or `get_if` checks, which silently ignore the new type. with the base class, adding `Calibration` means writing one class and implementing the pure virtuals; existing consumers compile unchanged, which is great if they never need to know, and a silent gap if some of them should have treated calibration specially. closed sets trade "edit many places" for "the compiler finds them"; open sets trade the opposite way.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-55"></a>

### day 55: `std::string_view`: borrowing characters

**module 9:** variants, views, and files · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** use `std::string_view` for read-only string parameters, and avoid the null-terminator and lifetime traps of a non-owning view  
**builds on:** [day 51](#day-51) (`std::optional`: modeling "maybe"), [day 08](#day-08) (temporaries, lifetime extension, and dangling references)

#### the idea

`void log_topic(const std::string& topic)` looks like the efficient way to accept a read-only string. now call it with a literal, `log_topic("/robot/arm/joint_states")`. the parameter needs a `std::string`, so the compiler builds a temporary one, which allocates if the text is longer than the small-string buffer (an implementation-defined capacity, 15 characters in libstdc++). call it with a substring of a larger buffer and you must first copy that substring into a `std::string`. the function only wanted to *read* some characters. C++17's `std::string_view` lets it say exactly that.

#### understanding the concept

a `std::string_view` (header `<string_view>`) is a pointer and a length, nothing more. it does not own the characters, never allocates, and is cheap to copy, so you pass it by value. three properties define how you use it:

- **it borrows.** the characters belong to someone else (a `std::string`, a literal, a receive buffer, a memory-mapped file). the view is valid only while that owner is alive and unmodified. this is the same contract as a reference or raw pointer ([day 09](#day-09)), with the same failure mode: dangling.
- **it is not necessarily null-terminated.** a view of `"x=1,y=2"` from offset 0, length 3 sees `x=1`, but the byte after it is `,`. there is no `c_str()` for a reason.
- **slicing is free.** `substr`, `remove_prefix`, and `remove_suffix` just adjust the pointer and length: O(1), no allocation. (`std::string::substr` returns a new string; `std::string_view::substr` returns a new view.)

conversions are asymmetric, and that is good API design: `std::string` converts *implicitly* to `std::string_view` (cheap and safe while the string lives), while `std::string_view` converts to `std::string` only *explicitly* (`std::string(sv)`), because that allocates and you should see it.

#### in code

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

#### in practice

moving an existing library to `std::string_view` parameters is a mechanical change with one judgment call per function. a function that only reads its argument during the call (`has_prefix`, `log_topic`, a lookup key) takes `std::string_view`, and every caller that passed a literal or a slice stops allocating. a function that *stores* the string (a setter, a constructor that keeps a name) should take `std::string` by value and move it into the member, so the class owns its characters. a function that hands the text to a C API that needs a terminator keeps `const std::string&` or `const char*`. changing a parameter from `const std::string&` to `std::string_view` is source compatible for callers, because `std::string` converts implicitly; it is not ABI compatible, so a shared library changing its exported functions needs a new version.

#### watch out for

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

reading through any of these views is undefined behavior. [day 08](#day-08)'s lifetime-extension rule does not rescue you: extension applies when a *reference* binds directly to a temporary, but a `string_view` is an object that merely holds a pointer into it. Clang flags some of these patterns with its `-Wdangling` family of warnings, and AddressSanitizer catches the reads at runtime, but the reliable defense is a rule: use `string_view` for parameters and for short-lived locals, and store `std::string` in members unless the class is explicitly a borrowing view type with a documented lifetime contract. also remember that a view into a `std::string` is invalidated by anything that may reallocate that string, just like a vector iterator ([day 34](#day-34)).

`std::string_view` is the first of the standard's **non-owning views**. [day 65](#day-65)'s `std::span` does the same for contiguous arrays of any type, and C++20 ranges views ([day 63](#day-63)) generalize the idea. the design question is always the same: does this component *own* the data, or *borrow* it for the duration of a call?

#### the takeaway

`std::string_view` is a borrowed pointer and length: ideal for read-only parameters and zero-copy parsing, wrong for anything that outlives the call unless the owner provably outlives it. make copies to `std::string` explicit, and never hand `data()` to a function that expects a null terminator.

#### optional challenge

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

[back to the curriculum map](#curriculum)

---

<a id="day-56"></a>

### day 56: parsing without allocation: views and from_chars

**module 9:** variants, views, and files · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** parse and format text without allocating, using string_view slicing with `std::from_chars` and `std::to_chars`  
**builds on:** [day 55](#day-55) (`std::string_view`: borrowing characters), [day 47](#day-47) (structured bindings)

#### the idea

a log-analysis tool ingests hours of GNSS data: millions of short comma-separated NMEA sentences. the obvious parser splits each line into `std::string` fields and calls `std::stod` on the ones it needs, allocating and copying for every field of every line, and consulting the global locale on every number. none of that work is needed to read a few digits out of a buffer you already hold. views for slicing and `<charconv>` for numbers do the same job touching each byte once.

#### understanding the concept

the parsing partners are `std::from_chars` and `std::to_chars` (header `<charconv>`, C++17). unlike `std::stod` or `strtod`, they take a `[first, last)` character range (perfect for a view), never allocate, never throw, ignore the locale, and report errors through a returned `{ptr, ec}` struct, which unpacks neatly with a structured binding ([day 47](#day-47)). `from_chars` does not skip leading whitespace or accept a leading `+`. integer support is universal; floating-point support arrived later in some standard libraries (libstdc++ has it from GCC 11), so check your toolchain before relying on it.

the slicing half of the toolkit is `std::string_view` itself: a tokenizer holds the unparsed remainder as a view, finds the next delimiter, returns the field as a view, and shortens the remainder with `remove_prefix`. nothing is copied, and every field is a window into the original line, so the whole parse is valid exactly as long as that line is.

#### in code

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

notice how the C++17 vocabulary composes: views for the slices, a structured binding for the `from_chars` result, `std::optional` for "this field may be empty or garbage". whether it is measurably faster than a `std::string`-based parser depends on line lengths and the allocator; count allocations ([day 109](#day-109) shows how) and profile before claiming a speedup. the design gain is certain either way: the parser's signature says it borrows the line and keeps nothing.

#### in practice

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

#### watch out for

**`from_chars` parses a prefix and stops.** it reports success as long as it could read *something*, and tells you where it stopped:

```cpp
double v{};
std::string_view s = "12.5abc";
auto [ptr, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
// ec == std::errc{}, v == 12.5, ptr points at 'a'
```

checking only `ec` accepts `"12.5abc"` as 12.5, which is why `to_double` also compares `ptr` with the end of the input. the other differences from `strtod` and `std::stod` matter just as much when porting a parser: no leading whitespace is skipped, a leading `+` is rejected, and an out-of-range value reports `std::errc::result_out_of_range` instead of returning infinity.

#### the takeaway

slice with `std::string_view`, convert numbers with `from_chars` and `to_chars`, and check both the error code and the end pointer; the parse is then allocation-free and locale-free, and valid exactly as long as the buffer it borrows.

#### optional challenge

using `to_double` from the code above, what do these return: `to_double("545.4")`, `to_double(" 12")`, `to_double("+5")`, `to_double("1e3")`, `to_double("")`?

<details>
<summary>answer</summary>

`545.4`, empty, empty, `1000`, and empty. `" 12"` fails because `from_chars` does not skip whitespace; `"+5"` fails because a leading plus sign is not accepted; `"1e3"` is valid scientific notation in the default general format; and an empty range reports `std::errc::invalid_argument`. if the input really can contain leading spaces or a plus sign, strip them explicitly before calling `from_chars`, so the accepted format is written down in your code.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-57"></a>

### day 57: `std::filesystem`: portable paths and directories

**module 9:** variants, views, and files · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** compose and inspect paths with `std::filesystem`, choose between its throwing and error_code overloads, and avoid check-then-use races  
**builds on:** [day 50](#day-50) (choosing an error-handling strategy), [day 55](#day-55) (`std::string_view`: borrowing characters)

#### the idea

`std::string(dir) + "/" + name` works until the code runs on Windows, the directory name already ends in a slash, or the file name contains a character in a different encoding. `opendir` and `readdir` work until an early `return` skips `closedir`. file-system code is where portable C++ used to stop and platform `#ifdef`s began. C++17's `std::filesystem` makes paths a value type and directory traversal an RAII iterator, with a deliberate choice of error reporting at every call.

#### understanding the concept

`std::filesystem` (header `<filesystem>`, conventionally aliased `namespace fs = std::filesystem;`) standardizes what used to be POSIX `dirent.h`, Win32 `FindFirstFile`, or Boost.Filesystem. on GCC 8 it needed `-lstdc++fs` at link time; from GCC 9 it is part of the main library.

`fs::path` is a value type holding a path in the platform's native format (`char` on POSIX, `wchar_t` on Windows). you compose with `/`, and you decompose with `filename()`, `stem()`, `extension()`, and `parent_path()`. these are pure string operations: they never touch the disk. converting back to `std::string` with `.string()` may have to transcode on Windows, so pass `fs::path` itself to APIs that accept it, including `std::ifstream`, whose constructor takes a `path` since C++17.

operations that do touch the disk (`exists`, `is_regular_file`, `file_size`, `create_directories`, `rename`, `remove`, iteration) come in two overloads:

- without an error argument, they throw `fs::filesystem_error`, which carries the paths and an `std::error_code`;
- with a trailing `std::error_code& ec`, they report failure through `ec` instead.

choose per call site with [day 50](#day-50)'s rule: if the failure is exceptional for this program (the config directory is missing at startup), throw; if it is an expected outcome (a file vanished from a drop directory between scans), use the `error_code` overload.

two semantic details trip people up. `fs::directory_iterator` and `fs::recursive_directory_iterator` visit entries in an **unspecified order**: it is whatever the file system returns, and it differs between machines. and the file system is shared mutable state: another process can change it between any two of your calls, which is the subject of today's watch-out.

#### in code

the basics, with no I/O until the last line:

```cpp complete
#include <filesystem>
#include <iostream>
namespace fs = std::filesystem;

int main() {
    const fs::path root = "/var/log/robot";
    const fs::path log = root / "arm" / "joint_states.2026-10-30.csv";
    std::cout << log.filename() << ' ' << log.stem() << ' ' << log.extension() << '\n';
    // prints: "joint_states.2026-10-30.csv" "joint_states.2026-10-30" ".csv"
    std::error_code ec;
    const auto bytes = fs::file_size(log, ec);              // no throw
    if (ec) std::cout << "no file: " << ec.message() << '\n';
    else    std::cout << bytes << " bytes\n";
}
```

the quotes come from `operator<<` for `path`, which writes the path quoted (as if by `std::quoted`) so that paths with spaces round-trip. use `.string()` when you want the raw text.

#### in practice

a disk-usage monitor in a long-running service must never throw just because a log rotator deleted a file between listing and measuring it. the `error_code` overloads make that explicit:

```cpp complete
#include <cstdint>
#include <filesystem>
#include <system_error>
namespace fs = std::filesystem;

std::uintmax_t total_bytes(const fs::path& dir) {
    std::uintmax_t total = 0;
    std::error_code ec;
    for (fs::recursive_directory_iterator it(dir, ec), end; !ec && it != end; it.increment(ec)) {
        std::error_code fe;
        const auto size = it->file_size(fe);    // may fail: vanished file, or a directory
        if (!fe) total += size;                 // skip what cannot be measured
    }
    return total;
}
```

the outer `ec` stops the walk if the directory itself cannot be read; the inner one skips individual entries that disappear or are not regular files. the same function written with the throwing overloads would be shorter and would fail in production the first time a file vanished mid-scan.

#### watch out for

the classic file-system bug is **check-then-use**, a time-of-check to time-of-use (TOCTOU) race:

```cpp
if (fs::exists(p) && fs::file_size(p) > max_bytes)   // BUG: p can vanish or change in between
    fs::remove(p);
```

between `exists` and `file_size`, a log rotator can delete or replace the file, and `file_size` then throws. worse, in security-sensitive code, an attacker can swap `p` for a symlink between the check and the `remove`. the checks do not make the operation safe; they only narrow the window. prefer to attempt the operation and handle the failure:

```cpp
std::error_code ec;
if (const auto size = fs::file_size(p, ec); !ec && size > max_bytes)
    fs::remove(p, ec);          // still racy in principle, but never throws, and ec reports what happened
```

truly atomic guarantees come from the operating system (opening a file once and working on the handle, `O_CREAT | O_EXCL`, an atomic `rename` to publish a file), not from `std::filesystem`, which only names paths.

#### the takeaway

`std::filesystem` gives portable paths and directory operations with a choice of exceptions or error codes per call; path operations never touch the disk, and checking before acting never makes a file-system operation safe.

#### optional challenge

on a POSIX system, what do these produce?

```cpp
fs::path("logs") / "/tmp/x"             // (1)
fs::path("data/run1/").filename()       // (2)
fs::path("archive.tar.gz").extension()  // (3)
```

<details>
<summary>answer</summary>

(1) `"/tmp/x"`: appending an absolute path replaces the left-hand side instead of concatenating, a frequent surprise when the right operand comes from user input. (2) an empty path: with a trailing separator, the last element is empty, so `filename()` is `""` (strip the trailing separator first if you want `"run1"`). (3) `".gz"`: `extension()` is only the part after the last dot, and `stem()` would be `"archive.tar"`.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-58"></a>

### day 58: a practical C++17 refactoring

**module 9:** variants, views, and files · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** modernize a legacy function one justified change at a time, stating every behavior change and keeping owning types at ownership boundaries  
**builds on:** [day 57](#day-57) (`std::filesystem`: portable paths and directories), [day 56](#day-56) (parsing without allocation: views and from_chars), [day 47](#day-47) (structured bindings)

#### the idea

somewhere in your code base there is a function that scans a directory with `opendir`, glues paths together with `+ "/" +`, parses lines with `std::string::substr`, and reports failure through a `bool` and an out-parameter. it works, it is not portable, and nobody wants to touch it. this lesson modernizes that function with the C++17 vocabulary from the last two modules, and treats each change as a decision that needs a reason, not a style preference.

#### understanding the concept

a good modernization is a sequence of small, individually justified changes. each one should make a specific defect impossible or a specific intent visible: a resource that can no longer leak, an error that can no longer be ignored, a name that replaces `.first`. "it is more modern" is not a reason. and a refactoring, by definition, preserves behavior; where behavior *does* change, that is a separate decision, written down and covered by a test that existed before the change.

#### in code

now the legacy loader. it reads `key = value` lines from every `*.conf` file in a directory:

```cpp complete
// before: C++03 style, POSIX only
#include <dirent.h>
#include <fstream>
#include <map>
#include <string>

std::string trim(const std::string& s);   // the usual hand-written helper

bool load_configs(const char* dir, std::map<std::string, std::string>& out,
                  std::string& err) {
    DIR* d = opendir(dir);
    if (!d) { err = "cannot open directory"; return false; }
    while (struct dirent* e = readdir(d)) {
        std::string name = e->d_name;
        if (name.size() < 5 || name.substr(name.size() - 5) != ".conf") continue;
        std::ifstream in((std::string(dir) + "/" + name).c_str());
        std::string line;
        while (std::getline(in, line)) {
            std::string::size_type eq = line.find('=');
            if (line.empty() || line[0] == '#' || eq == std::string::npos) continue;
            out[trim(line.substr(0, eq))] = trim(line.substr(eq + 1));
        }
    }
    closedir(d);
    return true;
}
```

and after, in C++17:

```cpp complete
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>
namespace fs = std::filesystem;

using Config = std::map<std::string, std::string, std::less<>>;

std::string_view trim(std::string_view s) {
    const auto first = s.find_first_not_of(" \t\r");
    if (first == std::string_view::npos) return {};
    return s.substr(first, s.find_last_not_of(" \t\r") - first + 1);
}

std::optional<std::pair<std::string_view, std::string_view>> parse_line(std::string_view line) {
    line = trim(line);
    const auto eq = line.find('=');
    if (line.empty() || line.front() == '#' || eq == std::string_view::npos)
        return std::nullopt;
    return std::pair{trim(line.substr(0, eq)), trim(line.substr(eq + 1))};
}

[[nodiscard]] Config load_configs(const fs::path& dir) {
    std::vector<fs::path> files;
    for (const auto& entry : fs::directory_iterator(dir))       // throws fs::filesystem_error
        if (entry.is_regular_file() && entry.path().extension() == ".conf")
            files.push_back(entry.path());
    std::sort(files.begin(), files.end());                      // make "last file wins" deterministic

    Config cfg;
    for (const auto& file : files) {
        std::ifstream in(file);
        if (!in) throw std::runtime_error("cannot open " + file.string());
        for (std::string line; std::getline(in, line);)
            if (auto kv = parse_line(line)) {
                auto [key, value] = *kv;
                cfg.insert_or_assign(std::string(key), std::string(value));
            }
    }
    return cfg;
}
```

#### in practice

each change, and why:

| change | why |
|---|---|
| `opendir`/`readdir` to `fs::directory_iterator` | portable, and no `closedir` to forget on an early return (RAII) |
| string concatenation to `fs::path` and `extension()` | correct separators, no off-by-one suffix check |
| `bool` plus `err` out-parameter to an exception | a missing config directory at startup is exceptional ([day 50](#day-50)) |
| out-parameter map to a returned `Config` with `[[nodiscard]]` | the result is the point of the call; returning a local costs at most a move, and NRVO usually removes even that ([day 12](#day-12)) |
| `parse_line` returning `std::optional` of a pair of views | a pure, testable function; "not a key-value line" is a normal outcome, not an error |
| structured bindings for the key and value | names instead of `.first` and `.second` |
| sorting the file list | `readdir` order made duplicate keys across files resolve differently per machine |

one change was deliberately **not** made. the views returned by `parse_line` are tempting to store directly, with a `std::map<std::string_view, std::string_view>`, to avoid the two string copies per line. that would be a dangling bug ([day 55](#day-55)): the views point into `line`, which is overwritten on the next `getline` and destroyed when the loop ends. the map must own its strings. the views are the right tool *inside* the parse, and the copies happen exactly once, at the ownership boundary. a second non-change: no parallel parsing and no `std::unordered_map`. a handful of config files at startup is not a performance problem, and changing the container would change the iteration order other code may depend on.

#### watch out for

**a "refactoring" that changes behavior.**

be honest about one thing: a refactoring is supposed to preserve behavior, and three behaviors changed here. duplicate keys now resolve in sorted file order, an unreadable file now throws instead of being skipped silently, and an indented `# comment` is now treated as a comment. each one is an improvement, and each one belongs in the commit message and in a characterization test written *before* the refactor ([day 114](#day-114) covers that discipline at scale).

#### the takeaway

modernize in small steps that each remove a specific defect or reveal a specific intent; state every behavior change openly, and keep owning types at ownership boundaries even when views are tempting.

#### optional challenge

a colleague wants to call `load_configs` every five seconds from a hot-reload thread. during deployments the directory briefly disappears. what would you change in the API, and what would you keep?

<details>
<summary>answer</summary>

a missing directory is now an expected outcome, so throwing and catching every five seconds would be exceptions as control flow ([day 50](#day-50)). add a non-throwing entry point, for example `std::optional<Config> try_load_configs(const fs::path& dir, std::error_code& ec)`, built on the `error_code` overloads of `directory_iterator` and `is_regular_file`, and have the reload thread keep the last good `Config` when it gets `std::nullopt`. keep the throwing `load_configs` for startup, where failing loudly is correct, ideally implemented on top of the non-throwing version so the parsing logic exists once. if callers need to tell "directory missing" from "file unreadable" from "parse error", the `error_code` (or a variant result from [day 53](#day-53)) carries that reason; a bare optional would not.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-59"></a>

### day 59: review: the C++17 vocabulary, and a complete refresher

**module 9:** variants, views, and files · **reading time:** about 9 minutes · **standard:** C++17  
**objective:** consolidate variant, string_view, from_chars, filesystem, and modernization practice, and check the standalone C++17 refresher  
**covers:** [day 53](#day-53) to [day 58](#day-58)

#### recap

| lesson | key idea |
|---|---|
| [day 53](#day-53) | a value-semantic sum type with inline storage; `std::visit` with per-type lambdas checks exhaustiveness. |
| [day 54](#day-54) | variants for closed sets you own, virtual functions for open sets, `std::any` only when the code must not know the type. |
| [day 55](#day-55) | a borrowed pointer and length: great for parameters, dangerous anywhere it can outlive its owner, and not null-terminated. |
| [day 56](#day-56) | slice with views, convert with `from_chars` and `to_chars`, check both the error code and the end pointer. |
| [day 57](#day-57) | portable paths and directory iteration with a per-call choice of exceptions or `error_code`; checks do not prevent races. |
| [day 58](#day-58) | modernize in small, justified steps; state behavior changes; keep owning types at ownership boundaries. |

##### checkpoint: the refresher is complete

this is the end of the course's standalone refresher. if you stopped here, you would have the full working model of modern C++17: how source becomes a program and what the standard does and does not promise, who owns every resource and how objects move, the library and template machinery the standard library is built from, and the C++17 vocabulary types that make interfaces say what they mean. a quick self-test: can you explain, without notes, why a `std::string_view` member is riskier than a `std::string` member, why `std::vector` cares whether your move constructor is `noexcept`, and why an unconstrained template's error messages are so long? if yes, the rest of the course will feel like extensions of things you already understand: C++20, concurrency, design, and production engineering.

#### review questions

1. your team is designing the message type for a planner that receives `Goal`, `Cancel`, and `MapUpdate` messages, all defined by your team. a colleague proposes a `Message` base class with virtual `apply()`. make the case for `std::variant` instead, and name one situation where the base class would be the better choice.
2. what is wrong with this member function, and what is the smallest fix?

   ```cpp
   class Frame {
       std::string prefix_ = "base";
       std::string id_ = "link";
   public:
       std::string_view name() const { return prefix_ + "_" + id_; }
   };
   ```
3. from [day 08](#day-08): `const std::string& a = std::string("x") + "y";` and `std::string_view b = std::string("x") + "y";` look alike. which one is safe to use on the next line, and why does the lifetime rule treat them differently?

#### mini exercise

modernize this pre-C++17 parser using at least three features from the last two modules. keep the caller working, and decide which behavior changes you are willing to accept.

```cpp complete
#include <cstdlib>
#include <map>
#include <string>

// "max_vel=1.5" -> name "max_vel", value 1.5; false if malformed
bool parse_limit(const std::string& line, std::string& name, double& value) {
    std::string::size_type eq = line.find('=');
    if (eq == std::string::npos) return false;
    name = line.substr(0, eq);
    const char* begin = line.c_str() + eq + 1;
    char* end = 0;
    value = std::strtod(begin, &end);
    return end != begin && *end == '\0';
}

void load(std::map<std::string, double>& limits, const std::string& line) {
    std::string name;
    double v;
    if (parse_limit(line, name, v)) limits[name] = v;
}
```

#### answers

<details>
<summary>answer 1: variant versus a base class</summary>

the set of message types is closed and owned by the team, which is exactly where a variant shines: values stored inline (no allocation per message), copyable and storable in containers, no `dynamic_cast`, and every `std::visit` with explicit per-type handlers fails to compile until it handles a newly added message type. adding new *operations* (logging, serialization, metrics) is a new visitor rather than a change to every class. the base class wins when the set must be open: plugins or other teams adding message types without recompiling your code, or when message types are large and you want each one to own its behavior.

</details>

<details>
<summary>answer 2: the dangling name()</summary>

`prefix_ + "_" + id_` creates a temporary `std::string`; the returned view points into it, and the temporary is destroyed at the end of the `return` statement. every use of the result is undefined behavior. the smallest fix is to return `std::string`. a view is only appropriate when it refers to storage that outlives the call, for example `std::string_view id() const { return id_; }`, which is valid as long as the `Frame` lives and `id_` is not modified.

</details>

<details>
<summary>answer 3: reference versus view</summary>

`a` is safe: binding a `const&` directly to a temporary extends the temporary's lifetime to the reference's ([day 08](#day-08)). `b` dangles: `std::string_view` is not a reference but an object that holds a pointer, initialized through `std::string`'s conversion operator. the temporary string is not bound to any reference, so it dies at the end of the full-expression, and reading `b` is undefined behavior. lifetime extension follows the language's reference-binding rules, not "anything that refers to something".

</details>

<details>
<summary>mini exercise answer</summary>

```cpp complete
#include <charconv>
#include <map>
#include <optional>
#include <string>
#include <string_view>

struct Limit { std::string_view name; double value; };   // name borrows from the line

[[nodiscard]] std::optional<Limit> parse_limit(std::string_view line) {
    const auto eq = line.find('=');
    if (eq == std::string_view::npos) return std::nullopt;
    const auto text = line.substr(eq + 1);
    double value{};
    if (auto [ptr, ec] = std::from_chars(text.data(), text.data() + text.size(), value);
        ec != std::errc{} || ptr != text.data() + text.size())
        return std::nullopt;
    return Limit{line.substr(0, eq), value};
}

void load(std::map<std::string, double>& limits, std::string_view line) {
    if (auto lim = parse_limit(line))
        limits.insert_or_assign(std::string(lim->name), lim->value);   // copy at the ownership boundary
}
```

C++17 features used: `std::string_view` parameters and slicing, `std::optional` instead of the `bool` plus out-parameters, an `if` with an initializer around a structured binding of the `from_chars` result, and `[[nodiscard]]`. the `Limit::name` view is safe only as long as the line lives, which is why `load` copies it into the map immediately.

behavior changes to accept consciously: `std::strtod` skipped leading whitespace, accepted a leading `+`, and depended on the current C locale's decimal point; `std::from_chars` does none of these, so `"max_vel= 1.5"` and `"max_vel=+1.5"` are now rejected. that is usually what you want in a config format, but it is a change and belongs in the commit message. (floating-point `from_chars` needs GCC 11 or later with libstdc++; check other toolchains.)

</details>

#### connections

the C++20 modules that follow sharpen tools you now know: concepts replace `enable_if` and give templates readable errors ([day 60](#day-60)), ranges turn iterator pairs into composable pipelines ([day 62](#day-62)), `std::span` does for arrays what `std::string_view` did for text ([day 65](#day-65)), and defaulted comparisons and `consteval` remove boilerplate you have been writing by hand.

[back to the curriculum map](#curriculum)

---

<a id="module-cpp20-generic"></a>

## module 10: C++20: concepts, ranges, and span

constrained templates, range algorithms and lazy views, and std::span for borrowing contiguous data.

<a id="day-60"></a>

### day 60: concepts: constraining templates

**module 10:** C++20: concepts, ranges, and span · **reading time:** about 8 minutes · **standard:** C++20  
**objective:** constrain templates with standard concepts so requirements are part of the signature, and predict which constrained overload is chosen  
**builds on:** [day 40](#day-40) (function templates and argument deduction), [day 44](#day-44) (compile-time branching with if constexpr)

#### the idea

call `std::sort(ids.begin(), ids.end())` on a `std::list<int>` and GCC 12 reports `no match for 'operator-'` at line 1938 of `stl_algo.h`, a file you never wrote, followed by a page of instantiation context. the real problem ("sort needs random access") appears nowhere. call `std::ranges::sort(ids)` instead and the first error is on your line, and the notes say the constraint `random_access_range` was not satisfied because `bidirectional_iterator_tag` is not `random_access_iterator_tag`.

the output is not shorter. it is *located*: the requirement is part of the signature, so the compiler checks it at the call site instead of discovering the problem deep in the body. that is what concepts buy you: a template's requirements move from its implementation into its interface.

#### understanding the concept

a **concept** is a named compile-time predicate over template arguments:

```cpp
template <typename T>
concept Arithmetic = std::integral<T> || std::floating_point<T>;
```

`Arithmetic<double>` is a `bool` constant expression. a concept is not a type and has no runtime presence. when a constrained template is a candidate in overload resolution, the compiler deduces the template arguments, then checks the constraints *before* instantiating anything. if they are not satisfied, the candidate is dropped, exactly as SFINAE would drop it ([day 40](#day-40)), but the diagnostic names the unsatisfied concept and the failing sub-expression.

`<concepts>` gives you the vocabulary: `std::integral`, `std::floating_point`, `std::same_as`, `std::convertible_to`, `std::derived_from`, `std::invocable`, `std::predicate`, `std::totally_ordered`, `std::copyable`, `std::regular`, and more. build on these instead of reinventing them, for a reason we will see under subsumption.

#### in code

**before and after.** C++17 hid the constraint in a defaulted template parameter ([day 40](#day-40)). C++20 gives four spellings that mean the same thing for a single parameter:

```cpp complete
#include <concepts>
#include <type_traits>

// C++17: SFINAE via enable_if
template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
T gcd17(T a, T b) { while (b != 0) { T t = a % b; a = b; b = t; } return a; }

// C++20: constrained template parameter
template <std::integral T>
T gcd(T a, T b) { while (b != 0) { T t = a % b; a = b; b = t; } return a; }

// equivalent: requires clause, or trailing requires clause
template <typename T> requires std::integral<T> T gcd2(T a, T b);
template <typename T> T gcd3(T a, T b) requires std::integral<T>;

// abbreviated function template: each `auto` is its own template parameter
auto scale(std::floating_point auto gain, std::integral auto counts) {
    return gain * counts;
}

// gcd(12, 18L);   // error: deduced conflicting types for 'T' (int and long)
// scale(0.5, 7L); // fine: two independent parameters
// gcd(1.5, 2.5);  // error: 'is_integral_v<double>' evaluated to 'false'
```

use the constrained parameter when one concept applies to one type; use a `requires` clause when the constraint relates several parameters (`requires std::convertible_to<From, To>`).

**overloading on constraints.** when two constrained overloads are both viable, the more constrained one wins if its constraints *subsume* the other's:

```cpp
#include <cstdio>
void describe(Arithmetic auto)    { std::puts("arithmetic"); }
void describe(std::integral auto) { std::puts("integral"); }

describe(3);     // prints: integral   (integral subsumes integral || floating_point)
describe(2.5);   // prints: arithmetic
describe('a');   // prints: integral   (char is an integral type)
```

subsumption is decided by breaking constraints into atomic pieces and comparing them, and two atomic constraints are only "the same" if they come from the same expression in the source, which in practice means the same named concept. that is why you build on `std::integral` rather than writing `std::is_integral_v<T>` in each overload (see "watch out for").

#### in practice

migrating a C++17 template library to concepts is mostly mechanical and immediately visible to users. every `std::enable_if_t<...>` in a template parameter list becomes a constrained parameter or a `requires` clause, behavior stays the same, and the error a user gets for a wrong type moves from the middle of the implementation to the line they wrote, naming the requirement they missed. the standard library made the same move: `std::ranges::sort` and the other range algorithms are constrained versions of the C++98 algorithms, which is exactly why the opening example's diagnostic improved. a good first step in your own code is the templates that users instantiate most often with the wrong types, because that is where the error messages cost the most time.

#### watch out for

**concepts do not check the template body.** this compiles, because the body is only checked when instantiated:

```cpp
template <std::integral T>
T half(T x) { return x.value / 2; }   // nonsense, but no error until someone calls it
```

unlike Rust traits, C++20 has no definition checking: the concept constrains *callers*, not the implementation. if the body uses `s.flush()` and the concept forgot to require it, a type can satisfy the concept and still fail inside. keep the concept and the body in sync, and test with a minimal archetype type that provides only what the concept demands.

#### the takeaway

a concept moves a template's requirements from its body into its signature; constrain with standard concepts, so error messages name the requirement and the most specific overload wins.

#### optional challenge

for `template <std::integral T> T gcd(T a, T b);`, which calls compile?

```cpp
gcd(12, 18);      // (1)
gcd(12u, 18u);    // (2)
gcd(12, 18L);     // (3)
gcd('a', 'b');    // (4)
gcd(true, false); // (5)
```

<details>
<summary>answer</summary>

(1), (2), (4), and (5) compile; (3) does not. deduction happens first and must agree, so `int` and `long` conflict before the constraint is even checked. `unsigned`, `char`, and `bool` all satisfy `std::integral`, which may be more than a `gcd` should accept; a `requires` clause such as `std::integral<T> && !std::same_as<T, bool>` states the narrower intent.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-61"></a>

### day 61: writing your own concepts

**module 10:** C++20: concepts, ranges, and span · **reading time:** about 8 minutes · **standard:** C++20  
**objective:** write concepts with requires expressions that capture a meaningful contract, and test types against them where they are defined  
**builds on:** [day 60](#day-60) (concepts: constraining templates)

#### the idea

a template's real contract tends to live in its body: "`S` must have a `read()` that returns its sample type, a `name()` that does not throw, and a `reset()`". callers learn it by failing to compile against it. a concept of your own puts that contract in one named, reusable place, where the compiler checks it at every call site and where a type's author can check it before anyone else calls anything.

#### understanding the concept

the building block for your own concepts is the **requires expression**, `requires (params) { requirements; }`. its parameters are just names to write expressions with; nothing is evaluated or executed. the compiler only asks "would this be valid?". there are four kinds of requirement:

| kind | form | checks |
|---|---|---|
| simple | `s.reset();` | the expression is valid |
| type | `typename S::sample_type;` | the type exists |
| compound | `{ s.read() } noexcept -> std::same_as<X>;` | valid, optionally `noexcept`, and `decltype((expr))` satisfies the concept |
| nested | `requires std::copyable<X>;` | a further constraint is satisfied |

concepts are not purely syntactic. `std::regular` means "copyable, default-constructible, and equality-comparable *in a way that behaves like a value*"; `std::totally_ordered` means the comparison operators are consistent with a total order. the compiler checks only the syntax. for standard library templates, a type that satisfies a concept's syntax but violates its semantic requirements makes the program ill-formed, no diagnostic required: you get no error, just no guarantees.

#### in code

**writing a concept.** a sensor driver contract for a robotics stack:

```cpp complete
#include <chrono>
#include <concepts>
#include <cstdint>
#include <string_view>

template <typename S>
concept Sensor = requires(S& s, const S& cs) {
    typename S::sample_type;                                  // type
    { s.read() } -> std::same_as<typename S::sample_type>;    // compound
    { cs.name() } noexcept -> std::convertible_to<std::string_view>;
    s.reset();                                                // simple
    requires std::copyable<typename S::sample_type>;          // nested
};

struct Imu {
    struct sample_type { float ax, ay, az; };
    sample_type read() { return {0.f, 0.f, 9.81f}; }
    std::string_view name() const noexcept { return "imu0"; }
    void reset() {}
};
static_assert(Sensor<Imu>);   // the contract is tested next to the type

struct Encoder {
    using sample_type = std::int32_t;
    std::int64_t read() { return 0; }   // BUG: does not return sample_type
    const char* name() const noexcept { return "enc0"; }
    void reset() {}
};

template <Sensor S>
typename S::sample_type poll(S& s) { return s.read(); }

// poll(enc);  GCC 12: note: 's.read()' does not satisfy return-type-requirement
```

that `static_assert` line is worth making a habit. it turns "does my type still fit the template?" into a compile error in the type's own header, not in someone else's instantiation three libraries away.

finally, C++20 lambdas can name their template parameters, which lets you constrain them and relate two arguments' types:

```cpp complete
#include <algorithm>
#include <vector>

auto clamp_all = []<std::floating_point T>(std::vector<T>& v, T lo, T hi) {
    for (T& x : v) x = std::clamp(x, lo, hi);
};
// clamp_all(floats, 0.f, 1.f);  OK
// clamp_all(floats, 0.0, 1.0);  error: conflicting types for 'T' (float and double)
```

with a generic lambda (`auto` parameters, [day 37](#day-37)) you could not say "these three are the same `T`" without `decltype` gymnastics.

#### in practice

a motion-control library offers `template <Sensor S, Actuator A> class JointController`. before concepts, the header said `template <typename S, typename A>` and the real contract lived in a wiki page and in the body of `update()`. integrators found out their encoder wrapper was missing `reset()` when a build failed inside the controller's implementation.

with concepts, the header *is* the contract, every driver header carries `static_assert(Sensor<MyDriver>)`, and the error appears where the driver is written. compare this with a virtual `ISensor` interface ([day 30](#day-30)): the concept version has no vtable, no inheritance requirement, and allows inlining, but every controller instantiation is a separate piece of code (compile time, binary size), and you cannot put heterogeneous sensors in one container without type erasure ([day 98](#day-98)). choose a concept when the type is fixed at build time and the call is hot; choose a virtual interface when you need runtime selection or a stable binary boundary.

#### watch out for

a related trap is subsumption with raw traits. these two overloads look like "general" and "more specific", but they are **ambiguous** for `int`:

```cpp
template <typename T> requires std::is_integral_v<T>                        void g(T);
template <typename T> requires std::is_integral_v<T> && (sizeof(T) == 4)   void g(T);
// g(1);  error: call of overloaded 'g(int)' is ambiguous
```

the two `std::is_integral_v<T>` are different atomic constraints because they are different expressions. write `std::integral<T>` in both and the second overload wins.

#### the takeaway

a concept moves a template's requirements from its body into its signature. write concepts that name a meaningful contract (`Sensor`, `std::regular`), build them from standard concepts so subsumption works, and test them with `static_assert` next to the types that must satisfy them.

#### optional challenge

```cpp complete
template <typename T>
concept Addable = requires(T a, T b) { a + b; };
```

which of these hold: `Addable<std::string>`, `Addable<const char*>`, `Addable<short>`, `Addable<bool>`? would you use `Addable` to constrain a `sum()` over sensor readings?

<details>
<summary>answer</summary>

`Addable<std::string>` is true (concatenation). `Addable<const char*>` is false: adding two pointers is ill-formed. `Addable<short>` and `Addable<bool>` are both true, through integral promotion to `int`, so `a + b` does not even have type `T`.

so `Addable` admits strings (concatenation, not summation) and `bool`, and says nothing about the result type. it describes syntax, not meaning. for a sum of readings, constrain on what you mean: `Arithmetic` from this lesson, or a compound requirement such as `{ a + b } -> std::convertible_to<T>` together with a semantic contract documented next to the concept.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-62"></a>

### day 62: range algorithms and projections

**module 10:** C++20: concepts, ranges, and span · **reading time:** about 5 minutes · **standard:** C++20  
**objective:** call the constrained `std::ranges` algorithms on whole ranges, and use projections instead of hand-written comparison lambdas  
**builds on:** [day 60](#day-60) (concepts: constraining templates), [day 36](#day-36) (iterators and algorithms over raw loops)

#### the idea

`std::sort(dets.begin(), dets.end(), [](const Detection& a, const Detection& b) { return a.range_m < b.range_m; });` says "sort detections by range" in about seventy characters, most of them ceremony: two iterators that always come as a pair, and a lambda whose only job is to pick one member twice. C++20's range algorithms let you write `std::ranges::sort(dets, {}, &Detection::range_m);`, and the shorter version is also the better-checked one.

#### understanding the concept

a **range** is anything with `std::ranges::begin` and `std::ranges::end` (the end may be a *sentinel* of a different type). C++20 adds two layers on top of the [day 36](#day-36) algorithms.

**range algorithms** in `std::ranges::` take a whole range, are constrained with concepts ([day 60](#day-60)), and accept a **projection**: a callable applied to each element before the comparison or predicate. `std::ranges::sort(dets, {}, &Detection::range_m)` sorts by one member with the default `std::ranges::less` (the `{}`); the member pointer works because projections are called through `std::invoke`.

every classic algorithm has a `std::ranges::` counterpart. besides taking a range and a projection, they differ in small ways worth knowing: they are constrained, so misuse fails at the call site; they accept an iterator and a *sentinel* of a different type; and several return more than the classic versions did (`std::ranges::copy` returns both the input and output positions where it stopped), which you can unpack with a structured binding.

#### in code

```cpp complete
#include <algorithm>
#include <cstdio>
#include <vector>

struct Detection { float range_m; float snr_db; int track_id; };

int main() {
    std::vector<Detection> dets{{80.f, 15.f, 3}, {30.f, 20.f, 1}, {60.f, 9.f, 2}};

    std::ranges::sort(dets, {}, &Detection::range_m);                    // by range, ascending
    auto strongest = std::ranges::max_element(dets, {}, &Detection::snr_db);
    auto it = std::ranges::find(dets, 2, &Detection::track_id);          // compares the projected id
    auto n = std::ranges::count_if(dets, [](float snr) { return snr > 12.f; }, &Detection::snr_db);

    std::printf("%d %d %d %td\n", dets.front().track_id, strongest->track_id, it->track_id, n);
    // prints: 1 1 2 2
}
```

the projection is applied to each element before the comparison or predicate sees it, so the predicate in `count_if` receives a `float`, not a `Detection`. the `{}` is the default comparator, `std::ranges::less`.

#### in practice

projections and comparators combine, which covers most real sorting needs without a custom lambda: `std::ranges::sort(tracks, std::ranges::greater{}, &Track::confidence)` sorts by confidence, highest first. a projection can also be any callable, for keys that are computed rather than stored, such as the distance from the vehicle: `std::ranges::sort(dets, {}, [&](const Detection& d) { return dist2(d, ego); })`. keep such projections cheap: a sort calls the projection twice per comparison, so O(n log n) times. when the key is expensive (a lookup, a string conversion), compute it once per element into a vector of key and index pairs, sort that, and reorder, rather than recomputing inside the sort.

#### watch out for

**algorithms on temporaries return `std::ranges::dangling`.**

```cpp
std::vector<int> make_ids();
auto it = std::ranges::find(make_ids(), 42);   // it is std::ranges::dangling
// *it;  error: no match for 'operator*' (operand type is 'std::ranges::dangling')
```

ranges that are safe to outlive (like `std::string_view` or `std::span`) opt in as *borrowed ranges*, and for those you get a real iterator.

the classic algorithms would have returned an iterator into the destroyed vector and let you dereference it. if you need the result, keep the container in a named variable first.

#### the takeaway

prefer the `std::ranges::` algorithms: pass the range, not two iterators, and use projections to say "by this member" instead of writing comparison lambdas.

#### optional challenge

`std::ranges::sort(v, {}, key)` is called on 1,000 elements, and `key` converts each element's id to a `std::string`. roughly how many conversions happen, and how would you avoid most of them?

<details>
<summary>answer</summary>

a comparison sort makes on the order of n log2 n comparisons, about 10,000 for 1,000 elements, and each comparison projects both operands, so about 20,000 string conversions instead of 1,000. compute the keys once: build a `std::vector<std::pair<std::string, std::size_t>>` of key and original index, sort that (by its first member), and use the indices to reorder or to read the elements in order. the general rule: projections are for cheap accessors, not for computation.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-63"></a>

### day 63: views: lazy pipelines

**module 10:** C++20: concepts, ranges, and span · **reading time:** about 9 minutes · **standard:** C++20  
**objective:** compose lazy view pipelines and predict when, and how often, their callables run  
**builds on:** [day 62](#day-62) (range algorithms and projections), [day 55](#day-55) (`std::string_view`: borrowing characters)

#### the idea

a radar tracker wants "the ranges of the three nearest detections with SNR above 12 dB". the C++17 version copies the strong detections into a temporary vector, sorts it with a lambda that compares one member, and then runs an index loop that stops at three. three passes, one temporary, and an off-by-one waiting to happen in `i < strong.size() && i < 3`.

C++20 ranges let you say it as a pipeline: filter, project, take. the interesting question is not the syntax but the mechanics: nothing in a pipeline runs until you iterate it, and nothing in it owns your data unless you hand it over. both facts make pipelines cheap, and both are the source of their bugs.

#### understanding the concept

**views** (`<ranges>`) are lazy adaptors. `std::views::filter(pred)`, `transform(f)`, `take(n)`, `drop(n)`, `reverse`, `iota(a, b)`, `keys`, `values`, and `split(delim)` each produce a small object that stores its underlying range (or a reference to it) plus the callable. iterating it pulls elements through the chain one at a time. a view is required to be cheap to move, and to copy if it is copyable, independent of how many elements it represents. `r | views::filter(p)` is just `views::filter(r, p)` written left to right.

there is no `std::ranges::to` in C++20 (it is C++23). to materialize a pipeline you write the container yourself, with `std::ranges::copy` into a `back_inserter`, or by constructing from the iterators of a `views::common` adaptor.

#### in code

**before and after.**

```cpp complete
#include <algorithm>
#include <iterator>
#include <ranges>
#include <vector>

struct Detection { float range_m; float snr_db; int track_id; };

// C++17
std::vector<float> near_strong_17(const std::vector<Detection>& dets) {
    std::vector<Detection> strong;
    for (const auto& d : dets)
        if (d.snr_db > 12.f) strong.push_back(d);
    std::sort(strong.begin(), strong.end(),
              [](const Detection& a, const Detection& b) { return a.range_m < b.range_m; });
    std::vector<float> out;
    for (std::size_t i = 0; i < strong.size() && i < 3; ++i)
        out.push_back(strong[i].range_m);
    return out;
}

// C++20
std::vector<float> near_strong_20(std::vector<Detection> dets) {   // our own copy to sort
    std::ranges::sort(dets, {}, &Detection::range_m);
    auto nearest = dets
        | std::views::filter([](const Detection& d) { return d.snr_db > 12.f; })
        | std::views::transform(&Detection::range_m)
        | std::views::take(3);
    std::vector<float> out;
    std::ranges::copy(nearest, std::back_inserter(out));
    return out;
}
// both return {30, 60, 80} for the same input
```

**predict the output.** laziness means the callable runs when an element is pulled, and it can run more than once:

```cpp complete
#include <cstdio>
#include <ranges>
#include <vector>

int calls = 0;
int main() {
    std::vector<int> raw{1, 2, 3, 4, 5, 6};
    auto square = [](int x) { ++calls; return x * x; };
    auto even   = [](int x) { return x % 2 == 0; };

    int sum = 0;
    for (int x : raw | std::views::transform(square) | std::views::filter(even)) sum += x;
    std::printf("sum=%d calls=%d\n", sum, calls);

    calls = 0; sum = 0;
    for (int x : raw | std::views::filter(even) | std::views::transform(square)) sum += x;
    std::printf("sum=%d calls=%d\n", sum, calls);
}
```

both sums are 56. the first pipeline makes 9 calls: `filter` calls `square` six times to test each element, and the loop's dereference calls it again for the three that pass. the second makes 3. views do not cache transformed values, so an expensive or side-effecting `transform` ahead of a `filter` is evaluated twice per surviving element. put cheap filters first, and keep transforms pure.

#### in practice

telemetry lines like `rpm=1200;temp=71;volt=24` are a natural fit for `views::split`, which with a `std::string_view` source yields contiguous subranges, so each field becomes a `string_view` with no allocation:

```cpp complete
#include <charconv>
#include <ranges>
#include <string_view>

void parse(std::string_view line) {
    for (auto field : line | std::views::split(';')) {
        std::string_view kv(field.begin(), field.end());   // C++20 iterator-pair constructor
        auto eq = kv.find('=');
        std::string_view key = kv.substr(0, eq);
        int value = 0;
        std::from_chars(kv.data() + eq + 1, kv.data() + kv.size(), value);
        // ... dispatch on key; prints [rpm] -> 1200 and so on in the test build
    }
}
```

these `split` semantics come from P2210, also a defect report against C++20 (the old behavior lives on as `views::lazy_split`). an older standard library may give you a forward-only range where this constructor does not work. the real code checks `eq == npos` and the `from_chars` result; it was left out to keep the example short.

#### watch out for

**debug builds and compile times.** each adaptor is a layer of templates. error messages name types like `filter_view<ref_view<vector<int>>, lambda>`, and in unoptimized builds each layer's `operator++` and `operator*` is a real call. if your robot's debug build has to meet a control-loop deadline, check that before converting a hot loop. and when the logic has early exits, two outputs, or index arithmetic, a plain loop is often clearer than a pipeline. "No raw loops" ([day 36](#day-36)) is a guideline.

#### the takeaway

views are lazy and cheap: a pipeline is a recipe that runs element by element when you iterate it, so put cheap filters first, keep transforms pure, and materialize the result explicitly.

#### optional challenge

what does this print, and why does it terminate even though `std::views::iota(1)` never ends?

```cpp
auto odd = [](int x) { return x % 2 == 1; };
for (int x : std::views::iota(1) | std::views::filter(odd) | std::views::take(3))
    std::printf("%d ", x);
```

<details>
<summary>answer</summary>

it prints `1 3 5`. `iota(1)` is an unbounded range, which is fine because nothing is computed up front: the loop pulls one element at a time through `take`, which pulls through `filter`, which pulls from `iota`. after the third element, `take` reports the end and the loop stops, so `iota` is asked for only five numbers. an eager pipeline (build a container, then filter it, then truncate it) could not even start.

</details>

#### going deeper (optional)

##### sorting before filtering

notice a real tradeoff hiding here: we sort *before* filtering because `ranges::sort` needs a random-access range and a filter view is at most bidirectional. so the C++20 version sorts every detection, while the C++17 version sorted only the strong ones. if most detections are weak and the frame is large, that matters; measure with realistic frames before deciding which one wins.

[back to the curriculum map](#curriculum)

---

<a id="day-64"></a>

### day 64: views and lifetimes: what a pipeline refers to

**module 10:** C++20: concepts, ranges, and span · **reading time:** about 5 minutes · **standard:** C++20  
**objective:** tell which views refer to their data and which own it, and avoid pipelines that outlive their source or a modification of it  
**builds on:** [day 63](#day-63) (views: lazy pipelines)

#### the idea

this function compiles without a warning on GCC 12, returns a perfectly ordinary-looking pipeline, and every use of its result is undefined behavior:

```cpp
auto strong_ids() {
    std::vector<int> ids = load();
    return ids | std::views::filter([](int i) { return i > 2; });   // BUG: refers to a dead local
}
```

a view is closer to a reference than to a container: it stores *how* to produce elements, not the elements. knowing exactly what each pipeline refers to is the price of laziness.

#### understanding the concept

what does a view hold? `views::all` decides. for an lvalue container it creates a `ref_view`: a pointer to your container. for an rvalue container it creates an `owning_view` that moves the container in. (`owning_view` came from P2415, a defect report applied to C++20; GCC 12, recent Clang and MSVC implement it. before it, piping an rvalue container did not compile.) so "views do not own" is true for lvalues, which is the common case and the dangerous one.

ranges that are safe to outlive (like `std::string_view` or `std::span`) opt in as *borrowed ranges*, and for those you get a real iterator.

#### in code

iterating the result is undefined behavior, and GCC 12 compiles it without a warning. return `std::move(ids) | ...` (an `owning_view`) or return the container. the same trap appears in range-for: `for (int x : next_frame().data() | std::views::take(2))` is UB if `data()` returns a reference into the temporary frame, because the frame dies at the end of the range initializer. (C++23 extends temporary lifetimes in range-for initializers; C++20 does not.)

the fixed version moves the vector into the pipeline, so the returned view owns it:

```cpp
auto strong_ids_fixed() {
    std::vector<int> ids = load();
    return std::move(ids) | std::views::filter([](int i) { return i > 2; });   // owning_view
}
```

returning the filtered *container* is often clearer still: callers then hold ordinary data with no lifetime puzzle attached.

#### in practice

a robust convention for APIs that use ranges: **accept views, return owning data.** a function that consumes a sequence takes its parameter as `auto&&` or a constrained template (`std::ranges::input_range auto&& r`), so callers can pass containers, views, or pipelines without copying. a function that produces a sequence returns a container, or a view only when the view's source is clearly owned by something longer-lived, such as a member of the object the function is called on, and that relationship is documented. pipelines then live as local variables in the code that iterates them, which is exactly the scope in which their references are obviously valid.

#### watch out for

**`filter_view` caches `begin()`.** to make `begin()` amortized O(1), `filter_view` finds the first match on the first call and remembers it. consequences:

- `begin()` is non-const, so `void dump(const auto& r)` will not accept a filter view. take views by value or by forwarding reference (`auto&&`) instead.
- modifying an element through a filter iterator so that it no longer satisfies the predicate is UB, by the standard's own wording.
- changing the underlying container after the first iteration can leave the cached iterator stale (see the challenge).

#### the takeaway

views over lvalues refer to their source and views over rvalues own it; keep pipelines local to the code that iterates them, do not keep a view across modifications of what it views, and return owning data from functions.

#### optional challenge

```cpp
std::vector<int> v{1, 2, 3, 4};
auto evens = v | std::views::filter([](int x) { return x % 2 == 0; });
v.push_back(6);
for (int x : evens) std::printf("%d ", x);
```

is this well-defined, and what does it print? does the answer change if you insert a `for (int x : evens) {}` loop before the `push_back`?

<details>
<summary>answer</summary>

as written it is fine and prints `2 4 6`. the view holds a `ref_view` (a pointer to `v` itself, not to its buffer) and has not cached anything yet, so iteration starts from the current `v.begin()`.

if you iterate first, `filter_view` caches an iterator to the `2`. the `push_back` may reallocate (with libstdc++ it does: the capacity after list-initialization is exactly 4), which invalidates that cached iterator, and the next loop starts from it: undefined behavior. the rule of thumb: do not keep a view across modifications of what it views. recreate it; it is cheap.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-65"></a>

### day 65: `std::span`: views over contiguous memory

**module 10:** C++20: concepts, ranges, and span · **reading time:** about 10 minutes · **standard:** C++20  
**objective:** replace pointer-plus-length parameters with `std::span`, use static extents as contracts, and keep spans from outliving their buffers  
**builds on:** [day 55](#day-55) (`std::string_view`: borrowing characters), [day 64](#day-64) (views and lifetimes: what a pipeline refers to)

#### the idea

every C and C++ codebase has functions like `void process(const float* data, std::size_t n)`. the pointer and the count travel separately, so nothing stops a caller from passing `n` in bytes instead of elements, the size of the wrong buffer, or `n` for the whole buffer with a pointer into the middle of it. and the signature cannot say whether the function writes through `data` beyond the `const` you remembered to type.

`std::span` (C++20, `<span>`) is the pointer and the count fused into one value type. it does for contiguous arrays of any `T` what `std::string_view` ([day 55](#day-55)) did for characters: it borrows, it does not own, and it makes the borrowing explicit in the signature.

#### understanding the concept

`std::span<T, Extent>` refers to a contiguous sequence of `T`. it has two forms:

- **dynamic extent** (`std::span<T>`, i.e. `Extent == std::dynamic_extent`): stores a pointer and a size. 16 bytes on a typical 64-bit platform (verified with GCC 12 on x86-64).
- **static extent** (`std::span<T, N>`): the size is part of the type, so typical implementations store only the pointer (8 bytes in the same test). the type itself carries a compile-time guarantee: this is exactly `N` elements.

a span is a cheap trivially copyable value: pass it by value, as you would a `string_view`. it converts implicitly from C arrays, `std::array`, `std::vector`, and any other contiguous, sized range (including another span), and explicitly from a pointer plus a count. the element type carries the constness: `std::span<const float>` is read-only, `std::span<float>` is writable, and a `std::span<float>` converts to `std::span<const float>` but not the other way.

slicing is O(1) and never copies: `first(n)`, `last(n)`, `subspan(offset, count)`, and static-extent versions `first<N>()`, `last<N>()`, `subspan<Offset, Count>()` that return a `std::span<T, N>`. finally, `std::as_bytes(s)` and `std::as_writable_bytes(s)` reinterpret any span as a span of `std::byte`, which is the C++20 way to say "the object representation of these elements".

bounds: C++20 `std::span` has **no** `at()`. `operator[]`, `front()`, `back()`, and the slicing functions have preconditions (index in range, count not past the end), and violating one is undefined behavior. `at()` is added in C++26. your standard library may check preconditions in a hardened mode: with libstdc++, `-D_GLIBCXX_ASSERTIONS` turns an out-of-range `operator[]` into an assertion failure (checked with GCC 12).

#### in code

**before and after.**

```cpp complete
#include <array>
#include <cmath>
#include <span>
#include <vector>

// C++17: two parameters that must agree, and nothing checks that they do
float rms17(const float* data, std::size_t n);

// C++20: one parameter, read-only by type
float rms(std::span<const float> samples) {
    if (samples.empty()) return 0.f;
    float acc = 0.f;
    for (float s : samples) acc += s * s;
    return std::sqrt(acc / static_cast<float>(samples.size()));
}

void scale(std::span<float> samples, float gain) {   // writable by type
    for (float& s : samples) s *= gain;
}

void demo(std::vector<float>& buf, std::array<float, 2>& arr, float (&raw)[4]) {
    rms(buf); rms(arr); rms(raw);                 // all implicit
    rms(std::span(buf).first(2));                 // first two samples, no copy
    rms(std::span(buf).subspan(1, 2));            // elements 1 and 2
    scale(buf, 0.5f);
}
```

the callee no longer cares who owns the samples. the caller can pass a whole buffer or a window into one, and the function body uses range-for instead of index arithmetic.

**static extent as a contract.** a 6-DoF pose is exactly six numbers. put that in the type:

```cpp
void set_pose(std::span<const double, 6> pose);

std::array<double, 6> p{};
set_pose(p);                         // OK: size known to match
std::array<double, 5> p5{};
// set_pose(p5);  error: could not convert 'p5' from 'std::array<double, 5>' to 'std::span<const double, 6>'

std::vector<double> pv(7);
// set_pose(pv);  error: a vector's size is a runtime value
set_pose(std::span<const double>(pv).first<6>());   // explicit; UB if pv.size() < 6
```

the dynamic-to-static conversion is deliberately explicit: it is where a runtime size becomes a compile-time promise, so it should be visible in the code (and is a good place for a check).

#### in practice

a radar pipeline stores a range-Doppler frame as one row-major `std::vector<float>` (one allocation, contiguous rows) and hands out rows as spans:

```cpp
class RangeDopplerFrame {
public:
    RangeDopplerFrame(std::size_t doppler_bins, std::size_t range_bins)
        : range_bins_(range_bins), cells_(doppler_bins * range_bins) {}
    std::span<float> row(std::size_t d) {                 // borrow one row, no copy
        return std::span(cells_).subspan(d * range_bins_, range_bins_);
    }
    std::span<const float> cells() const { return cells_; }
private:
    std::size_t range_bins_;
    std::vector<float> cells_;
};

float peak(std::span<const float> cells);   // CFAR, FFT, stats: none know about the frame
```

this is a coupling decision. signal-processing functions that take spans work on a frame row, a `std::array` in a unit test, a `pmr::vector`, or a DMA buffer the driver mapped into memory. if they took `const std::vector<float>&`, every caller would need a `std::vector`, and you would copy a DMA buffer into one just to call a function. the frame keeps ownership and the invariant (rows have `range_bins_` cells); the algorithms borrow.

#### watch out for

**dangling, and the const case that compiles.** `std::span<float> s = make_samples();` is rejected: a mutable span cannot bind to a temporary container. but a span of `const` elements can, by design (so that `rms(make_samples())` works as a function argument):

```cpp
std::vector<float> make_samples();
std::span<const float> s = make_samples();   // BUG: compiles; the vector dies at the semicolon
float first = s[0];                          // UB: reads freed memory
```

GCC 12 compiles this without a warning. the same goes for a span into a vector that later reallocates (`push_back` after taking the span): the span holds the old pointer. treat a span like a reference: fine as a parameter, suspicious as a local initialized from a function call, and a design decision as a data member.

#### the takeaway

replace pointer-plus-length parameters with `std::span<const T>` (read) or `std::span<T>` (write), pass it by value, use a static extent when the size is part of the contract, and never let a span outlive the buffer it borrows.

#### optional challenge

which of these compile, and which are correct?

```cpp
std::vector<float> v{1.f, 2.f};
std::span<float>          a = make_samples();            // 1
std::span<const float>    b = make_samples();            // 2
std::span<const float, 4> c = std::array<float, 4>{};    // 3
const std::span<float>    d = v;  d[0] = 9.f;            // 4
```

<details>
<summary>answer</summary>

1 does not compile: a span of mutable elements cannot be constructed from an rvalue `std::vector` (it is not a borrowed range). 2 compiles and dangles. 3 compiles too, through the constructor taking `const std::array<T, N>&`, and dangles just the same: the temporary array dies at the end of the declaration. 4 compiles and is correct: the span object is `const`, its elements are not, so `v[0]` becomes `9`. all four were checked with GCC 12, which warns about none of them.

</details>

#### going deeper (optional)

##### bytes for serialization

```cpp
#include <cstdint>

struct TelemetryPacket {
    std::uint32_t seq;
    float         temperature_c;
    std::uint16_t status;
};   // sizeof is 12 with GCC 12 on x86-64: 10 bytes of members, 2 of padding

void append(std::vector<std::byte>& wire, const TelemetryPacket& pkt) {
    auto bytes = std::as_bytes(std::span{&pkt, 1});   // span<const std::byte>, 12 bytes here
    wire.insert(wire.end(), bytes.begin(), bytes.end());
}
```

`as_bytes` is the honest version of `reinterpret_cast<const char*>(&pkt)`: reading any object's bytes through `std::byte` is allowed. what it does not fix is the wire format. the layout of `TelemetryPacket` (padding, byte order, the representation of `float`) is implementation-defined, and the two padding bytes hold indeterminate values (copying them as `std::byte` is allowed, but they are garbage), so you are shipping noise and an ABI-specific layout. that is acceptable for a same-machine ring buffer or shared memory; it is not a protocol. for a real protocol, serialize field by field in a defined byte order.

##### span, string_view, and range views

compared with neighbors: `std::string_view` is a read-only span of characters with string operations; `std::span` is any `T`, mutable or not, and has no comparison operators (use `std::ranges::equal`). range views ([day 63](#day-63)) are lazy computations over any range; a span is just memory, and it requires contiguity.

##### a `const` span is not a span of `const`

**`const` is shallow.** `const std::span<float> s` makes the span itself immutable (you cannot reseat it), but `s[0] = 1.f` still compiles. read-only access is spelled `std::span<const float>`. this is the same distinction as `T* const` versus `const T*` from [day 10](#day-10).

[back to the curriculum map](#curriculum)

---

<a id="day-66"></a>

### day 66: review: concepts, ranges, and span

**module 10:** C++20: concepts, ranges, and span · **reading time:** about 9 minutes · **standard:** C++20  
**objective:** consolidate concepts, range algorithms, view pipelines and their lifetimes, and `std::span`  
**covers:** [day 60](#day-60) to [day 65](#day-65)

#### recap

| lesson | key idea |
|---|---|
| [day 60](#day-60) | requirements move from the template body into its signature; errors name the unmet concept at the call site. |
| [day 61](#day-61) | a requires expression states a contract; build on standard concepts so subsumption works, and `static_assert` types against it. |
| [day 62](#day-62) | pass whole ranges and use projections instead of comparison lambdas. |
| [day 63](#day-63) | pipelines are lazy recipes: callables run per element, on iteration, possibly more than once. |
| [day 64](#day-64) | views over lvalues refer, views over rvalues own; keep pipelines local and return owning data. |
| [day 65](#day-65) | pointer plus length as one value: `span<const T>` to read, `span<T>` to write, static extent as a contract. |

#### review questions

1. a driver type passes `static_assert(Sensor<LidarDriver>)`, yet `JointController<LidarDriver>` fails to compile with an error inside `JointController::update()`. how is that possible, and what practice reduces the risk?
2. which of these is undefined behavior, and why is the other one fine?

   ```cpp
   std::vector<int> load_ids();                       // returns by value
   struct Config { const std::vector<int>& ids() const; };
   Config config();                                   // returns by value

   auto evens = load_ids() | std::views::filter(is_even);              // (a)
   for (int id : evens) use(id);
   for (int id : config().ids() | std::views::take(3)) use(id);        // (b)
   ```
3. two overloads are constrained with `requires std::is_integral_v<T>` and `requires std::is_integral_v<T> && (sizeof(T) == 4)`. why is `g(1)` ambiguous, and what one change makes the second overload win?
4. from [day 55](#day-55): `std::string_view name = make_name();` (where `make_name` returns `std::string`) and `std::span<const float> s = make_samples();` (returning `std::vector<float>`) both compile. what is the shared problem, and why does `std::span<float> s = make_samples();` not compile?
5. from [day 23](#day-23): `Frame` has a user-written move constructor without `noexcept` and a copy constructor. when a `std::vector<Frame>` reallocates, are the elements moved or copied, and why?

#### mini exercise

rewrite this C++17 helper with a range algorithm and a projection, and constrain it so that calling it with a range of something other than `Track` fails at the call site:

```cpp
const Track* most_confident(const std::vector<Track>& tracks) {
    if (tracks.empty()) return nullptr;
    auto it = std::max_element(tracks.begin(), tracks.end(),
        [](const Track& a, const Track& b) { return a.confidence < b.confidence; });
    return &*it;
}
```

#### answers

<details>
<summary>answer 1: concept satisfied, body fails</summary>

concepts are checked at the call site against the template arguments; C++20 does not check a template's body against its concepts. if `update()` calls `s.flush()` and `Sensor` never required `flush()`, the driver satisfies the concept and still fails during instantiation ([day 60](#day-60)). keep the concept in sync with what the body uses, and test the template with a minimal *archetype* type that provides exactly what the concept requires and nothing more: if the template compiles with the archetype, the concept is complete.

</details>

<details>
<summary>answer 2: owning versus referencing views</summary>

(a) is fine. `load_ids()` is an rvalue, so `views::all` wraps it in an `owning_view` that moves the vector into the pipeline (P2415, a defect report against C++20). the view owns its data.

(b) is UB. `config().ids()` is an lvalue reference into the temporary `Config`, so the pipeline holds a `ref_view` to it. the temporary is destroyed at the end of the range initializer, before the loop body runs (C++23 extends temporary lifetimes in range-for initializers; C++20 does not). GCC 12 compiles both without a warning ([day 63](#day-63)).

</details>

<details>
<summary>answer 3: subsumption needs named concepts</summary>

subsumption compares constraints as atomic pieces, and two atomic constraints are the same only if they come from the same expression in the source. the two `std::is_integral_v<T>` are different expressions, so neither overload is more constrained than the other and the call is ambiguous. write `std::integral<T>` in both: the second overload's constraint then contains the first's, subsumes it, and wins for 32-bit types.

</details>

<details>
<summary>answer 4: views into temporaries</summary>

both are non-owning views bound to a temporary that is destroyed at the end of the full-expression, so both dangle immediately ([day 55](#day-55) and [day 65](#day-65)). they compile because read-only views are deliberately constructible from temporaries, so that `f(make_name())` and `rms(make_samples())` work as function arguments, where the temporary lives long enough. a span of *mutable* elements refuses an rvalue container that is not a borrowed range, because writing into a temporary is almost always a bug. the rule: views are fine as parameters, suspicious as locals initialized from a call.

</details>

<details>
<summary>answer 5: noexcept and reallocation</summary>

copied. to keep the strong exception guarantee for `push_back` and `emplace_back`, `std::vector` moves elements during reallocation only if the move constructor is `noexcept` (or the type is not copyable); otherwise it copies, via `std::move_if_noexcept` ([day 23](#day-23)). a test with a printing `Frame` on GCC 12 prints `copy`. mark the move constructor `noexcept`, or better, follow the rule of zero ([day 25](#day-25)) and let the compiler generate it from members whose moves are already `noexcept`.

</details>

<details>
<summary>mini exercise answer</summary>

```cpp
#include <algorithm>
#include <ranges>

template <std::ranges::forward_range R>
    requires std::same_as<std::ranges::range_value_t<R>, Track>
const Track* most_confident(const R& tracks) {
    auto it = std::ranges::max_element(tracks, {}, &Track::confidence);
    return it == std::ranges::end(tracks) ? nullptr : &*it;
}
```

the projection replaces the comparison lambda, the empty case falls out of the algorithm (it returns the end iterator), and the function now accepts any forward range of `Track`: a vector, a `std::span<const Track>`, or a filtered view of confirmed tracks (taken by `const&`, which a `filter_view` does not support, so pass such a view by value or `auto&&` in real code). a constraint like `std::same_as<..., Track>` is deliberately narrow; widening it is a design decision, not a default.

</details>

#### connections

this module turned templates from a mechanism into an interface: concepts are what makes generic code readable at the call site, and ranges and span are the standard library's best examples of borrowing data instead of owning it. the next module rounds out the C++20 toolbox with comparisons, compile-time evaluation, and formatting, and then the course moves to threads, where every lifetime rule from these modules gets less forgiving.

[back to the curriculum map](#curriculum)

---

<a id="module-cpp20-everyday"></a>

## module 11: C++20: comparisons, compile time, and formatting

the spaceship operator, compile-time evaluation, std::format, and small additions that remove bug patterns.

<a id="day-67"></a>

### day 67: defaulted comparisons and the spaceship operator

**module 11:** C++20: comparisons, compile time, and formatting · **reading time:** about 6 minutes · **standard:** C++20  
**objective:** replace hand-written comparison operators with a defaulted operator<=> and operator==, and know how C++20 rewrites comparison expressions  
**builds on:** [day 61](#day-61) (writing your own concepts), [day 05](#day-05) (objects in memory: size, alignment, and padding)

#### the idea

to put a two-field grid cell in a `std::set` or sort it, C++17 asked for six operators, usually written as a pile of `std::tie` boilerplate. each one is a chance for a typo (`<=` implemented as `!(a < b)` instead of `!(b < a)`), and the next person to add a field has to update all of them.

C++20 replaces the pile with one line, but the line comes with rules: which operators the compiler synthesizes, which "kind" of ordering you get, and when it quietly stops generating `==` for you. those rules are worth ten minutes, because the failure modes are a missing operator at best and a sort with undefined behavior at worst.

#### understanding the concept

**the spaceship.** `a <=> b` returns an object that says less, equal (or equivalent), greater, or, for some types, unordered. you compare it against the literal `0`: `(a <=> b) < 0` means `a < b`.

**rewriting.** you no longer write the relational operators. for `a < b`, the compiler also considers `(a <=> b) < 0` and the reversed form `0 < (b <=> a)`; likewise for `>`, `<=`, `>=`. for `a != b` it considers `!(a == b)` and `!(b == a)`, and for `a == b` it also tries `b == a`. two consequences: one `operator==(const Meters&, double)` makes `2.0 == m` work as well, and a rewritten `!=` requires the `==` it uses to return exactly `bool`.

**defaulting.** `auto operator<=>(const T&) const = default;` compares base classes first, then non-static members **in declaration order**, lexicographically, stopping at the first difference. `bool operator==(const T&) const = default;` compares the same things with `==`. if you default `<=>` and the class declares no `operator==` at all (of any signature), the compiler also declares a defaulted `==` for you. if you *write* `<=>` yourself, it does not.

**why `==` is separate.** the original C++20 design derived `==` from `<=>`, and it was split out (P1185) for performance. equality on containers can return `false` as soon as the sizes differ (that is how the standard specifies container `==`, and mainstream `std::string` implementations do the same); a three-way comparison has to walk to the first differing element, because a shorter string can still compare greater. for two log lines of different lengths sharing a 4 KiB prefix, `==` can stop after comparing sizes, while `<=>` reads the whole prefix.

#### in code

**before and after.**

```cpp complete
#include <compare>
#include <tuple>

// C++17
struct Cell17 {
    int row, col;
    friend bool operator==(const Cell17& a, const Cell17& b) { return std::tie(a.row, a.col) == std::tie(b.row, b.col); }
    friend bool operator!=(const Cell17& a, const Cell17& b) { return !(a == b); }
    friend bool operator< (const Cell17& a, const Cell17& b) { return std::tie(a.row, a.col) <  std::tie(b.row, b.col); }
    friend bool operator> (const Cell17& a, const Cell17& b) { return b < a; }
    friend bool operator<=(const Cell17& a, const Cell17& b) { return !(b < a); }
    friend bool operator>=(const Cell17& a, const Cell17& b) { return !(a < b); }
};

// C++20
struct Cell {
    int row, col;
    auto operator<=>(const Cell&) const = default;   // also gives a defaulted ==
};
// Cell{1, 2} < Cell{1, 3}: true; result type of <=> is std::strong_ordering
```

#### in practice

defaulted comparisons pay off in the types that are compared most: keys in `std::set` and `std::map`, values checked in unit tests, messages deduplicated in a cache. one line gives a struct a complete, consistent set of operators, and when someone adds a field, equality and ordering include it automatically instead of silently ignoring it, as a forgotten line in a hand-written `operator<` would. that automatic inclusion deserves a moment in code review: adding a `last_seen_s` timestamp to a track that is used as a map key changes which tracks compare equal. whether a field participates in a type's identity is a design decision, and with defaulted comparisons the declaration is where that decision lives.

#### watch out for

**declaration order is behavior.**

reordering `row` and `col` in `Cell` changes the ordering. with the defaulted operator, declaration order is part of the type's observable behavior, so keep the most significant key first and leave a comment when it matters.

two smaller traps: writing `<=>` by hand silently removes the implicit `==` (you get "no match for 'operator=='" only where someone uses it), and a hand-written `==` that returns `int` cannot be used for a rewritten `!=` (GCC: "return type of ... is not 'bool'").

#### the takeaway

default `<=>` (and get `==` with it) when member-wise comparison in declaration order is what you mean; then the compiler writes every operator, consistently, and keeps them up to date.

#### optional challenge

given `struct Meters { double v; auto operator<=>(const Meters&) const = default; bool operator==(double d) const { return v == d; } };` and `Meters m{2.0};`, which of these compile: `m == 2.0`, `2.0 == m`, `m != 2.0`, `m == Meters{2.0}`, `m < 3.0`?

<details>
<summary>answer</summary>

`m == 2.0` calls the member directly. `2.0 == m` compiles via the reversed candidate `m == 2.0`, and `m != 2.0` via the rewritten `!(m == 2.0)`; both rely on the `==` returning `bool`.

`m == Meters{2.0}` does **not** compile, which surprises most people. declaring `operator==(double)` counts as declaring an `operator==`, so the compiler no longer adds the implicit defaulted `operator==(const Meters&)` that defaulting `<=>` would otherwise give you. add `bool operator==(const Meters&) const = default;` explicitly. (`m < Meters{3.0}` still compiles; only `==` is affected.)

`m < 3.0` does not compile either: the only `<=>` takes `const Meters&`, and `Meters` has no converting constructor from `double` (aggregate initialization is not an implicit conversion). if you want it, add `std::partial_ordering operator<=>(double d) const { return v <=> d; }`; the category is partial because of NaN. all five were checked with GCC 12.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-68"></a>

### day 68: comparison categories and custom orderings

**module 11:** C++20: comparisons, compile time, and formatting · **reading time:** about 9 minutes · **standard:** C++20  
**objective:** choose an honest comparison category, write a custom operator<=> with a consistent operator==, and keep NaN out of algorithms that need a strict weak ordering  
**builds on:** [day 67](#day-67) (defaulted comparisons and the spaceship operator)

#### the idea

one `float` member silently changes what "less than" means for a whole struct, and with it whether `std::sort` on a vector of them has defined behavior. case-insensitive keys are ordered but two different strings can compare equivalent. comparison categories make those distinctions part of the type of `<=>`'s result, so the compiler and every reader can see what kind of order a type really has.

#### understanding the concept

**comparison categories** (`<compare>`) describe what kind of order you have:

| category | values | meaning | example |
|---|---|---|---|
| `std::strong_ordering` | less, equal, greater | equal values are interchangeable | integers, `std::string` |
| `std::weak_ordering` | less, equivalent, greater | equivalent values may differ | case-insensitive keys |
| `std::partial_ordering` | less, equivalent, greater, unordered | some pairs are incomparable | `double` (NaN) |

stronger converts implicitly to weaker. a defaulted `auto operator<=>` returns the weakest category among its members, so one `float` member makes the whole struct `partial_ordering`. these categories are promises you make; the compiler does not check that your `strong_ordering` is really substitutable.

#### in code

**predict the output.** a detection with a `float` member:

```cpp
#include <cstdio>
#include <limits>

struct Detection {
    float range_m;
    int   track_id;
    auto operator<=>(const Detection&) const = default;   // std::partial_ordering
};

int main() {
    float nan = std::numeric_limits<float>::quiet_NaN();
    Detection x{nan, 1}, y{5.f, 2};
    std::printf("%d %d %d %d\n", x < y, x > y, x == y, x == x);
}
```

it prints `0 0 0 0`. `x <=> y` is `unordered`, so every relational comparison is false, and the defaulted `==` compares `range_m` with `==`, so `x == x` is false too. equality that is not reflexive breaks `std::find`, `std::set`, and any cache keyed on the struct.

**a custom ordering, and the `==` you must write.** a parameter server whose keys compare case-insensitively:

```cpp complete
#include <algorithm>
#include <cctype>
#include <string>

class ParamKey {
public:
    explicit ParamKey(std::string s) : s_(std::move(s)) {}
    std::weak_ordering operator<=>(const ParamKey& o) const {
        return std::lexicographical_compare_three_way(          // C++20 algorithm
            s_.begin(), s_.end(), o.s_.begin(), o.s_.end(),
            [](unsigned char a, unsigned char b) { return std::tolower(a) <=> std::tolower(b); });
    }
    bool operator==(const ParamKey& o) const { return (*this <=> o) == 0; }  // not generated
private:
    std::string s_;
};
// std::set<ParamKey>: inserting "MaxVelocity" then "maxvelocity" leaves size 1
```

`weak_ordering` is the honest category: `"MaxVelocity"` and `"maxvelocity"` are equivalent for ordering but are not the same string. the hand-written `==` must agree with `<=>`; a defaulted one here would compare case-sensitively and contradict the ordering.

#### in practice

a deployment tool decides whether to flash new firmware. versions look like `2.1.0-rc1` and, per semantic versioning, a prerelease sorts *before* its release. the defaulted operator gets that wrong, because the empty string sorts before `"rc1"`:

```cpp
struct Version {
    int major = 0, minor = 0, patch = 0;
    std::string pre;   // empty for a release
    std::strong_ordering operator<=>(const Version& o) const {
        if (auto c = std::tie(major, minor, patch) <=> std::tie(o.major, o.minor, o.patch); c != 0)
            return c;
        if (pre.empty() != o.pre.empty())   // a release outranks its prereleases
            return pre.empty() ? std::strong_ordering::greater : std::strong_ordering::less;
        return pre <=> o.pre;               // simplified: full semver compares dot-separated parts
    }
    bool operator==(const Version&) const = default;
};
// sorted: 2.0.9  2.1.0-rc1  2.1.0
```

`std::tie(...) <=> std::tie(...)` uses C++20's `<=>` on `std::tuple`, which keeps the "compare these three in order" logic in one line. defaulting `==` is fine here: two versions are equal exactly when all four fields are, which agrees with the custom ordering.

leave out that `==` and you find out quickly: `std::ranges::sort(versions)` and `std::ranges::max(versions)` stop compiling, because `std::totally_ordered` ([day 61](#day-61)) requires equality as well as ordering. the concept caught a half-specified type at the call site.

#### watch out for

**partial orders in algorithms that require a strict weak ordering.** `std::sort`, `std::set`, and `std::map` require that the comparison be a strict weak ordering over the values you actually pass. with NaN in the data, `<` on `double` (or on a struct whose defaulted `<=>` is `partial_ordering`) is not one, and violating that precondition is undefined behavior. typically you get silently misordered output; with some invalid comparators, implementations have also been known to read past the end of the range. either reject NaN at the boundary (a sensor driver is a good place) or sort with `std::strong_order`, which for IEEE 754 types implements the `totalOrder` predicate (-0 before +0, positive NaNs after all numbers):

```cpp
std::sort(v.begin(), v.end(), [](double a, double b) { return std::strong_order(a, b) < 0; });
// {3, NaN, -0.0, 0.0, 1} sorts to: -0 0 1 3 nan
```

#### the takeaway

default `<=>` (and get `==` for free) when member-wise lexicographic order in declaration order is what you mean. when it is not, write `<=>` with an honest category and write `==` next to it, consistent with it. watch any `float` member: it turns your type's ordering into a partial one.

#### optional challenge

which comparison category should `operator<=>` return for each type: (a) a timestamp stored as integer nanoseconds; (b) a file path compared case-insensitively; (c) a 2D point ordered by its distance from the origin; (d) a sensor reading whose value is a `double`?

<details>
<summary>answer</summary>

(a) `std::strong_ordering`: equal timestamps are interchangeable. (b) `std::weak_ordering`: `"Log.TXT"` and `"log.txt"` are equivalent for ordering but are different values. (c) `std::weak_ordering`: distinct points at the same distance are equivalent, not equal, and calling that `strong` would be a false promise to any code that substitutes one for the other. (d) `std::partial_ordering`, because NaN is unordered; if the type's invariant excludes NaN (checked in its constructor), you may document and return a stronger category, but then the check is what makes the promise true.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-69"></a>

### day 69: constexpr in C++20: computing at compile time

**module 11:** C++20: comparisons, compile time, and formatting · **reading time:** about 8 minutes · **standard:** C++20  
**objective:** write constexpr functions that build tables and use transient allocation, force and test their evaluation, and weigh compile-time work against its costs  
**builds on:** [day 06](#day-06) (storage duration and object lifetime), [day 44](#day-44) (compile-time branching with if constexpr), [day 60](#day-60) (concepts: constraining templates)

#### the idea

a radar firmware computes its CRC-32 lookup table in a global constructor: `static CrcTable g_crc;`. months later someone adds a static `PacketLogger` in another translation unit that checksums a startup banner. on one build configuration every checksum at startup is wrong, because the logger's constructor runs before the table's. that is the static initialization order fiasco from [day 06](#day-06), and the fix is not to order the constructors more cleverly. it is to make the table exist before any constructor runs at all: compute it at compile time.

#### understanding the concept

**`constexpr` functions** may be evaluated during constant evaluation, when their arguments are constants and the context requires a constant (a `constexpr` variable, an array bound, a template argument, `static_assert`). called with runtime values, they are ordinary functions. each standard widened what they may contain: C++11 allowed a single `return`, C++14 loops and local variables, C++17 lambdas. C++20 adds:

- `try` blocks (but actually evaluating a `throw` during constant evaluation is a compile error),
- virtual function calls, `dynamic_cast`, and `typeid`,
- changing the active member of a union, and uninitialized local variables (reading one is still an error),
- **transient dynamic allocation**: `new`/`delete`, and therefore `std::vector` and `std::string` (library support for `constexpr` `std::vector` and `std::string`: libstdc++ in GCC 12, libc++ 15, MSVC 19.29). memory allocated during a constant evaluation must be freed within that same evaluation. you can build a vector at compile time and return its size or copy it into a `std::array`; you cannot have a `constexpr std::vector` variable.

#### in code

**a compile-time table, tested by the compiler.**

```cpp complete
#include <array>
#include <cstdint>
#include <string_view>

constexpr std::array<std::uint32_t, 256> make_crc_table() {
    std::array<std::uint32_t, 256> table{};
    for (std::uint32_t i = 0; i < 256; ++i) {
        std::uint32_t c = i;
        for (int k = 0; k < 8; ++k)
            c = (c & 1u) ? 0xEDB88320u ^ (c >> 1) : c >> 1;
        table[i] = c;
    }
    return table;
}
inline constexpr auto crc_table = make_crc_table();   // no constructor, no ordering

constexpr std::uint32_t crc32(std::string_view data) {
    std::uint32_t c = 0xFFFFFFFFu;
    for (unsigned char b : data)
        c = crc_table[(c ^ b) & 0xFFu] ^ (c >> 8);
    return c ^ 0xFFFFFFFFu;
}
static_assert(crc32("123456789") == 0xCBF43926u);   // the standard CRC-32 check value
```

the same `crc32` serves runtime packets and compile-time tests. the `static_assert` is a unit test that runs on every build and cannot be skipped.

**transient allocation.** C++20 lets constant evaluation use the heap, as long as nothing escapes:

```cpp complete
#include <vector>

constexpr int count_primes(int n) {
    std::vector<bool> composite(n + 1, false);   // allocated and freed during evaluation
    int count = 0;
    for (int i = 2; i <= n; ++i) {
        if (composite[i]) continue;
        ++count;
        for (int j = 2 * i; j <= n; j += i) composite[j] = true;
    }
    return count;
}
static_assert(count_primes(100) == 25);

// constexpr std::vector<int> v{1, 2, 3};
// error: ... is not a constant expression because it refers to a result of 'operator new'
```

#### in practice

in embedded radar firmware the CRC table above lives in read-only memory (1 KiB), costs nothing at boot, and cannot be observed half-initialized. the alternative, computing it at startup into RAM, costs a few thousand simple operations once at boot and 1 KiB of RAM instead of flash. on a microcontroller with scarce RAM and plenty of flash, compile-time wins; on a desktop it hardly matters, and the real benefit is removing an initialization-order dependency.

the costs are real, though. constant evaluation is interpreted by the compiler, and compilers impose limits. as a data point on the machine used to check this course: `static_assert(count_primes(100000) == 9592)` hit GCC 12's default operation limit ("'constexpr' evaluation operation count exceeds limit of 33554432"), and with `-fconstexpr-ops-limit` raised it added about 7 seconds to the build, while the same call at runtime finished within process startup time. anything big generated in a header is paid for by every translation unit that includes it; put it in one `.cpp` file. you cannot step through constant evaluation in a debugger, so keep `constexpr` functions callable at runtime and unit test them there too. and a large generated table makes the binary bigger. "move it to compile time" is a tradeoff between build time, binary size, startup time, and debuggability, not a free win.

#### watch out for

**`constexpr` on a function is permission, not a command.** a local `const auto t = make_crc_table();` may well run at runtime: only a context that requires a constant forces evaluation. if you need the guarantee, use a `constexpr` (or `constinit`) variable, or a `consteval` function.

**compiler extensions leak in.** GCC accepts `constexpr double s = std::sin(0.5);` even with `-pedantic`, because it constant-folds its math builtins. `<cmath>` functions are not `constexpr` in C++20, and other compilers may reject it. later standards make more of `<cmath>` `constexpr`; until you target one, compute such tables with your own `constexpr` series or generate them offline.

#### the takeaway

a `constexpr` function may run at compile time and still works at run time; force evaluation with a `constexpr` variable or `static_assert`, use that as a free unit test, and treat moving work to compile time as a tradeoff, not a free win.

#### optional challenge

which of these are guaranteed to evaluate `make_crc_table()` at compile time?

```cpp
constexpr auto a = make_crc_table();                 // (1) namespace scope
void f() {
    const auto b = make_crc_table();                 // (2)
    static const auto c = make_crc_table();          // (3)
    static_assert(make_crc_table()[1] != 0);         // (4)
}
```

<details>
<summary>answer</summary>

(1), (3), and (4). a `constexpr` variable (1) must be initialized by a constant expression. a `static` local (3) has static storage duration, and a static variable whose initializer is a constant expression is *constant-initialized*, which is a language guarantee rather than an optimization. a `static_assert` (4) is a context that requires a constant. (2) is an ordinary local: the compiler may fold the call, and at higher optimization levels it probably will, but nothing requires it.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-70"></a>

### day 70: consteval and constinit

**module 11:** C++20: comparisons, compile time, and formatting · **reading time:** about 6 minutes · **standard:** C++20  
**objective:** use consteval for functions that must run at compile time and constinit for mutable globals that must be initialized before any constructor runs  
**builds on:** [day 69](#day-69) (constexpr in C++20: computing at compile time)

#### the idea

C++20 gives you three keywords for this, and they make three different promises. `constexpr` says "can run at compile time". `consteval` says "must run at compile time". `constinit` says "this variable is initialized at compile time, but it is not a constant". mixing them up is the most common mistake in this area.

the difference matters in exactly the places compile-time code is most useful: validating constants that would otherwise be checked at run time (or never), and making mutable globals safe from the initialization order problems in [day 06](#day-06).

#### understanding the concept

**`consteval`** declares an *immediate function*: every call must be a constant expression, or the program is ill-formed. that turns "this should be folded" into "this is checked". because a `throw` reached during constant evaluation is an error, a `consteval` function that throws on bad input becomes a compile-time validator. that is exactly how C++20 checks `std::format` strings ([day 71](#day-71)): `std::format_string` has a `consteval` constructor that parses the literal.

**`constinit`** applies to variables with static or thread storage duration. it asserts that the variable is constant-initialized (initialized before any dynamic initialization runs), and makes it an error if it is not. the variable stays mutable. it answers [day 06](#day-06)'s fiasco for globals that must be mutable: a `constinit` counter or pointer is valid before any constructor in any translation unit runs.

**`std::is_constant_evaluated()`** (`<type_traits>`) returns `true` when called during constant evaluation, so a `constexpr` function can use a portable loop at compile time and an intrinsic or `memcpy` at runtime. use it with plain `if`, never `if constexpr` (see "watch out for"). C++23's `if consteval` is a cleaner spelling; it is not C++20.

#### in code

**`consteval` and `constinit`.**

```cpp complete
#include <cstdint>
#include <numbers>

consteval double deg_to_rad(double deg) { return deg * std::numbers::pi / 180.0; }

consteval std::uint8_t can_channel(int ch) {
    if (ch < 0 || ch > 15) throw "CAN channel out of range";   // compile-time diagnostic
    return static_cast<std::uint8_t>(ch);
}

constexpr double joint_limit = deg_to_rad(170.0);   // 2.967060
constexpr auto steering_bus  = can_channel(3);
// can_channel(16);    error: expression '<throw-expression>' is not a constant expression
// deg_to_rad(runtime_angle);  error: the value of 'runtime_angle' is not usable in a constant expression

int compute_default();
constinit int retry_budget = 5;                    // OK: mutable, initialized before any constructor
// constinit int bad = compute_default();
// error: 'constinit' variable 'bad' does not have a constant initializer
```

`deg_to_rad` as `consteval` is a design choice: it says "this conversion is for constants in source code", and a runtime angle must go through a different (runtime) function. that keeps an accidental per-cycle conversion out of a control loop, but it also means you cannot reuse it at runtime. choose `constexpr` when both uses are legitimate.

#### in practice

`constinit` is the C++20 answer for mutable globals that other startup code may touch, which is common in embedded and real-time code: a statistics counter, a pointer to the active configuration, a flag set by an interrupt handler.

```cpp complete
#include <atomic>

constinit std::atomic<unsigned> g_dropped_frames{0};   // valid before any constructor runs
constinit const char* g_active_profile = "default";    // mutable pointer, constant initializer
```

both are initialized before any dynamic initialization in any translation unit, so a static constructor elsewhere can safely increment the counter or read the profile. and if a later edit changes either initializer into something that needs code at startup, the build fails instead of quietly reintroducing the ordering problem. `consteval` plays the same role for constants: register addresses, bus channels, unit conversions, and format strings ([day 71](#day-71)) can be validated where they are written, so an out-of-range value never reaches the hardware.

#### watch out for

**`if constexpr (std::is_constant_evaluated())` is always true**, because the condition of `if constexpr` is itself a constant evaluation. your runtime branch becomes dead code. GCC 12 warns: "'std::is_constant_evaluated' always evaluates to true in 'if constexpr'". use a plain `if`.

#### the takeaway

`constexpr` means "may run at compile time", `consteval` means "must", and `constinit` means "initialized at compile time, mutable afterwards". use compile-time evaluation to remove startup ordering problems and to turn checks into build errors, and weigh it against build time, binary size, and debuggability.

#### optional challenge

```cpp complete
constexpr int sq(int x) { return x * x; }
int g = sq(4);                 // namespace scope

int main() {
    int l = sq(4);             // local
}
```

is `g` guaranteed to be initialized at compile time? is `l`? what changes if you write `constinit int g = sq(4);`?

<details>
<summary>answer</summary>

`g` is guaranteed: a variable with static storage duration whose initializer is a constant expression undergoes *constant initialization*, which happens before any dynamic initialization. that is a language rule, not an optimization. `l` is not guaranteed: it is an ordinary local, and whether `sq(4)` is folded is up to the compiler. (GCC 12 happens to fold it even at `-O0`; that is an implementation choice, not a guarantee.)

`constinit` does not change the behavior of `g`; it adds a check. if someone later changes `sq` so it is no longer `constexpr`, plain `int g = sq(4);` silently becomes dynamic initialization, and the [day 06](#day-06) ordering problem is back. with `constinit`, that change is a compile error.

</details>

#### going deeper (optional)

##### class types as template arguments

C++20 also allows class types as non-type template parameters, if they are *structural* (public members, no `mutable`, all members structural). a small `fixed_string` lets a string literal become part of a type, so `Counter<"dropped_frames">` and `Counter<"crc_errors">` are distinct types with their own static storage. libraries use this for compile-time format strings, units, and register maps.

[back to the curriculum map](#curriculum)

---

<a id="day-71"></a>

### day 71: `std::format`: type-safe formatting

**module 11:** C++20: comparisons, compile time, and formatting · **reading time:** about 8 minutes · **standard:** C++20  
**objective:** format text with `std::format` and its spec mini-language, keep format strings compile-time checked in your own wrappers, and avoid allocation with format_to_n  
**builds on:** [day 70](#day-70) (consteval and constinit), [day 43](#day-43) (variadic templates and perfect-forwarding factories), [day 55](#day-55) (`std::string_view`: borrowing characters)

#### the idea

every C++ codebase formats text, and until C++20 the standard offered two bad choices. `printf("%llu", frame_id)` is compact, but passing an argument whose type does not match the conversion specifier is undefined behavior, and `std::uint64_t` is `unsigned long` on LP64 Linux, so `%llu` is wrong there and right on Windows. iostreams are type-safe, but `std::cout << std::setw(8) << std::fixed << std::setprecision(3) << x` is verbose, and `std::fixed` and `setprecision` stay set on the stream for whoever prints next.

`std::format` (C++20, `<format>`) keeps printf's compact format strings, gets the type from the argument instead of the string, checks the string at compile time, and has no hidden stream state.

**library support:** `<format>` needs GCC 13+, Clang with libc++ 17+, or MSVC 19.29+ (Visual Studio 2019 16.10), and the compile-time checking described below needs a recent version of each. on older toolchains, the {fmt} library (`fmt::format`) offers the same syntax; `std::format` was standardized from it. GCC 12, used to check this course, has no `<format>`, so the `std::format` code in this lesson is written against the standard but **not compile-checked**. the tour at the end was compiled with GCC 12.

#### understanding the concept

a replacement field is `{index:spec}`. both parts are optional; `{}` takes the next argument. the spec mini-language is `[[fill]align][sign][#][0][width][.precision][type]`: `{:>10.3f}` is right-aligned, width 10, three decimals, fixed; `{:#x}` is hex with a `0x` prefix; `{:*^9}` centers in nine characters, padded with `*`. each type defines which specs it accepts.

**compile-time checking.** in C++20 as amended by P2216 (a defect report, so it applies to C++20 mode), the format string parameter is not a plain `string_view`. it is `std::format_string<Args...>`, whose constructor is `consteval` ([day 70](#day-70)): it parses the literal during compilation, against the actual argument types. a bad spec or a missing argument is a compile error at your call site. (P2508 made the name `std::format_string` public for user code; current versions of the implementations above provide it in C++20 mode.) the flip side: the format string must be a constant expression. for a string known only at runtime (a user-configurable log template), call `std::vformat(fmt, std::make_format_args(a, b))`, which throws `std::format_error` on a bad string.

**locale.** `std::format` is locale-independent unless you ask for it with the `L` option. `{:.2f}` always uses `.` as the decimal separator, which is what you want for telemetry and file formats; printf follows the C locale (`LC_NUMERIC`).

#### in code

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

#### in practice

a joint-controller thread logs at 1 kHz and must not allocate in steady state ([day 109](#day-109) has the details). `std::format` returns a `std::string`, which can allocate. `std::format_to` writes to any output iterator, and `std::format_to_n` writes at most `n` characters, so a reusable fixed buffer avoids the result allocation:

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

the standard does not promise that formatting performs no internal allocation, so verify with an allocation counter ([day 109](#day-109)) on your implementation before you rely on it in a real-time loop.

your own logging wrapper must keep the compile-time check. take `std::format_string<Args...>`, not `std::string_view`:

```cpp
template <typename... Args>
void log_info(std::format_string<Args...> fmt, Args&&... args) {
    write_line(std::format(fmt, std::forward<Args>(args)...));
}
// log_info("joint {} over limit by {:.2f}", id);   compile error at *this* call: missing argument
```

a `std::string_view fmt` parameter cannot be passed on to `std::format` at all (it is not a constant expression), and the usual "fix", switching to `std::vformat`, silently moves every format error from compile time to runtime.

#### watch out for

**assuming `<format>` exists everywhere.**

the other trap is assuming `std::format` exists. libraries that must build on GCC 12 or older Clang often use {fmt} directly, or a thin wrapper that switches between `std::format` and `fmt::format`, rather than sprinkling feature tests (`__cpp_lib_format`) around the codebase.

#### the takeaway

`std::format` combines printf's compact syntax with type safety, compile-time checked format strings, and no stream state; keep the check alive in your wrappers with `std::format_string`, and use `format_to_n` when allocation matters.

#### optional challenge

a colleague writes `std::string msg = std::format(cfg.log_template, id, value);`, where `log_template` is a `std::string` loaded from a config file. does it compile? if not, what is the correct replacement, and what new failure mode does it introduce?

<details>
<summary>answer</summary>

it does not compile in C++20 (as amended by P2216): the format string is converted to `std::format_string<int, double>` through a `consteval` constructor, and a runtime `std::string` is not a constant expression. the replacement is `std::vformat(cfg.log_template, std::make_format_args(id, value))`, with `id` and `value` as lvalues (`make_format_args` stores references to them). the new failure mode is runtime: a template like `"{} {} {}"` or `"{:d}"` applied to a `double` throws `std::format_error`. validate the template once when the config is loaded (format it with representative values inside a `try`), not on every log call.

</details>

#### going deeper (optional)

##### a formatter for your own types

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

[back to the curriculum map](#curriculum)

---

<a id="day-72"></a>

### day 72: small C++20 features that remove bug patterns

**module 11:** C++20: comparisons, compile time, and formatting · **reading time:** about 6 minutes · **standard:** C++20  
**objective:** adopt the small C++20 library and language additions that replace error-prone idioms in everyday code  
**builds on:** [day 71](#day-71) (`std::format`: type-safe formatting), [day 36](#day-36) (iterators and algorithms over raw loops), [day 14](#day-14) (the usual suspects: aliasing, punning, and evaluation order)

#### the idea

`m.find(k) != m.end()` to ask a yes-or-no question, an erase-remove pair that is easy to get half right, `(lo + hi) / 2` that overflows, `s.substr(0, 7) == "/radar/"`, positional struct initialization that silently shifts when someone inserts a field. none of these is hard, and each has a long history of small bugs. C++20 added a set of small features whose main value is not saving keystrokes but removing one bug pattern each.

#### understanding the concept

| feature | replaces | bug pattern removed |
|---|---|---|
| designated initializers `{.kp = 2.5}` | positional aggregate initialization | arguments shifting when a field is inserted |
| `contains(key)` | `find(key) != end()`, `count(key) != 0` | noise, and accidental `operator[]` inserts |
| `std::erase`, `std::erase_if` | the erase-remove idiom | the single-iterator `erase` bug from [day 36](#day-36) |
| `starts_with`, `ends_with` | `substr` or `compare` with offsets | off-by-one and length mistakes |
| `std::source_location` | `__FILE__` and `__LINE__` macros | macros, and losing the *caller's* location |
| `std::bit_cast`, `std::popcount`, `std::endian` | pointer punning, compiler builtins | undefined behavior and non-portable code |
| `using enum` | repeated qualification in `switch` | noise in exhaustive switches |
| `std::midpoint`, `std::ssize` | `(a + b) / 2`, `size() - 1` loops | signed overflow and unsigned wraparound |

#### in code

excerpts from one file that was compiled and run with GCC 12, `-std=c++20`:

```cpp
#include <bit>
#include <climits>
#include <cstdint>
#include <map>
#include <numeric>
#include <source_location>
#include <string_view>
#include <vector>

struct PidConfig { double kp = 1.0; double ki = 0.0; double kd = 0.0; int rate_hz = 100; };
PidConfig cfg{.kp = 2.5, .kd = 0.1};   // designated initializers: ki and rate_hz keep defaults
// PidConfig bad{.kd = 0.1, .kp = 2.5};  error: designator order ... does not match declaration order

bool known = tracks.contains(42);                            // map, set, unordered_*: no find() != end()
bool radar = topic.starts_with("/radar/");                   // string and string_view; also ends_with
auto removed = std::erase_if(ids, [](int id) { return id < 0; });   // replaces erase-remove

void trace(std::string_view msg, std::source_location loc = std::source_location::current());
// default argument is evaluated at the call site: prints the caller's file, line, function

std::popcount(0b1011u);                  // 3; unsigned types only: popcount(11) does not compile
std::bit_cast<std::uint32_t>(1.0f);      // 0x3F800000 with IEEE 754 float; no UB, unlike type punning
std::endian::native == std::endian::little;

enum class Mode { idle, tracking, fault };
switch (m) { using enum Mode; case idle: /* ... */ case tracking: /* ... */ case fault: /* ... */ }

std::midpoint(INT_MAX - 2, INT_MAX);     // 2147483646; (a + b) / 2 would overflow: UB
for (auto i = std::ssize(ids) - 1; i >= 0; --i) { /* signed index, no wraparound */ }
```

designated initializers must follow declaration order, cannot nest (`.pose.x`), and cannot be mixed with positional ones; they make configuration structs self-documenting at the call site. `std::bit_cast` (introduced on [day 14](#day-14) as the fix for type punning) is `constexpr` and requires equal sizes and trivially copyable types; the bit pattern itself depends on the implementation's floating-point representation.

#### in practice

designated initializers change how configuration code reads and how it fails. a radar configuration built positionally, `RadarConfig cfg{250.0, 512, 8, true};`, cannot be reviewed without opening the header, and inserting a field before `num_bins` silently shifts every later value into the wrong member when the types are compatible. the designated version, `RadarConfig cfg{.max_range_m = 250.0, .num_bins = 512, .chirps = 8, .enable_cfar = true};`, documents itself at the call site, lets omitted fields keep their default member initializers, and turns a reordered or renamed field into a compile error instead of a misconfigured sensor. the order rule (designators must follow declaration order) is a small price, and it is checked by the compiler.

#### watch out for

**`[[likely]]` and `[[unlikely]]` are hints, not optimizations.** written as `if (frame.empty()) [[unlikely]] { return; }`, they influence block layout and branch weighting; they do not make code faster by themselves, and a wrong hint can make it slower. use them only where a profile ([day 106](#day-106)) shows a hot branch with a stable, known bias, such as an error path. profile-guided optimization derives the same information from measured frequencies, and unlike a hand annotation it does not go stale when the code around it changes.

#### the takeaway

each of these small features removes a specific bug pattern: adopt them where they replace the error-prone idiom, and treat performance hints like `[[likely]]` as measurements to justify, not decorations.

#### optional challenge

what do these produce, and which one does not compile?

```cpp
std::vector<int> v;
auto a = std::midpoint(0u, 10u);              // (1)
auto b = std::ssize(v) - 1;                   // (2)
auto c = std::popcount(-1);                   // (3)
auto d = std::bit_cast<float>(0x3F800000u);   // (4)
```

<details>
<summary>answer</summary>

(1) is `5u`. (2) is `-1` of a signed type (`std::ptrdiff_t`), so a loop down to zero behaves, unlike `v.size() - 1`, which wraps to a huge unsigned value. (3) does not compile: `std::popcount` accepts only unsigned integer types, deliberately, because the bit count of a negative number depends on its width; write `std::popcount(static_cast<unsigned>(x))` to say which width you mean. (4) is `1.0f` on any platform whose `float` is IEEE 754 single precision, with no undefined behavior.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-73"></a>

### day 73: review: comparisons, compile time, and formatting

**module 11:** C++20: comparisons, compile time, and formatting · **reading time:** about 8 minutes · **standard:** C++20  
**objective:** consolidate defaulted comparisons and categories, constexpr, consteval and constinit, `std::format`, and the small C++20 features  
**covers:** [day 67](#day-67) to [day 72](#day-72)

#### recap

| lesson | key idea |
|---|---|
| [day 67](#day-67) | one defaulted `<=>` gives every relational operator and a defaulted `==`; declaration order is behavior. |
| [day 68](#day-68) | strong, weak, partial: a `float` member makes ordering partial, and NaN breaks algorithms that need a strict weak ordering. |
| [day 69](#day-69) | `constexpr` may run at compile time, including transient allocation; force it and test it with `static_assert`. |
| [day 70](#day-70) | `consteval` must run at compile time; `constinit` initializes a mutable global before any constructor runs. |
| [day 71](#day-71) | type-safe, compile-time checked formatting; keep the check in wrappers with `std::format_string`. |
| [day 72](#day-72) | small additions that each remove a bug pattern: designated initializers, `contains`, `erase_if`, `midpoint`, `ssize`. |

#### review questions

1. a tracker keeps `std::set<Detection>`, where `Detection` has a `float range_m` member and `auto operator<=>(const Detection&) const = default;`. one radar frame contains a NaN range. what is wrong, precisely, and what are two reasonable fixes?
2. pick `constexpr`, `consteval`, or `constinit` for each: (a) a global, mutable `Logger* g_logger` that must be valid before any static constructor in any translation unit runs; (b) a function that validates CAN channel numbers written as literals in source code and must reject bad ones at build time; (c) a CRC function used both in `static_assert` tests and on runtime packets.

3. why should a project's `log_info` wrapper take `std::format_string<Args...>` rather than `std::string_view` for its format parameter?
4. from [day 04](#day-04): `for (std::size_t i = v.size() - 1; i >= 0; --i)` never terminates. why, and how does a C++20 helper make the reverse loop correct?

#### mini exercise

write a constrained function `rms` that takes a `std::span` of numeric samples (integers or floating point, but not `bool`), returns an empty `std::optional<double>` for an empty span, and works when called directly with a `std::vector<float>` or a `std::array<std::int16_t, N>`. then print the result with `std::format` to three decimals. hint: try calling your first version with a `std::vector<float>` before reading the answer.

#### answers

<details>
<summary>answer 1: NaN in a set</summary>

a `float` member makes the defaulted `<=>` return `std::partial_ordering`, and with NaN, `<` is not a strict weak ordering: the NaN detection is "equivalent" to everything, which breaks transitivity of equivalence. `std::set` requires a strict weak ordering over the values it holds, so violating it is undefined behavior (typical symptoms: lookups that miss and duplicates that should have been rejected). the defaulted `==` is not even reflexive for that element.

fixes: reject or sanitize NaN at the driver boundary, so the invariant "range is finite" holds for every `Detection`; or define the ordering with `std::strong_order` on the float (IEEE `totalOrder`) or on a non-float key such as a track id ([day 67](#day-67)).

</details>

<details>
<summary>answer 2: compile-time keywords</summary>

(a) `constinit Logger* g_logger = nullptr;`: constant-initialized, so it is valid before any dynamic initialization, and still assignable later. (b) `consteval`: every call must be a constant expression, and a `throw` reached during evaluation becomes a compile error. (c) `constexpr`: usable in constant expressions and at runtime ([day 69](#day-69)).

</details>

<details>
<summary>answer 3: format_string in wrappers</summary>

the compile-time check lives in the `consteval` constructor of `std::format_string<Args...>`, which runs when the caller's string literal is converted to the parameter type. a wrapper taking `std::format_string<Args...>` performs that conversion at *its* caller, against the real argument types, so a missing argument or bad spec fails there. a `std::string_view` parameter cannot be passed to `std::format` (it is not a constant expression), and switching to `std::vformat` moves every format error to runtime as `std::format_error` ([day 71](#day-71)).

</details>

<details>
<summary>answer 4: the reverse loop</summary>

`i` is unsigned, so `i >= 0` is always true: after `i` reaches 0, `--i` wraps to the largest `std::size_t` and the loop indexes far out of bounds (and for an empty `v`, it starts there). use a signed index: `for (auto i = std::ssize(v) - 1; i >= 0; --i)`, where `std::ssize` returns `std::ptrdiff_t`.

</details>

<details>
<summary>mini exercise answer</summary>

```cpp complete
#include <cmath>
#include <concepts>
#include <format>       // GCC 13+; the rest compiles with GCC 12
#include <optional>
#include <ranges>
#include <span>

template <typename T>
concept Numeric = (std::integral<T> && !std::same_as<T, bool>) || std::floating_point<T>;

template <Numeric T>
std::optional<double> rms(std::span<const T> xs) {
    if (xs.empty()) return std::nullopt;
    double acc = 0.0;
    for (T x : xs) acc += static_cast<double>(x) * static_cast<double>(x);
    return std::sqrt(acc / static_cast<double>(xs.size()));
}

// Deduction does not look through conversions: rms(vec) cannot deduce T
// from span<const T> ("'std::vector<float>' is not derived from 'std::span<const T>'").
// This overload accepts any contiguous range of Numeric and forwards to the span version.
template <std::ranges::contiguous_range R>
    requires std::ranges::sized_range<R> && Numeric<std::ranges::range_value_t<R>>
std::optional<double> rms(const R& r) {
    using T = std::ranges::range_value_t<R>;
    return rms(std::span<const T>(std::ranges::data(r), std::ranges::size(r)));
}

// std::vector<float> v{3.f, 4.f};
// if (auto r = rms(v)) std::string line = std::format("rms {:.3f} over {} samples", *r, v.size());
//                                       // "rms 3.536 over 2 samples"
```

the trap the hint points at is [day 40](#day-40)'s rule meeting [day 65](#day-65)'s type: template argument deduction does not consider implicit conversions, so a function template taking `std::span<const T>` cannot be called with a vector, an array, or even a `std::span<float>` (mutable elements) without help. the options are an explicit argument (`rms<float>(v)`), a non-template function for the one type you need, or a forwarding overload like the one above. the `!std::same_as<T, bool>` matters because `bool` is an integral type, and "the RMS of a bool vector" is almost certainly a bug; `std::vector<bool>` is also not a contiguous range, so it is rejected either way.

</details>

#### connections

with this module the C++20 toolbox is complete: constrained templates, ranges and views, span, comparisons, compile-time evaluation, and formatting. none of it changes the foundations from the first modules; each feature makes an existing intent checkable. the next two modules are about threads, where the ownership and lifetime rules from the whole course meet a new kind of undefined behavior: data races ([day 76](#day-76)).

[back to the curriculum map](#curriculum)

---

<a id="module-threads"></a>

## module 12: threads and synchronization

owning threads, data races, mutexes, condition variables, and a bounded queue with clean shutdown.

<a id="day-74"></a>

### day 74: `std::thread`: starting, joining, and passing arguments

**module 12:** threads and synchronization · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** start and join threads safely, explain why a joinable `std::thread` terminates the program on destruction, and pass arguments without dangling  
**builds on:** [day 16](#day-16) (RAII: let scope do the cleanup), [day 19](#day-19) (construction and destruction order), [day 38](#day-38) (lambdas that outlive their scope: callbacks and `std::function`)

#### the idea

you have a sensor driver that polls an IMU every 10 ms on its own thread. starting the thread is one line. stopping it correctly, on every path including exceptions and early returns, is where the bugs live. if a `std::thread` object is destroyed while it still represents a running thread, your process does not leak or hang: it calls `std::terminate`. sharing data between threads comes later; it starts with owning threads safely.

#### understanding the concept

a `std::thread` is a handle that owns at most one thread of execution. constructing it with a callable starts the thread; the standard says the end of the constructor *synchronizes with* the start of the callable, so everything the parent did before constructing the thread is visible inside it. when the thread finishes, its completion synchronizes with the return of `join()`, so everything the thread did is visible after `join` returns. we will make "synchronizes with" precise on [day 84](#day-84); for now, `join` is your visibility guarantee.

a thread object is *joinable* if it still owns a thread. it stops being joinable after `join()`, `detach()`, or being moved from. destroying (or move-assigning to) a joinable `std::thread` calls `std::terminate`. that sounds harsh, but both alternatives were worse: an implicit `join` can hang a destructor forever, and an implicit `detach` lets the thread keep running with references to locals that are gone.

`detach()` is rarely right. a detached thread cannot be waited for, so you cannot know when it has stopped touching your objects. at process exit, static objects are destroyed while a detached thread may still be running, and any access to an object after its lifetime ends is UB. use `detach` only for work that touches nothing but its own copies, and even then, ask what happens at shutdown.

arguments are *decay-copied* into storage owned by the new thread, in the constructing thread, and then passed to the callable as rvalues. two consequences follow. a parameter of type `T&` will not bind unless you pass `std::ref(x)`, and then `x`'s lifetime is your problem. and any conversion to the parameter type (say `const char*` to `std::string`) happens later, inside the new thread.

if an exception escapes the thread's top-level function, `std::terminate` is called. there is nobody to catch it. [day 81](#day-81) shows how futures carry exceptions across threads.

#### in code

**how arguments travel.**

```cpp ub
#include <string>
#include <thread>
#include <vector>

void fill(std::vector<double>& out) { out.assign(1024, 0.0); }
void log_line(const std::string& s) { /* write s somewhere */ }

void demo() {
    std::vector<double> samples;
    // std::thread t1(fill, samples);         // error: the copy is an rvalue, cannot bind to double&
    std::thread t1(fill, std::ref(samples));  // OK: samples must outlive the thread
    t1.join();                                // join makes the writes to samples visible here

    char buf[32] = "radar link up";
    std::thread t2(log_line, buf);            // BUG: buf decays to char*; the std::string
    t2.detach();                              // is built later, in t2, maybe after buf is gone (UB)

    std::thread t3(log_line, std::string(buf));  // fixed: convert before the thread starts
    t3.join();
}
```

**a member thread, started too early.**

```cpp ub
#include <atomic>
#include <chrono>
#include <thread>

class ImuPoller {
public:
    ImuPoller() : worker_([this] { run(); }) {}
    ~ImuPoller() {
        running_ = false;
        worker_.join();
    }
private:
    void run() {
        while (running_) {                       // may run before running_ is initialized
            poll_once();
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }
    void poll_once() { /* read registers, publish a sample */ }

    std::thread worker_;                         // BUG: declared first, so started first
    std::atomic<bool> running_{true};
};
```

members are initialized in declaration order ([day 19](#day-19)), so the thread starts before `running_` exists. initializing an atomic is not an atomic operation, so the thread's load races with it: undefined behavior. declaring `running_` first fixes that, but the class still needs a hand-written destructor that stops and joins, and every author writes that shutdown logic slightly differently. [day 75](#day-75) removes it.

#### in practice

how many threads? `std::thread::hardware_concurrency()` is a hint, and it may return 0 when the value is not computable. creating a thread is a system call plus a stack (commonly megabytes of reserved address space; the size is platform-dependent and `std::thread` gives you no portable way to set it). that cost is fine for a dozen long-lived component threads and wrong for one thread per incoming request, which is why thread pools exist ([day 87](#day-87)).

#### watch out for

**an exception between starting and joining terminates the program.**

```cpp
#include <thread>

void process() {
    std::thread worker(compute);
    prepare_output();     // if this throws, ~thread runs on a joinable thread: std::terminate
    worker.join();
}
```

the `join` is skipped by the exception, the destructor finds a joinable thread, and the process ends with no stack unwinding report from your code. this is the same "cleanup on every exit path" problem that [day 16](#day-16) solved for files, and the same solution applies: a guard that joins in its destructor, which is exactly what `std::jthread` is.

#### the takeaway

a `std::thread` must be joined (or, rarely, detached) before it is destroyed, its arguments are copied into the new thread, and anything it references must outlive it; let an RAII owner do the joining.

#### optional challenge

what is wrong with this function, and what are two ways to fix it?

```cpp
void start_logging(const std::vector<Sample>& samples) {
    std::vector<Sample> buffer = samples;
    std::thread t([&] { write_all(buffer); });
    t.detach();
}
```

<details>
<summary>answer</summary>

the lambda captures `buffer` by reference, and `buffer` is destroyed when `start_logging` returns, almost certainly while the detached thread is still writing: undefined behavior. one fix moves the data into the closure, `std::thread t([buf = std::move(buffer)] { write_all(buf); });`, so the thread owns what it uses (and then ask whether detaching is still right at shutdown). the other keeps ownership with the caller: return the thread, or a `std::jthread`, so someone joins it before the data goes away.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-75"></a>

### day 75: `std::jthread` and cooperative cancellation

**module 12:** threads and synchronization · **reading time:** about 7 minutes · **standard:** C++20  
**objective:** own threads with `std::jthread`, stop them cooperatively with stop tokens, and wake blocked work with stop_callback  
**builds on:** [day 74](#day-74) (`std::thread`: starting, joining, and passing arguments)

#### the idea

every class that owns a `std::thread` ends up with the same hand-written destructor: set a flag, wake the thread if it is waiting, join it. every author gets one detail slightly wrong, and the failure is a hang or a `std::terminate` at shutdown, the least tested path in most programs. C++20's `std::jthread` makes "stop, then join" the default behavior of the thread object itself, and adds a standard vocabulary for asking a thread to stop.

#### understanding the concept

C++20 `std::jthread` fixes the ownership story. its destructor does `if (joinable()) { request_stop(); join(); }`, which is RAII applied to threads ([day 16](#day-16)). it also owns a `std::stop_source`; if the callable's first parameter is a `std::stop_token`, the jthread passes it one. the three stop types:

| type | role |
|---|---|
| `std::stop_source` | the "remote control": `request_stop()` (returns `true` only for the call that made the request) |
| `std::stop_token` | a read-only view: `stop_requested()`, cheap to copy and pass down |
| `std::stop_callback` | registers a callable that runs when stop is requested |

cancellation is cooperative. nothing interrupts the thread; the thread has to look at the token.

#### in code

```cpp complete
#include <chrono>
#include <stop_token>
#include <thread>

class ImuPoller {
public:
    ImuPoller() : worker_([this](std::stop_token st) { run(st); }) {}
    // no destructor: ~jthread requests stop, then joins

private:
    void run(std::stop_token st) {
        while (!st.stop_requested()) {
            poll_once();
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }
    void poll_once() { /* read registers, publish a sample */ }

    // Other members (buffers, config) go above this line.
    std::jthread worker_;   // declared last: constructed last, destroyed first
};
```

the comment on `worker_` is the important design rule. destruction runs in reverse declaration order, so the thread is stopped and joined before any member it uses is destroyed. if the jthread is declared first, it is destroyed last, and the thread can briefly run against members that are already gone.

third, `std::stop_callback` lets a stop request reach into code that is blocked and not looking at the token:

```cpp complete
#include <optional>
#include <stop_token>

struct Frame { /* payload */ };
struct SerialPort {                  // driver API
    std::optional<Frame> read();     // blocks until a frame arrives or cancel() is called
    void cancel();                   // documented as safe to call from any thread
};
void handle(const Frame&);

void reader(std::stop_token st, SerialPort& port) {
    // Runs inside request_stop() on the requesting thread,
    // or immediately here if stop was already requested.
    std::stop_callback on_stop(st, [&port] { port.cancel(); });  // makes read() return early
    while (!st.stop_requested()) {
        if (auto frame = port.read())        // blocks until data or cancel()
            handle(*frame);
    }
}   // ~stop_callback deregisters; if the callback is running on another thread, it waits
```

the callback runs on whichever thread requests the stop, which is why `cancel()`'s thread-safety is part of the driver's contract. started as `std::jthread t(reader, std::ref(port));`, the jthread's destructor triggers the callback.

#### in practice

in a robot stack, each driver component (lidar, IMU, motor bus) typically owns one thread. making that thread a `std::jthread` member declared last gives you a component whose destructor is correct by construction, and whose shutdown order follows ownership: destroying the component tree in reverse order stops threads from the leaves up.

for process-wide shutdown (SIGTERM from systemd, say), keep one `std::stop_source` in `main`, and give each component a `std::stop_token` from it as a constructor argument. be aware that a jthread's own stop source is separate. the jthread injects its token only when the callable accepts one as an extra first argument; a lambda taking a single `std::stop_token`, started as `std::jthread t(f, process_token)`, receives *your* token, and `~jthread`'s `request_stop()` then reaches nobody. a `stop_callback` on the process token that calls `worker_.request_stop()` bridges the two cleanly.

#### watch out for

cooperative cancellation is only as responsive as the checks. in the jthread example, `sleep_for` does not observe the token, so destruction can block for up to one period. with 10 ms that is harmless. with a blocking `read()` that waits for a sensor that has been unplugged, the destructor hangs forever, and a hung destructor is worse than a crash because nothing reports it. every blocking call inside a stoppable thread needs a way to be woken: a `stop_callback`, a timeout, or a stop-token-aware wait such as `std::condition_variable_any::wait` with a token ([day 78](#day-78)).

#### the takeaway

own every thread with RAII: `std::jthread`, declared after everything it touches, with a `stop_token` checked at every point where the thread can block. treat `detach` as a code smell that needs a written justification.

#### optional challenge

```cpp complete
#include <iostream>
#include <thread>

int main() {
    int value = 0;
    {
        std::jthread t([&value] { value = 42; });
    }
    std::cout << value << '\n';
}
```

<details>
<summary>answer</summary>

it prints `42`, guaranteed. the inner scope ends, `~jthread` calls `request_stop()` (ignored, since the lambda takes no token) and then `join()`. the thread's completion synchronizes with the return of `join()`, so the write to `value` happens before the read in `main`. there is no data race. replace `std::jthread` with `std::thread` and the program calls `std::terminate` at the closing brace instead, because the thread is still joinable.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-76"></a>

### day 76: data races and race conditions

**module 12:** threads and synchronization · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** define a data race precisely, explain why it is undefined behavior rather than an imprecise result, and tell it apart from a race condition  
**builds on:** [day 74](#day-74) (`std::thread`: starting, joining, and passing arguments), [day 13](#day-13) (undefined behavior and the optimizer)

#### the idea

two radar worker threads each count processed frames into a shared `long`, a million frames each. on one machine with GCC 12, an `-O0` build printed totals between 1.0 and 1.5 million, different on every run. the `-O2` build printed exactly 2,000,000 every time. a colleague concludes the release build is fine and the debug build is "just losing a few counts." both conclusions are wrong. the program has a data race, and a data race is undefined behavior, not an imprecise number. the release build only looks right because the optimizer, assuming no race, collapsed each thread's loop into a single addition.

#### understanding the concept

the standard's definition is precise, and worth knowing word for word in spirit:

- two expression evaluations **conflict** if they access the same memory location and at least one of them modifies it. (a memory location is a scalar object or a run of adjacent non-zero-width bit-fields; two different `char` members are different locations, which is why threads may safely write neighbouring struct members.)
- a program has a **data race** if it contains two potentially concurrent conflicting actions, at least one of which is not atomic, and neither happens before the other.
- any data race is **UB** ([day 13](#day-13)).

why UB rather than "some interleaving of the two"? because the compiler is allowed to optimize single-threaded code as if no other thread could be watching. it may keep a variable in a register for a whole loop, merge or split stores, or hoist a load out of a loop entirely, which turns `while (!done) {}` into an infinite loop. on some targets a 64-bit store is two instructions, and a reader can see half of each value. `++count` is a read-modify-write: three steps, and even when it compiles to a single x86 instruction, it is not atomic without a `lock` prefix.

a **race condition** is different: a bug where the result depends on timing. you can have one with no data race at all, when every access is properly locked but the *sequence* of operations is not. locking each step separately does not make the sequence atomic.

#### in code

the counter, broken and fixed:

```cpp ub
#include <mutex>
#include <thread>

long frames = 0;
void count_frames_racy() {
    for (int i = 0; i < 1'000'000; ++i) ++frames;   // BUG: data race, UB
}

std::mutex frames_mutex;
long frames_safe = 0;
void count_frames() {
    for (int i = 0; i < 1'000'000; ++i) {
        std::lock_guard lock(frames_mutex);          // CTAD: lock_guard<std::mutex>
        ++frames_safe;
    }
}

int main() {
    std::thread a(count_frames), b(count_frames);
    a.join();
    b.join();
    // frames_safe == 2'000'000, guaranteed
}
```

locking per increment is correct but makes the threads take turns on every iteration. better designs avoid sharing: count locally and add once at the end, or use an atomic counter ([day 83](#day-83)). correct first, then reduce sharing.

#### in practice

races hide from ordinary testing: they depend on timing, compiler, and hardware, and the code usually works. ThreadSanitizer finds them by instrumenting every memory access and tracking happens-before relationships at run time:

```sh
g++ -std=c++17 -O1 -g -fsanitize=thread tests.cpp -o tests_tsan && ./tests_tsan
# WARNING: ThreadSanitizer: data race ... Write of size 8 ... Previous write of size 8 ...
```

it reports the two conflicting accesses with stack traces, even when the run happened to produce the right answer. it needs its own build (it cannot be combined with AddressSanitizer), slows the program down considerably, and only sees the interleavings your tests actually execute. a CI job that runs the concurrent tests under TSan is the cheapest insurance against this whole class of bug.

#### watch out for

**no data race, and still wrong.**

now a race condition with no data race. every method locks, and the code is still wrong:

```cpp ub
#include <map>
#include <mutex>

struct Track { double range_m; double velocity_mps; };

class TrackTable {
public:
    bool contains(int id) const {
        std::lock_guard lock(m_);
        return tracks_.count(id) != 0;
    }
    void insert(int id, Track t) {
        std::lock_guard lock(m_);
        tracks_[id] = t;
    }
    // Fix: make the operation callers need a single critical section.
    bool insert_if_absent(int id, Track t) {
        std::lock_guard lock(m_);
        return tracks_.try_emplace(id, t).second;
    }
private:
    mutable std::mutex m_;              // mutable: const readers must lock too
    std::map<int, Track> tracks_;
};

// BUG (race condition, not UB): another thread may insert between the two calls
// if (!table.contains(id)) table.insert(id, initial_track);
```

the lesson is about API design: the critical section is part of the interface. a thread-safe class must offer the *transactions* its callers need, not just thread-safe getters and setters.

#### the takeaway

a data race is undefined behavior, not an imprecise result, and the optimizer is entitled to assume you never wrote one; race conditions are a separate, higher-level bug that locking each step does not fix.

#### optional challenge

which of these are data races (assume no other synchronization)?

1. two threads write two different `char` members of the same struct object.
2. two threads read the same `int`.
3. one thread sets `bool done = true;` while another loops on `while (!done) {}`.
4. two threads call `++` on the same `std::atomic<int>`.
5. two threads write two adjacent bit-fields, `unsigned a : 4;` and `unsigned b : 4;`, of the same struct.

<details>
<summary>answer</summary>

3 and 5. distinct `char` members are distinct memory locations (1), and concurrent reads never conflict (2). (3) is the classic: a non-atomic write and read with no happens-before, so the compiler may hoist the load out of the loop and spin forever. atomic operations never race with each other (4). adjacent non-zero-width bit-fields form *one* memory location (5), so writing different fields is a conflicting access; a zero-width bit-field (`unsigned : 0;`) between them would separate the locations.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-77"></a>

### day 77: mutexes, locks, and thread-safe classes

**module 12:** threads and synchronization · **reading time:** about 6 minutes · **standard:** C++17  
**objective:** protect shared data with RAII locks, design thread-safe classes whose methods are complete transactions, and never let guarded data escape the lock  
**builds on:** [day 76](#day-76) (data races and race conditions)

#### the idea

"this vector is protected by that mutex" is usually a comment, and comments are not checked. nothing stops a new method from touching the vector without the lock, or an existing method from handing out a reference that is read after the lock is gone. the mechanics of locking are easy; the hard part is designing a class so that the lock and the data it guards cannot be separated.

#### understanding the concept

a mutex fixes data races by creating happens-before edges. each `unlock()` of a mutex synchronizes with the next `lock()` of the same mutex, so everything a thread wrote inside its critical section is visible to the next thread that takes the lock. you never call `lock()`/`unlock()` by hand; you use an RAII lock ([day 16](#day-16)) so exceptions and early returns cannot leave it held.

| lock type | when to use |
|---|---|
| `std::lock_guard` | one mutex, locked for the whole scope; the default |
| `std::scoped_lock` (C++17) | one *or several* mutexes; locks several without deadlock ([day 86](#day-86)) |
| `std::unique_lock` | needs to unlock early, defer, try, time out, or be moved; required by `std::condition_variable` ([day 78](#day-78)) |
| `std::shared_lock` + `std::shared_mutex` (C++17) | many readers or one writer |

a mutex protects *data*, not code. the useful question for every member of a thread-safe class is "which mutex guards this?", and the useful design keeps that answer structural: the mutex and its data are private members of the same small class, and every public method takes the lock for the whole of one logical operation.

#### in code

finally, encapsulate the mutex with the data it protects, so it is impossible to touch the data without the lock:

```cpp complete
#include <mutex>
#include <utility>

template <typename T>
class Synchronized {
public:
    explicit Synchronized(T value) : value_(std::move(value)) {}

    template <typename F>
    auto with_lock(F&& f) {                 // 'auto' returns by value:
        std::lock_guard lock(m_);           // a reference returned by f is copied,
        return std::forward<F>(f)(value_);  // not leaked past the lock
    }
private:
    std::mutex m_;
    T value_;
};

// Synchronized<std::vector<Detection>> pending{{}};
// pending.with_lock([&](auto& v) { v.push_back(d); });
// auto n = pending.with_lock([](auto& v) { return v.size(); });
```

`with_lock` deliberately returns `auto`, not `decltype(auto)`: a lambda that returns `auto&` gets a copy, so a reference to the guarded data cannot escape by accident. a determined caller can still smuggle out a pointer; the wrapper prevents mistakes, not malice.

#### in practice

a motion controller reads a calibration table at 1 kHz from several control threads; an operator tool updates it a few times per hour. this looks like the textbook case for `std::shared_mutex`, and it might be, but measure before assuming. a shared lock is not free: every reader still writes to the mutex's internal state, so the cache line holding it moves between cores on every acquisition, and if critical sections are short, that traffic can cost as much as the exclusive lock you were avoiding. the standard also says nothing about fairness between readers and writers, so writer starvation depends on the implementation.

an alternative worth knowing is the immutable snapshot: keep a `std::shared_ptr<const CalibrationTable>`, and have readers lock a mutex only long enough to copy the pointer. the writer builds a new table outside any lock and swaps the pointer under the mutex. readers then use their snapshot with no lock held, and an old table lives until its last reader drops it ([day 27](#day-27)). sharing immutable data is the cheapest kind of sharing to reason about.

whatever you choose, keep critical sections small: no I/O, no logging, no allocation-heavy formatting, and no calls into unknown code while holding a lock. copy what you need out, unlock, then do the slow work.

#### watch out for

returning references, pointers, iterators, or `string_view`s into guarded data. the lock protects the data only while it is held:

```cpp
const Track& find(int id) const {
    std::lock_guard lock(m_);
    return tracks_.at(id);   // BUG: the caller reads it after the lock is released
}
```

the caller's read races with any writer, and if another thread erases the entry, the reference dangles. return by value (`std::optional<Track>`), or pass a callable in, as `with_lock` does. tools help but do not replace design: ThreadSanitizer (`-fsanitize=thread` with GCC or Clang on Linux and macOS) reports races that occur on paths your tests actually execute, and silence means only that.

#### the takeaway

a data race is UB, not an imprecise result. bundle each mutex with the data it guards, make each method one complete transaction, and never let a reference to guarded data outlive the lock.

#### optional challenge

this compiles. what does it actually protect?

```cpp
void TrackTable::clear() {
    std::unique_lock<std::mutex>(m_);
    tracks_.clear();
}
```

<details>
<summary>answer</summary>

nothing. `std::unique_lock<std::mutex>(m_);` is parsed as a *declaration* (the same rule behind the most vexing parse, [day 03](#day-03)): a new local variable named `m_`, of type `std::unique_lock<std::mutex>`, default-constructed, owning no mutex. it shadows the member, and `tracks_.clear()` runs unlocked. with `std::lock_guard` the same mistake fails to compile, because `lock_guard` has no default constructor, which is one more reason to prefer it. always name your locks: `std::unique_lock lock(m_);`. GCC 12 with `-Wall` does warn here ("unnecessary parentheses in declaration of 'm_'"), and `-Wshadow` reports the shadowing, which is a good argument for treating warnings as errors.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-78"></a>

### day 78: condition variables: sleeping until state changes

**module 12:** threads and synchronization · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** wait for shared state with a condition variable, using a predicate and the same mutex, and avoid lost and spurious wakeups  
**builds on:** [day 77](#day-77) (mutexes, locks, and thread-safe classes), [day 75](#day-75) (`std::jthread` and cooperative cancellation)

#### the idea

a detection stage hands work to a tracker thread through a mutex-protected `std::deque`. the first version of the tracker loops on `if (q.empty()) continue;`, which burns a core doing nothing. the second sleeps 1 ms between checks, which adds up to a millisecond of latency to every frame and still wakes a thousand times a second. what you actually want is "sleep until there is something to do", and that is what a condition variable provides.

#### understanding the concept

a `std::condition_variable` is a wait queue tied to a mutex. `cv.wait(lock)` does two things atomically: it releases the mutex and puts the thread to sleep. when woken, it reacquires the mutex before returning. that atomicity is the whole point: there is no window between "I checked the condition" and "I am asleep" in which another thread can change the condition and notify.

two rules make it correct.

**always wait with a predicate.** waits may return without any notification (a *spurious wakeup*, explicitly allowed by the standard), and even a real notification may arrive after another thread has already consumed what you were woken for. so the condition is re-checked under the lock every time. the overload `cv.wait(lock, pred)` is exactly `while (!pred()) cv.wait(lock);`.

**modify the predicate's state while holding the same mutex.** a notification has no memory: if nobody is waiting, `notify_one()` does nothing. if the producer changes the state without the mutex, it can do so after the consumer evaluated the predicate (false) but before the consumer went to sleep. the notify finds nobody waiting, and the consumer sleeps forever. this is the *lost wakeup*, and making the flag `std::atomic` does not fix it: it removes the data race, not the window.

`std::condition_variable` works only with `std::unique_lock<std::mutex>`, because `wait` must unlock and relock it. `std::condition_variable_any` works with any lockable type, at some cost in overhead, and in C++20 it gained stop-token-aware waits.

notifying while holding the lock or right after releasing it are both correct, provided the state change happened under the lock. notifying after unlocking can avoid waking a thread that immediately blocks on the mutex you still hold (some implementations mitigate this anyway). notifying under the lock is the safer choice when a woken waiter might destroy the condition variable itself, for example by returning and ending the lifetime of the object that contains it; a notify on a destroyed condition variable is UB.

#### in code

the lost wakeup, labelled:

```cpp complete
#include <atomic>
#include <condition_variable>
#include <mutex>

std::mutex m;
std::condition_variable cv;
std::atomic<bool> ready{false};

void producer_buggy() {
    ready = true;            // BUG: not under m; the consumer may be between
    cv.notify_one();         // its predicate check and its sleep: wakeup lost
}

void producer() {
    {
        std::lock_guard lock(m);
        ready = true;        // a plain bool would now be enough
    }
    cv.notify_one();
}

void consumer() {
    std::unique_lock lock(m);
    cv.wait(lock, [] { return ready.load(); });
    // ready is true here, and m is held again
}
```

#### in practice

not every stage should block the producer. for a planner that only cares about the newest camera frame, a single overwrite slot is the right policy. this one needs C++20 for the stop-token wait:

```cpp
// C++20: condition_variable_any::wait(lock, stop_token, pred)
#include <condition_variable>
#include <mutex>
#include <optional>
#include <stop_token>
#include <utility>

template <typename T>
class LatestSlot {                     // producer never blocks; stale values are dropped
public:
    void publish(T v) {
        { std::lock_guard lock(m_); value_ = std::move(v); }
        cv_.notify_one();
    }
    std::optional<T> wait_next(std::stop_token st) {
        std::unique_lock lock(m_);
        if (!cv_.wait(lock, st, [&] { return value_.has_value(); }))
            return std::nullopt;       // woken by a stop request, nothing to return
        return std::exchange(value_, std::nullopt);
    }
private:
    std::mutex m_;
    std::condition_variable_any cv_;
    std::optional<T> value_;
};
```

the token overload registers a stop callback that wakes the waiter, then returns the final value of the predicate. inside a `std::jthread` ([day 75](#day-75)), this makes the blocking wait respond to the jthread's destructor without any extra close flag.

#### watch out for

**waiting with `if` instead of a predicate.**

```cpp
std::unique_lock lock(m);
if (!ready) cv.wait(lock);   // BUG: a spurious wakeup returns with ready still false
use_result();
```

the standard allows `wait` to return without any notification, and a real notification may be consumed by another waiter first. code that checks the condition once and then trusts the wakeup works in testing and fails rarely in production. the predicate overload, `cv.wait(lock, [&] { return ready; })`, loops for you, and there is no good reason to call the bare `wait` in new code.

#### the takeaway

a condition variable is not a signal; it is a way to sleep until shared state changes. change that state under the mutex, and always wait with a predicate.

#### optional challenge

`cv.wait(lock)` takes the lock as an argument and releases it internally. what would go wrong if the API instead asked you to unlock the mutex yourself and then call a `wait()` that only sleeps?

<details>
<summary>answer</summary>

there would be a window between your `unlock()` and the start of the sleep. a producer could take the mutex in that window, change the state, and notify, and the notification would find nobody waiting yet. the consumer would then go to sleep after the event it was waiting for: the lost wakeup, built into the API. `wait` releases the mutex and blocks as one atomic step with respect to notifications, which is the entire reason it needs the lock.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-79"></a>

### day 79: a bounded producer-consumer queue

**module 12:** threads and synchronization · **reading time:** about 6 minutes · **standard:** C++17  
**objective:** build a bounded blocking queue with clean shutdown, and choose a back-pressure policy deliberately  
**builds on:** [day 78](#day-78) (condition variables: sleeping until state changes), [day 51](#day-51) (`std::optional`: modeling "maybe")

#### the idea

every pipeline whose stages run at different speeds needs a buffer between them, and the interesting part of that buffer is not where items go but what happens when it fills up. block the producer, drop the oldest item, drop the newest, or grow without limit: each is a decision about latency, memory, and data loss, and an unbounded queue is the one that makes the decision silently and fails in the field.

#### understanding the concept

a bounded blocking queue has a small, complete contract: `push` waits while the queue is full, `pop` waits while it is empty, and `close` ends the conversation, waking every waiter so that producers stop and consumers drain what is left. two conditions are waited on ("not full" and "not empty"), so the queue uses two condition variables over one mutex. the class is the unit of synchronization: the mutex, both condition variables, and the state they guard are private, and every public operation is one complete transaction.

#### in code

the queue: a bounded blocking queue with shutdown. `push` blocks when full, `pop` blocks when empty, and `close` wakes everyone:

```cpp complete
#include <condition_variable>
#include <cstddef>
#include <deque>
#include <mutex>
#include <optional>

template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {}  // capacity > 0

    bool push(T item) {                                  // false if closed
        std::unique_lock lock(m_);
        not_full_.wait(lock, [&] { return closed_ || q_.size() < capacity_; });
        if (closed_) return false;
        q_.push_back(std::move(item));
        lock.unlock();
        not_empty_.notify_one();
        return true;
    }

    std::optional<T> pop() {                             // nullopt: closed and drained
        std::unique_lock lock(m_);
        not_empty_.wait(lock, [&] { return closed_ || !q_.empty(); });
        if (q_.empty()) return std::nullopt;
        std::optional<T> item(std::move(q_.front()));
        q_.pop_front();
        lock.unlock();
        not_full_.notify_one();
        return item;
    }

    void close() {
        { std::lock_guard lock(m_); closed_ = true; }
        not_full_.notify_all();                          // every waiter must re-check
        not_empty_.notify_all();
    }

private:
    std::mutex m_;
    std::condition_variable not_full_, not_empty_;
    std::deque<T> q_;
    std::size_t capacity_;
    bool closed_ = false;
};
```

a consumer is just `while (auto d = queue.pop()) track(*d);`, and it exits cleanly after `close()` once the queue is drained. returning `std::optional` ([day 51](#day-51)) makes "no more items" part of the type instead of a sentinel. notice that the class is the unit of synchronization: the mutex, both condition variables, and the state they guard are private, and every public operation is one complete transaction ([day 77](#day-77)).

#### in practice

back-pressure is a design decision, and the queue is where you make it explicit. in a radar chain, every detection matters for the tracker, so a bounded queue that blocks the detector is reasonable: when the tracker falls behind, the slowdown propagates upstream, and memory stays bounded. for a camera feeding a planner, a frame that is 200 ms old is worse than no frame, so drop-oldest (the `LatestSlot` above, or a ring buffer that overwrites) is the right policy. telemetry export sits in between: bounded, drop newest, and count what you dropped.

what you should almost never ship is an *unbounded* queue between stages with different throughput. it does not remove overload, it hides it until the process runs out of memory, usually in the field. whatever policy you pick, export the queue depth and drop counts as metrics: they are the first thing you will want when the pipeline misbehaves.

#### watch out for

producers and consumers sharing one condition variable. if both "not full" and "not empty" waiters sleep on the same `cv`, a `notify_one()` intended for a consumer can wake a producer instead. that producer re-checks its predicate, finds it still false, and goes back to sleep; the notification is used up, and the consumer that should have run keeps sleeping. the program can stall with items in the queue. the fix is either one condition variable per condition (as in `BoundedQueue`) or `notify_all()` on a shared one, which is correct but wakes everyone. the same reasoning is why `close()` uses `notify_all()`: every waiter must observe `closed_`.

#### the takeaway

decide deliberately what happens when the producer is faster than the consumer, make that policy explicit in the queue's type, and measure its depth and drops in production.

#### optional challenge

after the wait in `pop()`, why does the code test `q_.empty()` rather than `closed_`? what would change if it returned `std::nullopt` whenever `closed_` is true?

<details>
<summary>answer</summary>

testing `q_.empty()` gives drain-on-close semantics: items pushed before `close()` are still delivered, and `pop()` reports the end only when the queue is both closed and empty. if it returned on `closed_`, any items still queued at shutdown would be silently discarded, so a final batch of detections or log records would be lost. sometimes that is what you want (a fast abort), but then it should be a separate, explicitly named operation, not an accident of the predicate.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-80"></a>

### day 80: review: threads and synchronization

**module 12:** threads and synchronization · **reading time:** about 9 minutes · **standard:** C++20  
**objective:** consolidate thread ownership, jthread and stop tokens, data races, mutexes, condition variables, and the bounded queue  
**covers:** [day 74](#day-74) to [day 79](#day-79)

#### recap

| lesson | key idea |
|---|---|
| [day 74](#day-74) | a joinable `std::thread` terminates the program on destruction; arguments are copied in, and references must outlive the thread. |
| [day 75](#day-75) | `std::jthread` stops and joins in its destructor; cancellation is cooperative through stop tokens and callbacks. |
| [day 76](#day-76) | conflicting non-atomic accesses without happens-before are undefined behavior; race conditions are a separate bug. |
| [day 77](#day-77) | bundle each mutex with its data, make each method one transaction, and never let guarded data escape the lock. |
| [day 78](#day-78) | sleep until shared state changes: modify it under the mutex, and always wait with a predicate. |
| [day 79](#day-79) | a bounded queue with `close()` makes back-pressure and shutdown explicit. |

#### review questions

1. a `Poller` class declares `std::jthread worker_;` first and `std::vector<float> buffer_;` second, and the thread function writes into `buffer_`. every member is RAII. what can go wrong when a `Poller` is destroyed?
2. a `TrackTable` offers a locked `contains(id)` and a locked `insert(id, track)`, and callers write `if (!t.contains(id)) t.insert(id, track);`. is there a data race? is the code correct?
3. the producer never touches the mutex. is there a data race? can the consumer hang?

   ```cpp
   std::atomic<bool> ready{false};
   std::mutex m;
   std::condition_variable cv;

   void producer() { ready = true; cv.notify_one(); }
   void consumer() {
       std::unique_lock lock(m);
       cv.wait(lock, [] { return ready.load(); });
   }
   ```
4. from [day 65](#day-65): what is wrong here, and what are two fixes?

   ```cpp
   void start_fft(std::jthread& worker) {
       std::vector<float> samples = read_frame();
       worker = std::jthread([s = std::span<const float>(samples)] { fft(s); });
   }
   ```

5. from [day 27](#day-27): threads `A` and `B` each hold their own copy of a `std::shared_ptr<const Config>` and reset it at the same time. threads `C` and `D` share one global `std::shared_ptr<const Config> g_config`; `C` assigns a new config to it while `D` copies it. which pair is safe?

#### mini exercise

this class hands the latest reading from a sensor thread to a consumer. find two bugs, then fix them.

```cpp complete
#include <condition_variable>
#include <mutex>

class LatestReading {
public:
    void publish(double v) { value_ = v; ready_ = true; cv_.notify_one(); }
    double wait() {
        std::unique_lock lock(m_);
        cv_.wait(lock, [&] { return ready_; });
        ready_ = false;
        return value_;
    }
private:
    std::mutex m_;
    std::condition_variable cv_;
    double value_ = 0.0;
    bool ready_ = false;
};
```

#### answers

<details>
<summary>answer 1: member order and jthread</summary>

members are destroyed in reverse declaration order, so `buffer_` is destroyed first, while `worker_` is still running. the thread can write into a destroyed vector until `worker_`'s destructor requests stop and joins: UB. declare the `std::jthread` last, after everything it touches ([day 75](#day-75)). the same rule kept [day 86](#day-86)'s `ThreadPool` correct.

</details>

<details>
<summary>answer 2: locked steps are not a transaction</summary>

there is no data race: every access to the table happens under its mutex. the code is still wrong: another thread can insert the same id between `contains` and `insert`, so two threads both see "absent" and one insertion overwrites the other. that is a race condition, and the fix is an API change: a single locked `insert_if_absent` (or `try_emplace`-style) operation that checks and inserts in one critical section.

</details>

<details>
<summary>answer 3: lost wakeup</summary>

no data race, since `ready` is atomic. yes, it can hang. the consumer checks the predicate under `m` and sees `false`. before it blocks, the producer sets `ready` and calls `notify_one()`; nobody is waiting yet, so the notification is lost and the consumer sleeps forever (unless a spurious wakeup rescues it). because the producer never takes `m`, nothing orders its store between the consumer's check and its sleep. fix: `{ std::lock_guard lk(m); ready = true; } cv.notify_one();`. with the store under the mutex, `ready` can be a plain `bool` ([day 78](#day-78)).

</details>

<details>
<summary>answer 4: a span handed to a thread</summary>

`std::span` borrows ([day 65](#day-65)). `samples` is destroyed when `start_fft` returns, while the new thread may still be reading it: a dangling span and UB. a span is only safe to borrow across threads when the owner provably outlives the thread. fixes: move ownership into the thread (`[v = std::move(samples)] { fft(v); }`, with `fft` taking a span so the vector converts), or share immutable data with `std::shared_ptr<const std::vector<float>>` when several threads need it.

</details>

<details>
<summary>answer 5: shared_ptr and threads</summary>

`A` and `B` are safe: the reference count updates are atomic, so separate `shared_ptr` objects that share a control block may be copied and destroyed concurrently ([day 27](#day-27)). `C` and `D` are a data race on the single `g_config` object, UB. copy it under a mutex ([day 77](#day-77)'s snapshot pattern) or use C++20's `std::atomic<std::shared_ptr<const Config>>`. that specialization is not guaranteed to be lock-free, so measure before assuming it beats a mutex. either way, the `Config` itself is safe to read because it is `const`.

</details>

<details>
<summary>mini exercise answer</summary>

`publish` writes `value_` and `ready_` without the mutex while `wait` reads them under it: a data race, which is undefined behavior. and because the state changes outside the mutex, the notification can arrive after the consumer checked the predicate but before it went to sleep: a lost wakeup. the fix makes the state change under the same mutex, then notifies:

```cpp
void publish(double v) {
    {
        std::lock_guard lock(m_);
        value_ = v;
        ready_ = true;
    }
    cv_.notify_one();
}
```

note the policy this class implements: a second `publish` before the consumer wakes overwrites the first value, which is right for "latest reading" and wrong for anything that must not be dropped; for that, use the bounded queue.

</details>

#### connections

this module was about owning threads and protecting what they share. the next one covers the other tools: futures for one-shot results, atomics and the memory model that explains every "synchronizes with" used so far, and the design rules that keep deadlocks out. underneath all of it is the same idea as [day 28](#day-28): decide who owns each piece of state, and the synchronization follows from that decision.

[back to the curriculum map](#curriculum)

---

<a id="module-async"></a>

## module 13: futures, atomics, and concurrency design

one-shot results, atomics and the memory model, deadlocks, and the C++20 coordination primitives.

<a id="day-81"></a>

### day 81: promises and futures: one-shot results across threads

**module 13:** futures, atomics, and concurrency design · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** return a value or an exception from another thread through a promise and future, and know the edge cases of the shared state  
**builds on:** [day 79](#day-79) (a bounded producer-consumer queue), [day 49](#day-49) (exception safety guarantees)

#### the idea

a thread function returns `void`, and an exception that escapes it calls `std::terminate` ([day 74](#day-74)). so how does a worker hand back "here are the surface normals for your point cloud chunk" or "the calibration file was corrupt"? you could build a queue ([day 79](#day-79)) for a single value, plus an error slot, plus a flag. the standard library already has that one-shot channel: a promise on one end, a future on the other.

#### understanding the concept

`std::promise<T>` and `std::future<T>` share a heap-allocated *shared state* holding either a `T` or a `std::exception_ptr`. the promise writes it exactly once with `set_value` or `set_exception`, which makes the state *ready*. the future waits for that with `wait()`, `wait_for()`, or `get()`. making the state ready synchronizes with the return of the call that observes it, so everything the producer wrote before `set_value` is visible after `get()` returns, much like `join`.

the edges are well defined, and worth knowing:

| situation | result |
|---|---|
| `get()` on a ready future holding an exception | the exception is rethrown in the caller |
| `get()` called twice on a `std::future` | UB: `get()` leaves the future invalid (`valid() == false`), and calling `get` or a `wait` function on an invalid future is UB; libstdc++ happens to throw `std::future_error` |
| promise destroyed without setting anything | the future receives a `std::future_error` with `broken_promise` |
| `set_value` called twice | `std::future_error` with `promise_already_satisfied` |

`std::packaged_task<R(Args...)>` wraps a callable together with a promise: invoking the task calls the function and stores the return value or the thrown exception. it separates *what* to run from *where* it runs, which is exactly what a task queue or thread pool needs.

`std::shared_future<T>` lets several consumers wait for the same result; `get()` returns a `const T&` and can be called repeatedly. give each thread its own copy of the `shared_future` object: copies referring to one shared state are safe to use concurrently, while calls on a single object from several threads are not synchronized.

#### in code

a worker that reports either a result or its exception:

```cpp complete
#include <future>
#include <stdexcept>
#include <thread>

struct Calibration { double offset; double gain; };

Calibration run_calibration() { throw std::runtime_error("checksum mismatch"); }

void calibrate(std::promise<Calibration> result) {
    try {
        result.set_value(run_calibration());
    } catch (...) {
        result.set_exception(std::current_exception());  // ships the exception to get()
    }
}

int main() {
    std::promise<Calibration> p;
    std::future<Calibration> f = p.get_future();
    std::thread worker(calibrate, std::move(p));        // the promise is move-only
    try {
        Calibration c = f.get();                        // rethrows runtime_error here
        (void)c;
    } catch (const std::exception& e) {
        // report e.what(): "checksum mismatch"
    }
    worker.join();
}
```

third, `std::packaged_task` separates the callable from the thread that runs it:

```cpp complete
#include <future>
#include <stdexcept>
#include <thread>

int main() {
    std::packaged_task<int(int)> task([](int range_bin) {
        if (range_bin < 0) throw std::out_of_range("negative range bin");
        return range_bin * 2;
    });
    std::future<int> f = task.get_future();
    std::thread t(std::move(task), 21);   // packaged_task is move-only, like the promise
    t.join();
    return f.get() == 42 ? 0 : 1;         // the value, or the exception, is in f
}
```

`packaged_task` is move-only, and `std::function` requires a copyable callable, so a pool built on `std::queue<std::function<void()>>` cannot hold one directly. the usual C++17/20 workaround is to wrap it in a `std::shared_ptr` and capture that; C++23 adds `std::move_only_function` for exactly this reason.

#### in practice

several sensor threads may need the calibration before they start publishing. a `std::shared_future<Calibration>` (from `f.share()`) handed to each of them, by value, lets them all block on `get()` until it is ready, with no extra flags or condition variables.

#### watch out for

**a `std::future` has exactly one `get()`.**

```cpp
std::future<Calibration> f = p.get_future();
Calibration a = f.get();
Calibration b = f.get();   // BUG: f is no longer valid: undefined behavior
```

`get()` moves the result out and leaves the future invalid (`f.valid()` is `false`); libstdc++ happens to throw `std::future_error`, and another library may do anything. when two parts of the program need the same result, convert once with `f.share()` and give each consumer its own copy of the `std::shared_future`.

#### the takeaway

a promise and a future form a one-shot channel that carries either a value or an exception and synchronizes like `join`; one producer sets it once, and one consumer reads it once unless you share it.

#### optional challenge

`calibrate` is changed to return early, without touching the promise, when the calibration file does not exist. what does the caller's `f.get()` do now?

<details>
<summary>answer</summary>

when `calibrate` returns, its by-value `std::promise` parameter is destroyed without having set a value. the destructor stores a `std::future_error` with error code `std::future_errc::broken_promise` in the shared state and makes it ready, so `f.get()` throws that exception. the caller does not hang, which is the point: abandoning a promise is reported, not silently lost. it is still better to call `set_exception` with a meaningful error, because "broken promise" tells the caller nothing about the missing file.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-82"></a>

### day 82: `std::async` and its traps

**module 13:** futures, atomics, and concurrency design · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** use `std::async` for fork-join work with an explicit launch policy, and avoid the default policy and the blocking-destructor trap  
**builds on:** [day 81](#day-81) (promises and futures: one-shot results across threads)

#### the idea

`std::async` looks like the easiest way to run something concurrently: one call, and you get a future for the result. two of its rules are surprising enough to turn that one call into either no concurrency at all or code that silently runs sequentially. both rules exist for good reasons, and once you know them `std::async` is a fine tool for a small number of independent tasks.

#### understanding the concept

`std::async(policy, f, args...)` bundles both: it runs `f` and gives you the future. the policy matters:

- `std::launch::async`: run as if on a new thread.
- `std::launch::deferred`: do nothing now; run `f` on the calling thread the first time someone calls `get()` or `wait()`.
- no policy (`async | deferred`): the implementation chooses. you might get no concurrency at all.

there is one more rule that surprises everyone: the destructor of the last future referring to a shared state created by `std::async` blocks until the task completes. that is deliberate (otherwise the task could outlive everything it references), but it has a sharp edge, shown below.

finally, C++20 still has no continuations: no `.then()`, no `when_all`. those lived in the concurrency TS and were not standardized. if you need composition, you need a library, or a different structure.

#### in code

now fork-join over a point cloud with `std::async`, including the classic bug:

```cpp complete
#include <algorithm>
#include <cstddef>
#include <functional>
#include <future>
#include <vector>

struct Point { float x, y, z; };

double sum_heights(const std::vector<Point>& cloud, std::size_t first, std::size_t last) {
    double sum = 0;
    for (std::size_t i = first; i < last; ++i) sum += cloud[i].z;
    return sum;
}

double mean_height(const std::vector<Point>& cloud, std::size_t parts) {  // parts > 0
    const std::size_t n = cloud.size(), step = (n + parts - 1) / parts;
    std::vector<std::future<double>> futures;
    for (std::size_t first = 0; first < n; first += step) {
        const std::size_t last = std::min(first + step, n);
        // BUG version: std::async(std::launch::async, sum_heights, std::cref(cloud), first, last);
        // The discarded future is destroyed at the end of the statement and waits:
        // every chunk runs to completion before the next starts. Sequential, with thread overhead.
        futures.push_back(std::async(std::launch::async, sum_heights,
                                     std::cref(cloud), first, last));
    }
    double total = 0;
    for (auto& f : futures) total += f.get();  // may rethrow a chunk's exception
    return n ? total / n : 0.0;
}
```

recent libstdc++ marks `std::async` as `[[nodiscard]]`, so GCC warns about the bug version; do not count on every standard library doing so. the blocking destructor also does useful work here. if the first `get()` throws, the remaining futures are destroyed during stack unwinding, and each destructor waits for its task. so no task can still be reading `cloud` after `mean_height` has returned, and the `std::cref` is safe. a detached thread would offer no such guarantee.

#### in practice

at startup, a robot loads its map, its URDF model, and its sensor calibrations. these are independent and I/O-heavy, so launching each with `std::async(std::launch::async, ...)` and calling `get()` on all three is a clean fork-join, with each loader's exceptions arriving at the one place that can decide whether to abort.

futures fit one-shot results. for a *stream* of items, use a queue ([day 79](#day-79)). for many small tasks, use a pool ([day 87](#day-87)) rather than one `std::async` per task, because whether `std::async` reuses threads is up to the implementation and you cannot bound how many it creates.

#### watch out for

the default launch policy. `std::async(f)` may defer `f`, and a deferred task never runs until you call `get()` or `wait()`. this innocent-looking progress loop then never finishes:

```cpp
auto f = std::async(compute_tracks);   // policy: async | deferred, implementation's choice
while (f.wait_for(std::chrono::milliseconds(10)) != std::future_status::ready) {
    report_progress();                 // if deferred, wait_for returns 'deferred' forever
}
```

pass `std::launch::async` explicitly whenever you need concurrency, or handle `std::future_status::deferred` in the loop. treat the default policy as "I don't care whether this runs concurrently", which is rarely what you mean.

#### the takeaway

name the launch policy, keep every `std::async` future alive for as long as the work should run in parallel, and reach for queues or pools when you have more than a handful of tasks.

#### optional challenge

each loader takes about one second. roughly how long does this take, and why?

```cpp
void load_all() {
    std::async(std::launch::async, load_map);
    std::async(std::launch::async, load_model);
    std::async(std::launch::async, load_calibration);
}
```

<details>
<summary>answer</summary>

about three seconds. each returned future is a temporary destroyed at the end of its statement, and the destructor of the last future referring to an `std::async` shared state waits for the task, so each load finishes before the next one starts. keep the futures in named variables (or a container) and call `get()` on each at the end; the three loads then overlap and the function takes about one second, plus whatever the slowest loader adds.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-83"></a>

### day 83: `std::atomic`: indivisible operations

**module 13:** futures, atomics, and concurrency design · **reading time:** about 5 minutes · **standard:** C++17  
**objective:** make single variables race-free with `std::atomic`, use read-modify-write operations and compare-and-swap loops, and recognize when atomics are not enough  
**builds on:** [day 76](#day-76) (data races and race conditions), [day 77](#day-77) (mutexes, locks, and thread-safe classes)

#### the idea

the frame counter from [day 76](#day-76) lost updates because `++frames` is three steps: load, add, store. a mutex fixed it by making the threads take turns. for a single integer, that is a lot of machinery: what you want is for the increment itself to be one indivisible step. `std::atomic` provides exactly that, and only that, which is both why it is fast and why it is so easy to misuse.

#### understanding the concept

`std::atomic<T>` (for trivially copyable `T`) makes each operation on the object indivisible, and concurrent atomic operations on the same object are never a data race. every atomic object has a single *modification order* that all threads agree on, so no increment is ever lost.

read-modify-write operations (`exchange`, `fetch_add`, `compare_exchange_weak/strong`) are atomic as a whole. `compare_exchange` writes the new value only if the current value equals `expected` (compared byte for byte like `memcmp`, not with `operator==`, which matters for `float` and padding); on failure it loads the current value into `expected`. the `weak` form may fail spuriously (even when the values are equal), which is fine in a loop and can be cheaper on LL/SC architectures such as ARM.

atomicity covers *one operation on one object*. a sequence of atomic operations is not atomic as a whole, and an atomic variable says nothing by itself about other, non-atomic memory; how atomics order other memory is the subject of [day 84](#day-84).

#### in code

the counter, a statistic, and a compare-and-swap loop for an operation the library does not provide:

```cpp complete
#include <atomic>
#include <cstdint>

std::atomic<std::uint64_t> frames_dropped{0};
std::atomic<float> peak_power{0.0f};

void on_drop() {
    ++frames_dropped;                 // one atomic read-modify-write: no lost updates
}

void record_power(float p) {
    float cur = peak_power.load();
    while (cur < p && !peak_power.compare_exchange_weak(cur, p)) {
        // failed: cur now holds the latest value; the loop re-checks cur < p
    }
}
```

there is no `fetch_max` in C++20, so the CAS loop is the standard way to build any read-modify-write the library lacks: read the current value, compute the new one, and publish it only if nobody changed the value in between, retrying otherwise.

#### in practice

an atomic counter shared by eight worker threads is correct, and it can still be slow: every increment needs exclusive ownership of the cache line that holds it, so the line bounces between cores. when only the total matters, count in a local variable inside each worker and add it to the shared atomic once per batch or at the end. the same idea scales up: the cheapest synchronization is the one you avoid by not sharing. atomics are the right tool for genuinely shared single values (a stop flag, a sequence number, a statistic read by a monitoring thread), not a faster replacement for every mutex.

#### watch out for

**two atomic operations are not one.**

```cpp
std::atomic<int> active{0};
constexpr int max_active = 4;

bool try_enter() {
    if (active.load() < max_active) {   // BUG: another thread can enter between the load...
        ++active;                       // ...and the increment: five threads get in
        return true;
    }
    return false;
}
```

each operation is atomic and there is no data race, but the check and the increment are separate steps: a race condition, as in [day 76](#day-76). make the decision and the update one read-modify-write with a CAS loop (`while (cur < max_active && !active.compare_exchange_weak(cur, cur + 1))`), or protect the compound state with a mutex.

#### the takeaway

`std::atomic` makes each single operation on one variable indivisible and race-free; anything that spans two operations needs a compare-and-swap loop or a mutex.

#### optional challenge

two threads each run `x = x + 1;` a thousand times on `std::atomic<int> x{0};`. is the program undefined? what values can `x` end with?

<details>
<summary>answer</summary>

it is not undefined: every access is atomic, so there is no data race. but `x = x + 1` is an atomic load followed by a separate atomic store, so two threads can both read the same value and both store the same increment, losing one update. the final value can be anything from 2 up to 2000 (2 is reachable in a pathological interleaving). `++x`, `x += 1`, or `x.fetch_add(1)` is a single read-modify-write and always ends at 2000.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-84"></a>

### day 84: happens-before and memory orders

**module 13:** futures, atomics, and concurrency design · **reading time:** about 7 minutes · **standard:** C++20  
**objective:** explain happens-before and the synchronizes-with edge, publish data correctly with release and acquire, and choose a memory order deliberately  
**builds on:** [day 83](#day-83) (`std::atomic`: indivisible operations)

#### the idea

a radar thread fills a frame buffer and then sets `bool ready = true;`. a processing thread spins on `ready`, then reads the frame. on your x86 workstation it seems to work. it is still UB: `ready` is accessed concurrently and is not atomic, so it is a data race ([day 76](#day-76)); the optimizer may hoist the load out of the spin loop; and even with a correct flag, the question remains whether the *frame data* written before the flag is guaranteed to be visible after it. answering that precisely is what the memory model is for.

#### understanding the concept

`std::atomic<T>` (for trivially copyable `T`) makes each operation on the object indivisible, and concurrent atomic operations on the same object are never a data race. every atomic object also has a single *modification order* that all threads agree on. what atomicity alone does not give you is any promise about *other* memory. compilers reorder independent loads and stores, and so do CPUs (store buffers, out-of-order execution). the memory model defines which reorderings other threads may observe, using three relations:

- **sequenced-before**: program order within one thread.
- **synchronizes-with**: a *release* store to an atomic synchronizes with an *acquire* load of the same atomic that reads the value written by that store (or by a later read-modify-write in its release sequence).
- **happens-before**: built from the two above, transitively. if a write happens before a read of the same location, with no other write in between, the read sees that write. if two conflicting accesses, one non-atomic, are not ordered by happens-before, you have a data race.

mutex unlock/lock, thread start and `join`, and future readiness, which the previous lessons relied on, are all defined in terms of this relation. atomics let you build the edges yourself, choosing a `std::memory_order` per operation:

| order | what it guarantees | typical use |
|---|---|---|
| `seq_cst` (default) | acquire/release, plus one total order of all `seq_cst` operations that every thread agrees on | the default; anything you have not proven needs less |
| `release` (stores) / `acquire` (loads) / `acq_rel` (read-modify-writes) | the synchronizes-with edge: writes before the release are visible after the acquire that reads it | publishing data through a flag or pointer |
| `relaxed` | atomicity and the per-object modification order, nothing else | counters and statistics that publish nothing |
| `consume` | intended as a cheaper acquire for dependent loads | do not use: its specification is under revision, and compilers implement it as `acquire` |

#### in code

message passing, the pattern behind almost every correct use of acquire/release:

```cpp complete
#include <array>
#include <atomic>
#include <cassert>
#include <cstdint>

struct Frame { std::array<float, 1024> samples; std::uint64_t seq; };

Frame frame;                          // plain, non-atomic data
std::atomic<bool> ready{false};

void producer() {
    frame.samples.fill(1.0f);
    frame.seq = 42;
    ready.store(true, std::memory_order_release);        // (1) publish
}

void consumer() {
    while (!ready.load(std::memory_order_acquire)) {}    // (2) spin until published
    assert(frame.seq == 42);                             // guaranteed, no data race
}
```

```text
producer                                consumer
frame.samples = ...   | sequenced
frame.seq = 42        | before
ready.store(release) ---synchronizes-with--> ready.load(acquire) reads true
                                             | sequenced before
                                             frame.seq == 42 (happens after the write)
```

weaken either side to `relaxed` and the edge disappears: the reads of `frame` then race with the writes, which is UB, even though `ready` itself is still race-free. using a plain `bool` makes `ready` itself a data race. note the asymmetry: the order protects the *non-atomic* data around the atomic.

relaxed operations build no edges at all, so they are only right for values that publish nothing. the statistics from [day 83](#day-83) are the classic case: `frames_dropped.fetch_add(1, std::memory_order_relaxed)` still never loses an increment, and a monitoring thread that reads the counter sees *some* recent value, because nobody reads other data based on it.

#### in practice

the engineering advice is conservative. use mutexes for compound state, `seq_cst` atomics for single flags and counters, and weaken orders only with a written justification and a benchmark showing it matters. lock-free does not mean faster: a contended atomic still bounces a cache line between cores, CAS loops can retry under contention, and a lock-free design's correctness argument is much harder to review. what lock-freedom does guarantee is progress (some thread always makes progress, no thread can block others by being descheduled while holding a lock), and that is the property to want it for, for example in a real-time thread that must never block on a lower-priority one.

#### watch out for

mixing up "atomic" and "ordered". a `relaxed` flag is perfectly atomic and still publishes nothing: code that sets data, then `ready.store(true, std::memory_order_relaxed)`, then reads the data on the other side has a data race on the data. it may pass every test on x86, whose hardware ordering is strong enough to hide many such bugs, and then fail on ARM, or after a compiler upgrade reorders the stores. the memory model is a contract with the compiler and every CPU you will ever ship on, not a description of your test machine.

#### the takeaway

atomicity makes a single variable race-free; memory orders decide what *other* memory becomes visible. release/acquire pairs build happens-before edges, `relaxed` builds none, and `seq_cst` is the right default until a measurement says otherwise.

#### optional challenge

`x` and `y` are `std::atomic<int>` initialized to 0. thread `A` runs `x.store(1, release); r1 = y.load(acquire);` and thread `B` runs `y.store(1, release); r2 = x.load(acquire);`. after both finish, can `r1 == 0 && r2 == 0`? what if every operation is `seq_cst`?

<details>
<summary>answer</summary>

with release/acquire, yes. each acquire load synchronizes only with a release store *whose value it reads*; if both loads read 0, no synchronizes-with edge exists and nothing forbids the outcome. real hardware produces it: a store can sit in the core's store buffer while the subsequent load of a different address executes. with `seq_cst` on all four operations, no: there is a single total order of the four operations consistent with each thread's program order, so whichever store comes first in that order precedes the other thread's load, which must then read 1. this "store buffering" pattern (as in Dekker's mutual exclusion algorithm) is the classic case where `seq_cst` is required and acquire/release is not enough.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-85"></a>

### day 85: atomic waits, false sharing, and lock-freedom

**module 13:** futures, atomics, and concurrency design · **reading time:** about 5 minutes · **standard:** C++20  
**objective:** block on an atomic value with C++20 wait and notify, avoid false sharing between hot atomics, and check whether an atomic is really lock-free  
**builds on:** [day 84](#day-84) (happens-before and memory orders)

#### the idea

a consumer that spins on an atomic flag burns a core while it waits. two workers that each update their own counter, with no shared data at all, still slow each other down. and an `std::atomic` of a struct may quietly contain a lock. atomics are a low-level tool, and using them well means knowing how they interact with the operating system's scheduler and the CPU's caches, not just with the memory model.

#### understanding the concept

not every atomic is lock-free. `std::atomic<T>::is_always_lock_free` (C++17, `constexpr`) and `is_lock_free()` tell you; a large `T` may be implemented with a hidden lock. the standard guarantees lock-freedom only for `std::atomic_flag` (and, in C++20, the `std::atomic_signed_lock_free` and `std::atomic_unsigned_lock_free` aliases). C++20 adds `wait`/`notify_one`/`notify_all` on atomics (block until the value changes, without a condition variable) and `std::atomic_ref<T>`, which applies atomic operations to an ordinary object; while any `atomic_ref` to an object exists, every access to it must go through an `atomic_ref`.

#### in code

third, C++20 replaces the spin with a blocking wait, and keeps hot atomics on separate cache lines:

```cpp complete
#include <atomic>
#include <cstdint>

std::atomic<std::uint32_t> generation{0};

void publish_next() {                    // producer, after writing the new frame
    generation.fetch_add(1, std::memory_order_release);
    generation.notify_all();
}

void await_next(std::uint32_t& seen) {   // consumer
    generation.wait(seen, std::memory_order_acquire);   // blocks while value == seen
    seen = generation.load(std::memory_order_acquire);
}

struct alignas(64) WorkerStats {         // 64: a common cache-line size, not a guarantee
    std::atomic<std::uint64_t> processed{0};
};
WorkerStats stats[8];                    // one per worker: no false sharing between them
```

`wait(old)` returns only after observing a value different from `old`; it may wake spuriously internally, but it re-checks for you. it compares values, so if the counter changed and changed back before the waiter looked, the waiter keeps sleeping (the ABA problem), which is why a monotonically increasing generation counter is used rather than a toggling flag. note that this only signals. if the producer rewrites a single shared frame buffer while a consumer is still reading the previous frame, that is a data race again; pair the signal with double buffering or hand frames over through a queue ([day 79](#day-79)).

#### in practice

the `alignas(64)` matters when several threads each update their own counter at high rates. if two such counters share a cache line, every write by one core invalidates the line in the other core's cache, and two logically independent threads end up contending: *false sharing*. C++17 added `std::hardware_destructive_interference_size` in `<new>` for this, but support varies: GCC provides it from version 12 (64 on x86-64 here) and warns (`-Winterference-size`) when it is used in a header, because the value can change with tuning flags and so becomes an ABI hazard. check `__cpp_lib_hardware_interference_size`, or use a named constant you control. [day 107](#day-107) shows how to measure the effect with hardware counters.

#### watch out for

**an atomic is not necessarily lock-free.**

```cpp complete
#include <atomic>

struct Pose { double x, y, z, qw, qx, qy, qz; };   // 56 bytes
std::atomic<Pose> latest_pose;                      // compiles; very likely uses a lock

static_assert(std::atomic<int>::is_always_lock_free);   // true on mainstream platforms
// static_assert(std::atomic<Pose>::is_always_lock_free);   // fails on typical 64-bit targets
```

`std::atomic<T>` works for any trivially copyable `T`, and for types too large for the hardware's atomic instructions the library falls back to a lock (libstdc++ uses a small table of mutexes and needs `-latomic` for some sizes). that is correct, but it defeats the usual reason for choosing an atomic in a real-time thread. assert `is_always_lock_free` where it matters, and for large data publish a pointer or use double buffering instead.

#### the takeaway

use C++20 `wait`/`notify` instead of spinning, keep atomics that different threads update on separate cache lines, and assert lock-freedom wherever you rely on it.

#### optional challenge

why does `await_next` wait on a generation counter that only ever increases, instead of a `bool` that the producer sets to `true` and the consumer resets to `false`?

<details>
<summary>answer</summary>

`wait(old)` compares values: it sleeps while the atomic still equals `old`. with a toggling flag, two quick publications can change the value and change it back before the waiter looks, so the waiter sees "unchanged" and keeps sleeping through two frames (the ABA problem). a monotonically increasing counter never returns to a previous value in practice, so any publication is visible as a change, and the consumer can also tell how many frames it missed.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-86"></a>

### day 86: deadlocks: breaking the cycle

**module 13:** futures, atomics, and concurrency design · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** recognize the conditions for deadlock, take multiple locks safely, and keep unknown code and blocking waits out of critical sections  
**builds on:** [day 77](#day-77) (mutexes, locks, and thread-safe classes), [day 78](#day-78) (condition variables: sleeping until state changes)

#### the idea

a tracker merges track stores: `merge(a, b)` locks `a`, then `b`. under rare timing, one thread runs `merge(left, right)` while another runs `merge(right, left)`. each holds one mutex and waits forever for the other. nothing crashes and nothing is logged; the robot simply stops publishing tracks after three days in the field. deadlocks are the concurrency bug that hides best in testing, so the defenses have to be structural.

#### understanding the concept

a deadlock needs four conditions at once: mutual exclusion, hold-and-wait (holding one resource while waiting for another), no preemption (nobody can take a lock away), and a circular wait. mutexes give you the first three for free, so practical defenses break the cycle:

- **acquire several locks at once** with `std::scoped_lock(m1, m2)` (C++17). it uses the `std::lock` deadlock-avoidance algorithm, so argument order does not matter.
- **fixed lock ordering** when locks are taken at different times: every code path acquires them in the same global order. a *lock hierarchy* makes this checkable: give each mutex a level and assert, in debug builds, that a thread only acquires locks with a lower level than any it already holds.
- **never call unknown code while holding a lock.** a callback, a virtual function overridden elsewhere, or a user-supplied `std::function` can take other locks (creating a cycle you cannot see) or call back into your object and try to lock the same `std::mutex` again. locking a `std::mutex` the calling thread already owns is UB, and in practice usually a self-deadlock. `std::recursive_mutex` hides the symptom, but the callback then runs while your invariants may be half-updated.

two cousins are worth naming. in a *livelock*, threads keep reacting to each other (both back off with `try_lock`, both retry, forever) without progress. in *starvation*, one thread never gets its turn, for example a writer behind a constant stream of readers on a `std::shared_mutex`, whose fairness the standard does not specify.

#### in code

the merge deadlock and its fix:

```cpp ub
#include <mutex>
#include <vector>

struct Track { int id; double range_m; };
struct TrackStore {
    std::mutex m;
    std::vector<Track> tracks;
};

void merge_buggy(TrackStore& into, TrackStore& from) {
    std::lock_guard a(into.m);
    std::lock_guard b(from.m);     // BUG: merge(x, y) || merge(y, x) can deadlock
    into.tracks.insert(into.tracks.end(), from.tracks.begin(), from.tracks.end());
    from.tracks.clear();
}

void merge(TrackStore& into, TrackStore& from) {
    if (&into == &from) return;               // locking one std::mutex twice would be UB
    std::scoped_lock lock(into.m, from.m);    // both or neither, in any argument order
    into.tracks.insert(into.tracks.end(), from.tracks.begin(), from.tracks.end());
    from.tracks.clear();
}
```

calling out of the lock. the tempting version runs handlers inside the critical section; if a handler calls `subscribe()`, the same thread locks `m_` twice:

```cpp complete
#include <functional>
#include <mutex>
#include <vector>

struct Detection { float range_m; };

class DetectionBus {
public:
    using Handler = std::function<void(const Detection&)>;
    void subscribe(Handler h) {
        std::lock_guard lock(m_);
        handlers_.push_back(std::move(h));
    }
    void publish(const Detection& d) {
        std::vector<Handler> snapshot;
        {
            std::lock_guard lock(m_);
            snapshot = handlers_;              // copy under the lock...
        }
        for (const auto& h : snapshot) h(d);   // ...call unknown code with no lock held
    }
private:
    std::mutex m_;
    std::vector<Handler> handlers_;
};
```

the copy costs allocations per publish; a `std::shared_ptr<const std::vector<Handler>>` snapshot ([day 77](#day-77)) avoids that. [day 95](#day-95) returns to this as the observer pattern, including unsubscription.

#### in practice

the best way to avoid deadlocks is to need fewer locks. three designs do most of the work:

- **confinement**: each piece of mutable state is owned by exactly one thread. a lidar driver's parser state lives on the driver thread and is never shared.
- **message passing**: threads communicate by moving values through queues ([day 79](#day-79)). ownership transfers with the message, so nothing is shared at all.
- **immutable shared data**: configuration and calibration published as `std::shared_ptr<const T>` snapshots can be read by everyone without locks.

locks then remain only inside a few small, well-tested components (queues, snapshot holders), which is where they belong. test those components with stress tests: many iterations, more threads than cores, random small delays injected around the critical sections, and assertions on invariants. in a separate build on Linux or macOS, run them under ThreadSanitizer (`-fsanitize=thread` with GCC or Clang), which reports data races on the paths your tests execute and also lock-order inversions, the deadlock risk above, even in runs that did not actually deadlock.

#### watch out for

**waiting while holding a lock.** a deadlock does not need two mutexes. any blocking wait performed under a lock can close a cycle:

```cpp
void Driver::stop() {
    std::lock_guard lock(m_);
    running_ = false;
    worker_.join();        // BUG: if the worker needs m_ to finish its iteration, both wait forever
}
```

the worker is blocked on `m_`, and the thread holding `m_` is blocked on the worker. the same shape appears with `future::get()`, a condition variable on a different mutex, or a synchronous call into another component. update the shared state under the lock, release it, and only then wait.

#### the takeaway

deadlocks come from cycles, so break the cycle by design: take multiple locks with `std::scoped_lock`, never call unknown code under a lock, and prefer confinement, message passing, and immutable data so that few locks exist at all.

#### optional challenge

in the fixed `merge`, why does the self-merge check matter? without it, what does `merge(store, store)` do?

<details>
<summary>answer</summary>

`std::scoped_lock lock(into.m, from.m)` would be asked to lock the same `std::mutex` twice. the standard leaves the deadlock-avoidance algorithm unspecified; typical implementations lock one mutex and then `try_lock` the others. either way, calling `lock` or `try_lock` on a `std::mutex` the calling thread already owns is UB. in practice the thread may hang, spin forever, or appear to succeed. even if locking worked, the function body would then insert a vector into itself through iterators that the insertion can invalidate. the early return turns an invalid call into a no-op; documenting `into != from` as a precondition (and asserting it) is a reasonable alternative.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-87"></a>

### day 87: latches, barriers, semaphores, and thread pools

**module 13:** futures, atomics, and concurrency design · **reading time:** about 7 minutes · **standard:** C++20  
**objective:** coordinate threads with `std::latch`, `std::barrier`, and `std::counting_semaphore`, and understand what a minimal thread pool does and lacks  
**builds on:** [day 86](#day-86) (deadlocks: breaking the cycle), [day 79](#day-79) (a bounded producer-consumer queue), [day 81](#day-81) (promises and futures: one-shot results across threads)

#### the idea

"wait until every driver has initialized", "let all four simulation threads finish this step before anyone starts the next", "never run more than four uploads at once": these are common coordination needs, and before C++20 each one was a hand-written mix of a mutex, a condition variable, and a counter, with the usual opportunities for lost wakeups. C++20 standardized three small primitives for exactly these shapes, and they compose naturally with the queue you already have into the simplest kind of thread pool.

#### understanding the concept

C++20 also added three coordination primitives that replace many hand-rolled condition variable patterns:

| primitive | semantics | typical use |
|---|---|---|
| `std::latch` | one-shot countdown; `wait()` until it reaches zero | startup: wait until every driver is initialized |
| `std::barrier` | reusable; all participants `arrive_and_wait()` per phase; an optional completion function runs once per phase | lock-step simulation or pipelines |
| `std::counting_semaphore<N>` | a counter of permits; `acquire()` blocks at zero; any thread may `release()` | limit concurrent access to a resource |

#### in code

the C++20 primitives, one use each:

```cpp complete
#include <barrier>
#include <latch>
#include <semaphore>
#include <stop_token>
#include <thread>
#include <vector>

struct Blob;                                   // provided elsewhere:
void init_driver(int);  void run_driver(int, std::stop_token);  void run_until_shutdown();
void swap_buffers() noexcept;  void update_partition(int);  void send(const Blob&);

void start_drivers(int n) {
    std::latch initialized(n);                 // declared before the threads that use it
    std::vector<std::jthread> drivers;
    for (int i = 0; i < n; ++i)
        drivers.emplace_back([&initialized, i](std::stop_token st) {
            init_driver(i);
            initialized.count_down();
            run_driver(i, st);
        });
    initialized.wait();                        // every driver is initialized here
    run_until_shutdown();
}                                              // drivers stop and join, then the latch dies

std::barrier step_done(4, []() noexcept { swap_buffers(); });   // runs once per phase
void simulate(int part, int steps) {           // run by 4 threads
    for (int s = 0; s < steps; ++s) {
        update_partition(part);                // reads the old buffer, writes the new one
        step_done.arrive_and_wait();
    }
}

std::counting_semaphore<4> upload_slots(4);    // at most 4 concurrent uploads
void upload(const Blob& b) {
    upload_slots.acquire();
    struct Release { std::counting_semaphore<4>& s; ~Release() { s.release(); } } guard{upload_slots};
    send(b);                                   // released even if send throws
}
```

the barrier's completion function must be `noexcept`-invocable; it runs after all participants arrive and before any is released, which makes it the safe place to swap double buffers. a semaphore has no owner, unlike a mutex, so nothing stops a missing `release()`: wrap it in RAII as shown.

finally, the minimal thread pool, built on [day 79](#day-79)'s `BoundedQueue`:

```cpp
#include <cstddef>
#include <functional>
#include <thread>
#include <vector>
// plus BoundedQueue<T> from the bounded queue lesson

class ThreadPool {
public:
    explicit ThreadPool(std::size_t n) : tasks_(1024) {
        for (std::size_t i = 0; i < n; ++i)
            workers_.emplace_back([this] {
                while (auto task = tasks_.pop()) (*task)();   // a throwing task terminates
            });
    }
    ~ThreadPool() { tasks_.close(); }     // workers drain the queue and exit, then join
    bool submit(std::function<void()> f) { return tasks_.push(std::move(f)); }
private:
    BoundedQueue<std::function<void()>> tasks_;
    std::vector<std::jthread> workers_;   // declared last: joined before tasks_ dies
};
```

it is about fifteen lines, and it is missing what production pools need: futures for results ([day 81](#day-81)'s `packaged_task`), exception handling, work stealing, priorities, and protection against the deadlock below. use an existing executor (Boost.Asio's `thread_pool`, oneTBB, or your framework's) unless you have a reason not to.

#### in practice

how many threads should a pool have? for CPU-bound work, about one per core is the usual starting point, and `std::thread::hardware_concurrency()` is a hint for that (it may return 0). for work that blocks on I/O, more threads keep the cores busy while others wait, and the right number is found by measuring. two rules hold in either case. keep latency-critical threads, such as a control loop, out of general-purpose pools, so a burst of background work cannot delay them; give them their own dedicated thread. and prefer an existing executor in production: the hard parts (results, exceptions, fairness, nested tasks, shutdown) are already solved there.

#### watch out for

thread-starvation deadlock in pools. a task running on a pool submits a subtask to the same pool and blocks on its future. if every worker does this at once, all workers are waiting for subtasks that no free worker can run. no mutex is involved, so lock ordering cannot save you. avoid blocking waits inside pool tasks; split the work so the waiting happens outside the pool, or use a framework that runs nested tasks while waiting (work-stealing schedulers do).

#### the takeaway

use a latch for one-time startup synchronization, a barrier for lock-step phases, and a semaphore to bound concurrency, each wrapped so it cannot be left in the wrong state; and keep blocking waits out of pool tasks.

#### optional challenge

in `start_drivers`, why must the latch be declared before the vector of `std::jthread`s? what could go wrong if the declarations were swapped?

<details>
<summary>answer</summary>

locals are destroyed in reverse order of declaration. with the latch declared first, the vector is destroyed first: every `jthread` requests stop and joins, so no driver thread can still be using the latch when it is destroyed. swapped, the latch would be destroyed before the threads are joined, and a driver that is slow to initialize could call `count_down()` on a destroyed object, which is undefined behavior. it is the same rule as declaring a `jthread` member last in [day 75](#day-75).

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-88"></a>

### day 88: review: futures, atomics, and concurrency design

**module 13:** futures, atomics, and concurrency design · **reading time:** about 10 minutes · **standard:** C++20  
**objective:** consolidate futures and async, atomics and memory orders, atomic waits, deadlock avoidance, and C++20 coordination primitives  
**covers:** [day 81](#day-81) to [day 87](#day-87)

#### recap

| lesson | key idea |
|---|---|
| [day 81](#day-81) | a one-shot channel for a value or an exception, synchronizing like `join`. |
| [day 82](#day-82) | name the launch policy, and keep the futures alive: a discarded `std::async` future blocks. |
| [day 83](#day-83) | single operations are indivisible; anything spanning two operations needs a CAS loop or a mutex. |
| [day 84](#day-84) | release/acquire pairs build happens-before edges for the surrounding data; `relaxed` builds none. |
| [day 85](#day-85) | wait and notify instead of spinning, keep hot atomics on separate cache lines, assert lock-freedom. |
| [day 86](#day-86) | break the cycle: `std::scoped_lock`, no unknown code or blocking waits under a lock. |
| [day 87](#day-87) | latch for startup, barrier for phases, semaphore for limits; prefer existing executors. |

#### review questions

1. two threads run this. is it correct?

   ```cpp
   std::atomic<int> count{0};
   std::vector<int> data;

   void add(int x) {
       if (count.load() < 100) { data.push_back(x); ++count; }
   }
   ```
2. this loop was meant to process chunks of a point cloud in parallel. a profile shows one core busy at a time. why?

   ```cpp
   for (auto& chunk : chunks)
       std::async(std::launch::async, process, std::ref(chunk));
   ```
3. pick a memory order for each: (a) a frames-processed counter that a statistics thread prints once a second; (b) a flag that tells a consumer a calibration struct has been fully written; (c) two threads that each set their own "I want to enter" flag and then read the other thread's flag.
4. from [day 77](#day-77): a component calls registered callbacks while holding its mutex, and one callback calls back into the component. what happens, and what is the fix?

#### mini exercise

find three concurrency bugs in this class, then fix them. assume `on_change`, `set`, and `get` can each be called from any thread at any time.

```cpp complete
#include <functional>
#include <map>
#include <mutex>
#include <string>

class TelemetryHub {
public:
    using Listener = std::function<void(const std::string&, double)>;

    void on_change(Listener l) { listener_ = std::move(l); }

    void set(const std::string& key, double value) {
        std::lock_guard lock(m_);
        latest_[key] = value;
        if (listener_) listener_(key, value);
    }

    const double& get(const std::string& key) {
        std::lock_guard lock(m_);
        return latest_.at(key);
    }

private:
    std::mutex m_;
    std::map<std::string, double> latest_;
    Listener listener_;
};
```

#### answers

<details>
<summary>answer 1: an atomic counter does not protect a vector</summary>

no, and for two separate reasons. `data.push_back` from two threads is a data race on the vector, which is UB; making `count` atomic says nothing about other memory ([day 84](#day-84)). and even with the vector protected, check-then-act is a race condition: both threads can see 99 and both append ([day 77](#day-77)). fix both with one mutex guarding the vector, with the check and the push in one critical section; `data.size()` then replaces the counter.

</details>

<details>
<summary>answer 2: the accidentally sequential loop</summary>

each returned `std::future` is a temporary destroyed at the end of the statement, and a future from `std::async` blocks in its destructor until its task finishes. every iteration waits for its own chunk ([day 82](#day-82)). since C++20, `std::async` is `[[nodiscard]]`, so GCC warns about this line. keep the futures in a `std::vector<std::future<void>>`, then call `get()` on each, which also rethrows any exception a chunk threw.

</details>

<details>
<summary>answer 3: choosing memory orders</summary>

(a) `relaxed`: only the count matters, and nothing is published through it. (b) `release` on the store and `acquire` on the load: the edge makes the struct's non-atomic writes visible after the flag is seen. (c) `seq_cst`: this is the store-buffering pattern from [day 84](#day-84)'s challenge, where acquire/release allows both threads to read `false`. if you are unsure, the default `seq_cst` is never wrong, only sometimes slower.

</details>

<details>
<summary>answer 4: callbacks under a lock</summary>

the callback runs on the same thread that already holds the component's `std::mutex`, so its call back into the component tries to lock it again: undefined behavior, in practice usually a self-deadlock. `std::recursive_mutex` would hide the symptom and run the callback against half-updated state. copy what the callbacks need (including the list of callbacks) under the lock, release it, and then call them.

</details>

<details>
<summary>mini exercise answer</summary>

the bugs: (1) `on_change` writes `listener_` without the lock while `set` reads it, a data race. (2) `set` calls the listener while holding `m_`; a listener that calls `get()` locks `m_` again on the same thread (UB, in practice a self-deadlock), and one that takes another lock can form a lock-order cycle ([day 86](#day-86)). (3) `get` returns a reference into the map; reading it after the lock is released races with a concurrent `set` of the same key ([day 77](#day-77)).

```cpp
class TelemetryHub {
public:
    using Listener = std::function<void(const std::string&, double)>;

    void on_change(Listener l) {
        std::lock_guard lock(m_);
        listener_ = std::move(l);
    }

    void set(const std::string& key, double value) {
        Listener listener;
        {
            std::lock_guard lock(m_);
            latest_[key] = value;
            listener = listener_;           // copy under the lock
        }
        if (listener) listener(key, value); // call unknown code with no lock held
    }

    double get(const std::string& key) const {
        std::lock_guard lock(m_);
        return latest_.at(key);             // a copy, not a reference
    }

private:
    mutable std::mutex m_;
    std::map<std::string, double> latest_;
    Listener listener_;
};
```

the fix has a price worth naming: listeners now run outside the lock, so two concurrent `set` calls on the same key can notify in the opposite order to their writes. if listeners need a consistent order, push the updates into a queue drained by one thread ([day 78](#day-78)). copying the `std::function` may allocate on every `set`; a `std::shared_ptr<const Listener>` snapshot avoids that if a profile says it matters.

</details>

#### connections

with this module, the concurrency toolbox is complete: threads and their ownership, mutexes and condition variables, futures, atomics and the memory model, and the C++20 coordination primitives. the recurring design lesson is that the best synchronization is the one you do not need: confinement, message passing, and immutable shared data. the next module steps back from mechanisms to design: SOLID, coupling and cohesion, dependency injection, and patterns, where ownership and lifetimes decide how components are wired together.

[back to the curriculum map](#curriculum)

---

<a id="module-design"></a>

## module 14: design principles and patterns

SOLID and coupling as predictions about change, dependency injection and seams, and patterns written with modern tools.

<a id="day-89"></a>

### day 89: SOLID as heuristics, not rules

**module 14:** design principles and patterns · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** read the five SOLID principles as predictions about the cost of change, and separate responsibilities where change actually happens  
**builds on:** [day 32](#day-32) (composition, interfaces, and substitutability), [day 28](#day-28) (ownership in function signatures)

#### the idea

every codebase has a class that everybody touches. in a radar team it might be `TrackFileProcessor`: it opens the recording, parses binary frames, drops low-SNR detections, converts units, and writes CSV. a new file format, a new filter threshold, and a new output column are three unrelated changes, made by three people, all landing in the same 900-line file and the same merge conflicts.

SOLID is usually presented as five rules that fix this. it is more useful to read the five letters as heuristics about one question: when a requirement changes, how much code has to change with it, and how much has to be recompiled, retested, and redeployed?

#### understanding the concept

each principle in one sentence, phrased as the change it protects you from:

| principle | one-sentence version | the change it absorbs |
|---|---|---|
| single responsibility (SRP) | a module should have one reason to change, meaning one group of people or one requirement driving it | a format change does not touch filtering |
| open/closed (OCP) | you can add behaviour by adding code rather than editing working code | a new sensor type is a new class or a new variant alternative, not a new `case` in ten switches |
| Liskov substitution (LSP) | a derived type must honour the base contract, not just its signatures ([day 32](#day-32)) | callers of `Sensor::read()` keep working with every sensor |
| interface segregation (ISP) | clients should not depend on functions they do not call | a change to calibration does not recompile the planner |
| dependency inversion (DIP) | high-level policy should depend on an abstraction it owns, and low-level detail should implement it | swapping the map backend does not touch the planner |

#### in code

**SRP: separate the decision from the plumbing.** the before version mixes I/O, parsing, and policy, so you cannot test the filter without a file on disk.

```cpp
// before: three reasons to change in one function
void process_track_file(const std::string& in_path, const std::string& out_path) {
    std::ifstream in(in_path, std::ios::binary);
    std::ofstream out(out_path);
    RawFrame frame;
    while (in.read(reinterpret_cast<char*>(&frame), sizeof frame)) {  // format
        if (frame.snr_db < 12.0f) continue;                           // policy
        out << frame.range_m << ',' << frame.azimuth_deg << '\n';     // output
    }
}
```

```cpp complete
#include <algorithm>
#include <iterator>
#include <vector>

struct Detection { float range_m, azimuth_deg, snr_db; };

// policy: pure, cohesive, trivially unit-testable
struct SnrGate {
    float min_snr_db;
    bool accept(const Detection& d) const { return d.snr_db >= min_snr_db; }
};

std::vector<Detection> gate(const std::vector<Detection>& in, SnrGate g) {
    std::vector<Detection> out;
    std::copy_if(in.begin(), in.end(), std::back_inserter(out),
                 [&](const Detection& d) { return g.accept(d); });
    return out;
}

// format and output live in their own functions (or files), e.g.
// std::optional<Detection> parse_frame(const std::byte* p, std::size_t n);
// void write_csv(std::ostream& os, const std::vector<Detection>& ds);
```

notice what we did not do: no `IDetectionFilter` interface, no factory. the responsibilities are separated by plain functions and a small value type. an abstraction can come later if a second filter actually appears.

#### in practice

a common failure mode in robotics stacks is the opposite of the god class: every concrete class gets an `I`-prefixed interface, a mock, and a factory, "for testability". after a year the codebase has 300 interfaces with exactly one production implementation each. reading the control flow means jumping through an interface, a factory, and a registry to find the one class that actually runs. every signature change is made twice. the mocks encode call sequences, so refactors break tests that did not catch any bug.

a better default is **the smallest thing that keeps options open**:

- start concrete. pure functions and value types are already decoupled and testable.
- introduce an interface at a *real* seam: hardware, time, network, filesystem, a third-party library, or a point where you genuinely have two implementations today.
- let the consumer own the interface, and keep it as narrow as that consumer needs.
- keep headers lean, because the build graph is part of the architecture.

YAGNI ("you aren't gonna need it") is the counterweight to OCP. being open for extension in a direction nobody extends costs indirection forever. extracting an interface from concrete code when the second implementation arrives is usually a short, mechanical refactor; removing a speculative abstraction that ten modules depend on is not.

#### watch out for

the principles conflict, and following one to the extreme violates another. taken literally, SRP produces dozens of one-method classes, which raises coupling between them because every behaviour now needs five collaborators wired together. OCP via virtual dispatch hides control flow: the debugger shows `filter->apply()`, and you need runtime state to know what ran. DIP through a virtual interface also has a mechanism cost (an indirect call that usually cannot be inlined); in a 1 kHz control loop that is almost never the bottleneck, but in a per-sample inner loop over millions of samples it can be, so measure with a profiler before and after rather than guessing.

also notice that "reason to change" is about people and requirements, not about counting methods. a `Quaternion` class with 40 methods is cohesive: it all changes when the math changes, which is never.

#### the takeaway

SOLID is a set of tools for predicting the cost of change: use them to place seams where change actually happens, let the consumer own the interface, and keep everything else concrete and boring.

#### optional challenge

a `MotorController` class has methods `set_torque`, `read_encoder`, `log_to_file`, `load_gains_from_yaml`, and `publish_diagnostics_over_udp`. which of these would you pull out first, and which principle are you really applying?

<details>
<summary>answer</summary>

the control core is `set_torque` and `read_encoder`: they share state and change with the control law. `log_to_file`, `load_gains_from_yaml`, and `publish_diagnostics_over_udp` each change for a different reason (logging policy, config format, network protocol) and drag in heavy dependencies (filesystem, a YAML parser, sockets) that make the controller hard to build and test. pull the YAML loading out first: it is pure input conversion and can become a free function returning a `Gains` value, which the controller accepts in its constructor. that is SRP, but the practical win is physical: the controller no longer includes the YAML library, so it compiles faster and can be tested without files. diagnostics and logging can become an injected sink ([day 91](#day-91)) once you need to swap them.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-90"></a>

### day 90: coupling, cohesion, and physical design

**module 14:** design principles and patterns · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** judge a design by what must change and what must recompile together, invert dependencies with consumer-owned interfaces, and keep headers light  
**builds on:** [day 89](#day-89) (SOLID as heuristics, not rules), [day 02](#day-02) (linkage and the one definition rule)

#### the idea

two modules that look independent on an architecture diagram can still be welded together: change one header, and four hundred files recompile; change one data format, and three teams edit the same file. the vocabulary for this is older than SOLID and more general: coupling and cohesion. C++ adds a dimension that most languages hide, because its build model makes every `#include` a dependency you pay for in compile time.

#### understanding the concept

two older ideas sit underneath all five. **coupling** is the degree to which two pieces of code must change together. **cohesion** is the degree to which the things inside one piece belong together, meaning they change for the same reasons and use the same data. good design is high cohesion inside a module and low coupling between modules. SOLID is mostly a list of tactics for those two goals.

C++ adds a dimension most languages hide: **physical coupling**. every `#include` in a header is a compile-time dependency for every file that includes that header, transitively. a logical design can look clean on a whiteboard while one widely included header pulls a heavy linear-algebra header into 400 translation units. that cost shows up as build times and as rebuild cascades when someone edits a private detail. logical coupling decides what has to change together; physical coupling decides what has to recompile together.

#### in code

**ISP and DIP: let the client define the interface.** a path planner that takes the whole robot couples to everything the robot can do.

```cpp
// before: the planner sees calibration, firmware update, and motor control
class Robot {
public:
    virtual ~Robot() = default;
    virtual bool is_occupied(int x, int y) const = 0;
    virtual void calibrate_lidar() = 0;
    virtual void flash_firmware(const std::vector<unsigned char>& image) = 0;
    virtual void set_wheel_speeds(double left, double right) = 0;
};
std::vector<Cell> plan(const Robot& robot, Cell from, Cell to);
```

```cpp
// after: the planner owns the narrow interface it needs (DIP),
// and nothing else leaks into it (ISP)
struct Cell { int x, y; };

class OccupancyQuery {        // lives in the planner's header, not the robot's
public:
    virtual ~OccupancyQuery() = default;
    virtual bool is_occupied(Cell c) const = 0;
};

std::vector<Cell> plan(const OccupancyQuery& map, Cell from, Cell to);

// the low-level module depends upward on the planner's abstraction
class GridMap final : public OccupancyQuery {
public:
    GridMap(int width, int height) : width_(width), cells_(std::size_t(width) * height) {}
    bool is_occupied(Cell c) const override {
        return cells_[std::size_t(c.y) * width_ + c.x] != 0;  // caller keeps c in range
    }
private:
    int width_;
    std::vector<unsigned char> cells_;
};
```

the key detail of DIP is *ownership* of the interface. if `OccupancyQuery` lived in the map library, the planner would still depend on the map library. putting it next to the planner reverses the arrow: the map adapts to the planner, and a test can pass a ten-line fake ([day 91](#day-91) builds on exactly this).

**physical coupling: keep headers light.** a header only needs a full definition when it uses the size or members of a type.

```cpp external
// tracker.h
#pragma once
#include <memory>
#include <vector>

class KalmanFilter;           // forward declaration: no heavy include here
struct Detection;

class Tracker {
public:
    explicit Tracker(std::shared_ptr<const KalmanFilter> model);
    void update(const std::vector<Detection>& detections);  // incomplete type is fine in a declaration
private:
    std::shared_ptr<const KalmanFilter> model_;  // fine with an incomplete type
};                                               // (a unique_ptr member needs more care: see pimpl)
// tracker.cpp includes "kalman_filter.h" and "detection.h"
```

now editing `kalman_filter.h` rebuilds `tracker.cpp`, not every file that includes `tracker.h`. [day 100](#day-100) takes this further with pimpl.

#### in practice

in a large C++ codebase, the build graph is something you can measure and manage like any other architecture. the questions worth asking of a widely included header are: what does it include, and does each include provide something the header itself uses by size or by member? replace includes with forward declarations where a pointer, reference, or function declaration suffices; move implementation-only includes into the `.cpp`; and split headers that serve unrelated clients (a header with both the public API and the test helpers forces both on everyone). GCC's `-H` flag prints the include tree of a translation unit, and Clang's `-ftime-trace` shows where compile time goes, which turns "this build feels slow" into a list of specific headers.

#### watch out for

**relying on transitive includes.** a file that uses `std::vector` but compiles only because some other header it includes happens to include `<vector>` is coupled to that other header's private choices. the day that header switches to a forward declaration (exactly the improvement this lesson recommends), unrelated files stop compiling. "include what you use": every file includes the headers for the names it uses directly. tools such as include-what-you-use and `clang-tidy`'s `misc-include-cleaner` check it mechanically.

#### the takeaway

coupling is what must change together and cohesion is what belongs together; in C++, also ask what must recompile together, because your header graph is part of your design.

#### optional challenge

`tracker.h` is included by 300 files. which of these edits to it force all 300 to recompile, and which change the class layout that compiled clients depend on?

1. adding a private data member to `Tracker`
2. adding a private non-virtual member function declaration
3. changing a member function's body, which is defined in `tracker.cpp`
4. changing the default argument of a public member function

<details>
<summary>answer</summary>

with a typical timestamp-based build, (1), (2), and (4) recompile all 300 files, because the header's text changed; (3) recompiles only `tracker.cpp`. of those, only (1) changes the layout: `sizeof(Tracker)` and member offsets are baked into every client that creates or embeds a `Tracker`, so a client compiled against the old header and linked with the new `.cpp` would be broken. (2) changes no layout, and (4) changes only call sites (default arguments are substituted by the caller), but both still trigger rebuilds. the pimpl idiom in [day 100](#day-100) moves private members out of the header so that edits like (1) and (2) stop rippling.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-91"></a>

### day 91: dependency injection: passing collaborators in

**module 14:** design principles and patterns · **reading time:** about 10 minutes · **standard:** C++17  
**objective:** make a class testable by injecting the dependencies that cross a boundary, decide who owns them, and wire everything in one place  
**builds on:** [day 90](#day-90) (coupling, cohesion, and physical design), [day 28](#day-28) (ownership in function signatures)

#### the idea

here is a joint controller that looks perfectly reasonable:

```cpp
class JointController {
public:
    void step(double target_rad) {
        const auto t = std::chrono::steady_clock::now();       // hidden dependency
        const double dt = std::chrono::duration<double>(t - last_).count();
        const double err = target_rad - motor_.position();
        motor_.command_torque(kp_ * err + kd_ * (err - last_err_) / dt);
        last_ = t;
        last_err_ = err;
    }
private:
    CanBusMotor motor_{"can0", 0x141};                          // hidden dependency
    double kp_ = 10.0, kd_ = 0.5, last_err_ = 0.0;
    std::chrono::steady_clock::time_point last_ = std::chrono::steady_clock::now();
};
```

how do you test that the derivative term behaves when `dt` is 10 ms? you can't, short of plugging in a CAN adapter and sleeping. the controller decides *what* to compute and also *where its inputs come from*. dependency injection is just separating those: the object receives its collaborators instead of creating or fetching them.

#### understanding the concept

a **seam** is a place where you can change what code does without editing that code, and dependency injection creates seams deliberately: an object receives its collaborators (a clock, an actuator, a socket, a random number generator) instead of creating or fetching them itself. the things worth injecting are the ones that cross a boundary or make behavior nondeterministic: time, hardware, I/O, randomness, and third-party services. pure computation stays inside.

two decisions come with every injected dependency. **ownership**: does the controller own the clock (`std::unique_ptr<Clock>`), share it (`std::shared_ptr`, rarely justified), or borrow it (a reference, with the caller promising it outlives the controller)? [day 28](#day-28)'s rules apply unchanged. **who wires things up**: the answer should be one place near `main`, often called the composition root, where concrete objects are created and passed down. everything below it just takes what it is given.

on the test side, distinguish a **fake** from a **mock**. a fake is a small working implementation with its own state: a clock that only moves when the test advances it. a mock records calls and verifies expectations about them ("`command_torque` called once with 60"). prefer fakes and check outcomes; reach for mocks when the interaction itself is the requirement, such as "the enable command must precede the first torque command".

#### in code

**constructor injection with interfaces.** the controller now borrows a clock and an actuator. production code passes the real ones; tests pass fakes.

```cpp complete
#include <chrono>

class Clock {
public:
    virtual ~Clock() = default;
    virtual std::chrono::steady_clock::time_point now() const = 0;
};

class Actuator {
public:
    virtual ~Actuator() = default;
    virtual double position() const = 0;           // rad
    virtual void command_torque(double nm) = 0;
};

class JointController {
public:
    JointController(const Clock& clock, Actuator& motor, double kp, double kd)
        : clock_(clock), motor_(motor), kp_(kp), kd_(kd), last_(clock.now()) {}

    void step(double target_rad) {
        const auto t = clock_.now();
        const double dt = std::chrono::duration<double>(t - last_).count();
        const double err = target_rad - motor_.position();
        const double derr = dt > 0.0 ? (err - last_err_) / dt : 0.0;
        motor_.command_torque(kp_ * err + kd_ * derr);
        last_ = t;
        last_err_ = err;
    }

private:
    const Clock& clock_;         // borrowed: must outlive the controller
    Actuator& motor_;            // borrowed
    double kp_, kd_;
    std::chrono::steady_clock::time_point last_;
    double last_err_ = 0.0;
};
```

the test is now deterministic and runs in microseconds:

```cpp
#include <cassert>
#include <cmath>
#include <iostream>

struct FakeClock final : Clock {
    std::chrono::steady_clock::time_point t{};
    std::chrono::steady_clock::time_point now() const override { return t; }
};

struct FakeActuator final : Actuator {
    double pos = 0.0, last_torque = 0.0;
    double position() const override { return pos; }
    void command_torque(double nm) override { last_torque = nm; }
};

int main() {
    using namespace std::chrono_literals;
    FakeClock clock;
    FakeActuator motor;
    JointController ctl(clock, motor, /*kp=*/10.0, /*kd=*/0.5);

    clock.t += 10ms;
    ctl.step(1.0);                     // err 1.0, derr 100/s: 10 + 50
    assert(std::abs(motor.last_torque - 60.0) < 1e-9);

    motor.pos = 0.5;
    clock.t += 10ms;
    ctl.step(1.0);                     // err 0.5, derr -50/s: 5 - 25
    std::cout << motor.last_torque << '\n';   // prints: -20
}
```

#### in practice

in a typical robot stack the result looks like this: `main` reads config, constructs `CanBusMotor`, `SystemClock`, and a `UdpTelemetrySink`, then passes references into controllers and planners. unit tests construct the same controllers with fakes, and hardware-in-the-loop tests swap only the motor. nothing below `main` ever calls `steady_clock::now()` or opens a socket on its own.

#### watch out for

**service locators and DI containers.** a global registry you query (`Services::get<Clock>()`) looks convenient, but it hides dependencies again: the constructor no longer tells you what the class needs, missing registrations fail at run time instead of compile time, and tests have to reset global state. reflection-driven DI frameworks from Java or C# have no direct C++ equivalent, and the libraries that emulate them add template complexity to save a few lines in `main`. explicit constructor arguments are usually enough.

**borrowed references outliving their owner.** `JointController` stores references, so this compiles and is undefined behavior on the first `step`:

```cpp
JointController make_controller(Actuator& motor) {
    SystemClock clock;                        // production Clock, local to this function
    return JointController(clock, motor, 10.0, 0.5);
}   // BUG: clock is destroyed; the returned controller holds a dangling reference
```

if lifetimes are not obviously nested, take ownership (`std::unique_ptr<Clock>`) instead.

also watch the constructor length. a class that needs eight injected collaborators is usually telling you about poor cohesion ([day 90](#day-90)), not about a lack of DI tooling.

#### the takeaway

inject what crosses a boundary (time, hardware, I/O, randomness), make ownership of every injected object explicit, and wire everything in one place near `main`.

#### optional challenge

a trajectory follower uses a `std::vector<double>` of waypoints, `std::sqrt`, the system clock, a UDP socket for telemetry, and a random jitter source for testing robustness. which of these would you inject, and why?

<details>
<summary>answer</summary>

inject the clock, the socket, and the random source: each crosses a boundary or makes behavior nondeterministic, so a test needs to control it (advance time, capture what was sent, fix the random sequence). do not inject the vector or `std::sqrt`: they are deterministic, local, and already testable through the follower's inputs and outputs. injecting them would add indirection without adding a single test you could not already write.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-92"></a>

### day 92: choosing a seam: interfaces, templates, functions, and the linker

**module 14:** design principles and patterns · **reading time:** about 7 minutes · **standard:** C++20  
**objective:** choose between a virtual interface, a constrained template, `std::function`, and a link-time seam by when the decision is made and what it costs  
**builds on:** [day 91](#day-91) (dependency injection: passing collaborators in), [day 61](#day-61) (writing your own concepts), [day 38](#day-38) (lambdas that outlive their scope: callbacks and `std::function`)

#### the idea

once a class receives its collaborators, a second question remains: what *type* is the parameter? a virtual interface, a template parameter, a `std::function`, or nothing at all, with the substitution happening in the linker. all four make the code testable. they differ in when the choice is made, what it costs at run time, and how much of the decision is visible when you read the code.

#### understanding the concept

a **seam** is a place where you can change what code does without editing that code. dependency injection creates seams deliberately. in C++ you have four main kinds, and they differ in when the choice is made:

| seam | chosen at | cost and constraints | good for |
|---|---|---|---|
| virtual interface, injected via constructor | run time | indirect call, usually not inlined; needs an interface type and a lifetime decision | hardware, I/O, plugins, anything chosen from config |
| template parameter (constrained by a concept) | compile time | no indirection; code lives in headers, each instantiation is separate code, longer builds | hot paths, header-only utilities, policies |
| `std::function` | run time | type erasure: indirect call, may allocate for large callables ([day 38](#day-38)) | single callbacks: a time source, a log sink |
| link-time | link time | one implementation per binary; invisible in the source | replacing a platform function (time, GPIO) in a test binary |

#### in code

**compile-time injection with a concept (C++20).** when the dependency is fixed per build and sits on a hot path, make it a template parameter. the concept documents what the dependency must provide and gives readable errors ([day 61](#day-61)).

```cpp complete
#include <chrono>
#include <concepts>
#include <optional>

template <typename C>
concept SteadyTimeSource = requires(const C& c) {
    { c.now() } -> std::same_as<std::chrono::steady_clock::time_point>;
};

template <SteadyTimeSource Clock>
class RateLimiter {
public:
    RateLimiter(Clock clock, std::chrono::nanoseconds min_gap)
        : clock_(std::move(clock)), gap_(min_gap) {}

    bool allow() {
        const auto t = clock_.now();
        if (last_ && t - *last_ < gap_) return false;
        last_ = t;
        return true;
    }

private:
    Clock clock_;
    std::chrono::nanoseconds gap_;
    std::optional<std::chrono::steady_clock::time_point> last_;
};

struct SystemSteadyClock {                       // production
    auto now() const { return std::chrono::steady_clock::now(); }
};
struct ManualClock {                             // test: reads a time the test controls
    const std::chrono::steady_clock::time_point* t;
    auto now() const { return *t; }
};

// usage in a test:
//   std::chrono::steady_clock::time_point now{};
//   RateLimiter limiter(ManualClock{&now}, 100ms);    // CTAD picks ManualClock
//   limiter.allow();  // true
//   now += 50ms;  limiter.allow();  // false
//   now += 60ms;  limiter.allow();  // true
```

no interface, no virtual call, and `SystemSteadyClock` is an empty class (it still occupies at least one byte as a member; `[[no_unique_address]]` in C++20 can remove that). the price is that `RateLimiter<ManualClock>` and `RateLimiter<SystemSteadyClock>` are different types, so you cannot store both in one container or choose between them from a config file.

**a `std::function` seam** is the lightest runtime option when the dependency is a single operation:

```cpp
#include <functional>

using TimeSource = std::function<std::chrono::steady_clock::time_point()>;

class Watchdog {
public:
    explicit Watchdog(TimeSource now = [] { return std::chrono::steady_clock::now(); })
        : now_(std::move(now)), last_kick_(now_()) {}
    void kick() { last_kick_ = now_(); }
    bool expired(std::chrono::milliseconds limit) const { return now_() - last_kick_ > limit; }
private:
    TimeSource now_;
    std::chrono::steady_clock::time_point last_kick_;
};
```

#### in practice

**link-time seams** deserve a mention because embedded and robotics code uses them heavily. suppose the low-level HAL declares `std::uint64_t hal_monotonic_ns();` in a header. the firmware build links `hal_time_stm32.cpp`; the host test build links `hal_time_fake.cpp`, which returns a global the test sets. the code under test has no interface, template, or callback at all. the tradeoffs: only one implementation per binary, the seam is invisible when reading the source (only the build files reveal it), and if both files end up in the same link you get a duplicate-symbol error, or worse, with static libraries the linker silently uses whichever definition it pulls in first. use it for platform functions you cannot change, not for application design.

#### watch out for

**an interface on a per-sample hot path.** a virtual seam is cheap when it is called once per frame or per control cycle, and the indirect call disappears in the noise. put the same interface inside a loop that runs a million times per frame (a per-sample filter, a per-point distance function) and the call can no longer be inlined, which also blocks vectorization of the loop around it. the fix is not to give up the seam but to pick the right kind: a template parameter constrained by a concept keeps the substitution point and lets the compiler see through it. as always, measure before and after; the profile decides, not the principle.

#### the takeaway

choose the seam by when the decision is made: run time (virtual interface or `std::function`), compile time (a template constrained by a concept), or link time (platform functions only); every kind is testable, and each costs something different.

#### optional challenge

`RateLimiter` stores its clock by value. why does the test version use `ManualClock` holding a pointer, instead of passing a `FakeClock` with a mutable `t` member directly?

<details>
<summary>answer</summary>

because `RateLimiter` copies (or moves) the clock into its own member `clock_`. if the test passed a `FakeClock` value, advancing the test's copy would not affect the limiter's copy, so time would never move from the limiter's point of view. the pointer gives the copy a handle back to state the test controls. alternatives: pass a `std::reference_wrapper`-like adapter, or give `RateLimiter` a reference member and accept the borrowed-lifetime rule. value semantics for injected policies is a good default for stateless or cheaply copied policies; when the test needs to observe or steer shared state, some form of indirection is unavoidable.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-93"></a>

### day 93: patterns in modern C++: strategy

**module 14:** design principles and patterns · **reading time:** about 6 minutes · **standard:** C++17  
**objective:** make an algorithm a replaceable part with a virtual interface, `std::function`, or a template parameter, and choose by when and how often it varies  
**builds on:** [day 92](#day-92) (choosing a seam: interfaces, templates, functions, and the linker), [day 54](#day-54) (closed sets and open sets: variant state machines and `std::any`)

#### the idea

the classic pattern catalogue was written for C++98 and Smalltalk, before lambdas, `std::function`, `std::variant`, and smart pointers. some patterns survive unchanged, some shrink to a single line, and some need modern care that the original books never mentioned, such as who owns an observer and which thread calls it. the simplest one to start with is strategy: an algorithm that should be a replaceable part.

#### understanding the concept

a pattern is a name for a recurring solution, not a goal. its main value is vocabulary: "the planner takes a cost strategy" tells a reviewer a lot in six words. the risk is building the pattern because it is a pattern.

- **strategy** makes an algorithm a replaceable part. in C++ you have three ways to plug it in, with different tradeoffs (the table below).

several other classic patterns collapse into language features. command is usually a lambda stored in a `std::function` or a queue. visitor over a closed set of types is `std::visit` on a `std::variant` ([day 53](#day-53)). template method is often better served by passing a callable than by inheritance.

#### in code

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

#### in practice

a tracker library usually needs more than one of these at once. the smoothing filter for each track is chosen per build and runs for every measurement, so it is a template parameter (or a concrete type) and inlines into the update loop. the gating policy is chosen per deployment from a configuration file and runs once per frame, so a `std::function` or a small virtual interface is the honest choice. the cost model for association needs three related operations that must agree with each other (cost, gate size, and a debugging description), which is the case a virtual interface handles best: the operations travel together as one object. picking per call site, rather than one mechanism for the whole library, is what keeps both the hot path and the configuration flexible.

#### watch out for

**a stateful strategy is copied, not shared.** `Ema` carries state (`y` and `primed`), and every mechanism above stores its own copy:

```cpp
Ema shared{0.3};
TrackerF a{shared};
TrackerF b{shared};    // a and b each smooth independently; shared is never updated
```

that is usually right (each track needs its own filter state), but it surprises code that expects to reset or inspect "the" strategy through the original object. the standard algorithms copy function objects freely too. when state really must be shared, make that explicit with a reference or pointer member, and decide who owns the shared state.

#### the takeaway

a strategy is a replaceable algorithm: plug it in as a template parameter for hot, per-build choices, as a `std::function` for single operations chosen at run time, and as a virtual interface when several related operations travel together.

#### optional challenge

pick a mechanism for each: (a) a path cost function selected from a configuration file at startup; (b) a per-pixel kernel in an image filter; (c) a planner policy that provides a cost, a heuristic, and a neighbor generator that must stay consistent.

<details>
<summary>answer</summary>

(a) `std::function<double(const Edge&)>` (or a virtual interface): chosen at run time from data, and called often enough to matter only if profiling says so. (b) a template parameter: called millions of times per image, so inlining and vectorization matter, and the choice is known at compile time. (c) a virtual interface (or a template constrained by a concept, if the choice is per build): three operations that must agree belong in one object, and a single interface keeps them from being mixed and matched by accident.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-94"></a>

### day 94: patterns in modern C++: factories and registries

**module 14:** design principles and patterns · **reading time:** about 5 minutes · **standard:** C++17  
**objective:** hide the choice of concrete type behind a factory function or an explicit registry, and avoid self-registration tricks that break at link time  
**builds on:** [day 93](#day-93) (patterns in modern C++: strategy), [day 06](#day-06) (storage duration and object lifetime)

#### the idea

a configuration file says `type: lidar`, and somewhere a string must become an object of the right class. the code that knows all the concrete types should be in one place, and everything else should see only the interface. that is the factory pattern, and in modern C++ its default form is almost anticlimactic: a function that returns `std::unique_ptr<Base>`. the interesting decisions are about how that function learns which types exist.

#### understanding the concept

- **factory** hides which concrete type gets created. in modern C++ the default form is a plain function returning `std::unique_ptr<Base>`; a registry of creators appears when the choice comes from data (a config file, a plugin name).

#### in code

**factory with a registry.** when a config file says `type: lidar`, something has to map that string to a constructor.

```cpp
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>

struct SensorConfig { std::string type, device; };

class Sensor {
public:
    virtual ~Sensor() = default;
    virtual double read() = 0;
};

using SensorFactory = std::function<std::unique_ptr<Sensor>(const SensorConfig&)>;

class SensorRegistry {
public:
    void add(std::string type, SensorFactory f) { makers_[std::move(type)] = std::move(f); }
    std::unique_ptr<Sensor> create(const SensorConfig& cfg) const {
        const auto it = makers_.find(cfg.type);
        if (it == makers_.end()) throw std::invalid_argument("unknown sensor type: " + cfg.type);
        return it->second(cfg);
    }
private:
    std::unordered_map<std::string, SensorFactory> makers_;
};

// explicit registration, called once from main: visible, ordered, link-safe
void register_builtin_sensors(SensorRegistry& r) {
    r.add("imu",   [](const SensorConfig& c) { return std::make_unique<Imu>(c.device); });
    r.add("lidar", [](const SensorConfig& c) { return std::make_unique<Lidar>(c.device); });
}
```

the tempting alternative is self-registration, where each `.cpp` file registers itself from a namespace-scope initializer:

```cpp
// lidar.cpp: "automatic" registration
namespace {
const bool lidar_registered = (global_registry().add("lidar", make_lidar), true);
}
```

it works in a demo and breaks in production for two reasons. first, if `lidar.o` lives in a static library and nothing else references a symbol in it, the linker never pulls that object file into the executable, so the initializer never runs and `"lidar"` is silently unknown (the usual workarounds, `--whole-archive` or `/WHOLEARCHIVE`, are build-system patches for a design problem). second, the registry itself must be a function-local static, or you have the static initialization order problem from [day 06](#day-06). an explicit `register_builtin_sensors` call costs one line and has neither problem.

#### in practice

factories belong at the composition root from [day 91](#day-91): `main` reads the configuration, calls `registry.create(cfg)` for each configured sensor, and passes the resulting objects (or references to them) down to the components that use them. nothing below `main` names a concrete sensor type, so adding a new sensor is one new class plus one registration line, and components depend only on the `Sensor` interface. returning `std::unique_ptr<Sensor>` keeps the ownership decision with the caller, who can store it, move it into a component, or convert it to a `std::shared_ptr` if sharing is genuinely needed.

#### watch out for

patterns also invite premature generality. a `SensorRegistry` for two sensor types that are chosen by a compile-time flag is overkill; a `switch` in one factory function is clearer until the set becomes data-driven.

#### the takeaway

make factories return `std::unique_ptr<Base>`, register creators explicitly from one function called by `main`, and add a registry only when the choice of type really comes from data.

#### optional challenge

`SensorRegistry::create` throws `std::invalid_argument` for an unknown type. a colleague prefers returning `nullptr`. argue for one of them, using the error-handling criteria from [day 50](#day-50).

<details>
<summary>answer</summary>

an unknown sensor type in a configuration file is a configuration error found at startup: rare, not recoverable locally, and best reported with context ("unknown sensor type: lidr" names the typo). that is the case for an exception. returning `nullptr` makes every caller check, and a forgotten check turns a clear startup error into a null dereference later. if some caller genuinely treats unknown types as normal (a plugin browser listing what is available), give it a separate query such as `bool knows(std::string_view type)`, rather than weakening `create` for everyone.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-95"></a>

### day 95: patterns in modern C++: observer and subscriptions

**module 14:** design principles and patterns · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** notify interested parties without dangling observers, using RAII subscription tokens and notification outside the lock  
**builds on:** [day 94](#day-94) (patterns in modern C++: factories and registries), [day 86](#day-86) (deadlocks: breaking the cycle), [day 27](#day-27) (shared ownership with `std::shared_ptr` and `std::weak_ptr`)

#### the idea

a radar tracker announces "track confirmed" and "track lost" to a display, a recorder, and a fusion module, none of which it should know about. the classic observer pattern solves the knowing. it says nothing about the two problems that cause the real bugs: an observer that is destroyed while still registered, and a notification that calls unknown code while holding a lock.

#### understanding the concept

- **observer** lets a subject notify interested parties without knowing them. the hard parts are lifetime (an observer destroyed while still registered) and concurrency (calling unknown code while holding a lock, [day 86](#day-86)).

#### in code

**observer with RAII subscriptions.** the subscription token unsubscribes in its destructor, and `emit` calls observers outside the lock.

```cpp complete
#include <functional>
#include <map>
#include <memory>
#include <mutex>
#include <vector>

template <typename... Args>
class Signal {
    using Slot = std::function<void(Args...)>;
    struct State {
        std::mutex m;
        std::map<int, std::shared_ptr<Slot>> slots;
        int next_id = 0;
    };
    std::shared_ptr<State> state_ = std::make_shared<State>();

public:
    class Subscription {
    public:
        Subscription(std::weak_ptr<State> s, int id) : state_(std::move(s)), id_(id) {}
        Subscription(Subscription&&) noexcept = default;
        Subscription& operator=(Subscription&& o) noexcept {
            if (this != &o) { reset(); state_ = std::move(o.state_); id_ = o.id_; }
            return *this;
        }
        ~Subscription() { reset(); }
        void reset() {
            if (auto s = state_.lock()) {            // the signal may already be gone
                std::lock_guard lock(s->m);
                s->slots.erase(id_);
            }
            state_.reset();
        }
    private:
        std::weak_ptr<State> state_;
        int id_;
    };

    [[nodiscard]] Subscription subscribe(Slot f) {
        std::lock_guard lock(state_->m);
        const int id = state_->next_id++;
        state_->slots.emplace(id, std::make_shared<Slot>(std::move(f)));
        return Subscription(state_, id);
    }

    void emit(Args... args) const {
        std::vector<std::shared_ptr<Slot>> snapshot;
        {
            std::lock_guard lock(state_->m);
            for (const auto& kv : state_->slots) snapshot.push_back(kv.second);
        }
        for (const auto& slot : snapshot) (*slot)(args...);   // no lock held here
    }
};

// Signal<int> track_lost;
// {
//     auto sub = track_lost.subscribe([](int id) { std::cout << "lost " << id << '\n'; });
//     track_lost.emit(7);        // prints: lost 7
// }                              // sub destroyed: unsubscribed
// track_lost.emit(8);            // prints nothing
```

`[[nodiscard]]` matters here: discarding the token would unsubscribe immediately. the `weak_ptr` lets a token outlive its signal safely. the moved-from token holds an empty `weak_ptr`, so its destructor does nothing.

#### in practice

a radar tracker publishes "track confirmed" and "track lost" events to a display, a recorder, and a fusion module. with a raw `std::vector<Listener*>` in the tracker, the display gets closed, its object is destroyed, and the next event calls through a dangling pointer: undefined behavior, typically a crash far from the cause. RAII tokens tie the subscription's lifetime to the subscriber object (store the token as a member, and it unsubscribes when the subscriber dies).

the other classic fix is a subject holding `std::weak_ptr<Listener>` and calling `lock()` before each notification. it is correct, but it forces every observer to be owned by a `shared_ptr`, which is an ownership decision imposed by the notification mechanism ([day 27](#day-27) calls that a smell). tokens leave ownership to the observer.

calling observers outside the lock is the [day 86](#day-86) rule in action: a slot that subscribes, unsubscribes, or emits again would deadlock on a non-recursive mutex if `emit` held it, and a slow slot would block every other thread trying to subscribe.

#### watch out for

the snapshot in `emit` has a consequence. a slot can be called after its token was reset, if the reset happened after the snapshot was taken. the `shared_ptr<Slot>` keeps the `std::function` alive, but not whatever its lambda captured by reference, so if the subscriber object is gone, the call is undefined behavior. in a single thread this only happens when one slot destroys another subscriber during `emit`; re-checking under the lock that each slot is still registered just before calling it closes that case. across threads the re-check can go stale between the check and the call, so either make `reset` wait until in-flight calls to that slot finish, or deliver events by posting to the subscriber's own thread or queue ([day 79](#day-79)). decide which threading contract your signal offers and document it.

#### the takeaway

give every subscription an owner in the form of an RAII token, notify from a snapshot with no lock held, and document which thread calls observers and whether a call can arrive after unsubscribing.

#### optional challenge

a colleague changes `emit` to hold the lock while calling the slots, "to fix the cross-thread race". what breaks, even in a single-threaded program?

<details>
<summary>answer</summary>

any slot that touches the same signal from inside the callback now deadlocks, because `std::mutex` is not recursive and locking it twice from the same thread is undefined behavior (in practice usually a deadlock). common cases are a one-shot listener that destroys its own token when it fires, a listener that subscribes a follow-up handler, and an event handler that emits another event on the same signal. switching to `std::recursive_mutex` hides the deadlock but not the problem: erasing from `slots` while `emit` is iterating over it invalidates the iterator, which is also undefined behavior. the snapshot exists precisely to make reentrancy safe; the cross-thread issue needs a different fix (wait for in-flight calls, or post to the subscriber's thread).

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-96"></a>

### day 96: review: design principles and patterns

**module 14:** design principles and patterns · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** consolidate SOLID, coupling and cohesion, dependency injection and seams, and the strategy, factory, and observer patterns  
**covers:** [day 89](#day-89) to [day 95](#day-95)

#### recap

| lesson | key idea |
|---|---|
| [day 89](#day-89) | SOLID predicts the cost of change; separate responsibilities where change actually happens. |
| [day 90](#day-90) | what changes together, what belongs together, and in C++ what recompiles together; consumers own their interfaces. |
| [day 91](#day-91) | inject what crosses a boundary, make ownership explicit, wire in one place near `main`. |
| [day 92](#day-92) | choose the seam by when the decision is made: run time, compile time, or link time. |
| [day 93](#day-93) | a replaceable algorithm: template, `std::function`, or virtual interface, by frequency and shape. |
| [day 94](#day-94) | return `std::unique_ptr<Base>`, register creators explicitly, not through static initializers. |
| [day 95](#day-95) | RAII subscription tokens, notification from a snapshot with no lock held. |

#### review questions

1. your codebase has `IConfigLoader` with exactly one implementation, `YamlConfigLoader`, used only by `App`, and a mock used in one test that checks `load()` was called once. keep the interface, or remove it? what would change your answer?
2. in [day 95](#day-95)'s `Signal`, why does `subscribe` return a `[[nodiscard]]` token, and why does the token hold a `std::weak_ptr` to the signal's state rather than a raw pointer or a `shared_ptr`?
3. a `SensorRegistry` is populated by namespace-scope initializers in each driver's `.cpp`, and the drivers are built into a static library. on one product, `"lidar"` is suddenly an unknown type. what happened, and what is the robust fix?
4. a function that the profiler shows on a per-sample hot path takes a `const Filter&` with a virtual `apply(double)`. what seam would you use instead, and what do you give up?
5. from [day 86](#day-86): [day 95](#day-95)'s `emit` copies the subscriber list under the lock and then calls the slots without it. name two distinct failures if it called the slots while holding a `std::mutex` instead.

#### mini exercise

this uploader cannot be unit tested: it constructs its own HTTP client and reads the wall clock directly. refactor it so that the transport and the clock are injected, then write a fake transport and a test that checks two behaviors: the buffer is kept when sending fails, and cleared when it succeeds. keep the production wiring simple.

```cpp
class TelemetryUploader {
public:
    void record(std::string line) { buffer_.push_back(std::move(line)); }
    void flush() {
        if (buffer_.empty()) return;
        HttpClient client("https://telemetry.internal");          // hard-wired transport
        const auto now = std::chrono::system_clock::now();         // hard-wired clock
        if (client.post("/batch", serialize(buffer_, now)) == 200) buffer_.clear();
    }
private:
    std::vector<std::string> buffer_;
};
```

#### answers

<details>
<summary>answer 1: the single-implementation interface</summary>

probably remove it. an interface with one implementation and a test that only verifies a call happened is indirection without a seam: config loading is input conversion, and the better design is a free function that turns text into a `Config` value, plus an `App` constructor that takes the `Config` ([day 90](#day-90)'s `MotorController` challenge). the test then builds a `Config` directly and needs no mock at all. keep or add an interface when there is a real boundary to cross at run time: config fetched from a remote service in some deployments and a file in others, or tests that need to simulate failures of the source (permissions, timeouts) that a value cannot express.

</details>

<details>
<summary>answer 2: tokens and weak_ptr</summary>

the token is the subscription: its destructor unsubscribes. discarding the return value would subscribe and immediately unsubscribe, a silent bug, so `[[nodiscard]]` turns it into a warning. the token must work whether it dies before or after the signal. a raw pointer would dangle if the signal were destroyed first. a `shared_ptr` would keep the signal's state alive as long as any token exists, so ownership would be dictated by subscribers, the opposite of what an observer should do. `weak_ptr::lock()` answers "is the signal still there?" safely and does not extend its life.

</details>

<details>
<summary>answer 3: self-registration and static libraries</summary>

if nothing in the executable references a symbol in `lidar.o`, the linker never pulls that object file out of the static library, so its namespace-scope initializer never runs and the registration never happens. the build succeeds; the type is simply missing at run time. the robust fix is explicit registration: a `register_builtin_sensors(registry)` function called from `main`, which also makes the set of sensors visible in one place.

</details>

<details>
<summary>answer 4: a hot-path seam</summary>

make the filter a template parameter constrained by a concept: the call becomes direct and inlinable, which also lets the compiler vectorize the loop around it. you give up choosing the filter at run time and storing different filters behind one type; if both are needed, keep the virtual interface at a coarser grain (one call per block of samples) and use the template inside the block.

</details>

<details>
<summary>answer 5: callbacks under a lock</summary>

first, reentrancy: a slot that subscribes, unsubscribes (for example a one-shot handler that resets its own token), or emits on the same signal locks the same non-recursive `std::mutex` again, which is undefined behavior and in practice usually a deadlock. second, lock-order deadlocks across threads ([day 86](#day-86)): the slot may take its own mutex while thread B, holding that mutex, tries to subscribe and waits for the signal's mutex. a third, softer problem is latency: a slow slot blocks every thread that wants to subscribe or emit.

</details>

<details>
<summary>mini exercise answer</summary>

the transport becomes a narrow interface owned by the uploader's module ([day 90](#day-90)'s DIP), and the clock a `std::function` (one operation, [day 91](#day-91)). the production `main` would pass an adapter over the real HTTP client and `std::chrono::system_clock::now`.

the complete refactored class, the fake, and the test are in "going deeper" below.

notice what the fake lets you test that the original could not: the failure path, and the exact payload, both without a network. note also the borrowed `BatchSink&`: the sink must outlive the uploader, which is natural when both are created in `main`.

</details>

#### connections

design is where everything earlier in the course meets: ownership decides how components are wired ([day 28](#day-28)), lifetimes decide whether an observer or an injected reference is safe ([day 08](#day-08)), and the polymorphism mechanisms decide what a seam costs. the next module looks at the remaining design choices with long-term consequences: which kind of polymorphism to use, how to keep an API stable once it ships, and two C++20 features that change how code is organized, modules and coroutines.

#### going deeper (optional)

##### the uploader, refactored and tested

```cpp complete
#include <cassert>
#include <chrono>
#include <functional>
#include <string>
#include <string_view>
#include <vector>

class BatchSink {
public:
    virtual ~BatchSink() = default;
    virtual bool send(std::string_view payload) = 0;   // true on success
};

using WallClock = std::function<std::chrono::system_clock::time_point()>;

class TelemetryUploader {
public:
    TelemetryUploader(BatchSink& sink, WallClock now) : sink_(sink), now_(std::move(now)) {}
    void record(std::string line) { buffer_.push_back(std::move(line)); }
    void flush() {
        if (buffer_.empty()) return;
        if (sink_.send(serialize(now_()))) buffer_.clear();
    }
    std::size_t pending() const { return buffer_.size(); }
private:
    std::string serialize(std::chrono::system_clock::time_point t) const {
        std::string out = std::to_string(t.time_since_epoch().count()) + '\n';
        for (const auto& l : buffer_) out += l + '\n';
        return out;
    }
    BatchSink& sink_;
    WallClock now_;
    std::vector<std::string> buffer_;
};

struct FakeSink final : BatchSink {
    bool succeed = false;
    std::vector<std::string> sent;
    bool send(std::string_view payload) override {
        sent.emplace_back(payload);
        return succeed;
    }
};

int main() {
    FakeSink sink;
    TelemetryUploader up(sink, [] { return std::chrono::system_clock::time_point{}; });
    up.record("battery=24.1");
    up.flush();                                        // sink fails
    assert(up.pending() == 1 && sink.sent.size() == 1);
    sink.succeed = true;
    up.flush();                                        // sink succeeds
    assert(up.pending() == 0 && sink.sent.back() == "0\nbattery=24.1\n");
}
```

[back to the curriculum map](#curriculum)

---

<a id="module-abstractions"></a>

## module 15: polymorphism choices, APIs, modules, and coroutines

choosing a polymorphism mechanism, type erasure, interfaces that stay correct and stable, modules, and coroutines.

<a id="day-97"></a>

### day 97: one call, many types: choosing a polymorphism mechanism

**module 15:** polymorphism choices, APIs, modules, and coroutines · **reading time:** about 7 minutes · **standard:** C++20  
**objective:** compare virtual functions, templates with concepts, `std::variant`, and type erasure, and use static polymorphism where the choice is made at compile time  
**builds on:** [day 93](#day-93) (patterns in modern C++: strategy), [day 61](#day-61) (writing your own concepts), [day 54](#day-54) (closed sets and open sets: variant state machines and `std::any`)

#### the idea

a telemetry recorder must store a mixed stream of records: IMU samples from your team, battery states from the power team, GPS fixes from a vendor library you cannot modify. each can render itself as text. how do you put them in one `std::vector` and call "render" on each?

"make them inherit from `Record`" is the reflex, and it fails on the vendor type straight away. C++ gives you at least four ways to get "one call, many types", and they differ in who has to know about whom, when the choice is made, and what you pay for it.

#### understanding the concept

| | virtual functions | templates + concepts | `std::variant` | type erasure |
|---|---|---|---|---|
| set of types | open | open | closed (listed in the variant) | open |
| user types must inherit | yes | no | no | no |
| semantics | reference (via pointer to base) | value | value | value |
| one heterogeneous container | yes, of pointers | no | yes | yes |
| call mechanism | indirect call, usually through a vtable | direct, inlinable | `std::visit` dispatch (implementation-specific, often a jump table) | indirect call inside the wrapper |
| typical cost to watch | heap allocation per object, no inlining | compile time, code size per instantiation | adding a type touches every visitor | allocation per object unless small-buffer optimized, a clone per copy |
| across a shared-library boundary | the standard plugin mechanism | not applicable, code is instantiated in the caller | adding an alternative changes the type and its layout | possible if the wrapper's layout is fixed |

none of the "call mechanism" entries is a performance verdict. an indirect call costs a load and a branch that may be predicted well or badly, and it blocks inlining, which often matters more than the call itself. whether any of that shows up depends on how much work each call does. measure with a profiler on the real workload before choosing on speed.

**static polymorphism** resolves the call at compile time. the old tool is CRTP (the curiously recurring template pattern): a base class template that casts `this` to the derived type. in C++20, a concept plus a free function template often does the same job with less ceremony, and C++23's deducing `this` (an explicit object parameter, `this const auto& self`) removes most of CRTP's boilerplate. that is C++23 only.

#### in code

**static polymorphism: CRTP versus a concept.** both share the "raw times scale" logic without a virtual call.

```cpp complete
#include <concepts>

// CRTP: the base knows the derived type through the template argument
template <typename Derived>
class SensorBase {
public:
    double read_si() const {
        const auto& self = static_cast<const Derived&>(*this);
        return self.raw() * self.scale();
    }
};
class Thermistor : public SensorBase<Thermistor> {
public:
    int raw() const { return 2048; }
    double scale() const { return 0.05; }
};

// C++20 alternative: no base class at all
template <typename S>
concept ScaledSensor = requires(const S& s) {
    { s.raw() } -> std::integral;
    { s.scale() } -> std::floating_point;
};
double read_si(const ScaledSensor auto& s) { return s.raw() * s.scale(); }

// Thermistor{}.read_si() and read_si(Thermistor{}) both return 102.4
```

`SensorBase<Thermistor>` and `SensorBase<StrainGauge>` are unrelated types, so CRTP gives shared code, not a common type to store. either way you cannot put both sensors in one container.

#### in practice

in a robotics stack the four options usually coexist, each where it fits:

- **plugins loaded at run time** (a `dlopen`'d planner or driver) use a virtual interface plus an `extern "C"` factory function. templates cannot cross that boundary, and a virtual interface is the most widely understood ABI contract, as long as you never change the virtual functions of a released interface (even adding one can shift vtable slots, which is implementation-specific); publish a new versioned interface instead.
- **messages on an internal bus** with a fixed, versioned set of types are a `std::variant`. the closed set is a feature: the compiler can tell you about every visitor you forgot to update ([day 54](#day-54)).
- **hot numerical kernels** take their policies as template parameters constrained by concepts, so filters and interpolators inline into the loop.
- **task queues and callbacks** store `std::function` or a small custom erased wrapper, because the queue must hold arbitrary callables by value.

#### watch out for

**the CRTP copy-paste bug.** the base trusts its template argument completely:

```cpp
class StrainGauge : public SensorBase<Thermistor> {   // BUG: copied from Thermistor
public:
    int raw() const { return 512; }
    double scale() const { return 0.2; }
};
```

`StrainGauge{}.read_si()` compiles and casts a `StrainGauge` to `const Thermistor&`, which it is not: undefined behavior. a common guard is a private constructor in the base with `friend Derived;`, so only the class named in the template argument can construct it, and the mistake fails to compile. the concept-based version has no such hole, which is one more reason to prefer it in C++20.

#### the takeaway

choose by the shape of the problem: virtual functions for open sets behind pointers and binary boundaries, templates and concepts for compile-time choice and speed, `std::variant` for closed sets, and type erasure for open sets with value semantics; measure before choosing on performance.

#### optional challenge

the telemetry recorder from the opening must store IMU samples (your type), battery states (another team's type, which you can change), and GPS fixes (a vendor type you cannot change), by value, in one container, and new record types are added every few months. which of the four options fits, and why do the others not?

<details>
<summary>answer</summary>

type erasure. a virtual base class fails on the vendor type, which cannot inherit from it, and forces pointer semantics. templates and concepts give no single type to store in one container. a `std::variant` could hold the three types, but the set keeps growing, and every addition changes the variant type and every visitor; that is acceptable for a protocol you own, less so for an open-ended set. type erasure keeps an open set, value semantics, and requires nothing of the stored types except the operations the wrapper uses, which [day 98](#day-98) builds.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-98"></a>

### day 98: type erasure: value semantics without inheritance

**module 15:** polymorphism choices, APIs, modules, and coroutines · **reading time:** about 9 minutes · **standard:** C++20  
**objective:** implement a small type-erased wrapper with an internal concept and model, and know its costs compared with a plain virtual interface  
**builds on:** [day 97](#day-97) (one call, many types: choosing a polymorphism mechanism), [day 38](#day-38) (lambdas that outlive their scope: callbacks and `std::function`), [day 25](#day-25) (the rule of zero)

#### the idea

`std::function<void()>` holds a lambda, a function pointer, or your own function object, and none of them inherits from anything. you store them by value, copy them, and put them in a vector. the trick behind it is not specific to callables: any set of operations can be wrapped this way, which lets a library accept types it has never seen without asking them to derive from its base class.

#### understanding the concept

**type erasure** is how `std::function` and `std::any` work. a template constructor sees the concrete type once, wraps it in an internal "model" object that implements a private interface, and stores it behind a pointer of fixed type. after construction the wrapper's type no longer mentions the concrete type: it has been erased. inheritance still exists, but it is hidden inside the wrapper instead of imposed on users.

#### in code

**hand-written type erasure.** the users' types implement nothing; they only need a free function `to_text` that argument-dependent lookup can find, which also works for the vendor type because you can write that function yourself in its namespace.

```cpp complete
#include <concepts>
#include <memory>
#include <string>
#include <utility>

template <typename T>
concept TextRenderable = requires(const T& t) {
    { to_text(t) } -> std::convertible_to<std::string>;
};

class Record {
public:
    template <TextRenderable T>
    Record(T value) : self_(std::make_unique<Model<T>>(std::move(value))) {}

    Record(const Record& other) : self_(other.self_->clone()) {}
    Record& operator=(const Record& other) { return *this = Record(other); }
    Record(Record&&) noexcept = default;
    Record& operator=(Record&&) noexcept = default;

    friend std::string to_text(const Record& r) { return r.self_->render(); }

private:
    struct Concept {                                    // private interface
        virtual ~Concept() = default;
        virtual std::string render() const = 0;
        virtual std::unique_ptr<Concept> clone() const = 0;
    };
    template <typename T>
    struct Model final : Concept {                      // one per stored type
        explicit Model(T v) : value(std::move(v)) {}
        std::string render() const override { return to_text(value); }
        std::unique_ptr<Concept> clone() const override { return std::make_unique<Model>(*this); }
        T value;
    };
    std::unique_ptr<Concept> self_;
};
```

the virtual function is named `render`, not `to_text`, on purpose: inside `Model`, an unqualified call to `to_text` would otherwise find the member first, and finding a class member suppresses argument-dependent lookup, so the user's free function would never be considered.

using it:

```cpp
#include <iostream>
#include <vector>

namespace imu {
struct Sample { int seq; };
std::string to_text(const Sample& s) { return "imu #" + std::to_string(s.seq); }
}
namespace vendor {                                      // pretend we cannot edit this struct
struct GpsFix { int sats; };
}
namespace vendor {                                      // but we can add a function next to it
std::string to_text(const GpsFix& g) { return "gps sats=" + std::to_string(g.sats); }
}

int main() {
    std::vector<Record> records{imu::Sample{41}, vendor::GpsFix{9}};
    records.push_back(records.front());                  // value semantics: deep copy
    for (const auto& r : records) std::cout << to_text(r) << '\n';
    // prints: imu #41
    //         gps sats=9
    //         imu #41
}
```

adding a function to a vendor's namespace is your code, in your translation units, so it is fine; adding declarations to namespace `std` is not (with narrow exceptions such as specializing certain templates for your own types).

#### in practice

Sean Parent's line "inheritance is the base class of evil" is about the first option leaking into everything: if the interface is a base class, every user type must inherit from it, objects live behind pointers, and copying needs a `clone()` hierarchy. type erasure keeps the inheritance private and gives users plain value types.

the same structure appears wherever a library must accept arbitrary user types by value: `std::function` for callables, `std::any` for anything copyable, custom wrappers for "anything drawable", "anything serializable", or "anything that can be a task". writing one is a deliberate trade: forty lines of wrapper code, written once, against a constraint imposed on every user type forever.

#### watch out for

**type erasure is not free and not always worth it.** the wrapper above allocates once per stored object and once per copy, every call is an indirect call, and debuggers show you `Model<imu::Sample>` frames you did not write. real implementations often add a **small buffer optimization**: store small objects inside the wrapper itself and fall back to the heap for large ones. whether and when `std::function` does this is an implementation detail (buffer sizes and conditions differ between libstdc++, libc++, and MSVC), so do not design around it; count allocations if it matters ([day 109](#day-109)). also note that the wrapper requires copyable types; a move-only callable needs a move-only wrapper, which the standard only provides in C++23 (`std::move_only_function`).

if you own all the types, need reference semantics anyway, and the set is open, a ten-line virtual interface is easier to read and debug than a forty-line erased wrapper. reach for type erasure when you need value semantics or must accept types that cannot inherit from your base.

#### the takeaway

type erasure hides inheritance inside a wrapper: a template constructor captures the concrete type in a private model, and users get plain value types; use it when you need value semantics or must accept types that cannot inherit, and prefer a simple virtual interface otherwise.

#### optional challenge

`Record`'s converting constructor takes `T` by value and is constrained by `TextRenderable`. `Record` itself satisfies `TextRenderable` (its hidden friend `to_text` is found by ADL). so why doesn't `Record copy = records.front();` wrap a `Record` inside a `Model<Record>`?

<details>
<summary>answer</summary>

because the copy constructor wins. for `Record copy = records.front();` the argument is a `Record` lvalue. overload resolution looks at the copy constructor `Record(const Record&)` and at the constructor template, but the standard says a constructor template is never instantiated to produce a constructor whose first parameter is the class type by value (that signature would be a broken copy constructor), so the template is not a viable candidate here. if the constructor took `T&&` (a forwarding reference) instead, a non-const lvalue `Record` would deduce `T = Record&`, the template would be a better match than `const Record&`, and copying would try to wrap a `Record` inside a `Model<Record>`: at best a silent extra layer of allocation and indirection per copy, and with this concept GCC 12 reports a recursive constraint error instead. that is why forwarding constructors in erased wrappers need an explicit `!std::same_as<std::remove_cvref_t<T>, Record>` constraint.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-99"></a>

### day 99: designing APIs that are hard to misuse

**module 15:** polymorphism choices, APIs, modules, and coroutines · **reading time:** about 6 minutes · **standard:** C++20  
**objective:** push an API's contract into its types with strong types, enums, views, and explicit error channels, so wrong calls fail to compile  
**builds on:** [day 91](#day-91) (dependency injection: passing collaborators in), [day 65](#day-65) (`std::span`: views over contiguous memory), [day 50](#day-50) (choosing an error-handling strategy), [day 67](#day-67) (defaulted comparisons and the spaceship operator)

#### the idea

```cpp
bool move_joint(int joint, double position, double velocity, double timeout);

move_joint(2, 1.5, 0.5, 30);    // radians? degrees? 30 seconds or 30 ms? did it fail?
```

this compiles whether you swap position and velocity, pass degrees, or ignore the result. every one of those mistakes is a bug that only shows up on the robot. a good API makes the correct call easy to write and the wrong call hard to write, ideally impossible to compile. today is about the tools C++ gives you for that, and about the extra promise a library makes once it ships as a binary.

#### understanding the concept

an API is a contract with three parts. **preconditions** are what the caller must guarantee (the joint index exists, the span is non-empty). **postconditions** are what the function guarantees on success (the joint reached the target within tolerance). **invariants** are what is always true of an object between calls (a `Trajectory` is time-ordered). C++20 has no language feature for contracts; C++26 adds `pre`, `post`, and `contract_assert`, but in C++20 you have, in decreasing order of strength:

1. **types** that make violations unrepresentable: strong types, enums instead of `bool` flags, `std::span` instead of pointer plus length.
2. **construction** that establishes invariants (a constructor that validates, or a factory returning `std::optional`).
3. **assertions** for preconditions you cannot encode in types.
4. **documentation** for the rest.

the signature itself is part of the contract. the ownership rules from [day 28](#day-28) and the view types from the C++17 and C++20 modules give a compact vocabulary:

| parameter | tells the caller |
|---|---|
| `T` (cheap or sink) | "I take my own copy" |
| `const T&` | "I read it during the call and keep nothing" |
| `std::string_view`, `std::span<const T>` | "I borrow a sequence for the duration of the call" |
| `T*` | "may be null, I do not own it" |
| `std::unique_ptr<T>` by value | "ownership transfers to me" |
| `std::shared_ptr<T>` by value | "I will share ownership beyond this call" |

then choose **one error channel per kind of failure** and use it consistently across the API ([day 50](#day-50)): exceptions for failures the immediate caller cannot handle, return values (`std::optional`, a `std::variant` or small result type, an error code) for expected outcomes such as a sensor timeout. mark those return types or functions `[[nodiscard]]` so ignoring them is a warning. (`std::expected` is the standard result type in C++23.)

#### in code

**strong types and enums at the call site.**

```cpp complete
#include <chrono>
#include <compare>
#include <cstdint>
#include <optional>

template <typename Tag>
struct Quantity {
    double value;
    constexpr explicit Quantity(double v) : value(v) {}
    friend constexpr Quantity operator+(Quantity a, Quantity b) { return Quantity(a.value + b.value); }
    friend constexpr auto operator<=>(Quantity, Quantity) = default;
};
using Radians          = Quantity<struct RadiansTag>;
using RadiansPerSecond = Quantity<struct RadiansPerSecondTag>;

enum class JointId : std::uint8_t {};
enum class MoveError { unreachable, timeout, estop_active };

struct MoveRequest {
    Radians target;
    RadiansPerSecond max_speed;
    std::chrono::milliseconds timeout;
};

[[nodiscard]] std::optional<MoveError> move_joint(JointId joint, const MoveRequest& req);

// move_joint(JointId{2}, {Radians(1.5), RadiansPerSecond(0.5), std::chrono::seconds(30)});
// move_joint(JointId{2}, {RadiansPerSecond(0.5), Radians(1.5), ...});  // does not compile
// move_joint(2, ...);                                                    // does not compile
```

each `struct ...Tag` declared inside the template argument creates a distinct type, so `Radians` and `RadiansPerSecond` do not mix. `std::chrono` already does this for time, including safe conversion from seconds to milliseconds. for real unit algebra (meters divided by seconds giving meters per second) use a units library such as mp-units rather than growing this template. the `JointId{2}` form uses C++17's rule that an enum with a fixed underlying type can be list-initialized from an integer, while `JointId j = 2;` is still an error.

one honest weakness: `std::optional<MoveError>` reads backwards (an engaged optional means failure). a small result type with a named `ok()` member, or C++23 `std::expected<void, MoveError>`, says it better.

#### in practice

then there is **Hyrum's law**: with enough users, every observable behavior of your API will be depended on by somebody, whether or not you promised it. if `get_detections()` happened to return detections sorted by range for three years, someone's tracker now assumes it, and "unsorted" becomes a breaking change. document what is guaranteed, and where order or timing is not guaranteed, consider making that visible early (some libraries deliberately randomize iteration order for this reason).

#### watch out for

**not every class needs this.** pimpl, strong types, and result types each add code. use them on boundaries: public library headers, hardware interfaces, and functions where swapping two arguments is plausible. internal helpers with one caller can stay plain.

#### the takeaway

push contracts into types first, assertions second, and comments last; make ownership, borrowing, and failure visible in the signature, and pick one error channel per kind of failure.

#### optional challenge

list what is wrong with this public function from a deployment tool, and sketch a better signature: `bool deploy(char* host, int port, double timeout, bool force, bool dry_run);`

<details>
<summary>answer</summary>

`char*` says nothing about ownership or null termination, and non-const suggests the function may modify the string: take `std::string_view`. `double timeout` has no unit: use `std::chrono::milliseconds` (or `seconds`). two adjacent `bool` flags are easy to swap and unreadable at the call site (`deploy(h, 22, 30, true, false)`): use enums such as `enum class Mode { apply, dry_run }` and `enum class Conflict { abort, overwrite }`, or a small options struct with designated initializers (C++20). the `bool` return hides why it failed and is easy to ignore: return a `[[nodiscard]]` result carrying an error enum and message. port could be a `std::uint16_t` or a strong `Port` type. for example: `[[nodiscard]] DeployResult deploy(std::string_view host, std::uint16_t port, const DeployOptions& opts);` with `DeployOptions{.timeout = 30s, .mode = Mode::dry_run}` at the call site.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-100"></a>

### day 100: API and ABI stability: pimpl and deprecation

**module 15:** polymorphism choices, APIs, modules, and coroutines · **reading time:** about 8 minutes · **standard:** C++20  
**objective:** distinguish API from ABI stability, use the pimpl idiom as a compile-time and binary firewall, and evolve an interface without breaking callers  
**builds on:** [day 99](#day-99) (designing APIs that are hard to misuse), [day 90](#day-90) (coupling, cohesion, and physical design), [day 26](#day-26) (exclusive ownership with `std::unique_ptr`)

#### the idea

a library that is compiled together with its users can change freely, as long as the source still compiles. a library shipped as a binary, a `.so` or `.dll` that integrators link against without recompiling, makes a much stricter promise: the *layout* of every public class, the set of its virtual functions, and the code of every inline function are now part of the contract. most of the techniques in this lesson exist to keep that promise without freezing the code.

#### understanding the concept

finally, separate **API** stability (source code that compiled against version 1 still compiles against version 2) from **ABI** stability (binaries built against version 1 still link and run against version 2's shared library). ABI is much more fragile: changing a class's size, the order of its members, its virtual functions, or an inline function's body breaks it, even when the source-level API is unchanged.

#### in code

**the pimpl idiom: a compile-time and ABI firewall.**

```cpp complete
// lidar_driver.h: the only thing clients see
#pragma once
#include <cstddef>
#include <memory>
#include <span>
#include <string_view>

class LidarDriver {
public:
    explicit LidarDriver(std::string_view device);
    ~LidarDriver();                                   // declared here, defined in the .cpp
    LidarDriver(LidarDriver&&) noexcept;
    LidarDriver& operator=(LidarDriver&&) noexcept;

    [[nodiscard]] std::size_t read_scan(std::span<float> ranges_out);
    [[nodiscard]] bool healthy() const;

private:
    struct Impl;                                      // incomplete in every client
    std::unique_ptr<Impl> impl_;
};
```

```cpp external
// lidar_driver.cpp: vendor SDK headers and private state live here
#include "lidar_driver.h"
#include <algorithm>
#include <string>
#include <vector>

struct LidarDriver::Impl {
    std::string device;
    std::vector<float> last_scan = std::vector<float>(360, 5.0f);
    int error_count = 0;
};

LidarDriver::LidarDriver(std::string_view device)
    : impl_(std::make_unique<Impl>(Impl{std::string(device)})) {}
LidarDriver::~LidarDriver() = default;                // Impl is complete here
LidarDriver::LidarDriver(LidarDriver&&) noexcept = default;
LidarDriver& LidarDriver::operator=(LidarDriver&&) noexcept = default;

std::size_t LidarDriver::read_scan(std::span<float> out) {
    const std::size_t n = std::min(out.size(), impl_->last_scan.size());
    std::copy_n(impl_->last_scan.begin(), n, out.begin());
    return n;
}
bool LidarDriver::healthy() const { return impl_->error_count == 0; }
```

why the out-of-line destructor? `std::unique_ptr<Impl>` deletes through `std::default_delete<Impl>`, and the program is ill-formed if `Impl` is incomplete at that point. if you let the compiler define `~LidarDriver` implicitly, it is defined inline in every client translation unit, where `Impl` is incomplete, and compilation fails. declaring the destructor (and the move operations, which also need to destroy an `Impl`) in the header and defaulting them in the `.cpp` puts the definitions where `Impl` is complete.

what you get: clients never include the vendor SDK, editing `Impl` recompiles one file, and `sizeof(LidarDriver)` stays one `unique_ptr` regardless of private state, so adding a private member does not change the class layout that client binaries were compiled against. what you pay: one heap allocation per object, an extra indirection on every member access, and no inlining of member functions into callers (unless link-time optimization does it).

**evolving an API without breaking callers.**

```cpp complete
#include <cstddef>
#include <span>

class LidarDriverV2 {
public:
    [[nodiscard]] std::size_t read_scan(std::span<float> ranges_out);

    [[deprecated("use read_scan(std::span<float>); removed in 3.0")]]
    int read_scan(float* out, int max_count) {
        return static_cast<int>(read_scan(std::span<float>(out, static_cast<std::size_t>(max_count))));
    }
};
```

the old overload keeps source compatibility for a release cycle, warns at every call site, and forwards to the new implementation so there is only one code path.

#### in practice

a radar vendor ships `libradar.so` to integrators who cannot recompile when it updates. that makes every public header a binary contract. typical rules on such teams: public classes are pimpl or abstract interfaces with a factory, no inline functions that touch private data, no standard-library types across the boundary unless every party uses the same toolchain and standard library build (libstdc++'s `std::string` changed layout in GCC 5, which is why it ships a dual ABI), and a symbol-visibility policy that exports only the intended API.

#### watch out for

**`const` does not propagate through pimpl.** inside `healthy() const`, `impl_` is a `const std::unique_ptr<Impl>`, but `*impl_` is a non-const `Impl&`, so a const member function can modify private state without a compiler complaint. add a pair of private accessors (`Impl& impl()` and `const Impl& impl() const`) and use them everywhere instead of `impl_` directly. also, a moved-from `LidarDriver` has a null `impl_`; calling `read_scan` on it dereferences null (undefined behavior), so document that a moved-from driver may only be destroyed or assigned to, or check in every member.

#### the takeaway

a shipped shared library promises an ABI, which is far stricter than an API: hide private state behind pimpl or abstract interfaces, keep inline code out of public headers, and evolve through deprecation rather than silent change.

#### optional challenge

`libradar.so` exports a class `Tracker` that is *not* pimpl. which of these changes break binaries compiled against the previous version?

1. adding a private data member
2. adding a member to the private `Impl` struct of another, pimpl class
3. adding a new virtual function at the end of `Tracker`'s existing ones
4. adding a new non-virtual, non-inline member function
5. changing the body of an inline member function defined in the header

<details>
<summary>answer</summary>

(1) breaks: `sizeof(Tracker)` and possibly member offsets change, and clients allocated the old size. (2) is safe: only the library sees `Impl`. (3) is risky: it changes the vtable, which breaks any client class that derives from `Tracker` (its own virtual functions shift) and is implementation-specific even without derivation; treat it as breaking. (4) is safe: it adds a symbol without changing existing ones. (5) is the subtle one: old clients keep the old inline code compiled into their own binaries, so two versions of the function now coexist, which is an ODR problem and a behavior mismatch, not a link error.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-101"></a>

### day 101: C++20 modules: a practical first look

**module 15:** polymorphism choices, APIs, modules, and coroutines · **reading time:** about 5 minutes · **standard:** C++20  
**objective:** read and write a named module with interface and implementation units, and judge when the tooling makes adoption worthwhile  
**builds on:** [day 02](#day-02) (linkage and the one definition rule), [day 90](#day-90) (coupling, cohesion, and physical design)

#### the idea

`#include` is a sixty-year-old idea: paste the text of another file here. every translation unit reparses the same headers, macros leak from one header into everything included after it, and the one definition rule quietly depends on every pasted copy being identical. C++20 modules replace pasting with importing a compiled interface. the language feature is real and usable; the tooling around it is still arriving, and both facts matter for when you adopt it.

#### understanding the concept

**modules.** [day 01](#day-01) showed what `#include` really is: pasting text. every translation unit reparses the same headers, macros defined in one header leak into everything included after it, and the one definition rule depends on every copy of a header being identical. a named module is compiled once into a binary module interface (a compiler-specific file), and importers read that instead of reparsing source. only what you `export` is visible to importers; macros defined in a named module never leak out of it, and code that imports it is not affected by macros the importer defined earlier.

the vocabulary you need:

- **module interface unit**: starts with `export module name;` and declares what is exported.
- **module implementation unit**: starts with `module name;` and implicitly sees the interface, including its non-exported declarations.
- **global module fragment**: a `module;` line before the module declaration, where legacy `#include`s go so they do not become part of the module.
- **header units**: `import <vector>;` treats a header as an importable unit (it does export macros). compiler support is uneven.

#### in code

**a small module.** file extensions and compiler flags vary by toolchain (`.cppm`, `.ixx`, `.mpp`; GCC before 14 needs the experimental `-fmodules-ts`).

```cpp external
// geometry.cppm: module interface unit
export module robotics.geometry;

double square(double v) { return v * v; } // not exported: visible only inside the module

export namespace geo {
struct Vec2 { double x, y; };
double norm(Vec2 v);                      // exported declaration
}
```

```cpp external
// geometry.cpp: module implementation unit
module;                                   // global module fragment: legacy includes
#include <cmath>
module robotics.geometry;                 // implicitly imports the interface

namespace geo {
double norm(Vec2 v) { return std::sqrt(square(v.x) + square(v.y)); }
}

// main.cpp: a consumer
#include <cstdio>
import robotics.geometry;

int main() { std::printf("%.1f\n", geo::norm({3.0, 4.0})); }   // prints: 5.0
// square(2.0) here would not compile: it is not exported
```

#### in practice

**modules today.** named modules need a build system that scans sources for `import` and `export module` before compiling, because a module must be built before its importers. CMake supports this from 3.28 with the Ninja and Visual Studio generators, on recent compilers (CMake documents MSVC 19.34+, Clang 16+, and GCC 14+). binary module interfaces are compiler- and flag-specific, so a library still ships source interfaces, not BMIs. `import std;` is C++23, though some toolchains offer it as an extension in C++20 mode. a sensible adoption path: new leaf libraries as modules, internal code first, public headers kept until every consumer's toolchain supports modules. do not expect it to fix a build dominated by template instantiation or link time; measure where your build time goes first.

#### watch out for

**includes belong in the global module fragment.** a header included *after* the module declaration becomes part of the module's purview:

```cpp external
export module robotics.geometry;
#include <cmath>          // BUG: <cmath>'s declarations now belong to this module
```

the declarations from that header are attached to `robotics.geometry`, which can conflict with the same header included normally elsewhere in the program and produces confusing errors or ODR problems. legacy includes go between `module;` and the module declaration, exactly as in `geometry.cpp`; `import` declarations and the module's own code come after it.

#### the takeaway

modules fix textual inclusion and macro leakage, but adoption is gated by build-system and compiler support, so introduce them from the leaves inward and measure where your build time goes before expecting a speedup.

#### optional challenge

in `main.cpp`, which of these compile: `geo::norm(v)`, `geo::Vec2{1, 2}`, `square(2.0)`, `std::sqrt(2.0)` (with no `#include <cmath>` in `main.cpp`)?

<details>
<summary>answer</summary>

`geo::norm` and `geo::Vec2` compile: both are declared inside the `export namespace geo` block. `square` does not: it is not exported, so it is visible only inside the module. `std::sqrt` does not either: `<cmath>` was included in the implementation unit's global module fragment, and nothing from it is exported to importers. unlike an `#include`, importing a module brings in exactly what the module exports, so `main.cpp` must include `<cmath>` itself if it needs it.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-102"></a>

### day 102: coroutines: functions that suspend

**module 15:** polymorphism choices, APIs, modules, and coroutines · **reading time:** about 5 minutes · **standard:** C++20  
**objective:** read and use a coroutine that yields values, explain where its state lives, and avoid parameters that dangle across suspension points  
**builds on:** [day 16](#day-16) (RAII: let scope do the cleanup), [day 08](#day-08) (temporaries, lifetime extension, and dangling references), [day 37](#day-37) (lambdas are objects: closures and captures)

#### the idea

a radar steers its beam in a serpentine raster: left to right on even rows, right to left on odd rows. as an iterator, that needs the row, the column, and the direction stored as members, plus an `increment()` that reconstructs where the two nested loops were. as a coroutine, it is two nested loops with a `co_yield` in the middle. coroutines let a function pause and resume, so a state machine can be written as straight-line code, and the compiler keeps the state for you.

#### understanding the concept

**coroutines.** a function becomes a coroutine when its body uses `co_await`, `co_yield`, or `co_return`. its state (the parameters, the locals that live across a suspension, and a *promise object*) lives in a **coroutine frame**, which is usually heap-allocated; the compiler may elide that allocation when it can prove the frame's lifetime is nested in the caller's, but nothing guarantees it. C++20 supplies only the machinery: the return type must provide a nested `promise_type` that tells the compiler what to do at start, at each `co_yield`, at the end, and on exceptions. the standard ships no ready-made generator or task type in C++20 (`std::generator` arrives in C++23).

`co_await x` asks an *awaiter* three questions: `await_ready()` (can we skip suspending?), `await_suspend(handle)` (we are suspended; who resumes us, and when?), and `await_resume()` (the result of the expression). `std::suspend_always` and `std::suspend_never` are the two trivial awaiters.

#### in code

`Generator<T>` below is a small generator type; [day 103](#day-103) builds it line by line. using it looks like this:

```cpp
#include <iostream>

struct Beam { int elevation, azimuth; };

Generator<Beam> serpentine_scan(int rows, int cols) {    // parameters copied into the frame
    for (int el = 0; el < rows; ++el) {
        const bool forward = (el % 2 == 0);
        for (int i = 0; i < cols; ++i)
            co_yield Beam{el, forward ? i : cols - 1 - i};
    }
}

int main() {
    auto scan = serpentine_scan(2, 3);
    while (scan.next())
        std::cout << '(' << scan.value().elevation << ',' << scan.value().azimuth << ") ";
    // prints: (0,0) (0,1) (0,2) (1,2) (1,1) (1,0)
}
```

as an iterator class this needs `el`, `i`, and `forward` as members plus an `increment()` that reconstructs where the loops were. the coroutine keeps that state in its frame and lets the nested loops stay nested loops.

#### in practice

**coroutines today.** they shine for asynchronous I/O (a telemetry uploader written as `co_await socket.async_write(...)` in sequence instead of nested callbacks), protocol state machines, and lazy sequences. in practice you use a library's types: Asio's `awaitable`, folly's coro, or the generator in your toolchain's C++23 mode. writing your own `task` type with correct continuation, cancellation, and thread handoff is much harder than the generator above.

#### watch out for

**reference parameters dangle across suspension points.** the frame copies parameters, but copying a reference copies the reference.

```cpp
Generator<char> letters(const std::string& s) { for (char c : s) co_yield c; }

auto g = letters("radar");   // BUG: the temporary std::string dies at the end of this line
while (g.next()) { }         // undefined behavior: the frame refers to a destroyed string
```

the fix is to take the parameter by value (`std::string s`), so the frame owns a copy. the same applies to `std::string_view`, `std::span`, and lambda coroutines: a lambda's captures live in the lambda object, not the frame, so the lambda object must outlive the coroutine it started.

#### the takeaway

a coroutine keeps its state in a frame that outlives each suspension, so take parameters by value, let an RAII return type own the frame, and use a library's coroutine types for asynchronous work.

#### optional challenge

`auto scan = serpentine_scan(rows, cols);` is called with two local `int` variables, and the caller then changes `rows` before calling `scan.next()`. does the scan see the new value?

<details>
<summary>answer</summary>

no. parameters of a coroutine are copied (or moved) into the coroutine frame when it is called, and the body uses those copies. because the parameters are taken by value, later changes to the caller's variables do not affect the scan. had they been `const int&`, the frame would hold references to the caller's variables: the scan would see the change, and if those variables went out of scope before the scan finished, it would read dangling references.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-103"></a>

### day 103: inside a coroutine: writing a generator type

**module 15:** polymorphism choices, APIs, modules, and coroutines · **reading time:** about 5 minutes · **standard:** C++20  
**objective:** implement a minimal generator by providing a promise_type, and explain each step the compiler takes when a coroutine starts, yields, and finishes  
**builds on:** [day 102](#day-102) (coroutines: functions that suspend), [day 21](#day-21) (moving: transferring resources instead of copying them)

#### the idea

C++20 ships the coroutine *machinery* and almost no coroutine *types*: there is no `std::generator` until C++23 and no standard task type at all. that makes the contract between the compiler and a coroutine's return type worth understanding once, even if you will mostly use a library: it is what you read in a debugger, what decides when a coroutine runs, and what owns its frame.

#### understanding the concept

walk through it once. calling a coroutine allocates the frame, constructs the promise, calls `get_return_object()` (which is what the caller receives), then `co_await`s `initial_suspend()`. ours suspends, so nothing runs until the first `next()`. each `co_yield v` becomes `co_await promise.yield_value(v)`, which stores the value and suspends. falling off the end calls `return_void()` and suspends at `final_suspend()`, so `done()` becomes true and the `Generator` destructor frees the frame. (this version requires `T` to be default-constructible; a production one would store a pointer or `std::optional`.)

#### in code

**a hand-written generator.** this is the whole contract between the compiler and a generator type.

```cpp complete
#include <coroutine>
#include <utility>

template <typename T>
class Generator {
public:
    struct promise_type {
        T current{};
        Generator get_return_object() {
            return Generator(std::coroutine_handle<promise_type>::from_promise(*this));
        }
        std::suspend_always initial_suspend() noexcept { return {}; }  // start lazily
        std::suspend_always final_suspend() noexcept { return {}; }    // keep frame until we destroy it
        std::suspend_always yield_value(T v) {                         // co_yield v
            current = std::move(v);
            return {};
        }
        void return_void() noexcept {}
        void unhandled_exception() { throw; }  // rethrows out of resume() into next()
    };

    explicit Generator(std::coroutine_handle<promise_type> h) : h_(h) {}
    Generator(Generator&& o) noexcept : h_(std::exchange(o.h_, {})) {}
    Generator& operator=(Generator&&) = delete;
    ~Generator() { if (h_) h_.destroy(); }         // RAII for the frame

    bool next() {                                  // run to the next co_yield or the end
        h_.resume();
        return !h_.done();
    }
    const T& value() const { return h_.promise().current; }

private:
    std::coroutine_handle<promise_type> h_;
};
```

#### in practice

also count the cost: each coroutine call may allocate a frame, and every resume is typically an indirect call through the handle. that is irrelevant for an uploader and potentially relevant in a 10 kHz control loop; custom `operator new` on the promise type gives you control of the allocation, and a profiler tells you whether it matters.

#### watch out for

**resuming a finished coroutine is undefined behavior.** `next()` above resumes unconditionally. after it has returned `false` once, the coroutine is suspended at its final suspend point, and calling `next()` again calls `resume()` on it:

```cpp
auto scan = serpentine_scan(1, 1);
scan.next();   // true: (0,0)
scan.next();   // false: done
scan.next();   // BUG: resumes a coroutine at its final suspend point
```

a robust wrapper checks `h_.done()` before resuming (and returns `false` again), or exposes an iterator interface whose `end()` makes the misuse impossible. it should also check for a null handle, which a moved-from `Generator` holds.

#### the takeaway

a coroutine's return type defines its behavior through `promise_type`: when it starts, what `co_yield` does, and who destroys the frame; design the suspend points and the wrapper's API together, and guard every resume.

#### optional challenge

what does `serpentine_scan(2, 3)` execute before the first call to `next()`, and what would change if `initial_suspend()` returned `std::suspend_never`?

<details>
<summary>answer</summary>

with `suspend_always`, the call allocates the frame, copies `rows` and `cols` into it, constructs the promise, obtains the `Generator`, and suspends at the initial suspend point: none of the loop body runs. with `suspend_never`, the body runs immediately until the first `co_yield`, so `current` already holds `(0,0)` when the caller receives the generator. our `next()` resumes before reading, so the first `next()` would then skip to `(0,1)` and `(0,0)` would be lost. eager start is a legitimate design (some task types use it), but the rest of the type has to be written for it; this is why the promise's suspend points and the wrapper's API must be designed together.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-104"></a>

### day 104: review: polymorphism choices, APIs, modules, and coroutines

**module 15:** polymorphism choices, APIs, modules, and coroutines · **reading time:** about 8 minutes · **standard:** C++20  
**objective:** consolidate the polymorphism options and type erasure, API contracts and ABI stability, modules, and coroutines  
**covers:** [day 97](#day-97) to [day 103](#day-103)

#### recap

| lesson | key idea |
|---|---|
| [day 97](#day-97) | virtual functions, templates with concepts, `std::variant`, and type erasure fit different shapes of "one call, many types". |
| [day 98](#day-98) | a template constructor captures the type in a private model; users get value semantics without inheritance. |
| [day 99](#day-99) | contracts go into types first: strong types, enums, views, `[[nodiscard]]` result types. |
| [day 100](#day-100) | an ABI is stricter than an API: pimpl, no inline private logic in public headers, deprecate before removing. |
| [day 101](#day-101) | compiled interfaces instead of pasted text; adopt from the leaves inward as tooling allows. |
| [day 102](#day-102) | state lives in a frame across suspensions; take parameters by value. |
| [day 103](#day-103) | `promise_type` decides when a coroutine starts, what `co_yield` does, and who destroys the frame. |

#### review questions

1. a radar processing chain passes about a dozen message types defined by a versioned interface document, and a hot loop dispatches on them. separately, third-party detection plugins are loaded from shared libraries at startup. which polymorphism mechanism fits each, and why?
2. a pimpl class compiles in its own `.cpp` file but every client fails with an error about applying `sizeof` to an incomplete type. what is missing, and why does the fix work?
3. predict the problem:

   ```cpp
   Generator<std::string_view> fields(std::string_view line);   // splits on commas, lazily
   std::string read_line();

   auto f = fields(read_line());
   while (f.next()) use(f.value());
   ```

4. a type-erased wrapper declares `template <typename T> Wrapper(T&& value);` with no constraint. what happens on `Wrapper copy = original;` when `original` is a non-const `Wrapper`, and which earlier lesson predicted this?
5. a public function is `bool deploy(char* host, int port, double timeout, bool force, bool dry_run);`. name three changes that make it hard to misuse, and the lesson each comes from.

#### mini exercise

a header-only library exposes `class Tracker { public: void update(const Frame&); private: std::vector<Track> tracks_; KalmanFilter kf_; };` and is about to become a prebuilt shared library. sketch the header you would ship, and list what clients can no longer depend on.

#### answers

<details>
<summary>answer 1: radar messages and plugins</summary>

the internal messages are a closed, versioned set: `std::variant` with `std::visit`. value semantics, no per-message heap allocation, and adding a type forces every visitor to be updated (with an `overloaded` visitor lacking a catch-all, a missing case fails to compile). templates alone cannot hold mixed types in one stream. the plugins form an open set that crosses a shared-library boundary: a virtual interface plus an `extern "C"` factory, because templates cannot cross that boundary and a variant cannot be extended by someone else. if the hot loop ever shows the dispatch in a profile, that is the time to reconsider, not before.

</details>

<details>
<summary>answer 2: pimpl and the incomplete type</summary>

the class does not declare its destructor (and probably its move operations), so the compiler defines them implicitly and inline, in every client translation unit. they destroy the `std::unique_ptr<Impl>`, and `std::default_delete<Impl>` requires `Impl` to be complete, which it is only in the class's own `.cpp`. declaring `~Widget();` and the move operations in the header and defining them as `= default` in the `.cpp` (after `Impl` is defined) moves the code that destroys `Impl` to the one place where it is complete.

</details>

<details>
<summary>answer 3: the lazy splitter</summary>

`read_line()` returns a temporary `std::string`. the `std::string_view` parameter is copied into the coroutine frame, but it points into that temporary, which is destroyed at the end of the full-expression `auto f = fields(read_line());`. because the generator starts lazily, all of the splitting happens later, reading freed memory: undefined behavior. every yielded `string_view` would also point into the dead string. fix: take `std::string line` by value so the frame owns the text, and make sure consumers are done with each yielded view before the generator is destroyed, or yield `std::string` values.

</details>

<details>
<summary>answer 4: the greedy forwarding constructor</summary>

for a non-const lvalue, `T` deduces to `Wrapper&`, so the template's parameter is `Wrapper&`: an exact match, better than the copy constructor's `const Wrapper&`. the template wins and wraps a `Wrapper` inside the wrapper (or fails to compile in some confusing way). [day 42](#day-42) called this the hijacked copy constructor; [day 97](#day-97)'s challenge showed why a by-value parameter avoids it. fix by constraining: `requires (!std::same_as<std::remove_cvref_t<T>, Wrapper>)`.

</details>

<details>
<summary>answer 5: a signature that states its contract</summary>

`std::string_view host` instead of `char*` (borrowing, no null-termination assumptions: [day 55](#day-55)); `std::chrono::milliseconds timeout` instead of a unitless `double`, and enums or an options struct instead of two adjacent `bool`s ([day 99](#day-99)); and a `[[nodiscard]]` result type that says why it failed instead of a `bool` that is easy to ignore ([day 50](#day-50)).

</details>

<details>
<summary>mini exercise answer</summary>

```cpp complete
// tracker.h: the shipped header
#pragma once
#include <memory>

struct Frame;

class Tracker {
public:
    Tracker();
    ~Tracker();                                   // defined in the .cpp, where Impl is complete
    Tracker(Tracker&&) noexcept;
    Tracker& operator=(Tracker&&) noexcept;
    void update(const Frame& frame);
private:
    struct Impl;                                  // tracks_, kf_, and anything added later
    std::unique_ptr<Impl> impl_;
};
```

clients can no longer depend on `sizeof(Tracker)` changing with its members, on including `KalmanFilter`'s header transitively, or on inlining `update`. in exchange, the library can add members and change its filter without breaking binaries built against this header. a factory returning `std::unique_ptr<TrackerInterface>` would be the alternative if the library also wants to hide which tracker implementation is in use.

</details>

#### connections

the last two modules were about structure rather than mechanism: where seams go, how components are wired, and what an interface promises over time. the final modules turn to production engineering: measuring performance honestly, designing data for the cache, controlling allocation, testing and observing running systems, and changing legacy code safely, before putting the whole course together in one small program.

[back to the curriculum map](#curriculum)

---

<a id="module-performance"></a>

## module 16: performance

honest measurement, the memory hierarchy, data layout, and the cost of allocation.

<a id="day-105"></a>

### day 105: measure first: honest benchmarks

**module 16:** performance · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** write a microbenchmark the optimizer cannot hollow out, report robust statistics, and know what a benchmark does not tell you  
**builds on:** [day 36](#day-36) (iterators and algorithms over raw loops), [day 37](#day-37) (lambdas are objects: closures and captures)

#### the idea

a colleague replaces a `std::map` with a sorted `std::vector` and posts a microbenchmark: 40 times faster. you rebuild it with `-O2` and the measured loop takes almost no time at all, because the compiler deleted it. both numbers are wrong, and only one of them looks wrong. performance work starts with measurements you can trust, and most bad optimization decisions trace back to a number nobody questioned.

#### understanding the concept

intuition fails because the machine we reason about (one instruction after another, memory with uniform cost) is not the machine we run on. out-of-order execution, branch prediction, caches, prefetchers, and dynamic clock frequencies mean that instruction counts and complexity classes predict only part of the cost. complexity tells you how cost grows; constant factors, memory behavior, and the input distribution decide what happens at your sizes ([day 34](#day-34) made this point for containers).

- **benchmarks** answer "how long does this take, under these conditions?" a microbenchmark isolates one function. a macrobenchmark runs a realistic workload: replaying a recorded radar session, or a full planning cycle on logged sensor data.

for timing inside code, use `std::chrono::steady_clock`. it is monotonic, so an NTP adjustment cannot make an interval negative or inflate it. `system_clock` is calendar time and may jump. `high_resolution_clock` is allowed to be an alias of either (libstdc++ makes it `system_clock`, MSVC makes it `steady_clock`), so don't reach for it because of its name.

#### in code

the benchmark from the idea, reduced to its bugs:

```cpp complete
#include <chrono>
#include <cstdio>
#include <numeric>
#include <vector>

int main() {
    std::vector<int> v(1'000'000, 1);
    auto t0 = std::chrono::system_clock::now();          // BUG: wall clock, may jump
    for (int rep = 0; rep < 100; ++rep) {
        int sum = std::accumulate(v.begin(), v.end(), 0); // BUG: result never used
        (void)sum;
    }
    auto t1 = std::chrono::system_clock::now();
    auto us = std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0);
    std::printf("100 sums: %lld us\n", static_cast<long long>(us.count()));
}
```

the sum has no observable effect, so under the as-if rule the optimizer may remove the whole loop (dead-code elimination). GCC 12 at `-O2` does exactly that: the generated assembly contains the two `now()` calls and nothing between them. even if the result were used, the input is a compile-time constant pattern the optimizer might fold. and it is one sample, taken cold, with no idea of the spread.

a small harness that fixes each problem:

```cpp complete
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <numeric>
#include <random>
#include <vector>

struct Stats { double median_us, min_us, max_us; };

template <typename F>
Stats measure(F&& work, int warmup = 3, int reps = 31) {
    using clock = std::chrono::steady_clock;          // monotonic: never jumps
    for (int i = 0; i < warmup; ++i) work();          // caches, page faults, clock ramp-up
    std::vector<double> samples;
    samples.reserve(reps);
    for (int i = 0; i < reps; ++i) {
        const auto t0 = clock::now();
        work();
        const auto t1 = clock::now();
        samples.push_back(std::chrono::duration<double, std::micro>(t1 - t0).count());
    }
    std::sort(samples.begin(), samples.end());
    return {samples[samples.size() / 2], samples.front(), samples.back()};
}

volatile long long g_sink;  // a volatile write is observable behavior: it must happen

int main(int argc, char**) {
    std::mt19937 rng(static_cast<unsigned>(argc));     // input unknown at compile time
    std::vector<int> v(1'000'000);
    for (auto& x : v) x = static_cast<int>(rng() % 100);

    const Stats s = measure([&] { g_sink = std::accumulate(v.begin(), v.end(), 0LL); });
    std::printf("median %.1f us (min %.1f, max %.1f)\n", s.median_us, s.min_us, s.max_us);
}
```

why the median and the extremes rather than the mean: timing noise is one-sided. interrupts, thread migrations, and page faults only ever add time, so the distribution has a long right tail that drags the mean around. the median is robust; the minimum approximates "nothing interfered"; the maximum tells you whether the tail matters. for a control loop with a deadline, the tail (p99, worst case) is the requirement, so report it.

#### in practice

a radar team wants to catch performance regressions in CI. the naive version runs benchmarks on shared CI runners and fails the build if anything is 5 percent slower. within a week it is ignored, because run-to-run noise on a shared virtual machine is often larger than 5 percent.

what tends to work:

- run timing benchmarks on a dedicated, quiet machine with a fixed CPU frequency (the `performance` governor, turbo disabled) and pinned cores, or accept wider thresholds.
- compare against a stored baseline with repetitions on both sides, and flag only differences larger than the measured spread. Google Benchmark ships a `compare.py` tool for this.
- on noisy runners, track a proxy with less noise, such as instruction counts from `perf stat -e instructions` or Cachegrind. instructions are not time (a cache miss costs far more than an add), so treat a proxy alarm as a prompt to measure, not a verdict.

#### watch out for

a microbenchmark is a best-case laboratory. the data is hot in cache, branches are perfectly predicted after a few iterations, the allocator has a warm free list, and no other thread competes for memory bandwidth. production sees cold caches, varied inputs, and contention. a function that wins a microbenchmark by 30 percent can make no measurable difference in the full pipeline, or even lose if its larger code or tables evict something else. always close the loop with a macro measurement.

#### the takeaway

a benchmark number means nothing until you know what the compiler did to the measured code, which clock and statistics produced it, and how much it varies from run to run.

#### optional challenge

a teammate benchmarks `std::sort` with the harness above: `measure([&] { std::sort(v.begin(), v.end()); })`. the median looks impressively low. what is it actually measuring, and how would you fix it?

<details>
<summary>answer</summary>

after the first warm-up call the vector is sorted, so every timed repetition sorts already-sorted data, which is a very different (and for typical introsort implementations, much cheaper) workload. copy the original unsorted input into a working vector inside each repetition. the copy then becomes part of the measurement, so either measure the copy alone and report both, or sort many independent copies prepared in advance and divide. Google Benchmark has `state.PauseTiming()`, but pausing has its own overhead and is unreliable for very short regions. the general lesson: a benchmark that mutates its input must restore it, or it measures a different input after the first iteration.

</details>

#### going deeper (optional)

##### using a benchmark library

a hand-rolled harness is fine for a quick check, but a library handles iteration counts, repetitions, and statistics for you. with Google Benchmark (not part of the standard; shown for its idioms):

```cpp external
#include <benchmark/benchmark.h>
#include <map>

static void BM_MapFind(benchmark::State& state) {
    std::map<int, int> m;
    for (int i = 0; i < state.range(0); ++i) m[i * 2] = i;
    int key = 0;
    for (auto _ : state) {                         // the library chooses the iteration count
        auto it = m.find(key);
        benchmark::DoNotOptimize(it);              // forces the result to be "used"
        key = (key + 7) % static_cast<int>(2 * state.range(0));
    }
}
BENCHMARK(BM_MapFind)->Range(64, 1 << 16);         // several sizes, not one
BENCHMARK_MAIN();
```

run it with `--benchmark_repetitions=10 --benchmark_report_aggregates_only=true` to get mean, median, standard deviation, and coefficient of variation per size. note that `DoNotOptimize` keeps a value alive but does not stop the compiler from hoisting loop-invariant work out of the timed loop; the varying `key` above is what prevents that, and `benchmark::ClobberMemory()` exists for the memory side of the same problem.

[back to the curriculum map](#curriculum)

---

<a id="day-106"></a>

### day 106: profiling: finding where the time goes

**module 16:** performance · **reading time:** about 5 minutes · **standard:** C++17  
**objective:** use sampling and instrumentation profilers on optimized builds, and use Amdahl's law to decide whether an optimization can matter  
**builds on:** [day 105](#day-105) (measure first: honest benchmarks), [day 16](#day-16) (RAII: let scope do the cleanup)

#### the idea

a planning cycle sometimes misses its 50 ms deadline. the team has three theories (the collision checker, the cost map update, the logging), and three engineers ready to optimize their favorite. a profiler replaces the theories with data in an afternoon, and Amdahl's law tells you, before anyone writes code, how much each fix could possibly buy.

#### understanding the concept

two kinds of tools answer two different questions:

- **benchmarks** answer "how long does this take, under these conditions?" a microbenchmark isolates one function. a macrobenchmark runs a realistic workload: replaying a recorded radar session, or a full planning cycle on logged sensor data.
- **profilers** answer "where does the time go?" sampling profilers (`perf` on Linux, Intel VTune, Apple Instruments) interrupt the program at intervals and record the call stack: low overhead, whole-program coverage, statistical results. instrumentation profilers (Tracy, or your own scope timers) record explicit begin and end events, giving exact per-frame, per-thread timelines at the cost of touching the code. a flame graph draws sampled stacks so that width is proportional to time: wide plateaus are where to look.

the workflow that works: profile a realistic run to find the hot spot, write a benchmark around that hot spot, change the code, benchmark again, then confirm with the profiler that the whole program got faster, not just the microbenchmark.

**Amdahl's law** bounds what any optimization can buy. if a fraction `p` of the runtime is sped up by a factor `s`, the overall speedup is `1 / ((1 - p) + p / s)`. make a function that takes 10 percent of the frame infinitely fast and you save at most 10 percent. this is why profiling comes first: it tells you `p` before you spend effort on `s`.

#### in code

sampling needs no code changes; it needs the right build:

```sh
g++ -O2 -g -fno-omit-frame-pointer ...        # optimized, but with usable stacks
perf record -g ./radar_replay session.bin     # sample with call graphs
perf report                                   # or render a flame graph from 'perf script'
```

a debug build measures a different program: no inlining, every abstraction paid in full. its hot spots are frequently not the release build's hot spots.

instrumentation is the opposite trade: you add probes, and in exchange you get exact per-frame timings. the simplest probe is an RAII scope timer:

```cpp complete
#include <chrono>
#include <cstdio>

class ScopeTimer {                          // a minimal instrumentation probe
public:
    explicit ScopeTimer(const char* name) : name_(name), t0_(std::chrono::steady_clock::now()) {}
    ~ScopeTimer() {
        const auto us = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::steady_clock::now() - t0_).count();
        std::printf("%s: %lld us\n", name_, static_cast<long long>(us));
    }
    ScopeTimer(const ScopeTimer&) = delete;
    ScopeTimer& operator=(const ScopeTimer&) = delete;
private:
    const char* name_;
    std::chrono::steady_clock::time_point t0_;
};

void plan_cycle() {
    ScopeTimer t("plan_cycle");             // reported when the function exits, by any path
    // ...
}
```

real instrumentation profilers (Tracy, Perfetto, or your middleware's tracing) record these begin and end events into a buffer instead of printing them, and draw them as a timeline per thread.

#### in practice

averages hide the problem in real-time systems. a sampling profile of the planner says where time goes *on average*, which is the right first question for throughput, but a deadline miss is about the slowest cycle, not the typical one. the useful combination is a sampling profile to find the generally expensive code, then instrumentation around each stage of the cycle to find *which* cycles are slow and what happened in them: a periodic map reload, a lock held by a logging thread, an allocation spike every hundredth frame. the timeline view, one row per thread, makes those visible in a way no average can.

#### watch out for

remember the other side of the ledger, too: every optimization has a maintenance cost (less obvious code, more invariants, more tests). optimize where the profile points, stop when the requirement is met, and leave a comment with the measurement that justified the change.

#### the takeaway

profile to find where time goes, benchmark to compare alternatives, and distrust any number until you know what the compiler did to the code and how much the result varies.

#### optional challenge

collision checking takes 30 percent of a planning cycle. one engineer can make it three times faster; another proposes eliminating it entirely with a cached approximation. by Amdahl's law, what overall speedup does each achieve?

<details>
<summary>answer</summary>

with `p = 0.3`: three times faster gives `1 / (0.7 + 0.3 / 3) = 1 / 0.8 = 1.25`, a 25 percent faster cycle. eliminating it entirely gives at most `1 / 0.7`, about 1.43. the second proposal can never beat 1.43 no matter how clever, and it changes behavior; the first gets most of the available benefit. if the goal is a cycle twice as fast, neither is enough on its own, which is exactly the kind of conclusion worth reaching before writing code.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-107"></a>

### day 107: cache locality: why the same loop can be slower

**module 16:** performance · **reading time:** about 5 minutes · **standard:** C++17  
**objective:** explain cache lines, prefetching, and memory-level parallelism, and predict which traversals are fast, slow, or contended  
**builds on:** [day 106](#day-106) (profiling: finding where the time goes), [day 05](#day-05) (objects in memory: size, alignment, and padding), [day 34](#day-34) (containers and what they cost)

#### the idea

two loops do the same arithmetic over the same number of elements, both O(n), and one runs several times slower than the other. nothing in the source explains it, because the difference is not in the instructions: it is in where the bytes live. most code that is "slow for no reason" is waiting on memory.

#### understanding the concept

the CPU does not read bytes from RAM; it reads cache lines (64 bytes on most x86-64 and many ARM cores, 128 on some designs) through a hierarchy of caches. the numbers below are rough orders of magnitude only. they vary considerably across CPU generations and vendors, so treat them as a sense of scale, not as constants:

| level | typical size | rough latency |
|---|---|---|
| registers | a few hundred bytes | effectively zero |
| L1 data cache | 32 to 128 KiB per core | about 1 ns (a handful of cycles) |
| L2 | 256 KiB to a few MiB | a few ns |
| L3 (shared) | several to tens of MiB | around 10 to 20 ns |
| DRAM | GiB | around 50 to 100+ ns |

three mechanisms explain most of what you will observe:

- **spatial locality**: once a line is loaded, its other 63 bytes are nearly free. code that uses every byte it fetches gets the most out of each miss.
- **prefetching**: hardware prefetchers detect sequential and constant-stride access and fetch lines before you ask. they cannot predict where a pointer points.
- **memory-level parallelism**: a modern core can have many misses in flight at once, if it knows the addresses. in a linked list, the next address is inside the node you are still waiting for, so misses serialize: each one pays the full latency.

#### in code

three traversals, identical arithmetic:

```cpp complete
#include <list>
#include <memory>
#include <vector>

struct Point { float x, y, z; };

float sum_x(const std::vector<Point>& pts) {                   // contiguous, sequential
    float s = 0; for (const Point& p : pts) s += p.x; return s;
}
float sum_x(const std::vector<std::unique_ptr<Point>>& pts) {  // one indirection each
    float s = 0; for (const auto& p : pts) s += p->x; return s;
}
float sum_x(const std::list<Point>& pts) {                     // dependent pointer chase
    float s = 0; for (const Point& p : pts) s += p.x; return s;
}
```

the vector is the friendly case: sequential lines, prefetcher engaged. the vector of `unique_ptr` stores pointers contiguously but the pointees go wherever the allocator put them. in a fresh benchmark process they are often allocated back to back, so it looks fine; after hours of allocation churn they scatter, and the benchmark flattered the design ([day 105](#day-105)'s warning about laboratory conditions). the list adds a dependency chain on top of the scatter.

#### in practice

claims about memory behavior should be checked against the hardware's own counters, not inferred from timings alone:

```sh
perf stat -e cycles,instructions,cache-references,cache-misses,L1-dcache-load-misses ./localizer_replay run.bag
```

available event names vary by CPU (`perf list` shows yours). the useful readings are relative: a layout change that halves cache misses *and* reduces cycles per frame was memory-bound and worth it; one that halves misses with no change in cycles means memory was not the bottleneck, and the change probably is not worth its complexity. instructions per cycle (`instructions` divided by `cycles`) is a quick tell: a loop that retires far less than one instruction per cycle is usually waiting on memory.

#### watch out for

**false sharing: two threads, one cache line.** cache coherence works per line, not per variable, so threads that write *different* variables on the *same* line still contend:

```cpp
#include <vector>

struct PaddedSum { alignas(64) double value = 0; };   // one cache line per thread
std::vector<PaddedSum> partial(num_threads);           // C++17 vector honors over-alignment
```

without the padding, adjacent `double` accumulators for different threads share a line, and every write by one core invalidates it in the others' caches, so logically independent threads slow each other down. the 64 is a common line size, not a guarantee; [day 85](#day-85) discusses `std::hardware_destructive_interference_size` and its portability caveats.

#### the takeaway

performance is often decided by which bytes travel from memory, in what order, and which cores fight over them; contiguous, sequential, unshared access is the fast path.

#### optional challenge

a traversal of a `std::list` with a million nodes takes far longer than the extra cache misses alone would suggest, compared with a vector of the same elements. what mechanism makes it worse than "one miss per node"?

<details>
<summary>answer</summary>

the misses cannot overlap. a core can have many cache misses in flight at once, but only when it knows the addresses; in a list, the address of the next node is stored inside the current node, which is itself still being loaded. each miss must complete before the next one can even start, so the traversal pays the full memory latency per node, back to back. a vector of pointers has the same scatter but the pointers themselves are contiguous, so the core can request several pointees concurrently; a plain vector has neither problem.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-108"></a>

### day 108: data-oriented design: arrays of structs and structs of arrays

**module 16:** performance · **reading time:** about 6 minutes · **standard:** C++17  
**objective:** choose between array-of-structs, struct-of-arrays, and hot/cold splitting by the access pattern of the hot loops, and keep the choice encapsulated  
**builds on:** [day 107](#day-107) (cache locality: why the same loop can be slower)

#### the idea

object-oriented design starts from "what is a detection?" and packs everything a detection has into one struct. a loop that only checks each detection's signal-to-noise ratio then drags sixty unrelated bytes through the cache for every four it uses. data-oriented design starts from the other end: which loops are hot, which bytes do they read, and in what order? the layout follows from the answers, and so do its costs.

#### understanding the concept

data-oriented design takes these mechanisms as the starting point. instead of asking "what is a detection?" you ask "which bytes does this loop read, how many times, in what order?" and lay the data out to match.

the two classic layouts are an *array of structs* (AoS), where each element's fields are adjacent, and a *struct of arrays* (SoA), where each field is its own contiguous array. AoS is ideal when a loop uses most fields of one element at a time; SoA is ideal when a loop uses one or two fields of every element. most real systems end up in between.

#### in code

now a radar detection, laid out as an array of structs (AoS):

```cpp complete
#include <cstddef>
#include <cstdint>
#include <vector>

struct Detection {                                    // AoS: 64 bytes on common 64-bit ABIs
    float range_m, azimuth_rad, doppler_mps, snr_db;  // 16
    std::uint64_t timestamp_ns;                       //  8
    std::uint32_t track_id, flags;                    //  8
    char source[32];                                  // 32: sensor name, rarely read
};

std::size_t count_strong(const std::vector<Detection>& ds, float min_snr) {
    std::size_t n = 0;
    for (const Detection& d : ds) n += d.snr_db >= min_snr;  // 4 useful bytes per 64 fetched
    return n;
}
```

every iteration pulls in a whole line to use one `float`. the struct of arrays (SoA) version stores each field contiguously:

```cpp
#include <array>

struct Detections {                                   // SoA: one array per field
    std::vector<float> range_m, azimuth_rad, doppler_mps, snr_db;
    std::vector<std::uint64_t> timestamp_ns;
    std::vector<std::uint32_t> track_id, flags;
    std::vector<std::array<char, 32>> source;
};

std::size_t count_strong(const Detections& ds, float min_snr) {
    std::size_t n = 0;
    for (float snr : ds.snr_db) n += snr >= min_snr;  // 16 useful floats per line
    return n;
}
```

the gating loop now moves one sixteenth of the bytes, and its body is a uniform operation over contiguous floats, which is exactly the shape compilers auto-vectorize most readily. whether that turns into a large speedup depends on whether the AoS loop was memory-bound to begin with: for a few hundred detections that fit in L1, the difference may be noise. for hundreds of thousands per frame, it usually is not.

a middle ground is **hot/cold splitting**: keep the fields every loop touches in one compact struct (here `range`, `azimuth`, `doppler`, `snr`, `track_id`, `flags`: 24 bytes) and move the rarely read ones (timestamp, sensor name) into a parallel array indexed the same way. you keep most of the AoS ergonomics and stop paying for bytes you never read.

#### in practice

a robot localizer runs a particle filter with tens of thousands of particles. each cycle has three phases: predict (update every pose from odometry), weight (score every pose against the latest scan), and resample (cumulative sum over weights, then copy chosen poses). originally each `Particle` was a class with pose, weight, a history buffer for debugging, and virtual methods, held in a `std::vector<std::unique_ptr<Particle>>`.

the data-oriented rewrite stored `x`, `y`, `theta`, and `weight` as four float arrays inside a `ParticleSet` class, moved the debug history into a separate structure that is only filled when diagnostics are enabled, and replaced the virtual methods with whole-set operations (`predict`, `normalize_weights`, `resample`) that loop over the arrays. each step was justified with numbers: the benchmark harness from [day 105](#day-105) on a recorded dataset for time per cycle, and hardware counters for the mechanism.

note the design move: the SoA arrays are private to `ParticleSet`, which guarantees they always have equal length and exposes whole-set operations (`predict`, `normalize_weights`). encapsulation moved from the element to the collection; it did not disappear.

#### watch out for

SoA is a tradeoff, not an upgrade. code that accesses all fields of one element at a time (a tracker associating one detection, a lookup by index) touches one line in AoS and several lines in SoA. every new field touches several places. sorting means permuting every array, or sorting an index array instead. element identity becomes "an index", which invalidates as easily as an iterator ([day 34](#day-34)). and the readability cost is real: `particles.x[i]` reads worse than `particle.x`.

choose layout from the dominant access pattern of the hot loops, keep it behind an interface so the choice can change, and verify with counters that memory was the bottleneck before paying the complexity.

#### the takeaway

performance is often decided by which bytes travel from memory and in what order; lay out data for the loops that run hottest, and keep that layout encapsulated so it stays a decision rather than an accident.

#### optional challenge

on a typical 64-bit ABI, `struct Particle { bool active; double x, y, z; bool dirty; };` is 40 bytes. why, what is the smallest you can make it by reordering, and what would you do instead if the hot loop only checks `active` and skips most particles?

<details>
<summary>answer</summary>

each `double` needs 8-byte alignment, so `active` is followed by 7 bytes of padding, and `dirty` is followed by 7 more so that the size is a multiple of the alignment (arrays must keep every element aligned): 1 + 7 + 24 + 1 + 7 = 40. putting the doubles first and the two `bool`s together gives 24 + 2 = 26, rounded up to 32 bytes, so exactly two particles per 64-byte line instead of 1.6. padding is implementation-defined in general, but these numbers hold on the common x86-64 and AArch64 ABIs.

if the hot loop only needs `active` and most particles are inactive, layout tweaks are the wrong tool: the loop still visits every particle. keep the active ones compacted at the front of the arrays (swap-remove on deactivation), or keep a separate dense list of active indices, so the loop never touches inactive particles at all. doing less work beats doing the same work with fewer misses.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-109"></a>

### day 109: the cost of allocation

**module 16:** performance · **reading time:** about 8 minutes · **standard:** C++17  
**objective:** find hidden heap allocations, count them in tests, and move them out of hot paths into an allocation-free steady state  
**builds on:** [day 105](#day-105) (measure first: honest benchmarks), [day 107](#day-107) (cache locality: why the same loop can be slower), [day 38](#day-38) (lambdas that outlive their scope: callbacks and `std::function`)

#### the idea

a 1 kHz joint controller meets its deadline in every lab test, then misses one every few minutes in the field. the profiler shows nothing hot. the culprit is a `std::string` built for a log line and a `std::vector` that grows inside the loop: allocation calls whose cost is usually small but occasionally very large. in real-time code the average does not matter; the worst case does, and the general-purpose heap has no useful worst-case bound.

#### understanding the concept

`operator new` (and `malloc` beneath it) is a general-purpose allocator. on each call it may:

- find a free block of the right size class and update its bookkeeping (the cheap, common path, often served from a per-thread cache in modern allocators such as glibc's tcache, jemalloc, tcmalloc, or mimalloc);
- take a lock or touch shared structures when the thread cache is empty or memory was freed by another thread;
- ask the operating system for more memory (`brk`, `mmap`, `VirtualAlloc`), which is a system call, and the fresh pages are then page-faulted in on first touch.

so the cost distribution has a cheap mode and a long tail you cannot bound. allocation also scatters data (each node or object lands wherever a block was free, which is [day 107](#day-107)'s locality problem), and long-running processes fragment the heap.

the expensive part is that allocations hide. each of these allocates, or may:

| code | allocation |
|---|---|
| `std::string` longer than the small-string buffer | one per string (buffer size is implementation-defined: 15 chars in libstdc++ and MSVC, 22 in libc++, on 64-bit targets) |
| string concatenation `a + b + c` | possibly one per intermediate |
| `std::function` holding a large capture | one, beyond a small internal buffer (size implementation-specific) |
| `std::make_shared<T>()` | one (object and control block together); `shared_ptr<T>(new T)` makes two ([day 27](#day-27)) |
| `std::map`, `std::set`, `std::list`, `std::unordered_map` | one per node |
| `push_back` without `reserve` | about log2(n) reallocations with geometric growth |
| `throw` | the runtime allocates the exception object |

the remedies, roughly in order of how often you reach for them: `reserve` and reuse; avoiding node containers in hot paths; scoped arenas and pools ([day 110](#day-110)); and the strongest pattern of all for real-time code, an allocation-free steady state: allocate everything at startup, then never again.

#### in code

first, measure. replacing the global allocation functions is a standard, supported mechanism. put the replacement in its own file and link it only into test binaries:

```cpp complete
// alloc_counter.cpp: link into test binaries only
#include <atomic>
#include <cstddef>
#include <cstdlib>
#include <new>

std::atomic<std::size_t> g_allocs{0};

void* operator new(std::size_t n) {                  // replaces the global allocation function
    g_allocs.fetch_add(1, std::memory_order_relaxed);
    if (void* p = std::malloc(n ? n : 1)) return p;
    throw std::bad_alloc{};
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

// elsewhere:
template <typename F>
std::size_t count_allocs(F&& f) {
    const std::size_t before = g_allocs.load();
    f();
    return g_allocs.load() - before;
}
```

the array forms forward to these by default. with GCC 12 and libstdc++ on x86-64, `count_allocs` reported: a 6-character string 0, a 22-character string 1, a `std::function` capturing a `std::array<double, 8>` 1, `make_shared<int>` 1, 100 `std::map` inserts 100, and 1,000 `push_back` calls without `reserve` 11. these are implementation details, which is exactly why you count rather than guess. a complete counter also replaces the C++17 `std::align_val_t` overloads; libstdc++'s default `pmr` resource, for one, allocates through them.

the real-time pattern: preallocate, then reuse.

```cpp
class LocalPlanner {
public:
    explicit LocalPlanner(std::size_t max_obstacles) {
        nearby_.reserve(max_obstacles);           // pay once, at startup
    }
    std::size_t cycle(const std::vector<Obstacle>& scan) {
        nearby_.clear();                          // destroys elements, keeps capacity
        for (const Obstacle& o : scan)
            if (o.x * o.x + o.y * o.y < 25.0f) nearby_.push_back(o);
        return nearby_.size();
    }
private:
    std::vector<Obstacle> nearby_;                // reused every cycle
};

void test_planner_steady_state_is_allocation_free() {
    std::vector<Obstacle> scan(256, Obstacle{1.0f, 1.0f, 0.5f});
    LocalPlanner planner(512);
    planner.cycle(scan);                          // warm-up
    const std::size_t before = g_allocs.load();
    for (int i = 0; i < 1000; ++i) planner.cycle(scan);
    assert(g_allocs.load() == before);            // the steady state never touches the heap
}
```

the test turns a performance property into a regression test: if someone adds a `std::string` to `cycle` next year, CI fails instead of the robot.

#### in practice

a radar tracker processed each frame with a `std::map<TrackId, Track>` and built a fresh `std::vector` of candidate associations per track. a heap profiler (heaptrack on Linux, or Valgrind's massif) showed hundreds of thousands of allocations per second, and the tail of the frame time tracked them.

the fix came in layers, each verified with the counter and [day 105](#day-105)'s harness: tracks moved into a `std::vector` sorted by id ([day 35](#day-35)), candidate lists became members cleared each frame, and per-frame temporaries moved to a `monotonic_buffer_resource` reset at frame boundaries. the steady state dropped to zero allocations, and the remaining frame-time variation came from the work itself.

#### watch out for

**measurement traps.**

two measurement traps. the standard allows a new-expression to omit or merge its call to a replaceable allocation function, so an optimized build may count fewer allocations than the source suggests. and on Windows, a replacement in the executable does not intercept allocations made inside a DLL that has its own `operator new`: with MinGW's shared libstdc++, string allocations inside the library went uncounted until the program was linked with `-static`. exceptions are separate again: the common Itanium ABI runtimes allocate the exception object with `malloc`, so an `operator new` counter never sees it.

#### the takeaway

count allocations instead of guessing, move them out of hot loops and into startup, and when a steady state must be allocation-free, write a test that says so.

#### optional challenge

`LocalPlanner::cycle` calls `nearby_.clear()`. what happens to the allocation-free steady state if it instead calls `nearby_ = std::vector<Obstacle>{};` or `nearby_.clear(); nearby_.shrink_to_fit();`?

<details>
<summary>answer</summary>

both break it. `clear()` destroys the elements but keeps the capacity, so later `push_back` calls reuse the buffer. move-assigning an empty vector takes over the temporary's (empty) buffer and frees the old one, so the next cycle reallocates, about log2(n) times as it grows again. `shrink_to_fit()` is a non-binding request to drop unused capacity, and mainstream implementations honor it by reallocating, with the same result. the allocation test from this lesson would catch either change on the first CI run.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-110"></a>

### day 110: arenas and pools with `std::pmr`

**module 16:** performance · **reading time:** about 5 minutes · **standard:** C++17  
**objective:** use `std::pmr` memory resources for scoped arena allocation and pooling, and avoid their propagation and lifetime traps  
**builds on:** [day 109](#day-109) (the cost of allocation)

#### the idea

some allocations cannot simply be moved to startup: per-frame temporaries whose size depends on the data, tracks that are born and die while the system runs. for those, the problem is not that allocation happens but that the general-purpose heap is the wrong allocator for the pattern. a frame's temporaries all die together at the end of the frame; a pool's objects all have the same size. C++17's `std::pmr` lets a container use an allocator that matches the pattern without changing the container's type to a template parameter soup.

#### understanding the concept

second, `std::pmr` (C++17). a `memory_resource` is a runtime-polymorphic allocator, and the `std::pmr::` containers hold a pointer to one. `monotonic_buffer_resource` is a bump allocator: allocation advances a pointer, deallocation is a no-op, and everything is released at once when the resource dies.

the standard resources cover the common patterns: `monotonic_buffer_resource` for "allocate during a phase, free everything at its end"; `unsynchronized_pool_resource` and `synchronized_pool_resource` for many allocations of a few sizes; `new_delete_resource()` for the ordinary heap; and `null_memory_resource()`, which always throws, as a guard against silently falling back. resources chain: each takes an *upstream* resource to get more memory from when its own runs out.

#### in code

```cpp complete
#include <array>
#include <cstddef>
#include <memory_resource>
#include <vector>

struct Detection { float range_m, azimuth_rad, snr_db; };

std::size_t process_frame(const std::vector<Detection>& raw) {
    alignas(std::max_align_t) std::array<std::byte, 16 * 1024> buffer;   // scratch on the stack
    std::pmr::monotonic_buffer_resource arena(buffer.data(), buffer.size(),
                                              std::pmr::null_memory_resource());
    std::pmr::vector<Detection> gated(&arena);
    gated.reserve(raw.size());                   // a pointer bump, no heap
    for (const Detection& d : raw)
        if (d.snr_db > 10.0f) gated.push_back(d);
    return gated.size();
}                                                // everything released at once
```

the `null_memory_resource()` upstream is a deliberate choice: if a frame ever needs more than 16 KiB, allocation throws `std::bad_alloc` instead of silently falling back to the heap. in a test, that is a loud failure you want; in production you might prefer the default upstream plus a metric. note `reserve`: with a monotonic resource, a growing vector leaves every outgrown buffer behind as dead space until the arena is released.

#### in practice

object pools fill the remaining gap: when objects of one type are created and destroyed at runtime (tracks born and dying), a fixed-capacity pool with a free list gives O(1) allocation with no system calls. `std::pmr::unsynchronized_pool_resource` is a general-purpose version for single-threaded use; `synchronized_pool_resource` adds locking.

per-frame arenas fit naturally into a processing loop: create one `monotonic_buffer_resource` per frame over a buffer that is reused across frames, pass it to the frame's temporary containers, and let it be destroyed (or `release()`d) at the frame boundary. combined with the allocation counter from [day 109](#day-109), that turns "this stage does not touch the heap" into a property a test can check.

#### watch out for

`pmr` propagation surprises people. a pmr container does not propagate its resource on copy: `std::pmr::vector<int> copy = a;` gets the default resource (normally the heap), not `a`'s arena. moving keeps the resource, but move-assigning between containers with different resources copies element by element. uses-allocator construction passes the resource down only to elements that accept one: `pmr::vector<pmr::string>` puts the strings in the arena, `pmr::vector<std::string>` does not. and the resource must outlive every container using it; a container whose arena has been destroyed holds dangling memory, and touching it is undefined behavior.

#### the takeaway

match the allocator to the allocation pattern: a monotonic arena for data that dies together, a pool for objects of one size, and a null upstream wherever silently falling back to the heap would be a bug.

#### optional challenge

`std::pmr::vector<std::pmr::string> names(&arena); names.push_back("front_left_radar_long_name");` how many allocations come from the arena, and what changes if the element type is `std::string`?

<details>
<summary>answer</summary>

with `pmr::string` elements, uses-allocator construction gives the new string the vector's resource, so both the vector's buffer and the string's heap buffer (the name is longer than the small-string buffer) come from the arena. one subtlety: `push_back` first constructs a temporary `pmr::string` from the literal using the default resource, then moves it into the vector; because the resources differ, the move copies into arena memory, so the temporary's allocation hits the heap. `emplace_back("...")` constructs in place with the arena and avoids that. with `std::string` elements, only the vector's buffer is in the arena; every long string allocates from the global heap, defeating the point of the arena.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-111"></a>

### day 111: review: performance

**module 16:** performance · **reading time:** about 7 minutes · **standard:** C++17  
**objective:** consolidate benchmarking, profiling, cache locality, data-oriented layout, allocation costs, and memory resources  
**covers:** [day 105](#day-105) to [day 110](#day-110)

#### recap

| lesson | key idea |
|---|---|
| [day 105](#day-105) | a benchmark number means nothing until you know what the compiler did, which statistics produced it, and how it varies. |
| [day 106](#day-106) | profile optimized builds to find where time goes; Amdahl's law bounds what any fix can buy. |
| [day 107](#day-107) | cache lines, prefetching, and memory-level parallelism decide what a loop costs; false sharing makes independent threads contend. |
| [day 108](#day-108) | lay out data for the hot loops: AoS, SoA, or hot/cold splitting, kept behind an interface. |
| [day 109](#day-109) | count allocations, move them to startup, and test that the steady state is allocation-free. |
| [day 110](#day-110) | match the allocator to the pattern: arenas for data that dies together, pools for one size, a null upstream as a guard. |

#### review questions

1. a microbenchmark says your new hash function is 25 percent faster, but the end-to-end frame time does not move. give two distinct explanations and how you would tell them apart.
2. after converting detections from AoS to SoA, the SNR gating loop got faster but the per-detection association step got slower. why is that plausible?
3. `std::pmr::vector<int> copy = arena_vec;` quietly puts `copy` on the heap. why, and how do you keep it in the arena?
4. two worker threads each increment their own counter in a `std::array<std::uint64_t, 2>`, with no sharing at all, and scale badly. what is happening, and what is the fix?
5. from [day 25](#day-25): why does adding a logging destructor to a struct stored in a large `std::vector` make reallocation slower?

#### mini exercise

this function runs once per frame in a telemetry exporter. list where it may allocate, then sketch an allocation-free version, and say how you would verify it.

```cpp
std::string describe(const std::vector<Detection>& ds) {
    std::string out;
    for (const auto& d : ds) out += std::to_string(d.range_m) + " m, ";
    return out;
}
```

#### answers

<details>
<summary>answer 1: faster microbenchmark, unchanged frame time</summary>

either the hash is a small share of the frame (Amdahl: 25 percent of 2 percent is invisible), or the microbenchmark's conditions (hot cache, one key pattern, no contention) do not hold in the pipeline. a profile of the real workload distinguishes them: if the hash's share is tiny, it is the first; if the share is large but did not shrink, it is the second.

</details>

<details>
<summary>answer 2: SoA helps one loop and hurts another</summary>

gating reads one field across many detections, so SoA packs 16 useful floats per line. association reads all fields of one detection at a time, which in SoA touches a different line per field instead of one line. layout should follow the dominant access pattern; sometimes a hot/cold split serves both.

</details>

<details>
<summary>answer 3: pmr copy on the heap</summary>

copy construction asks `select_on_container_copy_construction`, which for `polymorphic_allocator` returns a default-constructed allocator, meaning the default resource. use the allocator-extended constructor: `std::pmr::vector<int> copy(arena_vec, &arena);`.

</details>

<details>
<summary>answer 4: false sharing</summary>

the two counters sit on the same cache line, and cache coherence works per line: every increment by one core invalidates the line in the other core's cache, so the threads contend as if they shared a variable. give each counter its own line (`struct alignas(64) Counter { std::uint64_t value; };`), or accumulate in a local variable and write the total once.

</details>

<details>
<summary>answer 5: a destructor suppresses moves</summary>

declaring a destructor suppresses the implicit move constructor, so the type's "moves" are copies, and `std::vector` reallocation copies every element (including any heap-owning members) instead of moving them. remove the destructor or default all five special members explicitly ([day 24](#day-24)).

</details>

<details>
<summary>mini exercise answer</summary>

it may allocate in `std::to_string` (if the text exceeds the small-string buffer), in the temporary created by `to_string(...) + " m, "`, every time `out` grows, and for the returned string itself. an allocation-free version takes a caller-owned output buffer that is reused every frame, reserves it once, and formats numbers with `std::to_chars` into a stack buffer before appending:

```cpp
#include <charconv>
#include <string>
#include <vector>

void describe(const std::vector<Detection>& ds, std::string& out) {   // out reused by the caller
    out.clear();                                                        // keeps capacity
    char num[32];
    for (const auto& d : ds) {
        auto [end, ec] = std::to_chars(num, num + sizeof num, d.range_m);
        out.append(num, end);
        out.append(" m, ");
    }
}
```

once `out` has grown to the largest frame seen, the steady state allocates nothing. verify it with the allocation counter from [day 109](#day-109) in a test that runs many frames after a warm-up, rather than by reading the code: whether a given call allocates is an implementation detail.

</details>

#### connections

performance work in C++ is mostly about memory: where bytes live, how often they are allocated, and which cores fight over them. the habits from this module (measure first, check the mechanism with counters, keep the fast path allocation-free, encapsulate layout decisions) apply to every earlier module, from container choice to concurrency. the final module turns to the rest of production engineering, and then puts the whole course together.

[back to the curriculum map](#curriculum)

---

<a id="module-production"></a>

## module 17: production engineering and integration

testing, observability, safe change in legacy code, and one small program that puts the course together.

<a id="day-112"></a>

### day 112: testing that catches real bugs

**module 17:** production engineering and integration · **reading time:** about 8 minutes · **standard:** C++20  
**objective:** structure tests by the test pyramid, test behavior through injected seams, and add property tests, fuzzing, and sanitizer builds where they pay off  
**builds on:** [day 92](#day-92) (choosing a seam: interfaces, templates, functions, and the linker), [day 72](#day-72) (small C++20 features that remove bug patterns)

#### the idea

tests tell you the code did what you expected on inputs you thought of. the useful questions are which inputs, at which level, and against what: a test that pins down the exact boundary of a watchdog's timeout catches more bugs than a dozen tests of the happy path, and a test that asserts how a function did its job breaks on every refactor while catching nothing.

#### understanding the concept

**the test pyramid, in C++ terms.** at the base, many fast unit tests that run in milliseconds and need no hardware: pure functions, classes with injected dependencies ([day 91](#day-91)). in the middle, integration tests: several real components wired together, perhaps over loopback sockets or by replaying recorded sensor data. at the top, few and expensive: hardware-in-the-loop (the real controller board driving a simulated plant) and field tests. push each check as low as it can go; a bug found by a unit test costs seconds, one found on the robot costs a day.

**test behavior, not implementation.** a test that asserts "the planner called `compute_cost` 14 times" breaks on every refactor and catches nothing. a test that asserts "the planned path never enters the keep-out zone" survives refactors and catches real bugs. mocks that verify call sequences are right only when the call is the behavior (the actuator command was sent exactly once).

**beyond examples.** property-based tests generate many inputs and check an invariant: `parse(serialize(msg)) == msg`, or "the filter output stays within sensor bounds". fuzzing (libFuzzer, AFL++) mutates inputs guided by code coverage, and is the most effective tool we have for parsers of untrusted bytes. sanitizers ([day 14](#day-14)) turn silent undefined behavior into loud test failures, but they need separate builds: AddressSanitizer and ThreadSanitizer cannot be combined in one binary, while ASan and UBSan usually can.

#### in code

a deterministic unit test with the fake clock from [day 91](#day-91), using `std::source_location` (C++20) for failure locations instead of a macro:

```cpp complete
#include <chrono>
#include <cstdio>
#include <source_location>
#include <string_view>

using namespace std::chrono_literals;
using TimePoint = std::chrono::steady_clock::time_point;

struct Clock {                                        // the seam from dependency injection
    virtual ~Clock() = default;
    virtual TimePoint now() const = 0;
};

class Watchdog {                                      // trips if heartbeats stop
public:
    Watchdog(const Clock& clock, std::chrono::milliseconds timeout)
        : clock_(clock), timeout_(timeout), last_(clock.now()) {}
    void heartbeat() { last_ = clock_.now(); }
    bool expired() const { return clock_.now() - last_ > timeout_; }
private:
    const Clock& clock_;
    std::chrono::milliseconds timeout_;
    TimePoint last_;
};

struct FakeClock final : Clock {                      // a fake: real behavior, controlled time
    TimePoint t{};
    TimePoint now() const override { return t; }
};

int g_failures = 0;
void check(bool ok, std::string_view what,
           std::source_location loc = std::source_location::current()) {
    if (ok) return;
    ++g_failures;
    std::printf("%s:%u: FAILED: %.*s\n", loc.file_name(), static_cast<unsigned>(loc.line()),
                static_cast<int>(what.size()), what.data());
}

void test_watchdog_trips_only_after_timeout() {
    FakeClock clock;
    Watchdog dog(clock, 100ms);
    clock.t += 100ms;
    check(!dog.expired(), "exactly at the timeout it is still alive");
    clock.t += 1ms;
    check(dog.expired(), "trips once the timeout has passed");
    dog.heartbeat();
    check(!dog.expired(), "a heartbeat re-arms it");
}
```

no sleeps, no flakiness, and the boundary (exactly 100 ms) is pinned down, which is where the bugs live. the default argument `std::source_location::current()` is evaluated at the call site, so the failure reports the line of the `check`, not of its definition. in a real project you would use GoogleTest (`EXPECT_TRUE`) or Catch2 (`CHECK`); the test's shape is the same.

#### in practice

a robotics team's CI runs a matrix rather than one build:

```text
release        -O2              unit + integration tests, benchmarks
asan+ubsan     -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer
tsan           -O1 -g -fsanitize=thread         concurrency tests, repeated
fuzz (nightly) clang++ -fsanitize=fuzzer,address    the telemetry parser
```

the fuzz target is a single function the fuzzer calls with mutated bytes:

```cpp external
extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t* data, std::size_t size) {
    parse_nmea_sentence(std::string_view(reinterpret_cast<const char*>(data), size));
    return 0;   // crashes, sanitizer reports, and timeouts are the failures
}
```

#### watch out for

**tests that sleep.** the tempting way to test a timeout uses real time:

```cpp
Watchdog dog(system_clock_adapter, 100ms);
std::this_thread::sleep_for(150ms);
check(dog.expired(), "trips after the timeout");   // slow, and flaky on a loaded CI machine
```

every such test adds real seconds to the suite, and the margins that make it pass on a laptop fail on a busy CI runner, where the thread may be descheduled for longer than the margin. it also cannot test the exact boundary. inject the clock and advance it explicitly, as the fake-clock test above does: the test becomes instant, deterministic, and precise.

#### the takeaway

push each check as low in the pyramid as it can go, test behavior rather than call sequences, inject time and I/O so tests are deterministic, and let sanitizers and fuzzers search the inputs you did not think of.

#### optional challenge

you add a helper `void check_near(double a, double b, double tol) { check(std::abs(a - b) <= tol, "near"); }` and use it across many tests. failures now all report the same line. why, and how do you fix it without a macro?

<details>
<summary>answer</summary>

`std::source_location::current()` as a default argument is evaluated where the call to `check` is written, which is now inside `check_near`, so every failure points at the helper. give the helper the same defaulted parameter and forward it: `void check_near(double a, double b, double tol, std::source_location loc = std::source_location::current()) { check(std::abs(a - b) <= tol, "near", loc); }`. each test's call site now fills in its own location, and `check` reports it. this forwarding is how test frameworks and logging libraries built on `source_location` pass the caller's location through layers of helpers.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-113"></a>

### day 113: observability: logs, metrics, and traces

**module 17:** production engineering and integration · **reading time:** about 8 minutes · **standard:** C++20  
**objective:** instrument production code with structured logs, cheap metrics, and spans, without letting the instrumentation disturb the code it observes  
**builds on:** [day 112](#day-112) (testing that catches real bugs), [day 83](#day-83) (`std::atomic`: indivisible operations), [day 16](#day-16) (RAII: let scope do the cleanup)

#### the idea

tests tell you the code did what you expected on inputs you thought of. observability tells you what it did in production on inputs you did not think of. a team with only the first ships bugs it cannot diagnose; a team with only the second diagnoses the same bug every week. both are design concerns, and both are cheaper when the code was built for them.

#### understanding the concept

**observability** has three complementary signals:

- **logs**: discrete events with context. make them structured (`key=value` or JSON) so machines can query them.
- **metrics**: cheap numeric aggregates (counters, gauges, histograms), exported periodically. they answer "how often" and "how slow" without storing every event.
- **traces**: timed spans with parent/child relationships, showing where one request or frame spent its time across stages and threads.

#### in code

structured logging, where the interesting part is what a disabled log costs:

```cpp
#include <atomic>
#include <initializer_list>

enum class Level { debug, info, warn, error };
inline std::atomic<Level> g_level{Level::info};       // adjustable at runtime

struct Field { std::string_view key; double value; };

void log_event(Level lvl, std::string_view event, std::initializer_list<Field> fields,
               std::source_location loc = std::source_location::current()) {
    if (lvl < g_level.load(std::memory_order_relaxed)) return;
    std::fprintf(stderr, "level=%d event=%.*s", static_cast<int>(lvl),
                 static_cast<int>(event.size()), event.data());
    for (const Field& f : fields)
        std::fprintf(stderr, " %.*s=%g", static_cast<int>(f.key.size()), f.key.data(), f.value);
    std::fprintf(stderr, " src=%s:%u\n", loc.file_name(), static_cast<unsigned>(loc.line()));
}

// The arguments of a disabled log_event() call are still evaluated. The macro checks first.
#define LOG_DEBUG(event, ...)                                                   \
    do {                                                                        \
        if (g_level.load(std::memory_order_relaxed) <= Level::debug)            \
            log_event(Level::debug, event, __VA_ARGS__);                        \
    } while (0)

// LOG_DEBUG("cycle", {{"residual", compute_residual()}});
// prints nothing at level info, and compute_residual() is never called
```

this is one of the few places where a macro still earns its keep: a function cannot avoid evaluating its arguments. if debug logs must cost nothing at all in release builds, add a compile-time floor (`if constexpr (kMinCompiledLevel <= Level::debug)`) so the code is not even generated; the tradeoff is that you cannot turn those logs on in the field without a rebuild. in a C++20 codebase with a newer toolchain, you would format with `std::format` ([day 71](#day-71)) rather than `printf`.

metrics and spans, built so they are safe to use inside a control loop:

```cpp
#include <algorithm>
#include <array>
#include <bit>

class LatencyHistogram {          // log2 buckets in microseconds: [0,1), [1,2), [2,4), ...
public:
    static constexpr std::size_t kBuckets = 24;
    void record(std::chrono::nanoseconds d) {
        const auto us = static_cast<std::uint64_t>(std::max<std::int64_t>(d.count(), 0) / 1000);
        const auto b = std::min<std::size_t>(std::bit_width(us), kBuckets - 1);
        counts_[b].fetch_add(1, std::memory_order_relaxed);   // no lock, no allocation
    }
    std::uint64_t count(std::size_t b) const { return counts_[b].load(std::memory_order_relaxed); }
private:
    std::array<std::atomic<std::uint64_t>, kBuckets> counts_{};
};

class ScopeTimer {                                    // a tracing span in miniature: RAII again
public:
    explicit ScopeTimer(LatencyHistogram& h) : h_(h), start_(std::chrono::steady_clock::now()) {}
    ~ScopeTimer() { h_.record(std::chrono::steady_clock::now() - start_); }
    ScopeTimer(const ScopeTimer&) = delete;
    ScopeTimer& operator=(const ScopeTimer&) = delete;
private:
    LatencyHistogram& h_;
    std::chrono::steady_clock::time_point start_;
};

// void control_cycle() { ScopeTimer span(g_cycle_latency); /* ... */ }
```

relaxed ordering is correct here because each counter is independent and nothing else is published through it ([day 84](#day-84)). a reporter thread reads the buckets periodically and exports them; the control loop only ever does one `fetch_add`.

#### in practice

on the robot, each pipeline stage has a latency histogram, a dropped-frame counter, and a span per frame. when an operator reports "the arm hesitated at 14:02", the team pulls the spans for that minute and sees the planner stage at its p99.9 while a log shows a map reload: a diagnosis in minutes instead of a week of trying to reproduce it.

#### watch out for

observability code runs in the paths you are trying to observe, so it can cause the problems it is meant to find. writing a log line can allocate ([day 109](#day-109)), take a lock inside the logging library, and block on I/O when the disk or the network is slow. inside a 1 kHz control loop, or while holding a mutex ([day 86](#day-86)), that turns a diagnostic into a deadline miss or a convoy of blocked threads. keep hot paths to counters and fixed-size records: push events into a preallocated lock-free ring buffer and let a background thread format and write them, rate-limit repeated messages, and never log while holding a lock you share with a latency-critical thread.

#### the takeaway

design for "what is it doing?" from the start: structured logs for events, counters and histograms for rates and latencies, spans for where time went, all built so that observing the system does not change it.

#### optional challenge

with `LatencyHistogram`'s log2 buckets, which bucket does a 5 µs cycle land in, and which does a 1 ms cycle land in? what does that bucketing make easy, and what does it give up?

<details>
<summary>answer</summary>

5 µs: `std::bit_width(5)` is 3, so bucket 3, covering [4, 8) µs. 1 ms is 1000 µs: `std::bit_width(1000)` is 10, so bucket 10, covering [512, 1024) µs. log2 buckets cover microseconds to seconds with a couple of dozen counters and one cheap instruction per record, which is what makes them safe in a control loop, and percentiles such as p99 can be estimated from them. what they give up is resolution: within a bucket, 520 µs and 1000 µs are indistinguishable, so a regression from 600 to 900 µs is invisible. finer buckets (or several sub-buckets per power of two) trade memory for precision.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-114"></a>

### day 114: refactoring legacy code safely

**module 17:** production engineering and integration · **reading time:** about 10 minutes · **standard:** C++17  
**objective:** put characterization tests around legacy code, modernize it in small verified steps behind a compatibility shim, and let tools do the mechanical changes  
**builds on:** [day 58](#day-58) (a practical C++17 refactoring), [day 112](#day-112) (testing that catches real bugs), [day 92](#day-92) (choosing a seam: interfaces, templates, functions, and the linker)

#### the idea

every engineer has opened a 4,000-line file full of raw `new`, `char*` buffers, and out-parameters and thought "this needs a rewrite". big rewrites usually take far longer than planned, while the old code keeps shipping and accumulating fixes the new code lacks. the approach that works is less dramatic: change the code in small, verified steps, each one leaving the system working, and make the architectural calls deliberately and in writing.

#### understanding the concept

legacy code, in the useful definition, is code without tests: you cannot change it with confidence. so the first step is not modernization; it is getting a safety net.

**characterization tests** record what the code does today, not what it should do. you feed it inputs, observe outputs, and assert those outputs, including the strange ones. they are scaffolding for refactoring: when one fails, you changed behavior, and you decide whether that was intended.

**seams** ([day 92](#day-92)) are where you can change behavior without editing the code in place: a constructor parameter, a virtual function, a template parameter, a link-time substitution. legacy code often has none; creating the first seam with a minimal, careful edit is usually the riskiest step, so keep it mechanical.

a safe **modernization order** goes from zero-risk to higher-risk changes:

1. turn on warnings (`-Wall -Wextra`, then `-Werror` directory by directory) and run sanitizer builds in CI ([day 113](#day-113)). this finds real bugs without touching a line.
2. write characterization tests around the code you are about to change.
3. fix ownership at boundaries: RAII wrappers and `std::unique_ptr` in signatures ([day 16](#day-16), [day 28](#day-28)), so leaks become impossible rather than unlikely.
4. adopt vocabulary types: `std::string_view` for read-only strings, `std::optional` or a variant result for "maybe" and errors, `std::filesystem::path` for paths ([day 51](#day-51) to [day 57](#day-57)).
5. apply mechanical modernizations with tools, one kind of change per commit.

#### in code

the legacy function, with its problems labelled:

```cpp ub
// calib_loader.cpp, circa 2009
#include <cstdio>
#include <cstring>

struct Calib { double gain, offset, skew; };

bool load_calibration(const char* path, Calib** out, char* err, int errlen) {
    FILE* f = std::fopen(path, "r");
    if (!f) { std::strncpy(err, "open failed", errlen); return false; }  // BUG: may not terminate
    Calib* c = new Calib;
    if (std::fscanf(f, "%lf %lf %lf", &c->gain, &c->offset, &c->skew) != 3) {
        std::strncpy(err, "parse failed", errlen);
        std::fclose(f);
        return false;                                                    // BUG: leaks c
    }
    std::fclose(f);
    *out = c;                                                            // caller must delete
    return true;
}
```

`strncpy` does not write a terminator when the source is at least `errlen` characters long, so a caller that prints `err` reads past the buffer: undefined behavior. the parse-failure path leaks. ownership of `*out` lives only in a comment.

before changing anything, pin the behavior down:

```cpp
// Pin what the code does today, including the parts that look odd.
void characterize_load_calibration() {
    char err[64] = {};
    Calib* c = nullptr;

    write_file("ok.cal", "1.5 0.25 -3\n");
    assert(load_calibration("ok.cal", &c, err, sizeof err));
    assert(c->gain == 1.5 && c->offset == 0.25 && c->skew == -3.0);
    delete c;

    write_file("trailing.cal", "1 2 3 garbage\n");                // accepted today: keep?
    assert(load_calibration("trailing.cal", &c, err, sizeof err));
    delete c;

    write_file("short.cal", "1 2\n");
    assert(!load_calibration("short.cal", &c, err, sizeof err));
    assert(std::string(err) == "parse failed");                   // someone greps for this

    assert(!load_calibration("missing.cal", &c, err, sizeof err));
    assert(std::string(err) == "open failed");
}
```

the trailing-garbage case is the interesting one. it may be a bug, but some calibration file in the fleet may rely on it. Hyrum's law ([day 99](#day-99)): every observable behavior has a user. the test makes that behavior visible so changing it becomes a decision.

now the modern core, plus a shim so existing callers keep compiling:

```cpp
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <string>
#include <variant>

struct LoadError { std::string message; };

[[nodiscard]] std::variant<Calib, LoadError> read_calibration(const std::filesystem::path& path) {
    std::ifstream in(path);
    if (!in) return LoadError{"open failed"};
    Calib c{};
    if (!(in >> c.gain >> c.offset >> c.skew)) return LoadError{"parse failed"};
    return c;                                     // value, no ownership question at all
}

// Compatibility shim: old signature, new implementation. Delete when the last caller is gone.
[[deprecated("use read_calibration")]]
bool load_calibration(const char* path, Calib** out, char* err, int errlen) {
    auto result = read_calibration(path);
    if (auto* c = std::get_if<Calib>(&result)) { *out = new Calib(*c); return true; }
    std::snprintf(err, static_cast<std::size_t>(errlen), "%s",
                  std::get<LoadError>(result).message.c_str());   // always terminated
    return false;
}
```

the same characterization test passes against the shim, which is the evidence that the refactor preserved behavior. the `[[deprecated]]` attribute turns every remaining caller into a compiler warning, a built-in migration to-do list. note what was deliberately not changed: the error strings, and the acceptance of trailing text. `fscanf` and `operator>>` can also differ on unusual numeric input, which is exactly why the test, not a code review, is the judge.

#### in practice

the shim turns a migration into a countable task. every remaining caller of `load_calibration` now produces a deprecation warning, so the build log is the to-do list; teams typically track the warning count per release and migrate callers in small commits, each reviewed on its own. when the count reaches zero, the shim is deleted in a commit that changes nothing else. at no point does the codebase stop building, and at every point the characterization test proves the old and new paths agree. large mechanical changes (adding `override`, replacing `NULL`) follow the same rhythm with tools doing the edits, as [day 115](#day-115) shows.

#### watch out for

never mix a refactoring and a behavior change in one commit. a refactoring should leave every characterization test green; a behavior change should change specific tests on purpose. combine them and a failing test no longer tells you which change caused it, the review cannot separate "moved code" from "changed meaning", and a revert throws away both. the discipline is tedious and it is what makes legacy work safe.

#### the takeaway

get a safety net before you change anything, then modernize in small, separately verifiable steps, with tools doing the mechanical work and a shim keeping old callers compiling.

#### optional challenge

product decides that trailing garbage in calibration files must now be rejected. describe how you would ship that change safely after the refactoring above.

<details>
<summary>answer</summary>

treat it as a behavior change in its own commit, after the refactor has landed and been verified. first check reality: scan the calibration files actually deployed (or a fleet sample) for trailing content, because a robot that refuses to start is worse than one that ignores a comment. then change the rule in `read_calibration` (after the three reads, check that only whitespace remains), and update the characterization test deliberately: the "trailing" case now expects `parse failed` or, better, a more specific error. if files in the field do have trailing text, consider a transition period in which the loader accepts the file but logs a structured warning ([day 113](#day-113)) so you can see who would break. document the decision, briefly, where the next person will look.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-115"></a>

### day 115: architectural decisions and their tradeoffs

**module 17:** production engineering and integration · **reading time:** about 4 minutes · **standard:** C++17  
**objective:** replace subsystems incrementally with the strangler pattern, decide what not to refactor, and record architectural tradeoffs so they can be revisited  
**builds on:** [day 114](#day-114) (refactoring legacy code safely), [day 108](#day-108) (data-oriented design: arrays of structs and structs of arrays)

#### the idea

"we should rewrite the tracker" is a sentence that has started many projects that took three times longer than planned, while the old tracker kept shipping fixes the new one did not have. most architectural change is better done the way the previous lesson changed one function: incrementally, with the old and the new side by side, and with the reasons written down so the next engineer can revisit the decision instead of rediscovering it.

#### understanding the concept

the **strangler pattern** replaces a subsystem without a big bang: put an interface in front of the old implementation, build the new one behind the same interface, route a growing share of traffic to it, and delete the old one when nothing uses it. in robotics this often means running the new module in shadow mode on recorded data and comparing its outputs with the old one before it ever drives a motor.

the decisions behind such changes are tradeoffs rather than improvements: maintainability against performance, abstraction against overengineering, compile-time against run-time flexibility, object-oriented against data-oriented layout. each side has real costs, and the course has met all four. what turns them from arguments into decisions is writing down the context, the alternatives, and the consequences accepted, in a place the next person will look.

#### in code

the refactors that need judgment get written down. a lightweight architecture decision record (ADR) fits in a file next to the code:

```text
ADR-017: track storage layout
status:       accepted
context:      tracker misses its frame budget at high detection counts; perf counters
              show the association loop is dominated by cache misses.
decision:     store tracks as struct-of-arrays inside TrackTable; public API unchanged.
alternatives: keep AoS with hot/cold split (measured, not enough);
              pooled Track objects (fewer allocations, same misses).
consequences: + association loop within budget on recorded sessions
              - a new track field touches three places in TrackTable
              - debugger shows arrays, not tracks (pretty-printer added)
revisit if:   per-track behavior grows (polymorphic motion models) or counts drop.
```

#### in practice

modernization campaigns across a whole codebase are architectural work too, and the same rule applies: small, reviewable steps. tools beat people at mechanical edits:

mechanical modernization is where tools beat people. `clang-tidy` has a family of `modernize-*` checks (`use-nullptr`, `use-override`, `make-unique`, `loop-convert`, `use-using`, `pass-by-value`, and more) that rewrite code with fixes:

```sh
# one check per commit: each diff is large but trivially reviewable
run-clang-tidy -p build -checks='-*,modernize-use-nullptr' -fix
run-clang-tidy -p build -checks='-*,modernize-use-override' -fix
# reformat once, in its own commit, then hide it from blame
clang-format -i $(git ls-files '*.cpp' '*.h')
git rev-parse HEAD >> .git-blame-ignore-revs     # git config blame.ignoreRevsFile ...
```

the format matters less than the habit: context, the decision, the alternatives considered, the costs accepted, and when to revisit. the classic tradeoffs (maintainability versus performance, abstraction versus overengineering, compile-time versus runtime flexibility, object-oriented versus data-oriented layout) stop being religious arguments once each side has to write down its consequences.

not everything should be refactored. code that works, rarely changes, and is scheduled for retirement is cheapest left alone. prioritize by change frequency times pain: `git log` tells you which files churn, and the bug tracker tells you which ones hurt.

#### watch out for

**the second-system effect.** a replacement designed to fix every complaint about the old system tends to become larger, slower, and later than anyone planned, because every stakeholder adds the feature the old design could not support. the strangler pattern is the antidote: the new component must reach parity with the old one on recorded data, one route at a time, before it gets new features. scope that is explicitly deferred in the decision record is scope that does not silently creep in.

#### the takeaway

replace subsystems incrementally behind a stable interface, refactor where change frequency and pain are highest, and record each architectural decision with its alternatives and costs.

#### optional challenge

your team wants to replace a legacy obstacle detector with a new one. using the strangler pattern, list the steps from today to deleting the old code, and say which observability signals tell you each step is safe.

<details>
<summary>answer</summary>

put an interface in front of the old detector (a seam, if there is none yet) and route all callers through it. build the new detector behind the same interface and run it in shadow mode on live or recorded data, comparing its outputs with the old one's: metrics for detection counts, disagreement rates, and per-frame latency histograms tell you when it is at parity. then route a growing share of real traffic to it (one robot, one site, one sensor configuration), watching the same metrics plus field reports. when nothing uses the old detector for a release cycle, delete it, together with the comparison code. at every step the system works and the switch can be reverted.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-116"></a>

### day 116: putting it together, part 1: values, messages, and the queue

**module 17:** production engineering and integration · **reading time:** about 7 minutes · **standard:** C++20  
**objective:** see the course's ideas combine in one small program, starting with value types, a closed message set, and a closable bounded queue  
**builds on:** [day 79](#day-79) (a bounded producer-consumer queue), [day 53](#day-53) (`std::variant` and `std::visit`), [day 67](#day-67) (defaulted comparisons and the spaceship operator), [day 115](#day-115) (architectural decisions and their tradeoffs)

#### the idea

each lesson so far isolated one idea. real code is where the ideas meet and pull against each other: the queue wants ownership to move, the processing stage wants to borrow, the test wants seams, and shutdown wants all of it to unwind in the right order. the next three lessons build one small program, about 160 lines in four parts that compile together with `-std=c++20`, and review every decision in it.

#### understanding the concept

the shape is a classic two-stage pipeline:

```text
 source (fake sensor)          bounded queue            consumer thread
 producer jthread  ---push--->  [ Message x 8 ]  ---pop--->  Processor<Sink>
                                                              gate(span) -> sink.on_frame(span)
```

a producer thread pulls `Message`s (a frame of detections or a sensor fault) from an injected source and pushes them into a bounded queue. a consumer thread pops them, gates each frame's detections (drop weak and distant returns, sort strongest first), and hands the result to an injected sink. ownership flows one way: a `Frame` is created by the source, moved through the queue, and owned by exactly one stage at a time. the sink only borrows the result.

#### in code

part 1 defines the vocabulary: a value type and a closed set of messages.

```cpp group=pipeline
// part 1: values and messages
#include <algorithm>
#include <cassert>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <deque>
#include <functional>
#include <mutex>
#include <optional>
#include <ranges>
#include <span>
#include <stop_token>
#include <thread>
#include <utility>
#include <variant>
#include <vector>

struct Detection {
    double range_m{}, azimuth_rad{}, snr_db{};
    bool operator==(const Detection&) const = default;  // equality yes, ordering no
};
struct Frame { std::uint64_t seq{}; std::vector<Detection> detections; };
struct SensorFault { std::uint64_t seq{}; int code{}; };
using Message = std::variant<Frame, SensorFault>;

template <typename... Fs> struct overloaded : Fs... { using Fs::operator()...; };
```

part 2 is the queue from [day 79](#day-79), with close semantics so shutdown never leaves a thread blocked forever.

```cpp group=pipeline
// part 2: a bounded, closable queue
template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {}
    bool push(T item) {                      // blocks while full; false once closed
        std::unique_lock lock(m_);
        not_full_.wait(lock, [&] { return closed_ || q_.size() < capacity_; });
        if (closed_) return false;
        q_.push_back(std::move(item));
        not_empty_.notify_one();
        return true;
    }
    std::optional<T> pop() {                 // blocks while empty; nullopt once closed and drained
        std::unique_lock lock(m_);
        not_empty_.wait(lock, [&] { return closed_ || !q_.empty(); });
        std::optional<T> item;
        if (!q_.empty()) {
            item.emplace(std::move(q_.front()));
            q_.pop_front();
            not_full_.notify_one();
        }
        return item;
    }
    void close() {
        { std::lock_guard lock(m_); closed_ = true; }
        not_full_.notify_all(); not_empty_.notify_all();
    }
private:
    std::mutex m_;
    std::condition_variable not_full_, not_empty_;
    std::deque<T> q_;
    std::size_t capacity_;
    bool closed_ = false;
};
```

#### in practice

the design review for these two parts. every row is a decision someone could reasonably have made differently:

| decision | alternative | why this one |
|---|---|---|
| `Detection` defaults `==` only | also default `<=>` | `double` members give only `partial_ordering`, and detections have no natural order; sort by an explicit projection instead ([day 67](#day-67)) |
| `Message` is a `std::variant` | base class with virtual `handle()` | closed set, value semantics, no allocation per message; a missing case in the visitor fails to compile ([day 53](#day-53)) |
| bounded queue, producer blocks | unbounded queue, or drop-oldest | back-pressure bounds memory and latency; a sensor that cannot wait would need drop-oldest instead ([day 79](#day-79)) |

#### watch out for

**`Detection` deliberately has no ordering.** it would be easy to default `operator<=>` along with `operator==`, and then `std::sort(detections)` would compile. but a detection has no natural order (by range? by strength? by azimuth?), and with `double` members the defaulted ordering is only partial, so NaN would make such a sort undefined. leaving `<=>` out forces every sort to name its key with a projection, which is both safer and clearer at the call site.

#### the takeaway

start an integrated design from its values and its messages: small value types with only the operations that mean something, a closed variant for what flows between stages, and a queue whose policy for "full" and "closed" is explicit.

#### optional challenge

`BoundedQueue::pop` here notifies `not_full_` while still holding the lock, while the version in [day 79](#day-79) unlocks first. is either one wrong?

<details>
<summary>answer</summary>

neither is wrong. notifying under the lock or right after releasing it are both correct, as long as the state change happened under the lock. notifying after unlocking can save a woken producer from immediately blocking on the mutex the consumer still holds; notifying under the lock is simpler to reason about and safe even if a woken thread might destroy the condition variable. here, `close()` and the queue's lifetime are controlled by the pipeline, so either choice is fine; consistency within one class matters more than the choice.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-117"></a>

### day 117: putting it together, part 2: the processing stage

**module 17:** production engineering and integration · **reading time:** about 5 minutes · **standard:** C++20  
**objective:** build a pure, allocation-free processing stage over borrowed data, and constrain an injected sink with a concept  
**builds on:** [day 116](#day-116) (putting it together, part 1: values, messages, and the queue), [day 65](#day-65) (`std::span`: views over contiguous memory), [day 63](#day-63) (views: lazy pipelines), [day 92](#day-92) (choosing a seam: interfaces, templates, functions, and the linker)

#### the idea

the processing stage is where the pipeline does its actual work: gate each frame's detections and hand the result on. it is also where the most design decisions concentrate. what does it borrow and what does it own? does it allocate every frame? how does it talk to a sink it must not know the type of, and how does a test replace that sink? the answers come straight from earlier modules.

#### understanding the concept

the stage is split in two. `gate` is a pure function: it reads a span of detections, writes the survivors into a caller-provided vector, and touches nothing else, so it can be tested without threads or fakes. `Processor` adapts `gate` to the message variant and owns the only mutable state, a scratch vector reused every frame. the sink is a template parameter constrained by a concept, which states exactly what any sink must provide and catches a wrong sink where the pipeline is created.

#### in code

part 3 is the actual work. `gate` is a pure function over a borrowed span; `Processor` adapts it to messages and is constrained on what a sink must provide.

```cpp group=pipeline
// part 3: the processing stage
struct GateConfig { double min_snr_db = 10.0; double max_range_m = 200.0; };

// Pure, and allocation-free once `out` has enough capacity.
void gate(std::span<const Detection> in, const GateConfig& cfg, std::vector<Detection>& out) {
    auto keep = [&](const Detection& d) {
        return d.snr_db >= cfg.min_snr_db && d.range_m <= cfg.max_range_m;
    };
    out.clear();
    for (const Detection& d : in | std::views::filter(keep)) out.push_back(d);
    std::ranges::sort(out, std::ranges::greater{}, &Detection::snr_db);   // strongest first
}

template <typename S>
concept DetectionSink = requires(S& s, std::uint64_t seq, std::span<const Detection> ds, int code) {
    s.on_frame(seq, ds);       // ds is borrowed: valid only during the call
    s.on_fault(seq, code);
};

template <DetectionSink Sink>
class Processor {
public:
    Processor(GateConfig cfg, Sink& sink) : cfg_(cfg), sink_(sink) {}
    void operator()(const Message& msg) {
        std::visit(overloaded{
            [&](const Frame& f) { gate(f.detections, cfg_, scratch_); sink_.on_frame(f.seq, scratch_); },
            [&](const SensorFault& e) { sink_.on_fault(e.seq, e.code); },
        }, msg);
    }
private:
    GateConfig cfg_;
    Sink& sink_;
    std::vector<Detection> scratch_;         // reused every frame
};
```

#### in practice

the design review for part 3:

| decision | alternative | why this one |
|---|---|---|
| `gate` is a free function on `std::span` | member function taking `std::vector` | pure and testable without threads; any contiguous owner works ([day 65](#day-65)) |
| `scratch_` reused every frame | return a fresh vector | no steady-state allocation ([day 109](#day-109)); the cost is that `Processor` is stateful and not reentrant |
| sink: template constrained by a concept | virtual interface, or `std::function` | the per-frame call can inline, and a wrong sink fails to compile where the pipeline is created, naming the unmet requirement ([day 60](#day-60), [day 92](#day-92)); the cost is that `Pipeline` is a template |
| `views::filter` feeding a loop | `std::copy_if` | equally good; C++20 has no `ranges::to` (that is C++23), so materializing is explicit either way ([day 63](#day-63)) |

#### watch out for

**the sink receives a borrowed span.** `on_frame` gets a view of `scratch_`, which the next frame overwrites. a sink that stored the span instead of copying the data would read garbage later. that is the lifetime rule from [day 55](#day-55) and [day 65](#day-65), and here it is enforced only by a comment in the concept. a sink that needs to keep data must copy it, which the recording sink in part 4 does.

#### the takeaway

make the core computation a pure function over borrowed data, keep the stage's mutable state small and reused, and constrain injected collaborators with a concept so mistakes surface where the parts are put together.

#### optional challenge

`Processor` reuses `scratch_` across frames. what would you lose, and what would you gain, by making `gate` return a fresh `std::vector<Detection>` instead?

<details>
<summary>answer</summary>

you would gain a simpler interface (no output parameter), a `Processor` with no mutable state, and a sink that could keep the vector it receives by moving it. you would lose the allocation-free steady state: every frame would allocate at least once, which matters in a real-time pipeline ([day 109](#day-109)) and does not in a tool that runs once. the output parameter is the price of reuse; choose it deliberately, and measure whether the allocation matters before paying it.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-118"></a>

### day 118: putting it together, part 3: wiring, shutdown, and testing

**module 17:** production engineering and integration · **reading time:** about 10 minutes · **standard:** C++20  
**objective:** wire the pipeline's threads so every exit path stops and joins them, test it deterministically with fakes, and review the design as a whole  
**builds on:** [day 117](#day-117) (putting it together, part 2: the processing stage), [day 75](#day-75) (`std::jthread` and cooperative cancellation), [day 113](#day-113) (observability: logs, metrics, and traces)

#### the idea

the last part is where most concurrent programs go wrong: starting threads only after everything they use exists, stopping them on every exit path, draining work instead of dropping it, and testing all of it without sleeps or hardware. none of it needs new tools. member declaration order, `std::jthread`, a stop callback, and two small fakes are enough.

#### understanding the concept

member order is the shutdown protocol. `Pipeline` declares its source, queue, and processor first and its two threads last, so the threads start after everything they touch is constructed and are stopped and joined before anything they touch is destroyed. `finish()` lets the source run dry, then asks the consumer to stop, which a stop callback turns into closing the queue: the consumer drains what is left and exits. the destructor requests a stop first, so leaving the scope early still shuts down cleanly.

#### in code

part 4 wires it together. member order is the shutdown protocol, and `main` doubles as the test.

```cpp group=pipeline
// part 4: wiring, shutdown, and a test run
using Source = std::function<std::optional<Message>()>;   // runtime seam: nullopt = end

template <DetectionSink Sink>
class Pipeline {
public:
    Pipeline(GateConfig cfg, Sink& sink, Source source)
        : source_(std::move(source)), queue_(8), processor_(cfg, sink),
          consumer_([this](std::stop_token st) {
              std::stop_callback on_stop(st, [this] { queue_.close(); });  // stop = close, then drain
              while (auto msg = queue_.pop()) processor_(*msg);
          }),
          producer_([this](std::stop_token st) {
              while (!st.stop_requested()) {
                  auto msg = source_();
                  if (!msg || !queue_.push(std::move(*msg))) return;
              }
          }) {}
    void finish() {                          // let the source run dry, then drain the queue
        if (producer_.joinable()) producer_.join();
        consumer_.request_stop();
        if (consumer_.joinable()) consumer_.join();
    }
    ~Pipeline() { producer_.request_stop(); finish(); }
private:
    Source source_;
    BoundedQueue<Message> queue_;
    Processor<Sink> processor_;
    std::jthread consumer_, producer_;       // last members: stopped and joined first
};

struct RecordingSink {                       // a fake, touched only by the consumer thread
    std::vector<std::pair<std::uint64_t, std::vector<Detection>>> frames;
    std::vector<int> faults;
    void on_frame(std::uint64_t seq, std::span<const Detection> ds) {   // ds is borrowed: copy it
        frames.emplace_back(seq, std::vector<Detection>(ds.begin(), ds.end())); }
    void on_fault(std::uint64_t, int code) { faults.push_back(code); }
};

int main() {
    std::vector<Detection> out;               // unit test of the pure stage: no threads
    const Detection strong{40, 0, 25}, weak{40, 0, 3}, far{900, 0, 40};
    const std::vector<Detection> in{weak, strong, far};
    gate(in, GateConfig{}, out);
    assert(out.size() == 1 && out[0] == strong);

    std::uint64_t seq = 0;                    // a fake sensor: deterministic frames, one fault
    Source fake_sensor = [&seq]() -> std::optional<Message> {
        if (seq == 4) return std::nullopt;
        if (seq == 2) return SensorFault{seq++, 17};
        const double s = static_cast<double>(seq);
        return Frame{seq++, {{50 + s, 0.1, 18}, {250, 0.2, 30}, {80, -0.3, 12 + s}, {120, 0, 6}}};
    };
    RecordingSink sink;
    {
        Pipeline pipeline(GateConfig{}, sink, fake_sensor);
        pipeline.finish();
    }                                         // threads joined: reading the sink is safe
    for (const auto& [n, ds] : sink.frames) {
        std::printf("frame %llu:", static_cast<unsigned long long>(n));
        for (const Detection& d : ds) std::printf("  %.0f m / %.0f dB", d.range_m, d.snr_db);
        std::printf("\n");
    }
    std::printf("faults: %zu (code %d)\n", sink.faults.size(), sink.faults.at(0));
}
```

concatenated in order, the four parts form one translation unit. built with `g++ -std=c++20 -Wall -Wextra -pedantic -O2 -pthread` (GCC 12), it compiles without warnings and prints:

```text
frame 0:  50 m / 18 dB  80 m / 12 dB
frame 1:  51 m / 18 dB  80 m / 13 dB
frame 3:  53 m / 18 dB  80 m / 15 dB
faults: 1 (code 17)
```

the output is deterministic even though two threads are involved: the queue is FIFO and there is one consumer, so the order of messages is fixed by the source.

#### in practice

the rest of the design review:

| decision | alternative | why this one |
|---|---|---|
| source: `std::function` | another template parameter | called once per frame, so one indirect call is noise next to sensor I/O; keeps `Pipeline` to one template parameter ([day 38](#day-38)) |
| `jthread` plus a `stop_callback` that closes the queue | atomic flag and manual `join` | every exit path stops and joins, including a constructor that throws after the first thread started ([day 75](#day-75)) |
| threads declared last | threads declared anywhere | members are built in declaration order, so the threads start only after everything they use exists; if construction fails midway, they are the first to be stopped ([day 19](#day-19)) |

what a production version would add, and where it would go: a real sensor behind `Source` with a read timeout; a latency histogram and dropped-frame counter ([day 113](#day-113)) around `processor_(*msg)`; validated configuration instead of defaults; and `std::format` ([day 71](#day-71)) for output on a toolchain that has it. none of these require changing the structure, which is the real test of a design: the seams are where the next requirements land.

#### watch out for

**every blocking call must cooperate with cancellation.** the producer checks its stop token only between messages. if `source_()` blocks indefinitely (a sensor read with no timeout), `~Pipeline` waits for it, and shutdown hangs. cooperative cancellation only works if every blocking call cooperates: give the real source a timeout, or pass it the stop token so it can abandon the read.

#### the takeaway

good C++ design is mostly about who owns what, who may block, and what can be substituted; when those three answers are explicit in the types, the rest of the program becomes small and testable.

#### optional challenge

what goes wrong if you move `BoundedQueue<Message> queue_;` below the two `std::jthread` members, leaving the constructor's initializer list unchanged?

<details>
<summary>answer</summary>

members are initialized in declaration order, not initializer-list order ([day 19](#day-19)). the `jthread`s would be constructed first, so the consumer thread could call `queue_.pop()` (and the producer `queue_.push()`) before `queue_` has been constructed: undefined behavior, and a race you might not see in testing. GCC's `-Wreorder` (part of `-Wall`) warns, because the initializer list no longer matches the declaration order, but that warning is the only safety net. normal destruction would happen to survive, because the destructor body joins both threads before any member is destroyed. the exceptional path would not: if a later member's constructor threw, the already-running threads would be torn down around a queue that was never built. declaring threads last, after everything they touch, makes both orders correct by construction.

</details>

[back to the curriculum map](#curriculum)

---

<a id="day-119"></a>

### day 119: review: production engineering, and the road ahead

**module 17:** production engineering and integration · **reading time:** about 10 minutes · **standard:** C++20  
**objective:** consolidate testing, observability, legacy refactoring, architectural decisions, and the integrated pipeline, with spaced repetition across the course  
**covers:** [day 112](#day-112) to [day 118](#day-118)

#### recap

| lesson | key idea |
|---|---|
| [day 112](#day-112) | push checks down the pyramid, test behavior, inject time and I/O, and let sanitizers and fuzzers explore. |
| [day 113](#day-113) | structured logs, cheap metrics, and spans, built so that observing does not disturb. |
| [day 114](#day-114) | characterization tests first, then small verified steps behind a compatibility shim. |
| [day 115](#day-115) | replace subsystems incrementally and record tradeoffs where the next engineer will look. |
| [day 116](#day-116) to [day 118](#day-118) | one small program where ownership, borrowing, seams, and shutdown order all have to agree. |

#### review questions

1. in [day 118](#day-118)'s pipeline, the consumer registers a `std::stop_callback` that closes the queue. why not simply check `st.stop_requested()` in the loop?
2. your characterization test asserts a behavior you are fairly sure is a bug. why keep it during the refactor?
3. a log line inside a 1 kHz control loop formats a string and writes to a file. name two ways it can cause the deadline misses it was added to investigate.
4. from [day 13](#day-13): classify each as undefined, unspecified, or implementation-defined: `sizeof(long)`; the order in which `a()` and `b()` run in `f(a(), b())`; `INT_MAX + 1` for `int`.
5. from [day 23](#day-23): why does `std::vector<T>` copy rather than move elements during reallocation when `T`'s move constructor is not `noexcept`?
6. from [day 55](#day-55): what is wrong with `std::string_view sv = std::string("radar") + "_0";` followed by any use of `sv`?
7. from [day 84](#day-84): a producer writes a non-atomic payload and then sets an atomic `ready` flag with `memory_order_relaxed`; the consumer spins on `ready` with relaxed loads, then reads the payload. what is the bug?
8. from [day 100](#day-100): with pimpl and `std::unique_ptr<Impl>`, why must the destructor be declared in the header and defined in the `.cpp`?

#### mini exercise

extend the [day 118](#day-118) pipeline so that the time each sink call takes is recorded in [day 113](#day-113)'s `LatencyHistogram`, without editing `Pipeline`, `Processor`, or `RecordingSink`. decide which seam the feature belongs behind, and name one thing your choice cannot measure.

#### answers

<details>
<summary>answer 1: why the stop callback closes the queue</summary>

a consumer blocked inside `pop()` is waiting on a condition variable and never reaches the loop condition, so checking the token would not wake it. closing the queue wakes it, lets it drain, and makes `pop()` return `nullopt`. (a `std::condition_variable_any` wait that takes the stop token is the other C++20 option.)

</details>

<details>
<summary>answer 2: keeping a test for a bug</summary>

the refactor must not change behavior; if it fixes the bug in passing, you cannot tell intended change from accident, and someone may depend on the old behavior. keep the test green through the refactor, then change the behavior in its own commit and update the test deliberately.

</details>

<details>
<summary>answer 3: observability that disturbs</summary>

formatting can allocate, and the general-purpose heap has an unbounded worst case; writing to a file can block on I/O, and logging libraries often take a lock that another thread may hold. any of these turns a diagnostic into the deadline miss. keep the hot path to counters and fixed-size records pushed into a preallocated buffer, and let a background thread format and write them.

</details>

<details>
<summary>answer 4: three kinds of looseness</summary>

`sizeof(long)`: implementation-defined (documented by the implementation). argument order: unspecified (since C++17 the two calls are indeterminately sequenced, never interleaved). `INT_MAX + 1`: undefined behavior, and the optimizer may assume it never happens.

</details>

<details>
<summary>answer 5: noexcept and reallocation</summary>

reallocation offers the strong guarantee. if a move could throw halfway, the old buffer would already be partly moved from and could not be restored. `std::move_if_noexcept` therefore copies when the move is not `noexcept` and a copy constructor exists.

</details>

<details>
<summary>answer 6: a view into a temporary</summary>

the concatenation produces a temporary `std::string` that is destroyed at the end of the full-expression. `sv` points into freed memory, so any read is undefined behavior. a view never extends a lifetime.

</details>

<details>
<summary>answer 7: relaxed is not publication</summary>

relaxed operations create no synchronizes-with edge, so seeing `ready == true` does not make the payload write visible. the payload accesses are an unordered conflicting pair: a data race, which is undefined behavior. use `release` on the store and `acquire` on the load.

</details>

<details>
<summary>answer 8: the pimpl destructor</summary>

`std::unique_ptr<Impl>`'s deleter needs a complete `Impl` where the destructor is instantiated. an implicit destructor is inline in the header, where `Impl` is incomplete, so it fails to compile (libstdc++ reports "invalid application of `sizeof` to incomplete type"). declare `~Widget();` in the header and define it as `= default` in the `.cpp` after `Impl`; the same applies to the move operations.

</details>

<details>
<summary>mini exercise answer</summary>

the sink concept is already a seam, so the feature fits behind it as a decorator that satisfies `DetectionSink` by forwarding:

```cpp
template <DetectionSink Inner>
class TimingSink {                         // same concept in, same concept out
public:
    TimingSink(Inner& inner, LatencyHistogram& h) : inner_(inner), h_(h) {}
    void on_frame(std::uint64_t seq, std::span<const Detection> ds) {
        ScopeTimer span(h_);
        inner_.on_frame(seq, ds);
    }
    void on_fault(std::uint64_t seq, int code) { inner_.on_fault(seq, code); }
private:
    Inner& inner_;
    LatencyHistogram& h_;
};

// RecordingSink recorder; LatencyHistogram h; TimingSink timed(recorder, h);
// Pipeline pipeline(GateConfig{}, timed, fake_sensor);   // Pipeline is unchanged
```

no existing class changes (open/closed, [day 89](#day-89)), and the decorator inlines because the seam is compile-time. what it cannot measure: time spent in `gate`, and end-to-end latency from sensor to sink. the first needs timing inside `Processor`; the second needs a capture timestamp in `Frame`, a change to the message type itself. features that change what the data means belong in the types; features that observe it belong behind seams.

</details>

#### connections

the course ends where it started: with what the language promises and what you must promise in return. the production modules leaned on everything before them: benchmarking and cache behavior gave substance to container choices, the cost of allocation explained why the rule of zero, `reserve`, and the hidden costs of `std::function` and `shared_ptr` matter, and testing and observability turned dependency injection and RAII into practical habits. the pipeline showed that the hard part of combining features is deciding who owns what, who may block, and what can be substituted.

##### where to go next

you now have the core of modern C++17 and C++20 and, more importantly, the habit of asking what each feature costs and what it promises. C++23 is the natural next step, and most of it builds directly on this course:

- `std::expected<T, E>`: the result type [day 50](#day-50) and [day 53](#day-53) approximated with variants, now standard.
- `std::print` and `std::println`: `std::format` ([day 71](#day-71)) straight to output.
- deducing `this`: explicit object parameters that simplify CRTP ([day 97](#day-97)) and remove const/non-const duplication.
- `std::generator`: the coroutine generator you wrote by hand on [day 103](#day-103), ready-made.
- `std::mdspan`: multidimensional views over contiguous memory, `std::span` ([day 65](#day-65)) for matrices and images.
- `std::flat_map` and `std::flat_set`: sorted-vector associative containers, [day 34](#day-34)'s locality argument as a library type.

further out, the C++26 feature set includes language contracts (preconditions and postconditions as declarations, the formal version of [day 100](#day-100)'s API contracts) and static reflection, which lets code inspect types at compile time and will reshape serialization and boilerplate generation. treat both as directions to watch; check your compiler's status pages before relying on them.

the most effective practice from here is unglamorous: read compiler output on Compiler Explorer when you wonder what something costs, run your tests under sanitizers, measure before you optimize, and write down the tradeoffs you choose. the language will keep growing; the judgment you built over this course is what makes each new feature easy to place. thanks for reading, and enjoy the code you write next.

[back to the curriculum map](#curriculum)

---

<a id="cheat-sheet"></a>

## modern C++17/20 cheat sheet

a compact reference for after the course. the day numbers point back to the full explanations.

### initialization ([day 03](#day-03))

```cpp
int a;            // local: indeterminate value, reading it is UB
int b{};          // value-initialized: 0
int c{3.5};       // error: narrowing is rejected inside braces
auto d{1};        // int (C++17 rule); auto e = {1}; is std::initializer_list<int>
std::vector<int> v1(3, 1);  // {1, 1, 1}
std::vector<int> v2{3, 1};  // {3, 1}: braces prefer initializer_list constructors
Point p{.x = 1, .y = 2};    // C++20 designated initializers, in declaration order
```

### special members and ownership ([day 16](#day-16) to [day 28](#day-28))

| you declare | copy ops generated? | move ops generated? |
| --- | --- | --- |
| nothing | yes | yes |
| destructor | yes (deprecated) | no, copies are used instead |
| copy constructor or copy assignment | the other one yes (deprecated) | no |
| move constructor or move assignment | no (deleted) | only the one you wrote |

- **rule of zero:** hold resources in members that manage themselves (`std::vector`, `std::string`, `std::unique_ptr`) and declare no special members.
- **rule of five:** if you must write one of destructor, copy constructor, copy assignment, move constructor, or move assignment, think about all five.
- mark move operations `noexcept` so `std::vector` can move instead of copy when it reallocates.
- destructors are implicitly `noexcept` (unless a member or base says otherwise); never let them throw.

| signature | meaning |
| --- | --- |
| `void f(Widget&)` / `void f(const Widget&)` | borrow, must not be null |
| `void f(Widget*)` | borrow, may be null |
| `void f(std::unique_ptr<Widget>)` | takes ownership |
| `void f(std::unique_ptr<Widget>&)` | may reseat the caller's pointer (rare) |
| `void f(std::shared_ptr<Widget>)` | shares ownership (keeps it alive) |
| `void f(std::span<const T>)`, `void f(std::string_view)` | borrows a contiguous sequence |
| `std::unique_ptr<Widget> make()` | caller becomes the owner |

### value categories and moves ([day 11](#day-11), [day 21](#day-21), [day 42](#day-42))

```text
           expression
           /        \
      glvalue      rvalue
      /     \      /    \
  lvalue    xvalue     prvalue

lvalue:  has identity, not moved from implicitly   x, *p, a[i], f() returning T&
xvalue:  has identity, can be moved from           std::move(x), f() returning T&&
prvalue: no identity until materialized            42, T{}, f() returning T
```

- `std::move(x)` is only a cast to `T&&`; the move happens when a move constructor or assignment picks it up.
- `std::forward<T>(x)` keeps the caller's value category; use it only with forwarding references (`T&&` with deduced `T`, or `auto&&`).
- don't `return std::move(local);`: it blocks copy elision. returning a prvalue is guaranteed to be elided since C++17.
- a named rvalue reference is an lvalue.

### undefined, unspecified, implementation-defined ([day 13](#day-13))

| category | meaning | examples |
| --- | --- | --- |
| undefined | no requirements at all; the optimizer assumes it never happens | signed overflow, out-of-bounds access, use after free, data race, reading an uninitialized `int`, strict aliasing violation |
| unspecified | one of several valid outcomes, not documented | order of evaluation of function arguments, string literal storage overlap |
| implementation-defined | chosen and documented by the implementation | `sizeof(int)`, signedness of plain `char`, `CHAR_BIT`, right shift of a negative integer (before C++20) |

defenses: `-Wall -Wextra`, `-fsanitize=address,undefined` (and `thread` for races), `std::bit_cast` or `std::memcpy` instead of pointer type punning.

### containers and algorithms ([day 34](#day-34) to [day 38](#day-38))

| container | access | insert/erase | notes |
| --- | --- | --- | --- |
| `vector` | O(1) random | O(1) amortized at end, O(n) elsewhere | default choice; contiguous; reallocation invalidates everything |
| `array` | O(1) random | fixed size | no heap |
| `deque` | O(1) random | O(1) at both ends | chunked, not contiguous |
| `list` | O(n) | O(1) with an iterator | stable references, splicing; one allocation per node |
| `map` / `set` | O(log n) | O(log n) | ordered; node-based |
| `unordered_map` / `set` | O(1) average | O(1) average | hashing cost; rehash invalidates iterators |

```cpp
std::erase_if(v, [](const Track& t) { return t.stale; });      // C++20
v.erase(std::remove_if(v.begin(), v.end(), is_stale), v.end()); // C++17 equivalent
auto [it, inserted] = m.try_emplace(key, args...);             // no move-from if key exists
if (auto it = m.find(k); it != m.end()) use(it->second);        // C++17 if-initializer
```

lambda captures: `[=]` copies what is used (implicitly capturing `this` through `[=]` is deprecated in C++20), `[&]` references (beware escaping), `[p = std::move(ptr)]` init-capture, `[this]` captures the pointer, `[*this]` copies the object (C++17).

### C++17 at a glance ([module 8](#module-results), [module 9](#module-cpp17))

| feature | example |
| --- | --- |
| structured bindings | `for (const auto& [name, value] : config)` |
| `if`/`switch` initializers | `if (auto r = parse(s); r) { ... }` |
| `if constexpr` | `if constexpr (std::is_integral_v<T>) { ... }` |
| fold expressions | `(std::cout << ... << args);` / `(... && checks)` |
| CTAD | `std::pair p{1, 2.0};` `std::lock_guard lock{m};` |
| inline variables | `inline constexpr int kMaxJoints = 7;` in a header |
| guaranteed copy elision | returning a prvalue of a non-movable type works |
| nested namespaces | `namespace robot::control { }` |
| attributes | `[[nodiscard]]`, `[[maybe_unused]]`, `[[fallthrough]]` |
| `std::optional<T>` | maybe a value; `value_or`, `*opt` (UB if empty) |
| `std::variant<Ts...>` | one of several types; `std::visit`, `std::get_if` |
| `std::any` | any copyable type; `std::any_cast`; rarely the right tool |
| `std::string_view` | non-owning, not null-terminated; never outlive the source |
| `std::filesystem` | `path`, `exists`, `directory_iterator`, `error_code` overloads |
| `std::from_chars`, `std::to_chars` | locale-free, allocation-free number conversion |
| `std::pmr` | memory resources: `monotonic_buffer_resource`, pool resources |
| `std::scoped_lock`, `std::shared_mutex` | multi-mutex locking, reader/writer locks |

```cpp
template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };
template <class... Fs> overloaded(Fs...) -> overloaded<Fs...>;  // not needed in C++20

std::visit(overloaded{
    [](const Detection& d) { handle(d); },
    [](const Heartbeat&)   { /* ignore */ },
}, message);
```

### C++20 at a glance ([module 10](#module-cpp20-generic), [module 11](#module-cpp20-everyday))

| feature | example |
| --- | --- |
| concepts | `template <std::integral T>`, `void f(std::floating_point auto x)` |
| custom concept | `template <class T> concept Sensor = requires(T s) { { s.read() } -> std::convertible_to<double>; };` |
| ranges and views | `v \| std::views::filter(pred) \| std::views::transform(f)` |
| projections | `std::ranges::sort(tracks, {}, &Track::range_m);` |
| `std::span<T>` | `void process(std::span<const float> samples)` |
| three-way comparison | `auto operator<=>(const T&) const = default;` |
| `consteval` / `constinit` | forced compile-time call / compile-time-initialized static |
| `std::format` | `std::format("{:>8.3f} m", range)` (GCC 13+, Clang 17+, MSVC 19.29+) |
| `std::jthread` | joins on destruction; `std::stop_token` for cancellation |
| `std::latch`, `std::barrier`, `std::counting_semaphore` | one-shot sync, phased sync, limited concurrency |
| atomic `wait`/`notify_one` | block on an atomic value change |
| `std::source_location` | file, line, function for logging without macros |
| `<bit>` | `std::bit_cast`, `std::popcount`, `std::endian` |
| container helpers | `contains`, `starts_with`, `ends_with`, `std::erase_if`, `std::ssize` |
| templated lambdas | `[]<class T>(const std::vector<T>& v) { ... }` |
| coroutines | `co_await`, `co_yield`, `co_return` (machinery only; no ready-made types) |
| modules | `export module sensors;` / `import sensors;` (tooling still maturing) |

### not in C++20 (easy to mix up)

| C++23 | what to use in C++20 |
| --- | --- |
| `std::expected` | `std::variant<T, Error>`, a small result type, or exceptions |
| `std::print`, `std::println` | `std::cout << std::format(...)` or `std::fputs` |
| `std::ranges::to` | construct the container from `begin()`/`end()` of the view |
| `std::views::zip`, `enumerate`, `chunk` | index loops or a hand-written helper |
| `std::generator` | a hand-written coroutine type or a library (cppcoro) |
| deducing `this` | CRTP |
| `std::mdspan` | `std::span` plus manual index math |
| `std::move_only_function` | `std::function` (requires copyable callables) or a custom wrapper |
| `std::flat_map` | sorted `std::vector` of pairs plus `std::lower_bound` |
| `if consteval` | `if (std::is_constant_evaluated())` |

### concurrency rules of thumb ([module 12](#module-threads), [module 13](#module-async))

- a data race (unsynchronized conflicting access, at least one write) is UB. a race condition (wrong timing logic) can exist without one.
- prefer `std::jthread` with `std::stop_token` over `std::thread` plus a flag; never let a joinable `std::thread` be destroyed.
- keep a mutex next to the data it protects, lock with `std::scoped_lock`, keep critical sections short, never call unknown code (callbacks) while holding a lock.
- always wait on a condition variable with a predicate: `cv.wait(lock, [&] { return !queue.empty() || closed; });`
- the future returned by `std::async` blocks in its destructor; keep it.
- atomics: default to `seq_cst`; use `release` on the publishing store and `acquire` on the observing load for the flag pattern; `relaxed` only for independent counters.
- lock ordering or `std::scoped_lock` prevents lock-order deadlocks. confinement and message passing prevent most of the rest.

### design reminders ([module 14](#module-design), [module 15](#module-abstractions))

| need | first choice | alternative |
| --- | --- | --- |
| open set of types, runtime choice | virtual interface | type erasure for value semantics |
| closed set of types | `std::variant` + `std::visit` | virtual interface |
| zero-overhead customization | template + concept | CRTP |
| store any callable | `std::function` | template parameter |
| testable dependency | constructor injection of an interface or a concept-constrained template | `std::function` seam, link-time seam |
| stable ABI | pimpl | C interface |

### performance habits ([module 16](#module-performance), [module 17](#module-production))

- measure first: optimized build, `std::chrono::steady_clock` or a benchmark library, many repetitions, report median and spread.
- contiguous data and predictable access patterns usually beat clever algorithms on small and medium inputs; confirm with a profiler and hardware counters.
- reserve, reuse, and preallocate; keep allocations out of real-time loops; consider `std::pmr` arenas.
- optimize where the profile says, and write down why the code is now less obvious.

### compiler flags worth knowing

```sh
-std=c++20 -Wall -Wextra -pedantic -Werror=return-type   # language mode and warnings
-O2 -g                                                     # optimized, still debuggable
-fsanitize=address,undefined                               # ASan + UBSan (debug/test builds)
-fsanitize=thread                                          # TSan, in a separate build
-D_GLIBCXX_ASSERTIONS                                      # bounds-checked libstdc++ operator[]
```

<a id="references"></a>

## references for deeper study

a short, curated list. where a resource covers several modules, it is listed once under the area where it helps most.

### primary references

- **cppreference.com**: <https://en.cppreference.com/w/cpp>. the day-to-day reference for the language and library, with a version tag on every feature. its compiler support tables (<https://en.cppreference.com/w/cpp/compiler_support>) tell you which compiler version implements which C++17/20/23 feature.
- **the C++ Core Guidelines** (Stroustrup and Sutter, eds.): <https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines>. rules with rationale for resource management (R), interfaces (I), functions (F), classes (C), concurrency (CP), and error handling (E). most `clang-tidy` `cppcoreguidelines-*` checks trace back to it.
- **the working draft of the standard**: <https://eel.is/c++draft/>. a browsable, linkable version of the latest draft. use it when cppreference is not precise enough; for a specific published standard, look for the final draft of that version (N4659 for C++17, N4861 for C++20).
- **isocpp.org**: <https://isocpp.org>. the Standard C++ Foundation's site, including the C++ FAQ and links to proposals and trip reports.

### books

| book | best for |
| --- | --- |
| Bjarne Stroustrup, *A Tour of C++*, 3rd edition (2022) | a fast, authoritative tour of modern C++ up to C++20 |
| Scott Meyers, *Effective Modern C++* (2014) | move semantics, forwarding references, smart pointers, lambdas ([module 3](#module-lifecycle) to [module 7](#module-generic)); written for C++11/14 but still the clearest treatment of those topics |
| Nicolai Josuttis, *C++17: The Complete Guide* (2019) | every C++17 feature in depth ([module 8](#module-results), [module 9](#module-cpp17)) |
| Nicolai Josuttis, *C++20: The Complete Guide* (2022) | concepts, ranges, `<=>`, `span`, `jthread`, coroutines, modules ([module 10](#module-cpp20-generic) to [module 15](#module-abstractions)) |
| Nicolai Josuttis, *C++ Move Semantics: The Complete Guide* (2020) | everything about moves, including the edge cases ([day 21](#day-21)) |
| Anthony Williams, *C++ Concurrency in Action*, 2nd edition (2019) | threads, synchronization, and the memory model ([module 12](#module-threads), [module 13](#module-async)) |
| Klaus Iglberger, *C++ Software Design* (2022) | design principles, patterns, and type erasure in modern C++ ([module 14](#module-design), [module 15](#module-abstractions)) |
| Fedor Pikus, *The Art of Writing Efficient Programs* (2021) | performance, the memory hierarchy, and concurrency performance ([module 16](#module-performance)) |
| Michael Feathers, *Working Effectively with Legacy Code* (2004) | seams, characterization tests, and safe refactoring ([day 91](#day-91) and [day 114](#day-114)) |
| Herb Sutter, *Exceptional C++* (1999) and *More Exceptional C++* (2001) | exception safety and the reasoning behind the guarantees ([day 49](#day-49)) |

### talks and articles

- Herb Sutter, "atomic<> Weapons: The C++ Memory Model and Modern Hardware" (C++ and Beyond 2012): the clearest long-form explanation of acquire/release and sequential consistency ([day 84](#day-84)).
- Sean Parent, "Inheritance Is the Base Class of Evil" (GoingNative 2013) and "C++ Seasoning" (GoingNative 2013): value semantics with runtime polymorphism, and "no raw loops" ([day 36](#day-36) and [day 97](#day-97)).
- Mike Acton, "Data-Oriented Design and C++" (CppCon 2014): thinking in data and access patterns ([day 108](#day-108)).
- Chandler Carruth, "Tuning C++: Benchmarks, and CPUs, and Compilers! Oh My!" (CppCon 2015): how to benchmark without fooling yourself ([day 105](#day-105)).
- Ulrich Drepper, "What Every Programmer Should Know About Memory" (2007): the deep background on caches and memory ([day 108](#day-108)).
- Lewis Baker, "Asymmetric Transfer" blog series: <https://lewissbaker.github.io>. the best explanation of how C++20 coroutines work under the hood ([day 102](#day-102)).
- Hyrum's law: <https://www.hyrumslaw.com>. one paragraph that will change how you think about API changes ([day 99](#day-99)).
- Herb Sutter, "Guru of the Week" archive: <https://herbsutter.com/gotw/>. short, deep puzzles in the same spirit as this course's challenges.

### tools for exploring and verifying

| tool | use |
| --- | --- |
| Compiler Explorer, <https://godbolt.org> | compile snippets on many compilers and standards; read the generated assembly |
| C++ Insights, <https://cppinsights.io> | see what the compiler generates for lambdas, range-for, structured bindings, coroutines |
| Quick C++ Benchmark, <https://quick-bench.com> | run small Google Benchmark comparisons online (results are indicative, not your production hardware) |
| sanitizers (ASan, UBSan, TSan) | GCC and Clang documentation: <https://clang.llvm.org/docs/AddressSanitizer.html> and sibling pages |
| clang-tidy, <https://clang.llvm.org/extra/clang-tidy/> | `modernize-*`, `bugprone-*`, `performance-*`, and `cppcoreguidelines-*` checks ([day 114](#day-114)) |
| Google Benchmark, <https://github.com/google/benchmark> | microbenchmarks with statistics ([day 105](#day-105)) |
| GoogleTest and Catch2 | unit testing frameworks ([day 112](#day-112)) |
| {fmt}, <https://fmt.dev> | the library `std::format` was standardized from; use it on toolchains without `<format>` ([day 71](#day-71)) |

### staying current

- **C++23 and later:** cppreference marks every feature with its version, and the compiler support page shows what you can use today. the forward notes on [day 119](#day-119) list the C++23 features most likely to matter to you next.
- **trip reports:** after each ISO committee meeting, several committee members (Herb Sutter among them) publish summaries of what changed. they are the fastest way to follow the language's direction.
