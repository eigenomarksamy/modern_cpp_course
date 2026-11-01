---
title: exclusive ownership with `std::unique_ptr`
standard: C++17
objective: own heap objects with `std::unique_ptr`, transfer ownership with `std::move`, and know what it costs
prerequisites: rule-of-zero
difficulty: 1
---

### the idea

`Detector* make_detector(const Config&);` hands the caller a heap object and an obligation: call `delete` exactly once, on every path, including the ones where an exception flies past. that is the same promise-everyone-must-keep that [[raii]] replaced for files. `std::unique_ptr` is RAII for heap objects, and in the common case it costs exactly as much as the raw pointer it replaces.

### understanding the concept

**`std::unique_ptr<T>`** is sole ownership: move-only ([[rule-of-zero]]), deletes the object in its destructor. with the default deleter, or any empty function-object deleter, it is typically the same size as a raw pointer, and `get()` and `operator->` compile down to the raw pointer. a stateful deleter costs its size: a function-pointer deleter typically doubles the `unique_ptr`. create one with `std::make_unique<T>(args...)` (C++14). before C++17, `make_unique` also prevented a leak in `f(std::unique_ptr<A>(new A), g())`, because the compiler could run `new A`, then `g()`, before constructing the `unique_ptr`. C++17 forbids that interleaving (each argument is fully evaluated before the next one starts), but `make_unique` is still the better spelling: no naked `new`, and the type is written once.

a `unique_ptr` converts to a `unique_ptr` of a base class, as long as the base has a virtual destructor, so a factory can return the concrete type and the caller can store it as the interface. `get()` lends the raw pointer without giving up ownership; `reset()` destroys the current object (and optionally adopts a new one); `release()` gives up ownership and returns the raw pointer, after which deleting it is your job again.

### in code

```cpp complete
#include <memory>
#include <vector>

struct Detector { virtual ~Detector() = default; virtual void run() = 0; };
struct CfarDetector : Detector { void run() override {} };

std::unique_ptr<Detector> make_detector() {
    return std::make_unique<CfarDetector>();    // converts to unique_ptr<Detector>
}

int main() {
    std::vector<std::unique_ptr<Detector>> stages;
    auto d = make_detector();
    stages.push_back(std::move(d));             // ownership moves; d is now empty
    // stages.push_back(d);                     // error: unique_ptr cannot be copied
    for (auto& s : stages) s->run();
}   // the vector's destructor deletes every detector exactly once
```

the commented-out line is the point of the type: the compiler refuses to create a second owner. ownership can only *move*, and every move is visible in the code as a `std::move`.

for arrays, `std::unique_ptr<float[]>` calls `delete[]` and offers `operator[]`; `std::make_unique<float[]>(n)` value-initializes the elements. in most code a `std::vector<float>` is still the better owner of a buffer, because it also knows its size.

### in practice

processing pipelines and plugin systems are full of objects with one obvious owner and a polymorphic type: stages built by a factory from a configuration file, drivers selected at startup, filters chosen per sensor. `std::vector<std::unique_ptr<Stage>>` holds them with no ceremony: the pipeline owns its stages, moving the pipeline moves the pointers (not the stages), and tearing it down deletes everything in reverse order of insertion. code that only *uses* a stage takes `Stage&`; nothing outside the pipeline ever sees a `unique_ptr`, which keeps the ownership decision in exactly one class.

### watch out for

**`release()` is not `reset()`.**

```cpp
std::unique_ptr<Frame> f = acquire();
f.release();    // BUG: gives up ownership and discards the pointer: a leak
f.reset();      // what was meant: destroy the frame, leave f empty
```

`release()` exists for handing ownership to code that takes a raw owning pointer (typically a C API or an old interface). call it only as part of that hand-off, in the same expression, and never just to "clear" the pointer.

### the takeaway

`std::unique_ptr` is sole ownership at the price of a raw pointer: create it with `make_unique`, transfer it with `std::move`, lend it with `*p` or `get()`, and let its destructor do the `delete`.

### optional challenge

which lines compile, and which compile but are still wrong?

```cpp
auto a = std::make_unique<int>(1);
auto b = a;                          // (1)
auto c = std::move(a);               // (2)
std::unique_ptr<int> d{c.get()};     // (3)
```

<details>
<summary>answer</summary>

(1) does not compile: the copy constructor is deleted. (2) compiles and leaves `a` empty. (3) compiles and is a bug: `c` and `d` both own the same `int`, and both destructors delete it, which is undefined behavior. constructing a `unique_ptr` from a raw pointer means "I am the owner now", so only do it with a pointer nobody else owns, ideally straight from `new` or a C API that transfers ownership.

</details>
