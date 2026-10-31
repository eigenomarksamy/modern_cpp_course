<a id="references"></a>

## references for deeper study

A short, curated list. Where a resource covers several weeks, it is listed once under the area where it helps most.

### primary references

- **cppreference.com**: <https://en.cppreference.com/w/cpp>. The day-to-day reference for the language and library, with a version tag on every feature. Its compiler support tables (<https://en.cppreference.com/w/cpp/compiler_support>) tell you which compiler version implements which C++17/20/23 feature.
- **the C++ Core Guidelines** (Stroustrup and Sutter, eds.): <https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines>. Rules with rationale for resource management (R), interfaces (I), functions (F), classes (C), concurrency (CP), and error handling (E). Most `clang-tidy` `cppcoreguidelines-*` checks trace back to it.
- **the working draft of the standard**: <https://eel.is/c++draft/>. A browsable, linkable version of the latest draft. Use it when cppreference is not precise enough; for a specific published standard, look for the final draft of that version (N4659 for C++17, N4861 for C++20).
- **isocpp.org**: <https://isocpp.org>. The Standard C++ Foundation's site, including the C++ FAQ and links to proposals and trip reports.

### books

| book | best for |
| --- | --- |
| Bjarne Stroustrup, *A Tour of C++*, 3rd edition (2022) | a fast, authoritative tour of modern C++ up to C++20 |
| Scott Meyers, *Effective Modern C++* (2014) | move semantics, forwarding references, smart pointers, lambdas (weeks 2 and 3); written for C++11/14 but still the clearest treatment of those topics |
| Nicolai Josuttis, *C++17: The Complete Guide* (2019) | every C++17 feature in depth (week 4) |
| Nicolai Josuttis, *C++20: The Complete Guide* (2022) | concepts, ranges, `<=>`, `span`, `jthread`, coroutines, modules (weeks 5 to 7) |
| Nicolai Josuttis, *C++ Move Semantics: The Complete Guide* (2020) | everything about moves, including the edge cases (day 10) |
| Anthony Williams, *C++ Concurrency in Action*, 2nd edition (2019) | threads, synchronization, and the memory model (week 6) |
| Klaus Iglberger, *C++ Software Design* (2022) | design principles, patterns, and type erasure in modern C++ (week 7) |
| Fedor Pikus, *The Art of Writing Efficient Programs* (2021) | performance, the memory hierarchy, and concurrency performance (week 8) |
| Michael Feathers, *Working Effectively with Legacy Code* (2004) | seams, characterization tests, and safe refactoring (days 44 and 54) |
| Herb Sutter, *Exceptional C++* (1999) and *More Exceptional C++* (2001) | exception safety and the reasoning behind the guarantees (day 20) |

### talks and articles

- Herb Sutter, "atomic<> Weapons: The C++ Memory Model and Modern Hardware" (C++ and Beyond 2012): the clearest long-form explanation of acquire/release and sequential consistency (day 40).
- Sean Parent, "Inheritance Is the Base Class of Evil" (GoingNative 2013) and "C++ Seasoning" (GoingNative 2013): value semantics with runtime polymorphism, and "no raw loops" (days 16 and 46).
- Mike Acton, "Data-Oriented Design and C++" (CppCon 2014): thinking in data and access patterns (day 51).
- Chandler Carruth, "Tuning C++: Benchmarks, and CPUs, and Compilers! Oh My!" (CppCon 2015): how to benchmark without fooling yourself (day 50).
- Ulrich Drepper, "What Every Programmer Should Know About Memory" (2007): the deep background on caches and memory (day 51).
- Lewis Baker, "Asymmetric Transfer" blog series: <https://lewissbaker.github.io>. The best explanation of how C++20 coroutines work under the hood (day 48).
- Hyrum's law: <https://www.hyrumslaw.com>. One paragraph that will change how you think about API changes (day 47).
- Herb Sutter, "Guru of the Week" archive: <https://herbsutter.com/gotw/>. Short, deep puzzles in the same spirit as this course's challenges.

### tools for exploring and verifying

| tool | use |
| --- | --- |
| Compiler Explorer, <https://godbolt.org> | compile snippets on many compilers and standards; read the generated assembly |
| C++ Insights, <https://cppinsights.io> | see what the compiler generates for lambdas, range-for, structured bindings, coroutines |
| Quick C++ Benchmark, <https://quick-bench.com> | run small Google Benchmark comparisons online (results are indicative, not your production hardware) |
| sanitizers (ASan, UBSan, TSan) | GCC and Clang documentation: <https://clang.llvm.org/docs/AddressSanitizer.html> and sibling pages |
| clang-tidy, <https://clang.llvm.org/extra/clang-tidy/> | `modernize-*`, `bugprone-*`, `performance-*`, and `cppcoreguidelines-*` checks (day 54) |
| Google Benchmark, <https://github.com/google/benchmark> | microbenchmarks with statistics (day 50) |
| GoogleTest and Catch2 | unit testing frameworks (day 53) |
| {fmt}, <https://fmt.dev> | the library `std::format` was standardized from; use it on toolchains without `<format>` (day 34) |

### staying current

- **C++23 and later:** cppreference marks every feature with its version, and the compiler support page shows what you can use today. The forward notes on [day 56](#day-56) list the C++23 features most likely to matter to you next.
- **trip reports:** after each ISO committee meeting, several committee members (Herb Sutter among them) publish summaries of what changed. They are the fastest way to follow the language's direction.
