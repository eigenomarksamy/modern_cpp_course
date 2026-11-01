---
title: `std::span`: views over contiguous memory
standard: C++20
objective: replace pointer-plus-length parameters with `std::span`, use static extents as contracts, and keep spans from outliving their buffers
prerequisites: string-view, view-lifetimes
difficulty: 2
---

### the idea

every C and C++ codebase has functions like `void process(const float* data, std::size_t n)`. the pointer and the count travel separately, so nothing stops a caller from passing `n` in bytes instead of elements, the size of the wrong buffer, or `n` for the whole buffer with a pointer into the middle of it. and the signature cannot say whether the function writes through `data` beyond the `const` you remembered to type.

`std::span` (C++20, `<span>`) is the pointer and the count fused into one value type. it does for contiguous arrays of any `T` what `std::string_view` ([[string-view]]) did for characters: it borrows, it does not own, and it makes the borrowing explicit in the signature.

### understanding the concept

`std::span<T, Extent>` refers to a contiguous sequence of `T`. it has two forms:

- **dynamic extent** (`std::span<T>`, i.e. `Extent == std::dynamic_extent`): stores a pointer and a size. 16 bytes on a typical 64-bit platform (verified with GCC 12 on x86-64).
- **static extent** (`std::span<T, N>`): the size is part of the type, so typical implementations store only the pointer (8 bytes in the same test). the type itself carries a compile-time guarantee: this is exactly `N` elements.

a span is a cheap trivially copyable value: pass it by value, as you would a `string_view`. it converts implicitly from C arrays, `std::array`, `std::vector`, and any other contiguous, sized range (including another span), and explicitly from a pointer plus a count. the element type carries the constness: `std::span<const float>` is read-only, `std::span<float>` is writable, and a `std::span<float>` converts to `std::span<const float>` but not the other way.

slicing is O(1) and never copies: `first(n)`, `last(n)`, `subspan(offset, count)`, and static-extent versions `first<N>()`, `last<N>()`, `subspan<Offset, Count>()` that return a `std::span<T, N>`. finally, `std::as_bytes(s)` and `std::as_writable_bytes(s)` reinterpret any span as a span of `std::byte`, which is the C++20 way to say "the object representation of these elements".

bounds: C++20 `std::span` has **no** `at()`. `operator[]`, `front()`, `back()`, and the slicing functions have preconditions (index in range, count not past the end), and violating one is undefined behavior. `at()` is added in C++26. your standard library may check preconditions in a hardened mode: with libstdc++, `-D_GLIBCXX_ASSERTIONS` turns an out-of-range `operator[]` into an assertion failure (checked with GCC 12).

### in code

**before and after.**

```cpp complete
#include <array>
#include <cmath>
#include <span>
#include <vector>

// C++17: two parameters that must agree, and nothing checks that they do
float rms17(const float* data, std::size_t n);

// C++20: one parameter, read-only by type
float rms(std::span<const float> samples) {
    if (samples.empty()) return 0.f;
    float acc = 0.f;
    for (float s : samples) acc += s * s;
    return std::sqrt(acc / static_cast<float>(samples.size()));
}

void scale(std::span<float> samples, float gain) {   // writable by type
    for (float& s : samples) s *= gain;
}

void demo(std::vector<float>& buf, std::array<float, 2>& arr, float (&raw)[4]) {
    rms(buf); rms(arr); rms(raw);                 // all implicit
    rms(std::span(buf).first(2));                 // first two samples, no copy
    rms(std::span(buf).subspan(1, 2));            // elements 1 and 2
    scale(buf, 0.5f);
}
```

the callee no longer cares who owns the samples. the caller can pass a whole buffer or a window into one, and the function body uses range-for instead of index arithmetic.

**static extent as a contract.** a 6-DoF pose is exactly six numbers. put that in the type:

```cpp
void set_pose(std::span<const double, 6> pose);

std::array<double, 6> p{};
set_pose(p);                         // OK: size known to match
std::array<double, 5> p5{};
// set_pose(p5);  error: could not convert 'p5' from 'std::array<double, 5>' to 'std::span<const double, 6>'

std::vector<double> pv(7);
// set_pose(pv);  error: a vector's size is a runtime value
set_pose(std::span<const double>(pv).first<6>());   // explicit; UB if pv.size() < 6
```

the dynamic-to-static conversion is deliberately explicit: it is where a runtime size becomes a compile-time promise, so it should be visible in the code (and is a good place for a check).

### in practice

a radar pipeline stores a range-Doppler frame as one row-major `std::vector<float>` (one allocation, contiguous rows) and hands out rows as spans:

```cpp
class RangeDopplerFrame {
public:
    RangeDopplerFrame(std::size_t doppler_bins, std::size_t range_bins)
        : range_bins_(range_bins), cells_(doppler_bins * range_bins) {}
    std::span<float> row(std::size_t d) {                 // borrow one row, no copy
        return std::span(cells_).subspan(d * range_bins_, range_bins_);
    }
    std::span<const float> cells() const { return cells_; }
private:
    std::size_t range_bins_;
    std::vector<float> cells_;
};

float peak(std::span<const float> cells);   // CFAR, FFT, stats: none know about the frame
```

this is a coupling decision. signal-processing functions that take spans work on a frame row, a `std::array` in a unit test, a `pmr::vector`, or a DMA buffer the driver mapped into memory. if they took `const std::vector<float>&`, every caller would need a `std::vector`, and you would copy a DMA buffer into one just to call a function. the frame keeps ownership and the invariant (rows have `range_bins_` cells); the algorithms borrow.

### watch out for

**dangling, and the const case that compiles.** `std::span<float> s = make_samples();` is rejected: a mutable span cannot bind to a temporary container. but a span of `const` elements can, by design (so that `rms(make_samples())` works as a function argument):

```cpp
std::vector<float> make_samples();
std::span<const float> s = make_samples();   // BUG: compiles; the vector dies at the semicolon
float first = s[0];                          // UB: reads freed memory
```

GCC 12 compiles this without a warning. the same goes for a span into a vector that later reallocates (`push_back` after taking the span): the span holds the old pointer. treat a span like a reference: fine as a parameter, suspicious as a local initialized from a function call, and a design decision as a data member.

### the takeaway

replace pointer-plus-length parameters with `std::span<const T>` (read) or `std::span<T>` (write), pass it by value, use a static extent when the size is part of the contract, and never let a span outlive the buffer it borrows.

### optional challenge

which of these compile, and which are correct?

```cpp
std::vector<float> v{1.f, 2.f};
std::span<float>          a = make_samples();            // 1
std::span<const float>    b = make_samples();            // 2
std::span<const float, 4> c = std::array<float, 4>{};    // 3
const std::span<float>    d = v;  d[0] = 9.f;            // 4
```

<details>
<summary>answer</summary>

1 does not compile: a span of mutable elements cannot be constructed from an rvalue `std::vector` (it is not a borrowed range). 2 compiles and dangles. 3 compiles too, through the constructor taking `const std::array<T, N>&`, and dangles just the same: the temporary array dies at the end of the declaration. 4 compiles and is correct: the span object is `const`, its elements are not, so `v[0]` becomes `9`. all four were checked with GCC 12, which warns about none of them.

</details>

### going deeper

#### bytes for serialization

```cpp
#include <cstdint>

struct TelemetryPacket {
    std::uint32_t seq;
    float         temperature_c;
    std::uint16_t status;
};   // sizeof is 12 with GCC 12 on x86-64: 10 bytes of members, 2 of padding

void append(std::vector<std::byte>& wire, const TelemetryPacket& pkt) {
    auto bytes = std::as_bytes(std::span{&pkt, 1});   // span<const std::byte>, 12 bytes here
    wire.insert(wire.end(), bytes.begin(), bytes.end());
}
```

`as_bytes` is the honest version of `reinterpret_cast<const char*>(&pkt)`: reading any object's bytes through `std::byte` is allowed. what it does not fix is the wire format. the layout of `TelemetryPacket` (padding, byte order, the representation of `float`) is implementation-defined, and the two padding bytes hold indeterminate values (copying them as `std::byte` is allowed, but they are garbage), so you are shipping noise and an ABI-specific layout. that is acceptable for a same-machine ring buffer or shared memory; it is not a protocol. for a real protocol, serialize field by field in a defined byte order.

#### span, string_view, and range views

compared with neighbors: `std::string_view` is a read-only span of characters with string operations; `std::span` is any `T`, mutable or not, and has no comparison operators (use `std::ranges::equal`). range views ([[views]]) are lazy computations over any range; a span is just memory, and it requires contiguity.

#### a `const` span is not a span of `const`

**`const` is shallow.** `const std::span<float> s` makes the span itself immutable (you cannot reseat it), but `s[0] = 1.f` still compiles. read-only access is spelled `std::span<const float>`. this is the same distinction as `T* const` versus `const T*` from [[const-correctness]].
