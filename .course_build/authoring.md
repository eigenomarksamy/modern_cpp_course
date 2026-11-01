# authoring guide (curriculum 2.0)

how lessons are written, checked, and assembled. `tools/course.py validate` enforces everything marked **checked**.

## where things live

| path | what it is |
| --- | --- |
| `curriculum.json` | module order, lesson order, and the explicit v1 progress mapping (**checked**: every lesson listed once and has a file) |
| `lessons/<id>.md` | one lesson per file; the file name is the lesson's stable id |
| `sections/*.md` | introduction, overview, cheat sheet, references |
| `curriculum.md` | generated curriculum map (day, objective, prerequisites, minutes, deeper topics, v1 mapping) |
| `tools/` | `course.py` (validate, assemble, stats), `editorial.py`, `readtime.py`, `check_code.py`, `check_ui.py` |
| `checks/` | the latest compile-check reports |
| `archive/v1/` | the original 56-day course, unchanged |

day numbers are not stored anywhere in a lesson. they come from the order in `curriculum.json`, so moving, splitting, or inserting a lesson renumbers everything after it on the next assembly, and every cross reference follows.

## a lesson file

```markdown
---
title: moving: transferring resources instead of copying them
standard: C++17
objective: implement move operations, explain why `std::move` is only a cast, and state what a moved-from object promises
prerequisites: copy-semantics, value-categories
difficulty: 3
---

### the idea
### understanding the concept
### in code
### in practice
### watch out for
### the takeaway
### optional challenge
### going deeper          (optional, always last)
#### a topic
```

- **checked:** frontmatter has `title`, `standard` (`C++17` or `C++20`, the minimum standard the examples need), `objective` (one learning goal, at least six words), `prerequisites` (lesson ids that come earlier, or `none`), and `difficulty` (1 to 3, used by the reading-time estimate). reviews add `kind: review`.
- **checked:** the sections appear exactly in this order, each with real content; `in code` has a code block; the optional challenge ends with a collapsed `<details><summary>answer</summary>` block.
- reviews use `recap`, `review questions`, `mini exercise`, `answers` (each answer in its own `<details>`), and `connections`. **checked:** every module ends with a review, the review lists the module's lessons as prerequisites, and there are never more than eight lessons in a row without one. run `python site_upgrade/renumber_reviews.py lessons/review-*.md` after editing review questions to renumber them and their answers.
- headings inside a lesson start at `###`; the assembler shifts them for each view.

## one objective per day, 5 to 10 minutes of core reading

each lesson teaches one idea. when a lesson grows past its budget, split it along the idea's natural stages (the problem, the mechanism, the implementation, the pitfalls) rather than compressing the explanation. material that is useful but not needed for the objective (detailed rules, rare edge cases, longer examples) goes into `going deeper`, which the website collapses. nothing needed for correctness may live only in `going deeper`.

**checked:** the estimated core reading time is at most 10.5 minutes; under 4 minutes is a warning. the estimate (`tools/readtime.py`) counts prose at 200 words per minute, code by lines and tokens (output and shell blocks at half weight), review questions at 15 seconds each, and scales by difficulty. it is approximate by design and most useful for comparing lessons. `python tools/course.py stats` prints it for every lesson.

## cross references

write `[[lesson-id]]` (rendered as "day 21" linking to the lesson), `[[lesson-id|custom text]]`, or `[[module:module-id]]`. **checked:** every reference resolves. do not write day numbers by hand. C++ attributes such as `[[nodiscard]]` belong in backticks, where they are never treated as references.

## code blocks

every fence has a language (`cpp`, `text`, `sh`; **checked**). C++ fences carry a tag that says what the example is, and the website labels it accordingly:

| fence | meaning | what `tools/check_code.py` does |
| --- | --- | --- |
| `` ```cpp complete `` | a standalone translation unit | compiles it; runs it if it has `main()` (with `--run`) |
| `` ```cpp complete norun `` | standalone, but must not be run (leaks or waits on purpose) | compiles it |
| `` ```cpp ub `` | compiles, contains undefined behavior on purpose | compiles it; never runs it |
| `` ```cpp fails `` | ill-formed on purpose | checks that it does **not** compile |
| `` ```cpp group=NAME `` | one part of a program split across blocks | concatenates the parts in course order, compiles and runs them |
| `` ```cpp external `` | needs several files, modules support, or a library | skips it |
| `` ```cpp `` | a snippet (fragment) | skips it |

add `c++20` to a block in a C++17 lesson that needs C++20. complete, failing, UB, and grouped examples get a Compiler Explorer link on the website; snippets and external examples do not, because they cannot compile on their own. mark output with `// prints: ...` and broken code with `// BUG: ...`, and say whether something is undefined, unspecified, or implementation-defined.

## editorial style

- **checked:** prose is lowercase, including the start of every sentence and every heading. capitals are allowed only for acronyms (`RAII`, `UB`), `C++` and its versions, proper names and products (the allowlist in `tools/editorial.py`), and identifiers that appear in the course's code. code, inline code, URLs, HTML tags, quotations, and italic titles are never checked.
- **checked:** no em dashes in prose. use commas, colons, parentheses, or separate sentences.
- **checked:** no placeholders (`TODO`, "to be added", and the like).
- `python tools/check_ui.py` applies the same rules to the generated website: navigation, buttons, labels, messages in `site/app.js`, and rendered lesson text.
- voice: one experienced engineer talking to another. direct, practical, a little opinionated; no hype; no "in this lesson we will".
- no unsupported performance claims: say what dominates and how to measure. no C++23 features presented as C++20; mark forward notes "C++23".

## editing workflow

```sh
python .course_build/tools/course.py check move-semantics       # one lesson, with curriculum context
python .course_build/tools/course.py validate                   # everything
python .course_build/tools/check_code.py --run --only move-semantics
python .course_build/tools/course.py assemble                   # writes the document, site/course.json, curriculum.md
npm run build && npm test                                       # website, then site tests
```

`assemble` refuses to publish if anything fails validation, and only replaces the published files after the assembled document also passes its own checks (anchors, links, references).
