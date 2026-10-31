<a id="day-43"></a>

## day 43: SOLID, coupling, and cohesion without dogma

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days 11, 12, 13

### the idea

Every codebase has a class that everybody touches. In a radar team it might be `TrackFileProcessor`: it opens the recording, parses binary frames, drops low-SNR detections, converts units, and writes CSV. A new file format, a new filter threshold, and a new output column are three unrelated changes, made by three people, all landing in the same 900-line file and the same merge conflicts.

SOLID is usually presented as five rules that fix this. It is more useful to read the five letters as heuristics about one question: when a requirement changes, how much code has to change with it, and how much has to be recompiled, retested, and redeployed?

### understanding the concept

Each principle in one sentence, phrased as the change it protects you from:

| principle | one-sentence version | the change it absorbs |
|---|---|---|
| single responsibility (SRP) | a module should have one reason to change, meaning one group of people or one requirement driving it | a format change does not touch filtering |
| open/closed (OCP) | you can add behaviour by adding code rather than editing working code | a new sensor type is a new class or a new variant alternative, not a new `case` in ten switches |
| Liskov substitution (LSP) | a derived type must honour the base contract, not just its signatures (day 13) | callers of `Sensor::read()` keep working with every sensor |
| interface segregation (ISP) | clients should not depend on functions they do not call | a change to calibration does not recompile the planner |
| dependency inversion (DIP) | high-level policy should depend on an abstraction it owns, and low-level detail should implement it | swapping the map backend does not touch the planner |

Two older ideas sit underneath all five. **Coupling** is the degree to which two pieces of code must change together. **Cohesion** is the degree to which the things inside one piece belong together, meaning they change for the same reasons and use the same data. Good design is high cohesion inside a module and low coupling between modules. SOLID is mostly a list of tactics for those two goals.

C++ adds a dimension most languages hide: **physical coupling**. Every `#include` in a header is a compile-time dependency for every file that includes that header, transitively. A logical design can look clean on a whiteboard while one widely included header pulls a heavy linear-algebra header into 400 translation units. That cost shows up as build times and as rebuild cascades when someone edits a private detail. Logical coupling decides what has to change together; physical coupling decides what has to recompile together.

### in code

**SRP: separate the decision from the plumbing.** The before version mixes I/O, parsing, and policy, so you cannot test the filter without a file on disk.

```cpp
// before: three reasons to change in one function
void process_track_file(const std::string& in_path, const std::string& out_path) {
    std::ifstream in(in_path, std::ios::binary);
    std::ofstream out(out_path);
    RawFrame frame;
    while (in.read(reinterpret_cast<char*>(&frame), sizeof frame)) {  // format
        if (frame.snr_db < 12.0f) continue;                           // policy
        out << frame.range_m << ',' << frame.azimuth_deg << '\n';     // output
    }
}
```

```cpp
#include <algorithm>
#include <iterator>
#include <vector>

struct Detection { float range_m, azimuth_deg, snr_db; };

// policy: pure, cohesive, trivially unit-testable
struct SnrGate {
    float min_snr_db;
    bool accept(const Detection& d) const { return d.snr_db >= min_snr_db; }
};

std::vector<Detection> gate(const std::vector<Detection>& in, SnrGate g) {
    std::vector<Detection> out;
    std::copy_if(in.begin(), in.end(), std::back_inserter(out),
                 [&](const Detection& d) { return g.accept(d); });
    return out;
}

// format and output live in their own functions (or files), e.g.
// std::optional<Detection> parse_frame(const std::byte* p, std::size_t n);
// void write_csv(std::ostream& os, const std::vector<Detection>& ds);
```

Notice what we did not do: no `IDetectionFilter` interface, no factory. The responsibilities are separated by plain functions and a small value type. An abstraction can come later if a second filter actually appears.

**ISP and DIP: let the client define the interface.** A path planner that takes the whole robot couples to everything the robot can do.

```cpp
// before: the planner sees calibration, firmware update, and motor control
class Robot {
public:
    virtual ~Robot() = default;
    virtual bool is_occupied(int x, int y) const = 0;
    virtual void calibrate_lidar() = 0;
    virtual void flash_firmware(const std::vector<unsigned char>& image) = 0;
    virtual void set_wheel_speeds(double left, double right) = 0;
};
std::vector<Cell> plan(const Robot& robot, Cell from, Cell to);
```

```cpp
// after: the planner owns the narrow interface it needs (DIP),
// and nothing else leaks into it (ISP)
struct Cell { int x, y; };

class OccupancyQuery {        // lives in the planner's header, not the robot's
public:
    virtual ~OccupancyQuery() = default;
    virtual bool is_occupied(Cell c) const = 0;
};

std::vector<Cell> plan(const OccupancyQuery& map, Cell from, Cell to);

// the low-level module depends upward on the planner's abstraction
class GridMap final : public OccupancyQuery {
public:
    GridMap(int width, int height) : width_(width), cells_(std::size_t(width) * height) {}
    bool is_occupied(Cell c) const override {
        return cells_[std::size_t(c.y) * width_ + c.x] != 0;  // caller keeps c in range
    }
private:
    int width_;
    std::vector<unsigned char> cells_;
};
```

The key detail of DIP is *ownership* of the interface. If `OccupancyQuery` lived in the map library, the planner would still depend on the map library. Putting it next to the planner reverses the arrow: the map adapts to the planner, and a test can pass a ten-line fake (day 44 builds on exactly this).

**Physical coupling: keep headers light.** A header only needs a full definition when it uses the size or members of a type.

```cpp
// tracker.h
#pragma once
#include <memory>
#include <vector>

class KalmanFilter;           // forward declaration: no heavy include here
struct Detection;

class Tracker {
public:
    explicit Tracker(std::shared_ptr<const KalmanFilter> model);
    void update(const std::vector<Detection>& detections);  // incomplete type is fine in a declaration
private:
    std::shared_ptr<const KalmanFilter> model_;  // fine with an incomplete type
};                                               // (a unique_ptr member needs more care: day 47)
// tracker.cpp includes "kalman_filter.h" and "detection.h"
```

Now editing `kalman_filter.h` rebuilds `tracker.cpp`, not every file that includes `tracker.h`. Day 47 takes this further with pimpl.

### in practice

A common failure mode in robotics stacks is the opposite of the god class: every concrete class gets an `I`-prefixed interface, a mock, and a factory, "for testability". After a year the codebase has 300 interfaces with exactly one production implementation each. Reading the control flow means jumping through an interface, a factory, and a registry to find the one class that actually runs. Every signature change is made twice. The mocks encode call sequences, so refactors break tests that did not catch any bug.

A better default is **the smallest thing that keeps options open**:

- Start concrete. Pure functions and value types are already decoupled and testable.
- Introduce an interface at a *real* seam: hardware, time, network, filesystem, a third-party library, or a point where you genuinely have two implementations today.
- Let the consumer own the interface, and keep it as narrow as that consumer needs.
- Keep headers lean, because the build graph is part of the architecture.

YAGNI ("you aren't gonna need it") is the counterweight to OCP. Being open for extension in a direction nobody extends costs indirection forever. Extracting an interface from concrete code when the second implementation arrives is usually a short, mechanical refactor; removing a speculative abstraction that ten modules depend on is not.

### watch out for

The principles conflict, and following one to the extreme violates another. Taken literally, SRP produces dozens of one-method classes, which raises coupling between them because every behaviour now needs five collaborators wired together. OCP via virtual dispatch hides control flow: the debugger shows `filter->apply()`, and you need runtime state to know what ran. DIP through a virtual interface also has a mechanism cost (an indirect call that usually cannot be inlined); in a 1 kHz control loop that is almost never the bottleneck, but in a per-sample inner loop over millions of samples it can be, so measure with a profiler before and after rather than guessing.

Also notice that "reason to change" is about people and requirements, not about counting methods. A `Quaternion` class with 40 methods is cohesive: it all changes when the math changes, which is never.

### the takeaway

SOLID, coupling, and cohesion are tools for predicting the cost of change. Use them to place seams where change actually happens, keep the rest concrete and boring, and remember that in C++ your header graph is part of your design.

### optional challenge

A `MotorController` class has methods `set_torque`, `read_encoder`, `log_to_file`, `load_gains_from_yaml`, and `publish_diagnostics_over_udp`. Which of these would you pull out first, and which principle are you really applying?

<details>
<summary>answer</summary>

The control core is `set_torque` and `read_encoder`: they share state and change with the control law. `log_to_file`, `load_gains_from_yaml`, and `publish_diagnostics_over_udp` each change for a different reason (logging policy, config format, network protocol) and drag in heavy dependencies (filesystem, a YAML parser, sockets) that make the controller hard to build and test. Pull the YAML loading out first: it is pure input conversion and can become a free function returning a `Gains` value, which the controller accepts in its constructor. That is SRP, but the practical win is physical: the controller no longer includes the YAML library, so it compiles faster and can be tested without files. Diagnostics and logging can become an injected sink (day 44) once you need to swap them.

</details>
