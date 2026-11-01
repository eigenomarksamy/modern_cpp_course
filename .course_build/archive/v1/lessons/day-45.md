<a id="day-45"></a>

## day 45: design patterns in modern C++: strategy, factory, and observer

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 12, 17, 25, 41, 43

### the idea

The classic pattern catalogue was written for C++98 and Smalltalk, before lambdas, `std::function`, `std::variant`, and smart pointers. Some patterns survive unchanged, some shrink to a single line, and some need modern care that the original books never mentioned, such as who owns an observer and which thread calls it. Today we look at three that every production codebase uses, and at what each one looks like when written with the tools you have now.

### understanding the concept

A pattern is a name for a recurring solution, not a goal. Its main value is vocabulary: "the planner takes a cost strategy" tells a reviewer a lot in six words. The risk is building the pattern because it is a pattern.

- **Strategy** makes an algorithm a replaceable part. In C++ you have three ways to plug it in, with different tradeoffs (the table below).
- **Factory** hides which concrete type gets created. In modern C++ the default form is a plain function returning `std::unique_ptr<Base>`; a registry of creators appears when the choice comes from data (a config file, a plugin name).
- **Observer** lets a subject notify interested parties without knowing them. The hard parts are lifetime (an observer destroyed while still registered) and concurrency (calling unknown code while holding a lock, day 41).

Several other classic patterns collapse into language features. Command is usually a lambda stored in a `std::function` or a queue. Visitor over a closed set of types is `std::visit` on a `std::variant` (day 25). Template method is often better served by passing a callable than by inheritance.

### in code

**Strategy, three ways.** An exponential moving average smooths radar range measurements inside a tracker.

```cpp
#include <functional>
#include <memory>

struct Ema {                                    // the algorithm as a plain value type
    double alpha;
    double y = 0.0;
    bool primed = false;
    double operator()(double x) {
        y = primed ? alpha * x + (1.0 - alpha) * y : x;
        primed = true;
        return y;
    }
};

// (a) virtual interface: strategies must inherit
class Smoother {
public:
    virtual ~Smoother() = default;
    virtual double operator()(double x) = 0;
};
class EmaSmoother final : public Smoother {
public:
    explicit EmaSmoother(double alpha) : ema_{alpha} {}
    double operator()(double x) override { return ema_(x); }
private:
    Ema ema_;
};
struct TrackerV { std::unique_ptr<Smoother> smooth; };

// (b) std::function: any callable with the right signature
struct TrackerF { std::function<double(double)> smooth; };

// (c) template parameter: fixed at compile time
template <typename Smooth>
struct TrackerT { Smooth smooth; };

// TrackerV v{std::make_unique<EmaSmoother>(0.3)};
// TrackerF f{Ema{0.3}};
// TrackerT<Ema> t{Ema{0.3}};
```

| | virtual interface | `std::function` | template parameter |
|---|---|---|---|
| chosen at | run time | run time | compile time |
| strategy types | must derive from `Smoother` | any copyable callable | any type the code compiles with (use a concept in C++20) |
| call mechanism | indirect call, rarely inlined | indirect call through type erasure; construction may allocate | direct call, inlinable |
| copying the owner | needs a `clone()` | value semantics | value semantics |
| mixed strategies in one container | yes | yes | no, each is a distinct type |
| best for | several related operations per strategy | one operation, callbacks | hot inner loops, per-build choice |

**Factory with a registry.** When a config file says `type: lidar`, something has to map that string to a constructor.

```cpp
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>

struct SensorConfig { std::string type, device; };

class Sensor {
public:
    virtual ~Sensor() = default;
    virtual double read() = 0;
};

using SensorFactory = std::function<std::unique_ptr<Sensor>(const SensorConfig&)>;

class SensorRegistry {
public:
    void add(std::string type, SensorFactory f) { makers_[std::move(type)] = std::move(f); }
    std::unique_ptr<Sensor> create(const SensorConfig& cfg) const {
        const auto it = makers_.find(cfg.type);
        if (it == makers_.end()) throw std::invalid_argument("unknown sensor type: " + cfg.type);
        return it->second(cfg);
    }
private:
    std::unordered_map<std::string, SensorFactory> makers_;
};

// explicit registration, called once from main: visible, ordered, link-safe
void register_builtin_sensors(SensorRegistry& r) {
    r.add("imu",   [](const SensorConfig& c) { return std::make_unique<Imu>(c.device); });
    r.add("lidar", [](const SensorConfig& c) { return std::make_unique<Lidar>(c.device); });
}
```

The tempting alternative is self-registration, where each `.cpp` file registers itself from a namespace-scope initializer:

```cpp
// lidar.cpp: "automatic" registration
namespace {
const bool lidar_registered = (global_registry().add("lidar", make_lidar), true);
}
```

It works in a demo and breaks in production for two reasons. First, if `lidar.o` lives in a static library and nothing else references a symbol in it, the linker never pulls that object file into the executable, so the initializer never runs and `"lidar"` is silently unknown (the usual workarounds, `--whole-archive` or `/WHOLEARCHIVE`, are build-system patches for a design problem). Second, the registry itself must be a function-local static, or you have the static initialization order problem from day 03. An explicit `register_builtin_sensors` call costs one line and has neither problem.

**Observer with RAII subscriptions.** The subscription token unsubscribes in its destructor, and `emit` calls observers outside the lock.

```cpp
#include <functional>
#include <map>
#include <memory>
#include <mutex>
#include <vector>

template <typename... Args>
class Signal {
    using Slot = std::function<void(Args...)>;
    struct State {
        std::mutex m;
        std::map<int, std::shared_ptr<Slot>> slots;
        int next_id = 0;
    };
    std::shared_ptr<State> state_ = std::make_shared<State>();

public:
    class Subscription {
    public:
        Subscription(std::weak_ptr<State> s, int id) : state_(std::move(s)), id_(id) {}
        Subscription(Subscription&&) noexcept = default;
        Subscription& operator=(Subscription&& o) noexcept {
            if (this != &o) { reset(); state_ = std::move(o.state_); id_ = o.id_; }
            return *this;
        }
        ~Subscription() { reset(); }
        void reset() {
            if (auto s = state_.lock()) {            // the signal may already be gone
                std::lock_guard lock(s->m);
                s->slots.erase(id_);
            }
            state_.reset();
        }
    private:
        std::weak_ptr<State> state_;
        int id_;
    };

    [[nodiscard]] Subscription subscribe(Slot f) {
        std::lock_guard lock(state_->m);
        const int id = state_->next_id++;
        state_->slots.emplace(id, std::make_shared<Slot>(std::move(f)));
        return Subscription(state_, id);
    }

    void emit(Args... args) const {
        std::vector<std::shared_ptr<Slot>> snapshot;
        {
            std::lock_guard lock(state_->m);
            for (const auto& kv : state_->slots) snapshot.push_back(kv.second);
        }
        for (const auto& slot : snapshot) (*slot)(args...);   // no lock held here
    }
};

// Signal<int> track_lost;
// {
//     auto sub = track_lost.subscribe([](int id) { std::cout << "lost " << id << '\n'; });
//     track_lost.emit(7);        // prints: lost 7
// }                              // sub destroyed: unsubscribed
// track_lost.emit(8);            // prints nothing
```

`[[nodiscard]]` matters here: discarding the token would unsubscribe immediately. The `weak_ptr` lets a token outlive its signal safely. The moved-from token holds an empty `weak_ptr`, so its destructor does nothing.

### in practice

A radar tracker publishes "track confirmed" and "track lost" events to a display, a recorder, and a fusion module. With a raw `std::vector<Listener*>` in the tracker, the display gets closed, its object is destroyed, and the next event calls through a dangling pointer: undefined behavior, typically a crash far from the cause. RAII tokens tie the subscription's lifetime to the subscriber object (store the token as a member, and it unsubscribes when the subscriber dies).

The other classic fix is a subject holding `std::weak_ptr<Listener>` and calling `lock()` before each notification. It is correct, but it forces every observer to be owned by a `shared_ptr`, which is an ownership decision imposed by the notification mechanism (day 12 calls that a smell). Tokens leave ownership to the observer.

Calling observers outside the lock is the day 41 rule in action: a slot that subscribes, unsubscribes, or emits again would deadlock on a non-recursive mutex if `emit` held it, and a slow slot would block every other thread trying to subscribe.

### watch out for

The snapshot in `emit` has a consequence. A slot can be called after its token was reset, if the reset happened after the snapshot was taken. The `shared_ptr<Slot>` keeps the `std::function` alive, but not whatever its lambda captured by reference, so if the subscriber object is gone, the call is undefined behavior. In a single thread this only happens when one slot destroys another subscriber during `emit`; re-checking under the lock that each slot is still registered just before calling it closes that case. Across threads the re-check can go stale between the check and the call, so either make `reset` wait until in-flight calls to that slot finish, or deliver events by posting to the subscriber's own thread or queue (day 38). Decide which threading contract your signal offers and document it.

Patterns also invite premature generality. A `SensorRegistry` for two sensor types that are chosen by a compile-time flag is overkill; a `switch` in one factory function is clearer until the set becomes data-driven.

### the takeaway

Use pattern names as vocabulary, then pick the lightest C++ mechanism that does the job: a callable for one-operation strategies, a function returning `std::unique_ptr` for factories, and RAII tokens plus lock-free notification for observers. Explicit wiring beats clever static registration.

### optional challenge

A colleague changes `emit` to hold the lock while calling the slots, "to fix the cross-thread race". What breaks, even in a single-threaded program?

<details>
<summary>answer</summary>

Any slot that touches the same signal from inside the callback now deadlocks, because `std::mutex` is not recursive and locking it twice from the same thread is undefined behavior (in practice usually a deadlock). Common cases are a one-shot listener that destroys its own token when it fires, a listener that subscribes a follow-up handler, and an event handler that emits another event on the same signal. Switching to `std::recursive_mutex` hides the deadlock but not the problem: erasing from `slots` while `emit` is iterating over it invalidates the iterator, which is also undefined behavior. The snapshot exists precisely to make reentrancy safe; the cross-thread issue needs a different fix (wait for in-flight calls, or post to the subscriber's thread).

</details>
