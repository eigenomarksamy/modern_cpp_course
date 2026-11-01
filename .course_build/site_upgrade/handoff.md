# handoff: course and site upgrade (v1 -> v2)

Read this first when asked to `resume cpp site upgrade`. Then read `state.json` (same folder) for the exact stage list, and `plan.md` for the curriculum decisions. Do not rely on conversation history.

## what is being done

The 56-day v1 course (archived unchanged in `.course_build/archive/v1/`, and in git at commit `b4ff6d7`) is being restructured into a variable-length v2 course with stable lesson ids, a lowercase editorial style, 5 to 10 minute core lessons with optional "going deeper" material, and a multi-page website (dashboard, `/day/NN/` reader, `/full/` page).

## how the migration works

1. `site_upgrade/work/v1/` is the v1 lessons and sections with prose lowercased by `tools/editorial.py` (run `python site_upgrade/tools_normalize_v1.py` to regenerate it). Line numbers match `archive/v1/`.
2. Each `site_upgrade/recipes/v1-XX.txt` says how v1 lesson XX becomes one or more v2 lessons (line ranges plus new text). `python site_upgrade/apply_recipe.py recipes/v1-XX.txt` writes `lessons/<id>.md`. It never overwrites an existing lesson without `--force`, so hand edits made after a recipe ran are safe.
3. After a recipe runs, lessons are edited in place; from then on `lessons/<id>.md` is canonical.
4. `curriculum.json` holds module order and the explicit v1 -> v2 progress mapping.

## rules

- Never delete or edit `archive/v1/`.
- Never re-run a recipe with `--force` for a lesson that `state.json` lists as `edited`.
- Do not commit, push, or deploy without explicit authorization from the user.
- Mark a stage done in `state.json` only after its output validates.

## status

the upgrade is complete: 119 days (102 lessons, 17 reviews) in 17 modules, assembled and validated; the website builds and its 55 checks pass locally. see `state.json` for the validation record and the items that only CI or a deployment can verify. nothing has been committed, pushed, or deployed.

after the migration, the lesson files are canonical; the recipes are a record of how each v1 lesson was split and are not meant to be re-run (re-running with `--force` would discard every later edit, including the code-block tags).
