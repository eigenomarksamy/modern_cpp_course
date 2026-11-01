<a id="day-39"></a>

## day 39: futures, promises, and tasks

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 20, 36, 38

### the idea

A thread function returns `void`, and an exception that escapes it calls `std::terminate` (day 36). So how does a worker hand back "here are the surface normals for your point cloud chunk" or "the calibration file was corrupt"? You could build a queue (day 38) for a single value, plus an error slot, plus a flag. The standard library already has that one-shot channel: a promise on one end, a future on the other.

### understanding the concept

`std::promise<T>` and `std::future<T>` share a heap-allocated *shared state* holding either a `T` or a `std::exception_ptr`. The promise writes it exactly once with `set_value` or `set_exception`, which makes the state *ready*. The future waits for that with `wait()`, `wait_for()`, or `get()`. Making the state ready synchronizes with the return of the call that observes it, so everything the producer wrote before `set_value` is visible after `get()` returns, much like `join`.

The edges are well defined, and worth knowing:

| situation | result |
|---|---|
| `get()` on a ready future holding an exception | the exception is rethrown in the caller |
| `get()` called twice on a `std::future` | UB: `get()` leaves the future invalid (`valid() == false`), and calling `get` or a `wait` function on an invalid future is UB; libstdc++ happens to throw `std::future_error` |
| promise destroyed without setting anything | the future receives a `std::future_error` with `broken_promise` |
| `set_value` called twice | `std::future_error` with `promise_already_satisfied` |

`std::packaged_task<R(Args...)>` wraps a callable together with a promise: invoking the task calls the function and stores the return value or the thrown exception. It separates *what* to run from *where* it runs, which is exactly what a task queue or thread pool needs.

`std::async(policy, f, args...)` bundles both: it runs `f` and gives you the future. The policy matters:

- `std::launch::async`: run as if on a new thread.
- `std::launch::deferred`: do nothing now; run `f` on the calling thread the first time someone calls `get()` or `wait()`.
- no policy (`async | deferred`): the implementation chooses. You might get no concurrency at all.

There is one more rule that surprises everyone: the destructor of the last future referring to a shared state created by `std::async` blocks until the task completes. That is deliberate (otherwise the task could outlive everything it references), but it has a sharp edge, shown below.

`std::shared_future<T>` lets several consumers wait for the same result; `get()` returns a `const T&` and can be called repeatedly. Give each thread its own copy of the `shared_future` object: copies referring to one shared state are safe to use concurrently, while calls on a single object from several threads are not synchronized.

Finally, C++20 still has no continuations: no `.then()`, no `when_all`. Those lived in the Concurrency TS and were not standardized. If you need composition, you need a library, or a different structure.

### in code

A worker that reports either a result or its exception:

```cpp
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

Now fork-join over a point cloud with `std::async`, including the classic bug:

```cpp
#include <algorithm>
#include <cstddef>
#include <functional>
#include <future>
#include <vector>

struct Point { float x, y, z; };

double sum_heights(const std::vector<Point>& cloud, std::size_t first, std::size_t last) {
    double sum = 0;
    for (std::size_t i = first; i < last; ++i) sum += cloud[i].z;
    return sum;
}

double mean_height(const std::vector<Point>& cloud, std::size_t parts) {  // parts > 0
    const std::size_t n = cloud.size(), step = (n + parts - 1) / parts;
    std::vector<std::future<double>> futures;
    for (std::size_t first = 0; first < n; first += step) {
        const std::size_t last = std::min(first + step, n);
        // BUG version: std::async(std::launch::async, sum_heights, std::cref(cloud), first, last);
        // The discarded future is destroyed at the end of the statement and waits:
        // every chunk runs to completion before the next starts. Sequential, with thread overhead.
        futures.push_back(std::async(std::launch::async, sum_heights,
                                     std::cref(cloud), first, last));
    }
    double total = 0;
    for (auto& f : futures) total += f.get();  // may rethrow a chunk's exception
    return n ? total / n : 0.0;
}
```

Recent libstdc++ marks `std::async` as `[[nodiscard]]`, so GCC warns about the bug version; do not count on every standard library doing so. The blocking destructor also does useful work here. If the first `get()` throws, the remaining futures are destroyed during stack unwinding, and each destructor waits for its task. So no task can still be reading `cloud` after `mean_height` has returned, and the `std::cref` is safe. A detached thread would offer no such guarantee.

Third, `std::packaged_task` separates the callable from the thread that runs it:

```cpp
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

`packaged_task` is move-only, and `std::function` requires a copyable callable, so a pool built on `std::queue<std::function<void()>>` cannot hold one directly. The usual C++17/20 workaround is to wrap it in a `std::shared_ptr` and capture that; C++23 adds `std::move_only_function` for exactly this reason.

### in practice

At startup, a robot loads its map, its URDF model, and its sensor calibrations. These are independent and I/O-heavy, so launching each with `std::async(std::launch::async, ...)` and calling `get()` on all three is a clean fork-join, with each loader's exceptions arriving at the one place that can decide whether to abort.

Several sensor threads may need the calibration before they start publishing. A `std::shared_future<Calibration>` (from `f.share()`) handed to each of them, by value, lets them all block on `get()` until it is ready, with no extra flags or condition variables.

Futures fit one-shot results. For a *stream* of items, use a queue (day 38). For many small tasks, use a pool (day 41) rather than one `std::async` per task, because whether `std::async` reuses threads is up to the implementation and you cannot bound how many it creates.

### watch out for

The default launch policy. `std::async(f)` may defer `f`, and a deferred task never runs until you call `get()` or `wait()`. This innocent-looking progress loop then never finishes:

```cpp
auto f = std::async(compute_tracks);   // policy: async | deferred, implementation's choice
while (f.wait_for(std::chrono::milliseconds(10)) != std::future_status::ready) {
    report_progress();                 // if deferred, wait_for returns 'deferred' forever
}
```

Pass `std::launch::async` explicitly whenever you need concurrency, or handle `std::future_status::deferred` in the loop. Treat the default policy as "I don't care whether this runs concurrently", which is rarely what you mean.

### the takeaway

A future is a one-shot channel that carries a value or an exception and synchronizes like `join`. Name the launch policy, keep every `std::async` future alive for as long as the work should run in parallel, and reach for queues or pools when you have more than a handful of tasks.

### optional challenge

`calibrate` is changed to return early, without touching the promise, when the calibration file does not exist. What does the caller's `f.get()` do now?

<details>
<summary>answer</summary>

When `calibrate` returns, its by-value `std::promise` parameter is destroyed without having set a value. The destructor stores a `std::future_error` with error code `std::future_errc::broken_promise` in the shared state and makes it ready, so `f.get()` throws that exception. The caller does not hang, which is the point: abandoning a promise is reported, not silently lost. It is still better to call `set_exception` with a meaningful error, because "broken promise" tells the caller nothing about the missing file.

</details>
