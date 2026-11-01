---
title: virtual destructors and object slicing
standard: C++17
objective: make polymorphic deletion safe with a virtual destructor, and avoid slicing by keeping polymorphic objects behind indirection
prerequisites: virtual-dispatch
difficulty: 2
---

### the idea

two rules protect every polymorphic object, and both are easy to break without a compiler error. deleting a derived object through a base pointer is only defined when the base destructor is virtual. and polymorphism only works through references and pointers: copy a derived object into a base object and the derived part is simply cut off. one rule is about destruction and one about copying, but they come from the same fact: the static type and the dynamic type are different things.

### understanding the concept

a `delete` expression on a `Base*` calls the destructor through the static type. if that destructor is virtual, the call dispatches like any other virtual call and the whole `Derived` object is destroyed, members included. if it is not virtual, the behavior is undefined: in practice the derived members are not destroyed and the deallocation may use the wrong size, but the standard promises nothing at all.

slicing is the copying side. a `Base` object has room for a `Base` and nothing more, so initializing one from a `Derived` copies the `Base` subobject and discards the rest, including the vptr: the result really is a `Base`. this is not undefined behavior; it is well-defined and almost never what you meant.

### in code

second, the virtual destructor, and a twist with smart pointers.

```cpp
struct Plugin { ~Plugin() {} virtual void run() {} };   // BUG: non-virtual destructor
struct Logger : Plugin { std::string path; };

void demo() {
    std::unique_ptr<Plugin> p = std::make_unique<Logger>();
    p.reset();           // UB: deletes a Logger through Plugin* without a virtual dtor

    std::shared_ptr<Plugin> s = std::make_shared<Logger>();
    s.reset();           // OK, by accident: the control block remembers ~Logger
}
```

deleting a derived object through a base pointer whose destructor is not virtual is undefined behavior, not merely "the derived destructor is skipped". `unique_ptr<Base>` calls `delete` on a `Base*`, so it inherits the bug. `shared_ptr` happens to survive because the control block captured a deleter for the real type at creation, but relying on that is fragile. the rule: a class meant to be deleted through a base pointer gets a public virtual destructor; otherwise make the destructor protected and non-virtual. GCC's `-Wdelete-non-virtual-dtor` (in `-Wall`) catches a direct `delete base_ptr;`, but GCC 12 stays silent on the `unique_ptr` version above, because the `delete` happens inside a system header. `-Wnon-virtual-dtor` (not in `-Wall`) flags the class definition itself and catches both.

third, predict the output.

```cpp complete
#include <cstdio>
#include <vector>

struct Sensor {
    virtual ~Sensor() = default;
    virtual const char* name() const { return "sensor"; }
};
struct Lidar : Sensor {
    const char* name() const override { return "lidar"; }
};

int main() {
    Lidar lidar;
    Sensor& ref = lidar;
    Sensor copy = lidar;                  // slicing
    std::vector<Sensor> rack{lidar};      // slicing, again
    std::printf("%s %s %s\n", ref.name(), copy.name(), rack[0].name());
}
// prints: lidar sensor sensor
```

copying a `Lidar` into a `Sensor` object constructs a `Sensor` from the `Sensor` part and discards the rest: the object's type is `Sensor`, vptr included. polymorphism needs indirection (references, pointers, or `std::vector<std::unique_ptr<Sensor>>`). to make slicing impossible, delete or protect the base's copy operations ([[special-members]]); an abstract base cannot be sliced into at all.

### in practice

a plugin interface should make both mistakes impossible rather than merely documented:

```cpp
class Plugin {
public:
    virtual ~Plugin() = default;                   // safe to delete through Plugin*
    virtual void run() = 0;                        // abstract: a Plugin cannot be sliced into
    Plugin(const Plugin&) = delete;                // no copying a plugin through its interface
    Plugin& operator=(const Plugin&) = delete;
protected:
    Plugin() = default;
};

std::unique_ptr<Plugin> load_plugin(const std::string& name);
```

the virtual destructor makes `std::unique_ptr<Plugin>` correct; the pure virtual function makes the class abstract, so no `Plugin` object can be created by slicing; and the deleted copy operations stop derived classes from being copied through the base by accident. whether plugins themselves should be copyable is a separate decision, made in the derived classes.

### watch out for

**not every base class needs a virtual destructor.** a base that only shares implementation or a policy (and is never deleted through a base pointer) can instead have a *protected, non-virtual* destructor. then `delete base_ptr;` does not compile at all, so the undefined behavior is impossible, and the class pays for no vtable. the guideline from the C++ Core Guidelines (C.35) is: a base class destructor should be either public and virtual, or protected and non-virtual. a public, non-virtual destructor on a class with virtual functions is the combination to avoid, and `-Wnon-virtual-dtor` flags it.

### the takeaway

a base class meant for deletion through a pointer gets a public virtual destructor, and polymorphic objects live behind references and pointers, never in base-class values.

### optional challenge

given `struct Lidar : Sensor` with virtual functions, which of these lines slice?

```cpp
void f(Sensor s);                      // (1) called as f(lidar)
void g(const Sensor& s);               // (2) called as g(lidar)
Sensor* p = new Lidar;                 // (3)
Sensor s2 = *p;                        // (4)
std::vector<Sensor> v{Lidar{}};        // (5)
```

<details>
<summary>answer</summary>

(1), (4), and (5) slice: each creates a `Sensor` object from a `Lidar`, by-value parameter, copy, and container element alike. (2) binds a reference, and (3) points to the full `Lidar`, so dispatch still works through them. (4) is worth a second look: `*p` refers to a whole `Lidar`, but the declared type of `s2` decides what gets created. making `Sensor` abstract turns (1), (4), and (5) into compile errors.

</details>
