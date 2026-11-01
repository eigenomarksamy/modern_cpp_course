---
title: coroutines: functions that suspend
standard: C++20
objective: read and use a coroutine that yields values, explain where its state lives, and avoid parameters that dangle across suspension points
prerequisites: raii, temporaries-dangling, lambdas
difficulty: 3
---

### the idea

a radar steers its beam in a serpentine raster: left to right on even rows, right to left on odd rows. as an iterator, that needs the row, the column, and the direction stored as members, plus an `increment()` that reconstructs where the two nested loops were. as a coroutine, it is two nested loops with a `co_yield` in the middle. coroutines let a function pause and resume, so a state machine can be written as straight-line code, and the compiler keeps the state for you.

### understanding the concept

**coroutines.** a function becomes a coroutine when its body uses `co_await`, `co_yield`, or `co_return`. its state (the parameters, the locals that live across a suspension, and a *promise object*) lives in a **coroutine frame**, which is usually heap-allocated; the compiler may elide that allocation when it can prove the frame's lifetime is nested in the caller's, but nothing guarantees it. C++20 supplies only the machinery: the return type must provide a nested `promise_type` that tells the compiler what to do at start, at each `co_yield`, at the end, and on exceptions. the standard ships no ready-made generator or task type in C++20 (`std::generator` arrives in C++23).

`co_await x` asks an *awaiter* three questions: `await_ready()` (can we skip suspending?), `await_suspend(handle)` (we are suspended; who resumes us, and when?), and `await_resume()` (the result of the expression). `std::suspend_always` and `std::suspend_never` are the two trivial awaiters.

### in code

`Generator<T>` below is a small generator type; [[coroutine-generator]] builds it line by line. using it looks like this:

```cpp
#include <iostream>

struct Beam { int elevation, azimuth; };

Generator<Beam> serpentine_scan(int rows, int cols) {    // parameters copied into the frame
    for (int el = 0; el < rows; ++el) {
        const bool forward = (el % 2 == 0);
        for (int i = 0; i < cols; ++i)
            co_yield Beam{el, forward ? i : cols - 1 - i};
    }
}

int main() {
    auto scan = serpentine_scan(2, 3);
    while (scan.next())
        std::cout << '(' << scan.value().elevation << ',' << scan.value().azimuth << ") ";
    // prints: (0,0) (0,1) (0,2) (1,2) (1,1) (1,0)
}
```

as an iterator class this needs `el`, `i`, and `forward` as members plus an `increment()` that reconstructs where the loops were. the coroutine keeps that state in its frame and lets the nested loops stay nested loops.

### in practice

**coroutines today.** they shine for asynchronous I/O (a telemetry uploader written as `co_await socket.async_write(...)` in sequence instead of nested callbacks), protocol state machines, and lazy sequences. in practice you use a library's types: Asio's `awaitable`, folly's coro, or the generator in your toolchain's C++23 mode. writing your own `task` type with correct continuation, cancellation, and thread handoff is much harder than the generator above.

### watch out for

**reference parameters dangle across suspension points.** the frame copies parameters, but copying a reference copies the reference.

```cpp
Generator<char> letters(const std::string& s) { for (char c : s) co_yield c; }

auto g = letters("radar");   // BUG: the temporary std::string dies at the end of this line
while (g.next()) { }         // undefined behavior: the frame refers to a destroyed string
```

the fix is to take the parameter by value (`std::string s`), so the frame owns a copy. the same applies to `std::string_view`, `std::span`, and lambda coroutines: a lambda's captures live in the lambda object, not the frame, so the lambda object must outlive the coroutine it started.

### the takeaway

a coroutine keeps its state in a frame that outlives each suspension, so take parameters by value, let an RAII return type own the frame, and use a library's coroutine types for asynchronous work.

### optional challenge

`auto scan = serpentine_scan(rows, cols);` is called with two local `int` variables, and the caller then changes `rows` before calling `scan.next()`. does the scan see the new value?

<details>
<summary>answer</summary>

no. parameters of a coroutine are copied (or moved) into the coroutine frame when it is called, and the body uses those copies. because the parameters are taken by value, later changes to the caller's variables do not affect the scan. had they been `const int&`, the frame would hold references to the caller's variables: the scan would see the change, and if those variables went out of scope before the scan finished, it would read dangling references.

</details>
