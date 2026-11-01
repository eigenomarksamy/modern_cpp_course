---
title: lambdas are objects: closures and captures
standard: C++17
objective: explain what a lambda expression compiles to, and choose captures by what the closure should own or refer to
prerequisites: algorithms, unique-ptr
difficulty: 2
---

### the idea

a lambda looks like an inline function, which is exactly the wrong mental model. a lambda expression creates an *object*. that object has a type, a size, data members, and a lifetime, and every lambda bug you will meet in production (a dangling capture in a callback, a stateful predicate behaving oddly, a `std::function` that refuses to compile) follows from forgetting that.

### understanding the concept

the compiler turns each lambda expression into a class with a unique, unnamed type (the closure type) and evaluates the expression to a prvalue of that type (the closure object). captures become data members, initialized when the lambda expression is evaluated. the body becomes `operator()`, which is `const` unless you write `mutable`.

```cpp complete
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

several rules fall out of this picture. a by-value capture is a snapshot taken at creation, not a live view. a `const` call operator can still modify what a reference capture refers to, because the constness applies to the member, not to the referent. two lambdas with identical text have different types, so you cannot assign one to a variable of the other's type. a lambda with no captures has no state and converts implicitly to a plain function pointer, which is how you pass one to a C API expecting `void(*)(int)`.

C++14 and C++17 added the pieces you use most:

- **init-captures** (`[p = std::move(ptr)]`, C++14) declare a member with any initializer. this is how you move a `std::unique_ptr` into a closure, or capture a computed value under a new name.
- **generic lambdas** (`[](const auto& a, const auto& b) {...}`, C++14) make `operator()` a template, instantiated per argument type.
- **`[*this]`** (C++17) copies the whole enclosing object into the closure, where `[this]` copies only the pointer.
- **constexpr lambdas** (C++17): a lambda's call operator is implicitly `constexpr` when it satisfies the requirements, so `constexpr auto sq = [](int x) { return x * x; }; static_assert(sq(4) == 16);` works.

### in code

closures are values: copying one copies its state. predict the output.

```cpp complete
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

the last pattern deserves more use than it gets: when a `const` variable needs branching or a loop to compute, an immediately invoked lambda keeps it `const` instead of forcing a mutable variable with a delayed assignment.

### in practice

capturing deliberately makes a lambda's dependencies as visible as a function's parameters. sorting detections by distance from the vehicle's current position is a one-liner, and the capture list documents exactly what the comparator depends on:

```cpp complete
#include <algorithm>
#include <vector>

struct Det { float x, y; };

void sort_by_distance(std::vector<Det>& dets, Det ego) {
    std::sort(dets.begin(), dets.end(), [ego](const Det& a, const Det& b) {
        auto d2 = [&ego](const Det& d) { return (d.x - ego.x) * (d.x - ego.x)
                                              + (d.y - ego.y) * (d.y - ego.y); };
        return d2(a) < d2(b);
    });
}
```

`ego` is captured by value: the comparator is a self-contained object that `std::sort` may copy as often as it likes. the inner helper captures by reference, which is safe because it never leaves the enclosing call. prefer explicit capture lists over `[=]` and `[&]` in anything longer than a line: they turn "what does this closure touch?" into something a reviewer can read instead of infer.

### watch out for

`[=]` reads as "copy everything", but inside a member function it captures `this`, a pointer, not the members:

```cpp ub
#include <functional>

struct JointController {
    double kp = 1.5;
    std::function<double(double)> law() {
        return [=](double err) { return kp * err; };   // BUG risk: really this->kp
    }
};
// auto f = JointController{}.law(); f(0.1);   // UB: the temporary controller is gone
```

the closure stores `this`, so calling it after the controller is destroyed is undefined behavior. capture what you need explicitly (`[kp = kp]`), or copy the object with `[*this]` when it is small and copyable. C++20 deprecates the implicit capture of `this` through `[=]` for exactly this reason, and wants you to write `[=, this]` to say it out loud.

### the takeaway

a lambda is a small class whose members are its captures; ask what it owns, what it points to, and how long it will live, exactly as you would for any other class.

### optional challenge

on libstdc++, this removes two elements, not one. why is that allowed?

```cpp
std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8, 9};
v.erase(std::remove_if(v.begin(), v.end(),
                       [n = 0](int) mutable { return ++n == 3; }),
        v.end());
// libstdc++ result: 1 2 4 5 7 8 9
```

<details>
<summary>answer</summary>

the predicate is a closure object, and algorithms are allowed to copy their predicates. libstdc++'s `remove_if` first passes a copy to an internal `find_if` to locate the first element to remove: that copy counts to 3 and finds the element `3`. the algorithm then continues scanning with its own, still-unused copy, whose counter starts from 0 again and hits 3 at element `6`. the standard lets algorithms copy function objects freely and requires a predicate to give the same answer for the same element no matter which copy is called or how often. a counting predicate breaks that requirement, so no result is guaranteed (formally, violating a library requirement is undefined behavior; in practice you get results like this one). keep predicates stateless, or keep the state outside the closure and capture a reference to it when you truly need it.

</details>
