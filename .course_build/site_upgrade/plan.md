# plan: restructuring the course (curriculum 1.0 to 2.0)

this records the audit of the 56-day course and the reasoning behind the restructured curriculum. the generated `../curriculum.md` is the resulting map; `state.json` in this folder records what was done.

## what the audit found

the v1 course covered its subject well, and the problem was density, not quality. measured with the new reading-time estimate (`../tools/readtime.py`: prose at 200 words per minute, code by lines and tokens, difficulty-scaled), a v1 day averaged **12.7 minutes** of core reading, and 55 of 56 days exceeded 10 minutes (the shortest was exactly 10.0, the longest 18.6). the v1 validator accepted them because it only bounded word counts (650 to 2,100 words), and a 1,600-word lesson with 90 lines of code is not a 5-minute read. most v1 days also combined two or three ideas that each deserve a day: copying and moving and `noexcept` in one lesson; atomics and the memory model in one; modules and coroutines in one; three design patterns in one.

per-lesson findings (v1 core minutes with the new estimator, lines of code, and where the material went):

| v1 | title | v1 core min | code lines | became (v2 days) |
| --- | --- | --- | --- | --- |
| 01 | from source file to running program | 12.4 | 51 | 01 `build-pipeline`, 02 `linkage-odr` |
| 02 | types and the many faces of initialization | 12.2 | 75 | 03 `initialization`, 04 `integer-types` |
| 03 | scope, storage duration, and object lifetime | 12.2 | 73 | 06 `storage-duration`, 08 `temporaries-dangling` |
| 04 | pointers, references, and const | 13.9 | 105 | 09 `pointers-references`, 10 `const-correctness` |
| 05 | value categories without the headache | 12.2 | 91 | 11 `value-categories`, 12 `copy-elision` |
| 06 | undefined behavior and other things the standard won't promise | 10.9 | 54 | 13 `undefined-behavior`, 14 `ub-usual-suspects` |
| 07 | week 1 review: the ground beneath your feet | 11.7 | 25 | 15 `review-values` |
| 08 | RAII: let scope do the cleanup | 12.7 | 102 | 16 `raii`, 17 `scope-guards` |
| 09 | constructors, destructors, and the object lifecycle | 12.4 | 92 | 18 `constructors`, 19 `construction-order` |
| 10 | copy and move semantics | 12.2 | 93 | 20 `copy-semantics`, 21 `move-semantics`, 23 `noexcept-moves` |
| 11 | the rule of zero, three, and five | 12.6 | 99 | 24 `special-members`, 25 `rule-of-zero` |
| 12 | smart pointers and ownership in interfaces | 12.3 | 74 | 26 `unique-ptr`, 27 `shared-ptr`, 28 `ownership-in-interfaces` |
| 13 | polymorphism, inheritance, and composition | 12.2 | 84 | 30 `virtual-dispatch`, 31 `virtual-destructors-slicing`, 32 `composition-over-inheritance` |
| 14 | week 2 review: owning your resources | 12.4 | 45 | 29 `review-ownership` |
| 15 | containers and what they cost | 11.1 | 64 | 34 `sequence-containers`, 35 `associative-containers` |
| 16 | iterators and algorithms over raw loops | 12.3 | 63 | 36 `algorithms` |
| 17 | lambdas and closures in depth | 13.5 | 97 | 37 `lambdas`, 38 `callbacks` |
| 18 | templates: writing code for many types | 13.9 | 90 | 40 `function-templates`, 41 `class-templates` |
| 19 | forwarding references and perfect forwarding | 12.5 | 79 | 42 `forwarding-references`, 43 `variadic-templates` |
| 20 | exception safety and error handling strategy | 10.5 | 61 | 49 `exception-safety`, 50 `error-strategy` |
| 21 | week 3 review: the library as a vocabulary | 13.6 | 58 | 39 `review-library` |
| 22 | structured bindings, init-statements, and helpful attributes | 13.7 | 95 | 47 `structured-bindings`, 48 `init-statements` |
| 23 | compile-time branching with `if constexpr` and fold expressions | 14.1 | 80 | 44 `if-constexpr`, 45 `fold-expressions` |
| 24 | `std::optional`: modeling "maybe" | 10.4 | 65 | 51 `optional` |
| 25 | `std::variant` and `std::any`: sum types and type-erased values | 12.5 | 67 | 53 `variant`, 54 `variant-design` |
| 26 | `std::string_view` and non-owning views | 11.4 | 70 | 55 `string-view`, 56 `parsing-with-views` |
| 27 | `std::filesystem` and a practical C++17 refactoring | 13.7 | 92 | 57 `filesystem`, 58 `cpp17-refactoring` |
| 28 | week 4 review: a complete C++17 refresher | 14.2 | 49 | 59 `review-cpp17` |
| 29 | concepts: constraining templates | 13.4 | 80 | 60 `concepts`, 61 `writing-concepts` |
| 30 | ranges and views: lazy pipelines | 13.1 | 75 | 63 `views`, 64 `view-lifetimes` |
| 31 | `std::span`: views over contiguous memory | 12.5 | 78 | 65 `span` |
| 32 | three-way comparison and defaulted equality | 12.4 | 66 | 67 `defaulted-comparisons`, 68 `comparison-categories` |
| 33 | compile-time programming in C++20 | 11.3 | 64 | 69 `constexpr-evolution`, 70 `consteval-constinit` |
| 34 | `std::format` and other everyday C++20 improvements | 14.0 | 83 | 71 `format`, 72 `cpp20-small-features` |
| 35 | week 5 review: the C++20 toolbox | 13.3 | 38 | 66 `review-cpp20-generic`, 73 `review-cpp20-everyday` |
| 36 | threads and `std::jthread` | 12.7 | 93 | 74 `threads`, 75 `jthread` |
| 37 | data races and mutexes | 11.1 | 79 | 76 `data-races`, 77 `mutexes` |
| 38 | condition variables and the producer-consumer queue | 11.1 | 96 | 78 `condition-variables`, 79 `blocking-queue` |
| 39 | futures, promises, and tasks | 11.2 | 75 | 81 `futures`, 82 `async` |
| 40 | atomics and the memory model | 10.9 | 62 | 84 `memory-model`, 85 `atomic-waiting` |
| 41 | deadlocks and concurrency design | 12.8 | 105 | 86 `deadlocks`, 87 `sync-primitives` |
| 42 | week 6 review: sharing safely | 14.8 | 77 | 80 `review-threads`, 88 `review-async` |
| 43 | SOLID, coupling, and cohesion without dogma | 12.5 | 81 | 89 `solid`, 90 `coupling-cohesion` |
| 44 | dependency injection and testable seams | 15.0 | 142 | 91 `dependency-injection`, 92 `test-seams` |
| 45 | design patterns in modern C++: strategy, factory, and observer | 14.7 | 137 | 93 `strategy`, 94 `factory`, 95 `observer` |
| 46 | static versus dynamic polymorphism and type erasure | 12.1 | 85 | 97 `static-polymorphism`, 98 `type-erasure` |
| 47 | designing APIs that are hard to misuse | 12.9 | 89 | 99 `api-contracts`, 100 `api-stability` |
| 48 | C++20 modules and coroutines: a practical first look | 12.0 | 81 | 101 `modules`, 102 `coroutines`, 103 `coroutine-generator` |
| 49 | week 7 review: design with judgment | 15.3 | 71 | 96 `review-design`, 104 `review-abstractions` |
| 50 | measure first: benchmarking and profiling | 12.0 | 69 | 105 `benchmarking`, 106 `profiling` |
| 51 | cache locality and data-oriented design | 10.0 | 47 | 107 `cache-locality`, 108 `data-oriented-design` |
| 52 | the cost of allocation | 10.6 | 63 | 109 `allocation-costs`, 110 `pmr-pools` |
| 53 | testing and observability | 14.2 | 113 | 112 `testing`, 113 `observability` |
| 54 | refactoring legacy code and architectural tradeoffs | 11.4 | 82 | 114 `legacy-refactoring`, 115 `architecture-decisions` |
| 55 | putting it together: a small sensor-processing pipeline | 18.6 | 168 | 116 `pipeline-design`, 117 `pipeline-processing`, 118 `pipeline-wiring` |
| 56 | week 8 review and the road ahead | 12.9 | 16 | 119 `review-final` |

v1 total estimated core reading: 708 minutes over 56 days (12.7 per day).


## decisions

**length follows the material.** the new course has 119 days: 102 lessons and 17 reviews in 17 modules. every v1 lesson was split along its natural stages, and every split gave each resulting day one objective. no v1 lesson was merged with another: none was short or fragmented enough that merging would help, and the reviews already consolidate.

**splits that matter most** (each was an explicit "do not combine" case or the densest material):

- copy semantics, move semantics, and `noexcept` moves became three days; special member rules and the rule of zero two.
- `unique_ptr`, `shared_ptr`/`weak_ptr`, and ownership in signatures became three days.
- virtual dispatch, virtual destructors and slicing, and composition/LSP became three days (a short module of their own).
- atomics, the memory model, and atomic waits/false sharing/lock-freedom became three days; mutexes and data races two; threads and `jthread` two.
- modules, coroutines (use), and coroutines (writing a generator) became three days.
- strategy, factory, and observer became one pattern per day.
- the integrated pipeline became three parts, each with its slice of the design review.

**reordering for prerequisites:**

- structured bindings and `if`/`switch` initializers now come before `std::optional`, whose examples use them, in a "results and failure" module with exception safety and error strategy.
- `if constexpr` and fold expressions moved from the C++17 module into the templates module, next to variadic templates where they belong conceptually.
- the C++17 vocabulary is split into "results and failure" and "variants, views, and files"; the refresher checkpoint stays at the end of the latter.

**gaps filled with new material:**

- a new lesson, *objects in memory: size, alignment, and padding*, gives the object model a home; later lessons on serialization, cache locality, and data layout build on it.
- several days are mostly new framing around v1 material: range algorithms and projections (separate from lazy views), view lifetimes, parsing with views and `from_chars`, atomic operations before memory orders, choosing a seam, and architectural decisions.
- all reviews were rebuilt per module, reusing the best v1 questions and adding spaced repetition from earlier modules.

**optional depth instead of deletion.** detailed rules, rare edge cases, and long worked solutions moved into "going deeper" sections (collapsed on the website, visible in the full course and the Markdown). nothing needed for correctness lives only there.

**rhythm.** modules are 3 to 8 lessons and always end with a review; the validator caps a run without review at 8 lessons. the polymorphism module is deliberately short: its ideas are few and sharp, and its review adds spaced repetition from the ownership modules.

## progress migration policy

v1 stored `#day-NN` per completed day. `curriculum.json` maps each v2 lesson to the v1 days it was derived from (`legacy.v1.complete_when`). a v2 lesson is marked complete on migration only if every listed v1 day was complete. split lessons inherit completion (the reader read that material); lessons with substantially new material, including `object-layout`, `range-algorithms`, `atomics`, and six of the reviews, are never marked complete automatically. the old key is never deleted. old links (`/#day-12`, `/#week-3`, `/#cheat-sheet`) redirect to their v2 equivalents.

## process

1. archive v1 unchanged (`../archive/v1/`), baseline commit `b4ff6d7`.
2. lowercase the v1 prose into a working copy with `../tools/editorial.py` (line numbers preserved): `tools_normalize_v1.py`.
3. one recipe per v1 lesson (`recipes/v1-NN.txt`) maps line ranges and new text into v2 lessons: `apply_recipe.py`. after a recipe ran, the lesson file is canonical.
4. write new lessons and reviews directly.
5. tag every C++ block by compiling it standalone (`classify_blocks.py`, `tag_blocks.py`), then verify with `../tools/check_code.py`.
6. rebuild the assembler, the website, and the tests around stable ids.
