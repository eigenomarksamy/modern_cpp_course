<a id="cheat-sheet"></a>

## modern C++17/20 cheat sheet

a compact reference for after the course. the day numbers point back to the full explanations.

### initialization ([[initialization]])

```cpp
int a;            // local: indeterminate value, reading it is UB
int b{};          // value-initialized: 0
int c{3.5};       // error: narrowing is rejected inside braces
auto d{1};        // int (C++17 rule); auto e = {1}; is std::initializer_list<int>
std::vector<int> v1(3, 1);  // {1, 1, 1}
std::vector<int> v2{3, 1};  // {3, 1}: braces prefer initializer_list constructors
Point p{.x = 1, .y = 2};    // C++20 designated initializers, in declaration order
```

### special members and ownership ([[raii]] to [[ownership-in-interfaces]])

| you declare | copy ops generated? | move ops generated? |
| --- | --- | --- |
| nothing | yes | yes |
| destructor | yes (deprecated) | no, copies are used instead |
| copy constructor or copy assignment | the other one yes (deprecated) | no |
| move constructor or move assignment | no (deleted) | only the one you wrote |

- **rule of zero:** hold resources in members that manage themselves (`std::vector`, `std::string`, `std::unique_ptr`) and declare no special members.
- **rule of five:** if you must write one of destructor, copy constructor, copy assignment, move constructor, or move assignment, think about all five.
- mark move operations `noexcept` so `std::vector` can move instead of copy when it reallocates.
- destructors are implicitly `noexcept` (unless a member or base says otherwise); never let them throw.

| signature | meaning |
| --- | --- |
| `void f(Widget&)` / `void f(const Widget&)` | borrow, must not be null |
| `void f(Widget*)` | borrow, may be null |
| `void f(std::unique_ptr<Widget>)` | takes ownership |
| `void f(std::unique_ptr<Widget>&)` | may reseat the caller's pointer (rare) |
| `void f(std::shared_ptr<Widget>)` | shares ownership (keeps it alive) |
| `void f(std::span<const T>)`, `void f(std::string_view)` | borrows a contiguous sequence |
| `std::unique_ptr<Widget> make()` | caller becomes the owner |

### value categories and moves ([[value-categories]], [[move-semantics]], [[forwarding-references]])

```text
           expression
           /        \
      glvalue      rvalue
      /     \      /    \
  lvalue    xvalue     prvalue

lvalue:  has identity, not moved from implicitly   x, *p, a[i], f() returning T&
xvalue:  has identity, can be moved from           std::move(x), f() returning T&&
prvalue: no identity until materialized            42, T{}, f() returning T
```

- `std::move(x)` is only a cast to `T&&`; the move happens when a move constructor or assignment picks it up.
- `std::forward<T>(x)` keeps the caller's value category; use it only with forwarding references (`T&&` with deduced `T`, or `auto&&`).
- don't `return std::move(local);`: it blocks copy elision. returning a prvalue is guaranteed to be elided since C++17.
- a named rvalue reference is an lvalue.

### undefined, unspecified, implementation-defined ([[undefined-behavior]])

| category | meaning | examples |
| --- | --- | --- |
| undefined | no requirements at all; the optimizer assumes it never happens | signed overflow, out-of-bounds access, use after free, data race, reading an uninitialized `int`, strict aliasing violation |
| unspecified | one of several valid outcomes, not documented | order of evaluation of function arguments, string literal storage overlap |
| implementation-defined | chosen and documented by the implementation | `sizeof(int)`, signedness of plain `char`, `CHAR_BIT`, right shift of a negative integer (before C++20) |

defenses: `-Wall -Wextra`, `-fsanitize=address,undefined` (and `thread` for races), `std::bit_cast` or `std::memcpy` instead of pointer type punning.

### containers and algorithms ([[sequence-containers]] to [[callbacks]])

| container | access | insert/erase | notes |
| --- | --- | --- | --- |
| `vector` | O(1) random | O(1) amortized at end, O(n) elsewhere | default choice; contiguous; reallocation invalidates everything |
| `array` | O(1) random | fixed size | no heap |
| `deque` | O(1) random | O(1) at both ends | chunked, not contiguous |
| `list` | O(n) | O(1) with an iterator | stable references, splicing; one allocation per node |
| `map` / `set` | O(log n) | O(log n) | ordered; node-based |
| `unordered_map` / `set` | O(1) average | O(1) average | hashing cost; rehash invalidates iterators |

```cpp
std::erase_if(v, [](const Track& t) { return t.stale; });      // C++20
v.erase(std::remove_if(v.begin(), v.end(), is_stale), v.end()); // C++17 equivalent
auto [it, inserted] = m.try_emplace(key, args...);             // no move-from if key exists
if (auto it = m.find(k); it != m.end()) use(it->second);        // C++17 if-initializer
```

lambda captures: `[=]` copies what is used (implicitly capturing `this` through `[=]` is deprecated in C++20), `[&]` references (beware escaping), `[p = std::move(ptr)]` init-capture, `[this]` captures the pointer, `[*this]` copies the object (C++17).

### C++17 at a glance ([[module:results]], [[module:cpp17]])

| feature | example |
| --- | --- |
| structured bindings | `for (const auto& [name, value] : config)` |
| `if`/`switch` initializers | `if (auto r = parse(s); r) { ... }` |
| `if constexpr` | `if constexpr (std::is_integral_v<T>) { ... }` |
| fold expressions | `(std::cout << ... << args);` / `(... && checks)` |
| CTAD | `std::pair p{1, 2.0};` `std::lock_guard lock{m};` |
| inline variables | `inline constexpr int kMaxJoints = 7;` in a header |
| guaranteed copy elision | returning a prvalue of a non-movable type works |
| nested namespaces | `namespace robot::control { }` |
| attributes | `[[nodiscard]]`, `[[maybe_unused]]`, `[[fallthrough]]` |
| `std::optional<T>` | maybe a value; `value_or`, `*opt` (UB if empty) |
| `std::variant<Ts...>` | one of several types; `std::visit`, `std::get_if` |
| `std::any` | any copyable type; `std::any_cast`; rarely the right tool |
| `std::string_view` | non-owning, not null-terminated; never outlive the source |
| `std::filesystem` | `path`, `exists`, `directory_iterator`, `error_code` overloads |
| `std::from_chars`, `std::to_chars` | locale-free, allocation-free number conversion |
| `std::pmr` | memory resources: `monotonic_buffer_resource`, pool resources |
| `std::scoped_lock`, `std::shared_mutex` | multi-mutex locking, reader/writer locks |

```cpp
template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };
template <class... Fs> overloaded(Fs...) -> overloaded<Fs...>;  // not needed in C++20

std::visit(overloaded{
    [](const Detection& d) { handle(d); },
    [](const Heartbeat&)   { /* ignore */ },
}, message);
```

### C++20 at a glance ([[module:cpp20-generic]], [[module:cpp20-everyday]])

| feature | example |
| --- | --- |
| concepts | `template <std::integral T>`, `void f(std::floating_point auto x)` |
| custom concept | `template <class T> concept Sensor = requires(T s) { { s.read() } -> std::convertible_to<double>; };` |
| ranges and views | `v \| std::views::filter(pred) \| std::views::transform(f)` |
| projections | `std::ranges::sort(tracks, {}, &Track::range_m);` |
| `std::span<T>` | `void process(std::span<const float> samples)` |
| three-way comparison | `auto operator<=>(const T&) const = default;` |
| `consteval` / `constinit` | forced compile-time call / compile-time-initialized static |
| `std::format` | `std::format("{:>8.3f} m", range)` (GCC 13+, Clang 17+, MSVC 19.29+) |
| `std::jthread` | joins on destruction; `std::stop_token` for cancellation |
| `std::latch`, `std::barrier`, `std::counting_semaphore` | one-shot sync, phased sync, limited concurrency |
| atomic `wait`/`notify_one` | block on an atomic value change |
| `std::source_location` | file, line, function for logging without macros |
| `<bit>` | `std::bit_cast`, `std::popcount`, `std::endian` |
| container helpers | `contains`, `starts_with`, `ends_with`, `std::erase_if`, `std::ssize` |
| templated lambdas | `[]<class T>(const std::vector<T>& v) { ... }` |
| coroutines | `co_await`, `co_yield`, `co_return` (machinery only; no ready-made types) |
| modules | `export module sensors;` / `import sensors;` (tooling still maturing) |

### not in C++20 (easy to mix up)

| C++23 | what to use in C++20 |
| --- | --- |
| `std::expected` | `std::variant<T, Error>`, a small result type, or exceptions |
| `std::print`, `std::println` | `std::cout << std::format(...)` or `std::fputs` |
| `std::ranges::to` | construct the container from `begin()`/`end()` of the view |
| `std::views::zip`, `enumerate`, `chunk` | index loops or a hand-written helper |
| `std::generator` | a hand-written coroutine type or a library (cppcoro) |
| deducing `this` | CRTP |
| `std::mdspan` | `std::span` plus manual index math |
| `std::move_only_function` | `std::function` (requires copyable callables) or a custom wrapper |
| `std::flat_map` | sorted `std::vector` of pairs plus `std::lower_bound` |
| `if consteval` | `if (std::is_constant_evaluated())` |

### concurrency rules of thumb ([[module:threads]], [[module:async]])

- a data race (unsynchronized conflicting access, at least one write) is UB. a race condition (wrong timing logic) can exist without one.
- prefer `std::jthread` with `std::stop_token` over `std::thread` plus a flag; never let a joinable `std::thread` be destroyed.
- keep a mutex next to the data it protects, lock with `std::scoped_lock`, keep critical sections short, never call unknown code (callbacks) while holding a lock.
- always wait on a condition variable with a predicate: `cv.wait(lock, [&] { return !queue.empty() || closed; });`
- the future returned by `std::async` blocks in its destructor; keep it.
- atomics: default to `seq_cst`; use `release` on the publishing store and `acquire` on the observing load for the flag pattern; `relaxed` only for independent counters.
- lock ordering or `std::scoped_lock` prevents lock-order deadlocks. confinement and message passing prevent most of the rest.

### design reminders ([[module:design]], [[module:abstractions]])

| need | first choice | alternative |
| --- | --- | --- |
| open set of types, runtime choice | virtual interface | type erasure for value semantics |
| closed set of types | `std::variant` + `std::visit` | virtual interface |
| zero-overhead customization | template + concept | CRTP |
| store any callable | `std::function` | template parameter |
| testable dependency | constructor injection of an interface or a concept-constrained template | `std::function` seam, link-time seam |
| stable ABI | pimpl | C interface |

### performance habits ([[module:performance]], [[module:production]])

- measure first: optimized build, `std::chrono::steady_clock` or a benchmark library, many repetitions, report median and spread.
- contiguous data and predictable access patterns usually beat clever algorithms on small and medium inputs; confirm with a profiler and hardware counters.
- reserve, reuse, and preallocate; keep allocations out of real-time loops; consider `std::pmr` arenas.
- optimize where the profile says, and write down why the code is now less obvious.

### compiler flags worth knowing

```sh
-std=c++20 -Wall -Wextra -pedantic -Werror=return-type   # language mode and warnings
-O2 -g                                                     # optimized, still debuggable
-fsanitize=address,undefined                               # ASan + UBSan (debug/test builds)
-fsanitize=thread                                          # TSan, in a separate build
-D_GLIBCXX_ASSERTIONS                                      # bounds-checked libstdc++ operator[]
```
