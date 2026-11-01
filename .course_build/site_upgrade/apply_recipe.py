"""One-time migration tool: build v2 lesson files from v1 lessons and recipes.

A recipe (recipes/*.txt) describes how one or more v1 lessons become v2 lessons:

    source: day-10                 default v1 file for line ranges
    refs: 10=move-semantics        per-recipe overrides of the v1 -> v2 ref map
    >>> move-semantics             start writing lessons/move-semantics.md
    ---                            frontmatter lines follow until the next ---
    title: ...
    ---
    <<< 13-29                      copy lines 13..29 of the source (inclusive)
    <<< day-11:40-52               copy from another v1 file
    any other line                 copied literally

Copied text comes from work/v1/ (the lowercased copy of the v1 lessons, same
line numbers as archive/v1/). Bare "day NN" references in copied prose are
rewritten to [[lesson-id]] cross references through v1_refmap.json plus the
recipe's overrides; every rewrite is printed so it can be reviewed.

Run: python apply_recipe.py recipes/v1-10.txt [more recipes...]
A lesson file that already exists is only replaced when --force is given, so
re-running a finished recipe never clobbers later hand edits.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
WORK = HERE / "work" / "v1"
LESSONS = BUILD / "lessons"
REFMAP = json.loads((HERE / "v1_refmap.json").read_text(encoding="utf-8"))
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


def convert_refs(line, refmap, log, where):
    def target(n):
        key = f"{int(n):02d}"
        if key not in refmap:
            log.append(f"{where}: no mapping for day {key}")
            return f"day {key}"
        return f"[[{refmap[key]}]]"

    def sub_list(m):
        nums = re.findall(r"\d{2}", m.group(0))
        joined = m.group(0)
        for n in nums:
            joined = re.sub(rf"\b{n}\b", target(n), joined, count=1)
        joined = re.sub(r"^days ", "", joined)
        log.append(f"{where}: {m.group(0)!r} -> {joined!r}")
        return joined

    original = line
    line = re.sub(r"\[days? (\d{2})\]\(#day-\d{2}\)", lambda m: target(m.group(1)), line)
    line = re.sub(r"\bdays \d{2}(?:(?:, | and |, and | to | or )\d{2})+", sub_list, line)
    line = re.sub(r"\bday (\d{2})\b", lambda m: target(m.group(1)), line)
    if line != original and "days" not in original:
        log.append(f"{where}: {original.strip()[:110]!r}")
    for m in re.finditer(r"\bweeks? \d", line):
        log.append(f"{where}: CHECK week reference: {line.strip()[:110]!r}")
    return line


def source_lines(name):
    return (WORK / f"{name}.md").read_text(encoding="utf-8").split("\n")


def apply(recipe_path, force=False):
    lines = Path(recipe_path).read_text(encoding="utf-8").split("\n")
    source, refmap, log = None, dict(REFMAP), []
    outputs, current, in_front = {}, None, False
    for raw in lines:
        if raw.startswith("source: ") and current is None:
            source = raw[len("source: "):].strip()
            continue
        if raw.startswith("refs: ") and current is None:
            for pair in raw[len("refs: "):].split():
                k, v = pair.split("=")
                refmap[f"{int(k):02d}"] = v
            continue
        if raw.startswith(">>> "):
            current = raw[4:].strip()
            outputs[current] = []
            continue
        if current is None:
            continue
        if raw.startswith("<<< "):
            spec = raw[4:].strip()
            name, rng = (spec.split(":") if ":" in spec else (source, spec))
            a, b = (int(x) for x in rng.split("-"))
            src = source_lines(name)
            in_code = False
            for i in range(a, b + 1):
                text = src[i - 1]
                if FENCE.match(text):
                    in_code = not in_code
                elif not in_code:
                    text = convert_refs(text, refmap, log, f"{current} <- {name}:{i}")
                outputs[current].append(text)
            continue
        outputs[current].append(raw)

    for lesson_id, body in outputs.items():
        text = "\n".join(body).strip("\n") + "\n"
        text = re.sub(r"\n{3,}", "\n\n", text)
        path = LESSONS / f"{lesson_id}.md"
        if path.exists() and not force:
            print(f"skip {path.name}: exists (use --force to rebuild from the recipe)")
            continue
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(BUILD)} ({len(text.split())} words)")
    for entry in log:
        print("  ref", entry)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--force"]
    for r in args:
        apply(r, force="--force" in sys.argv)
