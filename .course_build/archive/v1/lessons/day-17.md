<a id="day-17"></a>

## day 17: lambdas and closures in depth

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 03, 12, 16

### the idea

A lambda looks like an inline function, which is exactly the wrong mental model. A lambda expression creates an *object*. That object has a type, a size, data members, and a lifetime, and every lambda bug you will meet in production (a dangling capture in a callback, a stateful predicate behaving oddly, a `std::function` that refuses to compile) follows from forgetting that.

### understanding the concept

The compiler turns each lambda expression into a class with a unique, unnamed type (the closure type) and evaluates the expression to a prvalue of that type (the closure object). Captures become data members, initialized when the lambda expression is evaluated. The body becomes `operator()`, which is `const` unless you write `mutable`.

```cpp
double gain = 2.0;
int calls = 0;
auto f = [gain, &calls](double x) { ++calls; return x * gain; };

// is roughly equivalent to:
struct Closure {
    double gain;   // copied when the lambda expression is evaluated
    int& calls;    // a reference: no lifetime extension, no ownership
    double operator()(double x) const { ++calls; return x * gain; }
};
auto g = Closure{gain, calls};
```

Several rules fall out of this picture. A by-value capture is a snapshot taken at creation, not a live view. A `const` call operator can still modify what a reference capture refers to, because the constness applies to the member, not to the referent. Two lambdas with identical text have different types, so you cannot assign one to a variable of the other's type. A lambda with no captures has no state and converts implicitly to a plain function pointer, which is how you pass one to a C API expecting `void(*)(int)`.

C++14 and C++17 added the pieces you use most:

- **init-captures** (`[p = std::move(ptr)]`, C++14) declare a member with any initializer. This is how you move a `std::unique_ptr` into a closure, or capture a computed value under a new name.
- **generic lambdas** (`[](const auto& a, const auto& b) {...}`, C++14) make `operator()` a template, instantiated per argument type.
- **`[*this]`** (C++17) copies the whole enclosing object into the closure, where `[this]` copies only the pointer.
- **constexpr lambdas** (C++17): a lambda's call operator is implicitly `constexpr` when it satisfies the requirements, so `constexpr auto sq = [](int x) { return x * x; }; static_assert(sq(4) == 16);` works.

### in code

Closures are values: copying one copies its state. Predict the output.

```cpp
#include <iostream>

int main() {
    int n = 1;
    auto by_val = [n] { return n; };
    auto by_ref = [&n] { return n; };
    n = 2;
    std::cout << by_val() << by_ref() << '\n';    // prints: 12

    auto counter = [c = 0]() mutable { return ++c; };
    auto copy = counter;                           // copies the member c (still 0)
    counter();
    counter();
    std::cout << counter() << copy() << '\n';     // prints: 31

    // immediately invoked lambda: complex logic, but the result is const
    const auto mode = [&] {
        if (n > 1) return "fast";
        return "safe";
    }();
    std::cout << mode << '\n';                     // prints: fast
}
```

The last pattern deserves more use than it gets: when a `const` variable needs branching or a loop to compute, an immediately invoked lambda keeps it `const` instead of forcing a mutable variable with a delayed assignment.

The bug that matters most is a reference capture that outlives its referent. The lambda escapes the function, the stack frame goes away, and the closure holds a reference to nothing.

```cpp
#include <cstdio>
#include <functional>
#include <string>
#include <vector>

class Deferred {
    std::vector<std::function<void()>> tasks_;
public:
    void defer(std::function<void()> f) { tasks_.push_back(std::move(f)); }
    void flush() { for (auto& t : tasks_) t(); tasks_.clear(); }
};

void schedule_report(Deferred& d, const std::string& name) {
    std::string msg = "report: " + name;
    d.defer([&] { std::puts(msg.c_str()); });  // BUG: msg dies at return; flush() reads it: UB
}

void schedule_report_fixed(Deferred& d, const std::string& name) {
    std::string msg = "report: " + name;
    d.defer([msg = std::move(msg)] { std::puts(msg.c_str()); });  // the closure owns its data
}
```

`[&]` is fine when the lambda runs before the enclosing scope ends: a predicate passed to `std::find_if`, a comparator for `std::sort`. It is a liability as soon as the lambda is stored, deferred, or handed to another thread. A useful rule: if the lambda leaves the scope, capture by value or by init-capture, and if it must refer to a shared object, capture something that tracks lifetime (a `std::weak_ptr`, day 12) rather than a raw pointer or reference.

Now `std::function` versus a template parameter:

```cpp
#include <functional>
#include <memory>
#include <vector>

struct Point { float x, y, z; };

// Type-erased: one compiled function accepts any callable with this signature.
std::size_t count_if_erased(const std::vector<Point>& pts,
                            const std::function<bool(const Point&)>& keep) {
    std::size_t n = 0;
    for (const auto& p : pts) if (keep(p)) ++n;   // indirect call per point
    return n;
}

// Template: the callable's type is known, so the call can be inlined.
template <typename Pred>
std::size_t count_if_tmpl(const std::vector<Point>& pts, Pred&& keep) {
    std::size_t n = 0;
    for (const auto& p : pts) if (keep(p)) ++n;
    return n;
}

void demo() {
    auto owner = std::make_unique<float>(1.5f);
    auto in_range = [lim = std::move(owner)](const Point& p) { return p.z < *lim; };
    std::vector<Point> pts{{0, 0, 1}, {0, 0, 2}};
    count_if_tmpl(pts, in_range);                // fine
    // count_if_erased(pts, in_range);           // error: std::function needs a copyable callable
}
```

`std::function` stores the callable behind a type-erased interface (day 46 shows how). That costs an indirect call that the optimizer usually cannot inline, and possibly a heap allocation when the callable is too large for the internal buffer. The buffer size is a library detail: with libstdc++ in GCC 12, a lambda capturing two `double`s is stored inline and one capturing three `double`s allocates once. It also requires the callable to be copy-constructible, so closures owning a `unique_ptr` are rejected. (C++23 adds `std::move_only_function` for that case.) The template version has none of those costs, but it must be visible in a header and is instantiated once per callable type.

### in practice

A point-cloud preprocessing library exposes a filter step that takes a user predicate. The first API used `std::function<bool(const Point&)>`, because it compiles into a single function in a `.cpp` file and accepts anything. Profiling a 100,000-point cloud at 20 Hz showed the per-point indirect call in the hot loop, and the predicate's body could not be inlined or vectorized with the loop.

The fix is not "never use `std::function`". It is placing the type erasure where the call frequency is low. The library now takes a template parameter for the per-point predicate, and uses `std::function` for the per-frame "on cloud ready" callback, which fires twenty times a second and benefits from a stable, non-template, ABI-friendly signature. That is the general judgment: type erasure buys decoupling and a stable binary interface; templates buy inlining at the cost of compile time and header exposure. Pick per call site, and confirm with a profiler (day 50) that the hot path is really where you think it is.

### watch out for

`[=]` reads as "copy everything", but inside a member function it captures `this`, a pointer, not the members:

```cpp
#include <functional>

struct JointController {
    double kp = 1.5;
    std::function<double(double)> law() {
        return [=](double err) { return kp * err; };   // BUG risk: really this->kp
    }
};
// auto f = JointController{}.law(); f(0.1);   // UB: the temporary controller is gone
```

The closure stores `this`, so calling it after the controller is destroyed is undefined behavior. Capture what you need explicitly (`[kp = kp]`), or copy the object with `[*this]` when it is small and copyable. C++20 deprecates the implicit capture of `this` through `[=]` for exactly this reason, and wants you to write `[=, this]` to say it out loud.

### the takeaway

A lambda is a small class whose members are its captures. Ask the questions you would ask of any class: what does it own, what does it point to, and how long will it live? Use templates for hot-path callables and `std::function` at boundaries where flexibility is worth an indirect call.

### optional challenge

On libstdc++, this removes two elements, not one. Why is that allowed?

```cpp
std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8, 9};
v.erase(std::remove_if(v.begin(), v.end(),
                       [n = 0](int) mutable { return ++n == 3; }),
        v.end());
// libstdc++ result: 1 2 4 5 7 8 9
```

<details>
<summary>answer</summary>

The predicate is a closure object, and algorithms are allowed to copy their predicates. libstdc++'s `remove_if` first passes a copy to an internal `find_if` to locate the first element to remove: that copy counts to 3 and finds the element `3`. The algorithm then continues scanning with its own, still-unused copy, whose counter starts from 0 again and hits 3 at element `6`. The standard lets algorithms copy function objects freely and requires a predicate to give the same answer for the same element no matter which copy is called or how often. A counting predicate breaks that requirement, so no result is guaranteed (formally, violating a library requirement is undefined behavior; in practice you get results like this one). Keep predicates stateless, or keep the state outside the closure and capture a reference to it when you truly need it.

</details>
