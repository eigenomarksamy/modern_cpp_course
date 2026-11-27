# modern c++ daily course: plan

the course is at curriculum 2.0: 119 days (102 lessons and 17 reviews) in 17 modules, live at [cpp.eigenomar.com](https://cpp.eigenomar.com) and in [`modern_cpp_daily_course.md`](../modern_cpp_daily_course.md). no new course work is planned. this plan holds the repository's open work as tickets. its ecosystem onboarding (EO1–EO7) was done on 2026-11-14. the open tickets are [S6](#s6), the ecosystem's tab icon, [DOC6](#doc6) and [SCM6](#scm6), which adopt the ecosystem's standards, and [MIG6](#mig6), which moves this plan's tickets into their GitHub issues.

the lessons themselves are not planned here: they are changed in `.course_build/` as [`authoring.md`](../.course_build/authoring.md) describes. the finished 1.0 to 2.0 restructuring and its decisions are recorded in [`.course_build/site_upgrade/plan.md`](../.course_build/site_upgrade/plan.md), which is a record, not a plan of open work.

## how this plan works

- **tickets.** every ticket has an id, a lane prefix and a number, which is never reused or renumbered. a split ticket keeps its number and adds a letter (EO4a, EO4b). each ticket has a stable anchor, its id in lowercase (`#eo4`), above its heading, which doesn't change when the heading does.
- **lanes.**

  | prefix | lane |
  | --- | --- |
  | EO | ecosystem onboarding |
  | S | the site at cpp.eigenomar.com: how its pages are built and served, not the lessons |
  | DOC | the course's documents: vision, architecture, design, testing strategy, and verification and validation |
  | SCM | source control and delivery: CI, branching, protection, releases and versioning |
  | MIG | the backlog moves into GitHub issues: the cutover to GitHub as its home |

- **each ticket** says what to do, what it needs, and when it is done. its "done when" is its acceptance criteria. its size is on the ecosystem's scale, the same value as its issue's `Size` in the ecosystem's GitHub Project: xxs takes minutes, xs under an hour, s an hour or two, m about a session, l two or three, xl four to six and xxl more. tbd means an open decision or work not yet planned decides it. a change to one is made to the other in the same session.
- **issues.** every open ticket gets one GitHub issue in this repository. the issue's title starts with the ticket's id, and its body links the ticket's anchor here without copying it. the ticket holds the scope and history, and the issue holds status, priority and blockers ([EO7](#eo7)).
- **adding work.** new work goes here as a ticket in a lane, with a new lane when none fits. this repository is public, so confidential work never goes in this file. the ecosystem's shared rules, which `CLAUDE.md` imports, say where it goes.
- **when work ships,** update the ticket's status in the index, add a result with the commit to the ticket, and add a line to the [log](#log).

## index

| ticket | title | size | needs | status |
| --- | --- | --- | --- | --- |
| [EO1](#eo1) | `project.yaml` | s | none | done |
| [EO2](#eo2) | `CLAUDE.md` with the shared rules | s | none | done |
| [EO3](#eo3) | the plan in this repository | s | none | done |
| [EO4](#eo4) | `.gitattributes` with LF line endings | s | none | done |
| [EO5](#eo5) | Python's name on Linux | s | none | done |
| [EO6](#eo6) | toolchain notes without WSL | s | none | done |
| [EO7](#eo7) | an issue for every open ticket | s | the owner's approval | done |
| [S6](#s6) | the ecosystem's tab icon | xs | none | done |
| [DOC6](#doc6) | the course's documents | tbd | `meta-eigenomar` ST1 | todo |
| [SCM6](#scm6) | the ecosystem's SCM strategy | tbd | `meta-eigenomar` ST2 | todo |
| [MIG6](#mig6) | the backlog moves into GitHub issues | xs | `meta-eigenomar` ST3 | todo |

## ecosystem onboarding

the course is one of the eigenomar ecosystem's repositories, which share a contract: a `project.yaml` manifest, shared Claude rules that `CLAUDE.md` imports, and one issue per open ticket on the ecosystem's GitHub Project.

**goal.** make the course discoverable and coordinated in the ecosystem without changing how it is built or delivered.

**stays as it is.**

- **build:** `python .course_build/tools/course.py assemble` regenerates the document, `site/course.json` and the curriculum map from the lesson sources, and `npm run build` renders the site into `dist/`.
- **tests:** `course.py validate`, `check_code.py`, `check_ui.py` and `npm test`, as the [README](../README.md#building-testing-and-deploying) lists them.
- **CI:** `.github/workflows/ci.yml` runs the sources, the C++ examples (GCC 14 and Clang 18 under sanitizers) and the site's tests on ubuntu-24.04 for every push to `main` and every pull request. it is what covers Linux.
- **branching:** work is committed straight to `main`.
- **releases:** none. the curriculum's version is in `.course_build/curriculum.json`.
- **deployment:** Cloudflare's build deploys every push to `main` as a Worker serving `dist/` at cpp.eigenomar.com. it serves only the generated site, so `project.yaml` and this plan are not part of it.
- **documents:** `README.md`, `CLAUDE.md`, `course_spec.md` and `.course_build/` (`handoff.md`, `authoring.md`, `site_upgrade/`), where they are.

**portability, checked on 2026-11-14.** `course.py validate`, `npm run build`, `check_ui.py` and `npm test` (68 checks, with headless Edge) pass when started from `c:\` and from `C:\`, and `check_code.py --run` compiles and runs examples from `c:\` with MinGW g++ 12.1. the tools use only Python's standard library and `pathlib`, there is no shell-only script, and all 339 tracked files are LF in the index. EO4–EO6 are the gaps.

### steps

each step is small and independent, and can be done between other work.

<a id="eo1"></a>

#### EO1 · `project.yaml` · done

- **done when:** a manifest at the root points at the documents that exist, and the ecosystem's validator passes it.
- **result:** done 2026-11-14. it points at this plan, the README, `.course_build/handoff.md`, `authoring.md` and the restructuring's decisions, records CI, no releases, and Cloudflare deploying every push to `main`, and its status is `maintenance`. update it in the same change that moves or adds a document it names. `0085c9c`.

<a id="eo2"></a>

#### EO2 · `CLAUDE.md` with the shared rules · done

- **done when:** the first line of `CLAUDE.md` imports the ecosystem's shared rules, and the rest is unchanged.
- **result:** done 2026-11-14. sessions here don't commit on their own, so it grants no standing approval for commits. `0085c9c`.

<a id="eo3"></a>

#### EO3 · the plan in this repository · done

- **done when:** this file exists with the onboarding steps, and [how this plan works](#how-this-plan-works) says that confidential work never goes in this file.
- **result:** done 2026-11-14. nothing in the repository was found to be confidential, so nothing moved. `0085c9c`.

<a id="eo4"></a>

#### EO4 · `.gitattributes` with LF line endings · done

- **do:** add `.gitattributes` with `* text=auto eol=lf`, then run `git add --renormalize .`. all 339 tracked files are already LF in the index, so this should stage nothing. if it stages anything, commit that on its own.
- **needs:** nothing.
- **done when:** `.gitattributes` is committed, and `git ls-files --eol` shows every text file as `i/lf`.
- **result:** done 2026-11-14. `.gitattributes` holds `* text=auto eol=lf`, and `git ls-files --eol` shows all 341 tracked files as `i/lf`, so `git add --renormalize .` has nothing to stage.

<a id="eo5"></a>

#### EO5 · Python's name on Linux · done

- **do:** `npm run assemble` and `npm run check` call `python`, which a stock Linux install may not have, since it provides only `python3`. CI isn't affected: it runs the tools directly. either say in the README's requirements that Linux needs `python` on the `PATH` (on Ubuntu, `python-is-python3`), or make the scripts find Python on both systems. see [open question 2](#open-questions).
- **needs:** nothing.
- **done when:** on a Linux machine that has only `python3`, following the README makes `npm run check` pass, and it still passes on Windows.
- **result:** done 2026-11-14, with a line in the README's requirements, as the owner chose: the two scripts call `python`, so on Linux it must be on the `PATH` under that name (on Ubuntu, `python-is-python3`). the scripts and CI are unchanged. `npm run check` passes on Windows from `c:\` and `C:\` (68 checks). no Linux machine without `python` was at hand, so the Linux half rests on the README line.

<a id="eo6"></a>

#### EO6 · toolchain notes without WSL · done

- **do:** the toolchain notes in `.course_build/handoff.md` name g++ 11.4 in WSL Ubuntu as the local compiler for sanitizer runs. the ecosystem keeps one local environment, on Windows, and CI covers Linux, so reword them: sanitizer and Linux runs come from CI (GCC 14 and Clang 18 on ubuntu-24.04), and `checks/code_report_linux_gcc11_asan.*` is the 2.0 upgrade's record.
- **needs:** nothing.
- **done when:** the toolchain notes name no WSL environment, and they say that sanitizer and Linux runs come from CI.
- **result:** done 2026-11-14. the notes give MSYS2 g++ 12.1 as the local compiler, and say that sanitizer and Linux runs come from CI (g++ 14 and clang++ 18 on ubuntu-24.04, under ASan and UBSan, with the `code-report` artifact), and that `checks/code_report_linux_gcc11_asan.*` is the 2.0 upgrade's record.

<a id="eo7"></a>

#### EO7 · an issue for every open ticket · done

- **do:** open one issue in this repository for every open ticket (EO4–EO6 on 2026-11-14) and add each to the ecosystem's GitHub Project. the title is `<id>: <title>`, as in `EO4: .gitattributes with LF line endings`. the body's first line links the ticket's anchor on `main` and copies nothing. none of them needs another, so there are no blocked-by links. the proposed priority is P2 for each ([open question 1](#open-questions)).
- **needs:** the owner's approval. this repository is public, so the owner sees each issue's text before it is written.
- **done when:** every open ticket has exactly one issue in the Project, with its status, priority and work type set.
- **result:** done 2026-11-14 with no issues: the owner chose to do EO4–EO6 at once, so no ticket is open. a ticket added later gets its issue when it is added.

### open questions

1. **priorities for EO7:** answered on 2026-11-14: none needed, since EO4–EO6 were done at once and have no issues.
2. **EO5:** answered on 2026-11-14: the README line.
3. **GitHub's description:** answered on 2026-11-14: `project.yaml`'s, with cpp.eigenomar.com as the homepage.

## the site

changes to how cpp.eigenomar.com's pages are built and served, which touch `scripts/build.mjs` and `site/` but no lesson.

<a id="s6"></a>

### S6 · the ecosystem's tab icon · xs

- **do:** every app under eigenomar.com shows the same tab icon: eigenomar.com's lambda with its two colors swapped, a light-blue tile and a near-black lambda (shared decision SD5). the site has none today. add it as `site/favicon.svg`, copy it to `dist/assets/favicon.svg` in `scripts/build.mjs` beside `style.css` and `app.js`, and link it in the page head the script writes, with `<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">`.
- **needs:** nothing.
- **done when:** every page of the built site links the icon, and the tab shows it on `npm run build`'s output and at cpp.eigenomar.com, in a light and a dark browser theme. `npm run check` passes, and CI passes on `main`.
- **result (2026-11-27):** `site/favicon.svg` is shared decision SD5's icon, byte for byte. `scripts/build.mjs` copies it to `dist/assets/favicon.svg` and links it in every page's head, and `scripts/test-site.mjs` checks that every page links it, beside the check for the button back to eigenomar.com. `npm run check` passes with 69 checks, one of them new, and the build writes 130 files. in headless Chrome, the dashboard, a lesson, the full course, the cheat sheet, the references and the 404 page each load the icon from `npm run build`'s output. the icon is a filled tile with no `prefers-color-scheme` rule, so it is the same in a light and a dark theme. committed in `8f0b471`, and CI passes on `main`. at cpp.eigenomar.com the same six kinds of page load the icon, whose bytes are the committed file's.

## ecosystem standards

the ecosystem's contract, in `meta-eigenomar`, is adding two standards that every repository adopts: the documents each one keeps, and how each one manages its source and delivers it. DOC6 and SCM6 adopt them here, each once its standard is designed. until then, their issues stay in the backlog. the course is in maintenance, so both gather what exists rather than add course work.

a third standard, `meta-eigenomar` ST3, makes GitHub's issues the home of every repository's backlog, and its decisions were made on 2026-11-27. MIG6 moves this plan's tickets there, once ST3 is built.

<a id="doc6"></a>

### DOC6 · the course's documents · tbd

- **do:** write or gather the course's product vision, architecture, design, testing strategy, and verification and validation (V&V) documents, in the shape the ecosystem's document standard sets. where a file or section already covers one, name it rather than copy it. today `course_spec.md` holds the original 1.0 specification, kept for its educational requirements, the README's layout and website sections and `.course_build/handoff.md` the architecture, `.course_build/authoring.md` how lessons are written, and `.course_build/site_upgrade/plan.md` the 1.0 to 2.0 decisions. the checks are `course.py validate`, `check_code.py`, `check_ui.py` and `npm test`, and CI runs the C++ examples under GCC 14 and Clang 18 with sanitizers.
- **needs:** the ecosystem's document standard (`meta-eigenomar` ST1).
- **done when:** each of the five documents exists, or names the file or section that holds it, and follows the standard's outline. `project.yaml` names them under the standard's keys, and the ecosystem's validator passes. nothing in them is confidential, since this repository is public.

<a id="scm6"></a>

### SCM6 · the ecosystem's SCM strategy · tbd

- **do:** adopt the ecosystem's SCM strategy through its adoption checklist: CI, branching, protection of `main`, versioning and releases, the health report and dependency updates. today `.github/workflows/ci.yml` runs on ubuntu-24.04 for every push to `main` and every pull request, work is committed straight to `main`, Cloudflare's build deploys every push, and there are no releases: the curriculum's version is in `.course_build/curriculum.json`.
- **needs:** the ecosystem's SCM strategy (`meta-eigenomar` ST2).
- **done when:** every item on the checklist is applied here, or recorded here as an exception the strategy allows, with its reason. `project.yaml`'s `delivery` and `CLAUDE.md` say what runs, CI passes on `main`, and the ecosystem's validator passes.

<a id="mig6"></a>

### MIG6 · the backlog moves into GitHub issues · tbd

- **do:** move this plan's planning to GitHub all at once, following the cutover steps of the ecosystem's standard `meta-eigenomar` ST3. each open ticket's content moves into its issue's body, keeping its id and its issue's `<id>: <title>`. ideas not yet tickets become draft items in the Project with status `idea`, hard needs are blocked-by links, and size, status and priority live only in the Project. done, dropped and moved tickets stay here as a frozen archive, and each open ticket's anchor stays, linking its issue.
- **needs:** GitHub as the home of the backlog (`meta-eigenomar` ST3), which includes the ecosystem's own cutover first and the backlog's backup. DOC6 is a planning need: the plan's direction moves into the vision before this plan retires.
- **done when:** every open ticket's content is in its issue, and this file holds only the archive and the anchors. `project.yaml`'s `documents.plan` is `null` and `planning.source` names GitHub, the ecosystem's validator passes, nothing confidential is in any issue, since this repository is public, and the owner approved the cutover. bringing tickets up to the ecosystem's ticket standard (`meta-eigenomar` ST4) isn't part of it: each ticket follows it when it is picked up.

## log

- 2026-11-27 · S6 · done: every page links the ecosystem's tab icon, the lambda on a light-blue tile (shared decision SD5), copied into `dist/assets/` by the build, and the site's tests check it. `npm run check` passes (69 checks).
- 2026-11-27 · plan · added MIG6, in a new lane, at the owner's request: this repository's cutover to GitHub as the home of its backlog, the ecosystem's standard `meta-eigenomar` ST3, whose decisions were made that day. it needs ST3, so its issue waits as `blocked`.
- 2026-11-26 · plan · renamed, since the ecosystem's lanes are numbered across its repositories: S6 from `S1`, DOC6 from `DOC1` and SCM6 from `SCM1`. their anchors, headings, index rows and issues changed with them, and the log keeps the ids it was written with.
- 2026-11-20 · plan · added S1, in a new lane for the site, at the owner's request: every app under eigenomar.com shares one tab icon, eigenomar.com's lambda with its colors swapped (shared decision SD5). the site has none, so S1 adds it.
- 2026-11-18 · plan · added DOC1 and SCM1, in two new lanes, at the owner's request: this repository's adoption of the ecosystem's document standard and SCM strategy, which are designed in `meta-eigenomar`. each needs its standard, so its issue waits in the backlog.
- 2026-11-14 · EO4–EO7 · done, as the owner chose: `.gitattributes` with LF line endings, which staged nothing; the README's requirements say Linux needs `python` on the `PATH`; the toolchain notes name no WSL environment and give CI as the sanitizer and Linux runs; and EO7 needs no issues, since nothing is open. `npm run check` passes from `c:\` and `C:\` (68 checks). EO1–EO3's results name `0085c9c`. the ecosystem onboarding is complete.
- 2026-11-14 · plan · created by the ecosystem onboarding run, with EO1–EO7. EO1–EO3 are done: `project.yaml`, which validates, `CLAUDE.md`'s import of the shared rules, and this plan. EO4–EO6 are the portability gaps the run found, and EO7 opens their issues. nothing else in the repository changed.
