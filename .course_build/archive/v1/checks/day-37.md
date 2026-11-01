# day 37 compile checks

Toolchain: MSYS2 g++ 12.1.0 (winpthreads), flags `-std=c++17 -Wall -Wextra -pedantic -pthread`, scratch folder outside the repo.

- counter (racy and mutex versions) in one program: compiles cleanly. Mutex version printed `2000000` on all 10 runs (guaranteed by the lock, not by the runs).
- racy counter: observed only to describe the "idea" anecdote, not as proof of anything (it is UB). `-O0`: 1,033,086 / 1,224,664 / 1,520,645 / 1,309,438 / 1,075,882 over 5 runs. `-O2`: 2,000,000 on 5 runs; `-S` output shows the loop compiled to a single `addl $1000000, frames(%rip)` (no lock prefix), which is what the lesson says.
- `TrackTable` with `insert_if_absent` and `Synchronized<T>` with the usage lines from the comments: compiles and runs; a `static_assert` confirmed that a lambda returning `auto&` through `with_lock` yields a `std::vector<Detection>` copy, and a void-returning lambda works with the `auto` return type.
- optional challenge (`std::unique_lock<std::mutex>(m_);`): compiles; GCC 12 `-Wall` emits `-Wparentheses` "unnecessary parentheses in declaration of 'm_'", and `-Wshadow` reports shadowing a member. The lesson originally said it compiled silently under `-Wall -Wextra`; corrected after this check.
- `find` returning `const Track&` (watch out): fragment, not compiled separately (same members as the compiled class).
- ThreadSanitizer: not available on this mingw build; the lesson describes it without claiming it was run.
