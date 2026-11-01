---
title: mutexes, locks, and thread-safe classes
standard: C++17
objective: protect shared data with RAII locks, design thread-safe classes whose methods are complete transactions, and never let guarded data escape the lock
prerequisites: data-races
difficulty: 2
---

### the idea

"this vector is protected by that mutex" is usually a comment, and comments are not checked. nothing stops a new method from touching the vector without the lock, or an existing method from handing out a reference that is read after the lock is gone. the mechanics of locking are easy; the hard part is designing a class so that the lock and the data it guards cannot be separated.

### understanding the concept

a mutex fixes data races by creating happens-before edges. each `unlock()` of a mutex synchronizes with the next `lock()` of the same mutex, so everything a thread wrote inside its critical section is visible to the next thread that takes the lock. you never call `lock()`/`unlock()` by hand; you use an RAII lock ([[raii]]) so exceptions and early returns cannot leave it held.

| lock type | when to use |
|---|---|
| `std::lock_guard` | one mutex, locked for the whole scope; the default |
| `std::scoped_lock` (C++17) | one *or several* mutexes; locks several without deadlock ([[deadlocks]]) |
| `std::unique_lock` | needs to unlock early, defer, try, time out, or be moved; required by `std::condition_variable` ([[condition-variables]]) |
| `std::shared_lock` + `std::shared_mutex` (C++17) | many readers or one writer |

a mutex protects *data*, not code. the useful question for every member of a thread-safe class is "which mutex guards this?", and the useful design keeps that answer structural: the mutex and its data are private members of the same small class, and every public method takes the lock for the whole of one logical operation.

### in code

finally, encapsulate the mutex with the data it protects, so it is impossible to touch the data without the lock:

```cpp complete
#include <mutex>
#include <utility>

template <typename T>
class Synchronized {
public:
    explicit Synchronized(T value) : value_(std::move(value)) {}

    template <typename F>
    auto with_lock(F&& f) {                 // 'auto' returns by value:
        std::lock_guard lock(m_);           // a reference returned by f is copied,
        return std::forward<F>(f)(value_);  // not leaked past the lock
    }
private:
    std::mutex m_;
    T value_;
};

// Synchronized<std::vector<Detection>> pending{{}};
// pending.with_lock([&](auto& v) { v.push_back(d); });
// auto n = pending.with_lock([](auto& v) { return v.size(); });
```

`with_lock` deliberately returns `auto`, not `decltype(auto)`: a lambda that returns `auto&` gets a copy, so a reference to the guarded data cannot escape by accident. a determined caller can still smuggle out a pointer; the wrapper prevents mistakes, not malice.

### in practice

a motion controller reads a calibration table at 1 kHz from several control threads; an operator tool updates it a few times per hour. this looks like the textbook case for `std::shared_mutex`, and it might be, but measure before assuming. a shared lock is not free: every reader still writes to the mutex's internal state, so the cache line holding it moves between cores on every acquisition, and if critical sections are short, that traffic can cost as much as the exclusive lock you were avoiding. the standard also says nothing about fairness between readers and writers, so writer starvation depends on the implementation.

an alternative worth knowing is the immutable snapshot: keep a `std::shared_ptr<const CalibrationTable>`, and have readers lock a mutex only long enough to copy the pointer. the writer builds a new table outside any lock and swaps the pointer under the mutex. readers then use their snapshot with no lock held, and an old table lives until its last reader drops it ([[shared-ptr]]). sharing immutable data is the cheapest kind of sharing to reason about.

whatever you choose, keep critical sections small: no I/O, no logging, no allocation-heavy formatting, and no calls into unknown code while holding a lock. copy what you need out, unlock, then do the slow work.

### watch out for

returning references, pointers, iterators, or `string_view`s into guarded data. the lock protects the data only while it is held:

```cpp
const Track& find(int id) const {
    std::lock_guard lock(m_);
    return tracks_.at(id);   // BUG: the caller reads it after the lock is released
}
```

the caller's read races with any writer, and if another thread erases the entry, the reference dangles. return by value (`std::optional<Track>`), or pass a callable in, as `with_lock` does. tools help but do not replace design: ThreadSanitizer (`-fsanitize=thread` with GCC or Clang on Linux and macOS) reports races that occur on paths your tests actually execute, and silence means only that.

### the takeaway

a data race is UB, not an imprecise result. bundle each mutex with the data it guards, make each method one complete transaction, and never let a reference to guarded data outlive the lock.

### optional challenge

this compiles. what does it actually protect?

```cpp
void TrackTable::clear() {
    std::unique_lock<std::mutex>(m_);
    tracks_.clear();
}
```

<details>
<summary>answer</summary>

nothing. `std::unique_lock<std::mutex>(m_);` is parsed as a *declaration* (the same rule behind the most vexing parse, [[initialization]]): a new local variable named `m_`, of type `std::unique_lock<std::mutex>`, default-constructed, owning no mutex. it shadows the member, and `tracks_.clear()` runs unlocked. with `std::lock_guard` the same mistake fails to compile, because `lock_guard` has no default constructor, which is one more reason to prefer it. always name your locks: `std::unique_lock lock(m_);`. GCC 12 with `-Wall` does warn here ("unnecessary parentheses in declaration of 'm_'"), and `-Wshadow` reports the shadowing, which is a good argument for treating warnings as errors.

</details>
