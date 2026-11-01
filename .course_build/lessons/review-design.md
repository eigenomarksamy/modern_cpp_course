---
title: review: design principles and patterns
kind: review
standard: C++17
objective: consolidate SOLID, coupling and cohesion, dependency injection and seams, and the strategy, factory, and observer patterns
prerequisites: solid, coupling-cohesion, dependency-injection, test-seams, strategy, factory, observer
difficulty: 2
---

### recap

| lesson | key idea |
|---|---|
| [[solid]] | SOLID predicts the cost of change; separate responsibilities where change actually happens. |
| [[coupling-cohesion]] | what changes together, what belongs together, and in C++ what recompiles together; consumers own their interfaces. |
| [[dependency-injection]] | inject what crosses a boundary, make ownership explicit, wire in one place near `main`. |
| [[test-seams]] | choose the seam by when the decision is made: run time, compile time, or link time. |
| [[strategy]] | a replaceable algorithm: template, `std::function`, or virtual interface, by frequency and shape. |
| [[factory]] | return `std::unique_ptr<Base>`, register creators explicitly, not through static initializers. |
| [[observer]] | RAII subscription tokens, notification from a snapshot with no lock held. |

### review questions

1. your codebase has `IConfigLoader` with exactly one implementation, `YamlConfigLoader`, used only by `App`, and a mock used in one test that checks `load()` was called once. keep the interface, or remove it? what would change your answer?
2. in [[observer]]'s `Signal`, why does `subscribe` return a `[[nodiscard]]` token, and why does the token hold a `std::weak_ptr` to the signal's state rather than a raw pointer or a `shared_ptr`?
3. a `SensorRegistry` is populated by namespace-scope initializers in each driver's `.cpp`, and the drivers are built into a static library. on one product, `"lidar"` is suddenly an unknown type. what happened, and what is the robust fix?
4. a function that the profiler shows on a per-sample hot path takes a `const Filter&` with a virtual `apply(double)`. what seam would you use instead, and what do you give up?
5. from [[deadlocks]]: [[observer]]'s `emit` copies the subscriber list under the lock and then calls the slots without it. name two distinct failures if it called the slots while holding a `std::mutex` instead.

### mini exercise

this uploader cannot be unit tested: it constructs its own HTTP client and reads the wall clock directly. refactor it so that the transport and the clock are injected, then write a fake transport and a test that checks two behaviors: the buffer is kept when sending fails, and cleared when it succeeds. keep the production wiring simple.

```cpp
class TelemetryUploader {
public:
    void record(std::string line) { buffer_.push_back(std::move(line)); }
    void flush() {
        if (buffer_.empty()) return;
        HttpClient client("https://telemetry.internal");          // hard-wired transport
        const auto now = std::chrono::system_clock::now();         // hard-wired clock
        if (client.post("/batch", serialize(buffer_, now)) == 200) buffer_.clear();
    }
private:
    std::vector<std::string> buffer_;
};
```

### answers

<details>
<summary>answer 1: the single-implementation interface</summary>

probably remove it. an interface with one implementation and a test that only verifies a call happened is indirection without a seam: config loading is input conversion, and the better design is a free function that turns text into a `Config` value, plus an `App` constructor that takes the `Config` ([[coupling-cohesion]]'s `MotorController` challenge). the test then builds a `Config` directly and needs no mock at all. keep or add an interface when there is a real boundary to cross at run time: config fetched from a remote service in some deployments and a file in others, or tests that need to simulate failures of the source (permissions, timeouts) that a value cannot express.

</details>

<details>
<summary>answer 2: tokens and weak_ptr</summary>

the token is the subscription: its destructor unsubscribes. discarding the return value would subscribe and immediately unsubscribe, a silent bug, so `[[nodiscard]]` turns it into a warning. the token must work whether it dies before or after the signal. a raw pointer would dangle if the signal were destroyed first. a `shared_ptr` would keep the signal's state alive as long as any token exists, so ownership would be dictated by subscribers, the opposite of what an observer should do. `weak_ptr::lock()` answers "is the signal still there?" safely and does not extend its life.

</details>

<details>
<summary>answer 3: self-registration and static libraries</summary>

if nothing in the executable references a symbol in `lidar.o`, the linker never pulls that object file out of the static library, so its namespace-scope initializer never runs and the registration never happens. the build succeeds; the type is simply missing at run time. the robust fix is explicit registration: a `register_builtin_sensors(registry)` function called from `main`, which also makes the set of sensors visible in one place.

</details>

<details>
<summary>answer 4: a hot-path seam</summary>

make the filter a template parameter constrained by a concept: the call becomes direct and inlinable, which also lets the compiler vectorize the loop around it. you give up choosing the filter at run time and storing different filters behind one type; if both are needed, keep the virtual interface at a coarser grain (one call per block of samples) and use the template inside the block.

</details>

<details>
<summary>answer 5: callbacks under a lock</summary>

first, reentrancy: a slot that subscribes, unsubscribes (for example a one-shot handler that resets its own token), or emits on the same signal locks the same non-recursive `std::mutex` again, which is undefined behavior and in practice usually a deadlock. second, lock-order deadlocks across threads ([[deadlocks]]): the slot may take its own mutex while thread B, holding that mutex, tries to subscribe and waits for the signal's mutex. a third, softer problem is latency: a slow slot blocks every thread that wants to subscribe or emit.

</details>

<details>
<summary>mini exercise answer</summary>

the transport becomes a narrow interface owned by the uploader's module ([[coupling-cohesion]]'s DIP), and the clock a `std::function` (one operation, [[dependency-injection]]). the production `main` would pass an adapter over the real HTTP client and `std::chrono::system_clock::now`.

the complete refactored class, the fake, and the test are in "going deeper" below.

notice what the fake lets you test that the original could not: the failure path, and the exact payload, both without a network. note also the borrowed `BatchSink&`: the sink must outlive the uploader, which is natural when both are created in `main`.

</details>

### connections

design is where everything earlier in the course meets: ownership decides how components are wired ([[ownership-in-interfaces]]), lifetimes decide whether an observer or an injected reference is safe ([[temporaries-dangling]]), and the polymorphism mechanisms decide what a seam costs. the next module looks at the remaining design choices with long-term consequences: which kind of polymorphism to use, how to keep an API stable once it ships, and two C++20 features that change how code is organized, modules and coroutines.

### going deeper

#### the uploader, refactored and tested

```cpp complete
#include <cassert>
#include <chrono>
#include <functional>
#include <string>
#include <string_view>
#include <vector>

class BatchSink {
public:
    virtual ~BatchSink() = default;
    virtual bool send(std::string_view payload) = 0;   // true on success
};

using WallClock = std::function<std::chrono::system_clock::time_point()>;

class TelemetryUploader {
public:
    TelemetryUploader(BatchSink& sink, WallClock now) : sink_(sink), now_(std::move(now)) {}
    void record(std::string line) { buffer_.push_back(std::move(line)); }
    void flush() {
        if (buffer_.empty()) return;
        if (sink_.send(serialize(now_()))) buffer_.clear();
    }
    std::size_t pending() const { return buffer_.size(); }
private:
    std::string serialize(std::chrono::system_clock::time_point t) const {
        std::string out = std::to_string(t.time_since_epoch().count()) + '\n';
        for (const auto& l : buffer_) out += l + '\n';
        return out;
    }
    BatchSink& sink_;
    WallClock now_;
    std::vector<std::string> buffer_;
};

struct FakeSink final : BatchSink {
    bool succeed = false;
    std::vector<std::string> sent;
    bool send(std::string_view payload) override {
        sent.emplace_back(payload);
        return succeed;
    }
};

int main() {
    FakeSink sink;
    TelemetryUploader up(sink, [] { return std::chrono::system_clock::time_point{}; });
    up.record("battery=24.1");
    up.flush();                                        // sink fails
    assert(up.pending() == 1 && sink.sent.size() == 1);
    sink.succeed = true;
    up.flush();                                        // sink succeeds
    assert(up.pending() == 0 && sink.sent.back() == "0\nbattery=24.1\n");
}
```
