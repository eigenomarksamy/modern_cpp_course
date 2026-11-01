# compile checks: day 12

Toolchain: MSYS2 g++ 12.1.0 (x86_64), scratch folder outside the repo. Flags: `-std=c++17 -Wall -Wextra -pedantic`.

- ownership signatures (`make_detector`, `install`, `share`, `inspect`, `maybe_inspect`, `setup`) with stub definitions: compiles clean; run prints `inspect`, `run`, `~Cfar` (ownership transferred into `install` and released there).
- `Robot`/`Joint` cycle: compiles clean; run prints only `end of main`: neither destructor runs, as the lesson says. With the `weak_ptr` back-reference (`-DFIX`): prints `~Robot` then `~Joint`, matching the "now prints" comment.
- `MeshCache` (stub `Mesh` and `load_mesh`): compiles clean; two `get` calls while one result is alive load once and return the same pointer; after both are released, the next `get` reloads. The `shared_ptr<const Mesh>(new Mesh{})` alternative compiles.
- sizes on this toolchain (supporting the "typically" claims, which are implementation-specific): raw pointer 8, `unique_ptr<int>` 8, with an empty function-object deleter 8, with a function-pointer deleter 16, `shared_ptr` 16, `weak_ptr` 16.
- `shared_from_this()` on an object not owned by a `shared_ptr` throws `std::bad_weak_ptr` under `-std=c++17` (observed).
- optional challenge: prints `2 1 0 1`, matching the answer.
- two control blocks from one raw pointer: compiles silently. Not run (double delete is UB; no sanitizers on this mingw build).

Not checked: the claim that `make_shared` storage outlives the object while a `weak_ptr` exists follows from the single-allocation design and the standard's description; not measured here. `std::atomic<std::shared_ptr<T>>` (C++20) mentioned only; libstdc++ 12 does provide it, but it was not compiled.
