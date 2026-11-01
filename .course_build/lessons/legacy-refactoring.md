---
title: refactoring legacy code safely
standard: C++17
objective: put characterization tests around legacy code, modernize it in small verified steps behind a compatibility shim, and let tools do the mechanical changes
prerequisites: cpp17-refactoring, testing, test-seams
difficulty: 2
---

### the idea

every engineer has opened a 4,000-line file full of raw `new`, `char*` buffers, and out-parameters and thought "this needs a rewrite". big rewrites usually take far longer than planned, while the old code keeps shipping and accumulating fixes the new code lacks. the approach that works is less dramatic: change the code in small, verified steps, each one leaving the system working, and make the architectural calls deliberately and in writing.

### understanding the concept

legacy code, in the useful definition, is code without tests: you cannot change it with confidence. so the first step is not modernization; it is getting a safety net.

**characterization tests** record what the code does today, not what it should do. you feed it inputs, observe outputs, and assert those outputs, including the strange ones. they are scaffolding for refactoring: when one fails, you changed behavior, and you decide whether that was intended.

**seams** ([[test-seams]]) are where you can change behavior without editing the code in place: a constructor parameter, a virtual function, a template parameter, a link-time substitution. legacy code often has none; creating the first seam with a minimal, careful edit is usually the riskiest step, so keep it mechanical.

a safe **modernization order** goes from zero-risk to higher-risk changes:

1. turn on warnings (`-Wall -Wextra`, then `-Werror` directory by directory) and run sanitizer builds in CI ([[observability]]). this finds real bugs without touching a line.
2. write characterization tests around the code you are about to change.
3. fix ownership at boundaries: RAII wrappers and `std::unique_ptr` in signatures ([[raii]], [[ownership-in-interfaces]]), so leaks become impossible rather than unlikely.
4. adopt vocabulary types: `std::string_view` for read-only strings, `std::optional` or a variant result for "maybe" and errors, `std::filesystem::path` for paths ([[optional]] to [[filesystem]]).
5. apply mechanical modernizations with tools, one kind of change per commit.

### in code

the legacy function, with its problems labelled:

```cpp ub
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

`strncpy` does not write a terminator when the source is at least `errlen` characters long, so a caller that prints `err` reads past the buffer: undefined behavior. the parse-failure path leaks. ownership of `*out` lives only in a comment.

before changing anything, pin the behavior down:

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

the trailing-garbage case is the interesting one. it may be a bug, but some calibration file in the fleet may rely on it. Hyrum's law ([[api-contracts]]): every observable behavior has a user. the test makes that behavior visible so changing it becomes a decision.

now the modern core, plus a shim so existing callers keep compiling:

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

the same characterization test passes against the shim, which is the evidence that the refactor preserved behavior. the `[[deprecated]]` attribute turns every remaining caller into a compiler warning, a built-in migration to-do list. note what was deliberately not changed: the error strings, and the acceptance of trailing text. `fscanf` and `operator>>` can also differ on unusual numeric input, which is exactly why the test, not a code review, is the judge.

### in practice

the shim turns a migration into a countable task. every remaining caller of `load_calibration` now produces a deprecation warning, so the build log is the to-do list; teams typically track the warning count per release and migrate callers in small commits, each reviewed on its own. when the count reaches zero, the shim is deleted in a commit that changes nothing else. at no point does the codebase stop building, and at every point the characterization test proves the old and new paths agree. large mechanical changes (adding `override`, replacing `NULL`) follow the same rhythm with tools doing the edits, as [[architecture-decisions]] shows.

### watch out for

never mix a refactoring and a behavior change in one commit. a refactoring should leave every characterization test green; a behavior change should change specific tests on purpose. combine them and a failing test no longer tells you which change caused it, the review cannot separate "moved code" from "changed meaning", and a revert throws away both. the discipline is tedious and it is what makes legacy work safe.

### the takeaway

get a safety net before you change anything, then modernize in small, separately verifiable steps, with tools doing the mechanical work and a shim keeping old callers compiling.

### optional challenge

product decides that trailing garbage in calibration files must now be rejected. describe how you would ship that change safely after the refactoring above.

<details>
<summary>answer</summary>

treat it as a behavior change in its own commit, after the refactor has landed and been verified. first check reality: scan the calibration files actually deployed (or a fleet sample) for trailing content, because a robot that refuses to start is worse than one that ignores a comment. then change the rule in `read_calibration` (after the three reads, check that only whitespace remains), and update the characterization test deliberately: the "trailing" case now expects `parse failed` or, better, a more specific error. if files in the field do have trailing text, consider a transition period in which the loader accepts the file but logs a structured warning ([[observability]]) so you can see who would break. document the decision, briefly, where the next person will look.

</details>
