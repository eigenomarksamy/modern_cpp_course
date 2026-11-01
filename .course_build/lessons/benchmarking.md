---
title: measure first: honest benchmarks
standard: C++17
objective: write a microbenchmark the optimizer cannot hollow out, report robust statistics, and know what a benchmark does not tell you
prerequisites: algorithms, lambdas
difficulty: 2
---

### the idea

a colleague replaces a `std::map` with a sorted `std::vector` and posts a microbenchmark: 40 times faster. you rebuild it with `-O2` and the measured loop takes almost no time at all, because the compiler deleted it. both numbers are wrong, and only one of them looks wrong. performance work starts with measurements you can trust, and most bad optimization decisions trace back to a number nobody questioned.

### understanding the concept

intuition fails because the machine we reason about (one instruction after another, memory with uniform cost) is not the machine we run on. out-of-order execution, branch prediction, caches, prefetchers, and dynamic clock frequencies mean that instruction counts and complexity classes predict only part of the cost. complexity tells you how cost grows; constant factors, memory behavior, and the input distribution decide what happens at your sizes ([[sequence-containers]] made this point for containers).

- **benchmarks** answer "how long does this take, under these conditions?" a microbenchmark isolates one function. a macrobenchmark runs a realistic workload: replaying a recorded radar session, or a full planning cycle on logged sensor data.

for timing inside code, use `std::chrono::steady_clock`. it is monotonic, so an NTP adjustment cannot make an interval negative or inflate it. `system_clock` is calendar time and may jump. `high_resolution_clock` is allowed to be an alias of either (libstdc++ makes it `system_clock`, MSVC makes it `steady_clock`), so don't reach for it because of its name.

### in code

the benchmark from the idea, reduced to its bugs:

```cpp complete
#include <chrono>
#include <cstdio>
#include <numeric>
#include <vector>

int main() {
    std::vector<int> v(1'000'000, 1);
    auto t0 = std::chrono::system_clock::now();          // BUG: wall clock, may jump
    for (int rep = 0; rep < 100; ++rep) {
        int sum = std::accumulate(v.begin(), v.end(), 0); // BUG: result never used
        (void)sum;
    }
    auto t1 = std::chrono::system_clock::now();
    auto us = std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0);
    std::printf("100 sums: %lld us\n", static_cast<long long>(us.count()));
}
```

the sum has no observable effect, so under the as-if rule the optimizer may remove the whole loop (dead-code elimination). GCC 12 at `-O2` does exactly that: the generated assembly contains the two `now()` calls and nothing between them. even if the result were used, the input is a compile-time constant pattern the optimizer might fold. and it is one sample, taken cold, with no idea of the spread.

a small harness that fixes each problem:

```cpp complete
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <numeric>
#include <random>
#include <vector>

struct Stats { double median_us, min_us, max_us; };

template <typename F>
Stats measure(F&& work, int warmup = 3, int reps = 31) {
    using clock = std::chrono::steady_clock;          // monotonic: never jumps
    for (int i = 0; i < warmup; ++i) work();          // caches, page faults, clock ramp-up
    std::vector<double> samples;
    samples.reserve(reps);
    for (int i = 0; i < reps; ++i) {
        const auto t0 = clock::now();
        work();
        const auto t1 = clock::now();
        samples.push_back(std::chrono::duration<double, std::micro>(t1 - t0).count());
    }
    std::sort(samples.begin(), samples.end());
    return {samples[samples.size() / 2], samples.front(), samples.back()};
}

volatile long long g_sink;  // a volatile write is observable behavior: it must happen

int main(int argc, char**) {
    std::mt19937 rng(static_cast<unsigned>(argc));     // input unknown at compile time
    std::vector<int> v(1'000'000);
    for (auto& x : v) x = static_cast<int>(rng() % 100);

    const Stats s = measure([&] { g_sink = std::accumulate(v.begin(), v.end(), 0LL); });
    std::printf("median %.1f us (min %.1f, max %.1f)\n", s.median_us, s.min_us, s.max_us);
}
```

why the median and the extremes rather than the mean: timing noise is one-sided. interrupts, thread migrations, and page faults only ever add time, so the distribution has a long right tail that drags the mean around. the median is robust; the minimum approximates "nothing interfered"; the maximum tells you whether the tail matters. for a control loop with a deadline, the tail (p99, worst case) is the requirement, so report it.

### in practice

a radar team wants to catch performance regressions in CI. the naive version runs benchmarks on shared CI runners and fails the build if anything is 5 percent slower. within a week it is ignored, because run-to-run noise on a shared virtual machine is often larger than 5 percent.

what tends to work:

- run timing benchmarks on a dedicated, quiet machine with a fixed CPU frequency (the `performance` governor, turbo disabled) and pinned cores, or accept wider thresholds.
- compare against a stored baseline with repetitions on both sides, and flag only differences larger than the measured spread. Google Benchmark ships a `compare.py` tool for this.
- on noisy runners, track a proxy with less noise, such as instruction counts from `perf stat -e instructions` or Cachegrind. instructions are not time (a cache miss costs far more than an add), so treat a proxy alarm as a prompt to measure, not a verdict.

### watch out for

a microbenchmark is a best-case laboratory. the data is hot in cache, branches are perfectly predicted after a few iterations, the allocator has a warm free list, and no other thread competes for memory bandwidth. production sees cold caches, varied inputs, and contention. a function that wins a microbenchmark by 30 percent can make no measurable difference in the full pipeline, or even lose if its larger code or tables evict something else. always close the loop with a macro measurement.

### the takeaway

a benchmark number means nothing until you know what the compiler did to the measured code, which clock and statistics produced it, and how much it varies from run to run.

### optional challenge

a teammate benchmarks `std::sort` with the harness above: `measure([&] { std::sort(v.begin(), v.end()); })`. the median looks impressively low. what is it actually measuring, and how would you fix it?

<details>
<summary>answer</summary>

after the first warm-up call the vector is sorted, so every timed repetition sorts already-sorted data, which is a very different (and for typical introsort implementations, much cheaper) workload. copy the original unsorted input into a working vector inside each repetition. the copy then becomes part of the measurement, so either measure the copy alone and report both, or sort many independent copies prepared in advance and divide. Google Benchmark has `state.PauseTiming()`, but pausing has its own overhead and is unreliable for very short regions. the general lesson: a benchmark that mutates its input must restore it, or it measures a different input after the first iteration.

</details>

### going deeper

#### using a benchmark library

a hand-rolled harness is fine for a quick check, but a library handles iteration counts, repetitions, and statistics for you. with Google Benchmark (not part of the standard; shown for its idioms):

```cpp external
#include <benchmark/benchmark.h>
#include <map>

static void BM_MapFind(benchmark::State& state) {
    std::map<int, int> m;
    for (int i = 0; i < state.range(0); ++i) m[i * 2] = i;
    int key = 0;
    for (auto _ : state) {                         // the library chooses the iteration count
        auto it = m.find(key);
        benchmark::DoNotOptimize(it);              // forces the result to be "used"
        key = (key + 7) % static_cast<int>(2 * state.range(0));
    }
}
BENCHMARK(BM_MapFind)->Range(64, 1 << 16);         // several sizes, not one
BENCHMARK_MAIN();
```

run it with `--benchmark_repetitions=10 --benchmark_report_aggregates_only=true` to get mean, median, standard deviation, and coefficient of variation per size. note that `DoNotOptimize` keeps a value alive but does not stop the compiler from hoisting loop-invariant work out of the timed loop; the varying `key` above is what prevents that, and `benchmark::ClobberMemory()` exists for the memory side of the same problem.
