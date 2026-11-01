---
title: cache locality: why the same loop can be slower
standard: C++17
objective: explain cache lines, prefetching, and memory-level parallelism, and predict which traversals are fast, slow, or contended
prerequisites: profiling, object-layout, sequence-containers
difficulty: 2
---

### the idea

two loops do the same arithmetic over the same number of elements, both O(n), and one runs several times slower than the other. nothing in the source explains it, because the difference is not in the instructions: it is in where the bytes live. most code that is "slow for no reason" is waiting on memory.

### understanding the concept

the CPU does not read bytes from RAM; it reads cache lines (64 bytes on most x86-64 and many ARM cores, 128 on some designs) through a hierarchy of caches. the numbers below are rough orders of magnitude only. they vary considerably across CPU generations and vendors, so treat them as a sense of scale, not as constants:

| level | typical size | rough latency |
|---|---|---|
| registers | a few hundred bytes | effectively zero |
| L1 data cache | 32 to 128 KiB per core | about 1 ns (a handful of cycles) |
| L2 | 256 KiB to a few MiB | a few ns |
| L3 (shared) | several to tens of MiB | around 10 to 20 ns |
| DRAM | GiB | around 50 to 100+ ns |

three mechanisms explain most of what you will observe:

- **spatial locality**: once a line is loaded, its other 63 bytes are nearly free. code that uses every byte it fetches gets the most out of each miss.
- **prefetching**: hardware prefetchers detect sequential and constant-stride access and fetch lines before you ask. they cannot predict where a pointer points.
- **memory-level parallelism**: a modern core can have many misses in flight at once, if it knows the addresses. in a linked list, the next address is inside the node you are still waiting for, so misses serialize: each one pays the full latency.

### in code

three traversals, identical arithmetic:

```cpp complete
#include <list>
#include <memory>
#include <vector>

struct Point { float x, y, z; };

float sum_x(const std::vector<Point>& pts) {                   // contiguous, sequential
    float s = 0; for (const Point& p : pts) s += p.x; return s;
}
float sum_x(const std::vector<std::unique_ptr<Point>>& pts) {  // one indirection each
    float s = 0; for (const auto& p : pts) s += p->x; return s;
}
float sum_x(const std::list<Point>& pts) {                     // dependent pointer chase
    float s = 0; for (const Point& p : pts) s += p.x; return s;
}
```

the vector is the friendly case: sequential lines, prefetcher engaged. the vector of `unique_ptr` stores pointers contiguously but the pointees go wherever the allocator put them. in a fresh benchmark process they are often allocated back to back, so it looks fine; after hours of allocation churn they scatter, and the benchmark flattered the design ([[benchmarking]]'s warning about laboratory conditions). the list adds a dependency chain on top of the scatter.

### in practice

claims about memory behavior should be checked against the hardware's own counters, not inferred from timings alone:

```sh
perf stat -e cycles,instructions,cache-references,cache-misses,L1-dcache-load-misses ./localizer_replay run.bag
```

available event names vary by CPU (`perf list` shows yours). the useful readings are relative: a layout change that halves cache misses *and* reduces cycles per frame was memory-bound and worth it; one that halves misses with no change in cycles means memory was not the bottleneck, and the change probably is not worth its complexity. instructions per cycle (`instructions` divided by `cycles`) is a quick tell: a loop that retires far less than one instruction per cycle is usually waiting on memory.

### watch out for

**false sharing: two threads, one cache line.** cache coherence works per line, not per variable, so threads that write *different* variables on the *same* line still contend:

```cpp
#include <vector>

struct PaddedSum { alignas(64) double value = 0; };   // one cache line per thread
std::vector<PaddedSum> partial(num_threads);           // C++17 vector honors over-alignment
```

without the padding, adjacent `double` accumulators for different threads share a line, and every write by one core invalidates it in the others' caches, so logically independent threads slow each other down. the 64 is a common line size, not a guarantee; [[atomic-waiting]] discusses `std::hardware_destructive_interference_size` and its portability caveats.

### the takeaway

performance is often decided by which bytes travel from memory, in what order, and which cores fight over them; contiguous, sequential, unshared access is the fast path.

### optional challenge

a traversal of a `std::list` with a million nodes takes far longer than the extra cache misses alone would suggest, compared with a vector of the same elements. what mechanism makes it worse than "one miss per node"?

<details>
<summary>answer</summary>

the misses cannot overlap. a core can have many cache misses in flight at once, but only when it knows the addresses; in a list, the address of the next node is stored inside the current node, which is itself still being loaded. each miss must complete before the next one can even start, so the traversal pays the full memory latency per node, back to back. a vector of pointers has the same scatter but the pointers themselves are contiguous, so the core can request several pointees concurrently; a plain vector has neither problem.

</details>
