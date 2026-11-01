---
title: API and ABI stability: pimpl and deprecation
standard: C++20
objective: distinguish API from ABI stability, use the pimpl idiom as a compile-time and binary firewall, and evolve an interface without breaking callers
prerequisites: api-contracts, coupling-cohesion, unique-ptr
difficulty: 3
---

### the idea

a library that is compiled together with its users can change freely, as long as the source still compiles. a library shipped as a binary, a `.so` or `.dll` that integrators link against without recompiling, makes a much stricter promise: the *layout* of every public class, the set of its virtual functions, and the code of every inline function are now part of the contract. most of the techniques in this lesson exist to keep that promise without freezing the code.

### understanding the concept

finally, separate **API** stability (source code that compiled against version 1 still compiles against version 2) from **ABI** stability (binaries built against version 1 still link and run against version 2's shared library). ABI is much more fragile: changing a class's size, the order of its members, its virtual functions, or an inline function's body breaks it, even when the source-level API is unchanged.

### in code

**the pimpl idiom: a compile-time and ABI firewall.**

```cpp complete
// lidar_driver.h: the only thing clients see
#pragma once
#include <cstddef>
#include <memory>
#include <span>
#include <string_view>

class LidarDriver {
public:
    explicit LidarDriver(std::string_view device);
    ~LidarDriver();                                   // declared here, defined in the .cpp
    LidarDriver(LidarDriver&&) noexcept;
    LidarDriver& operator=(LidarDriver&&) noexcept;

    [[nodiscard]] std::size_t read_scan(std::span<float> ranges_out);
    [[nodiscard]] bool healthy() const;

private:
    struct Impl;                                      // incomplete in every client
    std::unique_ptr<Impl> impl_;
};
```

```cpp external
// lidar_driver.cpp: vendor SDK headers and private state live here
#include "lidar_driver.h"
#include <algorithm>
#include <string>
#include <vector>

struct LidarDriver::Impl {
    std::string device;
    std::vector<float> last_scan = std::vector<float>(360, 5.0f);
    int error_count = 0;
};

LidarDriver::LidarDriver(std::string_view device)
    : impl_(std::make_unique<Impl>(Impl{std::string(device)})) {}
LidarDriver::~LidarDriver() = default;                // Impl is complete here
LidarDriver::LidarDriver(LidarDriver&&) noexcept = default;
LidarDriver& LidarDriver::operator=(LidarDriver&&) noexcept = default;

std::size_t LidarDriver::read_scan(std::span<float> out) {
    const std::size_t n = std::min(out.size(), impl_->last_scan.size());
    std::copy_n(impl_->last_scan.begin(), n, out.begin());
    return n;
}
bool LidarDriver::healthy() const { return impl_->error_count == 0; }
```

why the out-of-line destructor? `std::unique_ptr<Impl>` deletes through `std::default_delete<Impl>`, and the program is ill-formed if `Impl` is incomplete at that point. if you let the compiler define `~LidarDriver` implicitly, it is defined inline in every client translation unit, where `Impl` is incomplete, and compilation fails. declaring the destructor (and the move operations, which also need to destroy an `Impl`) in the header and defaulting them in the `.cpp` puts the definitions where `Impl` is complete.

what you get: clients never include the vendor SDK, editing `Impl` recompiles one file, and `sizeof(LidarDriver)` stays one `unique_ptr` regardless of private state, so adding a private member does not change the class layout that client binaries were compiled against. what you pay: one heap allocation per object, an extra indirection on every member access, and no inlining of member functions into callers (unless link-time optimization does it).

**evolving an API without breaking callers.**

```cpp complete
#include <cstddef>
#include <span>

class LidarDriverV2 {
public:
    [[nodiscard]] std::size_t read_scan(std::span<float> ranges_out);

    [[deprecated("use read_scan(std::span<float>); removed in 3.0")]]
    int read_scan(float* out, int max_count) {
        return static_cast<int>(read_scan(std::span<float>(out, static_cast<std::size_t>(max_count))));
    }
};
```

the old overload keeps source compatibility for a release cycle, warns at every call site, and forwards to the new implementation so there is only one code path.

### in practice

a radar vendor ships `libradar.so` to integrators who cannot recompile when it updates. that makes every public header a binary contract. typical rules on such teams: public classes are pimpl or abstract interfaces with a factory, no inline functions that touch private data, no standard-library types across the boundary unless every party uses the same toolchain and standard library build (libstdc++'s `std::string` changed layout in GCC 5, which is why it ships a dual ABI), and a symbol-visibility policy that exports only the intended API.

### watch out for

**`const` does not propagate through pimpl.** inside `healthy() const`, `impl_` is a `const std::unique_ptr<Impl>`, but `*impl_` is a non-const `Impl&`, so a const member function can modify private state without a compiler complaint. add a pair of private accessors (`Impl& impl()` and `const Impl& impl() const`) and use them everywhere instead of `impl_` directly. also, a moved-from `LidarDriver` has a null `impl_`; calling `read_scan` on it dereferences null (undefined behavior), so document that a moved-from driver may only be destroyed or assigned to, or check in every member.

### the takeaway

a shipped shared library promises an ABI, which is far stricter than an API: hide private state behind pimpl or abstract interfaces, keep inline code out of public headers, and evolve through deprecation rather than silent change.

### optional challenge

`libradar.so` exports a class `Tracker` that is *not* pimpl. which of these changes break binaries compiled against the previous version?

1. adding a private data member
2. adding a member to the private `Impl` struct of another, pimpl class
3. adding a new virtual function at the end of `Tracker`'s existing ones
4. adding a new non-virtual, non-inline member function
5. changing the body of an inline member function defined in the header

<details>
<summary>answer</summary>

(1) breaks: `sizeof(Tracker)` and possibly member offsets change, and clients allocated the old size. (2) is safe: only the library sees `Impl`. (3) is risky: it changes the vtable, which breaks any client class that derives from `Tracker` (its own virtual functions shift) and is implementation-specific even without derivation; treat it as breaking. (4) is safe: it adds a symbol without changing existing ones. (5) is the subtle one: old clients keep the old inline code compiled into their own binaries, so two versions of the function now coexist, which is an ODR problem and a behavior mismatch, not a link error.

</details>
