---
title: patterns in modern C++: observer and subscriptions
standard: C++17
objective: notify interested parties without dangling observers, using RAII subscription tokens and notification outside the lock
prerequisites: factory, deadlocks, shared-ptr
difficulty: 3
---

### the idea

a radar tracker announces "track confirmed" and "track lost" to a display, a recorder, and a fusion module, none of which it should know about. the classic observer pattern solves the knowing. it says nothing about the two problems that cause the real bugs: an observer that is destroyed while still registered, and a notification that calls unknown code while holding a lock.

### understanding the concept

- **observer** lets a subject notify interested parties without knowing them. the hard parts are lifetime (an observer destroyed while still registered) and concurrency (calling unknown code while holding a lock, [[deadlocks]]).

### in code

**observer with RAII subscriptions.** the subscription token unsubscribes in its destructor, and `emit` calls observers outside the lock.

```cpp complete
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

`[[nodiscard]]` matters here: discarding the token would unsubscribe immediately. the `weak_ptr` lets a token outlive its signal safely. the moved-from token holds an empty `weak_ptr`, so its destructor does nothing.

### in practice

a radar tracker publishes "track confirmed" and "track lost" events to a display, a recorder, and a fusion module. with a raw `std::vector<Listener*>` in the tracker, the display gets closed, its object is destroyed, and the next event calls through a dangling pointer: undefined behavior, typically a crash far from the cause. RAII tokens tie the subscription's lifetime to the subscriber object (store the token as a member, and it unsubscribes when the subscriber dies).

the other classic fix is a subject holding `std::weak_ptr<Listener>` and calling `lock()` before each notification. it is correct, but it forces every observer to be owned by a `shared_ptr`, which is an ownership decision imposed by the notification mechanism ([[shared-ptr]] calls that a smell). tokens leave ownership to the observer.

calling observers outside the lock is the [[deadlocks]] rule in action: a slot that subscribes, unsubscribes, or emits again would deadlock on a non-recursive mutex if `emit` held it, and a slow slot would block every other thread trying to subscribe.

### watch out for

the snapshot in `emit` has a consequence. a slot can be called after its token was reset, if the reset happened after the snapshot was taken. the `shared_ptr<Slot>` keeps the `std::function` alive, but not whatever its lambda captured by reference, so if the subscriber object is gone, the call is undefined behavior. in a single thread this only happens when one slot destroys another subscriber during `emit`; re-checking under the lock that each slot is still registered just before calling it closes that case. across threads the re-check can go stale between the check and the call, so either make `reset` wait until in-flight calls to that slot finish, or deliver events by posting to the subscriber's own thread or queue ([[blocking-queue]]). decide which threading contract your signal offers and document it.

### the takeaway

give every subscription an owner in the form of an RAII token, notify from a snapshot with no lock held, and document which thread calls observers and whether a call can arrive after unsubscribing.

### optional challenge

a colleague changes `emit` to hold the lock while calling the slots, "to fix the cross-thread race". what breaks, even in a single-threaded program?

<details>
<summary>answer</summary>

any slot that touches the same signal from inside the callback now deadlocks, because `std::mutex` is not recursive and locking it twice from the same thread is undefined behavior (in practice usually a deadlock). common cases are a one-shot listener that destroys its own token when it fires, a listener that subscribes a follow-up handler, and an event handler that emits another event on the same signal. switching to `std::recursive_mutex` hides the deadlock but not the problem: erasing from `slots` while `emit` is iterating over it invalidates the iterator, which is also undefined behavior. the snapshot exists precisely to make reentrancy safe; the cross-thread issue needs a different fix (wait for in-flight calls, or post to the subscriber's thread).

</details>
