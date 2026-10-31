# checks: day 05

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++17 -Wall -Wextra -pedantic` unless noted. Blocks extracted from the lesson; stubs added only where a block uses undeclared names.

- `Registry::store` (idea, copying) and the fixed version with `std::move` (watch out for): compiled cleanly against a stub `Registry` with a `std::vector<std::string>` member. That the first copies follows from overload resolution; not instrumented.
- predict-the-overload block: compiled cleanly, printed exactly the seven lines in the collapsed output.
- `decltype` block: all `static_assert`s pass; `dangle()` gives `-Wreturn-local-addr` as stated. Additional asserts confirmed `decltype(("abc"))` is `const char(&)[4]` (lvalue), supporting the challenge answer.
- `Big` elision block: default flags printed `ctor` / `ctor` / `ctor ctor copy`; with `-fno-elide-constructors` printed `ctor` / `ctor move` / `ctor ctor copy`, as stated.
- `RegisterBlock` factory: compiles with `-std=c++17` (stub `validate` and constructor definition added); with `-std=c++14` fails with "use of deleted function 'RegisterBlock::RegisterBlock(const RegisterBlock&)'" at the `return` and at the initialization of `motor`. A separate test confirmed that returning a named local of a non-copyable, non-movable type fails in C++17 too.

Not checked: the challenge classifications beyond the `decltype` asserts above are from the standard's rules.
