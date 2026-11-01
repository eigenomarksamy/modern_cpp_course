---
title: putting it together, part 3: wiring, shutdown, and testing
standard: C++20
objective: wire the pipeline's threads so every exit path stops and joins them, test it deterministically with fakes, and review the design as a whole
prerequisites: pipeline-processing, jthread, observability
difficulty: 3
---

### the idea

the last part is where most concurrent programs go wrong: starting threads only after everything they use exists, stopping them on every exit path, draining work instead of dropping it, and testing all of it without sleeps or hardware. none of it needs new tools. member declaration order, `std::jthread`, a stop callback, and two small fakes are enough.

### understanding the concept

member order is the shutdown protocol. `Pipeline` declares its source, queue, and processor first and its two threads last, so the threads start after everything they touch is constructed and are stopped and joined before anything they touch is destroyed. `finish()` lets the source run dry, then asks the consumer to stop, which a stop callback turns into closing the queue: the consumer drains what is left and exits. the destructor requests a stop first, so leaving the scope early still shuts down cleanly.

### in code

part 4 wires it together. member order is the shutdown protocol, and `main` doubles as the test.

```cpp group=pipeline
// part 4: wiring, shutdown, and a test run
using Source = std::function<std::optional<Message>()>;   // runtime seam: nullopt = end

template <DetectionSink Sink>
class Pipeline {
public:
    Pipeline(GateConfig cfg, Sink& sink, Source source)
        : source_(std::move(source)), queue_(8), processor_(cfg, sink),
          consumer_([this](std::stop_token st) {
              std::stop_callback on_stop(st, [this] { queue_.close(); });  // stop = close, then drain
              while (auto msg = queue_.pop()) processor_(*msg);
          }),
          producer_([this](std::stop_token st) {
              while (!st.stop_requested()) {
                  auto msg = source_();
                  if (!msg || !queue_.push(std::move(*msg))) return;
              }
          }) {}
    void finish() {                          // let the source run dry, then drain the queue
        if (producer_.joinable()) producer_.join();
        consumer_.request_stop();
        if (consumer_.joinable()) consumer_.join();
    }
    ~Pipeline() { producer_.request_stop(); finish(); }
private:
    Source source_;
    BoundedQueue<Message> queue_;
    Processor<Sink> processor_;
    std::jthread consumer_, producer_;       // last members: stopped and joined first
};

struct RecordingSink {                       // a fake, touched only by the consumer thread
    std::vector<std::pair<std::uint64_t, std::vector<Detection>>> frames;
    std::vector<int> faults;
    void on_frame(std::uint64_t seq, std::span<const Detection> ds) {   // ds is borrowed: copy it
        frames.emplace_back(seq, std::vector<Detection>(ds.begin(), ds.end())); }
    void on_fault(std::uint64_t, int code) { faults.push_back(code); }
};

int main() {
    std::vector<Detection> out;               // unit test of the pure stage: no threads
    const Detection strong{40, 0, 25}, weak{40, 0, 3}, far{900, 0, 40};
    const std::vector<Detection> in{weak, strong, far};
    gate(in, GateConfig{}, out);
    assert(out.size() == 1 && out[0] == strong);

    std::uint64_t seq = 0;                    // a fake sensor: deterministic frames, one fault
    Source fake_sensor = [&seq]() -> std::optional<Message> {
        if (seq == 4) return std::nullopt;
        if (seq == 2) return SensorFault{seq++, 17};
        const double s = static_cast<double>(seq);
        return Frame{seq++, {{50 + s, 0.1, 18}, {250, 0.2, 30}, {80, -0.3, 12 + s}, {120, 0, 6}}};
    };
    RecordingSink sink;
    {
        Pipeline pipeline(GateConfig{}, sink, fake_sensor);
        pipeline.finish();
    }                                         // threads joined: reading the sink is safe
    for (const auto& [n, ds] : sink.frames) {
        std::printf("frame %llu:", static_cast<unsigned long long>(n));
        for (const Detection& d : ds) std::printf("  %.0f m / %.0f dB", d.range_m, d.snr_db);
        std::printf("\n");
    }
    std::printf("faults: %zu (code %d)\n", sink.faults.size(), sink.faults.at(0));
}
```

concatenated in order, the four parts form one translation unit. built with `g++ -std=c++20 -Wall -Wextra -pedantic -O2 -pthread` (GCC 12), it compiles without warnings and prints:

```text
frame 0:  50 m / 18 dB  80 m / 12 dB
frame 1:  51 m / 18 dB  80 m / 13 dB
frame 3:  53 m / 18 dB  80 m / 15 dB
faults: 1 (code 17)
```

the output is deterministic even though two threads are involved: the queue is FIFO and there is one consumer, so the order of messages is fixed by the source.

### in practice

the rest of the design review:

| decision | alternative | why this one |
|---|---|---|
| source: `std::function` | another template parameter | called once per frame, so one indirect call is noise next to sensor I/O; keeps `Pipeline` to one template parameter ([[callbacks]]) |
| `jthread` plus a `stop_callback` that closes the queue | atomic flag and manual `join` | every exit path stops and joins, including a constructor that throws after the first thread started ([[jthread]]) |
| threads declared last | threads declared anywhere | members are built in declaration order, so the threads start only after everything they use exists; if construction fails midway, they are the first to be stopped ([[construction-order]]) |

what a production version would add, and where it would go: a real sensor behind `Source` with a read timeout; a latency histogram and dropped-frame counter ([[observability]]) around `processor_(*msg)`; validated configuration instead of defaults; and `std::format` ([[format]]) for output on a toolchain that has it. none of these require changing the structure, which is the real test of a design: the seams are where the next requirements land.

### watch out for

**every blocking call must cooperate with cancellation.** the producer checks its stop token only between messages. if `source_()` blocks indefinitely (a sensor read with no timeout), `~Pipeline` waits for it, and shutdown hangs. cooperative cancellation only works if every blocking call cooperates: give the real source a timeout, or pass it the stop token so it can abandon the read.

### the takeaway

good C++ design is mostly about who owns what, who may block, and what can be substituted; when those three answers are explicit in the types, the rest of the program becomes small and testable.

### optional challenge

what goes wrong if you move `BoundedQueue<Message> queue_;` below the two `std::jthread` members, leaving the constructor's initializer list unchanged?

<details>
<summary>answer</summary>

members are initialized in declaration order, not initializer-list order ([[construction-order]]). the `jthread`s would be constructed first, so the consumer thread could call `queue_.pop()` (and the producer `queue_.push()`) before `queue_` has been constructed: undefined behavior, and a race you might not see in testing. GCC's `-Wreorder` (part of `-Wall`) warns, because the initializer list no longer matches the declaration order, but that warning is the only safety net. normal destruction would happen to survive, because the destructor body joins both threads before any member is destroyed. the exceptional path would not: if a later member's constructor threw, the already-running threads would be torn down around a queue that was never built. declaring threads last, after everything they touch, makes both orders correct by construction.

</details>
