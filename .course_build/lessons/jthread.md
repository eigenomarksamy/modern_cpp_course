---
title: `std::jthread` and cooperative cancellation
standard: C++20
objective: own threads with `std::jthread`, stop them cooperatively with stop tokens, and wake blocked work with stop_callback
prerequisites: threads
difficulty: 2
---

### the idea

every class that owns a `std::thread` ends up with the same hand-written destructor: set a flag, wake the thread if it is waiting, join it. every author gets one detail slightly wrong, and the failure is a hang or a `std::terminate` at shutdown, the least tested path in most programs. C++20's `std::jthread` makes "stop, then join" the default behavior of the thread object itself, and adds a standard vocabulary for asking a thread to stop.

### understanding the concept

C++20 `std::jthread` fixes the ownership story. its destructor does `if (joinable()) { request_stop(); join(); }`, which is RAII applied to threads ([[raii]]). it also owns a `std::stop_source`; if the callable's first parameter is a `std::stop_token`, the jthread passes it one. the three stop types:

| type | role |
|---|---|
| `std::stop_source` | the "remote control": `request_stop()` (returns `true` only for the call that made the request) |
| `std::stop_token` | a read-only view: `stop_requested()`, cheap to copy and pass down |
| `std::stop_callback` | registers a callable that runs when stop is requested |

cancellation is cooperative. nothing interrupts the thread; the thread has to look at the token.

### in code

```cpp complete
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

the comment on `worker_` is the important design rule. destruction runs in reverse declaration order, so the thread is stopped and joined before any member it uses is destroyed. if the jthread is declared first, it is destroyed last, and the thread can briefly run against members that are already gone.

third, `std::stop_callback` lets a stop request reach into code that is blocked and not looking at the token:

```cpp complete
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

the callback runs on whichever thread requests the stop, which is why `cancel()`'s thread-safety is part of the driver's contract. started as `std::jthread t(reader, std::ref(port));`, the jthread's destructor triggers the callback.

### in practice

in a robot stack, each driver component (lidar, IMU, motor bus) typically owns one thread. making that thread a `std::jthread` member declared last gives you a component whose destructor is correct by construction, and whose shutdown order follows ownership: destroying the component tree in reverse order stops threads from the leaves up.

for process-wide shutdown (SIGTERM from systemd, say), keep one `std::stop_source` in `main`, and give each component a `std::stop_token` from it as a constructor argument. be aware that a jthread's own stop source is separate. the jthread injects its token only when the callable accepts one as an extra first argument; a lambda taking a single `std::stop_token`, started as `std::jthread t(f, process_token)`, receives *your* token, and `~jthread`'s `request_stop()` then reaches nobody. a `stop_callback` on the process token that calls `worker_.request_stop()` bridges the two cleanly.

### watch out for

cooperative cancellation is only as responsive as the checks. in the jthread example, `sleep_for` does not observe the token, so destruction can block for up to one period. with 10 ms that is harmless. with a blocking `read()` that waits for a sensor that has been unplugged, the destructor hangs forever, and a hung destructor is worse than a crash because nothing reports it. every blocking call inside a stoppable thread needs a way to be woken: a `stop_callback`, a timeout, or a stop-token-aware wait such as `std::condition_variable_any::wait` with a token ([[condition-variables]]).

### the takeaway

own every thread with RAII: `std::jthread`, declared after everything it touches, with a `stop_token` checked at every point where the thread can block. treat `detach` as a code smell that needs a written justification.

### optional challenge

```cpp complete
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

it prints `42`, guaranteed. the inner scope ends, `~jthread` calls `request_stop()` (ignored, since the lambda takes no token) and then `join()`. the thread's completion synchronizes with the return of `join()`, so the write to `value` happens before the read in `main`. there is no data race. replace `std::jthread` with `std::thread` and the program calls `std::terminate` at the closing brace instead, because the thread is still joinable.

</details>
