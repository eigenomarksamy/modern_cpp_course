---
title: review: moves and ownership
kind: review
standard: C++17
objective: consolidate noexcept moves, special member generation, the rule of zero, smart pointers, and ownership in interfaces
prerequisites: noexcept-moves, special-members, rule-of-zero, unique-ptr, shared-ptr, ownership-in-interfaces
difficulty: 1
---

### recap

| lesson | key idea |
|---|---|
| [[noexcept-moves]] | containers move elements only if the move constructor is `noexcept`; otherwise they copy to keep the strong guarantee. |
| [[special-members]] | declaring a destructor or copy operation, even as `= default`, suppresses the implicit moves; then moves silently become copies. |
| [[rule-of-zero]] | write special members only in the few classes that own a resource; compose everything else from members that manage themselves. |
| [[unique-ptr]] | sole ownership at the cost of a raw pointer; transfers are explicit `std::move`s. |
| [[shared-ptr]] | counted ownership for the genuinely shared case; the count is thread-safe, the pointee is not, and cycles leak. |
| [[ownership-in-interfaces]] | raw pointers and references borrow; `unique_ptr` by value takes, `shared_ptr` by value shares. |

the thread through the module: **ownership is a design decision, and C++ lets you write it into types**. once it is in the types, the compiler enforces it, destructors execute it, and reviewers can read it.

### review questions

1. a class's destructor is declared as `~Telemetry() = default;` and nothing else special is declared. its members are a `std::string` and a `std::vector<Sample>`. when a `std::vector<Telemetry>` reallocates, are the elements moved or copied? why?
2. two threads each hold their own `std::shared_ptr<Stats>` to the same object. one calls `p->add(sample)`, the other `p->reset()`. the reference count is atomic; is this code safe?
3. looking ahead: a plugin interface has virtual functions but a public non-virtual destructor. `std::shared_ptr<Plugin> p = std::make_shared<Logger>(); p.reset();` works correctly. the same code with `std::unique_ptr` is undefined behavior. explain the difference, and why "use `shared_ptr`" is the wrong fix.
4. from [[copy-elision]]: C++17 guarantees elision for prvalues but not for named locals. how does that explain the advice against `return std::move(local);`?

### mini exercise

this class works in the happy path and has at least four ownership bugs. find them, then rewrite it so it needs no user-declared special members (or, if it needs one, say why and handle the consequence).

```cpp complete
#include <cstdio>
#include <cstring>
#include <stdexcept>

class TelemetryLog {
public:
    TelemetryLog(const char* path, std::size_t capacity)
        : file_(std::fopen(path, "a")), buf_(new char[capacity]), cap_(capacity) {
        if (!file_) throw std::runtime_error("cannot open log");
    }
    ~TelemetryLog() { flush(); std::fclose(file_); delete[] buf_; }

    void write(const char* msg) {
        std::size_t n = std::strlen(msg);
        if (used_ + n > cap_) flush();
        if (n > cap_) { std::fwrite(msg, 1, n, file_); return; }
        std::memcpy(buf_ + used_, msg, n);
        used_ += n;
    }
    void flush() { std::fwrite(buf_, 1, used_, file_); used_ = 0; }
private:
    std::FILE* file_;
    char* buf_;
    std::size_t cap_, used_ = 0;
};
```

### answers

<details>
<summary>answer 1: defaulted destructor and vector reallocation</summary>

copied. `= default` still counts as *declaring* the destructor ([[special-members]]), so the implicit move constructor and move assignment are not declared. rvalues then bind to the copy constructor, `std::is_nothrow_move_constructible_v<Telemetry>` is false (the copy constructor can throw), and `std::vector` falls back to copying to keep its strong guarantee ([[noexcept-moves]]). fix: delete the destructor declaration, or declare all five as `= default`.

</details>

<details>
<summary>answer 2: shared_ptr and threads</summary>

no. the atomic count makes it safe for each thread to copy and destroy *its own* `shared_ptr`; it does nothing for the `Stats` object. `add` and `reset` modify the same object concurrently, which is a data race and undefined behavior unless `Stats` synchronizes internally (or the threads share a mutex). sharing ownership and sharing mutable state are separate problems, and `shared_ptr` only solves the first.

</details>

<details>
<summary>answer 3: shared_ptr, unique_ptr, and the missing virtual destructor</summary>

`make_shared<Logger>()` creates a control block whose deleter destroys a `Logger`, and converting to `shared_ptr<Plugin>` keeps that control block, so the right destructor runs. `unique_ptr<Plugin>` uses `default_delete<Plugin>`, which does `delete` on a `Plugin*`; without a virtual destructor that is undefined behavior ([[virtual-destructors-slicing]]). switching to `shared_ptr` papers over the defect for one creation path only: a `shared_ptr<Plugin>(raw_plugin_ptr)` or any plain `delete` brings it back, and it imposes shared ownership where none is needed. the fix is a public virtual destructor in the interface.

</details>

<details>
<summary>answer 4: elision and return std::move</summary>

`return local;` is eligible for NRVO, which compilers routinely perform but the standard does not require; if it does not happen, the local is still treated as an rvalue and moved. `return std::move(local);` turns the operand into an xvalue, which is no longer "the name of a local", so NRVO is off the table and you are guaranteed a move instead of possibly nothing. C++17's guaranteed elision applies to prvalues (`return Frame{n};`), where no copy or move constructor is even required. GCC warns with `-Wpessimizing-move`.

</details>

<details>
<summary>mini exercise answer</summary>

the bugs:

- if `new char[capacity]` throws `std::bad_alloc`, the destructor never runs ([[construction-order]]), and the `FILE*` leaks.
- if `fopen` fails, the body throws and `buf_` leaks for the same reason.
- the implicit copy operations copy both raw pointers: two objects, then a double `fclose` and double `delete[]` (UB).
- no moves: the class cannot be returned from a factory or stored in a vector without copying, which is itself the double-free bug.
- the destructor calls `flush()`, whose `fwrite` errors are silently lost ([[raii]]).

the neatest rewrite notices that the hand-made buffer duplicates what stdio already does. remove it, size the stdio buffer instead, and the class owns exactly one resource through a type that already manages it:

```cpp complete
#include <cstdio>
#include <memory>
#include <stdexcept>

struct FileCloser {
    void operator()(std::FILE* f) const noexcept { std::fclose(f); }  // fclose flushes
};

class TelemetryLog {                         // move-only, rule of zero
public:
    TelemetryLog(const char* path, std::size_t capacity)
        : file_(std::fopen(path, "a")) {
        if (!file_) throw std::runtime_error("cannot open log");
        std::setvbuf(file_.get(), nullptr, _IOFBF, capacity);
    }
    void write(const char* msg) { std::fputs(msg, file_.get()); }
    [[nodiscard]] bool flush() { return std::fflush(file_.get()) == 0; }  // reports errors
private:
    std::unique_ptr<std::FILE, FileCloser> file_;
};
```

copying is now implicitly deleted, moves are implicit and `noexcept`, both leak paths are gone, and callers who care about write errors call `flush()` and check it. document the moved-from state: `file_` is null, so only assignment and destruction are allowed.

if you must keep a custom buffer (say, to batch records into fixed-size packets), make it a `std::vector<char>` member. flushing it on destruction then needs a user-declared destructor, which suppresses the implicit moves: declare the move operations `= default` and the copy operations `= delete`, so the class states its ownership explicitly instead of losing it by accident.

</details>

### connections

the last two modules turned the language rules from the first two into ownership, and that vocabulary is used everywhere from here on. the next module adds runtime polymorphism ([[virtual-dispatch]]), where virtual destructors and slicing are ownership questions again. after it, containers ([[sequence-containers]]) reward `noexcept` moves, lambdas ([[lambdas]]) capture `unique_ptr` with init-captures, and perfect forwarding ([[variadic-templates]]) is how `make_unique` and `emplace_back` pass arguments through.
