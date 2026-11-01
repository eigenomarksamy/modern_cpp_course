#!/usr/bin/env python3
"""Build tool for the modern C++ daily course (curriculum v2).

The sources are the canonical content; everything else is generated from them:

  .course_build/curriculum.json      module order, lesson order, v1 progress mapping
  .course_build/lessons/<id>.md      one lesson each: frontmatter + body
  .course_build/sections/*.md        introduction, overview, cheat sheet, references

  modern_cpp_daily_course.md         the whole course as one Markdown document
  site/course.json                   the same content as a manifest for the website
  .course_build/curriculum.md        the curriculum map for authors (generated)

Lessons are identified by stable ids (the file name). Day numbers come from the
order in curriculum.json and may change when the curriculum changes; ids do not.
Cross references are written [[lesson-id]] or [[lesson-id|link text]] (or
[[module:module-id]]) and are resolved to the current day numbers at assembly.

Commands (run from anywhere):
  python course.py validate          check every source; exit 1 on problems
  python course.py check ID [ID...]  check some lessons (curriculum context included)
  python course.py stats             reading-time table for every lesson
  python course.py assemble          validate, then write the document and manifest
  python course.py status            one-screen summary
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import editorial  # noqa: E402
import readtime  # noqa: E402

BUILD = TOOLS.parent
ROOT = BUILD.parent
LESSONS = BUILD / "lessons"
SECTIONS = BUILD / "sections"
CURRICULUM = BUILD / "curriculum.json"
STATE = BUILD / "state.json"
FINAL = ROOT / "modern_cpp_daily_course.md"
MANIFEST = ROOT / "site" / "course.json"

LESSON_SECTIONS = ["the idea", "understanding the concept", "in code", "in practice",
                   "watch out for", "the takeaway", "optional challenge"]
REVIEW_SECTIONS = ["recap", "review questions", "mini exercise", "answers", "connections"]
DEEPER = "going deeper"
FRONT_SECTIONS = ["introduction.md", "overview.md"]
BACK_SECTIONS = ["cheat_sheet.md", "references.md"]
STANDARDS = {"C++17", "C++20"}
CODE_TAGS = {"complete", "snippet", "fails", "ub", "external", "norun", "c++17", "c++20"}
MAX_MINUTES, MIN_MINUTES = 10.5, 4.0
MAX_RUN_WITHOUT_REVIEW = 8

PLACEHOLDER = re.compile(
    r"\b(TODO|TBD|FIXME|XXX|lorem ipsum)\b|to be added|continue here|forthcoming|"
    r"lesson goes here|content goes here|\[insert|<<<", re.IGNORECASE)
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
REF = re.compile(r"\[\[(module:)?([a-z0-9][a-z0-9-]*)(?:\|([^\]]+))?\]\]")
MD_LINK = re.compile(r"\]\(#([^)\s]+)\)")
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
TEMPLATE = re.compile(r"\{\{(\w+)\}\}")


# ---------------------------------------------------------------- loading

class Lesson:
    def __init__(self, lid, path):
        self.id, self.path = lid, path
        self.raw = path.read_text(encoding="utf-8")
        self.meta, self.body, self.body_offset = parse_frontmatter(self.raw)
        self.kind = self.meta.get("kind", "lesson")
        self.title = self.meta.get("title", "")
        self.standard = self.meta.get("standard", "")
        self.objective = self.meta.get("objective", "")
        pre = self.meta.get("prerequisites", "none").strip()
        self.prerequisites = [] if pre in ("", "none") else [p.strip() for p in pre.split(",")]
        try:
            self.difficulty = int(self.meta.get("difficulty", "1"))
        except ValueError:
            self.difficulty = 0
        self.day = self.module = None
        self.estimate = readtime.estimate(self.body, self.kind, self.difficulty or 1)

    @property
    def minutes(self):
        return readtime.display_minutes(self.estimate["core_minutes"])

    def sections(self):
        return [h for h, _ in readtime.split_sections(self.body) if h is not None]

    def deeper_topics(self):
        topics, in_deeper = [], False
        for line in prose_lines(self.body):
            if line.startswith("### "):
                in_deeper = line[4:].strip() == DEEPER
            elif in_deeper and line.startswith("#### "):
                topics.append(line[5:].strip())
        return topics


def parse_frontmatter(text):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text, 0
    meta, end = {}, None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
        if ":" in lines[i]:
            k, v = lines[i].split(":", 1)
            meta[k.strip()] = v.strip()
    if end is None:
        return meta, "", 0
    start = end + 1
    while start < len(lines) and not lines[start].strip():
        start += 1                       # body_offset must point at the body's first line
    return meta, "\n".join(lines[start:]).strip("\n") + "\n", start


def prose_lines(text):
    in_code = False
    for line in text.split("\n"):
        if FENCE.match(line):
            in_code = not in_code
            continue
        if not in_code:
            yield line


def load():
    cur = json.loads(CURRICULUM.read_text(encoding="utf-8"))
    order, lessons = [], {}
    for mi, mod in enumerate(cur["modules"], 1):
        mod["n"] = mi
        for lid in mod["lessons"]:
            order.append(lid)
            path = LESSONS / f"{lid}.md"
            if path.exists():
                lesson = Lesson(lid, path)
                lesson.module = mod
                lessons[lid] = lesson
    for day, lid in enumerate(order, 1):
        if lid in lessons:
            lessons[lid].day = day
    return cur, order, lessons


def day_slug(day):
    return f"{day:02d}"


# ---------------------------------------------------------------- references

def resolve_refs(text, lessons, modules, problems=None, where="", style="markdown"):
    """Replace [[id]] references in prose; leave code and inline code alone."""
    out, in_code = [], False
    for n, line in enumerate(text.split("\n"), 1):
        if FENCE.match(line):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
            continue
        parts = re.split(r"(`[^`]*`)", line)
        for i in range(0, len(parts), 2):
            def sub(m):
                is_module, target, label = m.group(1), m.group(2), m.group(3)
                if is_module:
                    mod = modules.get(target)
                    if not mod:
                        if problems is not None:
                            problems.append(f"{where}:{n}: unknown module reference [[module:{target}]]")
                        return m.group(0)
                    return f"[{label or 'module ' + str(mod['n'])}](#module-{target})"
                lesson = lessons.get(target)
                if not lesson:
                    if problems is not None:
                        problems.append(f"{where}:{n}: unknown lesson reference [[{target}]]")
                    return m.group(0)
                slug = day_slug(lesson.day)
                return f"[{label or 'day ' + slug}](#day-{slug})"
            parts[i] = REF.sub(sub, parts[i])
        out.append("".join(parts))
    return "\n".join(out)


def fill_templates(text, values):
    return TEMPLATE.sub(lambda m: str(values.get(m.group(1), m.group(0))), text)


# ---------------------------------------------------------------- validation

def code_blocks(text):
    """Yield (line_number, language, tags, code_lines) for each fenced block."""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if m:
            info = m.group(2).strip().split()
            lang, tags, start, body = (info[0] if info else ""), info[1:], i + 1, []
            i += 1
            while i < len(lines) and not (FENCE.match(lines[i]) and not FENCE.match(lines[i]).group(2).strip()):
                body.append(lines[i])
                i += 1
            yield start, lang, tags, body
        i += 1


def check_text_common(text, where, problems, warnings, identifiers, offset=0):
    if text.count("<details>") != text.count("</details>"):
        problems.append(f"{where}: unbalanced <details> blocks")
    fences = sum(1 for line in text.split("\n") if FENCE.match(line))
    if fences % 2:
        problems.append(f"{where}: unbalanced code fence")
    for n, line in enumerate(text.split("\n"), 1):
        if PLACEHOLDER.search(line) and not FENCE.match(line):
            problems.append(f"{where}:{n + offset}: placeholder-like text: {line.strip()[:80]!r}")
    for n, msg in editorial.check_text(text, identifiers):
        problems.append(f"{where}:{n + offset}: {msg}")
    for n, lang, tags, _ in code_blocks(text):
        if not lang:
            problems.append(f"{where}:{n + offset}: code fence without a language tag")
        if lang == "cpp":
            for t in tags:
                if t not in CODE_TAGS and not t.startswith("group="):
                    problems.append(f"{where}:{n + offset}: unknown code block tag {t!r}")


def validate_lesson(lesson, ctx, problems, warnings):
    cur, order, lessons, identifiers = ctx
    where = f".course_build/lessons/{lesson.id}.md"
    m = lesson.meta
    for key in ("title", "standard", "objective", "prerequisites", "difficulty"):
        if key not in m:
            problems.append(f"{where}: frontmatter is missing '{key}'")
    if lesson.kind not in ("lesson", "review"):
        problems.append(f"{where}: kind must be 'lesson' or 'review'")
    if lesson.standard not in STANDARDS:
        problems.append(f"{where}: standard must be one of {sorted(STANDARDS)}")
    if lesson.difficulty not in (1, 2, 3):
        problems.append(f"{where}: difficulty must be 1, 2, or 3")
    if len(lesson.objective.split()) < 6:
        problems.append(f"{where}: objective is missing or too short to state a learning goal")
    for field in ("title", "objective"):
        for _, msg in editorial.check_text(m.get(field, ""), identifiers):
            problems.append(f"{where}: {field}: {msg}")
    for pre in lesson.prerequisites:
        if pre not in lessons:
            problems.append(f"{where}: prerequisite {pre!r} is not a lesson")
        elif lessons[pre].day >= lesson.day:
            problems.append(f"{where}: prerequisite {pre!r} (day {lessons[pre].day}) does not come before day {lesson.day}")

    expected = REVIEW_SECTIONS if lesson.kind == "review" else LESSON_SECTIONS
    found = lesson.sections()
    core = [s for s in found if s != DEEPER]
    if core != expected:
        problems.append(f"{where}: sections must be {expected} (plus an optional '{DEEPER}' last), found {found}")
    if DEEPER in found and found[-1] != DEEPER:
        problems.append(f"{where}: '{DEEPER}' must be the last section")
    pre_text = [t for h, t in readtime.split_sections(lesson.body) if h is None]
    if pre_text and pre_text[0].strip():
        problems.append(f"{where}: text before the first section heading")
    for heading, text in readtime.split_sections(lesson.body):
        if heading in expected and len(re.sub(r"<[^>]+>", " ", text).split()) < 12:
            problems.append(f"{where}: section '{heading}' is nearly empty")
        if heading == "in code" and not any(True for _ in code_blocks(text)):
            problems.append(f"{where}: 'in code' has no code block")
        if heading == "optional challenge" and "<details>" not in text:
            problems.append(f"{where}: the optional challenge needs a collapsed <details> answer")
        if heading == "answers" and text.count("<details>") < 3:
            problems.append(f"{where}: review answers should be collapsed in <details> blocks")
        if heading == DEEPER and "#### " not in text:
            problems.append(f"{where}: '{DEEPER}' needs at least one '#### topic' heading")
    if any(re.match(r"^#{1,2} ", line) for line in prose_lines(lesson.body)):
        problems.append(f"{where}: lessons use ### for sections and #### below; no # or ## headings")

    core_min = lesson.estimate["core_minutes"]
    if core_min > MAX_MINUTES:
        problems.append(f"{where}: core reading time {core_min} min exceeds {MAX_MINUTES}; split the lesson or move material to '{DEEPER}'")
    elif core_min < MIN_MINUTES:
        warnings.append(f"{where}: core reading time {core_min} min is below {MIN_MINUTES}")

    check_text_common(lesson.body, where, problems, warnings, identifiers, lesson.body_offset)
    refs = []
    resolve_refs(lesson.body, lessons, {md["id"]: md for md in cur["modules"]}, refs, where)
    for r in refs:
        n, msg = r.split(": ", 1)[0], r.split(": ", 1)[1]
        file, line = n.rsplit(":", 1)
        problems.append(f"{file}:{int(line) + lesson.body_offset}: {msg}")


def validate_structure(cur, order, lessons, problems, warnings):
    seen = set()
    for lid in order:
        if lid in seen:
            problems.append(f"curriculum.json: lesson {lid!r} appears more than once")
        seen.add(lid)
        if lid not in lessons:
            problems.append(f"curriculum.json: lesson {lid!r} has no source file lessons/{lid}.md")
    files = {p.stem for p in LESSONS.glob("*.md")}
    for extra in sorted(files - seen):
        problems.append(f".course_build/lessons/{extra}.md is not listed in curriculum.json")
    mids = [m["id"] for m in cur["modules"]]
    if len(mids) != len(set(mids)):
        problems.append("curriculum.json: duplicate module ids")
    run = 0
    for mod in cur["modules"]:
        ids = [l for l in mod["lessons"] if l in lessons]
        if not ids:
            problems.append(f"module {mod['id']}: no lessons")
            continue
        if lessons[ids[-1]].kind != "review":
            problems.append(f"module {mod['id']}: must end with a review lesson")
        for lid in ids[:-1]:
            if lessons[lid].kind == "review":
                problems.append(f"module {mod['id']}: review {lid!r} must be the module's last lesson")
        taught = [l for l in ids if lessons[l].kind == "lesson"]
        review = lessons[ids[-1]]
        if review.kind == "review":
            missing = [l for l in taught if l not in review.prerequisites]
            if missing:
                problems.append(f".course_build/lessons/{review.id}.md: review does not list module lessons {missing} as prerequisites")
        for lid in ids:
            run = 0 if lessons[lid].kind == "review" else run + 1
            if run > MAX_RUN_WITHOUT_REVIEW:
                problems.append(f"{lid}: more than {MAX_RUN_WITHOUT_REVIEW} lessons in a row without a review")
        for field in ("title", "blurb"):
            for _, msg in editorial.check_text(mod.get(field, ""), set()):
                problems.append(f"curriculum.json: module {mod['id']} {field}: {msg}")
    legacy = cur.get("legacy", {}).get("v1", {})
    covered = set()
    for lid, days in legacy.get("complete_when", {}).items():
        if lid not in lessons:
            problems.append(f"curriculum.json: legacy mapping names unknown lesson {lid!r}")
        for d in days:
            if not 1 <= int(d) <= 56:
                problems.append(f"curriculum.json: legacy mapping for {lid!r} names v1 day {d}")
            covered.add(int(d))
    for k, lid in legacy.get("redirect", {}).items():
        if lid not in lessons:
            problems.append(f"curriculum.json: legacy redirect for v1 day {k} names unknown lesson {lid!r}")
        covered.add(int(k))
    missing = sorted(set(range(1, 57)) - covered)
    if missing:
        problems.append(f"curriculum.json: v1 days without any v2 mapping or redirect: {missing}")


def all_identifiers(lessons):
    texts = [l.body for l in lessons.values()]
    texts += [(SECTIONS / s).read_text(encoding="utf-8") for s in FRONT_SECTIONS + BACK_SECTIONS if (SECTIONS / s).exists()]
    return editorial.code_identifiers(texts)


def validate(only=None):
    cur, order, lessons = load()
    problems, warnings = [], []
    validate_structure(cur, order, lessons, problems, warnings)
    identifiers = all_identifiers(lessons)
    ctx = (cur, order, lessons, identifiers)
    modules = {m["id"]: m for m in cur["modules"]}
    for lid in order:
        if lid in lessons and (only is None or lid in only):
            validate_lesson(lessons[lid], ctx, problems, warnings)
    if only is None:
        for s in FRONT_SECTIONS + BACK_SECTIONS:
            path = SECTIONS / s
            where = f".course_build/sections/{s}"
            if not path.exists():
                problems.append(f"{where}: missing")
                continue
            text = path.read_text(encoding="utf-8")
            check_text_common(text, where, problems, warnings, identifiers)
            refs = []
            resolve_refs(text, lessons, modules, refs, where)
            problems += refs
    return cur, order, lessons, problems, warnings


# ---------------------------------------------------------------- assembly

def legacy_redirects(cur, order):
    legacy = cur.get("legacy", {}).get("v1", {})
    redirect = {f"{int(k):02d}": v for k, v in legacy.get("redirect", {}).items()}
    for lid in order:
        for d in legacy.get("complete_when", {}).get(lid, []):
            redirect.setdefault(f"{int(d):02d}", lid)
    return dict(sorted(redirect.items()))


def demote(text, levels=1):
    out, in_code = [], False
    for line in text.split("\n"):
        if FENCE.match(line):
            in_code = not in_code
        elif not in_code and re.match(r"^#{1,5} ", line):
            line = "#" * levels + line
        out.append(line)
    return "\n".join(out)


def lesson_header(lesson, lessons, level="###"):
    slug = day_slug(lesson.day)
    mod = lesson.module
    meta = [f"**module {mod['n']}:** {mod['title']}",
            f"**reading time:** about {lesson.minutes} minutes",
            f"**standard:** {lesson.standard}"]
    lines = [f'<a id="day-{slug}"></a>', "", f"{level} day {slug}: {lesson.title}", "",
             " · ".join(meta) + "  ", f"**objective:** {lesson.objective}"]
    if lesson.prerequisites:
        if lesson.kind == "review":
            days = [lessons[p].day for p in lesson.prerequisites if p in lessons]
            lines[-1] += "  "
            lines.append(f"**covers:** [day {day_slug(min(days))}](#day-{day_slug(min(days))}) "
                         f"to [day {day_slug(max(days))}](#day-{day_slug(max(days))})")
        else:
            refs = ", ".join(f"[day {day_slug(lessons[p].day)}](#day-{day_slug(lessons[p].day)}) "
                             f"({lessons[p].title})" for p in lesson.prerequisites if p in lessons)
            lines[-1] += "  "
            lines.append(f"**builds on:** {refs}")
    return "\n".join(lines)


def lesson_body_for_document(lesson, lessons, modules):
    body = resolve_refs(lesson.body, lessons, modules)
    body = re.sub(r"^### going deeper$", "### going deeper (optional)", body, flags=re.M)
    return demote(body, 1)


def curriculum_map(cur, lessons):
    lines = ['<a id="curriculum"></a>', "", "## curriculum map", ""]
    for mod in cur["modules"]:
        lines += [f"**[module {mod['n']}: {mod['title']}](#module-{mod['id']})**: {mod['blurb']}", "",
                  "| day | lesson | standard | minutes | going deeper |", "| --- | --- | --- | --- | --- |"]
        for lid in mod["lessons"]:
            l = lessons[lid]
            slug = day_slug(l.day)
            deeper = "; ".join(l.deeper_topics()) or ""
            lines.append(f"| {slug} | [{l.title}](#day-{slug}) | {l.standard} | {l.minutes} | {deeper} |")
        lines.append("")
    return "\n".join(lines)


def checklist(cur, lessons):
    lines = ['<a id="progress-checklist"></a>', "", "## progress checklist", "",
             "tick a box as you finish each day (in an editor, or on a printed copy). the website tracks progress for you.", ""]
    for mod in cur["modules"]:
        lines += [f"**module {mod['n']}: {mod['title']}**", ""]
        for lid in mod["lessons"]:
            l = lessons[lid]
            lines.append(f"- [ ] [day {day_slug(l.day)}: {l.title}](#day-{day_slug(l.day)})")
        lines.append("")
    return "\n".join(lines)


def counts(cur, lessons):
    reviews = sum(1 for l in lessons.values() if l.kind == "review")
    return {"lesson_count": len(lessons), "module_count": len(cur["modules"]),
            "instructional_count": len(lessons) - reviews, "review_count": reviews,
            "version": cur["version"]}


def build(cur, order, lessons):
    modules = {m["id"]: m for m in cur["modules"]}
    values = counts(cur, lessons)

    def section(name):
        text = (SECTIONS / name).read_text(encoding="utf-8").rstrip() + "\n"
        return resolve_refs(fill_templates(text, values), lessons, modules)

    toc = ['<a id="table-of-contents"></a>', "", "## table of contents", "",
           "- [introduction and learning philosophy](#introduction)",
           "- [course overview](#course-overview)",
           "- [curriculum map](#curriculum)",
           "- [progress checklist](#progress-checklist)"]
    toc += [f"- [module {m['n']}: {m['title']}](#module-{m['id']})" for m in cur["modules"]]
    toc += ["- [modern C++17/20 cheat sheet](#cheat-sheet)", "- [references for deeper study](#references)", ""]

    body = []
    for mod in cur["modules"]:
        body += [f'<a id="module-{mod["id"]}"></a>', "", f"## module {mod['n']}: {mod['title']}", "",
                 mod["blurb"], ""]
        for lid in mod["lessons"]:
            l = lessons[lid]
            body += [lesson_header(l, lessons), "", lesson_body_for_document(l, lessons, modules).rstrip(), "",
                     "[back to the curriculum map](#curriculum)", "", "---", ""]

    doc = [f"# {cur['title']}", "",
           f"*version {cur['version']}: {values['lesson_count']} days of C++17 and C++20 in {values['module_count']} modules. "
           "generated from `.course_build/` by `course.py assemble`; edit the lesson and section sources there, then reassemble.*", "",
           section("introduction.md"), section("overview.md"), "\n".join(toc), curriculum_map(cur, lessons),
           checklist(cur, lessons), "\n".join(body), section("cheat_sheet.md"), section("references.md")]
    text = "\n".join(doc).rstrip() + "\n"
    text = re.sub(r"\n{3,}", "\n\n", text)

    manifest = {
        "version": cur["version"],
        "title": cur["title"],
        "tagline": cur.get("tagline", ""),
        "counts": values,
        "modules": [{"id": m["id"], "n": m["n"], "title": m["title"], "blurb": m["blurb"],
                     "lessons": m["lessons"]} for m in cur["modules"]],
        "lessons": [],
        "sections": {
            "introduction": section("introduction.md"),
            "overview": section("overview.md"),
            "curriculum": curriculum_map(cur, lessons),
            "cheat_sheet": section("cheat_sheet.md"),
            "references": section("references.md"),
        },
        "legacy": {"v1": {"complete_when": cur["legacy"]["v1"]["complete_when"],
                          "redirect": legacy_redirects(cur, order)}},
    }
    used_by = {lid: [] for lid in order}
    for lid in order:
        for p in lessons[lid].prerequisites:
            if p in used_by and lessons[lid].kind == "lesson":
                used_by[p].append(lid)
    for lid in order:
        l = lessons[lid]
        manifest["lessons"].append({
            "id": l.id, "day": l.day, "slug": day_slug(l.day), "kind": l.kind,
            "module": l.module["id"], "module_n": l.module["n"],
            "title": l.title, "standard": l.standard, "objective": l.objective,
            "difficulty": l.difficulty, "minutes": l.minutes,
            "core_minutes": l.estimate["core_minutes"], "deeper_minutes": l.estimate["deeper_minutes"],
            "deeper_topics": l.deeper_topics(),
            "prerequisites": l.prerequisites, "used_by": used_by[lid],
            "v1": cur["legacy"]["v1"]["complete_when"].get(lid, []),
            "body": resolve_refs(l.body, lessons, modules),
        })
    return text, manifest


def validate_document(text):
    problems = []
    anchors = ANCHOR.findall(text)
    dupes = sorted({a for a in anchors if anchors.count(a) > 1})
    if dupes:
        problems.append(f"duplicate anchors: {dupes}")
    known = set(anchors)
    for target in sorted(set(MD_LINK.findall(text))):
        if target not in known:
            problems.append(f"broken internal link #{target}")
    prose = re.sub(r"`[^`]*`", "", "\n".join(prose_lines(text)))
    leftover = sorted(set(m.group(0) for m in REF.finditer(prose)))
    if leftover:
        problems.append(f"unresolved cross references: {leftover[:5]}")
    if TEMPLATE.search(text):
        problems.append("unfilled {{template}} variables")
    if editorial.EM_DASH in text:
        problems.append("the document contains em dashes")
    return problems


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    for attempt in range(20):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:  # Windows: another process has the file open
            time.sleep(0.1 * (attempt + 1))
    os.replace(tmp, path)


def assemble():
    cur, order, lessons, problems, warnings = validate()
    for w in warnings:
        print("warning:", w)
    if problems:
        for p in problems:
            print("problem:", p)
        print(f"not assembled: {len(problems)} problem(s); the published files were not touched")
        return 1
    text, manifest = build(cur, order, lessons)
    doc_problems = validate_document(text)
    if doc_problems:
        for p in doc_problems:
            print("problem:", p)
        print("assembled document failed validation; the published files were not touched")
        return 1
    atomic_write(FINAL, text)
    atomic_write(MANIFEST, json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
    atomic_write(BUILD / "curriculum.md", curriculum_document(cur, order, lessons))
    write_state(cur, lessons, "assembled_and_validated")
    c = counts(cur, lessons)
    print(f"published {FINAL.name} ({len(text.split())} words) and {MANIFEST.relative_to(ROOT)}: "
          f"{c['lesson_count']} days ({c['instructional_count']} lessons, {c['review_count']} reviews) in {c['module_count']} modules")
    return 0


def curriculum_document(cur, order, lessons):
    """The curriculum map for authors: everything about each day in one place."""
    c = counts(cur, lessons)
    out = [f"# curriculum map (version {cur['version']})", "",
           "generated by `course.py assemble` from `curriculum.json` and the lesson frontmatter; do not edit by hand. "
           "to change the curriculum, edit those sources and reassemble.", "",
           f"{c['lesson_count']} days in {c['module_count']} modules: {c['instructional_count']} lessons and "
           f"{c['review_count']} reviews. minutes are the estimated core reading time (see `tools/readtime.py`); "
           "\"v1\" lists the days of the original 56-day course a lesson was derived from (empty: new material).", ""]
    for mod in cur["modules"]:
        out += [f"## module {mod['n']}: {mod['title']} (`{mod['id']}`)", "", mod["blurb"], "",
                "| day | id | lesson and objective | builds on | std | min | going deeper | v1 |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for lid in mod["lessons"]:
            l = lessons[lid]
            pre = ", ".join(day_slug(lessons[p].day) for p in l.prerequisites if p in lessons) or "none"
            v1 = ", ".join(str(d) for d in cur["legacy"]["v1"]["complete_when"].get(lid, [])) or "new"
            out.append(f"| {day_slug(l.day)} | `{lid}` | **{l.title}**: {l.objective} | {pre} | {l.standard} | "
                       f"{l.estimate['core_minutes']} | {'; '.join(l.deeper_topics())} | {v1} |")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def write_state(cur, lessons, action):
    minutes = [l.estimate["core_minutes"] for l in lessons.values()]
    state = {
        "project": "modern_cpp_daily_course",
        "curriculum_version": cur["version"],
        "counts": counts(cur, lessons),
        "reading_time_core_minutes": {"min": min(minutes), "max": max(minutes),
                                      "mean": round(sum(minutes) / len(minutes), 1)},
        "last_successful_action": action,
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    atomic_write(STATE, json.dumps(state, indent=2) + "\n")


def stats():
    cur, order, lessons = load()
    print(f"{'day':>4} {'id':32} {'kind':6} {'std':6} {'core':>5} {'deep':>5} {'prose':>5} {'code s':>6}")
    for lid in order:
        l = lessons.get(lid)
        if not l:
            continue
        e = l.estimate
        print(f"{l.day:>4} {lid:32} {l.kind:6} {l.standard:6} {e['core_minutes']:5.1f} "
              f"{e['deeper_minutes']:5.1f} {e['prose_words']:5d} {e['code_seconds']:6d}")
    mins = [l.estimate["core_minutes"] for l in lessons.values()]
    print(f"\n{len(lessons)} days; core minutes min {min(mins)}, max {max(mins)}, "
          f"mean {sum(mins) / len(mins):.1f}, total {sum(mins):.0f}")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd in ("validate", "check"):
        only = set(argv[2:]) if cmd == "check" and len(argv) > 2 else None
        _, _, lessons, problems, warnings = validate(only)
        for w in warnings:
            print("warning:", w)
        for p in problems:
            print("problem:", p)
        print("ok" if not problems else f"FAILED: {len(problems)} problem(s)")
        return 1 if problems else 0
    if cmd == "assemble":
        return assemble()
    if cmd == "stats":
        stats()
        return 0
    if cmd == "status":
        cur, order, lessons, problems, warnings = validate()
        c = counts(cur, lessons)
        print(f"curriculum {cur['version']}: {c['lesson_count']} days in {c['module_count']} modules; "
              f"{len(problems)} problem(s), {len(warnings)} warning(s)")
        fresh = FINAL.exists() and MANIFEST.exists()
        print("published files present" if fresh else "published files missing: run assemble")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
