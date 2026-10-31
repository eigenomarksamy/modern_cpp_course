# day 21 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic`; scratch folder outside the repo. Snippets extracted mechanically from the lesson.

- question 2 (by-value capture snapshot): printed `3`, matching the answer.
- question 3 (forwarding versus rvalue reference declarations): compiled clean with a stub `make_frame`.
- question 5 (lifetime extension through member access versus a returned reference): compiled clean with no warnings (GCC 12 has no `-Wdangling-reference`; that arrived in GCC 13). Using `a` ran correctly. The dangling `b` was not used at run time (UB; no sanitizers on this mingw build).
- question 6 (user-declared destructor suppresses move): in a probe class with a destructor and a large vector member, `Probe q(std::move(p))` did not reuse the source buffer (a copy happened); `-Wdeprecated-copy-dtor` reported `implicitly-declared 'Probe::Probe(const Probe&)' is deprecated`.
- mini exercise: the buggy original compiles clean (the bugs are UB at run time, not compile errors); the buggy version was not run. The solution compiled clean and ran: ids `4 3 5` for five detections with one invalid, `9` for a two-element input with one invalid, and an empty result for empty input.
- not checked: question 1 and 4 answers are reasoning about documented container and `move_if_noexcept` rules (`move_if_noexcept` behavior was run in the day 20 check).
