# modern c++ daily course

a course on modern C++17 and C++20 for working engineers: 119 short daily lessons in 17 modules, each with one learning objective and about 5 to 10 minutes of core reading, plus optional "going deeper" material. read it at [cpp.eigenomar.com](https://cpp.eigenomar.com), or as one document in [`modern_cpp_daily_course.md`](modern_cpp_daily_course.md).

## the curriculum

| modules | what they cover |
| --- | --- |
| 1 to 2 | how programs are built, initialization, integers, object layout, lifetime, references, value categories, copy elision, undefined behavior |
| 3 to 5 | RAII, constructors, copying and moving, special members, the rule of zero, smart pointers, ownership in signatures, polymorphism |
| 6 to 7 | containers, algorithms, lambdas and callbacks, templates, forwarding, `if constexpr`, folds |
| 8 to 9 | results and failure (exception safety, error strategy, `optional`), `variant`, `string_view`, `filesystem`; the end of a standalone C++17 refresher |
| 10 to 11 | C++20: concepts, ranges and views, `span`, comparisons, `constexpr`/`consteval`/`constinit`, `std::format` |
| 12 to 13 | threads, data races, mutexes, condition variables, futures, atomics, the memory model, deadlocks |
| 14 to 15 | design: SOLID, coupling, dependency injection, patterns, type erasure, API and ABI design, modules, coroutines |
| 16 to 17 | performance, testing, observability, legacy code, and one small program that puts it all together |

every module ends with a review (recap, questions with spaced repetition, a mini exercise, collapsed answers). the full map, with each day's objective, prerequisites, reading time, and optional topics, is generated into [`.course_build/curriculum.md`](.course_build/curriculum.md).

### why 119 days instead of 56

the first version fit everything into 56 days and 8 weeks. measured honestly, prose plus the time to read code carefully, its days averaged about 12.7 minutes, and most combined two or three ideas (copying and moving and `noexcept`; atomics and the memory model; modules and coroutines). version 2.0 lets the length follow the material: every dense day was split along its natural stages so each day teaches one thing, prerequisites were reordered where a lesson used ideas taught later, a lesson on object size, alignment, and padding was added, and the reviews were rebuilt per module. nothing was dropped: detail that is useful but not needed for a day's objective moved into collapsed "going deeper" sections. [`.course_build/site_upgrade/plan.md`](.course_build/site_upgrade/plan.md) has the audit and the reasoning.

## the website

| route | what it shows |
| --- | --- |
| `/` | dashboard: progress, "continue learning", the curriculum by module, links, progress export and import |
| `/day/NN/` | one lesson: objective, prerequisites, core reading, collapsed optional material, previous and next, mark as completed |
| `/full/` | the whole course on one page with a clickable table of contents |
| `/cheat-sheet/`, `/references/` | the supplementary sections |
| `/modern_cpp_daily_course.md` | the Markdown download |

code blocks have a copy button and a label saying what the example is: a complete example, a snippet, ill-formed on purpose, undefined behavior on purpose, or needing other files or libraries. complete, ill-formed, and UB examples link to Compiler Explorer with the right `-std=` selected; snippets do not, because they cannot compile on their own. search covers lesson titles, objectives, and topics. the site has light and dark themes (following the system, with a toggle) and works at phone width.

### progress

progress lives only in your browser (`localStorage`, key `modern-cpp-course:progress`), as stable lesson ids rather than day numbers, so future curriculum changes cannot shift it. opening a lesson records it as last visited; only the button marks it complete. export writes a JSON file (format, schema version, curriculum version, completed lesson ids, last visited, timestamp); import accepts it in merge or replace mode.

**coming from version 1.0:** the old site stored completed days as `["#day-01", ...]` under `modern-cpp-course:done`. on first visit, the new site migrates them through the explicit mapping in [`.course_build/curriculum.json`](.course_build/curriculum.json): a new lesson counts as complete only if every old day it was derived from was complete, so split lessons inherit your progress and genuinely new material (including most reviews) does not. the old key is left in place, and old links such as `/#day-12` redirect to the matching lesson.

## layout

```text
modern_cpp_daily_course.md      the course as one document (generated)
site/course.json                the same content for the website (generated)
site/style.css, site/app.js     the website's stylesheet and script
scripts/build.mjs               renders site/course.json into dist/
scripts/test-site.mjs           link, accessibility, and headless-browser tests for dist/
wrangler.jsonc                  Cloudflare Worker config (static assets only)
course_spec.md                  the original 1.0 specification
.course_build/
  curriculum.json               modules, lesson order, v1 progress mapping
  lessons/<id>.md               one file per lesson (the canonical content)
  sections/                     introduction, overview, cheat sheet, references
  curriculum.md                 the curriculum map (generated)
  authoring.md                  lesson format, code tags, editorial rules
  handoff.md                    start here when maintaining the course
  tools/                        course.py, check_code.py, check_ui.py, editorial.py, readtime.py
  checks/                       latest compile-check reports
  archive/v1/                   the original 56-day course, unchanged
  site_upgrade/                 how 1.0 became 2.0: plan, recipes, checkpoint state
```

## editing the course

change a lesson in `.course_build/lessons/<id>.md` (or a section, or `curriculum.json` to move or add lessons), then:

```sh
python .course_build/tools/course.py validate              # structure, prerequisites, reading time, style
python .course_build/tools/check_code.py --run             # compile the tagged examples (GCC and Clang if found)
python .course_build/tools/course.py assemble              # regenerate the document, manifest, and curriculum map
npm run build && npm test                                  # build the website and test it
```

lessons are identified by their file name; day numbers and cross references (`[[lesson-id]]`) are computed at assembly, so adding or splitting a lesson renumbers everything automatically. never rename a lesson id: browsers store progress by id. [`.course_build/authoring.md`](.course_build/authoring.md) describes the lesson format and conventions.

### editorial style

all prose is lowercase, including the start of every sentence and every heading. capitals are kept only for acronyms (RAII, UB), `C++` and its versions, proper names and products (Linux, GitHub, CMake), and exact identifiers; code, URLs, and quotations are never changed. there are no em dashes. `course.py validate` checks the sources and `.course_build/tools/check_ui.py` checks the generated pages, reporting file and line for anything suspicious.

### reading time

each lesson shows an approximate reading time computed from its core content only: prose at 200 words per minute, code by lines and tokens (output and shell at half weight), review questions at 15 seconds each, scaled by the lesson's difficulty. the validator rejects a lesson whose core reading exceeds 10.5 minutes, which is the signal to split it or move material into "going deeper". it is an estimate for comparing lessons, not a promise about any reader's pace.

### code checks

C++ blocks are tagged `complete`, `ub`, `fails`, `external`, `group=NAME`, or left as snippets. `check_code.py` compiles complete and UB examples, confirms that `fails` examples are rejected, compiles split programs as one unit, runs complete programs (with `--run`, and under AddressSanitizer and UBSan with `--sanitize`), and never runs UB examples. it writes reports to `.course_build/checks/`. examples that need `<format>` are reported as skipped on standard libraries that lack it.

## building, testing, and deploying

requires Node 22.12 or newer and Python 3.10 or newer.

| command | what it does |
| --- | --- |
| `npm install` | install dependencies |
| `npm run assemble` | regenerate the document and manifest from the lesson sources |
| `npm run build` | render the site into `dist/` |
| `npm test` | test `dist/`: links, anchors, accessibility basics, and (with Chrome or Edge installed, or `CHROME_PATH`) progress, migration, import/export, redirects, search, themes, phone layout |
| `npm run check` | validate, build, check the site's text, and test |
| `npm run preview` | build and serve locally with wrangler |
| `npm run deploy` | build and deploy to Cloudflare from your machine |

deploys go to the `modern-cpp-course` Worker, which serves `dist/` as static assets (directory index pages, automatic trailing slashes, `404.html` for unknown paths) and attaches `cpp.eigenomar.com`. with the repository connected in the Cloudflare dashboard (build command `npm run build`, deploy command `npx wrangler deploy`), every push to `main` goes live. the build only needs Node: the generated `site/course.json` is committed, so Cloudflare does not need Python.

GitHub Actions (`.github/workflows/ci.yml`) validates the sources and checks that the generated files are up to date, compiles and runs the examples with GCC 14 and Clang 18 under sanitizers, and builds and tests the website in headless Chrome.

## recovering an interrupted restructuring

the 1.0 to 2.0 restructuring kept a checkpoint in `.course_build/site_upgrade/` (`plan.md`, `state.json`, `handoff.md`). a new Claude Code session asked to "resume cpp site upgrade" reads those files (see `CLAUDE.md`) and continues from the recorded next step without relying on conversation history; recipes never overwrite a lesson that was edited after its recipe ran.
