---
title: variadic templates and perfect-forwarding factories
standard: C++17
objective: write variadic function templates that forward any number of arguments to a constructor, and know the costs of doing so
prerequisites: forwarding-references
difficulty: 2
---

### the idea

`std::make_unique<T>(args...)`, `emplace_back(args...)`, and `std::thread`'s constructor all accept any number of arguments of any types and hand them, unchanged, to something else. none of them is magic: each is a variadic template whose parameters are forwarding references, plus one expansion that forwards every argument at once. once you can read that pattern, you can write it, and you can see what it costs.

### understanding the concept

variadic templates generalize this to any number of arguments. `typename... Args` declares a template parameter pack, `Args&&... args` a function parameter pack of forwarding references, and the pattern `std::forward<Args>(args)...` expands element-wise into a comma-separated list. `sizeof...(Args)` gives the count. that combination is the engine behind `std::make_unique`, `std::make_shared`, `std::thread`'s constructor, and every `emplace` function.

the `...` after a pattern expands the pattern once per element, so where you put it decides what gets repeated. with a pack `args` holding `a, b, c`:

| written | expands to |
|---|---|
| `f(args...)` | `f(a, b, c)` |
| `f(std::forward<Args>(args)...)` | `f(std::forward<A>(a), std::forward<B>(b), std::forward<C>(c))` |
| `f(g(args)...)` | `f(g(a), g(b), g(c))` |
| `f(g(args...))` | `f(g(a, b, c))` |

a pack can be empty, in which case `f(args...)` is simply `f()`. a pack cannot be indexed or iterated directly in C++17; you either expand it into a context that takes a list (function arguments, initializers, base classes) or, since C++17, reduce it with a fold expression ([[fold-expressions]]).

### in code

a variadic factory that does some bookkeeping and then constructs in place. this is the shape of `make_unique` and of `emplace_back`, which forwards its arguments through the allocator to construct the element directly in the vector's storage.

```cpp complete
#include <memory>
#include <string>
#include <utility>

inline int g_created = 0;   // C++17 inline variable

template <typename T, typename... Args>
std::unique_ptr<T> make_tracked(Args&&... args) {
    static_assert(sizeof...(Args) <= 4, "keep constructors small");
    ++g_created;
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
    // expands to: new T(std::forward<A1>(a1), std::forward<A2>(a2), ...)
}

struct Joint {
    Joint(std::string name, double limit) : name(std::move(name)), limit(limit) {}
    std::string name;
    double limit;
};

void build() {
    std::string base = "elbow";
    auto a = make_tracked<Joint>(base, 2.6);           // base copied into Joint::name
    auto b = make_tracked<Joint>(base + "_2", 2.6);    // temporary moved into Joint::name
}
```

note the parentheses in `new T(...)`. in C++17, parentheses cannot initialize an aggregate, so `std::make_unique<Point>(1.0, 2.0)` fails for `struct Point { double x, y; };`. C++20 (P0960) allows parenthesized aggregate initialization, and the same call compiles there.

### in practice

a robot's command queue offers `post<Cmd>(Args&&... args)`, which constructs the command inside the queue's preallocated slot instead of building a temporary and moving it in. for most command types the saving is one move construction, which is cheap, so the honest reasons to prefer it are different: it works for types that are neither copyable nor movable (a command holding a `std::mutex`, say), and it keeps the call site short.

two production costs come with it. first, every distinct combination of argument types is a separate instantiation, and forwarding references preserve exact types: `post<Log>("ok")` and `post<Log>("fail")` deduce `const char(&)[3]` and `const char(&)[5]`, two instantiations of the same function. in a header used everywhere, that shows up in compile time and binary size. second, a forwarded argument can be consumed only once. the bug looks innocent:

```cpp
template <typename... Args>
void post_and_log(Args&&... args) {
    log_args(std::forward<Args>(args)...);   // may move from the arguments...
    post(std::forward<Args>(args)...);       // BUG: ...so this may receive moved-from objects
}
```

pass by `const&` to everything except the last consumer, and forward only there.

### watch out for

**a braced list cannot be forwarded.** template argument deduction has no type to deduce from `{1, 2, 3}`:

```cpp complete
#include <memory>
#include <vector>

// auto v = std::make_unique<std::vector<int>>({1, 2, 3});   // error: cannot deduce Args
auto w = std::make_unique<std::vector<int>>(std::initializer_list<int>{1, 2, 3});   // OK
```

the same is why `v.push_back({1, 2})` works for a vector of pairs (the parameter type is known, so the braces can initialize it) while `v.emplace_back({1, 2})` does not. with emplacement, pass the constructor arguments themselves (`v.emplace_back(1, 2)`) or name the type.

### the takeaway

a variadic factory is a parameter pack of forwarding references plus one `std::forward<Args>(args)...` expansion; use it for factories, emplacement, and generic wrappers, forward each argument exactly once, and prefer pass-by-value for ordinary sink parameters.

### optional challenge

`template <typename T, typename... Args> void post(Args&&... args);` is called five times. how many distinct instantiations of `post` does the compiler generate?

```cpp
std::string s = "x";
post<Log>("ok");
post<Log>("no");
post<Log>("fail");
post<Log>(std::string("x"));
post<Log>(s);
```

<details>
<summary>answer</summary>

four. `"ok"` and `"no"` both deduce `Args = const char(&)[3]`, so they share an instantiation; `"fail"` deduces `const char(&)[5]`, a different one. the temporary `std::string` deduces `Args = std::string` and the named `s` deduces `std::string&`, which are different again. forwarding references preserve exact types and value categories, which is what makes them perfect, and also what multiplies instantiations in a header used across a large codebase.

</details>
