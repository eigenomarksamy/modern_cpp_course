# compile checks: day 52

Toolchain: MSYS2 g++ 12.1.0 (x86-64, Windows), scratch folder outside the repo.

- **all three cpp blocks extracted verbatim** from the lesson: the `alloc_counter.cpp` block (with `count_allocs`) compiled as its own translation unit; `process_frame` (pmr) and `LocalPlanner` plus its steady-state test compiled together with a small driver (`Obstacle` definition, `main`). Flags: `g++ -std=c++17 -Wall -Wextra -pedantic -O2 -static`. No warnings; ran, test passed.
- **allocation counts quoted in the lesson** (6-char string 0, 22-char string 1, `std::function` with `std::array<double, 8>` capture 1, `make_shared<int>` 1, `shared_ptr<int>(new int)` 2, 100 `std::map` inserts 100, 1,000 `push_back` without reserve 11, with reserve 1) were observed with this toolchain, statically linked, at `-O0` and `-O2`. They are labelled as libstdc++/GCC 12 details in the lesson.
- **DLL caveat observed**: with the default dynamic libstdc++ on MinGW, string allocations were not counted (0 for the 22-char string) until linking with `-static`.
- **aligned overloads**: verified that copying a `std::pmr::vector` lands on the default resource (not the arena) and that libstdc++'s default resource allocated through `operator new(size_t, align_val_t)` (only counted after replacing the aligned overloads in a separate test TU). Moving kept the arena. `null_memory_resource` upstream threw `bad_alloc` on overflow.
- **challenge answer verified**: `pmr::vector<pmr::string>::push_back("long literal")` caused 1 heap allocation (the temporary), `emplace_back` 0, and `pmr::vector<std::string>::emplace_back` 1.
- **GCC 12 false positive**: with the replacement operators in the same TU as their callers, `-O2` emits `-Wmismatched-new-delete` (free on pointer from operator new). Putting the replacement in its own TU, as the lesson recommends, avoids it.
- Not checked: heaptrack, massif (Linux tools, not available); exception-object allocation via `malloc` is from the Itanium ABI runtime design (libsupc++ `__cxa_allocate_exception`), not tested here.
