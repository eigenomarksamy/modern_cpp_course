<a id="day-55"></a>

## day 55: putting it together: a small sensor-processing pipeline

**reading time:** about 10 minutes · **standard:** C++20 · **builds on:** days 12, 25, 29, 30, 31, 32, 36, 38, 44

### the idea

Each lesson so far isolated one idea. Real code is where the ideas meet and pull against each other: the queue wants ownership to move, the processing stage wants to borrow, the test wants seams, and shutdown wants all of it to unwind in the right order. Today is one small program, about 160 lines, that compiles with `-std=c++20`, followed by a review of every decision in it.

### understanding the concept

The shape is a classic two-stage pipeline:

```text
 source (fake sensor)          bounded queue            consumer thread
 producer jthread  ---push--->  [ Message x 8 ]  ---pop--->  Processor<Sink>
                                                              gate(span) -> sink.on_frame(span)
```

A producer thread pulls `Message`s (a frame of detections or a sensor fault) from an injected source and pushes them into a bounded queue. A consumer thread pops them, gates each frame's detections (drop weak and distant returns, sort strongest first), and hands the result to an injected sink. Ownership flows one way: a `Frame` is created by the source, moved through the queue, and owned by exactly one stage at a time. The sink only borrows the result.

Read the four parts for structure first, then the design review that follows.

### in code

Part 1 defines the vocabulary: a value type and a closed set of messages.

```cpp
// part 1: values and messages (days 25, 32)
#include <algorithm>
#include <cassert>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <deque>
#include <functional>
#include <mutex>
#include <optional>
#include <ranges>
#include <span>
#include <stop_token>
#include <thread>
#include <utility>
#include <variant>
#include <vector>

struct Detection {
    double range_m{}, azimuth_rad{}, snr_db{};
    bool operator==(const Detection&) const = default;  // equality yes, ordering no
};
struct Frame { std::uint64_t seq{}; std::vector<Detection> detections; };
struct SensorFault { std::uint64_t seq{}; int code{}; };
using Message = std::variant<Frame, SensorFault>;

template <typename... Fs> struct overloaded : Fs... { using Fs::operator()...; };
```

Part 2 is day 38's queue, with close semantics so shutdown never leaves a thread blocked forever.

```cpp
// part 2: a bounded, closable queue (day 38)
template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {}
    bool push(T item) {                      // blocks while full; false once closed
        std::unique_lock lock(m_);
        not_full_.wait(lock, [&] { return closed_ || q_.size() < capacity_; });
        if (closed_) return false;
        q_.push_back(std::move(item));
        not_empty_.notify_one();
        return true;
    }
    std::optional<T> pop() {                 // blocks while empty; nullopt once closed and drained
        std::unique_lock lock(m_);
        not_empty_.wait(lock, [&] { return closed_ || !q_.empty(); });
        std::optional<T> item;
        if (!q_.empty()) {
            item.emplace(std::move(q_.front()));
            q_.pop_front();
            not_full_.notify_one();
        }
        return item;
    }
    void close() {
        { std::lock_guard lock(m_); closed_ = true; }
        not_full_.notify_all(); not_empty_.notify_all();
    }
private:
    std::mutex m_;
    std::condition_variable not_full_, not_empty_;
    std::deque<T> q_;
    std::size_t capacity_;
    bool closed_ = false;
};
```

Part 3 is the actual work. `gate` is a pure function over a borrowed span; `Processor` adapts it to messages and is constrained on what a sink must provide.

```cpp
// part 3: the processing stage (days 29, 30, 31, 52)
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

Part 4 wires it together. Member order is the shutdown protocol, and `main` doubles as the test.

```cpp
// part 4: wiring, shutdown, and a test run (days 08, 36, 44)
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

Concatenated in order, the four parts form one translation unit. Built with `g++ -std=c++20 -Wall -Wextra -pedantic -O2 -pthread` (GCC 12), it compiles without warnings and prints:

```text
frame 0:  50 m / 18 dB  80 m / 12 dB
frame 1:  51 m / 18 dB  80 m / 13 dB
frame 3:  53 m / 18 dB  80 m / 15 dB
faults: 1 (code 17)
```

The output is deterministic even though two threads are involved: the queue is FIFO and there is one consumer, so the order of messages is fixed by the source.

### in practice

Here is the design review, the part of the exercise that matters most. Every row is a decision someone could reasonably have made differently.

| decision | alternative | why this one |
|---|---|---|
| `Detection` defaults `==` only | also default `<=>` | `double` members give only `partial_ordering`, and detections have no natural order; sort by an explicit projection instead (day 32) |
| `Message` is a `std::variant` | base class with virtual `handle()` | closed set, value semantics, no allocation per message; a missing case in the visitor fails to compile (day 25) |
| bounded queue, producer blocks | unbounded queue, or drop-oldest | back-pressure bounds memory and latency; a sensor that cannot wait would need drop-oldest instead (day 38) |
| `gate` is a free function on `std::span` | member function taking `std::vector` | pure and testable without threads; any contiguous owner works (day 31) |
| `scratch_` reused every frame | return a fresh vector | no steady-state allocation (day 52); the cost is that `Processor` is stateful and not reentrant |
| sink: template constrained by a concept | virtual interface, or `std::function` | the per-frame call can inline, and a wrong sink fails to compile where the pipeline is created, naming the unmet requirement (days 29, 44); the cost is that `Pipeline` is a template |
| source: `std::function` | another template parameter | called once per frame, so one indirect call is noise next to sensor I/O; keeps `Pipeline` to one template parameter (day 17) |
| `jthread` plus a `stop_callback` that closes the queue | atomic flag and manual `join` | every exit path stops and joins, including a constructor that throws after the first thread started (day 36) |
| threads declared last | threads declared anywhere | members are built in declaration order, so the threads start only after everything they use exists; if construction fails midway, they are the first to be stopped (day 09) |
| `views::filter` feeding a loop | `std::copy_if` | equally good; C++20 has no `ranges::to` (that is C++23), so materializing is explicit either way (day 30) |

What a production version would add, and where it would go: a real sensor behind `Source` with a read timeout; a latency histogram and dropped-frame counter (day 53) around `processor_(*msg)`; validated configuration instead of defaults; and `std::format` (day 34) for output on a toolchain that has it. None of these require changing the structure, which is the real test of a design: the seams are where the next requirements land.

### watch out for

The producer checks its stop token only between messages. If `source_()` blocks indefinitely (a sensor read with no timeout), `~Pipeline` waits for it, and shutdown hangs. Cooperative cancellation (day 36) only works if every blocking call cooperates: give the real source a timeout, or pass it the stop token so it can abandon the read. The same discipline applies to the sink: it receives a span into `scratch_` that is overwritten by the next frame, so a sink that keeps the span instead of copying the data would read garbage later (the lifetime rule from days 26 and 31, now enforced only by a comment in the concept).

### the takeaway

Good C++ design is mostly about who owns what, who may block, and what can be substituted; when those three answers are explicit in the types, the rest of the program becomes small and testable.

### optional challenge

What goes wrong if you move `BoundedQueue<Message> queue_;` below the two `std::jthread` members, leaving the constructor's initializer list unchanged?

<details>
<summary>answer</summary>

Members are initialized in declaration order, not initializer-list order (day 09). The `jthread`s would be constructed first, so the consumer thread could call `queue_.pop()` (and the producer `queue_.push()`) before `queue_` has been constructed: undefined behavior, and a race you might not see in testing. GCC's `-Wreorder` (part of `-Wall`) warns, because the initializer list no longer matches the declaration order, but that warning is the only safety net. Normal destruction would happen to survive, because the destructor body joins both threads before any member is destroyed. The exceptional path would not: if a later member's constructor threw, the already-running threads would be torn down around a queue that was never built. Declaring threads last, after everything they touch, makes both orders correct by construction.

</details>
