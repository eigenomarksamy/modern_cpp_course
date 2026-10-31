<a id="day-56"></a>

## day 56: week 8 review and the road ahead

**reading time:** about 10 minutes · **standard:** C++20 · **builds on:** days 50 to 55

### recap

| day | key idea |
|---|---|
| [50](#day-50) | Profile to find where time goes, benchmark to compare alternatives; defeat dead-code elimination, warm up, repeat, report median and spread; Amdahl bounds the payoff. |
| [51](#day-51) | Memory moves in cache lines; contiguous, predictable access wins; AoS versus SoA and hot/cold splitting are layout choices driven by the hottest loops. |
| [52](#day-52) | Allocation has an unbounded tail; count it, `reserve` and reuse, use `std::pmr` arenas, and test that the steady state never touches the heap. |
| [53](#day-53) | Deterministic tests through injected seams; sanitizers and fuzzing in CI; structured logs, lock-free metrics, and RAII spans that are safe in hot paths. |
| [54](#day-54) | Characterization tests first, then small verified steps; shims and `[[deprecated]]` for migration; architecture decisions written down with their costs. |
| [55](#day-55) | One program where ownership, borrowing, seams, concurrency, and shutdown order all have to agree. |

### review questions

**This week**

1. A microbenchmark says your new hash function is 25 percent faster, but the end-to-end frame time does not move. Give two distinct explanations and how you would tell them apart.
2. After converting detections from AoS to SoA, the SNR gating loop got faster but the per-detection association step got slower. Why is that plausible?
3. `std::pmr::vector<int> copy = arena_vec;` quietly puts `copy` on the heap. Why, and how do you keep it in the arena?
4. In day 55's pipeline, the consumer registers a `std::stop_callback` that closes the queue. Why not simply check `st.stop_requested()` in the loop?
5. Your characterization test asserts a behavior you are fairly sure is a bug. Why keep it during the refactor?

**Spaced repetition across the course**

6. *From week 1:* classify each as undefined, unspecified, or implementation-defined: `sizeof(long)`; the order in which `a()` and `b()` run in `f(a(), b())`; `INT_MAX + 1` for `int`.
7. *From week 2:* why does `std::vector<T>` copy rather than move elements during reallocation when `T`'s move constructor is not `noexcept`?
8. *From week 3:* `const Track& t = tracks.front(); tracks.push_back(next);` Is `t` still usable?
9. *From week 4:* what is wrong with `std::string_view sv = std::string("radar") + "_0";` followed by any use of `sv`?
10. *From week 5:* why can you not iterate a `const std::ranges::filter_view`?
11. *From week 6:* a producer writes a non-atomic payload and then sets an atomic `ready` flag with `memory_order_relaxed`; the consumer spins on `ready` with relaxed loads, then reads the payload. What is the bug?
12. *From week 7:* with pimpl and `std::unique_ptr<Impl>`, why must the destructor be declared in the header and defined in the `.cpp`?

### mini exercise

Extend the day 55 pipeline so that the time each sink call takes is recorded in day 53's `LatencyHistogram`, without editing `Pipeline`, `Processor`, or `RecordingSink`. Decide which seam the feature belongs behind, and name one thing your choice cannot measure.

### answers

<details>
<summary>1. faster microbenchmark, unchanged frame time</summary>

Either the hash is a small share of the frame (Amdahl: 25 percent of 2 percent is invisible), or the microbenchmark's conditions (hot cache, one key pattern, no contention) do not hold in the pipeline. A profile of the real workload distinguishes them: if the hash's share is tiny, it is the first; if the share is large but did not shrink, it is the second.

</details>

<details>
<summary>2. SoA helps one loop and hurts another</summary>

Gating reads one field across many detections, so SoA packs 16 useful floats per line. Association reads all fields of one detection at a time, which in SoA touches a different line per field instead of one line. Layout should follow the dominant access pattern; sometimes a hot/cold split serves both.

</details>

<details>
<summary>3. pmr copy on the heap</summary>

Copy construction asks `select_on_container_copy_construction`, which for `polymorphic_allocator` returns a default-constructed allocator, meaning the default resource. Use the allocator-extended constructor: `std::pmr::vector<int> copy(arena_vec, &arena);`.

</details>

<details>
<summary>4. why the stop callback closes the queue</summary>

A consumer blocked inside `pop()` is waiting on a condition variable and never reaches the loop condition, so checking the token would not wake it. Closing the queue wakes it, lets it drain, and makes `pop()` return `nullopt`. (A `std::condition_variable_any` wait that takes the stop token is the other C++20 option.)

</details>

<details>
<summary>5. keeping a test for a bug</summary>

The refactor must not change behavior; if it fixes the bug in passing, you cannot tell intended change from accident, and someone may depend on the old behavior. Keep the test green through the refactor, then change the behavior in its own commit and update the test deliberately.

</details>

<details>
<summary>6. from week 1</summary>

`sizeof(long)`: implementation-defined (documented by the implementation). Argument order: unspecified (since C++17 the two calls are indeterminately sequenced, never interleaved). `INT_MAX + 1`: undefined behavior, and the optimizer may assume it never happens.

</details>

<details>
<summary>7. from week 2</summary>

Reallocation offers the strong guarantee. If a move could throw halfway, the old buffer would already be partly moved from and could not be restored. `std::move_if_noexcept` therefore copies when the move is not `noexcept` and a copy constructor exists.

</details>

<details>
<summary>8. from week 3</summary>

Only if no reallocation happened. If `size() == capacity()` before the `push_back`, the elements move to a new buffer, every reference is invalidated, and using `t` is undefined behavior. Copy the value, keep an index, or `reserve` first.

</details>

<details>
<summary>9. from week 4</summary>

The concatenation produces a temporary `std::string` that is destroyed at the end of the full-expression. `sv` points into freed memory, so any read is undefined behavior. A view never extends a lifetime.

</details>

<details>
<summary>10. from week 5</summary>

`filter_view::begin()` caches the first matching position so that repeated calls are amortized O(1). Caching mutates the view, so `begin()` is non-const. Take the view by value or by non-const reference.

</details>

<details>
<summary>11. from week 6</summary>

Relaxed operations create no synchronizes-with edge, so seeing `ready == true` does not make the payload write visible. The payload accesses are an unordered conflicting pair: a data race, which is undefined behavior. Use `release` on the store and `acquire` on the load.

</details>

<details>
<summary>12. from week 7</summary>

`std::unique_ptr<Impl>`'s deleter needs a complete `Impl` where the destructor is instantiated. An implicit destructor is inline in the header, where `Impl` is incomplete, so it fails to compile (libstdc++ reports "invalid application of `sizeof` to incomplete type"). Declare `~Widget();` in the header and define it as `= default` in the `.cpp` after `Impl`; the same applies to the move operations.

</details>

<details>
<summary>mini exercise</summary>

The sink concept is already a seam, so the feature fits behind it as a decorator that satisfies `DetectionSink` by forwarding:

```cpp
template <DetectionSink Inner>
class TimingSink {                         // same concept in, same concept out
public:
    TimingSink(Inner& inner, LatencyHistogram& h) : inner_(inner), h_(h) {}
    void on_frame(std::uint64_t seq, std::span<const Detection> ds) {
        ScopeTimer span(h_);               // day 53
        inner_.on_frame(seq, ds);
    }
    void on_fault(std::uint64_t seq, int code) { inner_.on_fault(seq, code); }
private:
    Inner& inner_;
    LatencyHistogram& h_;
};

// RecordingSink recorder; LatencyHistogram h; TimingSink timed(recorder, h);
// Pipeline pipeline(GateConfig{}, timed, fake_sensor);   // Pipeline is unchanged
```

No existing class changes (open/closed, day 43), and the decorator inlines because the seam is compile-time. What it cannot measure: time spent in `gate`, and end-to-end latency from sensor to sink. The first needs timing inside `Processor`; the second needs a capture timestamp in `Frame`, a change to the message type itself. Features that change what the data means belong in the types; features that observe it belong behind seams.

</details>

### connections

Week 8 leaned on everything before it. Benchmarking and cache behavior gave substance to the container choices of day 15 and the false sharing of day 40. The cost of allocation explained why the rule of zero (day 11), `reserve` (day 15), and the hidden costs of `std::function` (day 17) and `shared_ptr` (day 12) matter in practice. Testing and observability turned dependency injection (day 44), RAII (day 08), and `std::source_location` (day 34) into everyday tools, and the sanitizers of day 06 into CI jobs. Legacy refactoring was week 4's C++17 vocabulary applied at scale, and day 55 needed something from every week: value semantics, variants, concepts, spans, views, `jthread`, a condition-variable queue, and member order as a shutdown protocol.

#### where to go next

You now have the core of modern C++17 and C++20 and, more importantly, the habit of asking what each feature costs and what it promises. C++23 is the natural next step, and most of it builds directly on this course:

- `std::expected<T, E>`: the result type days 20 and 25 approximated with variants, now standard.
- `std::print` and `std::println`: `std::format` (day 34) straight to output.
- deducing `this`: explicit object parameters that simplify CRTP (day 46) and remove const/non-const duplication.
- `std::generator`: the coroutine generator you wrote by hand on day 48, ready-made.
- `std::mdspan`: multidimensional views over contiguous memory, `std::span` (day 31) for matrices and images.
- `std::flat_map` and `std::flat_set`: sorted-vector associative containers, day 15's locality argument as a library type.

Further out, the C++26 feature set includes language contracts (preconditions and postconditions as declarations, the formal version of day 47's API contracts) and static reflection, which lets code inspect types at compile time and will reshape serialization and boilerplate generation. Treat both as directions to watch; check your compiler's status pages before relying on them.

The most effective practice from here is unglamorous: read compiler output on Compiler Explorer when you wonder what something costs, run your tests under sanitizers, measure before you optimize, and write down the tradeoffs you choose. The language will keep growing; the judgment you built over these eight weeks is what makes each new feature easy to place. Thanks for reading, and enjoy the code you write next.
