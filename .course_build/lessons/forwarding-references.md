---
title: forwarding references and `std::forward`
standard: C++17
objective: recognize forwarding references, explain reference collapsing, and pass an argument's value category through with `std::forward`
prerequisites: function-templates, move-semantics
difficulty: 3
---

### the idea

you write a thin wrapper: it logs, then passes its argument on to a function that has a copy overload and a move overload. callers hand it temporaries, so the move overload should run. it never does. then you "fix" it with `std::move`, and now it quietly steals strings from callers who passed a named variable they still need. the wrapper needs to pass along not just the value but its value category, and that is precisely what forwarding references and `std::forward` are for.

### understanding the concept

`T&&` means two different things. when `T` is a template parameter deduced from the call, `T&&` is a **forwarding reference** (the standard's term; Scott Meyers popularized "universal reference"). anywhere else it is an ordinary rvalue reference.

```cpp
template <typename T> void f(T&& x);              // forwarding reference
auto&& r = make_value();                          // forwarding reference (auto deduces like T)
template <typename T> void g(std::vector<T>&& v); // rvalue reference: the parameter isn't exactly T&&
template <typename T> void h(const T&& x);        // rvalue reference: const disqualifies it
template <typename T> struct Box { void put(T&& x); };  // rvalue reference: T was fixed by the class
```

the trick is a special deduction rule plus reference collapsing. if the argument is an lvalue of type `U`, `T` is deduced as `U&`; if it is an rvalue, `T` is deduced as plain `U`. substituting gives `U& &&` or `U&&`, and since references to references can't exist in source code, the compiler collapses them:

| `T` | `T&&` becomes | meaning |
|---|---|---|
| `U&` | `U& &&` → `U&` | caller passed an lvalue |
| `U&&` | `U&& &&` → `U&&` | (via explicit arguments or aliases) |
| `U` | `U&&` | caller passed an rvalue |

any `&` in the mix wins; only `&& &&` stays `&&`. the upshot is that `T` *encodes* the caller's value category. inside the function, though, `x` is a named variable, and a named variable is always an lvalue ([[value-categories]]), whatever its declared type. to pass the caller's category on, you cast it back: `std::forward<T>(x)` is essentially `static_cast<T&&>(x)`. with `T = U&` that collapses to `U&` (an lvalue); with `T = U` it is `U&&` (an xvalue, so moves can happen). `std::move(x)` is the unconditional version: `static_cast<std::remove_reference_t<T>&&>(x)`, always an rvalue.

### in code

the wrapper problem, three ways. predict the output.

```cpp complete
#include <cstdio>
#include <string>
#include <utility>

void consume(const std::string&) { std::puts("copy"); }
void consume(std::string&&)      { std::puts("move"); }

template <typename T> void relay_named(T&& s) { consume(s); }             // s is an lvalue
template <typename T> void relay_moved(T&& s) { consume(std::move(s)); }  // always an rvalue
template <typename T> void relay(T&& s)       { consume(std::forward<T>(s)); }

int main() {
    std::string name = "lidar_front";
    relay_named(std::string{"tmp"});  // prints: copy  (a missed move)
    relay_moved(name);                // prints: move  (BUG: consume may now steal the caller's 'name')
    relay(name);                      // prints: copy
    relay(std::string{"tmp"});        // prints: move
}
```

### in practice

`auto&&` in a range-for is the forwarding reference you use most often without noticing:

```cpp complete
#include <vector>

void arm_all(std::vector<bool>& flags) {
    // for (auto& f : flags) f = true;   // error: *it is a prvalue proxy, not a bool&
    for (auto&& f : flags) f = true;     // OK: binds to the proxy, assignment writes through it
}
```

`auto&&` binds to whatever the iterator yields: an lvalue reference for ordinary containers, a temporary proxy for `std::vector<bool>` or for views that compute values. in generic code, `for (auto&& x : range)` is the form that always compiles; use `const auto&` when you mean read-only.

### watch out for

a constructor template taking a forwarding reference is greedier than you think. it can beat the copy constructor:

```cpp
#include <string>
#include <utility>

class Sensor {
public:
    template <typename S>
    explicit Sensor(S&& name) : name_(std::forward<S>(name)) {}
    Sensor(const Sensor&) = default;
private:
    std::string name_;
};

Sensor a{"lidar"};
Sensor b{a};   // error: picks the template with S = Sensor&, then tries std::string(Sensor&)
```

`a` is a non-const lvalue. the copy constructor needs a `const` qualification added; the template deduces `S = Sensor&` and matches exactly, so it wins overload resolution. copying a `const Sensor` works; copying a non-const one fails to compile here, and in worse cases compiles into the wrong conversion. the same happens with classes derived from `Sensor`. constrain the template (`std::enable_if_t<!std::is_base_of_v<Sensor, std::decay_t<S>>, int> = 0` in C++17, a `requires` clause in C++20), or, often better, drop the template and take `std::string name` by value and move it into the member. that costs one extra move and removes the whole problem, which is a good trade for anything that is not a hot path.

### the takeaway

`T&&` with a deduced `T` remembers whether the caller passed an lvalue or an rvalue, and `std::forward<T>` replays that choice; anywhere else, `T&&` is a plain rvalue reference.

### optional challenge

for `template <typename T> void f(T&& x);`, what are `T` and the type of `x` in each call?

```cpp
int i = 0;
const int ci = 0;
f(i);
f(ci);
f(42);
f(std::move(ci));
```

<details>
<summary>answer</summary>

- `f(i)`: lvalue `int`, so `T = int&` and `x` is `int&`.
- `f(ci)`: lvalue `const int`, so `T = const int&` and `x` is `const int&`. constness is preserved, which is why forwarding never accidentally strips `const`.
- `f(42)`: prvalue, so `T = int` and `x` is `int&&`.
- `f(std::move(ci))`: xvalue of type `const int`, so `T = const int` and `x` is `const int&&`. you can't move from it in any useful way ([[move-semantics]]): a move constructor taking `T&&` won't bind, so a copy happens.

</details>
