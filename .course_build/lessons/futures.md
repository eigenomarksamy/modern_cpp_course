---
title: promises and futures: one-shot results across threads
standard: C++17
objective: return a value or an exception from another thread through a promise and future, and know the edge cases of the shared state
prerequisites: blocking-queue, exception-safety
difficulty: 2
---

### the idea

a thread function returns `void`, and an exception that escapes it calls `std::terminate` ([[threads]]). so how does a worker hand back "here are the surface normals for your point cloud chunk" or "the calibration file was corrupt"? you could build a queue ([[blocking-queue]]) for a single value, plus an error slot, plus a flag. the standard library already has that one-shot channel: a promise on one end, a future on the other.

### understanding the concept

`std::promise<T>` and `std::future<T>` share a heap-allocated *shared state* holding either a `T` or a `std::exception_ptr`. the promise writes it exactly once with `set_value` or `set_exception`, which makes the state *ready*. the future waits for that with `wait()`, `wait_for()`, or `get()`. making the state ready synchronizes with the return of the call that observes it, so everything the producer wrote before `set_value` is visible after `get()` returns, much like `join`.

the edges are well defined, and worth knowing:

| situation | result |
|---|---|
| `get()` on a ready future holding an exception | the exception is rethrown in the caller |
| `get()` called twice on a `std::future` | UB: `get()` leaves the future invalid (`valid() == false`), and calling `get` or a `wait` function on an invalid future is UB; libstdc++ happens to throw `std::future_error` |
| promise destroyed without setting anything | the future receives a `std::future_error` with `broken_promise` |
| `set_value` called twice | `std::future_error` with `promise_already_satisfied` |

`std::packaged_task<R(Args...)>` wraps a callable together with a promise: invoking the task calls the function and stores the return value or the thrown exception. it separates *what* to run from *where* it runs, which is exactly what a task queue or thread pool needs.

`std::shared_future<T>` lets several consumers wait for the same result; `get()` returns a `const T&` and can be called repeatedly. give each thread its own copy of the `shared_future` object: copies referring to one shared state are safe to use concurrently, while calls on a single object from several threads are not synchronized.

### in code

a worker that reports either a result or its exception:

```cpp complete
#include <future>
#include <stdexcept>
#include <thread>

struct Calibration { double offset; double gain; };

Calibration run_calibration() { throw std::runtime_error("checksum mismatch"); }

void calibrate(std::promise<Calibration> result) {
    try {
        result.set_value(run_calibration());
    } catch (...) {
        result.set_exception(std::current_exception());  // ships the exception to get()
    }
}

int main() {
    std::promise<Calibration> p;
    std::future<Calibration> f = p.get_future();
    std::thread worker(calibrate, std::move(p));        // the promise is move-only
    try {
        Calibration c = f.get();                        // rethrows runtime_error here
        (void)c;
    } catch (const std::exception& e) {
        // report e.what(): "checksum mismatch"
    }
    worker.join();
}
```

third, `std::packaged_task` separates the callable from the thread that runs it:

```cpp complete
#include <future>
#include <stdexcept>
#include <thread>

int main() {
    std::packaged_task<int(int)> task([](int range_bin) {
        if (range_bin < 0) throw std::out_of_range("negative range bin");
        return range_bin * 2;
    });
    std::future<int> f = task.get_future();
    std::thread t(std::move(task), 21);   // packaged_task is move-only, like the promise
    t.join();
    return f.get() == 42 ? 0 : 1;         // the value, or the exception, is in f
}
```

`packaged_task` is move-only, and `std::function` requires a copyable callable, so a pool built on `std::queue<std::function<void()>>` cannot hold one directly. the usual C++17/20 workaround is to wrap it in a `std::shared_ptr` and capture that; C++23 adds `std::move_only_function` for exactly this reason.

### in practice

several sensor threads may need the calibration before they start publishing. a `std::shared_future<Calibration>` (from `f.share()`) handed to each of them, by value, lets them all block on `get()` until it is ready, with no extra flags or condition variables.

### watch out for

**a `std::future` has exactly one `get()`.**

```cpp
std::future<Calibration> f = p.get_future();
Calibration a = f.get();
Calibration b = f.get();   // BUG: f is no longer valid: undefined behavior
```

`get()` moves the result out and leaves the future invalid (`f.valid()` is `false`); libstdc++ happens to throw `std::future_error`, and another library may do anything. when two parts of the program need the same result, convert once with `f.share()` and give each consumer its own copy of the `std::shared_future`.

### the takeaway

a promise and a future form a one-shot channel that carries either a value or an exception and synchronizes like `join`; one producer sets it once, and one consumer reads it once unless you share it.

### optional challenge

`calibrate` is changed to return early, without touching the promise, when the calibration file does not exist. what does the caller's `f.get()` do now?

<details>
<summary>answer</summary>

when `calibrate` returns, its by-value `std::promise` parameter is destroyed without having set a value. the destructor stores a `std::future_error` with error code `std::future_errc::broken_promise` in the shared state and makes it ready, so `f.get()` throws that exception. the caller does not hang, which is the point: abandoning a promise is reported, not silently lost. it is still better to call `set_exception` with a meaningful error, because "broken promise" tells the caller nothing about the missing file.

</details>
