<a id="day-51"></a>

## day 51: cache locality and data-oriented design

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 15, 40, 50

### the idea

Two loops do the same arithmetic over the same number of elements, both O(n), and one runs several times slower than the other. Nothing in the source explains it, because the difference is not in the instructions: it is in where the bytes live. Most code that is "slow for no reason" is waiting on memory.

### understanding the concept

The CPU does not read bytes from RAM; it reads cache lines (64 bytes on most x86-64 and many ARM cores, 128 on some designs) through a hierarchy of caches. The numbers below are rough orders of magnitude only. They vary considerably across CPU generations and vendors, so treat them as a sense of scale, not as constants:

| level | typical size | rough latency |
|---|---|---|
| registers | a few hundred bytes | effectively zero |
| L1 data cache | 32 to 128 KiB per core | about 1 ns (a handful of cycles) |
| L2 | 256 KiB to a few MiB | a few ns |
| L3 (shared) | several to tens of MiB | around 10 to 20 ns |
| DRAM | GiB | around 50 to 100+ ns |

Three mechanisms explain most of what you will observe:

- **spatial locality**: once a line is loaded, its other 63 bytes are nearly free. Code that uses every byte it fetches gets the most out of each miss.
- **prefetching**: hardware prefetchers detect sequential and constant-stride access and fetch lines before you ask. They cannot predict where a pointer points.
- **memory-level parallelism**: a modern core can have many misses in flight at once, if it knows the addresses. In a linked list, the next address is inside the node you are still waiting for, so misses serialize: each one pays the full latency.

Data-oriented design takes these mechanisms as the starting point. Instead of asking "what is a detection?" you ask "which bytes does this loop read, how many times, in what order?" and lay the data out to match.

### in code

Three traversals, identical arithmetic:

```cpp
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

The vector is the friendly case: sequential lines, prefetcher engaged. The vector of `unique_ptr` stores pointers contiguously but the pointees go wherever the allocator put them. In a fresh benchmark process they are often allocated back to back, so it looks fine; after hours of allocation churn they scatter, and the benchmark flattered the design (day 50's warning about laboratory conditions). The list adds a dependency chain on top of the scatter.

Now a radar detection, laid out as an array of structs (AoS):

```cpp
#include <cstddef>
#include <cstdint>
#include <vector>

struct Detection {                                    // AoS: 64 bytes on common 64-bit ABIs
    float range_m, azimuth_rad, doppler_mps, snr_db;  // 16
    std::uint64_t timestamp_ns;                       //  8
    std::uint32_t track_id, flags;                    //  8
    char source[32];                                  // 32: sensor name, rarely read
};

std::size_t count_strong(const std::vector<Detection>& ds, float min_snr) {
    std::size_t n = 0;
    for (const Detection& d : ds) n += d.snr_db >= min_snr;  // 4 useful bytes per 64 fetched
    return n;
}
```

Every iteration pulls in a whole line to use one `float`. The struct of arrays (SoA) version stores each field contiguously:

```cpp
#include <array>

struct Detections {                                   // SoA: one array per field
    std::vector<float> range_m, azimuth_rad, doppler_mps, snr_db;
    std::vector<std::uint64_t> timestamp_ns;
    std::vector<std::uint32_t> track_id, flags;
    std::vector<std::array<char, 32>> source;
};

std::size_t count_strong(const Detections& ds, float min_snr) {
    std::size_t n = 0;
    for (float snr : ds.snr_db) n += snr >= min_snr;  // 16 useful floats per line
    return n;
}
```

The gating loop now moves one sixteenth of the bytes, and its body is a uniform operation over contiguous floats, which is exactly the shape compilers auto-vectorize most readily. Whether that turns into a large speedup depends on whether the AoS loop was memory-bound to begin with: for a few hundred detections that fit in L1, the difference may be noise. For hundreds of thousands per frame, it usually is not.

A middle ground is **hot/cold splitting**: keep the fields every loop touches in one compact struct (here `range`, `azimuth`, `doppler`, `snr`, `track_id`, `flags`: 24 bytes) and move the rarely read ones (timestamp, sensor name) into a parallel array indexed the same way. You keep most of the AoS ergonomics and stop paying for bytes you never read.

### in practice

A robot localizer runs a particle filter with tens of thousands of particles. Each cycle has three phases: predict (update every pose from odometry), weight (score every pose against the latest scan), and resample (cumulative sum over weights, then copy chosen poses). Originally each `Particle` was a class with pose, weight, a history buffer for debugging, and virtual methods, held in a `std::vector<std::unique_ptr<Particle>>`.

The data-oriented rewrite stored `x`, `y`, `theta`, and `weight` as four float arrays inside a `ParticleSet` class, moved the debug history into a separate structure that is only filled when diagnostics are enabled, and split the weighting phase across threads with per-thread partial sums. Those partial sums sat in an array of adjacent `double`s, which put several threads' accumulators on one cache line: false sharing (day 40). Padding each accumulator to its own line fixed it:

```cpp
struct alignas(64) PaddedSum { double value = 0; };  // one cache line per thread
std::vector<PaddedSum> partial(num_threads);          // C++17 vector honours over-alignment
```

(`std::hardware_destructive_interference_size` from `<new>` is the portable spelling of the 64, where your standard library provides it.)

Each step was justified with numbers, not intuition: the day 50 harness on a recorded dataset for time per cycle, and hardware counters for the mechanism, for example `perf stat -e cache-references,cache-misses,L1-dcache-load-misses ./localizer_replay run.bag`. Available event names vary by CPU; `perf list` shows yours. A drop in misses with no change in cycle time means memory was not the bottleneck, and the change probably is not worth its cost.

Note the design move: the SoA arrays are private to `ParticleSet`, which guarantees they always have equal length and exposes whole-set operations (`predict`, `normalize_weights`). Encapsulation moved from the element to the collection; it did not disappear.

### watch out for

SoA is a tradeoff, not an upgrade. Code that accesses all fields of one element at a time (a tracker associating one detection, a lookup by index) touches one line in AoS and several lines in SoA. Every new field touches several places. Sorting means permuting every array, or sorting an index array instead. Element identity becomes "an index", which invalidates as easily as an iterator (day 15). And the readability cost is real: `particles.x[i]` reads worse than `particle.x`.

Choose layout from the dominant access pattern of the hot loops, keep it behind an interface so the choice can change, and verify with counters that memory was the bottleneck before paying the complexity.

### the takeaway

Performance is often decided by which bytes travel from memory and in what order; lay out data for the loops that run hottest, and keep that layout encapsulated so it stays a decision rather than an accident.

### optional challenge

On a typical 64-bit ABI, `struct Particle { bool active; double x, y, z; bool dirty; };` is 40 bytes. Why, what is the smallest you can make it by reordering, and what would you do instead if the hot loop only checks `active` and skips most particles?

<details>
<summary>answer</summary>

Each `double` needs 8-byte alignment, so `active` is followed by 7 bytes of padding, and `dirty` is followed by 7 more so that the size is a multiple of the alignment (arrays must keep every element aligned): 1 + 7 + 24 + 1 + 7 = 40. Putting the doubles first and the two `bool`s together gives 24 + 2 = 26, rounded up to 32 bytes, so exactly two particles per 64-byte line instead of 1.6. Padding is implementation-defined in general, but these numbers hold on the common x86-64 and AArch64 ABIs.

If the hot loop only needs `active` and most particles are inactive, layout tweaks are the wrong tool: the loop still visits every particle. Keep the active ones compacted at the front of the arrays (swap-remove on deactivation), or keep a separate dense list of active indices, so the loop never touches inactive particles at all. Doing less work beats doing the same work with fewer misses.

</details>
