---
title: copy elision and temporary materialization
standard: C++17
objective: explain why returning a prvalue never copies in C++17, when NRVO applies, and why `return std::move(local)` is a pessimization
prerequisites: value-categories
difficulty: 2
---

### the idea

in C++14 you could not return a type with deleted copy and move constructors from a factory function. in C++17 you can. compilers did not get smarter; the language changed what `return T{...};` *means*. knowing what changed tells you which returns are free by definition, which are free in practice, and which quietly cost a move.

### understanding the concept

**temporary materialization.** a prvalue becomes an actual object only when it has to: when a reference binds to it, when you access a member of it, or when it is discarded. at that point a temporary is created and the expression becomes an xvalue. otherwise the prvalue directly initializes its final destination. that is the mechanism behind C++17's **guaranteed copy elision**: `T x = T{...};` and `return T{...};` initialize the target in place. no copy or move constructor is called, and none needs to exist.

returning a *named* local is different. named return value optimization (NRVO) lets the compiler construct the local directly in the return slot, but it is permitted, not required, and the copy or move constructor must still be accessible. when NRVO does not happen, a returned local is treated as an rvalue first, so it is moved if it can be.

### in code

**guaranteed elision versus NRVO.** a type that logs its special members:

```cpp complete
#include <cstdio>

struct Big {
    Big() { std::puts("ctor"); }
    Big(const Big&) { std::puts("copy"); }
    Big(Big&&) noexcept { std::puts("move"); }
};

Big make_prvalue() { return Big{}; }                     // guaranteed elision (C++17)
Big make_named()   { Big b; return b; }                  // NRVO: allowed, not required
Big make_either(bool c) { Big a, b; return c ? a : b; }  // not a plain name: copied

int main() {
    Big x = make_prvalue();   // prints: ctor
    Big y = make_named();     // prints: ctor (with NRVO), or ctor move (without)
    Big z = make_either(true);// prints: ctor ctor copy
    (void)x; (void)y; (void)z;
}
```

with GCC 12 at default settings we saw `ctor`, `ctor`, and `ctor ctor copy`. with `-fno-elide-constructors`, which disables optional elision, `make_named` printed `ctor move` while `make_prvalue` still printed only `ctor`: in C++17 that elision is part of the language, not an optimization. `make_either` copies because the conditional expression is an lvalue that is not simply the name of a local, so neither NRVO nor the implicit move applies. write `if (c) return a; return b;` and each branch qualifies again.

### in practice

guaranteed elision changes what you can design, not only how fast it runs. consider a handle to a memory-mapped device register block in a motor controller. other components cache its address, so it must never move, and you want no "moved-from" state to reason about:

```cpp
#include <cstdint>

class RegisterBlock {
public:
    explicit RegisterBlock(std::uintptr_t base);
    RegisterBlock(const RegisterBlock&) = delete;
    RegisterBlock& operator=(const RegisterBlock&) = delete;
    // no move operations are declared: deleting copy suppresses them
};

RegisterBlock open_block(std::uintptr_t base) {
    validate(base);                // checks before construction
    return RegisterBlock{base};    // C++17: compiles; C++14: error, deleted copy constructor
}

RegisterBlock motor = open_block(0x4000'0000);   // constructed in place
```

before C++17 you had to return such a type through `std::unique_ptr` or use a two-phase `init()`, both of which leak complexity into every caller. now a factory function can return a non-movable type by value, which keeps the class invariant ("if it exists, it is pinned and valid") without a heap allocation. note the limit: a factory that builds a named local and returns it still fails to compile for this type, because NRVO is optional and needs an accessible constructor.

### watch out for

**`return std::move(local);` is a pessimization.** it looks like a helpful hint and does the opposite:

```cpp complete
#include <utility>
#include <vector>

std::vector<int> collect() {
    std::vector<int> ids(1000);
    return std::move(ids);   // operand is no longer a plain name: NRVO is impossible
}
```

NRVO applies only when the return operand is the plain name of a local. `std::move(ids)` is an xvalue expression, so the compiler must construct the result by moving. a plain `return ids;` would either be elided or, failing that, moved anyway, because a returned local is treated as an rvalue first. the explicit `std::move` removes only the best case. GCC and Clang flag it with `-Wpessimizing-move`, which is part of `-Wall`. use `std::move` in a `return` only for things that are not locals or by-value parameters, such as a data member you are handing out.

### the takeaway

since C++17 a prvalue is an initializer that builds its object in place, so returning `T{...}` never copies or moves; returning a named local usually does not either, as long as you leave it a plain name.

### optional challenge

`make_big()` returns `Big` by value. which functions are *guaranteed* to call no copy or move constructor, and what happens in the others?

```cpp
Big a()      { return Big{}; }                 // (1)
Big b()      { Big x; return x; }              // (2)
Big c()      { return make_big(); }            // (3)
Big d(Big p) { return p; }                     // (4)
Big e()      { Big x; return std::move(x); }   // (5)
```

<details>
<summary>answer</summary>

(1) and (3) are guaranteed: both return a prvalue, which initializes the caller's object directly, and a chain of prvalue returns stays a chain of initializers.

(2) is NRVO: allowed and almost always done, but if it does not happen the local is moved. (4) can never use NRVO, because a parameter is not constructed in the function's return slot; it is moved (a returned by-value parameter is treated as an rvalue first). (5) always moves: the operand is not a plain name, so elision is impossible.

</details>
