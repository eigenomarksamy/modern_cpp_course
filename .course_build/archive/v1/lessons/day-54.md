<a id="day-54"></a>

## day 54: refactoring legacy code and architectural tradeoffs

**reading time:** about 9 minutes · **standard:** C++17 · **builds on:** days 08, 12, 24, 26, 27, 43, 44, 53

### the idea

Every engineer has opened a 4,000-line file full of raw `new`, `char*` buffers, and out-parameters and thought "this needs a rewrite". Big rewrites usually take far longer than planned, while the old code keeps shipping and accumulating fixes the new code lacks. The approach that works is less dramatic: change the code in small, verified steps, each one leaving the system working, and make the architectural calls deliberately and in writing.

### understanding the concept

Legacy code, in the useful definition, is code without tests: you cannot change it with confidence. So the first step is not modernization; it is getting a safety net.

**Characterization tests** record what the code does today, not what it should do. You feed it inputs, observe outputs, and assert those outputs, including the strange ones. They are scaffolding for refactoring: when one fails, you changed behavior, and you decide whether that was intended.

**Seams** (day 44) are where you can change behavior without editing the code in place: a constructor parameter, a virtual function, a template parameter, a link-time substitution. Legacy code often has none; creating the first seam with a minimal, careful edit is usually the riskiest step, so keep it mechanical.

A safe **modernization order** goes from zero-risk to higher-risk changes:

1. Turn on warnings (`-Wall -Wextra`, then `-Werror` directory by directory) and run sanitizer builds in CI (day 53). This finds real bugs without touching a line.
2. Write characterization tests around the code you are about to change.
3. Fix ownership at boundaries: RAII wrappers and `std::unique_ptr` in signatures (days 08, 12), so leaks become impossible rather than unlikely.
4. Adopt vocabulary types: `std::string_view` for read-only strings, `std::optional` or a variant result for "maybe" and errors, `std::filesystem::path` for paths (days 24 to 27).
5. Apply mechanical modernizations with tools, one kind of change per commit.

The **strangler pattern** replaces a subsystem without a big bang: put an interface in front of the old implementation, build the new one behind the same interface, route a growing share of traffic to it, and delete the old one when nothing uses it. In robotics this often means running the new module in shadow mode on recorded data and comparing its outputs with the old one before it ever drives a motor.

### in code

The legacy function, with its problems labelled:

```cpp
// calib_loader.cpp, circa 2009
#include <cstdio>
#include <cstring>

struct Calib { double gain, offset, skew; };

bool load_calibration(const char* path, Calib** out, char* err, int errlen) {
    FILE* f = std::fopen(path, "r");
    if (!f) { std::strncpy(err, "open failed", errlen); return false; }  // BUG: may not terminate
    Calib* c = new Calib;
    if (std::fscanf(f, "%lf %lf %lf", &c->gain, &c->offset, &c->skew) != 3) {
        std::strncpy(err, "parse failed", errlen);
        std::fclose(f);
        return false;                                                    // BUG: leaks c
    }
    std::fclose(f);
    *out = c;                                                            // caller must delete
    return true;
}
```

`strncpy` does not write a terminator when the source is at least `errlen` characters long, so a caller that prints `err` reads past the buffer: undefined behavior. The parse-failure path leaks. Ownership of `*out` lives only in a comment.

Before changing anything, pin the behavior down:

```cpp
// Pin what the code does today, including the parts that look odd.
void characterize_load_calibration() {
    char err[64] = {};
    Calib* c = nullptr;

    write_file("ok.cal", "1.5 0.25 -3\n");
    assert(load_calibration("ok.cal", &c, err, sizeof err));
    assert(c->gain == 1.5 && c->offset == 0.25 && c->skew == -3.0);
    delete c;

    write_file("trailing.cal", "1 2 3 garbage\n");                // accepted today: keep?
    assert(load_calibration("trailing.cal", &c, err, sizeof err));
    delete c;

    write_file("short.cal", "1 2\n");
    assert(!load_calibration("short.cal", &c, err, sizeof err));
    assert(std::string(err) == "parse failed");                   // someone greps for this

    assert(!load_calibration("missing.cal", &c, err, sizeof err));
    assert(std::string(err) == "open failed");
}
```

The trailing-garbage case is the interesting one. It may be a bug, but some calibration file in the fleet may rely on it. Hyrum's law (day 47): every observable behavior has a user. The test makes that behavior visible so changing it becomes a decision.

Now the modern core, plus a shim so existing callers keep compiling:

```cpp
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <string>
#include <variant>

struct LoadError { std::string message; };

[[nodiscard]] std::variant<Calib, LoadError> read_calibration(const std::filesystem::path& path) {
    std::ifstream in(path);
    if (!in) return LoadError{"open failed"};
    Calib c{};
    if (!(in >> c.gain >> c.offset >> c.skew)) return LoadError{"parse failed"};
    return c;                                     // value, no ownership question at all
}

// Compatibility shim: old signature, new implementation. Delete when the last caller is gone.
[[deprecated("use read_calibration")]]
bool load_calibration(const char* path, Calib** out, char* err, int errlen) {
    auto result = read_calibration(path);
    if (auto* c = std::get_if<Calib>(&result)) { *out = new Calib(*c); return true; }
    std::snprintf(err, static_cast<std::size_t>(errlen), "%s",
                  std::get<LoadError>(result).message.c_str());   // always terminated
    return false;
}
```

The same characterization test passes against the shim, which is the evidence that the refactor preserved behavior. The `[[deprecated]]` attribute turns every remaining caller into a compiler warning, a built-in migration to-do list. Note what was deliberately not changed: the error strings, and the acceptance of trailing text. `fscanf` and `operator>>` can also differ on unusual numeric input, which is exactly why the test, not a code review, is the judge.

### in practice

Mechanical modernization is where tools beat people. `clang-tidy` has a family of `modernize-*` checks (`use-nullptr`, `use-override`, `make-unique`, `loop-convert`, `use-using`, `pass-by-value`, and more) that rewrite code with fixes:

```sh
# one check per commit: each diff is large but trivially reviewable
run-clang-tidy -p build -checks='-*,modernize-use-nullptr' -fix
run-clang-tidy -p build -checks='-*,modernize-use-override' -fix
# reformat once, in its own commit, then hide it from blame
clang-format -i $(git ls-files '*.cpp' '*.h')
git rev-parse HEAD >> .git-blame-ignore-revs     # git config blame.ignoreRevsFile ...
```

The refactors that need judgment get written down. A lightweight architecture decision record (ADR) fits in a file next to the code:

```text
ADR-017: track storage layout
status:       accepted
context:      tracker misses its frame budget at high detection counts; perf counters
              show the association loop is dominated by cache misses (day 51).
decision:     store tracks as struct-of-arrays inside TrackTable; public API unchanged.
alternatives: keep AoS with hot/cold split (measured, not enough);
              pooled Track objects (fewer allocations, same misses).
consequences: + association loop within budget on recorded sessions
              - a new track field touches three places in TrackTable
              - debugger shows arrays, not tracks (pretty-printer added)
revisit if:   per-track behavior grows (polymorphic motion models) or counts drop.
```

The format matters less than the habit: context, the decision, the alternatives considered, the costs accepted, and when to revisit. The classic tradeoffs (maintainability versus performance, abstraction versus overengineering, compile-time versus runtime flexibility, object-oriented versus data-oriented layout) stop being religious arguments once each side has to write down its consequences.

Not everything should be refactored. Code that works, rarely changes, and is scheduled for retirement is cheapest left alone. Prioritize by change frequency times pain: `git log` tells you which files churn, and the bug tracker tells you which ones hurt.

### watch out for

Never mix a refactoring and a behavior change in one commit. A refactoring should leave every characterization test green; a behavior change should change specific tests on purpose. Combine them and a failing test no longer tells you which change caused it, the review cannot separate "moved code" from "changed meaning", and a revert throws away both. The discipline is tedious and it is what makes legacy work safe.

### the takeaway

Get a safety net before you change anything, then modernize in small, separately verifiable steps, and record the architectural decisions with their costs so the next engineer can revisit them instead of rediscovering them.

### optional challenge

Product decides that trailing garbage in calibration files must now be rejected. Describe how you would ship that change safely after the refactoring above.

<details>
<summary>answer</summary>

Treat it as a behavior change in its own commit, after the refactor has landed and been verified. First check reality: scan the calibration files actually deployed (or a fleet sample) for trailing content, because a robot that refuses to start is worse than one that ignores a comment. Then change the rule in `read_calibration` (after the three reads, check that only whitespace remains), and update the characterization test deliberately: the "trailing" case now expects `parse failed` or, better, a more specific error. If files in the field do have trailing text, consider a transition period in which the loader accepts the file but logs a structured warning (day 53) so you can see who would break. Document the decision, briefly, where the next person will look.

</details>
