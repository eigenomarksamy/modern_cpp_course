---
title: data-oriented design: arrays of structs and structs of arrays
standard: C++17
objective: choose between array-of-structs, struct-of-arrays, and hot/cold splitting by the access pattern of the hot loops, and keep the choice encapsulated
prerequisites: cache-locality
difficulty: 2
---

### the idea

object-oriented design starts from "what is a detection?" and packs everything a detection has into one struct. a loop that only checks each detection's signal-to-noise ratio then drags sixty unrelated bytes through the cache for every four it uses. data-oriented design starts from the other end: which loops are hot, which bytes do they read, and in what order? the layout follows from the answers, and so do its costs.

### understanding the concept

data-oriented design takes these mechanisms as the starting point. instead of asking "what is a detection?" you ask "which bytes does this loop read, how many times, in what order?" and lay the data out to match.

the two classic layouts are an *array of structs* (AoS), where each element's fields are adjacent, and a *struct of arrays* (SoA), where each field is its own contiguous array. AoS is ideal when a loop uses most fields of one element at a time; SoA is ideal when a loop uses one or two fields of every element. most real systems end up in between.

### in code

now a radar detection, laid out as an array of structs (AoS):

```cpp complete
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

every iteration pulls in a whole line to use one `float`. the struct of arrays (SoA) version stores each field contiguously:

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

the gating loop now moves one sixteenth of the bytes, and its body is a uniform operation over contiguous floats, which is exactly the shape compilers auto-vectorize most readily. whether that turns into a large speedup depends on whether the AoS loop was memory-bound to begin with: for a few hundred detections that fit in L1, the difference may be noise. for hundreds of thousands per frame, it usually is not.

a middle ground is **hot/cold splitting**: keep the fields every loop touches in one compact struct (here `range`, `azimuth`, `doppler`, `snr`, `track_id`, `flags`: 24 bytes) and move the rarely read ones (timestamp, sensor name) into a parallel array indexed the same way. you keep most of the AoS ergonomics and stop paying for bytes you never read.

### in practice

a robot localizer runs a particle filter with tens of thousands of particles. each cycle has three phases: predict (update every pose from odometry), weight (score every pose against the latest scan), and resample (cumulative sum over weights, then copy chosen poses). originally each `Particle` was a class with pose, weight, a history buffer for debugging, and virtual methods, held in a `std::vector<std::unique_ptr<Particle>>`.

the data-oriented rewrite stored `x`, `y`, `theta`, and `weight` as four float arrays inside a `ParticleSet` class, moved the debug history into a separate structure that is only filled when diagnostics are enabled, and replaced the virtual methods with whole-set operations (`predict`, `normalize_weights`, `resample`) that loop over the arrays. each step was justified with numbers: the benchmark harness from [[benchmarking]] on a recorded dataset for time per cycle, and hardware counters for the mechanism.

note the design move: the SoA arrays are private to `ParticleSet`, which guarantees they always have equal length and exposes whole-set operations (`predict`, `normalize_weights`). encapsulation moved from the element to the collection; it did not disappear.

### watch out for

SoA is a tradeoff, not an upgrade. code that accesses all fields of one element at a time (a tracker associating one detection, a lookup by index) touches one line in AoS and several lines in SoA. every new field touches several places. sorting means permuting every array, or sorting an index array instead. element identity becomes "an index", which invalidates as easily as an iterator ([[sequence-containers]]). and the readability cost is real: `particles.x[i]` reads worse than `particle.x`.

choose layout from the dominant access pattern of the hot loops, keep it behind an interface so the choice can change, and verify with counters that memory was the bottleneck before paying the complexity.

### the takeaway

performance is often decided by which bytes travel from memory and in what order; lay out data for the loops that run hottest, and keep that layout encapsulated so it stays a decision rather than an accident.

### optional challenge

on a typical 64-bit ABI, `struct Particle { bool active; double x, y, z; bool dirty; };` is 40 bytes. why, what is the smallest you can make it by reordering, and what would you do instead if the hot loop only checks `active` and skips most particles?

<details>
<summary>answer</summary>

each `double` needs 8-byte alignment, so `active` is followed by 7 bytes of padding, and `dirty` is followed by 7 more so that the size is a multiple of the alignment (arrays must keep every element aligned): 1 + 7 + 24 + 1 + 7 = 40. putting the doubles first and the two `bool`s together gives 24 + 2 = 26, rounded up to 32 bytes, so exactly two particles per 64-byte line instead of 1.6. padding is implementation-defined in general, but these numbers hold on the common x86-64 and AArch64 ABIs.

if the hot loop only needs `active` and most particles are inactive, layout tweaks are the wrong tool: the loop still visits every particle. keep the active ones compacted at the front of the arrays (swap-remove on deactivation), or keep a separate dense list of active indices, so the loop never touches inactive particles at all. doing less work beats doing the same work with fewer misses.

</details>
