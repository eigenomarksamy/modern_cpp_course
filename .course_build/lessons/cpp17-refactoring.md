---
title: a practical C++17 refactoring
standard: C++17
objective: modernize a legacy function one justified change at a time, stating every behavior change and keeping owning types at ownership boundaries
prerequisites: filesystem, parsing-with-views, structured-bindings
difficulty: 2
---

### the idea

somewhere in your code base there is a function that scans a directory with `opendir`, glues paths together with `+ "/" +`, parses lines with `std::string::substr`, and reports failure through a `bool` and an out-parameter. it works, it is not portable, and nobody wants to touch it. this lesson modernizes that function with the C++17 vocabulary from the last two modules, and treats each change as a decision that needs a reason, not a style preference.

### understanding the concept

a good modernization is a sequence of small, individually justified changes. each one should make a specific defect impossible or a specific intent visible: a resource that can no longer leak, an error that can no longer be ignored, a name that replaces `.first`. "it is more modern" is not a reason. and a refactoring, by definition, preserves behavior; where behavior *does* change, that is a separate decision, written down and covered by a test that existed before the change.

### in code

now the legacy loader. it reads `key = value` lines from every `*.conf` file in a directory:

```cpp complete
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

and after, in C++17:

```cpp complete
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

each change, and why:

| change | why |
|---|---|
| `opendir`/`readdir` to `fs::directory_iterator` | portable, and no `closedir` to forget on an early return (RAII) |
| string concatenation to `fs::path` and `extension()` | correct separators, no off-by-one suffix check |
| `bool` plus `err` out-parameter to an exception | a missing config directory at startup is exceptional ([[error-strategy]]) |
| out-parameter map to a returned `Config` with `[[nodiscard]]` | the result is the point of the call; returning a local costs at most a move, and NRVO usually removes even that ([[copy-elision]]) |
| `parse_line` returning `std::optional` of a pair of views | a pure, testable function; "not a key-value line" is a normal outcome, not an error |
| structured bindings for the key and value | names instead of `.first` and `.second` |
| sorting the file list | `readdir` order made duplicate keys across files resolve differently per machine |

one change was deliberately **not** made. the views returned by `parse_line` are tempting to store directly, with a `std::map<std::string_view, std::string_view>`, to avoid the two string copies per line. that would be a dangling bug ([[string-view]]): the views point into `line`, which is overwritten on the next `getline` and destroyed when the loop ends. the map must own its strings. the views are the right tool *inside* the parse, and the copies happen exactly once, at the ownership boundary. a second non-change: no parallel parsing and no `std::unordered_map`. a handful of config files at startup is not a performance problem, and changing the container would change the iteration order other code may depend on.

### watch out for

**a "refactoring" that changes behavior.**

be honest about one thing: a refactoring is supposed to preserve behavior, and three behaviors changed here. duplicate keys now resolve in sorted file order, an unreadable file now throws instead of being skipped silently, and an indented `# comment` is now treated as a comment. each one is an improvement, and each one belongs in the commit message and in a characterization test written *before* the refactor ([[legacy-refactoring]] covers that discipline at scale).

### the takeaway

modernize in small steps that each remove a specific defect or reveal a specific intent; state every behavior change openly, and keep owning types at ownership boundaries even when views are tempting.

### optional challenge

a colleague wants to call `load_configs` every five seconds from a hot-reload thread. during deployments the directory briefly disappears. what would you change in the API, and what would you keep?

<details>
<summary>answer</summary>

a missing directory is now an expected outcome, so throwing and catching every five seconds would be exceptions as control flow ([[error-strategy]]). add a non-throwing entry point, for example `std::optional<Config> try_load_configs(const fs::path& dir, std::error_code& ec)`, built on the `error_code` overloads of `directory_iterator` and `is_regular_file`, and have the reload thread keep the last good `Config` when it gets `std::nullopt`. keep the throwing `load_configs` for startup, where failing loudly is correct, ideally implemented on top of the non-throwing version so the parsing logic exists once. if callers need to tell "directory missing" from "file unreadable" from "parse error", the `error_code` (or a variant result from [[variant]]) carries that reason; a bare optional would not.

</details>
