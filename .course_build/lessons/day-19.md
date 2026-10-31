<a id="day-19"></a>

## day 19: forwarding references and perfect forwarding

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 05, 10, 18

### the idea

You write a thin wrapper: it logs, then passes its argument on to a function that has a copy overload and a move overload. Callers hand it temporaries, so the move overload should run. It never does. Then you "fix" it with `std::move`, and now it quietly steals strings from callers who passed a named variable they still need. The wrapper needs to pass along not just the value but its value category, and that is precisely what forwarding references and `std::forward` are for.

### understanding the concept

`T&&` means two different things. When `T` is a template parameter deduced from the call, `T&&` is a **forwarding reference** (the standard's term; Scott Meyers popularized "universal reference"). Anywhere else it is an ordinary rvalue reference.

```cpp
template <typename T> void f(T&& x);              // forwarding reference
auto&& r = make_value();                          // forwarding reference (auto deduces like T)
template <typename T> void g(std::vector<T>&& v); // rvalue reference: the parameter isn't exactly T&&
template <typename T> void h(const T&& x);        // rvalue reference: const disqualifies it
template <typename T> struct Box { void put(T&& x); };  // rvalue reference: T was fixed by the class
```

The trick is a special deduction rule plus reference collapsing. If the argument is an lvalue of type `U`, `T` is deduced as `U&`; if it is an rvalue, `T` is deduced as plain `U`. Substituting gives `U& &&` or `U&&`, and since references to references can't exist in source code, the compiler collapses them:

| `T` | `T&&` becomes | meaning |
|---|---|---|
| `U&` | `U& &&` → `U&` | caller passed an lvalue |
| `U&&` | `U&& &&` → `U&&` | (via explicit arguments or aliases) |
| `U` | `U&&` | caller passed an rvalue |

Any `&` in the mix wins; only `&& &&` stays `&&`. The upshot is that `T` *encodes* the caller's value category. Inside the function, though, `x` is a named variable, and a named variable is always an lvalue (day 05), whatever its declared type. To pass the caller's category on, you cast it back: `std::forward<T>(x)` is essentially `static_cast<T&&>(x)`. With `T = U&` that collapses to `U&` (an lvalue); with `T = U` it is `U&&` (an xvalue, so moves can happen). `std::move(x)` is the unconditional version: `static_cast<std::remove_reference_t<T>&&>(x)`, always an rvalue.

Variadic templates generalize this to any number of arguments. `typename... Args` declares a template parameter pack, `Args&&... args` a function parameter pack of forwarding references, and the pattern `std::forward<Args>(args)...` expands element-wise into a comma-separated list. `sizeof...(Args)` gives the count. That combination is the engine behind `std::make_unique`, `std::make_shared`, `std::thread`'s constructor, and every `emplace` function.

### in code

The wrapper problem, three ways. Predict the output.

```cpp
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

A variadic factory that does some bookkeeping and then constructs in place. This is the shape of `make_unique` and of `emplace_back`, which forwards its arguments through the allocator to construct the element directly in the vector's storage.

```cpp
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

Note the parentheses in `new T(...)`. In C++17, parentheses cannot initialize an aggregate, so `std::make_unique<Point>(1.0, 2.0)` fails for `struct Point { double x, y; };`. C++20 (P0960) allows parenthesized aggregate initialization, and the same call compiles there.

`auto&&` in a range-for is the forwarding reference you use most often without noticing:

```cpp
#include <vector>

void arm_all(std::vector<bool>& flags) {
    // for (auto& f : flags) f = true;   // error: *it is a prvalue proxy, not a bool&
    for (auto&& f : flags) f = true;     // OK: binds to the proxy, assignment writes through it
}
```

`auto&&` binds to whatever the iterator yields: an lvalue reference for ordinary containers, a temporary proxy for `std::vector<bool>` or for views that compute values. In generic code, `for (auto&& x : range)` is the form that always compiles; use `const auto&` when you mean read-only.

### in practice

A robot's command queue offers `post<Cmd>(Args&&... args)`, which constructs the command inside the queue's preallocated slot instead of building a temporary and moving it in. For most command types the saving is one move construction, which is cheap, so the honest reasons to prefer it are different: it works for types that are neither copyable nor movable (a command holding a `std::mutex`, say), and it keeps the call site short.

Two production costs come with it. First, every distinct combination of argument types is a separate instantiation, and forwarding references preserve exact types: `post<Log>("ok")` and `post<Log>("fail")` deduce `const char(&)[3]` and `const char(&)[5]`, two instantiations of the same function. In a header used everywhere, that shows up in compile time and binary size. Second, a forwarded argument can be consumed only once. The bug looks innocent:

```cpp
template <typename... Args>
void post_and_log(Args&&... args) {
    log_args(std::forward<Args>(args)...);   // may move from the arguments...
    post(std::forward<Args>(args)...);       // BUG: ...so this may receive moved-from objects
}
```

Pass by `const&` to everything except the last consumer, and forward only there.

### watch out for

A constructor template taking a forwarding reference is greedier than you think. It can beat the copy constructor:

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

`a` is a non-const lvalue. The copy constructor needs a `const` qualification added; the template deduces `S = Sensor&` and matches exactly, so it wins overload resolution. Copying a `const Sensor` works; copying a non-const one fails to compile here, and in worse cases compiles into the wrong conversion. The same happens with classes derived from `Sensor`. Constrain the template (`std::enable_if_t<!std::is_base_of_v<Sensor, std::decay_t<S>>, int> = 0` in C++17, a `requires` clause in C++20), or, often better, drop the template and take `std::string name` by value and move it into the member. That costs one extra move and removes the whole problem, which is a good trade for anything that is not a hot path.

### the takeaway

`T&&` with a deduced `T` remembers whether the caller passed an lvalue or an rvalue, and `std::forward<T>` replays that choice exactly once. Use perfect forwarding for factories, emplacement, and generic wrappers; use pass-by-value for ordinary "sink" parameters where simplicity beats the last move.

### optional challenge

For `template <typename T> void f(T&& x);`, what are `T` and the type of `x` in each call?

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
- `f(ci)`: lvalue `const int`, so `T = const int&` and `x` is `const int&`. Constness is preserved, which is why forwarding never accidentally strips `const`.
- `f(42)`: prvalue, so `T = int` and `x` is `int&&`.
- `f(std::move(ci))`: xvalue of type `const int`, so `T = const int` and `x` is `const int&&`. You can't move from it in any useful way (day 10): a move constructor taking `T&&` won't bind, so a copy happens.

</details>
