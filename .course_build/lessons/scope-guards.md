---
title: scope guards: cleanup without a new class
standard: C++17
objective: use a scope guard for one-off cleanup and commit-or-rollback logic, and avoid the unnamed-guard trap
prerequisites: raii
difficulty: 1
---

### the idea

not every cleanup deserves its own class. restoring a flag after a calibration routine, unregistering a callback, rolling back the first two steps of a three-step configuration change when the third fails: each happens once, in one function, and still has to happen on every exit path. writing a dedicated RAII type for each is ceremony; writing the cleanup by hand at every `return` is the bug RAII exists to prevent. a scope guard sits in between.

### understanding the concept

you already use this pattern every day: `std::lock_guard` locks in its constructor and unlocks in its destructor, `std::vector` frees its buffer, `std::ifstream` closes its file. for one-off cleanup that does not deserve its own type, a scope guard turns any callable into a destructor. C++17 class template argument deduction (CTAD) means you never spell out the lambda's type:

a scope guard is a tiny RAII type whose "resource" is an arbitrary callable. its destructor runs the callable unless the guard has been *dismissed*. that one extra bit of state gives two useful shapes:

- **always run:** arm the guard right after acquiring something, and the cleanup runs however the scope ends.
- **commit or roll back:** arm a rollback before a multi-step change, and dismiss it after the last step succeeds. if anything throws or returns early, the destructor undoes the partial work.

### in code

```cpp complete
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

reverse order of construction, as [[storage-duration]] promised. `dismiss` gives you the commit-or-rollback shape: arm a rollback before a multi-step operation and disarm it once the last step succeeds. the library fundamentals TS has `scope_exit`, `scope_fail`, and `scope_success`, but they are not in the C++17 or C++20 standard library, so most codebases carry a guard like this one.

### in practice

applying a new configuration to a running sensor driver touches several pieces of state, and a half-applied configuration is worse than the old one:

```cpp
void Driver::apply(const Config& next) {
    const Config previous = config_;
    ScopeGuard rollback{[&] { config_ = previous; push_to_hardware(config_); }};

    config_ = next;
    push_to_hardware(config_);   // may throw: device rejected a register write
    restart_streams();           // may throw: stream did not come back
    rollback.dismiss();          // every step succeeded: keep the new config
}
```

the rollback lambda captures by reference, which is safe here because the guard cannot outlive the function's locals. the order of the code now reads like the intent: remember, arm the undo, do the work, commit. note that the rollback itself calls `push_to_hardware`, which can throw; a destructor that throws during unwinding terminates the program, so a production guard would catch and log inside the rollback.

### watch out for

**an unnamed guard guards nothing.**

```cpp
std::lock_guard<std::mutex>{mtx_};           // BUG: temporary, unlocked at the ;
std::lock_guard<std::mutex> lock{mtx_};      // held until end of scope
```

the first line creates a temporary that dies at the end of the full-expression ([[storage-duration]]), so the critical section is empty. GCC 12 compiles it without a word under `-Wall -Wextra`. the same applies to `ScopeGuard{...};`. always give guards a name.

### the takeaway

when cleanup or rollback is needed once, in one place, arm a named scope guard next to the code that creates the need, and dismiss it at the point of commit.

### optional challenge

a function locks a mutex with `std::lock_guard<std::mutex> lock{m};` and then arms `ScopeGuard g{[&] { log_state(); }};`, where `log_state()` reads data protected by `m`. when the function returns, is the data still protected while `log_state()` runs?

<details>
<summary>answer</summary>

yes. automatic objects are destroyed in reverse order of construction, so `g` (constructed second) runs its callable first, while `lock` still holds the mutex, and only then is `lock` destroyed. if the declarations were swapped, the mutex would be released before `log_state()` ran, and the read would race with other threads. with several guards in one scope, the declaration order *is* the cleanup order, so declare them in the order of acquisition.

</details>
