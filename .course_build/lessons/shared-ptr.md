---
title: shared ownership with `std::shared_ptr` and `std::weak_ptr`
standard: C++17
objective: use shared_ptr only for genuinely shared ownership, break cycles with weak_ptr, and know exactly what is and is not thread-safe
prerequisites: unique-ptr
difficulty: 2
---

### the idea

a map is loaded once and used by the planner, the visualizer, and a logging thread. any of them may be the last to finish with it, and the map must be freed exactly when that happens, not before and not never. when no single object can be the owner, ownership has to be counted. `std::shared_ptr` counts it for you, and in doing so introduces costs and failure modes that `std::unique_ptr` does not have.

### understanding the concept

**`std::shared_ptr<T>`** is shared ownership via a reference count. the count lives in a separately allocated *control block* along with a weak count, the deleter, and the allocator. a `shared_ptr` object is typically two pointers (object and control block). copying it increments the strong count; the last owner to go away destroys the object. the counts are updated atomically, so different `shared_ptr` objects that share one control block may be copied and destroyed on different threads. that is the only thread-safety it gives you; more in "watch out for".

`std::make_shared<T>(args...)` puts the object and the control block in one allocation instead of two. the catch: the memory can only be freed when both counts reach zero, so a long-lived `weak_ptr` keeps a large object's storage allocated after its destructor has run. `make_shared` also cannot take a custom deleter.

**`std::weak_ptr<T>`** observes a shared object without owning it. it touches only the weak count. to use the object you call `lock()`, which returns a `shared_ptr` that is empty if the object is gone. that check-and-acquire is atomic, which is why `weak_ptr` has no `get()`.

**`std::enable_shared_from_this<T>`** lets an object that is already owned by a `shared_ptr` produce another `shared_ptr` to itself (`shared_from_this()`), sharing the existing control block. since C++17, calling it on an object no `shared_ptr` owns throws `std::bad_weak_ptr` (it used to be undefined behavior).

### in code

shared ownership in both directions is a leak:

```cpp complete norun
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

reference counting cannot collect cycles. each object keeps the other's count above zero, so when `robot` and `j` go out of scope, both objects leak. the fix is to decide which direction owns. a robot owns its joints; a joint merely refers back to its robot:

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

often the even simpler fix is better: if a joint can never outlive its robot, `Robot* owner` (or `Robot&`) states that precisely and costs nothing. `weak_ptr` is for when the referenced object really might disappear first.

### in practice

a perception stack loads large meshes and maps on demand, and several subsystems may use the same one. you want each loaded once, shared while in use, and released when nobody needs it, without the cache itself keeping everything alive forever. that is exactly what `weak_ptr` expresses:

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

two design notes. `shared_ptr<const Mesh>` makes the shared object immutable, which is what makes sharing it across subsystems and threads safe. and `make_shared` is a questionable choice here: an expired entry's `weak_ptr` pins the whole allocation, mesh storage included, until the entry is overwritten or erased. with large objects and long-lived weak references, `std::shared_ptr<const Mesh>(new Mesh(...))` keeps the object and control block separate so the mesh memory goes back as soon as the last user lets go. (a production cache would also prune expired entries.)

### watch out for

**thread-safe count, not thread-safe object.** two threads may each copy and destroy their own `shared_ptr` to the same object freely. but the pointee gets no protection at all: concurrent writes to `*p` are a data race unless you synchronize them. and one `shared_ptr` *instance* read and assigned by two threads at once is also a data race (undefined behavior); C++20's `std::atomic<std::shared_ptr<T>>` exists for that case.

**one raw pointer, two control blocks.**

```cpp
auto* raw = new Track{};
std::shared_ptr<Track> a(raw);
std::shared_ptr<Track> b(raw);   // BUG: second control block, double delete (UB)
```

each constructor from a raw pointer creates a fresh control block with its own count. the same bug hides in `std::shared_ptr<Session>(this)` inside a member function, which is exactly the problem `enable_shared_from_this` solves. create shared objects with `make_shared` at the point of allocation and never hand raw ownership around.

more broadly, treat widespread `shared_ptr` as a smell. "everything is shared" usually means nobody decided who owns what, and the cost shows up as unclear lifetimes, destructors running on whichever thread happened to drop the last reference, and cycles. most objects have one obvious owner.

### the takeaway

`shared_ptr` is for ownership that is genuinely shared; its count is thread-safe and its pointee is not, reference cycles leak, and most objects have one owner and should say so with `unique_ptr`.

### optional challenge

what does this print, and when is the `int`'s memory actually freed?

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

it prints `2 1 0 1`. after `b = a` there are two owners. `a.reset()` leaves one, so the object is alive (`expired()` is false). `b.reset()` drops the last strong reference: the `int` is destroyed and `w` reports expired.

the memory is not freed at that point. `make_shared` put the `int` and the control block in one allocation, and `w` still needs the control block (it holds the weak count). the block, including the dead `int`'s storage, is released when `w` is destroyed. for an `int` that is irrelevant; for a 200 MB point cloud observed by a long-lived `weak_ptr`, it is the difference between memory coming back now and memory coming back much later.

</details>
