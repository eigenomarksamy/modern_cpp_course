<a id="introduction"></a>

## introduction and learning philosophy

you already write C++ for a living. you have shipped code that runs on robots, servers, or build farms, and you have debugged the kind of crash that only happens in release builds on a Tuesday. this course isn't here to teach you C++ from scratch. it is a structured way to revisit the parts of the language you use every day, understand the mechanics underneath them, and get fluent with the C++17 and C++20 features that make production code safer and clearer.

the course has {{lesson_count}} daily lessons in {{module_count}} modules: {{instructional_count}} lessons that teach one idea each, and {{review_count}} short reviews, one at the end of every module. each day takes about 5 to 10 minutes of focused reading, code included. the length of the course follows from the material: a dense topic gets several days, each with one clear objective, rather than one day that tries to cover everything.

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
- cross references look like [[build-pipeline]] and jump to that lesson.

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

the modules through [[review-cpp17]] form a complete, standalone C++17 refresher. the rest builds on it with C++20, concurrency, design, and production engineering, ending with a small program that brings the pieces together.

this is version {{version}} of the course. each day is its own source file, so lessons can be expanded, corrected, split, or updated for newer standards one at a time.
