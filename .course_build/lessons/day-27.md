<a id="day-27"></a>

## day 27: `std::filesystem` and a practical C++17 refactoring

**reading time:** about 10 minutes · **standard:** C++17 · **builds on:** days 20, 22, 24, 26

### the idea

Somewhere in your code base there is a function that scans a directory with `opendir`, glues paths together with `+ "/" +`, parses lines with `std::string::substr`, and reports failure through a `bool` and two out-parameters. It works, it is not portable to Windows, and nobody wants to touch it. Today we add the last C++17 library piece of this week, `std::filesystem`, and then use everything from days 22 to 26 to modernize that function, one justified change at a time.

### understanding the concept

`std::filesystem` (header `<filesystem>`, conventionally aliased `namespace fs = std::filesystem;`) standardizes what used to be POSIX `dirent.h`, Win32 `FindFirstFile`, or Boost.Filesystem. On GCC 8 it needed `-lstdc++fs` at link time; from GCC 9 it is part of the main library.

`fs::path` is a value type holding a path in the platform's native format (`char` on POSIX, `wchar_t` on Windows). You compose with `/`, and you decompose with `filename()`, `stem()`, `extension()`, and `parent_path()`. These are pure string operations: they never touch the disk. Converting back to `std::string` with `.string()` may have to transcode on Windows, so pass `fs::path` itself to APIs that accept it, including `std::ifstream`, whose constructor takes a `path` since C++17.

Operations that do touch the disk (`exists`, `is_regular_file`, `file_size`, `create_directories`, `rename`, `remove`, iteration) come in two overloads:

- without an error argument, they throw `fs::filesystem_error`, which carries the paths and an `std::error_code`;
- with a trailing `std::error_code& ec`, they report failure through `ec` instead.

Choose per call site with day 20's rule: if the failure is exceptional for this program (the config directory is missing at startup), throw; if it is an expected outcome (a file vanished from a drop directory between scans), use the `error_code` overload.

Two semantic details trip people up. `fs::directory_iterator` and `fs::recursive_directory_iterator` visit entries in an **unspecified order**: it is whatever the file system returns, and it differs between machines. And the file system is shared mutable state: another process can change it between any two of your calls, which is the subject of today's watch-out.

### in code

The basics, with no I/O until the last line:

```cpp
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

The quotes come from `operator<<` for `path`, which writes the path quoted (as if by `std::quoted`) so that paths with spaces round-trip. Use `.string()` when you want the raw text.

Now the legacy loader. It reads `key = value` lines from every `*.conf` file in a directory:

```cpp
// before: C++03 style, POSIX only
#include <dirent.h>
#include <fstream>
#include <map>
#include <string>

std::string trim(const std::string& s);   // the usual hand-written helper

bool load_configs(const char* dir, std::map<std::string, std::string>& out,
                  std::string& err) {
    DIR* d = opendir(dir);
    if (!d) { err = "cannot open directory"; return false; }
    while (struct dirent* e = readdir(d)) {
        std::string name = e->d_name;
        if (name.size() < 5 || name.substr(name.size() - 5) != ".conf") continue;
        std::ifstream in((std::string(dir) + "/" + name).c_str());
        std::string line;
        while (std::getline(in, line)) {
            std::string::size_type eq = line.find('=');
            if (line.empty() || line[0] == '#' || eq == std::string::npos) continue;
            out[trim(line.substr(0, eq))] = trim(line.substr(eq + 1));
        }
    }
    closedir(d);
    return true;
}
```

And after, in C++17:

```cpp
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>
namespace fs = std::filesystem;

using Config = std::map<std::string, std::string, std::less<>>;

std::string_view trim(std::string_view s) {
    const auto first = s.find_first_not_of(" \t\r");
    if (first == std::string_view::npos) return {};
    return s.substr(first, s.find_last_not_of(" \t\r") - first + 1);
}

std::optional<std::pair<std::string_view, std::string_view>> parse_line(std::string_view line) {
    line = trim(line);
    const auto eq = line.find('=');
    if (line.empty() || line.front() == '#' || eq == std::string_view::npos)
        return std::nullopt;
    return std::pair{trim(line.substr(0, eq)), trim(line.substr(eq + 1))};
}

[[nodiscard]] Config load_configs(const fs::path& dir) {
    std::vector<fs::path> files;
    for (const auto& entry : fs::directory_iterator(dir))       // throws fs::filesystem_error
        if (entry.is_regular_file() && entry.path().extension() == ".conf")
            files.push_back(entry.path());
    std::sort(files.begin(), files.end());                      // make "last file wins" deterministic

    Config cfg;
    for (const auto& file : files) {
        std::ifstream in(file);
        if (!in) throw std::runtime_error("cannot open " + file.string());
        for (std::string line; std::getline(in, line);)
            if (auto kv = parse_line(line)) {
                auto [key, value] = *kv;
                cfg.insert_or_assign(std::string(key), std::string(value));
            }
    }
    return cfg;
}
```

### in practice

Each change, and why:

| change | why |
|---|---|
| `opendir`/`readdir` to `fs::directory_iterator` | portable, and no `closedir` to forget on an early return (RAII) |
| string concatenation to `fs::path` and `extension()` | correct separators, no off-by-one suffix check |
| `bool` plus `err` out-parameter to an exception | a missing config directory at startup is exceptional (day 20) |
| out-parameter map to a returned `Config` with `[[nodiscard]]` | the result is the point of the call; returning a local costs at most a move, and NRVO usually removes even that (day 05) |
| `parse_line` returning `std::optional` of a pair of views | a pure, testable function; "not a key-value line" is a normal outcome, not an error |
| structured bindings for the key and value | names instead of `.first` and `.second` |
| sorting the file list | `readdir` order made duplicate keys across files resolve differently per machine |

Be honest about one thing: a refactoring is supposed to preserve behavior, and three behaviors changed here. Duplicate keys now resolve in sorted file order, an unreadable file now throws instead of being skipped silently, and an indented `# comment` is now treated as a comment. Each one is an improvement, and each one belongs in the commit message and in a characterization test written *before* the refactor (day 54 covers that discipline at scale).

One change was deliberately **not** made. The views returned by `parse_line` are tempting to store directly, with a `std::map<std::string_view, std::string_view>`, to avoid the two string copies per line. That would be a dangling bug (day 26): the views point into `line`, which is overwritten on the next `getline` and destroyed when the loop ends. The map must own its strings. The views are the right tool *inside* the parse, and the copies happen exactly once, at the ownership boundary. A second non-change: no parallel parsing and no `std::unordered_map`. A handful of config files at startup is not a performance problem, and changing the container would change the iteration order other code may depend on.

### watch out for

The classic file-system bug is **check-then-use**, a time-of-check to time-of-use (TOCTOU) race:

```cpp
if (fs::exists(p) && fs::file_size(p) > max_bytes)   // BUG: p can vanish or change in between
    fs::remove(p);
```

Between `exists` and `file_size`, a log rotator can delete or replace the file, and `file_size` then throws. Worse, in security-sensitive code, an attacker can swap `p` for a symlink between the check and the `remove`. The checks do not make the operation safe; they only narrow the window. Prefer to attempt the operation and handle the failure:

```cpp
std::error_code ec;
if (const auto size = fs::file_size(p, ec); !ec && size > max_bytes)
    fs::remove(p, ec);          // still racy in principle, but never throws, and ec reports what happened
```

Truly atomic guarantees come from the operating system (opening a file once and working on the handle, `O_CREAT | O_EXCL`, an atomic `rename` to publish a file), not from `std::filesystem`, which only names paths.

### the takeaway

`std::filesystem` gives you portable paths and directory operations with a choice of exceptions or error codes per call. A good modernization is a sequence of small, individually justified changes, with behavior changes stated openly and owning types kept at ownership boundaries even when views are tempting.

### optional challenge

A colleague wants to call `load_configs` every five seconds from a hot-reload thread. During deployments the directory briefly disappears. What would you change in the API, and what would you keep?

<details>
<summary>answer</summary>

A missing directory is now an expected outcome, so throwing and catching every five seconds would be exceptions as control flow (day 20). Add a non-throwing entry point, for example `std::optional<Config> try_load_configs(const fs::path& dir, std::error_code& ec)`, built on the `error_code` overloads of `directory_iterator` and `is_regular_file`, and have the reload thread keep the last good `Config` when it gets `std::nullopt`. Keep the throwing `load_configs` for startup, where failing loudly is correct, ideally implemented on top of the non-throwing version so the parsing logic exists once. If callers need to tell "directory missing" from "file unreadable" from "parse error", the `error_code` (or a variant result from day 25) carries that reason; a bare optional would not.

</details>
