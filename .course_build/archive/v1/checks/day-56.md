# compile checks: day 56

Toolchain: MSYS2 g++ 12.1.0 (Windows), scratch folder outside the repo.

- **mini exercise answer (`TimingSink` decorator)**: the cpp block was extracted verbatim from the lesson and compiled together with the complete day 55 program (parts 1 to 4, with a replacement `main` that wraps `RecordingSink` in `TimingSink`) and day 53's `LatencyHistogram`/`ScopeTimer`. `g++ -std=c++20 -Wall -Wextra -pedantic -O2 -pthread`: no warnings. Ran: 3 frames recorded, 3 sink calls timed. CTAD deduced both `TimingSink<RecordingSink>` and `Pipeline<TimingSink<RecordingSink>>`, and `Pipeline` needed no edits.
- **answer 3 (pmr copy)**: verified with `-std=c++17` that `std::pmr::vector<int> a = v;` does not use the arena and `std::pmr::vector<int> b(v, &arena);` does.
- **answer 12 (pimpl)**: verified that an implicit destructor with `std::unique_ptr<Impl>` of incomplete `Impl` fails to compile with libstdc++ ("invalid application of 'sizeof' to incomplete type").
- **other answers** (UB/unspecified/implementation-defined classification, `move_if_noexcept`, vector reference invalidation, `string_view` dangling, `filter_view` begin caching, relaxed vs acquire/release) are restatements of facts compile-checked or documented on earlier days; not re-run here.
- **where to go next**: C++23 and C++26 features are named as forward-looking only; no C++23 code is presented. C++26 contracts and reflection are described as directions with a pointer to compiler status pages, not as available features.
