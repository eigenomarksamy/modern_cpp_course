<a id="day-12"></a>

## day 12: smart pointers and ownership in interfaces

**reading time:** about 10 minutes · **standard:** C++17 · **builds on:** days 04, 08, 10, 11

### the idea

Read this signature and tell me who deletes the track:

```cpp
void register_track(Track* t);
```

You cannot. Maybe the registry keeps it and deletes it later, maybe it only reads it during the call, maybe it keeps it but expects you to keep it alive. The type says nothing, so the answer lives in a comment, a wiki, or someone's memory. Smart pointers are RAII for heap objects, but their bigger contribution is that they turn ownership into part of the type, where the compiler can check it and a reviewer can see it.

### understanding the concept

**`std::unique_ptr<T>`** is sole ownership: move-only (day 11), deletes the object in its destructor. With the default deleter, or any empty function-object deleter, it is typically the same size as a raw pointer, and `get()` and `operator->` compile down to the raw pointer. A stateful deleter costs its size: a function-pointer deleter typically doubles the `unique_ptr`. Create one with `std::make_unique<T>(args...)` (C++14). Before C++17, `make_unique` also prevented a leak in `f(std::unique_ptr<A>(new A), g())`, because the compiler could run `new A`, then `g()`, before constructing the `unique_ptr`. C++17 forbids that interleaving (each argument is fully evaluated before the next one starts), but `make_unique` is still the better spelling: no naked `new`, and the type is written once.

**`std::shared_ptr<T>`** is shared ownership via a reference count. The count lives in a separately allocated *control block* along with a weak count, the deleter, and the allocator. A `shared_ptr` object is typically two pointers (object and control block). Copying it increments the strong count; the last owner to go away destroys the object. The counts are updated atomically, so different `shared_ptr` objects that share one control block may be copied and destroyed on different threads. That is the only thread-safety it gives you; more in "watch out for".

`std::make_shared<T>(args...)` puts the object and the control block in one allocation instead of two. The catch: the memory can only be freed when both counts reach zero, so a long-lived `weak_ptr` keeps a large object's storage allocated after its destructor has run. `make_shared` also cannot take a custom deleter.

**`std::weak_ptr<T>`** observes a shared object without owning it. It touches only the weak count. To use the object you call `lock()`, which returns a `shared_ptr` that is empty if the object is gone. That check-and-acquire is atomic, which is why `weak_ptr` has no `get()`.

**`std::enable_shared_from_this<T>`** lets an object that is already owned by a `shared_ptr` produce another `shared_ptr` to itself (`shared_from_this()`), sharing the existing control block. Since C++17, calling it on an object no `shared_ptr` owns throws `std::bad_weak_ptr` (it used to be undefined behavior).

### in code

Ownership written into signatures, following the C++ Core Guidelines:

```cpp
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

The most common mistake in that table is the last row used everywhere. A function that only reads a `Map` should take `const Map&`. Taking `shared_ptr` by value costs an atomic increment and decrement per call, and worse, it couples every caller to one particular ownership strategy.

Shared ownership in both directions is a leak:

```cpp
#include <cstdio>
#include <memory>
#include <vector>

struct Joint;
struct Robot {
    std::vector<std::shared_ptr<Joint>> joints;
    ~Robot() { std::puts("~Robot"); }
};
struct Joint {
    std::shared_ptr<Robot> owner;          // BUG: cycle: Robot -> Joint -> Robot
    ~Joint() { std::puts("~Joint"); }
};

int main() {
    auto robot = std::make_shared<Robot>();
    auto j = std::make_shared<Joint>();
    j->owner = robot;
    robot->joints.push_back(j);
}   // prints nothing: both counts stay at 1, neither destructor runs
```

Reference counting cannot collect cycles. Each object keeps the other's count above zero, so when `robot` and `j` go out of scope, both objects leak. The fix is to decide which direction owns. A robot owns its joints; a joint merely refers back to its robot:

```cpp
struct Joint {
    std::weak_ptr<Robot> owner;            // back-reference: does not own
    void report() const {
        if (auto r = owner.lock()) { /* use *r */ }   // empty if the robot is gone
    }
    ~Joint() { std::puts("~Joint"); }
};
// now prints: ~Robot, then ~Joint
```

Often the even simpler fix is better: if a joint can never outlive its robot, `Robot* owner` (or `Robot&`) states that precisely and costs nothing. `weak_ptr` is for when the referenced object really might disappear first.

### in practice

A perception stack loads large meshes and maps on demand, and several subsystems may use the same one. You want each loaded once, shared while in use, and released when nobody needs it, without the cache itself keeping everything alive forever. That is exactly what `weak_ptr` expresses:

```cpp
#include <map>
#include <memory>
#include <mutex>
#include <string>

class MeshCache {
public:
    std::shared_ptr<const Mesh> get(const std::string& path) {
        std::lock_guard<std::mutex> lock(mtx_);
        if (auto alive = cache_[path].lock()) return alive;   // still in use somewhere
        auto fresh = std::make_shared<const Mesh>(load_mesh(path));
        cache_[path] = fresh;                                 // observe, do not own
        return fresh;
    }
private:
    std::mutex mtx_;
    std::map<std::string, std::weak_ptr<const Mesh>> cache_;
};
```

Two design notes. `shared_ptr<const Mesh>` makes the shared object immutable, which is what makes sharing it across subsystems and threads safe. And `make_shared` is a questionable choice here: an expired entry's `weak_ptr` pins the whole allocation, mesh storage included, until the entry is overwritten or erased. With large objects and long-lived weak references, `std::shared_ptr<const Mesh>(new Mesh(...))` keeps the object and control block separate so the mesh memory goes back as soon as the last user lets go. (A production cache would also prune expired entries.)

### watch out for

**Thread-safe count, not thread-safe object.** Two threads may each copy and destroy their own `shared_ptr` to the same object freely. But the pointee gets no protection at all: concurrent writes to `*p` are a data race unless you synchronize them. And one `shared_ptr` *instance* read and assigned by two threads at once is also a data race (undefined behavior); C++20's `std::atomic<std::shared_ptr<T>>` exists for that case.

**One raw pointer, two control blocks.**

```cpp
auto* raw = new Track{};
std::shared_ptr<Track> a(raw);
std::shared_ptr<Track> b(raw);   // BUG: second control block, double delete (UB)
```

Each constructor from a raw pointer creates a fresh control block with its own count. The same bug hides in `std::shared_ptr<Session>(this)` inside a member function, which is exactly the problem `enable_shared_from_this` solves. Create shared objects with `make_shared` at the point of allocation and never hand raw ownership around.

More broadly, treat widespread `shared_ptr` as a smell. "Everything is shared" usually means nobody decided who owns what, and the cost shows up as unclear lifetimes, destructors running on whichever thread happened to drop the last reference, and cycles. Most objects have one obvious owner.

### the takeaway

Default to `unique_ptr` for ownership and plain references for use; reach for `shared_ptr` only when ownership is genuinely shared, and let every signature say which one it is.

### optional challenge

What does this print, and when is the `int`'s memory actually freed?

```cpp
auto a = std::make_shared<int>(7);
std::weak_ptr<int> w = a;
auto b = a;
std::printf("%ld ", a.use_count());
a.reset();
std::printf("%ld %d ", w.use_count(), w.expired());
b.reset();
std::printf("%d\n", w.expired());
```

<details>
<summary>answer</summary>

It prints `2 1 0 1`. After `b = a` there are two owners. `a.reset()` leaves one, so the object is alive (`expired()` is false). `b.reset()` drops the last strong reference: the `int` is destroyed and `w` reports expired.

The memory is not freed at that point. `make_shared` put the `int` and the control block in one allocation, and `w` still needs the control block (it holds the weak count). The block, including the dead `int`'s storage, is released when `w` is destroyed. For an `int` that is irrelevant; for a 200 MB point cloud observed by a long-lived `weak_ptr`, it is the difference between memory coming back now and memory coming back much later.

</details>
