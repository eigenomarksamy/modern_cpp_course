<a id="day-05"></a>

## day 05: value categories without the headache

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days [03](#day-03), [04](#day-04)

### the idea

Here is a function that looks like it moves a string into a container:

```cpp
void Registry::store(std::string&& name) {
    names_.push_back(name);   // copies
}
```

It copies. `name` has type "rvalue reference to `std::string`", but the *expression* `name` is an lvalue, so `push_back(const std::string&)` is chosen. The confusion comes from mixing up two independent properties that every expression has: a **type** and a **value category**. Once you keep them apart, overload resolution, moves, and copy elision stop being folklore.

### understanding the concept

Value categories classify **expressions**, not variables or objects. Since C++11 there are three leaf categories, and C++17 sharpened what they mean:

```text
                 expression
                /          \
          glvalue           rvalue
         /       \         /      \
     lvalue        xvalue          prvalue
  (identity,     (identity,      (no identity:
   not movable)   movable)        a recipe for a value)
```

- An **lvalue** designates an object or function with an identity you can refer to again: a variable name (of *any* type, including `T&&`), `*p`, `a[i]`, `++x`, a call to a function returning `T&`, a string literal.
- An **xvalue** ("expiring") designates an object whose resources may be reused: `std::move(x)`, a call to a function returning `T&&`, a member access on an xvalue.
- A **prvalue** ("pure") has no identity yet. In C++17 it is not an object at all but an *initializer*: `42`, `x + 1`, `x++`, `Frame{}`, a call to a function returning by value.

A **glvalue** is an lvalue or xvalue (it has identity); an **rvalue** is an xvalue or prvalue (it may be moved from).

**Temporary materialization.** A prvalue becomes an actual object only when it has to: when a reference binds to it, when you access a member of it, or when it is discarded. At that point a temporary is created and the expression becomes an xvalue. Otherwise the prvalue directly initializes its final destination. That is the mechanism behind C++17's **guaranteed copy elision**: `T x = T{...};` and `return T{...};` initialize the target in place. No copy or move constructor is called, and none needs to exist.

Returning a *named* local is different. Named return value optimization (NRVO) lets the compiler construct the local directly in the return slot, but it is permitted, not required, and the copy or move constructor must still be accessible. When NRVO does not happen, a returned local is treated as an rvalue first, so it is moved if it can be.

**Binding rules** decide which overload wins:

| parameter | lvalue | xvalue | prvalue |
|---|---|---|---|
| `T&` | yes | no | no |
| `const T&` | yes | yes | yes |
| `T&&` | no | yes | yes |

When both `const T&` and `T&&` accept an rvalue, `T&&` is the better match. `std::move` does not move anything: it is a cast that turns its argument into an xvalue so that the `T&&` overload is selected. What the move then does is day 10's subject.

### in code

**Predict which overload is called.**

```cpp
#include <cstdio>
#include <utility>

struct Frame { int id = 0; };

void take(Frame&)       { std::puts("Frame&"); }
void take(const Frame&) { std::puts("const Frame&"); }
void take(Frame&&)      { std::puts("Frame&&"); }

Frame make() { return Frame{}; }

int main() {
    Frame f;
    const Frame cf;
    Frame&& r = make();   // lifetime-extended temporary (day 03)

    take(f);              // 1
    take(cf);             // 2
    take(Frame{});        // 3
    take(make());         // 4
    take(std::move(f));   // 5
    take(r);              // 6
    take(std::move(cf));  // 7
}
```

<details>
<summary>output</summary>

```text
Frame&
const Frame&
Frame&&
Frame&&
Frame&&
Frame&
const Frame&
```

Lines 3 and 4 are prvalues, line 5 is an xvalue. Line 6 is the headline: `r` is declared as `Frame&&`, but the expression `r` is an lvalue, so `Frame&` wins. Line 7: `std::move(cf)` is an xvalue of type `const Frame`; `Frame&&` cannot bind to a const object, so `const Frame&` is chosen. Moving from a `const` object silently copies.

</details>

**`decltype` sees both the name and the expression.** `decltype(name)` gives the declared type of the entity. `decltype(expression)` encodes the category: `T&` for an lvalue, `T&&` for an xvalue, `T` for a prvalue. Parentheses turn a name into an expression:

```cpp
#include <type_traits>
#include <utility>

int x = 0;
static_assert(std::is_same_v<decltype(x), int>);                 // the entity
static_assert(std::is_same_v<decltype((x)), int&>);              // lvalue expression
static_assert(std::is_same_v<decltype(std::move(x)), int&&>);    // xvalue
static_assert(std::is_same_v<decltype(x + 1), int>);             // prvalue
static_assert(std::is_same_v<decltype(x++), int>);               // prvalue
static_assert(std::is_same_v<decltype(++x), int&>);              // lvalue

decltype(auto) value()  { int local = 1; return local; }    // returns int
decltype(auto) dangle() { int local = 1; return (local); }  // BUG: returns int&, dangling
```

The last pair is why `decltype(auto)` (C++14) deserves care: an innocent pair of parentheses changes the return type to a reference to a dead local. GCC flags it with `-Wreturn-local-addr`.

**Guaranteed elision versus NRVO.** A type that logs its special members:

```cpp
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

With GCC 12 at default settings we saw `ctor`, `ctor`, and `ctor ctor copy`. With `-fno-elide-constructors`, which disables optional elision, `make_named` printed `ctor move` while `make_prvalue` still printed only `ctor`: in C++17 that elision is part of the language, not an optimization. `make_either` copies because the conditional expression is an lvalue that is not simply the name of a local, so neither NRVO nor the implicit move applies. Write `if (c) return a; return b;` and each branch qualifies again.

### in practice

Guaranteed elision changes what you can design, not only how fast it runs. Consider a handle to a memory-mapped device register block in a motor controller. Other components cache its address, so it must never move, and you want no "moved-from" state to reason about:

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

Before C++17 you had to return such a type through `std::unique_ptr` or use a two-phase `init()`, both of which leak complexity into every caller. Now a factory function can return a non-movable type by value, which keeps the class invariant ("if it exists, it is pinned and valid") without a heap allocation. Note the limit: a factory that builds a named local and returns it still fails to compile for this type, because NRVO is optional and needs an accessible constructor.

### watch out for

"If it has a name, it is an lvalue." Every function parameter, including one declared `T&&`, is an lvalue inside the function body. The fix in the opening example is to say what you mean:

```cpp
void Registry::store(std::string&& name) {
    names_.push_back(std::move(name));   // xvalue: selects push_back(std::string&&)
}
```

The rule exists for safety: a name can be used more than once, and silently moving on first use would leave later uses looking at a gutted object. Moving is therefore always an explicit decision at the point of last use. The opposite mistake is also common: `std::move` on a `const` object (line 7 above), or on an object you read again later.

### the takeaway

Every expression has a type and a value category; overloads, moves, and elision are decided by the category, a named variable is always an lvalue, and since C++17 a prvalue is just an initializer that builds its object in place.

### optional challenge

Classify each expression as lvalue, xvalue, or prvalue, given `int x = 0; int& f(); int g(); std::string s;`:
`x`, `x + 1`, `f()`, `g()`, `std::move(x)`, `"abc"`, `x++`, `++x`, `std::move(s).size()`.

<details>
<summary>answer</summary>

- `x`: lvalue (a name).
- `x + 1`: prvalue (built-in arithmetic yields a value).
- `f()`: lvalue (returns `int&`).
- `g()`: prvalue (returns by value).
- `std::move(x)`: xvalue (returns `int&&`).
- `"abc"`: lvalue. String literals are arrays with static storage duration, so they have identity; it is the only literal that is an lvalue.
- `x++`: prvalue (the old value, a copy). `++x`: lvalue (the variable itself, after incrementing).
- `std::move(s).size()`: prvalue. The object expression is an xvalue, but `size()` returns `std::size_t` by value, and the category of a call depends only on the function's return type.

</details>
