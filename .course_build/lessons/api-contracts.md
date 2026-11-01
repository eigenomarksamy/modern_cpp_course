---
title: designing APIs that are hard to misuse
standard: C++20
objective: push an API's contract into its types with strong types, enums, views, and explicit error channels, so wrong calls fail to compile
prerequisites: dependency-injection, span, error-strategy, defaulted-comparisons
difficulty: 2
---

### the idea

```cpp
bool move_joint(int joint, double position, double velocity, double timeout);

move_joint(2, 1.5, 0.5, 30);    // radians? degrees? 30 seconds or 30 ms? did it fail?
```

this compiles whether you swap position and velocity, pass degrees, or ignore the result. every one of those mistakes is a bug that only shows up on the robot. a good API makes the correct call easy to write and the wrong call hard to write, ideally impossible to compile. today is about the tools C++ gives you for that, and about the extra promise a library makes once it ships as a binary.

### understanding the concept

an API is a contract with three parts. **preconditions** are what the caller must guarantee (the joint index exists, the span is non-empty). **postconditions** are what the function guarantees on success (the joint reached the target within tolerance). **invariants** are what is always true of an object between calls (a `Trajectory` is time-ordered). C++20 has no language feature for contracts; C++26 adds `pre`, `post`, and `contract_assert`, but in C++20 you have, in decreasing order of strength:

1. **types** that make violations unrepresentable: strong types, enums instead of `bool` flags, `std::span` instead of pointer plus length.
2. **construction** that establishes invariants (a constructor that validates, or a factory returning `std::optional`).
3. **assertions** for preconditions you cannot encode in types.
4. **documentation** for the rest.

the signature itself is part of the contract. the ownership rules from [[ownership-in-interfaces]] and the view types from the C++17 and C++20 modules give a compact vocabulary:

| parameter | tells the caller |
|---|---|
| `T` (cheap or sink) | "I take my own copy" |
| `const T&` | "I read it during the call and keep nothing" |
| `std::string_view`, `std::span<const T>` | "I borrow a sequence for the duration of the call" |
| `T*` | "may be null, I do not own it" |
| `std::unique_ptr<T>` by value | "ownership transfers to me" |
| `std::shared_ptr<T>` by value | "I will share ownership beyond this call" |

then choose **one error channel per kind of failure** and use it consistently across the API ([[error-strategy]]): exceptions for failures the immediate caller cannot handle, return values (`std::optional`, a `std::variant` or small result type, an error code) for expected outcomes such as a sensor timeout. mark those return types or functions `[[nodiscard]]` so ignoring them is a warning. (`std::expected` is the standard result type in C++23.)

### in code

**strong types and enums at the call site.**

```cpp complete
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

each `struct ...Tag` declared inside the template argument creates a distinct type, so `Radians` and `RadiansPerSecond` do not mix. `std::chrono` already does this for time, including safe conversion from seconds to milliseconds. for real unit algebra (meters divided by seconds giving meters per second) use a units library such as mp-units rather than growing this template. the `JointId{2}` form uses C++17's rule that an enum with a fixed underlying type can be list-initialized from an integer, while `JointId j = 2;` is still an error.

one honest weakness: `std::optional<MoveError>` reads backwards (an engaged optional means failure). a small result type with a named `ok()` member, or C++23 `std::expected<void, MoveError>`, says it better.

### in practice

then there is **Hyrum's law**: with enough users, every observable behavior of your API will be depended on by somebody, whether or not you promised it. if `get_detections()` happened to return detections sorted by range for three years, someone's tracker now assumes it, and "unsorted" becomes a breaking change. document what is guaranteed, and where order or timing is not guaranteed, consider making that visible early (some libraries deliberately randomize iteration order for this reason).

### watch out for

**not every class needs this.** pimpl, strong types, and result types each add code. use them on boundaries: public library headers, hardware interfaces, and functions where swapping two arguments is plausible. internal helpers with one caller can stay plain.

### the takeaway

push contracts into types first, assertions second, and comments last; make ownership, borrowing, and failure visible in the signature, and pick one error channel per kind of failure.

### optional challenge

list what is wrong with this public function from a deployment tool, and sketch a better signature: `bool deploy(char* host, int port, double timeout, bool force, bool dry_run);`

<details>
<summary>answer</summary>

`char*` says nothing about ownership or null termination, and non-const suggests the function may modify the string: take `std::string_view`. `double timeout` has no unit: use `std::chrono::milliseconds` (or `seconds`). two adjacent `bool` flags are easy to swap and unreadable at the call site (`deploy(h, 22, 30, true, false)`): use enums such as `enum class Mode { apply, dry_run }` and `enum class Conflict { abort, overwrite }`, or a small options struct with designated initializers (C++20). the `bool` return hides why it failed and is easy to ignore: return a `[[nodiscard]]` result carrying an error enum and message. port could be a `std::uint16_t` or a strong `Port` type. for example: `[[nodiscard]] DeployResult deploy(std::string_view host, std::uint16_t port, const DeployOptions& opts);` with `DeployOptions{.timeout = 30s, .mode = Mode::dry_run}` at the call site.

</details>
