# day 20 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic`; scratch folder outside the repo. Snippets extracted mechanically from the lesson.

- `TrackTable` (`add_broken`, `add` with rollback): compiled clean; driver confirmed the duplicate-id path throws `invalid_argument` with the stated message. The broken-invariant path was not exercised (would need allocation failure injection).
- `ControllerConfig` reload with `noexcept` swap: compiled clean with a stub `parse`; ran a successful reload and a throwing reload.
- catch by value / `throw e;`: GCC warns `catching polymorphic type 'class std::exception' by value [-Wcatch-value=]`; `what()` printed `std::exception` on libstdc++; the outer handler caught only the base (`base only`), not `out_of_range`, as described.
- `noexcept` violation: separate test, GCC warns `'throw' will always call 'terminate' [-Wterminate]`; at run time `terminate` was called and the local `Guard` destructor did not run (stack not unwound), supporting the "with GCC 12, in a quick test" statement.
- `move_if_noexcept`: separate test, `reserve` on a vector of a type with a throwing move printed `copy`; with a `noexcept` move printed `move`.
- `-fno-exceptions`: compiling the catch example fails with `exception handling disabled, use '-fexceptions' to enable`.
- optional challenge: strong version (`copy` then `swap`) compiled and ran.
- not checked: zero-cost happy path, throw latency, and unwind-table size are stated qualitatively from ABI knowledge, not measured. The `reserve(size()+1)` O(n^2) claim relies on `reserve` allocating exactly the request, which libstdc++ does (seen on day 15's check), not measured as timing.
