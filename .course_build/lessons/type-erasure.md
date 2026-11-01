---
title: type erasure: value semantics without inheritance
standard: C++20
objective: implement a small type-erased wrapper with an internal concept and model, and know its costs compared with a plain virtual interface
prerequisites: static-polymorphism, callbacks, rule-of-zero
difficulty: 3
---

### the idea

`std::function<void()>` holds a lambda, a function pointer, or your own function object, and none of them inherits from anything. you store them by value, copy them, and put them in a vector. the trick behind it is not specific to callables: any set of operations can be wrapped this way, which lets a library accept types it has never seen without asking them to derive from its base class.

### understanding the concept

**type erasure** is how `std::function` and `std::any` work. a template constructor sees the concrete type once, wraps it in an internal "model" object that implements a private interface, and stores it behind a pointer of fixed type. after construction the wrapper's type no longer mentions the concrete type: it has been erased. inheritance still exists, but it is hidden inside the wrapper instead of imposed on users.

### in code

**hand-written type erasure.** the users' types implement nothing; they only need a free function `to_text` that argument-dependent lookup can find, which also works for the vendor type because you can write that function yourself in its namespace.

```cpp complete
#include <concepts>
#include <memory>
#include <string>
#include <utility>

template <typename T>
concept TextRenderable = requires(const T& t) {
    { to_text(t) } -> std::convertible_to<std::string>;
};

class Record {
public:
    template <TextRenderable T>
    Record(T value) : self_(std::make_unique<Model<T>>(std::move(value))) {}

    Record(const Record& other) : self_(other.self_->clone()) {}
    Record& operator=(const Record& other) { return *this = Record(other); }
    Record(Record&&) noexcept = default;
    Record& operator=(Record&&) noexcept = default;

    friend std::string to_text(const Record& r) { return r.self_->render(); }

private:
    struct Concept {                                    // private interface
        virtual ~Concept() = default;
        virtual std::string render() const = 0;
        virtual std::unique_ptr<Concept> clone() const = 0;
    };
    template <typename T>
    struct Model final : Concept {                      // one per stored type
        explicit Model(T v) : value(std::move(v)) {}
        std::string render() const override { return to_text(value); }
        std::unique_ptr<Concept> clone() const override { return std::make_unique<Model>(*this); }
        T value;
    };
    std::unique_ptr<Concept> self_;
};
```

the virtual function is named `render`, not `to_text`, on purpose: inside `Model`, an unqualified call to `to_text` would otherwise find the member first, and finding a class member suppresses argument-dependent lookup, so the user's free function would never be considered.

using it:

```cpp
#include <iostream>
#include <vector>

namespace imu {
struct Sample { int seq; };
std::string to_text(const Sample& s) { return "imu #" + std::to_string(s.seq); }
}
namespace vendor {                                      // pretend we cannot edit this struct
struct GpsFix { int sats; };
}
namespace vendor {                                      // but we can add a function next to it
std::string to_text(const GpsFix& g) { return "gps sats=" + std::to_string(g.sats); }
}

int main() {
    std::vector<Record> records{imu::Sample{41}, vendor::GpsFix{9}};
    records.push_back(records.front());                  // value semantics: deep copy
    for (const auto& r : records) std::cout << to_text(r) << '\n';
    // prints: imu #41
    //         gps sats=9
    //         imu #41
}
```

adding a function to a vendor's namespace is your code, in your translation units, so it is fine; adding declarations to namespace `std` is not (with narrow exceptions such as specializing certain templates for your own types).

### in practice

Sean Parent's line "inheritance is the base class of evil" is about the first option leaking into everything: if the interface is a base class, every user type must inherit from it, objects live behind pointers, and copying needs a `clone()` hierarchy. type erasure keeps the inheritance private and gives users plain value types.

the same structure appears wherever a library must accept arbitrary user types by value: `std::function` for callables, `std::any` for anything copyable, custom wrappers for "anything drawable", "anything serializable", or "anything that can be a task". writing one is a deliberate trade: forty lines of wrapper code, written once, against a constraint imposed on every user type forever.

### watch out for

**type erasure is not free and not always worth it.** the wrapper above allocates once per stored object and once per copy, every call is an indirect call, and debuggers show you `Model<imu::Sample>` frames you did not write. real implementations often add a **small buffer optimization**: store small objects inside the wrapper itself and fall back to the heap for large ones. whether and when `std::function` does this is an implementation detail (buffer sizes and conditions differ between libstdc++, libc++, and MSVC), so do not design around it; count allocations if it matters ([[allocation-costs]]). also note that the wrapper requires copyable types; a move-only callable needs a move-only wrapper, which the standard only provides in C++23 (`std::move_only_function`).

if you own all the types, need reference semantics anyway, and the set is open, a ten-line virtual interface is easier to read and debug than a forty-line erased wrapper. reach for type erasure when you need value semantics or must accept types that cannot inherit from your base.

### the takeaway

type erasure hides inheritance inside a wrapper: a template constructor captures the concrete type in a private model, and users get plain value types; use it when you need value semantics or must accept types that cannot inherit, and prefer a simple virtual interface otherwise.

### optional challenge

`Record`'s converting constructor takes `T` by value and is constrained by `TextRenderable`. `Record` itself satisfies `TextRenderable` (its hidden friend `to_text` is found by ADL). so why doesn't `Record copy = records.front();` wrap a `Record` inside a `Model<Record>`?

<details>
<summary>answer</summary>

because the copy constructor wins. for `Record copy = records.front();` the argument is a `Record` lvalue. overload resolution looks at the copy constructor `Record(const Record&)` and at the constructor template, but the standard says a constructor template is never instantiated to produce a constructor whose first parameter is the class type by value (that signature would be a broken copy constructor), so the template is not a viable candidate here. if the constructor took `T&&` (a forwarding reference) instead, a non-const lvalue `Record` would deduce `T = Record&`, the template would be a better match than `const Record&`, and copying would try to wrap a `Record` inside a `Model<Record>`: at best a silent extra layer of allocation and indirection per copy, and with this concept GCC 12 reports a recursive constraint error instead. that is why forwarding constructors in erased wrappers need an explicit `!std::same_as<std::remove_cvref_t<T>, Record>` constraint.

</details>
