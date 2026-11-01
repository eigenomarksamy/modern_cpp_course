---
title: inside a coroutine: writing a generator type
standard: C++20
objective: implement a minimal generator by providing a promise_type, and explain each step the compiler takes when a coroutine starts, yields, and finishes
prerequisites: coroutines, move-semantics
difficulty: 3
---

### the idea

C++20 ships the coroutine *machinery* and almost no coroutine *types*: there is no `std::generator` until C++23 and no standard task type at all. that makes the contract between the compiler and a coroutine's return type worth understanding once, even if you will mostly use a library: it is what you read in a debugger, what decides when a coroutine runs, and what owns its frame.

### understanding the concept

walk through it once. calling a coroutine allocates the frame, constructs the promise, calls `get_return_object()` (which is what the caller receives), then `co_await`s `initial_suspend()`. ours suspends, so nothing runs until the first `next()`. each `co_yield v` becomes `co_await promise.yield_value(v)`, which stores the value and suspends. falling off the end calls `return_void()` and suspends at `final_suspend()`, so `done()` becomes true and the `Generator` destructor frees the frame. (this version requires `T` to be default-constructible; a production one would store a pointer or `std::optional`.)

### in code

**a hand-written generator.** this is the whole contract between the compiler and a generator type.

```cpp complete
#include <coroutine>
#include <utility>

template <typename T>
class Generator {
public:
    struct promise_type {
        T current{};
        Generator get_return_object() {
            return Generator(std::coroutine_handle<promise_type>::from_promise(*this));
        }
        std::suspend_always initial_suspend() noexcept { return {}; }  // start lazily
        std::suspend_always final_suspend() noexcept { return {}; }    // keep frame until we destroy it
        std::suspend_always yield_value(T v) {                         // co_yield v
            current = std::move(v);
            return {};
        }
        void return_void() noexcept {}
        void unhandled_exception() { throw; }  // rethrows out of resume() into next()
    };

    explicit Generator(std::coroutine_handle<promise_type> h) : h_(h) {}
    Generator(Generator&& o) noexcept : h_(std::exchange(o.h_, {})) {}
    Generator& operator=(Generator&&) = delete;
    ~Generator() { if (h_) h_.destroy(); }         // RAII for the frame

    bool next() {                                  // run to the next co_yield or the end
        h_.resume();
        return !h_.done();
    }
    const T& value() const { return h_.promise().current; }

private:
    std::coroutine_handle<promise_type> h_;
};
```

### in practice

also count the cost: each coroutine call may allocate a frame, and every resume is typically an indirect call through the handle. that is irrelevant for an uploader and potentially relevant in a 10 kHz control loop; custom `operator new` on the promise type gives you control of the allocation, and a profiler tells you whether it matters.

### watch out for

**resuming a finished coroutine is undefined behavior.** `next()` above resumes unconditionally. after it has returned `false` once, the coroutine is suspended at its final suspend point, and calling `next()` again calls `resume()` on it:

```cpp
auto scan = serpentine_scan(1, 1);
scan.next();   // true: (0,0)
scan.next();   // false: done
scan.next();   // BUG: resumes a coroutine at its final suspend point
```

a robust wrapper checks `h_.done()` before resuming (and returns `false` again), or exposes an iterator interface whose `end()` makes the misuse impossible. it should also check for a null handle, which a moved-from `Generator` holds.

### the takeaway

a coroutine's return type defines its behavior through `promise_type`: when it starts, what `co_yield` does, and who destroys the frame; design the suspend points and the wrapper's API together, and guard every resume.

### optional challenge

what does `serpentine_scan(2, 3)` execute before the first call to `next()`, and what would change if `initial_suspend()` returned `std::suspend_never`?

<details>
<summary>answer</summary>

with `suspend_always`, the call allocates the frame, copies `rows` and `cols` into it, constructs the promise, obtains the `Generator`, and suspends at the initial suspend point: none of the loop body runs. with `suspend_never`, the body runs immediately until the first `co_yield`, so `current` already holds `(0,0)` when the caller receives the generator. our `next()` resumes before reading, so the first `next()` would then skip to `(0,1)` and `(0,0)` would be lost. eager start is a legitimate design (some task types use it), but the rest of the type has to be written for it; this is why the promise's suspend points and the wrapper's API must be designed together.

</details>
