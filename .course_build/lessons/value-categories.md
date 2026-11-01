---
title: value categories without the headache
standard: C++17
objective: classify expressions as lvalues, xvalues, or prvalues, and use the binding rules to predict which overload is called
prerequisites: temporaries-dangling, const-correctness
difficulty: 3
---

### the idea

here is a function that looks like it moves a string into a container:

```cpp
void Registry::store(std::string&& name) {
    names_.push_back(name);   // copies
}
```

it copies. `name` has type "rvalue reference to `std::string`", but the *expression* `name` is an lvalue, so `push_back(const std::string&)` is chosen. the confusion comes from mixing up two independent properties that every expression has: a **type** and a **value category**. once you keep them apart, overload resolution, moves, and copy elision stop being folklore.

### understanding the concept

value categories classify **expressions**, not variables or objects. since C++11 there are three leaf categories, and C++17 sharpened what they mean:

```text
                 expression
                /          \
          glvalue           rvalue
         /       \         /      \
     lvalue        xvalue          prvalue
  (identity,     (identity,      (no identity:
   not movable)   movable)        a recipe for a value)
```

- an **lvalue** designates an object or function with an identity you can refer to again: a variable name (of *any* type, including `T&&`), `*p`, `a[i]`, `++x`, a call to a function returning `T&`, a string literal.
- an **xvalue** ("expiring") designates an object whose resources may be reused: `std::move(x)`, a call to a function returning `T&&`, a member access on an xvalue.
- a **prvalue** ("pure") has no identity yet. in C++17 it is not an object at all but an *initializer*: `42`, `x + 1`, `x++`, `Frame{}`, a call to a function returning by value.

a **glvalue** is an lvalue or xvalue (it has identity); an **rvalue** is an xvalue or prvalue (it may be moved from).

**binding rules** decide which overload wins:

| parameter | lvalue | xvalue | prvalue |
|---|---|---|---|
| `T&` | yes | no | no |
| `const T&` | yes | yes | yes |
| `T&&` | no | yes | yes |

when both `const T&` and `T&&` accept an rvalue, `T&&` is the better match. `std::move` does not move anything: it is a cast that turns its argument into an xvalue so that the `T&&` overload is selected. what the move then does is [[move-semantics]]'s subject.

### in code

**predict which overload is called.**

```cpp complete
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
    Frame&& r = make();   // lifetime-extended temporary

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

lines 3 and 4 are prvalues, line 5 is an xvalue. line 6 is the headline: `r` is declared as `Frame&&`, but the expression `r` is an lvalue, so `Frame&` wins. line 7: `std::move(cf)` is an xvalue of type `const Frame`; `Frame&&` cannot bind to a const object, so `const Frame&` is chosen. moving from a `const` object silently copies.

</details>

### in practice

the standard library is built on these binding rules. `std::vector::push_back` has two overloads: `push_back(const T&)`, which copies, and `push_back(T&&)`, which moves. as a caller you never pick one explicitly; the category of your argument does. a temporary (`push_back(Frame{})`) or an explicitly expiring object (`push_back(std::move(frame))`) takes the cheap path, and an ordinary named object is copied because you might still use it. in a telemetry pipeline that hands large message buffers from stage to stage, reading a call site with categories in mind tells you exactly where the copies are: every argument that is a plain name and not wrapped in `std::move` is one. your own interfaces can offer the same pair of overloads when copying is expensive, or take the parameter by value and let the caller's category decide, which [[noexcept-moves]] discusses.

### watch out for

**if it has a name, it is an lvalue.** every function parameter, including one declared `T&&`, is an lvalue inside the function body. the fix in the opening example is to say what you mean:

```cpp
void Registry::store(std::string&& name) {
    names_.push_back(std::move(name));   // xvalue: selects push_back(std::string&&)
}
```

the rule exists for safety: a name can be used more than once, and silently moving on first use would leave later uses looking at a gutted object. moving is therefore always an explicit decision at the point of last use. the opposite mistake is also common: `std::move` on a `const` object (line 7 above), or on an object you read again later.

### the takeaway

every expression has a type and a value category; overload resolution picks by category, and a named variable, even one declared `T&&`, is always an lvalue.

### optional challenge

classify each expression as lvalue, xvalue, or prvalue, given `int x = 0; int& f(); int g(); std::string s;`:
`x`, `x + 1`, `f()`, `g()`, `std::move(x)`, `"abc"`, `x++`, `++x`, `std::move(s).size()`.

<details>
<summary>answer</summary>

- `x`: lvalue (a name).
- `x + 1`: prvalue (built-in arithmetic yields a value).
- `f()`: lvalue (returns `int&`).
- `g()`: prvalue (returns by value).
- `std::move(x)`: xvalue (returns `int&&`).
- `"abc"`: lvalue. string literals are arrays with static storage duration, so they have identity; it is the only literal that is an lvalue.
- `x++`: prvalue (the old value, a copy). `++x`: lvalue (the variable itself, after incrementing).
- `std::move(s).size()`: prvalue. the object expression is an xvalue, but `size()` returns `std::size_t` by value, and the category of a call depends only on the function's return type.

</details>

### going deeper

#### `decltype` and value categories

**`decltype` sees both the name and the expression.** `decltype(name)` gives the declared type of the entity. `decltype(expression)` encodes the category: `T&` for an lvalue, `T&&` for an xvalue, `T` for a prvalue. parentheses turn a name into an expression:

```cpp ub
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

the last pair is why `decltype(auto)` (C++14) deserves care: an innocent pair of parentheses changes the return type to a reference to a dead local. GCC flags it with `-Wreturn-local-addr`.
