---
title: ownership in function signatures
standard: C++17
objective: choose parameter and return types that state whether a function borrows, takes, shares, or creates ownership
prerequisites: shared-ptr, const-correctness
difficulty: 2
---

### the idea

read this signature and tell me who deletes the track:

```cpp
void register_track(Track* t);
```

you cannot. maybe the registry keeps it and deletes it later, maybe it only reads it during the call, maybe it keeps it but expects you to keep it alive. the type says nothing, so the answer lives in a comment, a wiki, or someone's memory. smart pointers are RAII for heap objects, but their bigger contribution is that they turn ownership into part of the type, where the compiler can check it and a reviewer can see it.

### understanding the concept

the C++ Core Guidelines turn ownership into a small vocabulary of types, and the rule behind it is simple: **a raw pointer or reference never owns**. it borrows, for at most as long as the call (or as long as a documented relationship lasts). everything that transfers or shares ownership says so with a smart pointer:

- **returning ownership:** factories return `std::unique_ptr<T>` (or a value). a caller that wants shared ownership can convert it: a `shared_ptr` constructs from a `unique_ptr&&`.
- **taking ownership:** a sink parameter is `std::unique_ptr<T>` by value. the caller must write `std::move`, so the transfer is visible at the call site.
- **sharing ownership:** `std::shared_ptr<T>` by value, only when the callee keeps a share beyond the call.
- **borrowing:** `T&` or `const T&` when the object must exist, `T*` when "nothing" is allowed. smart pointers in a parameter list for a function that merely uses the object add cost and constrain every caller.

### in code

ownership written into signatures, following the C++ Core Guidelines:

```cpp complete
#include <memory>

struct Config; struct Map;
struct Detector { virtual ~Detector() = default; virtual void run() = 0; };

std::unique_ptr<Detector> make_detector(const Config& cfg);  // gives you ownership
void install(std::unique_ptr<Detector> d);                   // takes ownership
void share(std::shared_ptr<const Map> m);                    // keeps a share
void inspect(const Detector& d);                             // uses, never owns
void maybe_inspect(const Detector* d);                       // uses; may be null

void setup(const Config& cfg) {
    auto d = make_detector(cfg);
    inspect(*d);                 // borrow: no ownership in the signature
    install(std::move(d));       // transfer: visible at the call site
}
```

| parameter | meaning |
|---|---|
| `T&`, `const T&`, `T*` | borrows for the duration of the call; ownership untouched |
| `std::unique_ptr<T>` by value | sink: the callee now owns it |
| `std::unique_ptr<T>&` | the callee may reseat or reset your pointer (rare) |
| `std::shared_ptr<T>` by value | the callee keeps a share (stores it, or hands it to a thread) |
| `const std::shared_ptr<T>&` | the callee *might* keep a share; otherwise just use `T&` |

the most common mistake in that table is the last row used everywhere. a function that only reads a `Map` should take `const Map&`. taking `shared_ptr` by value costs an atomic increment and decrement per call, and worse, it couples every caller to one particular ownership strategy.

### in practice

legacy interfaces rarely say who owns what, and changing their types is the cheapest documentation you can add. take `void register_track(Track* t);` from the opening. once you have established (by reading the implementation) that the registry keeps the track and deletes it later, change the signature to `void register_track(std::unique_ptr<Track> t);`. every caller that compiled before now fails to compile until it writes `register_track(std::move(track))` or `register_track(std::make_unique<Track>(...))`, which forces each one to show that it is handing the track over. the compiler does the audit you would otherwise do by reading every call site, and the result stays correct when new callers appear.

### watch out for

**a borrowed pointer that is quietly stored.** a reference or raw pointer parameter promises "I only use this during the call". storing it breaks the promise without changing the signature:

```cpp
class Monitor {
public:
    void watch(const Detector& d) { watched_ = &d; }   // stores a borrow
    void tick() { if (watched_) report(*watched_); }   // may run after d is gone
private:
    const Detector* watched_ = nullptr;
};
```

if the function keeps the object, the parameter type should say how: a `shared_ptr` if it shares ownership, or a reference plus a documented lifetime rule ("the detector must outlive the monitor") enforced by the code that wires them together. a long-lived raw pointer with no stated lifetime is a dangling pointer waiting for a refactor.

### the takeaway

default to `unique_ptr` for ownership and plain references for use; reach for `shared_ptr` only when ownership is genuinely shared, and let every signature say which one it is.

### optional challenge

choose parameter types for each function: (a) logs a detector's name; (b) adds a detector to a registry that keeps it forever; (c) starts a background thread that reads a map for as long as the thread runs; (d) may replace the caller's detector with a recalibrated one.

<details>
<summary>answer</summary>

(a) `const Detector&`: it only reads during the call. (b) `std::unique_ptr<Detector>` by value: a sink, and the call site shows the transfer. (c) `std::shared_ptr<const Map>` by value: the thread keeps a share, so the map cannot disappear underneath it, and `const` makes the concurrent reads safe. (d) `std::unique_ptr<Detector>&`, the rare case where the callee reseats the caller's pointer; returning a new `std::unique_ptr<Detector>` is often clearer.

</details>
