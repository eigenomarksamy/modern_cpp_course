---
title: patterns in modern C++: factories and registries
standard: C++17
objective: hide the choice of concrete type behind a factory function or an explicit registry, and avoid self-registration tricks that break at link time
prerequisites: strategy, storage-duration
difficulty: 2
---

### the idea

a configuration file says `type: lidar`, and somewhere a string must become an object of the right class. the code that knows all the concrete types should be in one place, and everything else should see only the interface. that is the factory pattern, and in modern C++ its default form is almost anticlimactic: a function that returns `std::unique_ptr<Base>`. the interesting decisions are about how that function learns which types exist.

### understanding the concept

- **factory** hides which concrete type gets created. in modern C++ the default form is a plain function returning `std::unique_ptr<Base>`; a registry of creators appears when the choice comes from data (a config file, a plugin name).

### in code

**factory with a registry.** when a config file says `type: lidar`, something has to map that string to a constructor.

```cpp
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>

struct SensorConfig { std::string type, device; };

class Sensor {
public:
    virtual ~Sensor() = default;
    virtual double read() = 0;
};

using SensorFactory = std::function<std::unique_ptr<Sensor>(const SensorConfig&)>;

class SensorRegistry {
public:
    void add(std::string type, SensorFactory f) { makers_[std::move(type)] = std::move(f); }
    std::unique_ptr<Sensor> create(const SensorConfig& cfg) const {
        const auto it = makers_.find(cfg.type);
        if (it == makers_.end()) throw std::invalid_argument("unknown sensor type: " + cfg.type);
        return it->second(cfg);
    }
private:
    std::unordered_map<std::string, SensorFactory> makers_;
};

// explicit registration, called once from main: visible, ordered, link-safe
void register_builtin_sensors(SensorRegistry& r) {
    r.add("imu",   [](const SensorConfig& c) { return std::make_unique<Imu>(c.device); });
    r.add("lidar", [](const SensorConfig& c) { return std::make_unique<Lidar>(c.device); });
}
```

the tempting alternative is self-registration, where each `.cpp` file registers itself from a namespace-scope initializer:

```cpp
// lidar.cpp: "automatic" registration
namespace {
const bool lidar_registered = (global_registry().add("lidar", make_lidar), true);
}
```

it works in a demo and breaks in production for two reasons. first, if `lidar.o` lives in a static library and nothing else references a symbol in it, the linker never pulls that object file into the executable, so the initializer never runs and `"lidar"` is silently unknown (the usual workarounds, `--whole-archive` or `/WHOLEARCHIVE`, are build-system patches for a design problem). second, the registry itself must be a function-local static, or you have the static initialization order problem from [[storage-duration]]. an explicit `register_builtin_sensors` call costs one line and has neither problem.

### in practice

factories belong at the composition root from [[dependency-injection]]: `main` reads the configuration, calls `registry.create(cfg)` for each configured sensor, and passes the resulting objects (or references to them) down to the components that use them. nothing below `main` names a concrete sensor type, so adding a new sensor is one new class plus one registration line, and components depend only on the `Sensor` interface. returning `std::unique_ptr<Sensor>` keeps the ownership decision with the caller, who can store it, move it into a component, or convert it to a `std::shared_ptr` if sharing is genuinely needed.

### watch out for

patterns also invite premature generality. a `SensorRegistry` for two sensor types that are chosen by a compile-time flag is overkill; a `switch` in one factory function is clearer until the set becomes data-driven.

### the takeaway

make factories return `std::unique_ptr<Base>`, register creators explicitly from one function called by `main`, and add a registry only when the choice of type really comes from data.

### optional challenge

`SensorRegistry::create` throws `std::invalid_argument` for an unknown type. a colleague prefers returning `nullptr`. argue for one of them, using the error-handling criteria from [[error-strategy]].

<details>
<summary>answer</summary>

an unknown sensor type in a configuration file is a configuration error found at startup: rare, not recoverable locally, and best reported with context ("unknown sensor type: lidr" names the typo). that is the case for an exception. returning `nullptr` makes every caller check, and a forgotten check turns a clear startup error into a null dereference later. if some caller genuinely treats unknown types as normal (a plugin browser listing what is available), give it a separate query such as `bool knows(std::string_view type)`, rather than weakening `create` for everyone.

</details>
