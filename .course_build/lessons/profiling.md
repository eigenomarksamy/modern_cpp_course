---
title: profiling: finding where the time goes
standard: C++17
objective: use sampling and instrumentation profilers on optimized builds, and use Amdahl's law to decide whether an optimization can matter
prerequisites: benchmarking, raii
difficulty: 2
---

### the idea

a planning cycle sometimes misses its 50 ms deadline. the team has three theories (the collision checker, the cost map update, the logging), and three engineers ready to optimize their favorite. a profiler replaces the theories with data in an afternoon, and Amdahl's law tells you, before anyone writes code, how much each fix could possibly buy.

### understanding the concept

two kinds of tools answer two different questions:

- **benchmarks** answer "how long does this take, under these conditions?" a microbenchmark isolates one function. a macrobenchmark runs a realistic workload: replaying a recorded radar session, or a full planning cycle on logged sensor data.
- **profilers** answer "where does the time go?" sampling profilers (`perf` on Linux, Intel VTune, Apple Instruments) interrupt the program at intervals and record the call stack: low overhead, whole-program coverage, statistical results. instrumentation profilers (Tracy, or your own scope timers) record explicit begin and end events, giving exact per-frame, per-thread timelines at the cost of touching the code. a flame graph draws sampled stacks so that width is proportional to time: wide plateaus are where to look.

the workflow that works: profile a realistic run to find the hot spot, write a benchmark around that hot spot, change the code, benchmark again, then confirm with the profiler that the whole program got faster, not just the microbenchmark.

**Amdahl's law** bounds what any optimization can buy. if a fraction `p` of the runtime is sped up by a factor `s`, the overall speedup is `1 / ((1 - p) + p / s)`. make a function that takes 10 percent of the frame infinitely fast and you save at most 10 percent. this is why profiling comes first: it tells you `p` before you spend effort on `s`.

### in code

sampling needs no code changes; it needs the right build:

```sh
g++ -O2 -g -fno-omit-frame-pointer ...        # optimized, but with usable stacks
perf record -g ./radar_replay session.bin     # sample with call graphs
perf report                                   # or render a flame graph from 'perf script'
```

a debug build measures a different program: no inlining, every abstraction paid in full. its hot spots are frequently not the release build's hot spots.

instrumentation is the opposite trade: you add probes, and in exchange you get exact per-frame timings. the simplest probe is an RAII scope timer:

```cpp complete
#include <chrono>
#include <cstdio>

class ScopeTimer {                          // a minimal instrumentation probe
public:
    explicit ScopeTimer(const char* name) : name_(name), t0_(std::chrono::steady_clock::now()) {}
    ~ScopeTimer() {
        const auto us = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::steady_clock::now() - t0_).count();
        std::printf("%s: %lld us\n", name_, static_cast<long long>(us));
    }
    ScopeTimer(const ScopeTimer&) = delete;
    ScopeTimer& operator=(const ScopeTimer&) = delete;
private:
    const char* name_;
    std::chrono::steady_clock::time_point t0_;
};

void plan_cycle() {
    ScopeTimer t("plan_cycle");             // reported when the function exits, by any path
    // ...
}
```

real instrumentation profilers (Tracy, Perfetto, or your middleware's tracing) record these begin and end events into a buffer instead of printing them, and draw them as a timeline per thread.

### in practice

averages hide the problem in real-time systems. a sampling profile of the planner says where time goes *on average*, which is the right first question for throughput, but a deadline miss is about the slowest cycle, not the typical one. the useful combination is a sampling profile to find the generally expensive code, then instrumentation around each stage of the cycle to find *which* cycles are slow and what happened in them: a periodic map reload, a lock held by a logging thread, an allocation spike every hundredth frame. the timeline view, one row per thread, makes those visible in a way no average can.

### watch out for

remember the other side of the ledger, too: every optimization has a maintenance cost (less obvious code, more invariants, more tests). optimize where the profile points, stop when the requirement is met, and leave a comment with the measurement that justified the change.

### the takeaway

profile to find where time goes, benchmark to compare alternatives, and distrust any number until you know what the compiler did to the code and how much the result varies.

### optional challenge

collision checking takes 30 percent of a planning cycle. one engineer can make it three times faster; another proposes eliminating it entirely with a cached approximation. by Amdahl's law, what overall speedup does each achieve?

<details>
<summary>answer</summary>

with `p = 0.3`: three times faster gives `1 / (0.7 + 0.3 / 3) = 1 / 0.8 = 1.25`, a 25 percent faster cycle. eliminating it entirely gives at most `1 / 0.7`, about 1.43. the second proposal can never beat 1.43 no matter how clever, and it changes behavior; the first gets most of the available benefit. if the goal is a cycle twice as fast, neither is enough on its own, which is exactly the kind of conclusion worth reaching before writing code.

</details>
