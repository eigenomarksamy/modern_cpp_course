<a id="day-49"></a>

## day 49: week 7 review: design with judgment

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 43 to 48

### recap

| day | key idea |
|---|---|
| [43](#day-43) | SOLID, coupling, and cohesion are heuristics for the cost of change. Put seams where change actually happens, let the client own narrow interfaces, and treat the header graph as part of the design. |
| [44](#day-44) | Inject what crosses a boundary (time, hardware, I/O). Choose the seam by when the decision is made: virtual interface (run time), template plus concept (compile time), `std::function` (one operation), link time (platform functions). Wire everything near `main`. Prefer fakes to mocks. |
| [45](#day-45) | Patterns are vocabulary. Strategy is a callable, an interface, or a template parameter; factories return `std::unique_ptr`; registries are filled explicitly, not by static self-registration; observers use RAII tokens and are notified outside the lock. |
| [46](#day-46) | Four kinds of polymorphism: virtual (open set, reference semantics, binary boundaries), templates and concepts (compile time), `std::variant` (closed set), type erasure (open set with value semantics). Measure before choosing on speed. |
| [47](#day-47) | Contracts go into types first: strong types, enums instead of `bool`, views for borrowing, `[[nodiscard]]` results, one error channel per kind of failure. Pimpl buys a compile-time and ABI firewall for an allocation and an indirection. |
| [48](#day-48) | Modules replace textual inclusion; adopt from the leaves, gated by build-system support. Coroutines keep state in a frame; the return type's `promise_type` defines behavior, and reference parameters dangle across suspension points. |

### review questions

1. Your codebase has `IConfigLoader` with exactly one implementation, `YamlConfigLoader`, used only by `App`, and a mock used in one test that checks `load()` was called once. Keep the interface, or remove it? What would change your answer?
2. In day 45's `Signal`, why does `subscribe` return a `[[nodiscard]]` token, and why does the token hold a `std::weak_ptr` to the signal's state rather than a raw pointer or a `shared_ptr`?
3. A radar processing chain passes about a dozen message types defined by a versioned interface document, and a hot loop dispatches on them. Separately, third-party detection plugins are loaded from shared libraries at startup. Which polymorphism mechanism fits each, and why?
4. A pimpl class compiles in its own `.cpp` file but every client fails with an error about applying `sizeof` to an incomplete type. What is missing, and why does the fix work?
5. Predict the problem:

   ```cpp
   Generator<std::string_view> fields(std::string_view line);   // splits on commas, lazily
   std::string read_line();

   auto f = fields(read_line());
   while (f.next()) use(f.value());
   ```

6. **From week 3.** A type-erased wrapper declares `template <typename T> Wrapper(T&& value);` with no constraint. What happens on `Wrapper copy = original;` when `original` is a non-const `Wrapper`, and which earlier lesson predicted this?
7. **From week 6.** Day 45's `emit` copies the subscriber list under the lock and then calls the slots without it. Name two distinct failures if it called the slots while holding a `std::mutex` instead.

### mini exercise

This uploader cannot be unit tested: it constructs its own HTTP client and reads the wall clock directly. Refactor it so that the transport and the clock are injected, then write a fake transport and a test that checks two behaviors: the buffer is kept when sending fails, and cleared when it succeeds. Keep the production wiring simple.

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
<summary>1. the single-implementation interface</summary>

Probably remove it. An interface with one implementation and a test that only verifies a call happened is indirection without a seam: config loading is input conversion, and the better design is a free function that turns text into a `Config` value, plus an `App` constructor that takes the `Config` (day 43's MotorController challenge). The test then builds a `Config` directly and needs no mock at all. Keep or add an interface when there is a real boundary to cross at run time: config fetched from a remote service in some deployments and a file in others, or tests that need to simulate failures of the source (permissions, timeouts) that a value cannot express.

</details>

<details>
<summary>2. tokens and weak_ptr</summary>

The token is the subscription: its destructor unsubscribes. Discarding the return value would subscribe and immediately unsubscribe, a silent bug, so `[[nodiscard]]` turns it into a warning. The token must work whether it dies before or after the signal. A raw pointer would dangle if the signal were destroyed first. A `shared_ptr` would keep the signal's state alive as long as any token exists, so ownership would be dictated by subscribers, the opposite of what an observer should do. `weak_ptr::lock()` answers "is the signal still there?" safely and does not extend its life.

</details>

<details>
<summary>3. radar messages and plugins</summary>

The internal messages are a closed, versioned set: `std::variant` with `std::visit`. Value semantics, no per-message heap allocation, and adding a type forces every visitor to be updated (with an `overloaded` visitor lacking a catch-all, a missing case fails to compile). Templates alone cannot hold mixed types in one stream. The plugins form an open set that crosses a shared-library boundary: a virtual interface plus an `extern "C"` factory, because templates cannot cross that boundary and a variant cannot be extended by someone else. If the hot loop ever shows the dispatch in a profile, that is the time to reconsider, not before.

</details>

<details>
<summary>4. pimpl and the incomplete type</summary>

The class does not declare its destructor (and probably its move operations), so the compiler defines them implicitly and inline, in every client translation unit. They destroy the `std::unique_ptr<Impl>`, and `std::default_delete<Impl>` requires `Impl` to be complete, which it is only in the class's own `.cpp`. Declaring `~Widget();` and the move operations in the header and defining them as `= default` in the `.cpp` (after `Impl` is defined) moves the code that destroys `Impl` to the one place where it is complete.

</details>

<details>
<summary>5. the lazy splitter</summary>

`read_line()` returns a temporary `std::string`. The `std::string_view` parameter is copied into the coroutine frame, but it points into that temporary, which is destroyed at the end of the full-expression `auto f = fields(read_line());`. Because the generator starts lazily, all of the splitting happens later, reading freed memory: undefined behavior. Every yielded `string_view` would also point into the dead string. Fix: take `std::string line` by value so the frame owns the text, and make sure consumers are done with each yielded view before the generator is destroyed, or yield `std::string` values.

</details>

<details>
<summary>6. from week 3: the greedy forwarding constructor</summary>

For a non-const lvalue, `T` deduces to `Wrapper&`, so the template's parameter is `Wrapper&`: an exact match, better than the copy constructor's `const Wrapper&`. The template wins and wraps a `Wrapper` inside the wrapper (or fails to compile in some confusing way). Day 19 called this the hijacked copy constructor; day 46's challenge showed why a by-value parameter avoids it. Fix by constraining: `requires (!std::same_as<std::remove_cvref_t<T>, Wrapper>)`.

</details>

<details>
<summary>7. from week 6: callbacks under a lock</summary>

First, reentrancy: a slot that subscribes, unsubscribes (for example a one-shot handler that resets its own token), or emits on the same signal locks the same non-recursive `std::mutex` again, which is undefined behavior and in practice usually a deadlock. Second, lock-order deadlocks across threads (day 41): the slot may take its own mutex while thread B, holding that mutex, tries to subscribe and waits for the signal's mutex. A third, softer problem is latency: a slow slot blocks every thread that wants to subscribe or emit.

</details>

<details>
<summary>mini exercise: one possible solution</summary>

The transport becomes a narrow interface owned by the uploader's module (day 43's DIP), and the clock a `std::function` (one operation, day 44). The production `main` would pass an adapter over the real HTTP client and `std::chrono::system_clock::now`.

```cpp
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

Notice what the fake lets you test that the original could not: the failure path, and the exact payload, both without a network. Note also the borrowed `BatchSink&`: the sink must outlive the uploader, which is natural when both are created in `main`.

</details>

### connections

This week leaned on almost everything before it. Ownership in signatures and `std::unique_ptr` with incomplete types came from week 2 (days 11 to 13), which is also where virtual dispatch and Liskov substitution were introduced. `std::function`, forwarding references, and exception-safe error channels came from week 3. `std::variant` as a closed-set alternative to inheritance came from week 4 (day 25), and concepts as the constraint language for compile-time injection and type erasure came from week 5 (day 29), along with `std::span` and `std::string_view` as borrowing parameters. Week 6's rule about not calling unknown code under a lock reappeared in the observer.

Week 8 cashes these designs in. Day 50 gives you the tools to settle "is the virtual call too slow?" with data instead of opinion. Day 53 builds tests on day 44's fakes and seams, day 54 uses seams to get legacy code under test before changing it, and day 55 assembles an injected clock, a variant message type, concepts, and RAII shutdown into one small pipeline.
