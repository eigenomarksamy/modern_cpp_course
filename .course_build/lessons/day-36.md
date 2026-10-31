<a id="day-36"></a>

## day 36: threads and `std::jthread`

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 08, 09, 17

### the idea

You have a sensor driver that polls an IMU every 10 ms on its own thread. Starting the thread is one line. Stopping it correctly, on every path including exceptions and early returns, is where the bugs live. If a `std::thread` object is destroyed while it still represents a running thread, your process does not leak or hang: it calls `std::terminate`. This week is about sharing safely, and it starts with owning threads safely.

### understanding the concept

A `std::thread` is a handle that owns at most one thread of execution. Constructing it with a callable starts the thread; the standard says the end of the constructor *synchronizes with* the start of the callable, so everything the parent did before constructing the thread is visible inside it. When the thread finishes, its completion synchronizes with the return of `join()`, so everything the thread did is visible after `join` returns. We will make "synchronizes with" precise on day 40; for now, `join` is your visibility guarantee.

A thread object is *joinable* if it still owns a thread. It stops being joinable after `join()`, `detach()`, or being moved from. Destroying (or move-assigning to) a joinable `std::thread` calls `std::terminate`. That sounds harsh, but both alternatives were worse: an implicit `join` can hang a destructor forever, and an implicit `detach` lets the thread keep running with references to locals that are gone.

`detach()` is rarely right. A detached thread cannot be waited for, so you cannot know when it has stopped touching your objects. At process exit, static objects are destroyed while a detached thread may still be running, and any access to an object after its lifetime ends is UB. Use `detach` only for work that touches nothing but its own copies, and even then, ask what happens at shutdown.

Arguments are *decay-copied* into storage owned by the new thread, in the constructing thread, and then passed to the callable as rvalues. Two consequences follow. A parameter of type `T&` will not bind unless you pass `std::ref(x)`, and then `x`'s lifetime is your problem. And any conversion to the parameter type (say `const char*` to `std::string`) happens later, inside the new thread.

If an exception escapes the thread's top-level function, `std::terminate` is called. There is nobody to catch it. Day 39 shows how futures carry exceptions across threads.

C++20 `std::jthread` fixes the ownership story. Its destructor does `if (joinable()) { request_stop(); join(); }`, which is RAII applied to threads (day 08). It also owns a `std::stop_source`; if the callable's first parameter is a `std::stop_token`, the jthread passes it one. The three stop types:

| type | role |
|---|---|
| `std::stop_source` | the "remote control": `request_stop()` (returns `true` only for the call that made the request) |
| `std::stop_token` | a read-only view: `stop_requested()`, cheap to copy and pass down |
| `std::stop_callback` | registers a callable that runs when stop is requested |

Cancellation is cooperative. Nothing interrupts the thread; the thread has to look at the token.

### in code

First, the classic hand-rolled version. It has a real bug, and it is not the one you might look for first.

```cpp
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

Members are initialized in declaration order (day 09), so the thread starts before `running_` exists. Initializing an atomic is not an atomic operation, so the thread's load races with it: UB. Swapping the declarations fixes that, but the class still needs a hand-written destructor, and the shutdown logic is something every author reimplements slightly differently. With `std::jthread`:

```cpp
#include <chrono>
#include <stop_token>
#include <thread>

class ImuPoller {
public:
    ImuPoller() : worker_([this](std::stop_token st) { run(st); }) {}
    // no destructor: ~jthread requests stop, then joins

private:
    void run(std::stop_token st) {
        while (!st.stop_requested()) {
            poll_once();
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }
    void poll_once() { /* read registers, publish a sample */ }

    // Other members (buffers, config) go above this line.
    std::jthread worker_;   // declared last: constructed last, destroyed first
};
```

The comment on `worker_` is the important design rule. Destruction runs in reverse declaration order, so the thread is stopped and joined before any member it uses is destroyed. If the jthread is declared first, it is destroyed last, and the thread can briefly run against members that are already gone.

Second, how arguments travel:

```cpp
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

Third, `std::stop_callback` lets a stop request reach into code that is blocked and not looking at the token:

```cpp
#include <optional>
#include <stop_token>

struct Frame { /* payload */ };
struct SerialPort {                  // driver API
    std::optional<Frame> read();     // blocks until a frame arrives or cancel() is called
    void cancel();                   // documented as safe to call from any thread
};
void handle(const Frame&);

void reader(std::stop_token st, SerialPort& port) {
    // Runs inside request_stop() on the requesting thread,
    // or immediately here if stop was already requested.
    std::stop_callback on_stop(st, [&port] { port.cancel(); });  // makes read() return early
    while (!st.stop_requested()) {
        if (auto frame = port.read())        // blocks until data or cancel()
            handle(*frame);
    }
}   // ~stop_callback deregisters; if the callback is running on another thread, it waits
```

The callback runs on whichever thread requests the stop, which is why `cancel()`'s thread-safety is part of the driver's contract. Started as `std::jthread t(reader, std::ref(port));`, the jthread's destructor triggers the callback.

### in practice

In a robot stack, each driver component (lidar, IMU, motor bus) typically owns one thread. Making that thread a `std::jthread` member declared last gives you a component whose destructor is correct by construction, and whose shutdown order follows ownership: destroying the component tree in reverse order stops threads from the leaves up.

For process-wide shutdown (SIGTERM from systemd, say), keep one `std::stop_source` in `main`, and give each component a `std::stop_token` from it as a constructor argument. Be aware that a jthread's own stop source is separate. The jthread injects its token only when the callable accepts one as an extra first argument; a lambda taking a single `std::stop_token`, started as `std::jthread t(f, process_token)`, receives *your* token, and `~jthread`'s `request_stop()` then reaches nobody. A `stop_callback` on the process token that calls `worker_.request_stop()` bridges the two cleanly.

How many threads? `std::thread::hardware_concurrency()` is a hint, and it may return 0 when the value is not computable. Creating a thread is a system call plus a stack (commonly megabytes of reserved address space; the size is platform-dependent and `std::thread` gives you no portable way to set it). That cost is fine for a dozen long-lived component threads and wrong for one thread per incoming request, which is why thread pools exist (day 41).

### watch out for

Cooperative cancellation is only as responsive as the checks. In the jthread example, `sleep_for` does not observe the token, so destruction can block for up to one period. With 10 ms that is harmless. With a blocking `read()` that waits for a sensor that has been unplugged, the destructor hangs forever, and a hung destructor is worse than a crash because nothing reports it. Every blocking call inside a stoppable thread needs a way to be woken: a `stop_callback`, a timeout, or a stop-token-aware wait such as `std::condition_variable_any::wait` with a token (day 38).

### the takeaway

Own every thread with RAII: `std::jthread`, declared after everything it touches, with a `stop_token` checked at every point where the thread can block. Treat `detach` as a code smell that needs a written justification.

### optional challenge

What does this print, and is it guaranteed?

```cpp
#include <iostream>
#include <thread>

int main() {
    int value = 0;
    {
        std::jthread t([&value] { value = 42; });
    }
    std::cout << value << '\n';
}
```

<details>
<summary>answer</summary>

It prints `42`, guaranteed. The inner scope ends, `~jthread` calls `request_stop()` (ignored, since the lambda takes no token) and then `join()`. The thread's completion synchronizes with the return of `join()`, so the write to `value` happens before the read in `main`. There is no data race. Replace `std::jthread` with `std::thread` and the program calls `std::terminate` at the closing brace instead, because the thread is still joinable.

</details>
