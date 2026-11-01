<a id="day-18"></a>

## day 18: templates: writing code for many types

**reading time:** about 10 minutes · **standard:** C++17 · **builds on:** days 01, 16, 17

### the idea

```cpp
template <typename T>
T clamp_to(T v, T lo, T hi) { return v < lo ? lo : (hi < v ? hi : v); }

double speed = 12.5;
auto s = clamp_to(speed, 0, 10);  // error: deduced conflicting types for 'T' ('double' and 'int')
```

A function would have converted `0` and `10` to `double` without complaint. A template refuses. That refusal is the first rule of templates in action, and the rest of the model (instantiation, headers, specialization, the `typename` keyword nobody remembers to write) follows from taking templates for what they are: not functions or classes, but recipes the compiler uses to generate them.

### understanding the concept

**Deduction comes before conversion.** For a function template call, the compiler first deduces `T` from each argument independently, and every deduction must agree. Implicit conversions are considered only after `T` is fixed. Here the first argument says `double` and the others say `int`, so deduction fails before conversion is ever considered. The fixes say different things: `clamp_to<double>(speed, 0, 10)` fixes `T` explicitly and lets conversions happen; `clamp_to(speed, 0.0, 10.0)` makes the arguments agree; separate parameters `template <typename T, typename U>` accept the mix but must then define what mixing means. `std::max(1, 2.0)` fails for the same reason.

**Instantiation happens where the template is used.** When the compiler sees `clamp_to<double>`, it stamps out a real function from the template body, which it can only do if the body is visible in that translation unit. That is why template definitions live in headers (day 01): put the body in a `.cpp` and every other translation unit gets an `undefined reference` at link time. Identical instantiations from different translation units are emitted as weak or COMDAT symbols and merged by the linker, so this does not violate the one definition rule. You can opt out with explicit instantiation: `template class RingBuffer<float, 64>;` in one `.cpp`, plus `extern template class RingBuffer<float, 64>;` in the header to stop every other translation unit from instantiating it again.

**Two-phase lookup.** A template is checked twice. At its definition, names that do not depend on a template parameter are looked up and bound, and obvious errors are reported. At instantiation, dependent names (anything involving `T`) are resolved. Because the compiler cannot know what `T::something` is before it knows `T`, you must tell it: `typename` marks a dependent name as a type, and `template` marks a dependent name as a member template.

**Before concepts, SFINAE.** If substituting a deduced type into a template's signature produces an invalid type or expression, that candidate silently drops out of overload resolution ("substitution failure is not an error"). `std::enable_if` exploits this to restrict a template:

```cpp
#include <type_traits>

template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
T half(T v) { return v / 2; }   // half(3.0) finds no viable function
```

It works, but the intent is buried in the syntax and the errors are poor. C++20 concepts (day 29) state the same constraint as `template <std::integral T>`, and `if constexpr` (day 23) replaces many overload-set tricks.

### in code

A class template, with a non-type parameter for capacity, and C++17 class template argument deduction (CTAD) with a deduction guide:

```cpp
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

CTAD reads the constructors and synthesizes deduction candidates from them, which is how `std::pair p{1, 2.0}`, `std::vector v{1, 2, 3}`, and `std::lock_guard lock{m}` work without angle brackets. A deduction guide adds a candidate when the constructor's parameter types do not say what you want deduced. Note that CTAD from aggregate initialization without a guide arrived only in C++20.

Specialization customizes a template for particular arguments. Class templates allow full and partial specialization. Function templates allow only full specialization, and even that is usually the wrong tool: overload instead.

```cpp
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

Dependent names, the part of templates that produces the most confusing errors:

```cpp
template <typename T>
struct Base { void reset() {} };

template <typename T>
struct Filter : Base<T> {
    void clear() {
        // reset();       // error: not found; the base depends on T, so phase one doesn't look there
        this->reset();    // OK: 'this->' makes the name dependent, looked up at instantiation
    }
};

template <typename Container>
auto first_or(const Container& c, typename Container::value_type fallback) {
    typename Container::const_iterator it = c.begin();   // 'typename': this dependent name is a type
    return it != c.end() ? *it : fallback;
}
```

`Base<T>` could be specialized later so that it has no `reset` at all, which is why the compiler refuses to look inside a dependent base during the first phase. Writing `this->` defers the lookup to instantiation, when the base is known. GCC 12's error says this almost directly: `there are no arguments to 'reset' that depend on a template parameter, so a declaration of 'reset' must be available`.

### in practice

A robotics middleware team templated its message buffers on both element type and capacity, `MessageQueue<T, N>`, and used it across 60 translation units with a dozen distinct `(T, N)` pairs. Two costs showed up. Compile time: every translation unit that touched a queue re-instantiated the same member functions, and the parser had to chew through the full implementation each time. Binary size: `MessageQueue<Pose, 16>` and `MessageQueue<Pose, 32>` are entirely separate code even though only a constant differs.

The fixes were design decisions, not tricks. Capacity moved to a constructor argument (allocated once at startup), because nothing needed it at compile time; that collapsed the instantiation count by type. The handful of remaining instantiations were declared `extern template` in the header and explicitly instantiated in a single `.cpp`. The rule of thumb: make something a template parameter when the compiler genuinely benefits from knowing it (inline storage, type safety, unrolling, compile-time checks), and a runtime value when it merely varies. Measure the compile side with `-ftime-report` (GCC) or `-ftime-trace` (Clang), and the size side with `nm --size-sort` or a tool like Bloaty.

### watch out for

Explicit specializations of function templates do not take part in overload resolution; only primary templates do. The result can surprise you:

```cpp
#include <iostream>

template <typename T> void f(T)  { std::cout << "a\n"; }
template <> void f<int*>(int*)   { std::cout << "b\n"; }   // specializes the first template
template <typename T> void f(T*) { std::cout << "c\n"; }

int main() { int x = 0; f(&x); }   // prints: c
```

Overload resolution picks between the two primary templates, chooses the more specialized `f(T*)`, and the specialization of `f(T)` is never considered. Which template a specialization belongs to depends on what was declared before it and how it is spelled: written as `template <> void f(int*)` below the second template, it specializes `f(T*)` and the call prints `b`. Prefer plain overloads for functions, and specialize class templates when you need per-type behavior that a function can forward to.

### the takeaway

A template is a recipe the compiler runs per set of arguments: deduction is exact, instantiation needs the definition, and dependent names need your help. Every template parameter is a compile-time decision with compile-time and binary-size costs, so give the compiler only what it can actually use.

### optional challenge

What type does `v` have, and how many elements does it hold?

```cpp
std::vector<int> inner{1, 2};
std::vector v{inner};
```

<details>
<summary>answer</summary>

`std::vector<int>` with 2 elements: a copy of `inner`. You might expect braces to prefer the `std::initializer_list` constructor and produce `std::vector<std::vector<int>>` with one element. But CTAD has a special rule: when the braced list holds a single element whose type is a specialization of the class template being deduced, the copy deduction candidate wins. With two elements, `std::vector w{inner, inner}`, you do get `std::vector<std::vector<int>>`. If you mean a vector of vectors, spell the type out.

</details>
