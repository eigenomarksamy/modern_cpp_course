---
title: SOLID as heuristics, not rules
standard: C++17
objective: read the five SOLID principles as predictions about the cost of change, and separate responsibilities where change actually happens
prerequisites: composition-over-inheritance, ownership-in-interfaces
difficulty: 2
---

### the idea

every codebase has a class that everybody touches. in a radar team it might be `TrackFileProcessor`: it opens the recording, parses binary frames, drops low-SNR detections, converts units, and writes CSV. a new file format, a new filter threshold, and a new output column are three unrelated changes, made by three people, all landing in the same 900-line file and the same merge conflicts.

SOLID is usually presented as five rules that fix this. it is more useful to read the five letters as heuristics about one question: when a requirement changes, how much code has to change with it, and how much has to be recompiled, retested, and redeployed?

### understanding the concept

each principle in one sentence, phrased as the change it protects you from:

| principle | one-sentence version | the change it absorbs |
|---|---|---|
| single responsibility (SRP) | a module should have one reason to change, meaning one group of people or one requirement driving it | a format change does not touch filtering |
| open/closed (OCP) | you can add behaviour by adding code rather than editing working code | a new sensor type is a new class or a new variant alternative, not a new `case` in ten switches |
| Liskov substitution (LSP) | a derived type must honour the base contract, not just its signatures ([[composition-over-inheritance]]) | callers of `Sensor::read()` keep working with every sensor |
| interface segregation (ISP) | clients should not depend on functions they do not call | a change to calibration does not recompile the planner |
| dependency inversion (DIP) | high-level policy should depend on an abstraction it owns, and low-level detail should implement it | swapping the map backend does not touch the planner |

### in code

**SRP: separate the decision from the plumbing.** the before version mixes I/O, parsing, and policy, so you cannot test the filter without a file on disk.

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

```cpp complete
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

notice what we did not do: no `IDetectionFilter` interface, no factory. the responsibilities are separated by plain functions and a small value type. an abstraction can come later if a second filter actually appears.

### in practice

a common failure mode in robotics stacks is the opposite of the god class: every concrete class gets an `I`-prefixed interface, a mock, and a factory, "for testability". after a year the codebase has 300 interfaces with exactly one production implementation each. reading the control flow means jumping through an interface, a factory, and a registry to find the one class that actually runs. every signature change is made twice. the mocks encode call sequences, so refactors break tests that did not catch any bug.

a better default is **the smallest thing that keeps options open**:

- start concrete. pure functions and value types are already decoupled and testable.
- introduce an interface at a *real* seam: hardware, time, network, filesystem, a third-party library, or a point where you genuinely have two implementations today.
- let the consumer own the interface, and keep it as narrow as that consumer needs.
- keep headers lean, because the build graph is part of the architecture.

YAGNI ("you aren't gonna need it") is the counterweight to OCP. being open for extension in a direction nobody extends costs indirection forever. extracting an interface from concrete code when the second implementation arrives is usually a short, mechanical refactor; removing a speculative abstraction that ten modules depend on is not.

### watch out for

the principles conflict, and following one to the extreme violates another. taken literally, SRP produces dozens of one-method classes, which raises coupling between them because every behaviour now needs five collaborators wired together. OCP via virtual dispatch hides control flow: the debugger shows `filter->apply()`, and you need runtime state to know what ran. DIP through a virtual interface also has a mechanism cost (an indirect call that usually cannot be inlined); in a 1 kHz control loop that is almost never the bottleneck, but in a per-sample inner loop over millions of samples it can be, so measure with a profiler before and after rather than guessing.

also notice that "reason to change" is about people and requirements, not about counting methods. a `Quaternion` class with 40 methods is cohesive: it all changes when the math changes, which is never.

### the takeaway

SOLID is a set of tools for predicting the cost of change: use them to place seams where change actually happens, let the consumer own the interface, and keep everything else concrete and boring.

### optional challenge

a `MotorController` class has methods `set_torque`, `read_encoder`, `log_to_file`, `load_gains_from_yaml`, and `publish_diagnostics_over_udp`. which of these would you pull out first, and which principle are you really applying?

<details>
<summary>answer</summary>

the control core is `set_torque` and `read_encoder`: they share state and change with the control law. `log_to_file`, `load_gains_from_yaml`, and `publish_diagnostics_over_udp` each change for a different reason (logging policy, config format, network protocol) and drag in heavy dependencies (filesystem, a YAML parser, sockets) that make the controller hard to build and test. pull the YAML loading out first: it is pure input conversion and can become a free function returning a `Gains` value, which the controller accepts in its constructor. that is SRP, but the practical win is physical: the controller no longer includes the YAML library, so it compiles faster and can be tested without files. diagnostics and logging can become an injected sink ([[dependency-injection]]) once you need to swap them.

</details>
