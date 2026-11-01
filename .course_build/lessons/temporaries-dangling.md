---
title: temporaries, lifetime extension, and dangling references
standard: C++17
objective: predict when a temporary dies, apply the one rule that extends its life, and spot references that outlive their objects
prerequisites: storage-duration
difficulty: 2
---

### the idea

`for (int d : load_frame().detections())` compiles cleanly, passes code review, and iterates a vector that has already been destroyed. temporaries are the objects you never named: function results, conversions, the result of `a + b`. their lifetime rule is short enough to memorize, and its one exception is narrower than most people assume.

### understanding the concept

a temporary object is destroyed at the end of the **full-expression** that created it: the outermost expression that is not part of another one, which in practice usually means at the `;`. everything inside the expression can use the temporary safely; a reference or pointer that escapes the expression cannot.

**lifetime extension.** when a temporary is bound *directly* to a `const T&` or `T&&` local reference, the temporary lives as long as the reference. "directly" includes a member accessed on a temporary (`make_frame().ids`). it does not include anything that passes through a function returning a reference, because the compiler cannot see what that reference refers to. also, a temporary bound to a function's reference parameter only lives until the end of the full-expression containing the call, and a temporary bound to the return value in a `return` statement is not extended at all.

### in code

**dangling: a reference to a local, and a range-for over a temporary.**

```cpp ub
#include <string>
#include <vector>

const std::string& frame_id() {
    std::string id = "base_link";
    return id;                // BUG: the reference outlives id (GCC: -Wreturn-local-addr)
}

struct Frame {
    std::vector<int> ids;
    const std::vector<int>& detections() const { return ids; }
};
Frame load_frame();
void consume(int);

void process() {
    for (int d : load_frame().detections()) consume(d);   // BUG: UB in C++17 and C++20
    for (int d : load_frame().ids) consume(d);            // fine: member of a temporary, extended
}
```

the range-for is the subtle one. it expands to roughly `auto&& range = load_frame().detections();` followed by the loop. `detections()` returns a reference, so the `Frame` temporary is not extended; it dies at the end of that hidden declaration and the loop iterates a destroyed vector. GCC 12 gave no warning for it. C++23 extends the lifetime of all temporaries in the range-for initializer, which fixes this exact case, but in C++17 and C++20 it is undefined behavior. the portable fix is to name the object first: `auto frame = load_frame(); for (int d : frame.detections())`.

### in practice

getters that return references are a common performance habit, and they are only safe when the caller holds the object they point into. in a robotics stack, `robot_state()` might return a snapshot *by value*, copied out from under a mutex. then `const Pose& pose = robot_state().pose();` binds to a member of a temporary that dies at the `;`, and every later read of `pose` is undefined behavior that usually still "works" in tests. the fix at the call site is to name the snapshot: `auto state = robot_state();` and read `state.pose()` from it. the design rule behind it: functions that produce a new object return it by value; only accessors on objects the caller already owns return references. AddressSanitizer (`-fsanitize=address`) reports most of these as `heap-use-after-free` or `stack-use-after-scope` the first time a test exercises the path.

### watch out for

lifetime extension does not pass through function calls, and the classic victim is a standard algorithm returning a reference:

```cpp ub
#include <algorithm>

int lo();
int hi();

const int& m = std::max(lo(), hi());   // BUG: dangles
int v = std::max(lo(), hi());          // fine: copied before the ';'
```

`std::max` takes `const int&` parameters and returns one of them. the two temporaries are bound to its parameters, so they live only until the end of the full-expression, and `m` is left referring to a dead temporary. in our test at `-O2`, GCC printed `0` for `m` (and, by luck, warned about an uninitialized read). GCC 13 added `-Wdangling-reference` for this pattern; GCC 12 has nothing specific. the defense is a habit: bind function results by value unless you know the function returns a reference to something that outlives your reference.

### the takeaway

temporaries die at the `;` unless they are bound *directly* to a local reference; a reference that comes back out of a function call extends nothing, so bind function results by value unless you know what the reference points into.

### optional challenge

`load()` returns a `Frame` by value. which of these three lines leave a dangling reference?

```cpp
struct Frame {
    std::vector<int> ids;
    const std::vector<int>& get() const { return ids; }
};
Frame load();

const auto& a = load().ids;     // (1)
const auto& b = load().get();   // (2)
auto c = load().get();          // (3)
```

<details>
<summary>answer</summary>

only (2). in (1) the reference binds directly to a member subobject of the temporary, so the whole `Frame` temporary is extended to `a`'s lifetime. in (2) the reference comes back through a member function; the compiler does not extend anything, the `Frame` dies at the `;`, and `b` dangles. in (3) `c` is a copy of the vector (`auto` deduces `std::vector<int>`), made while the temporary is still alive, so it is safe and owns its own data.

</details>
