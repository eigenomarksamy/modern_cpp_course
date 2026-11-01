---
title: class templates, CTAD, and specialization
standard: C++17
objective: write class templates with type and non-type parameters, use class template argument deduction, and specialize where per-type behavior is needed
prerequisites: function-templates
difficulty: 2
---

### the idea

`std::vector v{1, 2, 3};` names a class template without angle brackets, `std::array<float, 64>` puts a number in a type, and `std::vector<bool>` behaves differently from every other `std::vector`. those are three features of class templates: argument deduction from constructors, non-type parameters, and specialization. each is powerful, and each has a cost that shows up in compile times, binary size, or surprises.

### understanding the concept

a class template generates a distinct class for every set of template arguments: `RingBuffer<float, 64>` and `RingBuffer<float, 128>` are unrelated types with separate code. a **non-type template parameter** puts a value (an integer, an enumerator, a pointer, and since C++17 any type deduced with `auto`) into the type, so the compiler can size storage, unroll loops, and check bounds at compile time.

CTAD reads the constructors and synthesizes deduction candidates from them, which is how `std::pair p{1, 2.0}`, `std::vector v{1, 2, 3}`, and `std::lock_guard lock{m}` work without angle brackets. a deduction guide adds a candidate when the constructor's parameter types do not say what you want deduced. note that CTAD from aggregate initialization without a guide arrived only in C++20.

specialization customizes a template for particular arguments. class templates allow full and partial specialization. function templates allow only full specialization, and even that is usually the wrong tool: overload instead.

### in code

a class template, with a non-type parameter for capacity, and C++17 class template argument deduction (CTAD) with a deduction guide:

```cpp complete
#include <array>
#include <cstddef>
#include <string>

template <typename T, std::size_t N>
class RingBuffer {
    static_assert(N > 0, "capacity must be positive");
    std::array<T, N> buf_{};
    std::size_t next_ = 0, count_ = 0;
public:
    void push(const T& v) { buf_[next_] = v; next_ = (next_ + 1) % N; if (count_ < N) ++count_; }
    std::size_t size() const { return count_; }
    static constexpr std::size_t capacity() { return N; }
};

RingBuffer<float, 64> imu_window;   // N is part of the type: <float, 64> and <float, 128> are unrelated

template <typename T>
class Setting {
public:
    Setting(std::string name, T value) : name_(std::move(name)), value_(std::move(value)) {}
    const T& value() const { return value_; }
private:
    std::string name_;
    T value_;
};
Setting(std::string, const char*) -> Setting<std::string>;   // deduction guide

Setting gain{"gain", 2.5};     // CTAD: Setting<double>
Setting mode{"mode", "auto"};  // without the guide: Setting<const char*>, storing a pointer
                               // with the guide:    Setting<std::string>, owning its text

template <auto Value>          // C++17: the parameter's type is deduced from the argument
struct Constant { static constexpr auto value = Value; };
static_assert(Constant<'x'>::value == 'x' && Constant<42u>::value == 42u);
```

```cpp complete
#include <string>

template <typename T>
struct Serializer {                 // primary template
    static std::string to_text(const T& v) { return std::to_string(v); }
};

template <>
struct Serializer<bool> {           // full specialization
    static std::string to_text(bool b) { return b ? "true" : "false"; }
};

template <typename T>
struct Serializer<T*> {             // partial specialization: any pointer
    static std::string to_text(const T* p) { return p ? Serializer<T>::to_text(*p) : "null"; }
};

template <typename T> std::string describe(const T& v) { return Serializer<T>::to_text(v); }
// template <typename T> std::string describe<T*>(T* p);  // error: function templates cannot
                                                          // be partially specialized
template <typename T> std::string describe(T* p) { return "ptr:" + Serializer<T*>::to_text(p); }  // overload instead
```

### in practice

a robotics middleware team templated its message buffers on both element type and capacity, `MessageQueue<T, N>`, and used it across 60 translation units with a dozen distinct `(T, N)` pairs. two costs showed up. compile time: every translation unit that touched a queue re-instantiated the same member functions, and the parser had to chew through the full implementation each time. binary size: `MessageQueue<Pose, 16>` and `MessageQueue<Pose, 32>` are entirely separate code even though only a constant differs.

the fixes were design decisions, not tricks. capacity moved to a constructor argument (allocated once at startup), because nothing needed it at compile time; that collapsed the instantiation count by type. the handful of remaining instantiations were declared `extern template` in the header and explicitly instantiated in a single `.cpp`. the rule of thumb: make something a template parameter when the compiler genuinely benefits from knowing it (inline storage, type safety, unrolling, compile-time checks), and a runtime value when it merely varies. measure the compile side with `-ftime-report` (GCC) or `-ftime-trace` (Clang), and the size side with `nm --size-sort` or a tool like Bloaty.

### watch out for

**member functions of a class template are instantiated only when used.** that is what lets `std::vector<T>` work for types that support only some operations, and it also means untested members are uncompiled code:

```cpp
#include <memory>

RingBuffer<std::unique_ptr<int>, 4> owners;      // compiles: push() is not instantiated yet
// owners.push(std::make_unique<int>(1));        // error only now: push(const T&) copies
```

a template library can pass its own test suite and still fail to compile for a user's type the first time an untested member is called. test templates with the kinds of types users will actually bring: move-only, non-default-constructible, and expensive to copy.

### the takeaway

every template parameter is a compile-time decision with compile-time and binary-size costs; make something a template parameter only when the compiler genuinely benefits from knowing it, and specialize class templates, not function templates.

### optional challenge

what type does `v` have, and how many elements does it hold?

```cpp
std::vector<int> inner{1, 2};
std::vector v{inner};
```

<details>
<summary>answer</summary>

`std::vector<int>` with 2 elements: a copy of `inner`. you might expect braces to prefer the `std::initializer_list` constructor and produce `std::vector<std::vector<int>>` with one element. but CTAD has a special rule: when the braced list holds a single element whose type is a specialization of the class template being deduced, the copy deduction candidate wins. with two elements, `std::vector w{inner, inner}`, you do get `std::vector<std::vector<int>>`. if you mean a vector of vectors, spell the type out.

</details>
