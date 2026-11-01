---
title: arenas and pools with `std::pmr`
standard: C++17
objective: use `std::pmr` memory resources for scoped arena allocation and pooling, and avoid their propagation and lifetime traps
prerequisites: allocation-costs
difficulty: 3
---

### the idea

some allocations cannot simply be moved to startup: per-frame temporaries whose size depends on the data, tracks that are born and die while the system runs. for those, the problem is not that allocation happens but that the general-purpose heap is the wrong allocator for the pattern. a frame's temporaries all die together at the end of the frame; a pool's objects all have the same size. C++17's `std::pmr` lets a container use an allocator that matches the pattern without changing the container's type to a template parameter soup.

### understanding the concept

second, `std::pmr` (C++17). a `memory_resource` is a runtime-polymorphic allocator, and the `std::pmr::` containers hold a pointer to one. `monotonic_buffer_resource` is a bump allocator: allocation advances a pointer, deallocation is a no-op, and everything is released at once when the resource dies.

the standard resources cover the common patterns: `monotonic_buffer_resource` for "allocate during a phase, free everything at its end"; `unsynchronized_pool_resource` and `synchronized_pool_resource` for many allocations of a few sizes; `new_delete_resource()` for the ordinary heap; and `null_memory_resource()`, which always throws, as a guard against silently falling back. resources chain: each takes an *upstream* resource to get more memory from when its own runs out.

### in code

```cpp complete
#include <array>
#include <cstddef>
#include <memory_resource>
#include <vector>

struct Detection { float range_m, azimuth_rad, snr_db; };

std::size_t process_frame(const std::vector<Detection>& raw) {
    alignas(std::max_align_t) std::array<std::byte, 16 * 1024> buffer;   // scratch on the stack
    std::pmr::monotonic_buffer_resource arena(buffer.data(), buffer.size(),
                                              std::pmr::null_memory_resource());
    std::pmr::vector<Detection> gated(&arena);
    gated.reserve(raw.size());                   // a pointer bump, no heap
    for (const Detection& d : raw)
        if (d.snr_db > 10.0f) gated.push_back(d);
    return gated.size();
}                                                // everything released at once
```

the `null_memory_resource()` upstream is a deliberate choice: if a frame ever needs more than 16 KiB, allocation throws `std::bad_alloc` instead of silently falling back to the heap. in a test, that is a loud failure you want; in production you might prefer the default upstream plus a metric. note `reserve`: with a monotonic resource, a growing vector leaves every outgrown buffer behind as dead space until the arena is released.

### in practice

object pools fill the remaining gap: when objects of one type are created and destroyed at runtime (tracks born and dying), a fixed-capacity pool with a free list gives O(1) allocation with no system calls. `std::pmr::unsynchronized_pool_resource` is a general-purpose version for single-threaded use; `synchronized_pool_resource` adds locking.

per-frame arenas fit naturally into a processing loop: create one `monotonic_buffer_resource` per frame over a buffer that is reused across frames, pass it to the frame's temporary containers, and let it be destroyed (or `release()`d) at the frame boundary. combined with the allocation counter from [[allocation-costs]], that turns "this stage does not touch the heap" into a property a test can check.

### watch out for

`pmr` propagation surprises people. a pmr container does not propagate its resource on copy: `std::pmr::vector<int> copy = a;` gets the default resource (normally the heap), not `a`'s arena. moving keeps the resource, but move-assigning between containers with different resources copies element by element. uses-allocator construction passes the resource down only to elements that accept one: `pmr::vector<pmr::string>` puts the strings in the arena, `pmr::vector<std::string>` does not. and the resource must outlive every container using it; a container whose arena has been destroyed holds dangling memory, and touching it is undefined behavior.

### the takeaway

match the allocator to the allocation pattern: a monotonic arena for data that dies together, a pool for objects of one size, and a null upstream wherever silently falling back to the heap would be a bug.

### optional challenge

`std::pmr::vector<std::pmr::string> names(&arena); names.push_back("front_left_radar_long_name");` how many allocations come from the arena, and what changes if the element type is `std::string`?

<details>
<summary>answer</summary>

with `pmr::string` elements, uses-allocator construction gives the new string the vector's resource, so both the vector's buffer and the string's heap buffer (the name is longer than the small-string buffer) come from the arena. one subtlety: `push_back` first constructs a temporary `pmr::string` from the literal using the default resource, then moves it into the vector; because the resources differ, the move copies into arena memory, so the temporary's allocation hits the heap. `emplace_back("...")` constructs in place with the arena and avoids that. with `std::string` elements, only the vector's buffer is in the arena; every long string allocates from the global heap, defeating the point of the arena.

</details>
