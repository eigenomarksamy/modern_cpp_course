---
title: review: resources and the object lifecycle
kind: review
standard: C++17
objective: consolidate RAII, scope guards, constructors, construction order, copying, and moving
prerequisites: raii, scope-guards, constructors, construction-order, copy-semantics, move-semantics
difficulty: 1
---

### recap

| lesson | key idea |
|---|---|
| [[raii]] | tie a resource to an object: acquire in the constructor, release in a destructor that never throws, and every exit path that unwinds cleans up. |
| [[scope-guards]] | for one-off cleanup or rollback, arm a named guard and dismiss it at the point of commit. |
| [[constructors]] | a constructor establishes the invariant: initializer lists, validation once, derived state not stored, `explicit` single-argument constructors. |
| [[construction-order]] | bases, then members in declaration order, then the body; destruction reverses it, and a constructor that throws leaves no object. |
| [[copy-semantics]] | a copy must be an independent value; the generated memberwise copy is wrong for a class that owns through a raw handle. |
| [[move-semantics]] | `std::move` is a cast; the move constructor transfers the resource and leaves a valid, documented moved-from state. |

the thread through the module: **an object's lifetime is a tool**. constructors, destructors, copies, and moves are where a class decides what it owns, and the language runs that code at precisely defined moments.

### review questions

1. which ways of leaving a scope run the destructors of its automatic objects, and which do not? why do long-running services catch exceptions at the top of every thread function?
2. a class has members `A a; B b; C c;` in that order, and its constructor's initializer list names them as `c(...), a(...), b(...)`. `B`'s constructor throws. which constructors and destructors run?
3. after `std::string b = std::move(a);`, which of these are fine: `a.size()`, `a.clear()`, `a = "x"`, `assert(a.empty())`, `a.front()`?
4. why does a correct copy assignment allocate the new buffer *before* releasing the old one? name the two failures the opposite order causes.
5. from [[temporaries-dangling]]: is this safe? `const std::string& name = load_config().name();` where `Config::name()` returns `const std::string&` to a member.

### mini exercise

this class has four bugs from this module. find them, then fix the class so it declares no destructor at all.

```cpp complete
#include <cstdio>

class Recorder {
public:
    Recorder(const char* path, std::size_t n)
        : count_(n), samples_(new double[count_]), file_(std::fopen(path, "w")) {}
    ~Recorder() { std::fclose(file_); delete[] samples_; }
private:
    std::FILE* file_;
    double* samples_;
    std::size_t count_;
};
```

### answers

<details>
<summary>answer 1: which exits run destructors</summary>

normal fall-through, `return`, `break`, `continue`, `goto` out of a block, and an exception propagating to a matching handler all run them. `std::exit` runs static destructors but not the ones on the stack; `std::abort`, `std::_Exit`, crashes, and `kill -9` run nothing. an exception that is never caught calls `std::terminate`, and whether the stack is unwound first is implementation-defined (GCC and Clang typically do not unwind). catching at the top of `main` and of every thread function guarantees that unwinding, and therefore every RAII cleanup, actually happens.

</details>

<details>
<summary>answer 2: partial construction</summary>

the initializer list order is ignored: members are built in declaration order. `A` is constructed, then `B`'s constructor throws, so `C` is never constructed. the fully constructed `a` is destroyed during unwinding; the class's own destructor does not run, because the object never existed. any raw resource acquired in the constructor body would leak, which is why each member should clean up after itself.

</details>

<details>
<summary>answer 3: using a moved-from string</summary>

`a.size()`, `a.clear()`, and `a = "x"` are fine: they have no preconditions, and a moved-from standard type is valid but unspecified. `assert(a.empty())` compiles and will probably pass on your implementation, but nothing guarantees it, so it encodes a false assumption. `a.front()` has a precondition (`!a.empty()`); calling it on an empty string is undefined behavior, so it is only safe after you check. (`a[0]`, by contrast, is always valid on a `std::string`: at `size() == 0` it refers to the terminating null.) treat a moved-from object as "assign or destroy" unless its type documents more.

</details>

<details>
<summary>answer 4: acquire before release</summary>

if the old buffer is released first, self-assignment (`b = b`) frees the very data it is about to copy, and an exception from the allocation leaves the object holding a dangling pointer that its destructor frees a second time. allocating and copying into a fresh buffer first, then swapping it in, leaves `*this` untouched if anything throws (the strong guarantee) and makes self-assignment harmless.

</details>

<details>
<summary>answer 5: lifetime extension through a member function</summary>

not safe: `name` dangles. lifetime extension ([[temporaries-dangling]]) applies only when a reference binds directly to a temporary. here it binds to whatever `name()` returns, a reference into the temporary `Config`, and that temporary is destroyed at the end of the full-expression. using `name` afterwards is undefined behavior. fix: copy (`std::string name = load_config().name();`) or keep the `Config` alive in a named variable.

</details>

<details>
<summary>mini exercise answer</summary>

- **construction order:** members are initialized in declaration order: `file_`, then `samples_`, then `count_`. `samples_(new double[count_])` reads `count_` before it is initialized, which is undefined behavior.
- **unchecked open:** if `fopen` fails, `file_` is null and the destructor calls `fclose(nullptr)`, which is undefined behavior.
- **partial construction:** `file_` is opened first; if `new double[...]` then throws, the destructor never runs and the file leaks.
- **copying:** the generated copy constructor copies both raw pointers, so two objects close the same file and free the same buffer.

```cpp complete
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <vector>

struct FileCloser {
    void operator()(std::FILE* f) const noexcept { std::fclose(f); }
};

class Recorder {                                  // no destructor, no copy, safe moves
public:
    Recorder(const char* path, std::size_t n) : file_(std::fopen(path, "w")), samples_(n) {
        if (!file_) throw std::runtime_error("cannot open recording");
    }
private:
    std::unique_ptr<std::FILE, FileCloser> file_;
    std::vector<double> samples_;                 // knows its own size
};
```

each member now cleans up after itself, so a throw at any point releases exactly what was acquired, copying is implicitly deleted (a `unique_ptr` member is move-only), and the count is no longer stored twice.

</details>

### connections

the previous modules supplied the mechanics this one relied on: deterministic destruction from [[storage-duration]], value categories from [[value-categories]], and undefined behavior from [[undefined-behavior]], which is what every double free and dangling handle above really is. the next module finishes the ownership story: when moves are trusted ([[noexcept-moves]]), which special members the compiler writes ([[special-members]]), how to need none of them ([[rule-of-zero]]), and how smart pointers write ownership into types.
