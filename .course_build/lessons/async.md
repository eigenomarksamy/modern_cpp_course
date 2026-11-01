---
title: `std::async` and its traps
standard: C++17
objective: use `std::async` for fork-join work with an explicit launch policy, and avoid the default policy and the blocking-destructor trap
prerequisites: futures
difficulty: 2
---

### the idea

`std::async` looks like the easiest way to run something concurrently: one call, and you get a future for the result. two of its rules are surprising enough to turn that one call into either no concurrency at all or code that silently runs sequentially. both rules exist for good reasons, and once you know them `std::async` is a fine tool for a small number of independent tasks.

### understanding the concept

`std::async(policy, f, args...)` bundles both: it runs `f` and gives you the future. the policy matters:

- `std::launch::async`: run as if on a new thread.
- `std::launch::deferred`: do nothing now; run `f` on the calling thread the first time someone calls `get()` or `wait()`.
- no policy (`async | deferred`): the implementation chooses. you might get no concurrency at all.

there is one more rule that surprises everyone: the destructor of the last future referring to a shared state created by `std::async` blocks until the task completes. that is deliberate (otherwise the task could outlive everything it references), but it has a sharp edge, shown below.

finally, C++20 still has no continuations: no `.then()`, no `when_all`. those lived in the concurrency TS and were not standardized. if you need composition, you need a library, or a different structure.

### in code

now fork-join over a point cloud with `std::async`, including the classic bug:

```cpp complete
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

recent libstdc++ marks `std::async` as `[[nodiscard]]`, so GCC warns about the bug version; do not count on every standard library doing so. the blocking destructor also does useful work here. if the first `get()` throws, the remaining futures are destroyed during stack unwinding, and each destructor waits for its task. so no task can still be reading `cloud` after `mean_height` has returned, and the `std::cref` is safe. a detached thread would offer no such guarantee.

### in practice

at startup, a robot loads its map, its URDF model, and its sensor calibrations. these are independent and I/O-heavy, so launching each with `std::async(std::launch::async, ...)` and calling `get()` on all three is a clean fork-join, with each loader's exceptions arriving at the one place that can decide whether to abort.

futures fit one-shot results. for a *stream* of items, use a queue ([[blocking-queue]]). for many small tasks, use a pool ([[sync-primitives]]) rather than one `std::async` per task, because whether `std::async` reuses threads is up to the implementation and you cannot bound how many it creates.

### watch out for

the default launch policy. `std::async(f)` may defer `f`, and a deferred task never runs until you call `get()` or `wait()`. this innocent-looking progress loop then never finishes:

```cpp
auto f = std::async(compute_tracks);   // policy: async | deferred, implementation's choice
while (f.wait_for(std::chrono::milliseconds(10)) != std::future_status::ready) {
    report_progress();                 // if deferred, wait_for returns 'deferred' forever
}
```

pass `std::launch::async` explicitly whenever you need concurrency, or handle `std::future_status::deferred` in the loop. treat the default policy as "I don't care whether this runs concurrently", which is rarely what you mean.

### the takeaway

name the launch policy, keep every `std::async` future alive for as long as the work should run in parallel, and reach for queues or pools when you have more than a handful of tasks.

### optional challenge

each loader takes about one second. roughly how long does this take, and why?

```cpp
void load_all() {
    std::async(std::launch::async, load_map);
    std::async(std::launch::async, load_model);
    std::async(std::launch::async, load_calibration);
}
```

<details>
<summary>answer</summary>

about three seconds. each returned future is a temporary destroyed at the end of its statement, and the destructor of the last future referring to an `std::async` shared state waits for the task, so each load finishes before the next one starts. keep the futures in named variables (or a container) and call `get()` on each at the end; the three loads then overlap and the function takes about one second, plus whatever the slowest loader adds.

</details>
