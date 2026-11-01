---
title: `std::thread`: starting, joining, and passing arguments
standard: C++17
objective: start and join threads safely, explain why a joinable `std::thread` terminates the program on destruction, and pass arguments without dangling
prerequisites: raii, construction-order, callbacks
difficulty: 2
---

### the idea

you have a sensor driver that polls an IMU every 10 ms on its own thread. starting the thread is one line. stopping it correctly, on every path including exceptions and early returns, is where the bugs live. if a `std::thread` object is destroyed while it still represents a running thread, your process does not leak or hang: it calls `std::terminate`. sharing data between threads comes later; it starts with owning threads safely.

### understanding the concept

a `std::thread` is a handle that owns at most one thread of execution. constructing it with a callable starts the thread; the standard says the end of the constructor *synchronizes with* the start of the callable, so everything the parent did before constructing the thread is visible inside it. when the thread finishes, its completion synchronizes with the return of `join()`, so everything the thread did is visible after `join` returns. we will make "synchronizes with" precise on [[memory-model]]; for now, `join` is your visibility guarantee.

a thread object is *joinable* if it still owns a thread. it stops being joinable after `join()`, `detach()`, or being moved from. destroying (or move-assigning to) a joinable `std::thread` calls `std::terminate`. that sounds harsh, but both alternatives were worse: an implicit `join` can hang a destructor forever, and an implicit `detach` lets the thread keep running with references to locals that are gone.

`detach()` is rarely right. a detached thread cannot be waited for, so you cannot know when it has stopped touching your objects. at process exit, static objects are destroyed while a detached thread may still be running, and any access to an object after its lifetime ends is UB. use `detach` only for work that touches nothing but its own copies, and even then, ask what happens at shutdown.

arguments are *decay-copied* into storage owned by the new thread, in the constructing thread, and then passed to the callable as rvalues. two consequences follow. a parameter of type `T&` will not bind unless you pass `std::ref(x)`, and then `x`'s lifetime is your problem. and any conversion to the parameter type (say `const char*` to `std::string`) happens later, inside the new thread.

if an exception escapes the thread's top-level function, `std::terminate` is called. there is nobody to catch it. [[futures]] shows how futures carry exceptions across threads.

### in code

**how arguments travel.**

```cpp ub
#include <string>
#include <thread>
#include <vector>

void fill(std::vector<double>& out) { out.assign(1024, 0.0); }
void log_line(const std::string& s) { /* write s somewhere */ }

void demo() {
    std::vector<double> samples;
    // std::thread t1(fill, samples);         // error: the copy is an rvalue, cannot bind to double&
    std::thread t1(fill, std::ref(samples));  // OK: samples must outlive the thread
    t1.join();                                // join makes the writes to samples visible here

    char buf[32] = "radar link up";
    std::thread t2(log_line, buf);            // BUG: buf decays to char*; the std::string
    t2.detach();                              // is built later, in t2, maybe after buf is gone (UB)

    std::thread t3(log_line, std::string(buf));  // fixed: convert before the thread starts
    t3.join();
}
```

**a member thread, started too early.**

```cpp ub
#include <atomic>
#include <chrono>
#include <thread>

class ImuPoller {
public:
    ImuPoller() : worker_([this] { run(); }) {}
    ~ImuPoller() {
        running_ = false;
        worker_.join();
    }
private:
    void run() {
        while (running_) {                       // may run before running_ is initialized
            poll_once();
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }
    void poll_once() { /* read registers, publish a sample */ }

    std::thread worker_;                         // BUG: declared first, so started first
    std::atomic<bool> running_{true};
};
```

members are initialized in declaration order ([[construction-order]]), so the thread starts before `running_` exists. initializing an atomic is not an atomic operation, so the thread's load races with it: undefined behavior. declaring `running_` first fixes that, but the class still needs a hand-written destructor that stops and joins, and every author writes that shutdown logic slightly differently. [[jthread]] removes it.

### in practice

how many threads? `std::thread::hardware_concurrency()` is a hint, and it may return 0 when the value is not computable. creating a thread is a system call plus a stack (commonly megabytes of reserved address space; the size is platform-dependent and `std::thread` gives you no portable way to set it). that cost is fine for a dozen long-lived component threads and wrong for one thread per incoming request, which is why thread pools exist ([[sync-primitives]]).

### watch out for

**an exception between starting and joining terminates the program.**

```cpp
#include <thread>

void process() {
    std::thread worker(compute);
    prepare_output();     // if this throws, ~thread runs on a joinable thread: std::terminate
    worker.join();
}
```

the `join` is skipped by the exception, the destructor finds a joinable thread, and the process ends with no stack unwinding report from your code. this is the same "cleanup on every exit path" problem that [[raii]] solved for files, and the same solution applies: a guard that joins in its destructor, which is exactly what `std::jthread` is.

### the takeaway

a `std::thread` must be joined (or, rarely, detached) before it is destroyed, its arguments are copied into the new thread, and anything it references must outlive it; let an RAII owner do the joining.

### optional challenge

what is wrong with this function, and what are two ways to fix it?

```cpp
void start_logging(const std::vector<Sample>& samples) {
    std::vector<Sample> buffer = samples;
    std::thread t([&] { write_all(buffer); });
    t.detach();
}
```

<details>
<summary>answer</summary>

the lambda captures `buffer` by reference, and `buffer` is destroyed when `start_logging` returns, almost certainly while the detached thread is still writing: undefined behavior. one fix moves the data into the closure, `std::thread t([buf = std::move(buffer)] { write_all(buf); });`, so the thread owns what it uses (and then ask whether detaching is still right at shutdown). the other keeps ownership with the caller: return the thread, or a `std::jthread`, so someone joins it before the data goes away.

</details>
