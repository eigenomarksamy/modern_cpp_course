# modern c++ daily course: plan

the course is at curriculum 2.0: 119 days (102 lessons and 17 reviews) in 17 modules, live at [cpp.eigenomar.com](https://cpp.eigenomar.com) and in [`modern_cpp_daily_course.md`](../modern_cpp_daily_course.md). no new course work is planned. this plan holds the repository's open work as tickets. its ecosystem onboarding (EO1–EO7) was done on 2026-11-14, so nothing is open.

the lessons themselves are not planned here: they are changed in `.course_build/` as [`authoring.md`](../.course_build/authoring.md) describes. the finished 1.0 to 2.0 restructuring and its decisions are recorded in [`.course_build/site_upgrade/plan.md`](../.course_build/site_upgrade/plan.md), which is a record, not a plan of open work.

## how this plan works

- **tickets.** every ticket has an id, a lane prefix and a number, which is never reused or renumbered. a split ticket keeps its number and adds a letter (EO4a, EO4b). each ticket has a stable anchor, its id in lowercase (`#eo4`), above its heading, which doesn't change when the heading does.
- **lanes.**

  | prefix | lane |
  | --- | --- |
  | EO | ecosystem onboarding |

- **each ticket** says what to do, what it needs, and when it is done. its "done when" is its acceptance criteria. size is a rough guess: S is small, M is medium.
- **issues.** every open ticket gets one GitHub issue in this repository. the issue's title starts with the ticket's id, and its body links the ticket's anchor here without copying it. the ticket holds the scope and history, and the issue holds status, priority and blockers ([EO7](#eo7)).
- **adding work.** new work goes here as a ticket in a lane, with a new lane when none fits. this repository is public, so confidential work never goes in this file. the ecosystem's shared rules, which `CLAUDE.md` imports, say where it goes.
- **when work ships,** update the ticket's status in the index, add a result with the commit to the ticket, and add a line to the [log](#log).

## index

| ticket | title | size | needs | status |
| --- | --- | --- | --- | --- |
| [EO1](#eo1) | `project.yaml` | S | none | done |
| [EO2](#eo2) | `CLAUDE.md` with the shared rules | S | none | done |
| [EO3](#eo3) | the plan in this repository | S | none | done |
| [EO4](#eo4) | `.gitattributes` with LF line endings | S | none | done |
| [EO5](#eo5) | Python's name on Linux | S | none | done |
| [EO6](#eo6) | toolchain notes without WSL | S | none | done |
| [EO7](#eo7) | an issue for every open ticket | S | the owner's approval | done |

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

## log

- 2026-11-14 · EO4–EO7 · done, as the owner chose: `.gitattributes` with LF line endings, which staged nothing; the README's requirements say Linux needs `python` on the `PATH`; the toolchain notes name no WSL environment and give CI as the sanitizer and Linux runs; and EO7 needs no issues, since nothing is open. `npm run check` passes from `c:\` and `C:\` (68 checks). EO1–EO3's results name `0085c9c`. the ecosystem onboarding is complete.
- 2026-11-14 · plan · created by the ecosystem onboarding run, with EO1–EO7. EO1–EO3 are done: `project.yaml`, which validates, `CLAUDE.md`'s import of the shared rules, and this plan. EO4–EO6 are the portability gaps the run found, and EO7 opens their issues. nothing else in the repository changed.
