---
title: review: production engineering, and the road ahead
kind: review
standard: C++20
objective: consolidate testing, observability, legacy refactoring, architectural decisions, and the integrated pipeline, with spaced repetition across the course
prerequisites: testing, observability, legacy-refactoring, architecture-decisions, pipeline-design, pipeline-processing, pipeline-wiring
difficulty: 2
---

### recap

| lesson | key idea |
|---|---|
| [[testing]] | push checks down the pyramid, test behavior, inject time and I/O, and let sanitizers and fuzzers explore. |
| [[observability]] | structured logs, cheap metrics, and spans, built so that observing does not disturb. |
| [[legacy-refactoring]] | characterization tests first, then small verified steps behind a compatibility shim. |
| [[architecture-decisions]] | replace subsystems incrementally and record tradeoffs where the next engineer will look. |
| [[pipeline-design]] to [[pipeline-wiring]] | one small program where ownership, borrowing, seams, and shutdown order all have to agree. |

### review questions

1. in [[pipeline-wiring]]'s pipeline, the consumer registers a `std::stop_callback` that closes the queue. why not simply check `st.stop_requested()` in the loop?
2. your characterization test asserts a behavior you are fairly sure is a bug. why keep it during the refactor?
3. a log line inside a 1 kHz control loop formats a string and writes to a file. name two ways it can cause the deadline misses it was added to investigate.
4. from [[undefined-behavior]]: classify each as undefined, unspecified, or implementation-defined: `sizeof(long)`; the order in which `a()` and `b()` run in `f(a(), b())`; `INT_MAX + 1` for `int`.
5. from [[noexcept-moves]]: why does `std::vector<T>` copy rather than move elements during reallocation when `T`'s move constructor is not `noexcept`?
6. from [[string-view]]: what is wrong with `std::string_view sv = std::string("radar") + "_0";` followed by any use of `sv`?
7. from [[memory-model]]: a producer writes a non-atomic payload and then sets an atomic `ready` flag with `memory_order_relaxed`; the consumer spins on `ready` with relaxed loads, then reads the payload. what is the bug?
8. from [[api-stability]]: with pimpl and `std::unique_ptr<Impl>`, why must the destructor be declared in the header and defined in the `.cpp`?

### mini exercise

extend the [[pipeline-wiring]] pipeline so that the time each sink call takes is recorded in [[observability]]'s `LatencyHistogram`, without editing `Pipeline`, `Processor`, or `RecordingSink`. decide which seam the feature belongs behind, and name one thing your choice cannot measure.

### answers

<details>
<summary>answer 1: why the stop callback closes the queue</summary>

a consumer blocked inside `pop()` is waiting on a condition variable and never reaches the loop condition, so checking the token would not wake it. closing the queue wakes it, lets it drain, and makes `pop()` return `nullopt`. (a `std::condition_variable_any` wait that takes the stop token is the other C++20 option.)

</details>

<details>
<summary>answer 2: keeping a test for a bug</summary>

the refactor must not change behavior; if it fixes the bug in passing, you cannot tell intended change from accident, and someone may depend on the old behavior. keep the test green through the refactor, then change the behavior in its own commit and update the test deliberately.

</details>

<details>
<summary>answer 3: observability that disturbs</summary>

formatting can allocate, and the general-purpose heap has an unbounded worst case; writing to a file can block on I/O, and logging libraries often take a lock that another thread may hold. any of these turns a diagnostic into the deadline miss. keep the hot path to counters and fixed-size records pushed into a preallocated buffer, and let a background thread format and write them.

</details>

<details>
<summary>answer 4: three kinds of looseness</summary>

`sizeof(long)`: implementation-defined (documented by the implementation). argument order: unspecified (since C++17 the two calls are indeterminately sequenced, never interleaved). `INT_MAX + 1`: undefined behavior, and the optimizer may assume it never happens.

</details>

<details>
<summary>answer 5: noexcept and reallocation</summary>

reallocation offers the strong guarantee. if a move could throw halfway, the old buffer would already be partly moved from and could not be restored. `std::move_if_noexcept` therefore copies when the move is not `noexcept` and a copy constructor exists.

</details>

<details>
<summary>answer 6: a view into a temporary</summary>

the concatenation produces a temporary `std::string` that is destroyed at the end of the full-expression. `sv` points into freed memory, so any read is undefined behavior. a view never extends a lifetime.

</details>

<details>
<summary>answer 7: relaxed is not publication</summary>

relaxed operations create no synchronizes-with edge, so seeing `ready == true` does not make the payload write visible. the payload accesses are an unordered conflicting pair: a data race, which is undefined behavior. use `release` on the store and `acquire` on the load.

</details>

<details>
<summary>answer 8: the pimpl destructor</summary>

`std::unique_ptr<Impl>`'s deleter needs a complete `Impl` where the destructor is instantiated. an implicit destructor is inline in the header, where `Impl` is incomplete, so it fails to compile (libstdc++ reports "invalid application of `sizeof` to incomplete type"). declare `~Widget();` in the header and define it as `= default` in the `.cpp` after `Impl`; the same applies to the move operations.

</details>

<details>
<summary>mini exercise answer</summary>

the sink concept is already a seam, so the feature fits behind it as a decorator that satisfies `DetectionSink` by forwarding:

```cpp
template <DetectionSink Inner>
class TimingSink {                         // same concept in, same concept out
public:
    TimingSink(Inner& inner, LatencyHistogram& h) : inner_(inner), h_(h) {}
    void on_frame(std::uint64_t seq, std::span<const Detection> ds) {
        ScopeTimer span(h_);
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

no existing class changes (open/closed, [[solid]]), and the decorator inlines because the seam is compile-time. what it cannot measure: time spent in `gate`, and end-to-end latency from sensor to sink. the first needs timing inside `Processor`; the second needs a capture timestamp in `Frame`, a change to the message type itself. features that change what the data means belong in the types; features that observe it belong behind seams.

</details>

### connections

the course ends where it started: with what the language promises and what you must promise in return. the production modules leaned on everything before them: benchmarking and cache behavior gave substance to container choices, the cost of allocation explained why the rule of zero, `reserve`, and the hidden costs of `std::function` and `shared_ptr` matter, and testing and observability turned dependency injection and RAII into practical habits. the pipeline showed that the hard part of combining features is deciding who owns what, who may block, and what can be substituted.

#### where to go next

you now have the core of modern C++17 and C++20 and, more importantly, the habit of asking what each feature costs and what it promises. C++23 is the natural next step, and most of it builds directly on this course:

- `std::expected<T, E>`: the result type [[error-strategy]] and [[variant]] approximated with variants, now standard.
- `std::print` and `std::println`: `std::format` ([[format]]) straight to output.
- deducing `this`: explicit object parameters that simplify CRTP ([[static-polymorphism]]) and remove const/non-const duplication.
- `std::generator`: the coroutine generator you wrote by hand on [[coroutine-generator]], ready-made.
- `std::mdspan`: multidimensional views over contiguous memory, `std::span` ([[span]]) for matrices and images.
- `std::flat_map` and `std::flat_set`: sorted-vector associative containers, [[sequence-containers]]'s locality argument as a library type.

further out, the C++26 feature set includes language contracts (preconditions and postconditions as declarations, the formal version of [[api-stability]]'s API contracts) and static reflection, which lets code inspect types at compile time and will reshape serialization and boilerplate generation. treat both as directions to watch; check your compiler's status pages before relying on them.

the most effective practice from here is unglamorous: read compiler output on Compiler Explorer when you wonder what something costs, run your tests under sanitizers, measure before you optimize, and write down the tradeoffs you choose. the language will keep growing; the judgment you built over this course is what makes each new feature easy to place. thanks for reading, and enjoy the code you write next.
