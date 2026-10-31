<a id="day-47"></a>

## day 47: designing APIs that are hard to misuse

**reading time:** about 9 minutes · **standard:** C++20 · **builds on:** days 04, 12, 20, 26, 31

### the idea

```cpp
bool move_joint(int joint, double position, double velocity, double timeout);

move_joint(2, 1.5, 0.5, 30);    // radians? degrees? 30 seconds or 30 ms? did it fail?
```

This compiles whether you swap position and velocity, pass degrees, or ignore the result. Every one of those mistakes is a bug that only shows up on the robot. A good API makes the correct call easy to write and the wrong call hard to write, ideally impossible to compile. Today is about the tools C++ gives you for that, and about the extra promise a library makes once it ships as a binary.

### understanding the concept

An API is a contract with three parts. **Preconditions** are what the caller must guarantee (the joint index exists, the span is non-empty). **Postconditions** are what the function guarantees on success (the joint reached the target within tolerance). **Invariants** are what is always true of an object between calls (a `Trajectory` is time-ordered). C++20 has no language feature for contracts; C++26 adds `pre`, `post`, and `contract_assert`, but in C++20 you have, in decreasing order of strength:

1. **Types** that make violations unrepresentable: strong types, enums instead of `bool` flags, `std::span` instead of pointer plus length.
2. **Construction** that establishes invariants (a constructor that validates, or a factory returning `std::optional`).
3. **Assertions** for preconditions you cannot encode in types.
4. **Documentation** for the rest.

The signature itself is part of the contract. Day 12's ownership rules and week 4 and 5's view types give a compact vocabulary:

| parameter | tells the caller |
|---|---|
| `T` (cheap or sink) | "I take my own copy" |
| `const T&` | "I read it during the call and keep nothing" |
| `std::string_view`, `std::span<const T>` | "I borrow a sequence for the duration of the call" |
| `T*` | "may be null, I do not own it" |
| `std::unique_ptr<T>` by value | "ownership transfers to me" |
| `std::shared_ptr<T>` by value | "I will share ownership beyond this call" |

Then choose **one error channel per kind of failure** and use it consistently across the API (day 20): exceptions for failures the immediate caller cannot handle, return values (`std::optional`, a `std::variant` or small result type, an error code) for expected outcomes such as a sensor timeout. Mark those return types or functions `[[nodiscard]]` so ignoring them is a warning. (`std::expected` is the standard result type in C++23.)

Finally, separate **API** stability (source code that compiled against version 1 still compiles against version 2) from **ABI** stability (binaries built against version 1 still link and run against version 2's shared library). ABI is much more fragile: changing a class's size, the order of its members, its virtual functions, or an inline function's body breaks it, even when the source-level API is unchanged.

### in code

**Strong types and enums at the call site.**

```cpp
#include <chrono>
#include <compare>
#include <cstdint>
#include <optional>

template <typename Tag>
struct Quantity {
    double value;
    constexpr explicit Quantity(double v) : value(v) {}
    friend constexpr Quantity operator+(Quantity a, Quantity b) { return Quantity(a.value + b.value); }
    friend constexpr auto operator<=>(Quantity, Quantity) = default;
};
using Radians          = Quantity<struct RadiansTag>;
using RadiansPerSecond = Quantity<struct RadiansPerSecondTag>;

enum class JointId : std::uint8_t {};
enum class MoveError { unreachable, timeout, estop_active };

struct MoveRequest {
    Radians target;
    RadiansPerSecond max_speed;
    std::chrono::milliseconds timeout;
};

[[nodiscard]] std::optional<MoveError> move_joint(JointId joint, const MoveRequest& req);

// move_joint(JointId{2}, {Radians(1.5), RadiansPerSecond(0.5), std::chrono::seconds(30)});
// move_joint(JointId{2}, {RadiansPerSecond(0.5), Radians(1.5), ...});  // does not compile
// move_joint(2, ...);                                                    // does not compile
```

Each `struct ...Tag` declared inside the template argument creates a distinct type, so `Radians` and `RadiansPerSecond` do not mix. `std::chrono` already does this for time, including safe conversion from seconds to milliseconds. For real unit algebra (meters divided by seconds giving meters per second) use a units library such as mp-units rather than growing this template. The `JointId{2}` form uses C++17's rule that an enum with a fixed underlying type can be list-initialized from an integer, while `JointId j = 2;` is still an error.

One honest weakness: `std::optional<MoveError>` reads backwards (an engaged optional means failure). A small result type with a named `ok()` member, or C++23 `std::expected<void, MoveError>`, says it better.

**The pimpl idiom: a compile-time and ABI firewall.**

```cpp
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

```cpp
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

Why the out-of-line destructor? `std::unique_ptr<Impl>` deletes through `std::default_delete<Impl>`, and the program is ill-formed if `Impl` is incomplete at that point. If you let the compiler define `~LidarDriver` implicitly, it is defined inline in every client translation unit, where `Impl` is incomplete, and compilation fails. Declaring the destructor (and the move operations, which also need to destroy an `Impl`) in the header and defaulting them in the `.cpp` puts the definitions where `Impl` is complete.

What you get: clients never include the vendor SDK, editing `Impl` recompiles one file, and `sizeof(LidarDriver)` stays one `unique_ptr` regardless of private state, so adding a private member does not change the class layout that client binaries were compiled against. What you pay: one heap allocation per object, an extra indirection on every member access, and no inlining of member functions into callers (unless link-time optimization does it).

**Evolving an API without breaking callers.**

```cpp
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

The old overload keeps source compatibility for a release cycle, warns at every call site, and forwards to the new implementation so there is only one code path.

### in practice

A radar vendor ships `libradar.so` to integrators who cannot recompile when it updates. That makes every public header a binary contract. Typical rules on such teams: public classes are pimpl or abstract interfaces with a factory, no inline functions that touch private data, no standard-library types across the boundary unless every party uses the same toolchain and standard library build (libstdc++'s `std::string` changed layout in GCC 5, which is why it ships a dual ABI), and a symbol-visibility policy that exports only the intended API.

Then there is **Hyrum's law**: with enough users, every observable behavior of your API will be depended on by somebody, whether or not you promised it. If `get_detections()` happened to return detections sorted by range for three years, someone's tracker now assumes it, and "unsorted" becomes a breaking change. Document what is guaranteed, and where order or timing is not guaranteed, consider making that visible early (some libraries deliberately randomize iteration order for this reason).

### watch out for

**`const` does not propagate through pimpl.** Inside `healthy() const`, `impl_` is a `const std::unique_ptr<Impl>`, but `*impl_` is a non-const `Impl&`, so a const member function can modify private state without a compiler complaint. Add a pair of private accessors (`Impl& impl()` and `const Impl& impl() const`) and use them everywhere instead of `impl_` directly. Also, a moved-from `LidarDriver` has a null `impl_`; calling `read_scan` on it dereferences null (undefined behavior), so document that a moved-from driver may only be destroyed or assigned to, or check in every member.

**Not every class needs this.** Pimpl, strong types, and result types each add code. Use them on boundaries: public library headers, hardware interfaces, and functions where swapping two arguments is plausible. Internal helpers with one caller can stay plain.

### the takeaway

Push contracts into types first, assertions second, and comments last. Make ownership, borrowing, and failure visible in the signature, pick one error channel per kind of failure, and remember that a shipped shared library promises an ABI, which is far stricter than an API.

### optional challenge

List what is wrong with this public function from a deployment tool, and sketch a better signature: `bool deploy(char* host, int port, double timeout, bool force, bool dry_run);`

<details>
<summary>answer</summary>

`char*` says nothing about ownership or null termination, and non-const suggests the function may modify the string: take `std::string_view`. `double timeout` has no unit: use `std::chrono::milliseconds` (or `seconds`). Two adjacent `bool` flags are easy to swap and unreadable at the call site (`deploy(h, 22, 30, true, false)`): use enums such as `enum class Mode { apply, dry_run }` and `enum class Conflict { abort, overwrite }`, or a small options struct with designated initializers (C++20). The `bool` return hides why it failed and is easy to ignore: return a `[[nodiscard]]` result carrying an error enum and message. Port could be a `std::uint16_t` or a strong `Port` type. For example: `[[nodiscard]] DeployResult deploy(std::string_view host, std::uint16_t port, const DeployOptions& opts);` with `DeployOptions{.timeout = 30s, .mode = Mode::dry_run}` at the call site.

</details>
