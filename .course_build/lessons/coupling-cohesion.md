---
title: coupling, cohesion, and physical design
standard: C++17
objective: judge a design by what must change and what must recompile together, invert dependencies with consumer-owned interfaces, and keep headers light
prerequisites: solid, linkage-odr
difficulty: 2
---

### the idea

two modules that look independent on an architecture diagram can still be welded together: change one header, and four hundred files recompile; change one data format, and three teams edit the same file. the vocabulary for this is older than SOLID and more general: coupling and cohesion. C++ adds a dimension that most languages hide, because its build model makes every `#include` a dependency you pay for in compile time.

### understanding the concept

two older ideas sit underneath all five. **coupling** is the degree to which two pieces of code must change together. **cohesion** is the degree to which the things inside one piece belong together, meaning they change for the same reasons and use the same data. good design is high cohesion inside a module and low coupling between modules. SOLID is mostly a list of tactics for those two goals.

C++ adds a dimension most languages hide: **physical coupling**. every `#include` in a header is a compile-time dependency for every file that includes that header, transitively. a logical design can look clean on a whiteboard while one widely included header pulls a heavy linear-algebra header into 400 translation units. that cost shows up as build times and as rebuild cascades when someone edits a private detail. logical coupling decides what has to change together; physical coupling decides what has to recompile together.

### in code

**ISP and DIP: let the client define the interface.** a path planner that takes the whole robot couples to everything the robot can do.

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

the key detail of DIP is *ownership* of the interface. if `OccupancyQuery` lived in the map library, the planner would still depend on the map library. putting it next to the planner reverses the arrow: the map adapts to the planner, and a test can pass a ten-line fake ([[dependency-injection]] builds on exactly this).

**physical coupling: keep headers light.** a header only needs a full definition when it uses the size or members of a type.

```cpp external
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
};                                               // (a unique_ptr member needs more care: see pimpl)
// tracker.cpp includes "kalman_filter.h" and "detection.h"
```

now editing `kalman_filter.h` rebuilds `tracker.cpp`, not every file that includes `tracker.h`. [[api-stability]] takes this further with pimpl.

### in practice

in a large C++ codebase, the build graph is something you can measure and manage like any other architecture. the questions worth asking of a widely included header are: what does it include, and does each include provide something the header itself uses by size or by member? replace includes with forward declarations where a pointer, reference, or function declaration suffices; move implementation-only includes into the `.cpp`; and split headers that serve unrelated clients (a header with both the public API and the test helpers forces both on everyone). GCC's `-H` flag prints the include tree of a translation unit, and Clang's `-ftime-trace` shows where compile time goes, which turns "this build feels slow" into a list of specific headers.

### watch out for

**relying on transitive includes.** a file that uses `std::vector` but compiles only because some other header it includes happens to include `<vector>` is coupled to that other header's private choices. the day that header switches to a forward declaration (exactly the improvement this lesson recommends), unrelated files stop compiling. "include what you use": every file includes the headers for the names it uses directly. tools such as include-what-you-use and `clang-tidy`'s `misc-include-cleaner` check it mechanically.

### the takeaway

coupling is what must change together and cohesion is what belongs together; in C++, also ask what must recompile together, because your header graph is part of your design.

### optional challenge

`tracker.h` is included by 300 files. which of these edits to it force all 300 to recompile, and which change the class layout that compiled clients depend on?

1. adding a private data member to `Tracker`
2. adding a private non-virtual member function declaration
3. changing a member function's body, which is defined in `tracker.cpp`
4. changing the default argument of a public member function

<details>
<summary>answer</summary>

with a typical timestamp-based build, (1), (2), and (4) recompile all 300 files, because the header's text changed; (3) recompiles only `tracker.cpp`. of those, only (1) changes the layout: `sizeof(Tracker)` and member offsets are baked into every client that creates or embeds a `Tracker`, so a client compiled against the old header and linked with the new `.cpp` would be broken. (2) changes no layout, and (4) changes only call sites (default arguments are substituted by the caller), but both still trigger rebuilds. the pimpl idiom in [[api-stability]] moves private members out of the header so that edits like (1) and (2) stop rippling.

</details>
