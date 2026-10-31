# curriculum: modern c++ daily course (v1.0)

This is the authoritative 56-day topic map. Do not change it silently during resumption; a deliberate change belongs in a `revise` operation and must be noted in `handoff.md`.

Each day lists: title, language standard of its examples, objectives, what it must cover, what belongs to another day (so lessons do not repeat each other), and dependencies.

---

## authoring conventions (apply to every lesson file)

### file layout

Each lesson lives in `.course_build/lessons/day-XX.md` and is written at standalone heading depth: `##` for the day, `###` for its sections, `####` for anything smaller. The assembler demotes headings by one level when it builds the final document, so never use a single `#` in a lesson file.

Instructional lesson (every day that is not a multiple of 7):

````markdown
<a id="day-01"></a>

## day 01: from source file to running program

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** none

### the idea
### understanding the concept
### in code
### in practice
### watch out for
### the takeaway
### optional challenge
````

Review day (days 7, 14, 21, 28, 35, 42, 49, 56):

````markdown
<a id="day-07"></a>

## day 07: week 1 review: the ground beneath your feet

**reading time:** about 8 minutes · **standard:** C++17 · **builds on:** days 01 to 06

### recap
### review questions
### mini exercise
### answers
### connections
````

The section headings above are required, spelled exactly like that, in that order. Extra `####` subheadings inside a section are fine.

- The `builds on` field lists earlier days by number (`days 03, 05`), or `none`.
- The `standard` field is the minimum standard the lesson's examples need: `C++17` or `C++20`. If one snippet needs C++20 inside a C++17 lesson, say so above that snippet.
- The optional challenge ends with a collapsed answer:

  ```markdown
  <details>
  <summary>answer</summary>

  The explanation goes here.

  </details>
  ```

- On review days, the answers to the review questions and the mini exercise go in the `answers` section, each one inside its own `<details>` block, so readers can test themselves first.

### length and density

- Target 1,000 to 1,600 words per lesson including code (5 to 10 minutes for a professional reader who reads code carefully). The validator rejects anything under 650 or over 2,100 words.
- 2 to 3 code examples in `in code`, each short (usually 5 to 30 lines). Other sections may have a snippet when it earns its place.
- Concise paragraphs (2 to 5 sentences). A small table or ASCII diagram when it beats prose.

### voice and style

- One experienced engineer talking to another: direct, practical, a little opinionated, never a textbook. Use "you" and "we". No hype, no filler intros like "In this lesson we will...".
- All headings lowercase. Acronyms (RAII, ODR, UB, SOLID, ABI), `C++`, and identifiers in backticks are allowed in headings.
- Never use em dashes (the long dash). Use commas, colons, parentheses, or separate sentences. Prefer to avoid en dashes as well.
- Code blocks are fenced with a language tag: ` ```cpp `, ` ```text `, ` ```sh `, ` ```cmake `.
- Mark output in comments: `// prints: 3`. Mark broken code clearly: `// BUG: ...`, and say whether something is undefined behavior (UB), unspecified, or implementation-defined. Use those three terms precisely:
  - **undefined behavior**: the standard imposes no requirements; the optimizer may assume it never happens.
  - **unspecified behavior**: one of several allowed outcomes; the implementation need not document which.
  - **implementation-defined behavior**: unspecified, but the implementation must document its choice (for example `sizeof(long)`).
- Do not use C++23 features (`std::expected`, `std::print`, `std::mdspan`, deducing `this`, `std::generator`, `std::flat_map`, `std::ranges::to`, `std::views::zip`/`enumerate`/`chunk`, `std::move_only_function`, `if consteval`, `std::unreachable`, `std::to_underlying`, `[[assume]]`, multidimensional `operator[]`). You may mention a C++23 feature as a forward-looking note, clearly labelled "C++23".
- Never make unsupported performance claims. Say what the complexity is, what tends to dominate, and how you would measure. "Usually faster" needs a reason (fewer allocations, contiguous memory, fewer indirections), and "measure it" needs a hint about how.
- Recurring domains for examples: robotics (joint controllers, sensor fusion, motion planning), radar processing (detections, tracks, range-Doppler frames), telemetry and logging, build and deployment tooling, embedded and real-time constraints. Rotate them; don't force them.

### code correctness

- Examples must compile under the stated standard unless they are deliberately broken (and labelled so). Include the headers a reader would need, or at least the non-obvious ones.
- Compile representative examples with the local toolchain (`g++` 12.1, MSYS2) using `-std=c++17` or `-std=c++20` plus `-Wall -Wextra -pedantic`. GCC 12 has no `<format>` (it arrived in GCC 13): such examples cannot be compile-checked here and the check note must say so. GCC 12 also has no usable modules support for checks; say so as well.
- Record what you compiled in `.course_build/checks/day-XX.md` (which snippets, which flags, result, and anything not checked and why). Never claim a check you did not run.

### design thread

Design thinking runs through every week, not only week 7. Where it fits naturally, connect the day's feature to: encapsulation, ownership and API contracts, composition versus inheritance, coupling and cohesion, testability, compile-time versus runtime tradeoffs, data-oriented versus object-oriented layout, error handling, maintainability versus performance, and abstraction versus overengineering. One sentence of judgment is often enough.

### cross references

Refer to other lessons as "day 12" (the final document links `#day-12`). You may write a markdown link `[day 12](#day-12)`. Only refer backwards for prerequisites; forward references ("we'll come back to this on day 40") are fine but sparing.

### review days

- Recap: a compact bullet list or table of the week's key ideas (one line per day is plenty).
- 3 to 5 conceptual review questions on this week, plus 1 or 2 spaced-repetition questions drawn from earlier weeks (label them "from week N").
- One optional mini coding exercise (a few minutes).
- Answers with brief explanations, collapsed.
- Connections: how this week links to earlier weeks and what it sets up next.

---

## week 1: rediscovering c++ fundamentals

The ground floor: how code becomes a program, how objects come into existence, and what the language actually promises.

### day 01: from source file to running program
- standard: C++17
- objectives: explain translation units, the preprocessor, compilation, and linking; read a linker error; understand what headers really are.
- cover: the pipeline (preprocess, compile, assemble, link), object files and symbols, declarations versus definitions, external versus internal linkage (`static`, anonymous namespaces), the one definition rule and why ODR violations are often silent, C++17 `inline` variables for header-defined constants, include guards and `#pragma once`, why templates live in headers. Example: a duplicate-symbol link error and a silent ODR violation from two different definitions of the same inline function or class.
- leave for later: build systems in depth, modules (day 48).
- builds on: none

### day 02: types and the many faces of initialization
- standard: C++17
- objectives: choose the right initialization syntax; avoid narrowing, the most vexing parse, and uninitialized locals.
- cover: default, value, direct, copy, list, and aggregate initialization; zero-initialization of statics; narrowing conversions rejected by braces; `std::initializer_list` constructors hijacking braces (`std::vector<int>{3, 1}` versus `(3, 1)`); most vexing parse; `auto` with braces (the C++17 rule change: `auto x{1}` is `int`); fundamental type sizes are implementation-defined; fixed-width integers; integer promotions and signed/unsigned comparison surprises. Predict-the-output question.
- leave for later: designated initializers (day 34), constructors in depth (day 09).
- builds on: day 01

### day 03: scope, storage duration, and object lifetime
- standard: C++17
- objectives: separate scope (a name's visibility) from lifetime (an object's existence); recognize dangling references and static initialization order problems.
- cover: automatic, static, thread, and dynamic storage duration; when lifetime starts and ends; temporaries and the end of the full-expression; lifetime extension by `const&` and `&&` binding (and where it does not apply: members returned by reference, function parameters); returning a reference to a local; the static initialization order fiasco and the function-local static fix (thread-safe since C++11); construction and destruction order.
- leave for later: RAII as a design technique (day 08).
- builds on: days 01, 02

### day 04: pointers, references, and const
- standard: C++17
- objectives: choose between pointer, reference, and value in signatures; read and apply const correctly.
- cover: what a reference is (an alias, not reseatable, no null references in valid programs), pointers as nullable and reseatable; `const T*` versus `T* const`; const member functions and logical constness with `mutable`; `const` as an API contract; parameter-passing guidelines (value for cheap types, `const&` for read-only large ones, pointer for optional, non-const reference for in/out) with the tradeoffs; `nullptr` versus `NULL`/`0`; arrays decaying to pointers; pointer arithmetic beyond the array (UB).
- leave for later: smart pointers (day 12), `std::span` (day 31), `std::optional<T&>` absence (day 24).
- builds on: days 02, 03

### day 05: value categories without the headache
- standard: C++17
- objectives: classify expressions as lvalue, xvalue, prvalue; understand why this governs overloading and moves; understand C++17 guaranteed copy elision.
- cover: expressions have a type and a value category; the glvalue/rvalue taxonomy with a small diagram; "has identity" and "can be moved from"; binding rules for `T&`, `const T&`, `T&&`; `decltype(x)` versus `decltype((x))`; temporary materialization; C++17 guaranteed copy elision for prvalues (returning a non-movable type by value works), versus NRVO, which is still optional. Predict-which-overload-gets-called example.
- leave for later: move constructors (day 10), forwarding references (day 19).
- builds on: days 03, 04

### day 06: undefined behavior and other things the standard won't promise
- standard: C++17
- objectives: tell UB, unspecified, and implementation-defined behavior apart; understand why the optimizer makes UB dangerous; know the usual suspects and the tools that catch them.
- cover: the three categories with an example of each; how the compiler reasons from "UB never happens" (signed overflow loop, null check removed after a dereference); the usual suspects: signed overflow, out-of-bounds, use-after-free, uninitialized reads, strict aliasing violations (and `std::memcpy`, C++20 `std::bit_cast` as the fix), data races (preview of day 37), modifying a string literal; order of evaluation (C++17 tightened some rules, e.g. `<<` and assignment, but function arguments remain unspecified order); common misconceptions (`volatile` is not for threads, "it works on my machine", `i = i++` status changed in C++17); sanitizers (`-fsanitize=address,undefined`) and warnings as the practical defense.
- leave for later: data races in depth (day 37).
- builds on: days 01 to 05

### day 07: week 1 review: the ground beneath your feet
- standard: C++17
- review of days 01 to 06. Mini exercise idea: find the three lifetime or UB bugs in a short function.
- builds on: days 01 to 06

---

## week 2: ownership and object-oriented c++

Who owns what, for how long, and how objects relate to each other.

### day 08: RAII: let scope do the cleanup
- standard: C++17
- objectives: explain RAII as the core C++ resource-management idiom; wrap a C-style resource safely.
- cover: acquire in the constructor, release in the destructor; why destructors run during stack unwinding; naive `fopen`/`fclose` code with early returns and exceptions versus a small RAII wrapper; `std::lock_guard` and `std::unique_ptr` with a custom deleter as RAII you already use; a scope guard (C++17, via a class template with CTAD); destructors should not throw (implicitly `noexcept`); RAII as encapsulation of an invariant ("if the object exists, the resource is valid").
- leave for later: copy/move of RAII types (days 10, 11).
- builds on: days 03, 06

### day 09: constructors, destructors, and the object lifecycle
- standard: C++17
- objectives: write constructors that establish invariants; know construction and destruction order and its consequences.
- cover: member initializer lists versus assignment in the body; members initialized in declaration order, not list order (the `-Wreorder` bug); default member initializers; delegating constructors; `explicit` for single-argument constructors (and why); construction order: bases, then members, then body; destruction is the reverse; calling virtual functions in constructors/destructors does not dispatch to the derived class; a constructor that throws means the destructor does not run, but fully constructed members are destroyed; invariants and class design (when a struct is fine and when you need a class).
- leave for later: special member generation rules (day 11), virtual destructors (day 13).
- builds on: days 02, 03, 08

### day 10: copy and move semantics
- standard: C++17
- objectives: implement and reason about copy and move operations; understand that `std::move` is only a cast.
- cover: deep versus shallow copy with a small buffer class; the move constructor and move assignment stealing resources; the moved-from state ("valid but unspecified" for standard types, your own contract for yours); `std::move` is a `static_cast<T&&>`; why `noexcept` on the move constructor matters for `std::vector` reallocation (`std::move_if_noexcept`, strong guarantee); self-assignment; returning locals (do not `std::move` a returned local: it inhibits NRVO, links to day 05); `const` objects cannot be moved from.
- leave for later: rule of zero/five (day 11), perfect forwarding (day 19).
- builds on: days 05, 08, 09

### day 11: the rule of zero, three, and five
- standard: C++17
- objectives: know when the compiler generates special members; prefer designs that need none.
- cover: the six special members and the generation rules (a table: declaring a destructor or copy suppresses implicit move, and so on); `= default` and `= delete`; rule of three (C++98), rule of five, rule of zero: compose from members that manage themselves (`std::vector`, `std::unique_ptr`, `std::string`); move-only types; a class refactored from a hand-written rule-of-five to rule of zero; copy-and-swap as an option and its cost; the "rule of zero" as a design principle (single responsibility for resource management).
- leave for later: exception guarantees in depth (day 20).
- builds on: days 08, 09, 10

### day 12: smart pointers and ownership in interfaces
- standard: C++17
- objectives: choose between `unique_ptr`, `shared_ptr`, `weak_ptr`, and raw pointers/references; express ownership in function signatures.
- cover: `std::unique_ptr` (zero-overhead in the common case, custom deleters change its size), `std::make_unique`; `std::shared_ptr` control block, atomic reference counts (thread-safe count, not thread-safe object), `std::make_shared` single allocation tradeoff with `weak_ptr` keeping the block alive; `std::weak_ptr` to break cycles (a parent/child cycle leak example); `enable_shared_from_this`; Core Guidelines style signatures: take `T*`/`T&` when you do not affect ownership, `unique_ptr<T>` by value to transfer, `shared_ptr<T>` by value only to share; shared ownership as a design smell when overused.
- leave for later: allocation costs (day 52), observer with `weak_ptr` (day 45).
- builds on: days 04, 08, 10, 11

### day 13: polymorphism, inheritance, and composition
- standard: C++17
- objectives: understand how virtual dispatch works (and that vtables are an implementation technique, not a rule); choose composition over inheritance by default.
- cover: virtual functions, `override`, `final`; a typical vtable/vptr layout diagram (labelled implementation-specific); virtual destructors and deleting through a base pointer (UB without one); object slicing; non-virtual interface (NVI) idiom; abstract interfaces; Liskov substitution in one example (the classic rectangle/square or a sensor that cannot honour the base contract); composition over inheritance with a robot that *has* a drive system rather than *is* one; cost of virtual calls stated carefully (indirection, inhibits inlining, often negligible; measure).
- leave for later: static polymorphism and type erasure (day 46), SOLID (day 43).
- builds on: days 09, 11, 12

### day 14: week 2 review: owning your resources
- standard: C++17
- review of days 08 to 13 plus spaced repetition from week 1. Mini exercise idea: turn a hand-rolled resource class into a rule-of-zero class.
- builds on: days 08 to 13

---

## week 3: standard library and generic programming

The standard library as a vocabulary, and templates as the machinery behind it.

### day 15: containers and what they cost
- standard: C++17
- objectives: pick containers based on access patterns, complexity, and memory layout; know iterator invalidation rules.
- cover: `std::vector` as the default (contiguous, amortized O(1) push_back, `reserve`), `std::array`, `std::deque`, `std::list` (when it actually wins: stable references, splicing), `std::map` versus `std::unordered_map` (ordering, complexity, node allocations, hashing cost), a small comparison table; iterator and reference invalidation (vector reallocation bug); `emplace_back` versus `push_back`; complexity versus constant factors and cache behavior (measure; preview day 51); C++17 node handles (`extract`, `merge`) and `try_emplace`/`insert_or_assign`.
- leave for later: allocators and pmr (day 52).
- builds on: days 10, 12

### day 16: iterators and algorithms over raw loops
- standard: C++17
- objectives: use standard algorithms to express intent; understand iterator categories and the erase-remove idiom.
- cover: iterator categories (input, forward, bidirectional, random access, and contiguous in C++20 as a note); half-open ranges `[begin, end)`; naive loop versus `std::find_if`, `std::count_if`, `std::transform`, `std::accumulate`, `std::partition`, `std::stable_sort`, `std::any_of`; erase-remove idiom (and C++20 `std::erase_if` as a forward note); algorithms with predicates; C++17 parallel algorithms (`std::execution::par`) with caveats (library support varies, measure, needs TBB on libstdc++); "no raw loops" as a guideline, not a law.
- leave for later: ranges (day 30), lambdas in depth (day 17).
- builds on: day 15

### day 17: lambdas and closures in depth
- standard: C++17
- objectives: understand what a lambda compiles to; choose captures deliberately; know the cost of `std::function`.
- cover: a lambda is an object of a unique closure type with `operator()`; captures by value, by reference, init-captures (`[p = std::move(ptr)]`), `[this]` versus `[*this]` (C++17); `mutable`; generic lambdas (`auto` parameters); dangling reference captures escaping into a callback or thread (bug and fix); `std::function` type erasure (possible allocation, indirect call, requires copyable callables) versus templates taking `F&&`; immediately invoked lambdas for complex `const` initialization; C++17 constexpr lambdas.
- leave for later: type erasure internals (day 46), templated lambdas `[]<typename T>` (C++20, day 29 may mention).
- builds on: days 03, 12, 16

### day 18: templates: writing code for many types
- standard: C++17
- objectives: write function and class templates; understand deduction, instantiation, and where templates must be defined.
- cover: function templates and template argument deduction (no conversions during deduction); class templates and C++17 class template argument deduction (CTAD) with a deduction guide; non-type template parameters (C++17 `auto` NTTP); full and partial specialization (function templates cannot be partially specialized: overload instead); instantiation and why definitions live in headers (link to day 01); two-phase lookup and `typename`/`template` disambiguators; code bloat and compile time as costs; SFINAE and `std::enable_if` briefly as the pre-concepts tool.
- leave for later: concepts (day 29), `if constexpr` (day 23), variadics (day 19).
- builds on: days 01, 16, 17

### day 19: forwarding references and perfect forwarding
- standard: C++17
- objectives: recognize forwarding references; forward arguments without losing value category; understand variadic templates.
- cover: `T&&` in a deduced context is a forwarding reference, not an rvalue reference; reference collapsing rules (small table); `std::forward<T>` versus `std::move`; why a named rvalue reference is an lvalue (link to day 05); variadic templates and parameter packs; a factory function `make_widget(Args&&...)` and how `emplace_back` uses this; overloading on a forwarding reference is greedy (the "hijacked copy constructor" problem); `auto&&` in range-for.
- leave for later: fold expressions (day 23).
- builds on: days 05, 10, 18

### day 20: exception safety and error handling strategy
- standard: C++17
- objectives: apply the basic, strong, and nothrow guarantees; choose an error-handling strategy for a codebase.
- cover: the three guarantees with a container-insert example; strong guarantee via do-the-work-then-commit (copy-and-swap); `noexcept` as a contract and its effect (`std::terminate` on violation, enables move optimizations); RAII as what makes exceptions workable; exceptions versus error codes versus `std::optional`/result types (`std::expected` is C++23: mention only); real-time and embedded constraints (exceptions disabled with `-fno-exceptions`, deterministic latency concerns stated carefully); throw by value, catch by `const&`; what not to do (exceptions for control flow, swallowing errors); error handling as part of API design.
- leave for later: `std::optional` (day 24), `std::variant` results (day 25), API design (day 47).
- builds on: days 08, 10, 11

### day 21: week 3 review: the library as a vocabulary
- standard: C++17
- review of days 15 to 20 plus spaced repetition from weeks 1 and 2. Mini exercise idea: rewrite a raw loop pipeline with algorithms and lambdas, noting iterator invalidation.
- builds on: days 15 to 20

---

## week 4: modernizing with c++17

The C++17 features that change day-to-day code, ending with a practical refactoring. After this week the reader has a complete standalone refresher.

### day 22: structured bindings, init-statements, and helpful attributes
- standard: C++17
- objectives: use structured bindings and `if`/`switch` initializers to tighten scope and clarify intent.
- cover: structured bindings for pairs, tuples, arrays, and aggregates (map iteration, `insert` results); bindings are names for parts of a hidden object (consequences for references and lambdas: in C++17 they cannot be captured by lambdas, C++20 allows it); `if (auto it = m.find(k); it != m.end())`; `switch` with initializer; `[[nodiscard]]`, `[[maybe_unused]]`, `[[fallthrough]]`; before/after modernization of a lookup function.
- leave for later: making your own types support structured bindings in depth (tuple protocol) as optional detail only.
- builds on: days 03, 15

### day 23: compile-time branching with `if constexpr` and fold expressions
- standard: C++17
- objectives: replace tag dispatch and SFINAE overload sets with `if constexpr`; use fold expressions with parameter packs.
- cover: `if constexpr` discards the untaken branch in templates (and only in templates); before (tag dispatch or `enable_if` overloads) and after; the `static_assert(false)` pitfall in discarded branches (dependent-false trick in C++17; note the C++23 relaxation); fold expressions (unary and binary, left and right) for summing, printing, and checking all arguments; combining folds with `if constexpr`; `constexpr` functions in C++17 (what is allowed) as a bridge to day 33; compile-time versus runtime tradeoff (compile times, readability).
- leave for later: concepts (day 29), consteval/constinit (day 33).
- builds on: days 18, 19

### day 24: `std::optional`: modeling "maybe"
- standard: C++17
- objectives: use `std::optional` for values that may be absent; compare it with sentinel values, pointers, and exceptions.
- cover: before/after: `-1` sentinels and out-parameters versus `std::optional<T>` return; `has_value`, `value` (throws `std::bad_optional_access`), `operator*` (UB if empty), `value_or`; `std::nullopt`; in-place construction; storage is inline (no heap allocation; size is at least `sizeof(T)` plus a flag); no `optional<T&>` (use `T*`); `optional<bool>` and `optional<pointer>` confusion; optional as a member versus a parameter (prefer overloads or defaults for parameters); optional does not say why something is missing (link to day 20 and day 25).
- leave for later: C++23 monadic operations (`and_then`, `transform`): mention as C++23 only.
- builds on: days 04, 20

### day 25: `std::variant` and `std::any`: sum types and type-erased values
- standard: C++17
- objectives: model "one of several types" with `std::variant`; know why `std::any` is rarely the right answer.
- cover: variant as a type-safe union; `std::get`, `std::get_if`, `std::holds_alternative`; `std::visit` with the `overloaded` lambda pattern (C++17 needs the deduction guide; mention that C++20 aggregate CTAD makes it optional); a state machine or message type for a robot or radar pipeline; variant versus inheritance (closed versus open set of types: the expression problem in one paragraph); `valueless_by_exception`; `std::monostate`; `std::any` (type-erased single value, `any_cast`, likely heap allocation for large types, loses static type information) and its narrow legitimate uses; a variant-based result type as an error-handling option.
- leave for later: type erasure techniques (day 46).
- builds on: days 13, 17, 20, 24

### day 26: `std::string_view` and non-owning views
- standard: C++17
- objectives: use `std::string_view` for read-only string parameters; avoid its lifetime traps.
- cover: what a string_view is (pointer plus length, no ownership, not necessarily null-terminated); before/after: `const std::string&` parameters forcing allocations from literals versus `std::string_view`; substrings without copying (parsing a config line or NMEA/telemetry sentence); dangling: returning a view into a temporary string, storing views in members, `std::string_view sv = std::string("x") + "y";`; passing to C APIs that need null termination; `std::from_chars`/`std::to_chars` (C++17) for allocation-free, locale-free numeric parsing; non-owning view as a general design idea (borrowing versus owning, preview of `std::span` on day 31).
- leave for later: `std::span` (day 31).
- builds on: days 03, 04, 24

### day 27: `std::filesystem` and a practical C++17 refactoring
- standard: C++17
- objectives: use `std::filesystem` for portable path and directory work; consolidate week 4 by modernizing a realistic piece of legacy code.
- cover: `std::filesystem::path` (composition with `/`, `extension`, `stem`), `exists`, `directory_iterator`/`recursive_directory_iterator`, `file_size`, error handling via exceptions versus `std::error_code` overloads, TOCTOU races; then a before/after refactoring of a C++03-style log-or-config loader into C++17 using filesystem, `std::optional`, `std::string_view`, structured bindings, and `[[nodiscard]]`; keep the refactor small and explain each change and why one change was deliberately not made.
- leave for later: legacy refactoring strategy at scale (day 54).
- builds on: days 20, 22, 24, 26

### day 28: week 4 review: a complete C++17 refresher
- standard: C++17
- review of days 22 to 27, plus a short "you now have a complete refresher" checkpoint with spaced-repetition questions from weeks 1 to 3. Mini exercise idea: modernize a short pre-C++17 function using at least three week 4 features.
- builds on: days 22 to 27

---

## week 5: the c++20 toolbox

C++20's everyday features: constraints, ranges, views, comparisons, compile-time programming, and formatting.

### day 29: concepts: constraining templates
- standard: C++20
- objectives: constrain templates with concepts for clearer interfaces and errors; write a simple concept.
- cover: the problem: unconstrained template errors and SFINAE noise (link to day 18); `requires` clauses, constrained template parameters (`template <std::integral T>`), abbreviated function templates (`void f(std::integral auto x)`); standard concepts (`std::integral`, `std::floating_point`, `std::same_as`, `std::convertible_to`, `std::invocable`, `std::regular`, `std::totally_ordered`); writing a concept with a `requires` expression (simple, type, compound requirements); overload selection by constraints and subsumption (briefly); concepts should express semantic requirements, not just syntax; templated lambdas `[]<typename T>(T x)`.
- leave for later: ranges concepts (day 30).
- builds on: days 18, 19, 23

### day 30: ranges and views: lazy pipelines
- standard: C++20
- objectives: use range algorithms and view pipelines; understand laziness, ownership, and dangling.
- cover: range algorithms (`std::ranges::sort(v)`, projections `std::ranges::sort(people, {}, &Person::age)`); views as lazy, cheap-to-copy adaptors: `filter`, `transform`, `take`, `drop`, `iota`, `reverse`, `keys`/`values`, `split` (C++20 semantics); the pipe syntax; before/after from a loop with temporaries to a pipeline; views do not own (dangling with temporaries; `std::ranges::dangling`); `filter_view` caches `begin()` (cannot iterate a const filter view; mutation pitfalls); no `std::ranges::to` in C++20 (C++23): build containers explicitly; debugging and compile-time costs; when a plain loop is clearer.
- leave for later: span (day 31).
- builds on: days 16, 17, 26, 29

### day 31: `std::span`: views over contiguous memory
- standard: C++20
- objectives: replace pointer-plus-length parameters with `std::span`; understand static versus dynamic extent.
- cover: before/after: `void process(const float* data, size_t n)` versus `std::span<const float>`; construction from arrays, `std::vector`, `std::array`; `subspan`, `first`, `last`; static extent `std::span<T, N>` versus `std::dynamic_extent`; `as_bytes` for serialization; `std::span` has no bounds-checked `at()` in C++20 (`operator[]` out of range is UB; `at` arrives in C++26); spans of const versus mutable; dangling from a temporary vector; span versus string_view versus ranges views; a radar sample buffer or image row example; span in API design (borrowing contiguous data regardless of the owner's container).
- leave for later: data layout (day 51).
- builds on: days 04, 26, 30

### day 32: three-way comparison and defaulted equality
- standard: C++20
- objectives: use `operator<=>` and defaulted comparisons to remove boilerplate; understand comparison categories.
- cover: before: six hand-written operators; after: `auto operator<=>(const T&) const = default;` and `bool operator==(const T&) const = default;`; the rewriting rules (the compiler synthesizes `<`, `>`, `<=`, `>=` from `<=>` and `!=` from `==`; reversed arguments); comparison categories `std::strong_ordering`, `std::weak_ordering`, `std::partial_ordering` (floating point and NaN); why defaulted `<=>` does not imply a defaulted `==` when you write `<=>` yourself, and why `==` is separate (performance of equality for strings and containers); a custom `<=>` for a version number or a case-insensitive key; lexicographic member order matters; mixed-type comparisons.
- leave for later: concepts like `std::totally_ordered` were on day 29.
- builds on: days 09, 29

### day 33: compile-time programming in C++20
- standard: C++20
- objectives: choose between `constexpr`, `consteval`, and `constinit`; understand what can run at compile time and why you might want it.
- cover: `constexpr` functions relaxed over versions (C++20: `try` blocks, virtual functions, `std::vector`/`std::string` transient allocation in constant evaluation, with the rule that allocations must not escape); `consteval` immediate functions (guaranteed compile-time, e.g., checked format strings or unit conversions); `constinit` for avoiding static initialization order problems (link to day 03); `std::is_constant_evaluated()`; lookup tables generated at compile time (a CRC or sine table); non-type template parameters of class type (C++20) briefly; costs: compile time, debugging difficulty, binary size; compile-time versus runtime as a design tradeoff.
- leave for later: `if consteval` is C++23 (mention only).
- builds on: days 03, 23, 29

### day 34: `std::format` and other everyday C++20 improvements
- standard: C++20
- objectives: format text safely with `std::format`; know a handful of small C++20 features that make code clearer.
- cover: `std::format` versus `printf` (type safety) and iostreams (verbosity, stateful manipulators); format spec mini-language (`{:>8.3f}`, `{:#x}`, positional args); compile-time checking of format strings in C++20 (`std::format_string`, after the P2216 defect report); custom `std::formatter` specialization for a domain type; `std::format_to` and `std::format_to_n` with output iterators to avoid allocations; `std::print` is C++23; library support note (GCC 13+, Clang/libc++ 17+, MSVC 19.29+; on older toolchains the {fmt} library offers the same API). Then a quick tour: designated initializers, `contains` on associative containers, `starts_with`/`ends_with`, `std::erase`/`std::erase_if`, `std::source_location` (preview of day 53), `<bit>` (`std::popcount`, `std::bit_cast`, `std::endian`), `using enum`, `[[likely]]`/`[[unlikely]]` (with a caution), `std::midpoint`, `std::ssize`.
- builds on: days 15, 16, 26, 33

### day 35: week 5 review: the C++20 toolbox
- standard: C++20
- review of days 29 to 34 plus spaced repetition from weeks 2 to 4. Mini exercise idea: write a constrained function that takes a `std::span` and returns a statistic, formatted with `std::format`.
- builds on: days 29 to 34

---

## week 6: concurrency and multithreading

Threads, synchronization, and the memory model, with an emphasis on designs that avoid trouble.

### day 36: threads and `std::jthread`
- standard: C++20
- objectives: start, join, and stop threads safely; prefer `std::jthread` with cooperative cancellation.
- cover: `std::thread` lifecycle, joinable destruction calls `std::terminate`; `join` versus `detach` (why detach is rarely right); arguments are copied into the thread (`std::ref` and dangling references); `std::jthread` joins in its destructor; `std::stop_token`, `std::stop_source`, `std::stop_callback`; a sensor polling thread with a clean shutdown (before/after with an `std::atomic<bool>` flag versus stop_token); `std::thread::hardware_concurrency` (a hint, may be 0); exceptions escaping a thread function call `std::terminate`; thread creation cost and why pools exist (preview day 41).
- builds on: days 08, 17

### day 37: data races and mutexes
- standard: C++17
- objectives: define a data race precisely; protect shared state with mutexes and RAII locks.
- cover: data race definition: two conflicting accesses, at least one write, not ordered by happens-before, at least one non-atomic: UB (link to day 06); race condition versus data race (a higher-level timing bug can exist without a data race); a shared counter bug and fix; `std::mutex`, `std::lock_guard`, `std::unique_lock` (deferred, movable, needed for condition variables), `std::scoped_lock` (C++17, multiple mutexes); `std::shared_mutex` with `std::shared_lock` for readers/writers (and why it is not automatically faster); keep critical sections small; encapsulating the mutex with the data it protects (a `Synchronized<T>` style wrapper, or a class whose methods lock); never return references to guarded data.
- builds on: days 06, 08, 36

### day 38: condition variables and the producer-consumer queue
- standard: C++17
- objectives: wait for conditions correctly; build a bounded thread-safe queue.
- cover: busy-waiting versus condition variables; `std::condition_variable::wait(lock, predicate)`; spurious wakeups and lost wakeups (bug: notify before the waiter checks a condition that is not protected by the mutex); notify while holding the lock or after unlocking (both correct, tradeoff); a bounded blocking queue with close/shutdown semantics; `std::condition_variable_any` and C++20 stop-token-aware waits (`wait(lock, stoken, pred)`); back-pressure as a design decision in a radar or camera pipeline (drop oldest versus block producer).
- builds on: days 36, 37

### day 39: futures, promises, and tasks
- standard: C++17
- objectives: return results and exceptions from asynchronous work; understand `std::async` pitfalls.
- cover: `std::promise`/`std::future` as a one-shot channel; exceptions propagate through futures (`set_exception`, `get()` rethrows); `std::packaged_task`; `std::async` with `std::launch::async` versus `deferred` (default policy lets the implementation choose); the blocking destructor of a future returned from `std::async` (the "accidentally sequential" bug); `std::shared_future` for multiple consumers; no continuations (`.then`) in standard C++20; when to use futures versus a queue or a thread pool; a parallel computation over chunks of a point cloud.
- builds on: days 20, 36, 38

### day 40: atomics and the memory model
- standard: C++20
- objectives: use `std::atomic` correctly; understand happens-before and the main memory orders.
- cover: atomics make single operations indivisible and race-free; `load`, `store`, `exchange`, `fetch_add`, `compare_exchange_weak/strong` (a CAS loop); the problem: compilers and CPUs reorder; sequenced-before, synchronizes-with, happens-before explained with a message-passing example (data + flag); `memory_order_seq_cst` (default), `acquire`/`release` (the flag pattern), `relaxed` (counters only); `memory_order_consume` is discouraged; `is_lock_free`; `std::atomic_flag`, C++20 `wait`/`notify_one` on atomics, `std::atomic_ref` (C++20); false sharing and `std::hardware_destructive_interference_size` (C++17, library support varies); advice: default to seq_cst and mutexes, weaken orders only with measurement and a reason; lock-free does not mean faster.
- builds on: days 06, 37
- note: `volatile` misconception was covered on day 06.

### day 41: deadlocks and concurrency design
- standard: C++20
- objectives: avoid deadlocks and choose higher-level concurrency structures; apply C++20 synchronization primitives.
- cover: deadlock conditions (circular wait); lock ordering, `std::scoped_lock` for multiple locks; calling unknown code (callbacks) under a lock as a deadlock and reentrancy hazard; lock hierarchy idea; livelock and starvation briefly; C++20 `std::latch`, `std::barrier`, `std::counting_semaphore` with one example each (startup synchronization, phased simulation, limiting concurrent requests); task-based design and a minimal thread pool sketch (using day 38's queue), and why production code usually uses an existing pool/executor; designing for concurrency: confine data to threads, message passing, immutable shared data; testing concurrent code (ThreadSanitizer, stress tests).
- builds on: days 36 to 40

### day 42: week 6 review: sharing safely
- standard: C++20
- review of days 36 to 41 plus spaced repetition from weeks 2 and 5. Mini exercise idea: spot the race or deadlock in a short snippet and fix it.
- builds on: days 36 to 41

---

## week 7: software design and deeper c++

Design principles applied with judgment, plus C++20's two largest new language features.

### day 43: SOLID, coupling, and cohesion without dogma
- standard: C++17
- objectives: use SOLID as heuristics; reason about coupling and cohesion in a C++ codebase.
- cover: each SOLID principle in a sentence plus a compact C++ illustration where it helps (SRP via a class doing parsing, filtering, and I/O; OCP via a new sensor type; LSP linked to day 13; ISP via a fat interface split; DIP via a high-level planner depending on an abstraction); coupling (what changes together) and cohesion (what belongs together), with physical coupling in C++ (header dependencies, compile times); where SOLID goes wrong (interface-per-class, premature abstraction, indirection that hides control flow); YAGNI; a "smallest thing that keeps options open" approach.
- builds on: days 11, 12, 13

### day 44: dependency injection and testable seams
- standard: C++20
- objectives: inject dependencies to make code testable and flexible; pick the right kind of seam.
- cover: the problem: a controller that constructs its own hardware driver and reads the clock directly (untestable); constructor injection with an abstract interface (`std::unique_ptr<IClock>` or a reference); templates as compile-time injection (with a concept, C++20); `std::function` as a lightweight seam; link-time seams (choosing an implementation at link time); a fake versus a mock; avoiding DI frameworks and service locators in C++ unless there is a strong reason; testing a controller with a fake clock and a fake actuator; cost and complexity tradeoffs of each seam.
- builds on: days 12, 13, 17, 29, 43

### day 45: design patterns in modern C++: strategy, factory, and observer
- standard: C++17
- objectives: implement classic patterns idiomatically and know when they are unnecessary.
- cover: strategy: virtual interface versus `std::function` versus template parameter (a table of tradeoffs), with a path-planning or filtering strategy; factory: a function returning `std::unique_ptr<Base>`, and a registry mapping names to creators (careful with static-registration tricks and linker dead-stripping); observer: the dangling-observer problem, subscription tokens that unsubscribe in their destructor (RAII), `weak_ptr`-based observers, and notifying outside the lock (link to day 41); patterns as vocabulary, not goals; mention that many classic patterns collapse to a lambda or a variant in modern C++ (command, visitor via `std::visit`).
- builds on: days 12, 17, 25, 41, 43

### day 46: static versus dynamic polymorphism and type erasure
- standard: C++20
- objectives: choose between virtual functions, templates/concepts, `std::variant`, and type erasure; implement a small type-erased wrapper.
- cover: the four options with a table (open versus closed set of types, binary size, compile times, call cost, value semantics, ABI); CRTP briefly as static polymorphism (and that C++23 deducing `this` simplifies it: mention only); how `std::function` and `std::any` erase types; hand-written type erasure with an internal concept/model pair (a `Shape` or `Drawable` with value semantics, around 30 lines); small buffer optimization as an implementation detail; the "inheritance is the base class of evil" argument (value semantics without forcing user types to inherit); when to stop: virtual interfaces are often the simplest answer.
- builds on: days 13, 17, 25, 29, 45

### day 47: designing APIs that are hard to misuse
- standard: C++20
- objectives: design interfaces that express contracts, ownership, and errors clearly, and that stay stable.
- cover: preconditions, postconditions, invariants (and that contracts as a language feature are not in C++20); strong types instead of `double, double, double` (a units example: `Meters`, `Seconds`); ownership in signatures recap (link to day 12) and `std::span`/`std::string_view` parameters; `[[nodiscard]]` and `explicit`; error channel choice (exceptions, error codes, optional, variant results) and consistency across an API; const-correctness as contract; the pimpl idiom for compile-time firewalls and ABI stability (with `std::unique_ptr` and an out-of-line destructor); ABI versus API stability in shared libraries; Hyrum's law in one paragraph; versioning and deprecation (`[[deprecated]]`).
- builds on: days 04, 12, 20, 26, 31

### day 48: C++20 modules and coroutines: a practical first look
- standard: C++20
- objectives: understand what modules and coroutines change and the current state of tooling; read and write a simple module and a simple coroutine.
- cover: modules (about 40 percent of the lesson): why (textual inclusion costs, macro leakage, ODR fragility from day 01), `export module`, `import`, module interface versus implementation units, global module fragment for legacy headers, header units; macros do not cross module boundaries; build-system and compiler support caveats (needs a build system that scans dependencies; CMake 3.28+ with Ninja; standard library module `import std;` is C++23); adopt incrementally. Coroutines (about 60 percent): a coroutine is a function that can suspend (`co_await`, `co_yield`, `co_return`); the coroutine frame (usually heap-allocated, elision possible); C++20 provides the machinery, not ready-made types (`std::generator` is C++23); a minimal hand-written generator with a `promise_type` (around 40 lines, explained); lifetime pitfalls (references parameters dangling across suspension points); where coroutines shine (async I/O, state machines) and when not to use them; using a library (cppcoro, Asio, folly) in practice.
- builds on: days 01, 03, 08

### day 49: week 7 review: design with judgment
- standard: C++20
- review of days 43 to 48 plus spaced repetition from weeks 3 to 6. Mini exercise idea: refactor a tightly coupled class to accept an injected dependency and write a fake for it.
- builds on: days 43 to 48

---

## week 8: production engineering and integration

Making code fast, observable, testable, and maintainable, then putting it all together.

### day 50: measure first: benchmarking and profiling
- standard: C++17
- objectives: design trustworthy measurements; know the common benchmarking traps.
- cover: why intuition fails; wall-clock timing with `std::chrono::steady_clock` (not `system_clock`, not `high_resolution_clock` blindly); microbenchmark traps: dead-code elimination, constant folding, warm-up, CPU frequency scaling, noisy neighbors, debug builds, single runs; using a benchmark library (Google Benchmark `benchmark::DoNotOptimize`, `State` loop) shown in a small example; statistics (repeat, report median and spread, not just mean); profilers (sampling: `perf`, VTune, Instruments; instrumentation: Tracy) and flame graphs; benchmarks in CI: regression detection and its noise; Amdahl's law in one paragraph; optimization as an engineering decision (maintainability cost).
- builds on: days 15, 16

### day 51: cache locality and data-oriented design
- standard: C++17
- objectives: reason about memory hierarchy effects; restructure data for access patterns.
- cover: the memory hierarchy with rough, clearly approximate latency orders of magnitude (registers, L1, L2, L3, DRAM; stated as typical orders of magnitude that vary by hardware); cache lines and prefetching; vector of objects versus vector of pointers versus linked list traversal; array of structs (AoS) versus struct of arrays (SoA) for a particle or radar detection update loop; hot/cold splitting; false sharing recap (day 40); data-oriented design versus object-oriented design as a tradeoff (encapsulation and flexibility versus throughput); measure with the tools from day 50 and hardware counters (cache misses via `perf stat`).
- builds on: days 15, 40, 50

### day 52: the cost of allocation
- standard: C++17
- objectives: find and reduce unnecessary heap allocations; know the tools (`reserve`, small buffer optimization, pmr, pooling).
- cover: what `new` costs (allocator bookkeeping, locking or thread caches, fragmentation, non-deterministic latency in real-time loops); hidden allocations (string concatenation, `std::function`, `shared_ptr`, node containers, exceptions); `reserve` and reuse (clear keeps capacity); small string optimization (implementation-defined capacity); `std::pmr` (C++17): `memory_resource`, `monotonic_buffer_resource` with a stack buffer, `unsynchronized_pool_resource`, pmr containers, propagation pitfalls; object pools; allocation-free steady state in a control loop (preallocate at startup); measuring allocations (counting `operator new` replacement, heap profilers).
- builds on: days 12, 15, 17, 50

### day 53: testing and observability
- standard: C++20
- objectives: structure tests that catch real bugs; instrument production code with logs, metrics, and traces.
- cover: the test pyramid in C++ terms (unit, integration, hardware-in-the-loop for robotics); a unit test with a fake from day 44 (shown with a minimal framework-neutral style plus a note on GoogleTest/Catch2); testing behavior not implementation; property-based and fuzz testing (libFuzzer) for parsers; sanitizers in CI (ASan, UBSan, TSan) and why they need separate builds; observability: structured logging with `std::source_location`, log levels and cost of disabled logs, metrics (counters, histograms), tracing spans with RAII scope timers; compile-time switches versus runtime levels; avoiding logging inside hot loops and under locks.
- builds on: days 06, 08, 34, 41, 44

### day 54: refactoring legacy code and architectural tradeoffs
- standard: C++17
- objectives: modernize a legacy codebase safely and incrementally; weigh architectural tradeoffs explicitly.
- cover: characterization tests before changes; seams in legacy code (link to day 44); incremental modernization order (warnings and sanitizers first, then RAII and smart pointers at boundaries, then `std::` vocabulary types); automated tools (`clang-tidy` `modernize-*` checks, `clang-format`); the strangler pattern for replacing subsystems; when not to refactor; architectural tradeoffs as explicit decisions (maintainability versus performance, abstraction versus overengineering, compile-time versus runtime flexibility, OOP versus data-oriented), with a short decision record example; a before/after legacy snippet (raw `new`/`delete`, out-parameters, `char*`) modernized step by step.
- builds on: days 08, 12, 24, 26, 27, 43, 44, 53

### day 55: putting it together: a small sensor-processing pipeline
- standard: C++20
- objectives: see the course's ideas working together in one small, coherent program and justify each design choice.
- cover: an integrated example of about 120 to 160 lines total, presented in 3 or 4 parts: a `Detection` value type with defaulted comparison; a `std::variant` message type; a bounded queue (day 38) between a producer `std::jthread` simulating a sensor and a consumer stage; a processing stage constrained by a concept and operating on `std::span`; ranges for filtering; RAII for shutdown; injected clock or sink for testability; avoid `std::format` in the compiled code if it would block compile-checking (or note it clearly). After the code: a design-review table listing each decision, the alternative, and why. The example should compile with `-std=c++20`.
- builds on: days 12, 25, 29, 30, 31, 32, 36, 38, 44

### day 56: week 8 review and the road ahead
- standard: C++20
- review of days 50 to 55, plus a final cross-course spaced-repetition set (one question each from weeks 1 to 7), and a short "where to go next" note (C++23 highlights to explore: `std::expected`, `std::print`, deducing `this`, `std::generator`, `std::mdspan`, `std::flat_map`; C++26 contracts and reflection direction as forward-looking, not detailed). Mini exercise idea: extend the day 55 pipeline with one feature and decide which seam it belongs behind.
- builds on: days 50 to 55
