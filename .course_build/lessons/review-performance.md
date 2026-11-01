---
title: review: performance
kind: review
standard: C++17
objective: consolidate benchmarking, profiling, cache locality, data-oriented layout, allocation costs, and memory resources
prerequisites: benchmarking, profiling, cache-locality, data-oriented-design, allocation-costs, pmr-pools
difficulty: 2
---

### recap

| lesson | key idea |
|---|---|
| [[benchmarking]] | a benchmark number means nothing until you know what the compiler did, which statistics produced it, and how it varies. |
| [[profiling]] | profile optimized builds to find where time goes; Amdahl's law bounds what any fix can buy. |
| [[cache-locality]] | cache lines, prefetching, and memory-level parallelism decide what a loop costs; false sharing makes independent threads contend. |
| [[data-oriented-design]] | lay out data for the hot loops: AoS, SoA, or hot/cold splitting, kept behind an interface. |
| [[allocation-costs]] | count allocations, move them to startup, and test that the steady state is allocation-free. |
| [[pmr-pools]] | match the allocator to the pattern: arenas for data that dies together, pools for one size, a null upstream as a guard. |

### review questions

1. a microbenchmark says your new hash function is 25 percent faster, but the end-to-end frame time does not move. give two distinct explanations and how you would tell them apart.
2. after converting detections from AoS to SoA, the SNR gating loop got faster but the per-detection association step got slower. why is that plausible?
3. `std::pmr::vector<int> copy = arena_vec;` quietly puts `copy` on the heap. why, and how do you keep it in the arena?
4. two worker threads each increment their own counter in a `std::array<std::uint64_t, 2>`, with no sharing at all, and scale badly. what is happening, and what is the fix?
5. from [[rule-of-zero]]: why does adding a logging destructor to a struct stored in a large `std::vector` make reallocation slower?

### mini exercise

this function runs once per frame in a telemetry exporter. list where it may allocate, then sketch an allocation-free version, and say how you would verify it.

```cpp
std::string describe(const std::vector<Detection>& ds) {
    std::string out;
    for (const auto& d : ds) out += std::to_string(d.range_m) + " m, ";
    return out;
}
```

### answers

<details>
<summary>answer 1: faster microbenchmark, unchanged frame time</summary>

either the hash is a small share of the frame (Amdahl: 25 percent of 2 percent is invisible), or the microbenchmark's conditions (hot cache, one key pattern, no contention) do not hold in the pipeline. a profile of the real workload distinguishes them: if the hash's share is tiny, it is the first; if the share is large but did not shrink, it is the second.

</details>

<details>
<summary>answer 2: SoA helps one loop and hurts another</summary>

gating reads one field across many detections, so SoA packs 16 useful floats per line. association reads all fields of one detection at a time, which in SoA touches a different line per field instead of one line. layout should follow the dominant access pattern; sometimes a hot/cold split serves both.

</details>

<details>
<summary>answer 3: pmr copy on the heap</summary>

copy construction asks `select_on_container_copy_construction`, which for `polymorphic_allocator` returns a default-constructed allocator, meaning the default resource. use the allocator-extended constructor: `std::pmr::vector<int> copy(arena_vec, &arena);`.

</details>

<details>
<summary>answer 4: false sharing</summary>

the two counters sit on the same cache line, and cache coherence works per line: every increment by one core invalidates the line in the other core's cache, so the threads contend as if they shared a variable. give each counter its own line (`struct alignas(64) Counter { std::uint64_t value; };`), or accumulate in a local variable and write the total once.

</details>

<details>
<summary>answer 5: a destructor suppresses moves</summary>

declaring a destructor suppresses the implicit move constructor, so the type's "moves" are copies, and `std::vector` reallocation copies every element (including any heap-owning members) instead of moving them. remove the destructor or default all five special members explicitly ([[special-members]]).

</details>

<details>
<summary>mini exercise answer</summary>

it may allocate in `std::to_string` (if the text exceeds the small-string buffer), in the temporary created by `to_string(...) + " m, "`, every time `out` grows, and for the returned string itself. an allocation-free version takes a caller-owned output buffer that is reused every frame, reserves it once, and formats numbers with `std::to_chars` into a stack buffer before appending:

```cpp
#include <charconv>
#include <string>
#include <vector>

void describe(const std::vector<Detection>& ds, std::string& out) {   // out reused by the caller
    out.clear();                                                        // keeps capacity
    char num[32];
    for (const auto& d : ds) {
        auto [end, ec] = std::to_chars(num, num + sizeof num, d.range_m);
        out.append(num, end);
        out.append(" m, ");
    }
}
```

once `out` has grown to the largest frame seen, the steady state allocates nothing. verify it with the allocation counter from [[allocation-costs]] in a test that runs many frames after a warm-up, rather than by reading the code: whether a given call allocates is an implementation detail.

</details>

### connections

performance work in C++ is mostly about memory: where bytes live, how often they are allocated, and which cores fight over them. the habits from this module (measure first, check the mechanism with counters, keep the fast path allocation-free, encapsulate layout decisions) apply to every earlier module, from container choice to concurrency. the final module turns to the rest of production engineering, and then puts the whole course together.
