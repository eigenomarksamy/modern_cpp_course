---
title: putting it together, part 2: the processing stage
standard: C++20
objective: build a pure, allocation-free processing stage over borrowed data, and constrain an injected sink with a concept
prerequisites: pipeline-design, span, views, test-seams
difficulty: 2
---

### the idea

the processing stage is where the pipeline does its actual work: gate each frame's detections and hand the result on. it is also where the most design decisions concentrate. what does it borrow and what does it own? does it allocate every frame? how does it talk to a sink it must not know the type of, and how does a test replace that sink? the answers come straight from earlier modules.

### understanding the concept

the stage is split in two. `gate` is a pure function: it reads a span of detections, writes the survivors into a caller-provided vector, and touches nothing else, so it can be tested without threads or fakes. `Processor` adapts `gate` to the message variant and owns the only mutable state, a scratch vector reused every frame. the sink is a template parameter constrained by a concept, which states exactly what any sink must provide and catches a wrong sink where the pipeline is created.

### in code

part 3 is the actual work. `gate` is a pure function over a borrowed span; `Processor` adapts it to messages and is constrained on what a sink must provide.

```cpp group=pipeline
// part 3: the processing stage
struct GateConfig { double min_snr_db = 10.0; double max_range_m = 200.0; };

// Pure, and allocation-free once `out` has enough capacity.
void gate(std::span<const Detection> in, const GateConfig& cfg, std::vector<Detection>& out) {
    auto keep = [&](const Detection& d) {
        return d.snr_db >= cfg.min_snr_db && d.range_m <= cfg.max_range_m;
    };
    out.clear();
    for (const Detection& d : in | std::views::filter(keep)) out.push_back(d);
    std::ranges::sort(out, std::ranges::greater{}, &Detection::snr_db);   // strongest first
}

template <typename S>
concept DetectionSink = requires(S& s, std::uint64_t seq, std::span<const Detection> ds, int code) {
    s.on_frame(seq, ds);       // ds is borrowed: valid only during the call
    s.on_fault(seq, code);
};

template <DetectionSink Sink>
class Processor {
public:
    Processor(GateConfig cfg, Sink& sink) : cfg_(cfg), sink_(sink) {}
    void operator()(const Message& msg) {
        std::visit(overloaded{
            [&](const Frame& f) { gate(f.detections, cfg_, scratch_); sink_.on_frame(f.seq, scratch_); },
            [&](const SensorFault& e) { sink_.on_fault(e.seq, e.code); },
        }, msg);
    }
private:
    GateConfig cfg_;
    Sink& sink_;
    std::vector<Detection> scratch_;         // reused every frame
};
```

### in practice

the design review for part 3:

| decision | alternative | why this one |
|---|---|---|
| `gate` is a free function on `std::span` | member function taking `std::vector` | pure and testable without threads; any contiguous owner works ([[span]]) |
| `scratch_` reused every frame | return a fresh vector | no steady-state allocation ([[allocation-costs]]); the cost is that `Processor` is stateful and not reentrant |
| sink: template constrained by a concept | virtual interface, or `std::function` | the per-frame call can inline, and a wrong sink fails to compile where the pipeline is created, naming the unmet requirement ([[concepts]], [[test-seams]]); the cost is that `Pipeline` is a template |
| `views::filter` feeding a loop | `std::copy_if` | equally good; C++20 has no `ranges::to` (that is C++23), so materializing is explicit either way ([[views]]) |

### watch out for

**the sink receives a borrowed span.** `on_frame` gets a view of `scratch_`, which the next frame overwrites. a sink that stored the span instead of copying the data would read garbage later. that is the lifetime rule from [[string-view]] and [[span]], and here it is enforced only by a comment in the concept. a sink that needs to keep data must copy it, which the recording sink in part 4 does.

### the takeaway

make the core computation a pure function over borrowed data, keep the stage's mutable state small and reused, and constrain injected collaborators with a concept so mistakes surface where the parts are put together.

### optional challenge

`Processor` reuses `scratch_` across frames. what would you lose, and what would you gain, by making `gate` return a fresh `std::vector<Detection>` instead?

<details>
<summary>answer</summary>

you would gain a simpler interface (no output parameter), a `Processor` with no mutable state, and a sink that could keep the vector it receives by moving it. you would lose the allocation-free steady state: every frame would allocate at least once, which matters in a real-time pipeline ([[allocation-costs]]) and does not in a tool that runs once. the output parameter is the price of reuse; choose it deliberately, and measure whether the allocation matters before paying it.

</details>
