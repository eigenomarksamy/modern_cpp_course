<a id="day-07"></a>

## day 07: week 1 review: the ground beneath your feet

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days 01 to 06

### recap

| day | key idea |
|---|---|
| [01](#day-01) | The compiler sees one translation unit; the linker matches names. The ODR lets inline functions, classes, and templates be defined in many translation units only if every definition is identical, and violations need no diagnostic. C++17 `inline` variables give one object defined in a header. |
| [02](#day-02) | Braces reject narrowing but prefer `std::initializer_list` constructors. Automatic scalars start indeterminate; statics start zeroed. Arithmetic happens in at least `int`, and signed meets unsigned as unsigned. |
| [03](#day-03) | Scope belongs to names, lifetime to objects. Temporaries die at the end of the full-expression unless bound *directly* to a local reference. Cross-file static initialization order is unspecified; a function-local static fixes it. |
| [04](#day-04) | References are non-null, non-reseatable aliases; pointers are nullable and reseatable. `const` is a read-only view, shallow on pointer members, and an API contract that callers (and threads) rely on. |
| [05](#day-05) | Every expression has a type and a value category. Named variables are lvalues, even `T&&` ones. In C++17 a prvalue is an initializer, so returning one by value needs no copy or move constructor; NRVO is still optional. |
| [06](#day-06) | Implementation-defined (documented), unspecified (any allowed outcome), undefined (no requirements, and the optimizer assumes it never happens). Warnings and sanitizers are the practical defense. |

The thread through all six days: the standard defines an abstract machine, and most of what surprises engineers is the gap between that machine and the intuition "it's just memory and instructions".

### review questions

1. A header is included by `planner.cpp` and `controller.cpp`. It contains `int g_cycle_count;`, `const double kDt = 0.01;`, and `inline double clamp01(double x) { ... }`. Which of these links, which does not, and what single C++17 change gives you one shared, mutable `g_cycle_count` without touching any `.cpp` file?

2. Predict the sizes, then explain the rule that decides each: `std::vector<int> a{10, 0};`, `std::vector<int> b(10, 0);`, `std::vector<int> c{};`. Why does the guideline "use braces everywhere" need an exception for containers?

3. One of these lines dangles and the other is fine. Explain the difference in terms of value categories and lifetime extension.

   ```cpp
   const Frame& f = make_frame();               // make_frame returns Frame by value
   const int&   m = std::max(lo(), hi());       // lo and hi return int by value
   ```

4. A colleague says "the order in which `f(read_header(), read_body())` evaluates its arguments is undefined behavior, just like signed overflow." What is right and wrong about that, and why does the difference matter in practice?

5. Looking ahead to week 2: a `LogFile` class opens a `FILE*` in its constructor. Using what you know about storage duration and destruction order (day 03), where should `fclose` go so that every path out of a scope, including an exception, closes the file? And what goes wrong if a `LogFile` is copied with the compiler-generated copy constructor?

### mini exercise

This radar helper has three bugs that this week's lessons cover: one lifetime bug and two pieces of undefined behavior. One line that looks suspicious is actually fine. Find all four, then rewrite the function so it is correct.

```cpp
#include <vector>

struct Track { int id = 0; std::vector<float> ranges; };
std::vector<Track> load_tracks();

const float& latest_range(int id) {
    const auto& tracks = load_tracks();
    int index;
    for (std::size_t i = 0; i < tracks.size(); ++i)
        if (tracks[i].id == id) index = i;
    const Track& t = tracks[index];
    return t.ranges[t.ranges.size() - 1];
}
```

### answers

<details>
<summary>answer 1: linkage and the ODR</summary>

`int g_cycle_count;` fails: it is a definition with external linkage in two translation units (`multiple definition of 'g_cycle_count'`). `const double kDt` links, because namespace-scope `const` without `inline` or `extern` has internal linkage: each file gets its own copy, which is fine for a value. `inline double clamp01` links, because inline functions may be defined in every translation unit as long as the definitions are identical. Changing the first line to `inline int g_cycle_count = 0;` makes it a C++17 inline variable: one object for the whole program, defined in the header.

</details>

<details>
<summary>answer 2: braces and containers</summary>

`a` has 2 elements (10 and 0), `b` has 10 zeros, `c` is empty. A non-empty braced list strongly prefers a `std::initializer_list` constructor when one is viable; empty braces mean value-initialization, which calls the default constructor. Braces are a good default because they reject narrowing and avoid the most vexing parse, but for any class with an `initializer_list` constructor (all standard containers, `std::string`) braces mean "these are the elements". Use parentheses for the sizing and fill constructors.

</details>

<details>
<summary>answer 3: lifetime extension</summary>

`make_frame()` is a prvalue. Binding it directly to `const Frame&` materializes a temporary and extends its lifetime to that of `f`, so `f` is fine. `std::max(lo(), hi())` is an lvalue of type `const int` (it returns `const int&`): the temporaries from `lo()` and `hi()` were bound to `std::max`'s reference parameters, which only keeps them alive until the end of the full-expression. Lifetime extension happens only when the reference binds to the temporary itself, never through a function returning a reference, so `m` dangles at the `;`. Writing `int m = std::max(lo(), hi());` copies the value in time.

</details>

<details>
<summary>answer 4: unspecified versus undefined</summary>

The order is *unspecified*, not undefined. Since C++17 each argument is evaluated completely before the next one starts (they are indeterminately sequenced), and either order is a valid execution. The program is correct if it is correct for both orders; GCC happens to evaluate right to left in our tests, and another compiler may not. Signed overflow is *undefined*: there is no valid execution, and the optimizer may delete code on the assumption it never happens. In practice, unspecified order is a portability and reproducibility bug (here: reading the body before the header from a stream), fixed by naming intermediate results; undefined behavior can corrupt unrelated logic and must be eliminated outright.

</details>

<details>
<summary>answer 5: preview of week 2</summary>

`fclose` belongs in the destructor. Automatic objects are destroyed when their scope exits by any route: normal flow, `return`, `break`, or stack unwinding from an exception. Putting the release in the destructor ties the resource's lifetime to the object's lifetime, which is RAII (day 08).

The compiler-generated copy constructor copies the `FILE*` member, so two `LogFile` objects hold the same handle and both destructors call `fclose` on it: a double close, which is undefined behavior. The class must either forbid copying (`= delete`) or define what a copy means, and since C++11 it can also support *moving* ownership of the handle from one object to another. Days 10 and 11 cover how, and day 05's value categories are what decide when a move is chosen.

</details>

<details>
<summary>mini exercise answer</summary>

- **Fine (the decoy):** `const auto& tracks = load_tracks();` binds a prvalue directly to a `const&`, so the vector lives until the function returns.
- **Bug 1, UB (uninitialized read):** if no track has the requested `id`, `index` is never assigned, and `tracks[index]` reads an indeterminate value. GCC 12 at `-O2` warned `'index' may be used uninitialized`; it was the only one of the three bugs any warning caught.
- **Bug 2, UB (out of bounds):** if the track has no ranges, `t.ranges.size() - 1` wraps to the largest `std::size_t` (well-defined unsigned arithmetic, day 02), and indexing with it is out of bounds.
- **Bug 3, lifetime:** the returned reference points into `tracks`, whose lifetime-extended vector is destroyed when the function returns. Every caller receives a dangling reference. Lifetime extension lasts as long as the *reference variable*, which is a local.

A corrected version returns a value and makes "not found" explicit:

```cpp
#include <optional>
#include <vector>

std::optional<float> latest_range(int id) {
    const auto tracks = load_tracks();        // owned locally, by value
    for (const Track& t : tracks)
        if (t.id == id && !t.ranges.empty())
            return t.ranges.back();           // copy the float out while tracks is alive
    return std::nullopt;                      // not found, or no ranges yet
}
```

With test data `{1, {10, 12.5}}` and `{2, {}}`, ids 1, 2, and 3 gave `12.5`, empty, and empty. `std::optional` gets its own lesson on day 24; a `bool` plus an out-parameter would also work, at the cost of a clumsier call site. If loading all tracks is expensive, the real fix is an API change: the caller should own the track list and pass it in by `const&`, so this function no longer creates the data it needs to reference.

</details>

### connections

This week was about what the language actually guarantees, and every later week leans on it. Week 2 turns day 03's lifetime rules into a design technique: RAII (day 08) puts resource release in destructors because destruction order is deterministic, and constructors (day 09) are where day 02's initialization rules meet class invariants. Day 05's value categories are the entire mechanism behind move semantics (day 10) and the rule of zero and five (day 11), and day 04's "pointers say nothing about ownership" sets up smart pointers in interfaces (day 12).

Further out: day 01's ODR and header model is what C++20 modules (day 48) try to replace; day 06's data races and `volatile` misconception return with mutexes and atomics (days 37 and 40); `std::bit_cast` returns in the C++20 tour (day 34), and `constinit` (day 33) offers another answer to day 03's initialization order fiasco; and the "measure, use sanitizers, trust tools over intuition" habit becomes the whole of week 8.
