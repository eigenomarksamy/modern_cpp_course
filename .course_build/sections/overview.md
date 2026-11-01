<a id="course-overview"></a>

## course overview

the modules build on each other in order. the first nine rebuild the foundations and finish with a complete C++17 refresher; the rest add C++20, concurrency, design, and production engineering.

```text
 foundations -> values -> lifecycle -> ownership -> polymorphism -> library -> generic
      -> results -> variants, views, files              (a complete C++17 refresher)
      -> C++20 generic -> C++20 everyday
      -> threads -> futures and atomics
      -> design -> abstractions -> performance -> production
```

the curriculum map below lists every day: its module, its title, the standard its examples need, and its approximate core reading time. each lesson page also states its objective and the lessons it builds on.

### the threads that run through every module

some ideas are not confined to one module; they come back repeatedly, each time with more depth:

- **lifetime and ownership:** [[storage-duration]], [[temporaries-dangling]], [[raii]], [[move-semantics]], [[ownership-in-interfaces]], [[callbacks]], [[string-view]], [[view-lifetimes]], [[span]], [[jthread]], [[observer]], [[api-stability]], [[coroutines]].
- **error handling:** [[exception-safety]], [[error-strategy]], [[optional]], [[variant]], [[filesystem]], [[futures]], [[api-contracts]], [[testing]].
- **compile time versus run time:** [[function-templates]], [[if-constexpr]], [[concepts]], [[constexpr-evolution]], [[consteval-constinit]], [[test-seams]], [[static-polymorphism]].
- **design judgment** (coupling, cohesion, abstraction cost): [[constructors]], [[composition-over-inheritance]], [[callbacks]], [[variant-design]], [[mutexes]], [[solid]], [[coupling-cohesion]], [[dependency-injection]], [[strategy]], [[architecture-decisions]].
- **performance and measurement:** [[object-layout]], [[sequence-containers]], [[algorithms]], [[atomic-waiting]], [[benchmarking]], [[cache-locality]], [[allocation-costs]].

### pacing

each day takes about 5 to 10 minutes. if you miss a day, read two the next day, or use the review day to catch up; the reviews are deliberately light. if a topic hooks you, open the lesson's "going deeper" section, or the [references](#references) at the end.
