# day 15 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic`, scratch folder outside the repo.

- invalidation bug and fix (`annotate`, `annotate_fixed`): compiled with no warnings; ran the fixed version in a small driver. The buggy version was not run (it is UB only when reallocation happens; no sanitizers on this mingw build).
- `try_emplace` / `insert_or_assign` / `extract` / `merge` example: compiled clean, ran. Output `0 1`, `0 70`, `2 1`, matching the comments.
- `emplace_back` versus `push_back`: compiled clean and ran (row of 1,000,000 confirmed). With the commented-out `rows.push_back(1'000'000)` enabled: error `no matching function for call to push_back(int)`, as described. The leak on throwing growth was not demonstrated (would need allocation failure injection).
- optional challenge: ran the sequence with capacity printing; libstdc++ gives capacity 4 after `reserve(4)`, 4 after the first `push_back`, 8 after the second, confirming the answer's libstdc++ statement.
- not checked: MSVC growth factor (1.5x) is stated from documentation and common knowledge, not run here.
