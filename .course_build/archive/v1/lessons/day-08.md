<a id="day-08"></a>

## day 08: RAII: let scope do the cleanup

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days 03, 06

### the idea

Here is a function that reads a calibration header from a file. It has three exits, and every one of them must remember `fclose`. Six months later someone adds a call that can throw, and now there is a fourth exit that nobody wrote down.

That is the whole problem RAII solves. Cleanup that depends on every author remembering every exit path will eventually be forgotten. Cleanup that the language performs whenever a scope ends cannot be forgotten, because nobody has to remember it.

### understanding the concept

RAII (resource acquisition is initialization; the name is famously bad) means: tie a resource to the lifetime of an object. The constructor acquires the resource, or throws if it cannot. The destructor releases it. You then lean on the lifetime rules from day 03: an object with automatic storage duration is destroyed when control leaves its scope, in reverse order of construction, however control leaves.

"However control leaves" is the important part. Normal fall-through, `return`, `break`, `continue`, `goto` out of a block, and an exception propagating to a handler all run the destructors of the automatic objects being left. During exception propagation this is called stack unwinding: each frame between the `throw` and the matching `catch` is torn down, destructors included.

A few exits do not run destructors, and you should know them:

- `std::exit` destroys static objects but not the automatic objects on the stack.
- `std::abort`, `std::_Exit`, a crash, and `kill -9` destroy nothing.
- If an exception is never caught, `std::terminate` is called, and **whether the stack is unwound first is implementation-defined**. GCC and Clang typically do not unwind in that case, so your destructors may not run.

The deeper idea is an invariant: **if the object exists, the resource is valid**. A `File` object that exists holds an open file. There is no "not yet opened" or "already closed" state for every caller to check. That is encapsulation in its most useful form: the class owns a rule, and no caller can break it.

Destructors are implicitly `noexcept` (since C++11), unless a base or member has a potentially-throwing destructor. If an exception escapes a `noexcept` destructor, `std::terminate` is called. Even a destructor explicitly marked `noexcept(false)` that throws while the stack is already unwinding because of another exception calls `std::terminate`. Treat "destructors do not throw" as a hard rule.

### in code

First, the naive version. It is correct today and fragile tomorrow.

```cpp
#include <cstdio>
#include <optional>

struct Header { char magic[4]; unsigned version; };

std::optional<Header> read_header(const char* path) {
    std::FILE* f = std::fopen(path, "rb");
    if (!f) return std::nullopt;

    Header h{};
    if (std::fread(&h, sizeof h, 1, f) != 1) {
        std::fclose(f);                  // exit 1: remembered
        return std::nullopt;
    }
    if (h.version > 3) {
        return std::nullopt;             // BUG: exit 2 leaks the FILE*
    }
    validate(h);                         // BUG: if this throws, f leaks too
    std::fclose(f);
    return h;
}
```

The RAII version moves the cleanup into a type. You rarely need a hand-written class for a C handle: `std::unique_ptr` with a custom deleter is already a general RAII wrapper.

```cpp
#include <cstdio>
#include <memory>
#include <optional>

struct FileCloser {
    void operator()(std::FILE* f) const noexcept { std::fclose(f); }
};
using FilePtr = std::unique_ptr<std::FILE, FileCloser>;

std::optional<Header> read_header(const char* path) {
    FilePtr f{std::fopen(path, "rb")};
    if (!f) return std::nullopt;

    Header h{};
    if (std::fread(&h, sizeof h, 1, f.get()) != 1) return std::nullopt;
    if (h.version > 3) return std::nullopt;
    validate(h);                         // may throw: f is still closed
    return h;                            // every path closes exactly once
}
```

Two details. `unique_ptr` never calls the deleter on a null pointer, so a failed `fopen` is handled for free. And the deleter is a function object rather than `&std::fclose`: since C++20, forming a pointer to most standard library functions is unspecified (possibly ill-formed), and an empty function object also lets the `unique_ptr` stay pointer-sized (more on that on day 12).

You already use this pattern every day: `std::lock_guard` locks in its constructor and unlocks in its destructor, `std::vector` frees its buffer, `std::ifstream` closes its file. For one-off cleanup that does not deserve its own type, a scope guard turns any callable into a destructor. C++17 class template argument deduction (CTAD) means you never spell out the lambda's type:

```cpp
#include <cstdio>
#include <utility>

template <typename F>
class ScopeGuard {
public:
    explicit ScopeGuard(F f) : f_(std::move(f)) {}
    ~ScopeGuard() { if (active_) f_(); }
    void dismiss() noexcept { active_ = false; }

    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;
private:
    F f_;
    bool active_ = true;
};

int main() {
    ScopeGuard a{[] { std::puts("release a"); }};   // CTAD deduces F
    ScopeGuard b{[] { std::puts("release b"); }};
    ScopeGuard c{[] { std::puts("rollback c"); }};
    c.dismiss();                                    // commit: skip rollback
    std::puts("body done");
}
// prints:
// body done
// release b
// release a
```

Reverse order of construction, as day 03 promised. `dismiss` gives you the commit-or-rollback shape: arm a rollback before a multi-step operation and disarm it once the last step succeeds. The Library Fundamentals TS has `scope_exit`, `scope_fail`, and `scope_success`, but they are not in the C++17 or C++20 standard library, so most codebases carry a guard like this one.

### in practice

A joint controller enables motor torque before running a trajectory. If the trajectory code throws (a planner exception, a bad sensor reading, an allocation failure), the motors must not be left energized.

```cpp
class TorqueEnable {
public:
    explicit TorqueEnable(MotorBus& bus) : bus_(bus) { bus_.enable_all(); }
    ~TorqueEnable() { bus_.disable_all(); }   // must not throw
    TorqueEnable(const TorqueEnable&) = delete;
    TorqueEnable& operator=(const TorqueEnable&) = delete;
private:
    MotorBus& bus_;
};

void run_trajectory(MotorBus& bus, const Trajectory& t) {
    TorqueEnable power{bus};
    for (const auto& setpoint : t) step(bus, setpoint);   // may throw
}   // torque off on every exit path that unwinds
```

Notice what RAII does not cover. If the process segfaults, is killed, or hits an uncaught exception on an implementation that does not unwind, `disable_all` never runs. For anything safety-relevant, RAII is the software layer; a hardware watchdog that cuts torque when the heartbeat stops is the layer below it. Good engineering uses both, and knows which failure each one handles.

Copying is deleted here deliberately. Two `TorqueEnable` objects for one bus would disable it twice, the first time too early. Whether an RAII type should be copyable, movable, or neither is a design decision about ownership; days 10 and 11 cover how to make it.

### watch out for

**Release can fail, and a destructor cannot report it.** `fclose` on a file you wrote may flush buffered data and fail (disk full, network filesystem gone). The `FileCloser` above silently drops that error. For read-only handles that is fine. For writes, give the class an explicit `close()` that returns or throws an error, call it on the success path, and let the destructor be the fallback that cleans up quietly (perhaps logging) when an earlier failure already happened.

**An unnamed guard guards nothing.**

```cpp
std::lock_guard<std::mutex>{mtx_};           // BUG: temporary, unlocked at the ;
std::lock_guard<std::mutex> lock{mtx_};      // held until end of scope
```

The first line creates a temporary that dies at the end of the full-expression (day 03), so the critical section is empty. GCC 12 compiles it without a word under `-Wall -Wextra`. The same applies to `ScopeGuard{...};`. Always give guards a name.

### the takeaway

If something must happen when a scope ends, put it in a destructor. Then every exit path, including the ones someone adds next year, gets it for free.

### optional challenge

Predict the output, then predict what changes if you delete the `try`/`catch` in `main`.

```cpp
#include <cstdio>
#include <stdexcept>

struct Noisy {
    const char* name;
    ~Noisy() { std::puts(name); }
};

void work() {
    Noisy a{"a"};
    Noisy b{"b"};
    throw std::runtime_error("sensor timeout");
}

int main() {
    try { work(); }
    catch (const std::exception& e) { std::puts(e.what()); }
}
```

<details>
<summary>answer</summary>

With the handler, the stack unwinds to `main` before the `catch` body runs, so you see `b`, `a`, then `sensor timeout`. Destruction is in reverse order of construction, and the destructors run before the handler.

Without the handler, no matching `catch` exists, so `std::terminate` is called. Whether `b` and `a` are destroyed first is implementation-defined. With GCC on Linux and MinGW you typically see neither line, just the terminate message and an abort. This is one reason long-running services catch exceptions at the top of `main` and at the top of every thread function: it guarantees that unwinding, and therefore your RAII cleanup, actually happens.

</details>
