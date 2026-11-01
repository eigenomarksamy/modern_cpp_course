---
title: virtual functions and dynamic dispatch
standard: C++17
objective: explain how a virtual call selects an override at run time, what it typically costs, and how override and final catch mistakes
prerequisites: construction-order, unique-ptr
difficulty: 2
---

### the idea

`s.describe()` runs different code depending on which object is behind the reference `s`, and the compiler that generated the call did not know which one it would be. that is the whole point of a virtual function, and it is also where its costs and its classic mistakes come from: a signature that is almost right silently stops overriding, and a call that cannot be inlined blocks optimizations you did not know you were relying on.

### understanding the concept

a virtual function call through a reference or pointer selects the override for the object's *dynamic* type. the standard specifies only that behavior. every mainstream compiler implements it the same way, though, and knowing the mechanism makes the costs concrete:

```text
typical layout (Itanium C++ ABI: GCC and Clang on Linux, also MinGW;
MSVC differs in details; none of this is required by the standard)

  Lidar object                    vtable for Lidar (one per class, read-only)
 +------------------+            +------------------------------------+
 | vptr  -----------+----------> | &Lidar::~Lidar (two entries)       |
 | Sensor members   |            | &Lidar::describe     (overridden)  |
 | Lidar members    |            | &Sensor::calibrate   (inherited)   |
 +------------------+            +------------------------------------+
                                   (RTTI and offset data sit just before)
```

a call `s.describe()` becomes: load the vptr from the object, load the function pointer from a fixed slot, call indirectly. the constructor of each class in the chain sets the vptr to its own class's table, which is exactly why [[construction-order]]'s virtual call in a base constructor reached the base version.

the cost is an extra dependent load or two and an indirect branch, which modern branch predictors handle well when a call site keeps seeing the same type. the larger cost is usually what the compiler cannot do: it cannot inline a call whose target it does not know, so it also cannot optimize across it (constant propagation, vectorizing a loop that contains it). compilers devirtualize when they can prove the dynamic type, and `final` helps them. whether any of this matters depends on call frequency, so put virtual boundaries at a coarse grain (one call per frame or per batch, not per sample) and measure before contorting a design to avoid them.

### in code

first, let the compiler check your overrides.

```cpp fails
struct Filter {
    virtual ~Filter() = default;
    virtual double apply(double x) const = 0;
};

struct LowPass : Filter {
    double apply(double x);               // BUG: missing const: a new function that
};                                        // hides Filter::apply; LowPass stays abstract

struct LowPass2 final : Filter {
    double apply(double x) override;      // error: marked 'override' but does not override
};

struct LowPass3 final : Filter {
    double apply(double x) const override { return 0.9 * x; }   // correct
};
```

without `override`, a signature mismatch (missing `const`, `float` versus `double`, a changed base signature after a refactor) silently declares a new function. here the mistake surfaces only because `LowPass` remains abstract; had the base function not been pure, the base version would run and nothing would complain. GCC 12's `-Woverloaded-virtual` would flag the hiding, but it is not part of `-Wall` in that version. write `override` on every override; `final` on a class or function says "no further overriding" and gives the optimizer a devirtualization hint.

### in practice

put virtual boundaries where calls are rare relative to the work they do. a radar processing chain built from interchangeable stages pays one indirect call per *frame* if the interface is `virtual void process(Frame& f) = 0;`, and one per *sample* if it is `virtual float filter(float sample) = 0;`. the first is noise; the second can be the difference between a vectorized inner loop and a scalar one, because the compiler cannot see through the call. designing the interface at the coarse grain keeps the flexibility of runtime polymorphism without asking anyone to measure its cost in a hot loop. when the set of types is fixed and the call is fine-grained, the alternatives in [[static-polymorphism]] fit better.

### watch out for

**default arguments are bound statically, overrides dynamically.**

```cpp complete
#include <cstdio>

struct Base {
    virtual ~Base() = default;
    virtual void log(int level = 1) const { std::printf("base %d\n", level); }
};
struct Derived : Base {
    void log(int level = 2) const override { std::printf("derived %d\n", level); }
};

int main() {
    Derived d;
    const Base& b = d;
    b.log();   // prints: derived 1
}
```

the function is chosen by the dynamic type, but the default argument comes from the declaration the compiler sees, which is `Base::log`. the result mixes two classes' intentions. do not redefine default arguments in overrides; better, avoid default arguments on virtual functions entirely and provide a non-virtual overload in the base.

### the takeaway

a virtual call picks the override from the object's dynamic type through an indirect call; mark every override `override`, keep virtual calls at a coarse grain, and treat their cost as something to measure, not fear.

### optional challenge

`Base` has a non-virtual public function `void tick()` and `Derived` declares its own `void tick()`. given `Derived d; Base& b = d;`, which function do `d.tick()` and `b.tick()` call? would adding `override` to `Derived::tick` help?

<details>
<summary>answer</summary>

`d.tick()` calls `Derived::tick` and `b.tick()` calls `Base::tick`. without `virtual`, the call is resolved from the static type of the expression, so the same object behaves differently depending on how you name it. `Derived::tick` merely hides `Base::tick`.

adding `override` would not compile ("marked 'override', but does not override"), and that is the point: it turns the silent mistake into an error that tells you the base function is not virtual. the fix is then a deliberate choice: make `Base::tick` virtual, or rename the derived function so nobody expects dispatch.

</details>
