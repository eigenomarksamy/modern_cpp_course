# archive: curriculum 1.0

the original 56-day, 8-week course exactly as it was before the 2.0 restructuring (git commit `b4ff6d7`): lesson sources, sections, the v1 curriculum and handoff, compile-check notes, the assembled document, and the v1 build tool. nothing here is used by the current build. `site_upgrade/tools_normalize_v1.py` and the recipes in `site_upgrade/recipes/` read the lessons from here to show how each v1 day became its 2.0 lessons.

`tools/course.py` here is the v1 assembler; it resolves paths relative to this folder, so run it only on a copy if you want to rebuild the 1.0 document.
