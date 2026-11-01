---
title: lambdas that outlive their scope: callbacks and `std::function`
standard: C++17
objective: capture safely for lambdas that are stored or deferred, and choose between `std::function` and a template parameter
prerequisites: lambdas
difficulty: 2
---

### the idea

a lambda passed to `std::sort` runs and is gone before the next line. a lambda passed to a timer, an event bus, or another thread runs *later*, after the function that created it may have returned. every capture is then a question about lifetime: does the object it refers to still exist when the callback finally fires? and once callbacks are stored, they need a type you can store them as, which brings type erasure and its costs.

### understanding the concept

`[&]` is fine when the lambda runs before the enclosing scope ends: a predicate passed to `std::find_if`, a comparator for `std::sort`. it is a liability as soon as the lambda is stored, deferred, or handed to another thread. a useful rule: if the lambda leaves the scope, capture by value or by init-capture, and if it must refer to a shared object, capture something that tracks lifetime (a `std::weak_ptr`, [[shared-ptr]]) rather than a raw pointer or reference.

a stored callback also needs a type that can hold "any callable with this signature", because every lambda has its own unique type. `std::function<R(Args...)>` is that type. it is a value that owns a copy of the callable and erases the callable's concrete type behind an internal interface.

`std::function` stores the callable behind a type-erased interface ([[type-erasure]] shows how). that costs an indirect call that the optimizer usually cannot inline, and possibly a heap allocation when the callable is too large for the internal buffer. the buffer size is a library detail: with libstdc++ in GCC 12, a lambda capturing two `double`s is stored inline and one capturing three `double`s allocates once. it also requires the callable to be copy-constructible, so closures owning a `unique_ptr` are rejected. (C++23 adds `std::move_only_function` for that case.) the template version has none of those costs, but it must be visible in a header and is instantiated once per callable type.

### in code

the bug that matters most is a reference capture that outlives its referent. the lambda escapes the function, the stack frame goes away, and the closure holds a reference to nothing.

```cpp ub
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

now `std::function` versus a template parameter:

```cpp complete
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

### in practice

a point-cloud preprocessing library exposes a filter step that takes a user predicate. the first API used `std::function<bool(const Point&)>`, because it compiles into a single function in a `.cpp` file and accepts anything. profiling a 100,000-point cloud at 20 Hz showed the per-point indirect call in the hot loop, and the predicate's body could not be inlined or vectorized with the loop.

the fix is not "never use `std::function`". it is placing the type erasure where the call frequency is low. the library now takes a template parameter for the per-point predicate, and uses `std::function` for the per-frame "on cloud ready" callback, which fires twenty times a second and benefits from a stable, non-template, ABI-friendly signature. that is the general judgment: type erasure buys decoupling and a stable binary interface; templates buy inlining at the cost of compile time and header exposure. pick per call site, and confirm with a profiler ([[profiling]]) that the hot path is really where you think it is.

### watch out for

**an empty `std::function` throws when called.** a default-constructed or moved-from `std::function` holds nothing, and calling it throws `std::bad_function_call`. in an event loop that means an exception from deep inside dispatch, far from the code that forgot to set the handler. test before calling (`if (on_ready) on_ready(frame);`), or give the member a no-op default (`std::function<void(const Frame&)> on_ready = [](const Frame&) {};`) so the "not set" state cannot occur.

### the takeaway

if a lambda leaves its scope, capture by value, by init-capture, or through a lifetime-tracking handle; use templates for hot-path callables and `std::function` at boundaries where flexibility and a stable signature are worth an indirect call.

### optional challenge

`Bus::on_frame` stores its callback for as long as the bus lives, which is longer than `wire`. which subscriptions are safe?

```cpp
void wire(Bus& bus, Sensor& s, std::shared_ptr<Log> log) {
    int threshold = 5;
    bus.on_frame([&](const Frame& f) { if (f.count > threshold) s.update(f); });        // (1)
    bus.on_frame([threshold](const Frame& f) { /* uses threshold */ });                 // (2)
    bus.on_frame([&s](const Frame& f) { s.update(f); });                                // (3)
    bus.on_frame([log](const Frame& f) { log->write(f); });                             // (4)
    bus.on_frame([w = std::weak_ptr<Log>(log)](const Frame& f) {
        if (auto l = w.lock()) l->write(f);                                             // (5)
    });
}
```

<details>
<summary>answer</summary>

(1) is a bug: `threshold` is a local of `wire`, and every later frame reads a dead variable. (2) is safe: the closure owns a copy. (3) is safe only if the sensor outlives the subscription; that is a lifetime contract between the code that owns the sensor and the code that owns the bus, and it should be written down. (4) is safe, and it keeps the log alive as long as the bus holds the callback, which may be forever; if the log also refers back to the bus, that is a reference cycle. (5) is safe without extending the log's life: when the log is gone, `lock()` returns an empty pointer and the callback does nothing.

</details>
