# handoff: modern c++ daily course

read this first in a fresh session. it is short on purpose.

## state

the course is at curriculum 2.0: 119 days (102 lessons and 17 reviews) in 17 modules, generated from `.course_build/`. the original 56-day course (1.0) is archived unchanged in `archive/v1/` and in git history.

- `authoring.md`: lesson format, code tags, editorial rules, workflow.
- `curriculum.md`: the generated curriculum map.
- `site_upgrade/`: how the 1.0 to 2.0 restructuring was done (plan, recipes, state). read `site_upgrade/handoff.md` if asked to `resume cpp site upgrade`.

## how to change the course

1. edit `lessons/<id>.md`, `sections/*.md`, or `curriculum.json` (order, modules, v1 mapping).
2. `python .course_build/tools/course.py validate`, then `check_code.py --run` for any lesson whose code changed.
3. `python .course_build/tools/course.py assemble` regenerates `modern_cpp_daily_course.md`, `site/course.json`, and `curriculum.md`.
4. `npm run build && npm test` builds and tests the website; `python .course_build/tools/check_ui.py` checks its text.

never edit the generated files directly. adding a lesson: create the file, add its id to a module in `curriculum.json`, reassemble; day numbers and cross references renumber themselves. stable ids are also what browsers store as progress, so **never rename a lesson id** without adding a migration (see "progress" below).

## progress and migration

the website stores progress in `localStorage` under `modern-cpp-course:progress` as lesson ids. the 1.0 site stored `["#day-01", ...]` under `modern-cpp-course:done`; on first load the 2.0 site maps those through `curriculum.json` → `legacy.v1.complete_when` and leaves the old key in place. if a future change renames or removes ids, add an explicit mapping the same way and handle it in `site/app.js` (`load`, `parseImport`).

## toolchain notes

- local: MSYS2 g++ 12.1 on Windows (no `<format>`, no sanitizers) and g++ 11.4 in WSL Ubuntu (sanitizers; lacks `constexpr std::vector` and P2210 `split`). CI uses g++ 14 and clang++ 18 on ubuntu-24.04.
- `std::barrier` with several threads hangs on this MinGW toolchain (libstdc++ 12, non-futex wait); the barrier example is compile-checked only.
- the website needs Node 22.12 or newer; `npm test` drives a headless Chrome or Edge if one is installed (set `CHROME_PATH` otherwise).

## publishing

`npm run build` renders `site/course.json` into `dist/`; `wrangler.jsonc` serves it as a Cloudflare Worker with static assets on `cpp.eigenomar.com`. with the repository connected in the Cloudflare dashboard (build command `npm run build`, deploy command `npx wrangler deploy`), every push to `main` deploys. nothing is committed, pushed, or deployed without the owner's go-ahead.
