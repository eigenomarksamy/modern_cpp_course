<a id="introduction"></a>

## introduction and learning philosophy

You already write C++ for a living. You have shipped code that runs on robots, servers, or build farms, and you have debugged the kind of crash that only happens in release builds on a Tuesday. This course isn't here to teach you C++ from scratch. It is a structured way to revisit the parts of the language you use every day, understand the mechanics underneath them, and get fluent with the C++17 and C++20 features that make production code safer and clearer.

It runs for 56 days, in 8 weeks of 7 days. Each day takes 5 to 10 minutes to read, code included. Six days a week teach something new; the seventh is a short review with questions and a small exercise.

### how this course thinks

- **mechanics before features.** Move semantics make sense once value categories do. `std::string_view` is obvious once lifetime is. So the first weeks rebuild the foundations, and later features are explained in terms of them.
- **examples over prose.** Every lesson leans on small, purposeful code: naive version, then improved version; buggy version, then fixed version; "predict the output" puzzles. Read the code as carefully as the text.
- **judgment over rules.** "Never use raw pointers", "always use algorithms", "SOLID everything": rules like these are compressed experience, and they leak. Each lesson tries to say when a feature is the right tool, when it is not, and what it costs.
- **design is everywhere.** Ownership, coupling, error handling, testability, and compile-time versus runtime tradeoffs show up in every week, not only in the design week.
- **honesty about performance.** You will not find "X is 3x faster" here. You will find complexity, mechanisms (allocations, cache lines, indirections), and how to measure.

### how each day is structured

Instructional days follow the same shape, so you always know where you are:

| section | what it gives you |
| --- | --- |
| the idea | a question, a bug, or a misconception that motivates the topic |
| understanding the concept | the mechanics and the relevant rules, briefly |
| in code | 2 or 3 short examples, often before/after or buggy/fixed |
| in practice | where it matters in real systems |
| watch out for | the most common trap or tradeoff |
| the takeaway | one sentence worth remembering |
| optional challenge | a 2-minute puzzle, with a collapsed answer |

Review days (7, 14, 21, 28, 35, 42, 49, 56) have a recap, review questions (including spaced-repetition questions from earlier weeks), a mini exercise, collapsed answers, and a note on how the week connects to the rest.

### conventions used in the lessons

- Each day lists its **standard** (`C++17` or `C++20`): the minimum language version its examples need. If a single snippet needs something newer, it says so. C++23 features appear only as clearly labelled forward notes.
- `// prints: ...` shows expected output. `// BUG:` marks code that is wrong on purpose.
- Three terms are used precisely, because the difference matters:
  - **undefined behavior (UB):** the standard places no requirements on the program. The optimizer is allowed to assume it never happens, which is why UB bugs can look like time travel.
  - **unspecified behavior:** the program does one of several permitted things, and the implementation doesn't have to tell you which (for example, the order in which function arguments are evaluated).
  - **implementation-defined behavior:** unspecified, but the implementation must document its choice (for example, `sizeof(long)`).
- Cross references look like [day 05](#day-05) and jump to that lesson.

### setting up a playground

Any recent compiler works. A reasonable baseline:

```sh
# GCC 13+ or Clang 17+ for full C++20 library coverage including <format>
g++ -std=c++20 -Wall -Wextra -pedantic -g -fsanitize=address,undefined main.cpp -o main
./main
```

Sanitizers are available with GCC and Clang on Linux and macOS (MSVC supports AddressSanitizer). [Compiler Explorer](https://godbolt.org) is ideal for the short examples, and it lets you compare compilers and look at the generated assembly when a lesson talks about what the compiler does.

### how to use it

Read one day at a time, ideally with a compiler open. Do the optional challenge if it catches your interest, and don't skip the review days: they are short, and retrieval practice is what makes the material stick. Tick off days in the [progress checklist](#progress-checklist) as you go.

Weeks 1 to 4 form a complete, standalone C++17 refresher. Weeks 5 to 8 build on it with C++20, concurrency, design, and production engineering, ending with a small program on day 55 that brings the pieces together.

This is version 1.0 of the course. Each day is its own source file, so lessons can be expanded, corrected, or updated for newer standards one at a time.
