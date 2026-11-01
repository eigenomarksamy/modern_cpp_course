# day 28 compile checks

Toolchain: MSYS2 g++ 12.1.0. Flags: `-std=c++17 -Wall -Wextra -pedantic`. Scratch: `$TEMP/claude/cpp-week-4/`.

- Question 1: `auto& [id, r] = make_track();` fails (`cannot bind non-const lvalue reference ... to an rvalue`); `const auto&` and `auto&&` forms compile and run, and the `auto&&` binding is modifiable, as the answer says.
- Question 2: the eager `static_assert(false)` behavior was checked on day 23 (rejected by GCC 12 in C++17, C++20, and C++2b modes, even uninstantiated).
- Question 3: an empty `std::optional<double>` compared `< 80.0` yields `true` (printed `1`).
- Question 5: the dangling `Frame::name()` compiles with no warning on GCC 12; the dangling itself is UB and was not executed.
- Question 6: the `const std::string&` lifetime-extended temporary prints `xy`. The `string_view` case was covered by day 26's checks (compiles silently).
- Question 7: `(sink(std::forward<Ts>(xs)), ...)` called `sink(int&)`, `sink(int&&)`, `sink(int&)` for `emit(v, 2, v)`, in order.
- Mini exercise: the legacy `parse_limit`/`load` and the modernized version compiled together and were run on six inputs. Both accept `max_vel=1.5` and `max_jerk=3e2`; both reject `max_acc=2.5x` and `noeq`; the old version accepts `max_vel= 1.5` and `max_vel=+1.5` while the new one rejects them, matching the stated behavior changes. Locale-dependence of `strtod` was not exercised.
