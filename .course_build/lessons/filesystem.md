---
title: `std::filesystem`: portable paths and directories
standard: C++17
objective: compose and inspect paths with `std::filesystem`, choose between its throwing and error_code overloads, and avoid check-then-use races
prerequisites: error-strategy, string-view
difficulty: 1
---

### the idea

`std::string(dir) + "/" + name` works until the code runs on Windows, the directory name already ends in a slash, or the file name contains a character in a different encoding. `opendir` and `readdir` work until an early `return` skips `closedir`. file-system code is where portable C++ used to stop and platform `#ifdef`s began. C++17's `std::filesystem` makes paths a value type and directory traversal an RAII iterator, with a deliberate choice of error reporting at every call.

### understanding the concept

`std::filesystem` (header `<filesystem>`, conventionally aliased `namespace fs = std::filesystem;`) standardizes what used to be POSIX `dirent.h`, Win32 `FindFirstFile`, or Boost.Filesystem. on GCC 8 it needed `-lstdc++fs` at link time; from GCC 9 it is part of the main library.

`fs::path` is a value type holding a path in the platform's native format (`char` on POSIX, `wchar_t` on Windows). you compose with `/`, and you decompose with `filename()`, `stem()`, `extension()`, and `parent_path()`. these are pure string operations: they never touch the disk. converting back to `std::string` with `.string()` may have to transcode on Windows, so pass `fs::path` itself to APIs that accept it, including `std::ifstream`, whose constructor takes a `path` since C++17.

operations that do touch the disk (`exists`, `is_regular_file`, `file_size`, `create_directories`, `rename`, `remove`, iteration) come in two overloads:

- without an error argument, they throw `fs::filesystem_error`, which carries the paths and an `std::error_code`;
- with a trailing `std::error_code& ec`, they report failure through `ec` instead.

choose per call site with [[error-strategy]]'s rule: if the failure is exceptional for this program (the config directory is missing at startup), throw; if it is an expected outcome (a file vanished from a drop directory between scans), use the `error_code` overload.

two semantic details trip people up. `fs::directory_iterator` and `fs::recursive_directory_iterator` visit entries in an **unspecified order**: it is whatever the file system returns, and it differs between machines. and the file system is shared mutable state: another process can change it between any two of your calls, which is the subject of today's watch-out.

### in code

the basics, with no I/O until the last line:

```cpp complete
#include <filesystem>
#include <iostream>
namespace fs = std::filesystem;

int main() {
    const fs::path root = "/var/log/robot";
    const fs::path log = root / "arm" / "joint_states.2026-10-30.csv";
    std::cout << log.filename() << ' ' << log.stem() << ' ' << log.extension() << '\n';
    // prints: "joint_states.2026-10-30.csv" "joint_states.2026-10-30" ".csv"
    std::error_code ec;
    const auto bytes = fs::file_size(log, ec);              // no throw
    if (ec) std::cout << "no file: " << ec.message() << '\n';
    else    std::cout << bytes << " bytes\n";
}
```

the quotes come from `operator<<` for `path`, which writes the path quoted (as if by `std::quoted`) so that paths with spaces round-trip. use `.string()` when you want the raw text.

### in practice

a disk-usage monitor in a long-running service must never throw just because a log rotator deleted a file between listing and measuring it. the `error_code` overloads make that explicit:

```cpp complete
#include <cstdint>
#include <filesystem>
#include <system_error>
namespace fs = std::filesystem;

std::uintmax_t total_bytes(const fs::path& dir) {
    std::uintmax_t total = 0;
    std::error_code ec;
    for (fs::recursive_directory_iterator it(dir, ec), end; !ec && it != end; it.increment(ec)) {
        std::error_code fe;
        const auto size = it->file_size(fe);    // may fail: vanished file, or a directory
        if (!fe) total += size;                 // skip what cannot be measured
    }
    return total;
}
```

the outer `ec` stops the walk if the directory itself cannot be read; the inner one skips individual entries that disappear or are not regular files. the same function written with the throwing overloads would be shorter and would fail in production the first time a file vanished mid-scan.

### watch out for

the classic file-system bug is **check-then-use**, a time-of-check to time-of-use (TOCTOU) race:

```cpp
if (fs::exists(p) && fs::file_size(p) > max_bytes)   // BUG: p can vanish or change in between
    fs::remove(p);
```

between `exists` and `file_size`, a log rotator can delete or replace the file, and `file_size` then throws. worse, in security-sensitive code, an attacker can swap `p` for a symlink between the check and the `remove`. the checks do not make the operation safe; they only narrow the window. prefer to attempt the operation and handle the failure:

```cpp
std::error_code ec;
if (const auto size = fs::file_size(p, ec); !ec && size > max_bytes)
    fs::remove(p, ec);          // still racy in principle, but never throws, and ec reports what happened
```

truly atomic guarantees come from the operating system (opening a file once and working on the handle, `O_CREAT | O_EXCL`, an atomic `rename` to publish a file), not from `std::filesystem`, which only names paths.

### the takeaway

`std::filesystem` gives portable paths and directory operations with a choice of exceptions or error codes per call; path operations never touch the disk, and checking before acting never makes a file-system operation safe.

### optional challenge

on a POSIX system, what do these produce?

```cpp
fs::path("logs") / "/tmp/x"             // (1)
fs::path("data/run1/").filename()       // (2)
fs::path("archive.tar.gz").extension()  // (3)
```

<details>
<summary>answer</summary>

(1) `"/tmp/x"`: appending an absolute path replaces the left-hand side instead of concatenating, a frequent surprise when the right operand comes from user input. (2) an empty path: with a trailing separator, the last element is empty, so `filename()` is `""` (strip the trailing separator first if you want `"run1"`). (3) `".gz"`: `extension()` is only the part after the last dot, and `stem()` would be `"archive.tar"`.

</details>
