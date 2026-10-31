<a id="day-37"></a>

## day 37: data races and mutexes

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 06, 08, 19, 36

### the idea

Two radar worker threads each count processed frames into a shared `long`, a million frames each. On one machine with GCC 12, an `-O0` build printed totals between 1.0 and 1.5 million, different on every run. The `-O2` build printed exactly 2,000,000 every time. A colleague concludes the release build is fine and the debug build is "just losing a few counts." Both conclusions are wrong. The program has a data race, and a data race is undefined behavior, not an imprecise number. The release build only looks right because the optimizer, assuming no race, collapsed each thread's loop into a single addition.

### understanding the concept

The standard's definition is precise, and worth knowing word for word in spirit:

- Two expression evaluations **conflict** if they access the same memory location and at least one of them modifies it. (A memory location is a scalar object or a run of adjacent non-zero-width bit-fields; two different `char` members are different locations, which is why threads may safely write neighbouring struct members.)
- A program has a **data race** if it contains two potentially concurrent conflicting actions, at least one of which is not atomic, and neither happens before the other.
- Any data race is **UB** (day 06).

Why UB rather than "some interleaving of the two"? Because the compiler is allowed to optimize single-threaded code as if no other thread could be watching. It may keep a variable in a register for a whole loop, merge or split stores, or hoist a load out of a loop entirely, which turns `while (!done) {}` into an infinite loop. On some targets a 64-bit store is two instructions, and a reader can see half of each value. `++count` is a read-modify-write: three steps, and even when it compiles to a single x86 instruction, it is not atomic without a `lock` prefix.

A **race condition** is different: a bug where the result depends on timing. You can have one with no data race at all, when every access is properly locked but the *sequence* of operations is not. Locking each step separately does not make the sequence atomic.

A mutex fixes data races by creating happens-before edges. Each `unlock()` of a mutex synchronizes with the next `lock()` of the same mutex, so everything a thread wrote inside its critical section is visible to the next thread that takes the lock. You never call `lock()`/`unlock()` by hand; you use an RAII lock (day 08) so exceptions and early returns cannot leave it held.

| lock type | when to use |
|---|---|
| `std::lock_guard` | one mutex, locked for the whole scope; the default |
| `std::scoped_lock` (C++17) | one *or several* mutexes; locks several without deadlock (day 41) |
| `std::unique_lock` | needs to unlock early, defer, try, time out, or be moved; required by `std::condition_variable` (day 38) |
| `std::shared_lock` + `std::shared_mutex` (C++17) | many readers or one writer |

### in code

The counter, broken and fixed:

```cpp
#include <mutex>
#include <thread>

long frames = 0;
void count_frames_racy() {
    for (int i = 0; i < 1'000'000; ++i) ++frames;   // BUG: data race, UB
}

std::mutex frames_mutex;
long frames_safe = 0;
void count_frames() {
    for (int i = 0; i < 1'000'000; ++i) {
        std::lock_guard lock(frames_mutex);          // CTAD: lock_guard<std::mutex>
        ++frames_safe;
    }
}

int main() {
    std::thread a(count_frames), b(count_frames);
    a.join();
    b.join();
    // frames_safe == 2'000'000, guaranteed
}
```

Locking per increment is correct but makes the threads take turns on every iteration. Better designs avoid sharing: count locally and add once at the end, or use an atomic counter (day 40). Correct first, then reduce sharing.

Now a race condition with no data race. Every method locks, and the code is still wrong:

```cpp
#include <map>
#include <mutex>

struct Track { double range_m; double velocity_mps; };

class TrackTable {
public:
    bool contains(int id) const {
        std::lock_guard lock(m_);
        return tracks_.count(id) != 0;
    }
    void insert(int id, Track t) {
        std::lock_guard lock(m_);
        tracks_[id] = t;
    }
    // Fix: make the operation callers need a single critical section.
    bool insert_if_absent(int id, Track t) {
        std::lock_guard lock(m_);
        return tracks_.try_emplace(id, t).second;
    }
private:
    mutable std::mutex m_;              // mutable: const readers must lock too
    std::map<int, Track> tracks_;
};

// BUG (race condition, not UB): another thread may insert between the two calls
// if (!table.contains(id)) table.insert(id, initial_track);
```

The lesson is about API design: the critical section is part of the interface. A thread-safe class must offer the *transactions* its callers need, not just thread-safe getters and setters.

Finally, encapsulate the mutex with the data it protects, so it is impossible to touch the data without the lock:

```cpp
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

`with_lock` deliberately returns `auto`, not `decltype(auto)`: a lambda that returns `auto&` gets a copy, so a reference to the guarded data cannot escape by accident. A determined caller can still smuggle out a pointer; the wrapper prevents mistakes, not malice.

### in practice

A motion controller reads a calibration table at 1 kHz from several control threads; an operator tool updates it a few times per hour. This looks like the textbook case for `std::shared_mutex`, and it might be, but measure before assuming. A shared lock is not free: every reader still writes to the mutex's internal state, so the cache line holding it moves between cores on every acquisition, and if critical sections are short, that traffic can cost as much as the exclusive lock you were avoiding. The standard also says nothing about fairness between readers and writers, so writer starvation depends on the implementation.

An alternative worth knowing is the immutable snapshot: keep a `std::shared_ptr<const CalibrationTable>`, and have readers lock a mutex only long enough to copy the pointer. The writer builds a new table outside any lock and swaps the pointer under the mutex. Readers then use their snapshot with no lock held, and an old table lives until its last reader drops it (day 12). Sharing immutable data is the cheapest kind of sharing to reason about.

Whatever you choose, keep critical sections small: no I/O, no logging, no allocation-heavy formatting, and no calls into unknown code while holding a lock. Copy what you need out, unlock, then do the slow work.

### watch out for

Returning references, pointers, iterators, or `string_view`s into guarded data. The lock protects the data only while it is held:

```cpp
const Track& find(int id) const {
    std::lock_guard lock(m_);
    return tracks_.at(id);   // BUG: the caller reads it after the lock is released
}
```

The caller's read races with any writer, and if another thread erases the entry, the reference dangles. Return by value (`std::optional<Track>`), or pass a callable in, as `with_lock` does. Tools help but do not replace design: ThreadSanitizer (`-fsanitize=thread` with GCC or Clang on Linux and macOS) reports races that occur on paths your tests actually execute, and silence means only that.

### the takeaway

A data race is UB, not an imprecise result. Bundle each mutex with the data it guards, make each method one complete transaction, and never let a reference to guarded data outlive the lock.

### optional challenge

This compiles. What does it actually protect?

```cpp
void TrackTable::clear() {
    std::unique_lock<std::mutex>(m_);
    tracks_.clear();
}
```

<details>
<summary>answer</summary>

Nothing. `std::unique_lock<std::mutex>(m_);` is parsed as a *declaration* (the same rule behind the most vexing parse, day 02): a new local variable named `m_`, of type `std::unique_lock<std::mutex>`, default-constructed, owning no mutex. It shadows the member, and `tracks_.clear()` runs unlocked. With `std::lock_guard` the same mistake fails to compile, because `lock_guard` has no default constructor, which is one more reason to prefer it. Always name your locks: `std::unique_lock lock(m_);`. GCC 12 with `-Wall` does warn here ("unnecessary parentheses in declaration of 'm_'"), and `-Wshadow` reports the shadowing, which is a good argument for treating warnings as errors.

</details>
