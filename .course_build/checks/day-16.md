# day 16 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic` unless noted; scratch folder outside the repo. Snippets were extracted from the lesson file mechanically.

- telemetry algorithms (`any_fault`, `first_over`, `scaled`, `energy`): compiled clean, ran with a driver; results as expected.
- erase-remove predict-the-output: compiled clean, printed `5` then `3`, matching the comments. Separately printed the buggy vector's contents: `1 3 5 5 6` on libstdc++, as stated (tail values are unspecified in general).
- C++20 `std::erase_if(w, is_even)`: compiled with `-std=c++20`, returned 3 and left size 3.
- `stable_partition` + `stable_sort` display ordering: compiled clean, printed `3 1 4 2 5`, matching the comment.
- `std::sort` on `std::list`: fails with `no match for 'operator-'` in `bits/stl_algo.h`, as described.
- `std::accumulate(..., 0)` over doubles: printed `0` (and `1.5` with `0.0`); no warning with `-Wall -Wextra -pedantic`, nor with `-Wconversion` added, as stated.
- `std::execution::par` sort: compiles and runs on GCC 12 here; preprocessor shows `_PSTL_PAR_BACKEND_SERIAL` defined (no TBB installed), supporting the "serial backend" statement. No parallel speedup was measured (no TBB available). MSVC behavior stated from documentation, not run.
- optional challenge (`transform` into an empty vector): not run, it is UB; no sanitizers on this mingw build.
