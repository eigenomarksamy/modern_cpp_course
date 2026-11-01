---
title: function templates and argument deduction
standard: C++17
objective: predict template argument deduction, explain why template definitions live in headers, and resolve dependent names
prerequisites: linkage-odr, algorithms
difficulty: 2
---

### the idea

```cpp fails
template <typename T>
T clamp_to(T v, T lo, T hi) { return v < lo ? lo : (hi < v ? hi : v); }

double speed = 12.5;
auto s = clamp_to(speed, 0, 10);  // error: deduced conflicting types for 'T' ('double' and 'int')
```

a function would have converted `0` and `10` to `double` without complaint. a template refuses. that refusal is the first rule of templates in action, and the rest of the model (instantiation, headers, specialization, the `typename` keyword nobody remembers to write) follows from taking templates for what they are: not functions or classes, but recipes the compiler uses to generate them.

### understanding the concept

**deduction comes before conversion.** for a function template call, the compiler first deduces `T` from each argument independently, and every deduction must agree. implicit conversions are considered only after `T` is fixed. here the first argument says `double` and the others say `int`, so deduction fails before conversion is ever considered. the fixes say different things: `clamp_to<double>(speed, 0, 10)` fixes `T` explicitly and lets conversions happen; `clamp_to(speed, 0.0, 10.0)` makes the arguments agree; separate parameters `template <typename T, typename U>` accept the mix but must then define what mixing means. `std::max(1, 2.0)` fails for the same reason.

**instantiation happens where the template is used.** when the compiler sees `clamp_to<double>`, it stamps out a real function from the template body, which it can only do if the body is visible in that translation unit. that is why template definitions live in headers ([[linkage-odr]]): put the body in a `.cpp` and every other translation unit gets an `undefined reference` at link time. identical instantiations from different translation units are emitted as weak or COMDAT symbols and merged by the linker, so this does not violate the one definition rule. you can opt out with explicit instantiation: `template class RingBuffer<float, 64>;` in one `.cpp`, plus `extern template class RingBuffer<float, 64>;` in the header to stop every other translation unit from instantiating it again.

**two-phase lookup.** a template is checked twice. at its definition, names that do not depend on a template parameter are looked up and bound, and obvious errors are reported. at instantiation, dependent names (anything involving `T`) are resolved. because the compiler cannot know what `T::something` is before it knows `T`, you must tell it: `typename` marks a dependent name as a type, and `template` marks a dependent name as a member template.

### in code

dependent names, the part of templates that produces the most confusing errors:

```cpp complete
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

`Base<T>` could be specialized later so that it has no `reset` at all, which is why the compiler refuses to look inside a dependent base during the first phase. writing `this->` defers the lookup to instantiation, when the base is known. GCC 12's error says this almost directly: `there are no arguments to 'reset' that depend on a template parameter, so a declaration of 'reset' must be available`.

### in practice

library authors design around deduction. `std::clamp(v, lo, hi)` deduces one `T` from all three arguments, so `std::clamp(speed, 0, 10)` fails exactly like `clamp_to`. when one argument should decide the type and the others should simply convert to it, put the others in a *non-deduced context*, where the compiler does not try to deduce from them at all:

```cpp complete
template <typename T> struct identity { using type = T; };   // C++20: std::type_identity

template <typename T>
T clamp_to(T v, typename identity<T>::type lo, typename identity<T>::type hi) {
    return v < lo ? lo : (hi < v ? hi : v);
}

double s = clamp_to(12.5, 0, 10);   // T = double from v alone; 0 and 10 convert
```

a type nested inside a template that depends on `T` (anything to the left of `::`) cannot be used to deduce `T`, so only `v` participates. the same idea explains why `std::function<void(T)>` parameters never deduce from a lambda: the lambda's type is not `std::function`, and conversions are not considered during deduction.

### watch out for

explicit specializations of function templates do not take part in overload resolution; only primary templates do. the result can surprise you:

```cpp complete
#include <iostream>

template <typename T> void f(T)  { std::cout << "a\n"; }
template <> void f<int*>(int*)   { std::cout << "b\n"; }   // specializes the first template
template <typename T> void f(T*) { std::cout << "c\n"; }

int main() { int x = 0; f(&x); }   // prints: c
```

overload resolution picks between the two primary templates, chooses the more specialized `f(T*)`, and the specialization of `f(T)` is never considered. which template a specialization belongs to depends on what was declared before it and how it is spelled: written as `template <> void f(int*)` below the second template, it specializes `f(T*)` and the call prints `b`. prefer plain overloads for functions, and specialize class templates when you need per-type behavior that a function can forward to.

### the takeaway

a function template is a recipe: deduction is exact and per argument, instantiation needs the definition in the translation unit, and dependent names need `typename` or `this->` from you.

### optional challenge

given `template <typename T> void put(T a, T b);`, which calls compile?

```cpp
put(1, 2);            // (1)
put(1, 2u);           // (2)
put<long>(1, 2u);     // (3)
put("ab", "cd");      // (4)
put("ab", "abc");     // (5)
```

<details>
<summary>answer</summary>

(1), (3), (4), and (5) compile; (2) does not, because `int` and `unsigned int` deduce conflicting types. in (3) `T` is given, so both arguments convert to `long`. (4) and (5) are the subtle ones: by-value parameters decay arrays to pointers *before* deduction, so both arguments deduce `const char*` even though `"ab"` and `"abc"` have different array types (`const char[3]` and `const char[4]`). change the parameters to `const T&` and (5) stops compiling, because references do not decay.

</details>

### going deeper

#### before concepts: SFINAE and `std::enable_if`

**before concepts, SFINAE.** if substituting a deduced type into a template's signature produces an invalid type or expression, that candidate silently drops out of overload resolution ("substitution failure is not an error"). `std::enable_if` exploits this to restrict a template:

```cpp complete
#include <type_traits>

template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
T half(T v) { return v / 2; }   // half(3.0) finds no viable function
```

it works, but the intent is buried in the syntax and the errors are poor. C++20 concepts ([[concepts]]) state the same constraint as `template <std::integral T>`, and `if constexpr` ([[if-constexpr]]) replaces many overload-set tricks.
