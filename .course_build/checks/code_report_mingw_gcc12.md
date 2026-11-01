# code check report

generated 2026-11-01T04:35:37+00:00 on `win32`; run: True; sanitizers: False.

| example | kind | standard | compiler | status | detail |
| --- | --- | --- | --- | --- | --- |
| `build-pipeline#2` | external | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | needs other files, modules, or a library |
| `build-pipeline#4` | external | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | needs other files, modules, or a library |
| `build-pipeline#6` | external | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | needs other files, modules, or a library |
| `linkage-odr#0` | external | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | needs other files, modules, or a library |
| `linkage-odr#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `linkage-odr#3` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `linkage-odr#4` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `initialization#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `initialization#1` | fails | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | rejected as intended |
| `initialization#3` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `initialization#4` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `integer-types#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `integer-types#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `integer-types#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `integer-types#3` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `object-layout#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `object-layout#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `object-layout#4` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `storage-duration#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `storage-duration#1` | external | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | needs other files, modules, or a library |
| `storage-duration#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-foundations#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `temporaries-dangling#0` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `temporaries-dangling#1` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `pointers-references#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `pointers-references#1` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `pointers-references#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `pointers-references#3` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `const-correctness#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `const-correctness#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `const-correctness#3` | fails | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | rejected as intended |
| `value-categories#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `value-categories#5` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `copy-elision#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `copy-elision#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `undefined-behavior#0` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `undefined-behavior#1` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `ub-usual-suspects#0` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `ub-usual-suspects#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-values#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `raii#3` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `scope-guards#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `constructors#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `construction-order#0` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `construction-order#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `copy-semantics#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `move-semantics#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-lifecycle#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-lifecycle#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `noexcept-moves#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `special-members#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `special-members#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `special-members#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `rule-of-zero#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `rule-of-zero#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `rule-of-zero#3` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `unique-ptr#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `shared-ptr#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `ownership-in-interfaces#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-ownership#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-ownership#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `virtual-dispatch#1` | fails | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | rejected as intended |
| `virtual-dispatch#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `virtual-destructors-slicing#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `review-polymorphism#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `sequence-containers#0` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `sequence-containers#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `sequence-containers#2` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `associative-containers#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `associative-containers#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `algorithms#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `algorithms#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `algorithms#5` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `lambdas#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `lambdas#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `lambdas#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `lambdas#3` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `callbacks#0` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `callbacks#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-library#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-library#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `function-templates#0` | fails | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | rejected as intended |
| `function-templates#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `function-templates#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `function-templates#3` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `function-templates#5` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `class-templates#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `class-templates#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `forwarding-references#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `forwarding-references#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `variadic-templates#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `variadic-templates#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `if-constexpr#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `if-constexpr#3` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `fold-expressions#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `fold-expressions#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `fold-expressions#3` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-generic#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `structured-bindings#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `init-statements#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `exception-safety#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `exception-safety#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `exception-safety#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `error-strategy#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `optional#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `optional#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `optional#4` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-results#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `variant#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `variant-design#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `string-view#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `parsing-with-views#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `parsing-with-views#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `filesystem#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `filesystem#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `cpp17-refactoring#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `cpp17-refactoring#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-cpp17#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-cpp17#2` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `concepts#1` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `writing-concepts#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `writing-concepts#1` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `writing-concepts#3` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `range-algorithms#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `views#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `views#1` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `views#2` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `span#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `defaulted-comparisons#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `comparison-categories#1` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `constexpr-evolution#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `constexpr-evolution#1` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `consteval-constinit#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `consteval-constinit#1` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `consteval-constinit#2` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `format#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | the standard library has no <format> |
| `format#3` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | the standard library has no <format> |
| `review-cpp20-everyday#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | the standard library has no <format> |
| `threads#0` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `threads#1` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `jthread#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `jthread#1` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `jthread#2` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `data-races#0` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `data-races#2` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `mutexes#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `condition-variables#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `blocking-queue#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-threads#2` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `futures#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `futures#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `async#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `atomics#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `memory-model#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `atomic-waiting#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `atomic-waiting#1` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `deadlocks#0` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `deadlocks#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `sync-primitives#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-async#2` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `solid#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `coupling-cohesion#2` | external | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | needs other files, modules, or a library |
| `dependency-injection#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `test-seams#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `strategy#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `observer#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-design#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `static-polymorphism#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `type-erasure#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `api-contracts#1` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `api-stability#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `api-stability#1` | external | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | needs other files, modules, or a library |
| `api-stability#2` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `modules#0` | external | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | needs other files, modules, or a library |
| `modules#1` | external | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | needs other files, modules, or a library |
| `modules#2` | external | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | needs other files, modules, or a library |
| `coroutine-generator#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `review-abstractions#1` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `benchmarking#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `benchmarking#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |
| `benchmarking#2` | external | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | needs other files, modules, or a library |
| `profiling#1` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `cache-locality#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `data-oriented-design#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `allocation-costs#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `pmr-pools#0` | complete | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `testing#0` | complete | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled |
| `testing#2` | external | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | skipped | needs other files, modules, or a library |
| `legacy-refactoring#0` | ub | c++17 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled (undefined behavior: not run) |
| `group:pipeline` | group | c++20 | g++ (Rev2, Built by MSYS2 project) 12.1. | ok | compiled and ran |

164 snippet checks skipped (fragments are not standalone programs).
