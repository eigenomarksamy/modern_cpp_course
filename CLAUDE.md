# modern c++ daily course

- course sources, tools, and workflow: read `.course_build/handoff.md`, then `.course_build/authoring.md`.
- if asked to **resume cpp site upgrade**: read `.course_build/site_upgrade/handoff.md` and `.course_build/site_upgrade/state.json`, and continue from `next_operation` there. do not rely on earlier conversation history.
- generated files (`modern_cpp_daily_course.md`, `site/course.json`, `.course_build/curriculum.md`, `dist/`) are never edited by hand; change the sources and run `python .course_build/tools/course.py assemble`, then `npm run build`.
- all course prose follows the lowercase editorial style in `.course_build/authoring.md`; `course.py validate` and `tools/check_ui.py` enforce it.
- do not commit, push, or deploy without the owner's explicit go-ahead.
