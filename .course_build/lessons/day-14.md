<a id="day-14"></a>

## day 14: week 2 review: owning your resources

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 08 to 13

### recap

| day | idea in one line |
|---|---|
| [08](#day-08) | RAII ties a resource to an object's lifetime: acquire in the constructor, release in a destructor that never throws, and every exit path that unwinds cleans up. |
| [09](#day-09) | Bases, then members in declaration order, then the body; destruction reverses it. A constructor that throws leaves no object, so only fully constructed members are cleaned up. |
| [10](#day-10) | `std::move` is a cast; overload resolution picks the move. Moves must be `noexcept` for `std::vector` to use them, and moved-from objects are valid but unspecified. |
| [11](#day-11) | Declaring a destructor or copy operation suppresses the implicit moves. Write special members only in resource-owning classes; compose everything else (rule of zero). |
| [12](#day-12) | `unique_ptr` for sole ownership, `shared_ptr` only for genuinely shared ownership, `weak_ptr` to observe or break cycles, references for borrowing; signatures state which. |
| [13](#day-13) | Virtual dispatch needs indirection and a virtual destructor; use `override`, avoid slicing, inherit interfaces, and compose implementations. |

The thread through the week: **ownership is a design decision, and C++ lets you write it into types**. Once it is in the types, the compiler enforces it, destructors execute it, and reviewers can read it.

### review questions

1. A class's destructor is declared as `~Telemetry() = default;` and nothing else special is declared. Its members are a `std::string` and a `std::vector<Sample>`. When a `std::vector<Telemetry>` reallocates, are the elements moved or copied? Why?

2. Choose a parameter type for each function and say what it communicates: (a) `log_stats` reads a `Frame` and keeps nothing; (b) `Pipeline::enqueue` keeps the frame until a worker processes it, and the caller is done with it; (c) `reload_detector` may replace the caller's `Detector` with a new one.

3. After `std::string b = std::move(a);`, which of these are fine: `a.size()`, `a.clear()`, `a = "x"`, `assert(a.empty())`, `a.front()`?

4. A plugin interface has virtual functions but a public non-virtual destructor. `std::shared_ptr<Plugin> p = std::make_shared<Logger>(); p.reset();` works correctly. The same code with `std::unique_ptr` is undefined behavior. Explain the difference, and why "use `shared_ptr`" is the wrong fix.

5. **From week 1.** Day 05 said C++17 guarantees copy elision for prvalues but not for named locals. How does that connect to day 10's advice against `return std::move(local);`?

6. **From week 1.** Is this safe? `const std::string& name = load_config().name();` where `Config::name()` returns `const std::string&` to a member.

### mini exercise

This class works in the happy path and has at least four ownership bugs. Find them, then rewrite it so it needs no user-declared special members (or, if it needs one, say why and handle the consequence).

```cpp
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
<summary>1. defaulted destructor and vector reallocation</summary>

Copied. `= default` still counts as *declaring* the destructor (day 11), so the implicit move constructor and move assignment are not declared. Rvalues then bind to the copy constructor, `std::is_nothrow_move_constructible_v<Telemetry>` is false (the copy constructor can throw), and `std::vector` falls back to copying to keep its strong guarantee (day 10). Fix: delete the destructor declaration, or declare all five as `= default`.

</details>

<details>
<summary>2. parameter types</summary>

(a) `const Frame&`: a borrow for the duration of the call; ownership is not the callee's business. (b) A sink: `Frame` by value (if `Frame` is a movable value type) or `std::unique_ptr<Frame>` by value (if frames live on the heap); the caller writes `std::move(frame)`, which makes the hand-over visible. (c) `std::unique_ptr<Detector>&`: the rare "may reseat your pointer" signature. Returning a new `std::unique_ptr<Detector>` is often clearer still.

</details>

<details>
<summary>3. using a moved-from string</summary>

`a.size()`, `a.clear()`, and `a = "x"` are fine: they have no preconditions, and a moved-from standard type is valid but unspecified. `assert(a.empty())` compiles and will probably pass on your implementation, but nothing guarantees it, so it encodes a false assumption. `a.front()` has a precondition (`!a.empty()`); calling it on an empty string is undefined behavior, so it is only safe after you check. (`a[0]`, by contrast, is always valid on a `std::string`: at `size() == 0` it refers to the terminating null.) Treat a moved-from object as "assign or destroy" unless its type documents more.

</details>

<details>
<summary>4. shared_ptr, unique_ptr, and the missing virtual destructor</summary>

`make_shared<Logger>()` creates a control block whose deleter destroys a `Logger`, and converting to `shared_ptr<Plugin>` keeps that control block, so the right destructor runs. `unique_ptr<Plugin>` uses `default_delete<Plugin>`, which does `delete` on a `Plugin*`; without a virtual destructor that is undefined behavior (day 13). Switching to `shared_ptr` papers over the defect for one creation path only: a `shared_ptr<Plugin>(raw_plugin_ptr)` or any plain `delete` brings it back, and it imposes shared ownership where none is needed. The fix is a public virtual destructor in the interface.

</details>

<details>
<summary>5. from week 1: elision and return std::move</summary>

`return local;` is eligible for NRVO, which compilers routinely perform but the standard does not require; if it does not happen, the local is still treated as an rvalue and moved. `return std::move(local);` turns the operand into an xvalue, which is no longer "the name of a local", so NRVO is off the table and you are guaranteed a move instead of possibly nothing. C++17's guaranteed elision applies to prvalues (`return Frame{n};`), where no copy or move constructor is even required. GCC warns with `-Wpessimizing-move`.

</details>

<details>
<summary>6. from week 1: lifetime extension through a member function</summary>

Not safe: `name` dangles. Lifetime extension (day 03) applies only when a reference binds directly to a temporary. Here it binds to whatever `name()` returns, a reference into the temporary `Config`, and that temporary is destroyed at the end of the full-expression. Using `name` afterwards is undefined behavior. Fix: copy (`std::string name = load_config().name();`) or keep the `Config` alive in a named variable.

</details>

<details>
<summary>mini exercise: bugs and a rule-of-zero rewrite</summary>

The bugs:

- If `new char[capacity]` throws `std::bad_alloc`, the destructor never runs (day 09), and the `FILE*` leaks.
- If `fopen` fails, the body throws and `buf_` leaks for the same reason.
- The implicit copy operations copy both raw pointers: two objects, then a double `fclose` and double `delete[]` (UB).
- No moves: the class cannot be returned from a factory or stored in a vector without copying, which is itself the double-free bug.
- The destructor calls `flush()`, whose `fwrite` errors are silently lost (day 08).

The neatest rewrite notices that the hand-made buffer duplicates what stdio already does. Remove it, size the stdio buffer instead, and the class owns exactly one resource through a type that already manages it:

```cpp
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

Copying is now implicitly deleted, moves are implicit and `noexcept`, both leak paths are gone, and callers who care about write errors call `flush()` and check it. Document the moved-from state: `file_` is null, so only assignment and destruction are allowed.

If you must keep a custom buffer (say, to batch records into fixed-size packets), make it a `std::vector<char>` member. Flushing it on destruction then needs a user-declared destructor, which suppresses the implicit moves: declare the move operations `= default` and the copy operations `= delete`, so the class states its ownership explicitly instead of losing it by accident.

</details>

### connections

Week 1 supplied the mechanics this week relies on. RAII is day 03's lifetime rules turned into a design technique. Move semantics is day 05's value categories feeding overload resolution. Double deletes, deleting through a non-virtual base, and dangling back-pointers are day 06's undefined behavior wearing ownership clothes.

Week 3 builds directly on top. Containers (day 15) reward `noexcept` moves and punish iterator invalidation; lambdas (day 17) capture `unique_ptr` with init-captures; perfect forwarding (day 19) is how `make_unique` and `emplace_back` pass arguments through; and exception safety (day 20) formalizes the strong guarantee you met in copy-and-swap and `std::vector` reallocation. Further out, `std::lock_guard` and `std::jthread` (days 36 and 37) are RAII again, and dependency injection (day 44), type erasure (day 46), and the pimpl idiom (day 47) are all ownership decisions expressed through the tools from this week.
