#!/usr/bin/env python3
"""Build tool for the modern C++ daily course.

The filesystem is the source of truth; state.json and the auto section of
handoff.md are always recomputed from it, so every command is idempotent and
safe to run from any session.

Commands (run from anywhere):
  python course.py check <lesson-file>   validate one lesson file (may be a .tmp)
  python course.py commit <tmp-file>     validate, atomically rename to day-XX.md, reconcile
  python course.py reconcile             rescan lessons, rewrite state.json and handoff.md
  python course.py status                print a one-screen summary
  python course.py assemble              build, validate, and publish modern_cpp_daily_course.md
  python course.py validate              validate the published final document
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

BUILD = Path(__file__).resolve().parent.parent
ROOT = BUILD.parent
LESSONS = BUILD / "lessons"
SECTIONS = BUILD / "sections"
CHECKS = BUILD / "checks"
STATE = BUILD / "state.json"
HANDOFF = BUILD / "handoff.md"
CURRICULUM = BUILD / "curriculum.md"
FINAL = ROOT / "modern_cpp_daily_course.md"

TOTAL_DAYS = 56
REVIEW_DAYS = {7, 14, 21, 28, 35, 42, 49, 56}
LESSON_SECTIONS = ["the idea", "understanding the concept", "in code", "in practice",
                   "watch out for", "the takeaway", "optional challenge"]
REVIEW_SECTIONS = ["recap", "review questions", "mini exercise", "answers", "connections"]
FRONT_SECTIONS = ["introduction.md", "overview.md"]
BACK_SECTIONS = ["cheat_sheet.md", "references.md"]
MIN_WORDS, MAX_WORDS = 650, 2100

PLACEHOLDER = re.compile(
    r"\b(TODO|TBD|FIXME|lorem ipsum)\b|to be added|continue here|forthcoming|"
    r"lesson goes here|content goes here|\[insert", re.IGNORECASE)
META = re.compile(r"^\*\*reading time:\*\* about (\d+) minutes · \*\*standard:\*\* C\+\+(17|20)"
                  r" · \*\*builds on:\*\* (.+)$")
FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^(#{1,6}) (.*)$")
LINK = re.compile(r"\]\(#([^)\s]+)\)")
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')


def day_id(n):
    return f"{n:02d}"


def lesson_path(n):
    return LESSONS / f"day-{day_id(n)}.md"


def atomic_write(path, text):
    path = Path(path)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    for attempt in range(20):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            # Windows refuses to replace a file another process has open; retry briefly.
            time.sleep(0.1 * (attempt + 1))
    os.replace(tmp, path)


def split_code(lines):
    """Yield (line, in_code, fence_info) and report unbalanced fences."""
    out, fence, info = [], None, None
    for line in lines:
        m = FENCE.match(line)
        if fence is None and m:
            fence, info = m.group(2), m.group(3).strip()
            out.append((line, True, ("open", info)))
        elif fence is not None and m and m.group(2).startswith(fence[0]) \
                and len(m.group(2)) >= len(fence) and not m.group(3).strip():
            fence = None
            out.append((line, True, ("close", None)))
        else:
            out.append((line, fence is not None, None))
    return out, fence is not None


def heading_case_problems(text):
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"C\+\+\d*", "", text)
    bad = []
    for word in re.findall(r"[A-Za-z][A-Za-z0-9_'-]*", text):
        if word != word.lower() and not re.fullmatch(r"[A-Z0-9_]{2,}s?", word):
            bad.append(word)
    return bad


def common_text_checks(lines, problems, warnings):
    tagged, unbalanced = split_code(lines)
    if unbalanced:
        problems.append("unbalanced code fence")
    for line, in_code, fence in tagged:
        if fence and fence[0] == "open" and not fence[1]:
            problems.append(f"code fence without a language tag: {line.strip()!r}")
        if not in_code:
            h = HEADING.match(line)
            if h:
                bad = heading_case_problems(h.group(2))
                if bad:
                    problems.append(f"heading not lowercase ({', '.join(bad)}): {line.strip()}")
    text = "\n".join(lines)
    if "—" in text:
        problems.append(f"contains {text.count(chr(0x2014))} em dash(es)")
    if "–" in text:
        warnings.append(f"contains {text.count(chr(0x2013))} en dash(es)")
    m = PLACEHOLDER.search(text)
    if m:
        problems.append(f"placeholder-like text: {m.group(0)!r}")
    return tagged


def check_lesson(path):
    """Return (problems, warnings, info) for one lesson file."""
    path = Path(path)
    problems, warnings, info = [], [], {}
    m = re.match(r"day-(\d{2})\.md(\.tmp)?$", path.name)
    if not m:
        return [f"file name must be day-XX.md or day-XX.md.tmp, got {path.name}"], warnings, info
    n = int(m.group(1))
    if not 1 <= n <= TOTAL_DAYS:
        return [f"day {n} out of range"], warnings, info
    if not path.exists():
        return ["file does not exist"], warnings, info
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    is_review = n in REVIEW_DAYS
    info["review"] = is_review

    nonblank = [l for l in lines if l.strip()]
    if not nonblank or nonblank[0].strip() != f'<a id="day-{day_id(n)}"></a>':
        problems.append(f'first line must be <a id="day-{day_id(n)}"></a>')

    tagged = common_text_checks(lines, problems, warnings)
    prose = [l for l, code, _ in tagged if not code]
    h2 = [l for l in prose if l.startswith("## ")]
    h1 = [l for l in prose if l.startswith("# ")]
    if h1:
        problems.append("lesson files must not use a level-1 heading")
    if len(h2) != 1:
        problems.append(f"expected exactly one '## day {day_id(n)}: ...' heading, found {len(h2)}")
    elif not h2[0].startswith(f"## day {day_id(n)}: ") or len(h2[0]) < 14:
        problems.append(f"day heading must start with '## day {day_id(n)}: ' and have a title")
    else:
        info["title"] = h2[0][len(f"## day {day_id(n)}: "):].strip()

    metas = [META.match(l) for l in prose]
    metas = [mm for mm in metas if mm]
    if len(metas) != 1:
        problems.append("missing or duplicated meta line "
                        "('**reading time:** about N minutes · **standard:** C++17 · **builds on:** ...')")
    else:
        minutes = int(metas[0].group(1))
        info["minutes"], info["standard"] = minutes, "C++" + metas[0].group(2)
        if not 5 <= minutes <= 10:
            problems.append(f"reading time {minutes} is outside 5 to 10 minutes")

    expected = REVIEW_SECTIONS if is_review else LESSON_SECTIONS
    h3 = [l[4:].strip() for l in prose if l.startswith("### ")]
    if h3 != expected:
        problems.append(f"section headings must be exactly {expected}, found {h3}")

    # Section bodies must not be empty.
    current, bodies = None, {}
    for l, code, _ in tagged:
        if not code and l.startswith("### "):
            current = l[4:].strip()
            bodies[current] = 0
        elif current is not None and l.strip():
            bodies[current] += len(l.split())
    for name in expected:
        if name in bodies and bodies[name] < 15:
            problems.append(f"section '{name}' is nearly empty ({bodies[name]} words)")

    cpp_blocks = sum(1 for _, _, f in tagged if f and f[0] == "open" and f[1].startswith("cpp"))
    info["cpp_blocks"] = cpp_blocks
    if not is_review and cpp_blocks < 2:
        problems.append(f"instructional lessons need at least 2 cpp code blocks, found {cpp_blocks}")

    details = text.count("<details>")
    if details != text.count("</details>"):
        problems.append("unbalanced <details> blocks")
    if is_review:
        if details < 4:
            problems.append(f"review answers should be collapsed (<details>), found {details}")
    elif details < 1:
        problems.append("optional challenge needs a collapsed <details> answer")

    words = len(text.split())
    info["words"] = words
    if not MIN_WORDS <= words <= MAX_WORDS:
        problems.append(f"{words} words, outside {MIN_WORDS} to {MAX_WORDS}")
    elif words > 1900:
        warnings.append(f"{words} words is on the long side")

    for target in LINK.findall(text):
        if not re.fullmatch(r"day-(\d{2})|week-[1-8]|cheat-sheet|references", target):
            problems.append(f"link to unknown anchor #{target}")
        elif target.startswith("day-") and not 1 <= int(target[4:]) <= TOTAL_DAYS:
            problems.append(f"link to nonexistent day #{target}")
    return problems, warnings, info


def parse_weeks():
    """Read week numbers, titles, and blurbs from the curriculum."""
    weeks, current = [], None
    for line in CURRICULUM.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## week (\d): (.+)$", line)
        if m:
            current = {"n": int(m.group(1)), "title": m.group(2).strip(), "blurb": ""}
            weeks.append(current)
        elif current is not None and not current["blurb"] and line.strip() and not line.startswith("#"):
            current["blurb"] = line.strip()
    return weeks


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def reconcile(action=None, quiet=False):
    old = load_state()
    old_lessons = old.get("lessons", {})
    lessons, completed, notes = {}, 0, []
    for n in range(1, TOTAL_DAYS + 1):
        key, path = day_id(n), lesson_path(n)
        rel = f".course_build/lessons/day-{key}.md"
        entry = {"status": "pending", "path": rel,
                 "kind": "review" if n in REVIEW_DAYS else "lesson"}
        if path.exists():
            problems, _, info = check_lesson(path)
            if problems:
                entry["status"] = "needs_repair"
                entry["problems"] = problems
            else:
                entry["status"] = "complete"
                completed += 1
                entry.update({k: info[k] for k in ("title", "words", "minutes", "standard") if k in info})
            entry["compile_check_note"] = (CHECKS / f"day-{key}.md").exists()
        elif (LESSONS / f"day-{key}.md.tmp").exists():
            entry["status"] = "in_progress"
        elif old_lessons.get(key, {}).get("status") == "complete":
            entry["status"] = "needs_repair"
            entry["problems"] = ["manifest said complete but the file is missing"]
        lessons[key] = entry

    incomplete = [k for k, e in lessons.items() if e["status"] != "complete"]
    sections_ok = all((SECTIONS / s).exists() for s in FRONT_SECTIONS + BACK_SECTIONS)
    assembly = old.get("assembly", "pending")
    validation = old.get("validation", "pending")
    final_ok = False
    if FINAL.exists():
        final_ok = not validate_final(FINAL.read_text(encoding="utf-8"))[0]
    if incomplete or not final_ok:
        if incomplete:
            assembly = validation = "pending"
        elif not FINAL.exists():
            assembly, validation = "pending", "pending"
        else:
            validation = "failed"

    if incomplete:
        phase = "generation"
        repair = [k for k in incomplete if lessons[k]["status"] == "needs_repair"]
        nxt = (repair or incomplete)[0]
        next_action = f"{'repair' if repair else 'write'} lesson day-{nxt}"
    elif not sections_ok:
        phase, nxt = "assembly", None
        missing = [s for s in FRONT_SECTIONS + BACK_SECTIONS if not (SECTIONS / s).exists()]
        next_action = "write supplementary sections: " + ", ".join(missing)
    elif not final_ok or validation != "complete":
        phase, nxt = ("validation" if FINAL.exists() else "assembly"), None
        next_action = "run: python .course_build/tools/course.py assemble"
    else:
        phase, nxt, next_action = "complete", None, "none: course is complete"

    state = {
        "project": "modern_cpp_daily_course",
        "spec_version": "1.0",
        "phase": phase,
        "total_days": TOTAL_DAYS,
        "completed_days": completed,
        "next_day": int(nxt) if nxt else None,
        "next_action": next_action,
        "lessons": lessons,
        "supplementary_sections": {s: (SECTIONS / s).exists() for s in FRONT_SECTIONS + BACK_SECTIONS},
        "assembly": assembly,
        "validation": validation,
        "last_successful_action": action or old.get("last_successful_action", "reconciled"),
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    atomic_write(STATE, json.dumps(state, indent=2) + "\n")
    write_handoff(state)
    if not quiet:
        print_status(state)
    return state


AUTO_START, AUTO_END = "<!-- auto:start -->", "<!-- auto:end -->"


def write_handoff(state):
    done = [k for k, e in state["lessons"].items() if e["status"] == "complete"]
    by_status = {}
    for k, e in state["lessons"].items():
        if e["status"] != "complete":
            by_status.setdefault(e["status"], []).append(k)
    other = {s: compress(keys) for s, keys in by_status.items()}
    auto = [
        AUTO_START,
        "## current position (generated by `course.py reconcile`, do not edit by hand)",
        "",
        f"- phase: **{state['phase']}**",
        f"- lessons complete: {state['completed_days']} / {TOTAL_DAYS}"
        + (f" (days {compress(done)})" if done else ""),
        f"- not complete: {'; '.join(f'{s}: {days}' for s, days in other.items()) if other else 'none'}",
        f"- supplementary sections: "
        + ", ".join(f"{k} {'ok' if v else 'missing'}" for k, v in state["supplementary_sections"].items()),
        f"- assembly: {state['assembly']}, validation: {state['validation']}",
        f"- **next action: {state['next_action']}**",
        f"- last successful action: {state['last_successful_action']} ({state['updated']})",
        AUTO_END,
    ]
    block = "\n".join(auto)
    if HANDOFF.exists():
        text = HANDOFF.read_text(encoding="utf-8")
        if AUTO_START in text and AUTO_END in text:
            pre, rest = text.split(AUTO_START, 1)
            post = rest.split(AUTO_END, 1)[1]
            text = pre + block + post
        else:
            text = text.rstrip() + "\n\n" + block + "\n"
    else:
        text = "# handoff\n\n" + block + "\n"
    atomic_write(HANDOFF, text)


def compress(keys):
    nums = sorted(int(k) for k in keys)
    ranges, start = [], None
    for i, n in enumerate(nums):
        if start is None:
            start = n
        if i == len(nums) - 1 or nums[i + 1] != n + 1:
            ranges.append(f"{start:02d}" if start == n else f"{start:02d}-{n:02d}")
            start = None
    return ", ".join(ranges)


def print_status(state):
    counts = {}
    for e in state["lessons"].values():
        counts[e["status"]] = counts.get(e["status"], 0) + 1
    print(f"phase: {state['phase']} | complete {state['completed_days']}/{TOTAL_DAYS} | "
          + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    for k, e in state["lessons"].items():
        if e.get("problems"):
            print(f"  day-{k} {e['status']}: " + "; ".join(e["problems"]))
    print(f"next action: {state['next_action']}")


def demote(lines):
    out, tagged = [], split_code(lines)[0]
    for line, code, _ in tagged:
        out.append("#" + line if not code and HEADING.match(line) else line)
    return out


def assemble():
    state = reconcile(quiet=True)
    incomplete = [k for k, e in state["lessons"].items() if e["status"] != "complete"]
    if incomplete:
        sys.exit(f"cannot assemble: lessons not complete: {', '.join(incomplete)}")
    missing = [s for s in FRONT_SECTIONS + BACK_SECTIONS if not (SECTIONS / s).exists()]
    if missing:
        sys.exit(f"cannot assemble: missing sections: {', '.join(missing)}")

    weeks = parse_weeks()
    titles = {int(k): e["title"] for k, e in state["lessons"].items()}
    read = lambda name: (SECTIONS / name).read_text(encoding="utf-8").rstrip() + "\n"

    toc = ['<a id="table-of-contents"></a>', "", "## table of contents", "",
           "- [introduction and learning philosophy](#introduction)",
           "- [course overview](#course-overview)",
           "- [progress checklist](#progress-checklist)"]
    checklist = ['<a id="progress-checklist"></a>', "", "## progress checklist", "",
                 "Tick a box as you finish each day (in an editor, or on a printed copy).", ""]
    body = []
    for w in weeks:
        first = (w["n"] - 1) * 7 + 1
        toc.append(f"- [week {w['n']}: {w['title']}](#week-{w['n']})")
        checklist.append(f"**week {w['n']}: {w['title']}**")
        checklist.append("")
        body += [f'<a id="week-{w["n"]}"></a>', "", f"## week {w['n']}: {w['title']}", "", w["blurb"], ""]
        for n in range(first, first + 7):
            label = f"day {day_id(n)}: {titles[n]}"
            toc.append(f"  - [{label}](#day-{day_id(n)})")
            checklist.append(f"- [ ] [{label}](#day-{day_id(n)})")
            lesson = lesson_path(n).read_text(encoding="utf-8").rstrip().splitlines()
            body += demote(lesson) + ["", f"[back to table of contents](#table-of-contents)", "", "---", ""]
        checklist.append("")
    toc += ["- [modern C++17/20 cheat sheet](#cheat-sheet)", "- [references for deeper study](#references)", ""]

    doc = ["# modern c++ daily course: 56 days of C++17 and C++20", "",
           "*version 1.0. Generated from `.course_build/` by `course.py assemble`; "
           "edit the lesson and section sources there, then reassemble.*", "",
           read("introduction.md"), read("overview.md"), "\n".join(toc), "\n".join(checklist),
           "\n".join(body), read("cheat_sheet.md"), read("references.md")]
    text = "\n".join(doc).rstrip() + "\n"

    problems, warnings = validate_final(text)
    tmp = FINAL.with_name(FINAL.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    if problems:
        print("assembled document failed validation; the published file was not touched:")
        for p in problems:
            print("  -", p)
        print(f"draft left at {tmp}")
        old = load_state()
        old["assembly"], old["validation"] = "complete", "failed"
        atomic_write(STATE, json.dumps(old, indent=2) + "\n")
        sys.exit(1)
    os.replace(tmp, FINAL)
    old = load_state()
    old["assembly"] = old["validation"] = "complete"
    atomic_write(STATE, json.dumps(old, indent=2) + "\n")
    state = reconcile(action="assembled_and_validated", quiet=True)
    for w in warnings:
        print("warning:", w)
    words = len(text.split())
    print(f"published {FINAL} ({words} words, {len(text.splitlines())} lines); phase: {state['phase']}")


def validate_final(text):
    problems, warnings = [], []
    lines = text.splitlines()
    common_text_checks(lines, problems, warnings)
    anchors = ANCHOR.findall(text)
    for n in range(1, TOTAL_DAYS + 1):
        c = anchors.count(f"day-{day_id(n)}")
        if c != 1:
            problems.append(f"day-{day_id(n)} anchor appears {c} times")
        if text.count(f"\n### day {day_id(n)}: ") != 1:
            problems.append(f"day {day_id(n)} heading appears {text.count(f'### day {day_id(n)}: ')} times")
    for w in range(1, 9):
        if anchors.count(f"week-{w}") != 1:
            problems.append(f"week-{w} anchor missing or duplicated")
    for review in sorted(REVIEW_DAYS):
        if f"### day {day_id(review)}: week {(review // 7)} review" not in text:
            problems.append(f"day {review} is not titled as the week {review // 7} review")
    order = ["introduction", "course-overview", "table-of-contents", "progress-checklist",
             "week-1", "cheat-sheet", "references"]
    positions = [text.find(f'<a id="{a}"></a>') for a in order]
    if -1 in positions:
        problems.append("missing front or back section anchors: "
                        + ", ".join(a for a, p in zip(order, positions) if p == -1))
    elif positions != sorted(positions):
        problems.append("sections are out of the required order")
    dupes = {a for a in anchors if anchors.count(a) > 1}
    if dupes:
        problems.append(f"duplicate anchors: {sorted(dupes)}")
    known = set(anchors)
    for target in set(LINK.findall(text)):
        if target not in known:
            problems.append(f"broken internal link #{target}")
    if text.count("- [ ] [day ") != TOTAL_DAYS:
        problems.append("progress checklist does not have exactly 56 entries")
    return problems, warnings


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "check" and len(argv) == 3:
        problems, warnings, info = check_lesson(argv[2])
        for w in warnings:
            print("warning:", w)
        for p in problems:
            print("problem:", p)
        print("ok" if not problems else "FAILED", info)
        return 1 if problems else 0
    if cmd == "commit" and len(argv) == 3:
        tmp = Path(argv[2]).resolve()
        problems, warnings, info = check_lesson(tmp)
        for w in warnings:
            print("warning:", w)
        if problems:
            for p in problems:
                print("problem:", p)
            print("not committed")
            return 1
        final = tmp.with_name(tmp.name[: -len(".tmp")]) if tmp.name.endswith(".tmp") else tmp
        if final != tmp:
            os.replace(tmp, final)
        reconcile(action=f"committed {final.name}", quiet=True)
        print(f"committed {final.name}: {info}")
        return 0
    if cmd == "reconcile":
        reconcile(action="reconciled")
        return 0
    if cmd == "status":
        print_status(reconcile(quiet=True))
        return 0
    if cmd == "assemble":
        assemble()
        return 0
    if cmd == "validate":
        if not FINAL.exists():
            print("no published document")
            return 1
        problems, warnings = validate_final(FINAL.read_text(encoding="utf-8"))
        for w in warnings:
            print("warning:", w)
        for p in problems:
            print("problem:", p)
        print("ok" if not problems else "FAILED")
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
