---
title: RAII: let scope do the cleanup
standard: C++17
objective: tie a resource's lifetime to an object so every exit path releases it, and know which exits skip destructors
prerequisites: storage-duration, undefined-behavior
difficulty: 2
---

### the idea

here is a function that reads a calibration header from a file. it has three exits, and every one of them must remember `fclose`. six months later someone adds a call that can throw, and now there is a fourth exit that nobody wrote down.

that is the whole problem RAII solves. cleanup that depends on every author remembering every exit path will eventually be forgotten. cleanup that the language performs whenever a scope ends cannot be forgotten, because nobody has to remember it.

### understanding the concept

RAII (resource acquisition is initialization; the name is famously bad) means: tie a resource to the lifetime of an object. the constructor acquires the resource, or throws if it cannot. the destructor releases it. you then lean on the lifetime rules from [[storage-duration]]: an object with automatic storage duration is destroyed when control leaves its scope, in reverse order of construction, however control leaves.

"however control leaves" is the important part. normal fall-through, `return`, `break`, `continue`, `goto` out of a block, and an exception propagating to a handler all run the destructors of the automatic objects being left. during exception propagation this is called stack unwinding: each frame between the `throw` and the matching `catch` is torn down, destructors included.

a few exits do not run destructors, and you should know them:

- `std::exit` destroys static objects but not the automatic objects on the stack.
- `std::abort`, `std::_Exit`, a crash, and `kill -9` destroy nothing.
- if an exception is never caught, `std::terminate` is called, and **whether the stack is unwound first is implementation-defined**. GCC and Clang typically do not unwind in that case, so your destructors may not run.

the deeper idea is an invariant: **if the object exists, the resource is valid**. a `File` object that exists holds an open file. there is no "not yet opened" or "already closed" state for every caller to check. that is encapsulation in its most useful form: the class owns a rule, and no caller can break it.

### in code

first, the naive version. it is correct today and fragile tomorrow.

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

the RAII version moves the cleanup into a type. you rarely need a hand-written class for a C handle: `std::unique_ptr` with a custom deleter is already a general RAII wrapper.

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

two details. `unique_ptr` never calls the deleter on a null pointer, so a failed `fopen` is handled for free. and the deleter is a function object rather than `&std::fclose`: since C++20, forming a pointer to most standard library functions is unspecified (possibly ill-formed), and an empty function object also lets the `unique_ptr` stay pointer-sized (more on that on [[unique-ptr]]).

### in practice

a joint controller enables motor torque before running a trajectory. if the trajectory code throws (a planner exception, a bad sensor reading, an allocation failure), the motors must not be left energized.

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

notice what RAII does not cover. if the process segfaults, is killed, or hits an uncaught exception on an implementation that does not unwind, `disable_all` never runs. for anything safety-relevant, RAII is the software layer; a hardware watchdog that cuts torque when the heartbeat stops is the layer below it. good engineering uses both, and knows which failure each one handles.

copying is deleted here deliberately. two `TorqueEnable` objects for one bus would disable it twice, the first time too early. whether an RAII type should be copyable, movable, or neither is a design decision about ownership; [[copy-semantics]] and [[special-members]] cover how to make it.

### watch out for

**destructors must not throw, and release can fail anyway.**

destructors are implicitly `noexcept` (since C++11), unless a base or member has a potentially-throwing destructor. if an exception escapes a `noexcept` destructor, `std::terminate` is called. even a destructor explicitly marked `noexcept(false)` that throws while the stack is already unwinding because of another exception calls `std::terminate`. treat "destructors do not throw" as a hard rule.

**release can fail, and a destructor cannot report it.** `fclose` on a file you wrote may flush buffered data and fail (disk full, network filesystem gone). the `FileCloser` above silently drops that error. for read-only handles that is fine. for writes, give the class an explicit `close()` that returns or throws an error, call it on the success path, and let the destructor be the fallback that cleans up quietly (perhaps logging) when an earlier failure already happened.

### the takeaway

if something must happen when a scope ends, put it in a destructor. then every exit path, including the ones someone adds next year, gets it for free.

### optional challenge

predict the output, then predict what changes if you delete the `try`/`catch` in `main`.

```cpp complete
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

with the handler, the stack unwinds to `main` before the `catch` body runs, so you see `b`, `a`, then `sensor timeout`. destruction is in reverse order of construction, and the destructors run before the handler.

without the handler, no matching `catch` exists, so `std::terminate` is called. whether `b` and `a` are destroyed first is implementation-defined. with GCC on Linux and MinGW you typically see neither line, just the terminate message and an abort. this is one reason long-running services catch exceptions at the top of `main` and at the top of every thread function: it guarantees that unwinding, and therefore your RAII cleanup, actually happens.

</details>
