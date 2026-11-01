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
| Scott Meyers, *Effective Modern C++* (2014) | move semantics, forwarding references, smart pointers, lambdas ([[module:lifecycle]] to [[module:generic]]); written for C++11/14 but still the clearest treatment of those topics |
| Nicolai Josuttis, *C++17: The Complete Guide* (2019) | every C++17 feature in depth ([[module:results]], [[module:cpp17]]) |
| Nicolai Josuttis, *C++20: The Complete Guide* (2022) | concepts, ranges, `<=>`, `span`, `jthread`, coroutines, modules ([[module:cpp20-generic]] to [[module:abstractions]]) |
| Nicolai Josuttis, *C++ Move Semantics: The Complete Guide* (2020) | everything about moves, including the edge cases ([[move-semantics]]) |
| Anthony Williams, *C++ Concurrency in Action*, 2nd edition (2019) | threads, synchronization, and the memory model ([[module:threads]], [[module:async]]) |
| Klaus Iglberger, *C++ Software Design* (2022) | design principles, patterns, and type erasure in modern C++ ([[module:design]], [[module:abstractions]]) |
| Fedor Pikus, *The Art of Writing Efficient Programs* (2021) | performance, the memory hierarchy, and concurrency performance ([[module:performance]]) |
| Michael Feathers, *Working Effectively with Legacy Code* (2004) | seams, characterization tests, and safe refactoring ([[dependency-injection]] and [[legacy-refactoring]]) |
| Herb Sutter, *Exceptional C++* (1999) and *More Exceptional C++* (2001) | exception safety and the reasoning behind the guarantees ([[exception-safety]]) |

### talks and articles

- Herb Sutter, "atomic<> Weapons: The C++ Memory Model and Modern Hardware" (C++ and Beyond 2012): the clearest long-form explanation of acquire/release and sequential consistency ([[memory-model]]).
- Sean Parent, "Inheritance Is the Base Class of Evil" (GoingNative 2013) and "C++ Seasoning" (GoingNative 2013): value semantics with runtime polymorphism, and "no raw loops" ([[algorithms]] and [[static-polymorphism]]).
- Mike Acton, "Data-Oriented Design and C++" (CppCon 2014): thinking in data and access patterns ([[data-oriented-design]]).
- Chandler Carruth, "Tuning C++: Benchmarks, and CPUs, and Compilers! Oh My!" (CppCon 2015): how to benchmark without fooling yourself ([[benchmarking]]).
- Ulrich Drepper, "What Every Programmer Should Know About Memory" (2007): the deep background on caches and memory ([[data-oriented-design]]).
- Lewis Baker, "Asymmetric Transfer" blog series: <https://lewissbaker.github.io>. the best explanation of how C++20 coroutines work under the hood ([[coroutines]]).
- Hyrum's law: <https://www.hyrumslaw.com>. one paragraph that will change how you think about API changes ([[api-contracts]]).
- Herb Sutter, "Guru of the Week" archive: <https://herbsutter.com/gotw/>. short, deep puzzles in the same spirit as this course's challenges.

### tools for exploring and verifying

| tool | use |
| --- | --- |
| Compiler Explorer, <https://godbolt.org> | compile snippets on many compilers and standards; read the generated assembly |
| C++ Insights, <https://cppinsights.io> | see what the compiler generates for lambdas, range-for, structured bindings, coroutines |
| Quick C++ Benchmark, <https://quick-bench.com> | run small Google Benchmark comparisons online (results are indicative, not your production hardware) |
| sanitizers (ASan, UBSan, TSan) | GCC and Clang documentation: <https://clang.llvm.org/docs/AddressSanitizer.html> and sibling pages |
| clang-tidy, <https://clang.llvm.org/extra/clang-tidy/> | `modernize-*`, `bugprone-*`, `performance-*`, and `cppcoreguidelines-*` checks ([[legacy-refactoring]]) |
| Google Benchmark, <https://github.com/google/benchmark> | microbenchmarks with statistics ([[benchmarking]]) |
| GoogleTest and Catch2 | unit testing frameworks ([[testing]]) |
| {fmt}, <https://fmt.dev> | the library `std::format` was standardized from; use it on toolchains without `<format>` ([[format]]) |

### staying current

- **C++23 and later:** cppreference marks every feature with its version, and the compiler support page shows what you can use today. the forward notes on [[review-final]] list the C++23 features most likely to matter to you next.
- **trip reports:** after each ISO committee meeting, several committee members (Herb Sutter among them) publish summaries of what changed. they are the fastest way to follow the language's direction.
