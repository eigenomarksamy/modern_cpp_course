"""One-time helper: write code-block tags into lesson sources from classify results.

Idempotent: existing tags on a fence are replaced by the computed ones.
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import course
res = {(r["lesson"], r["index"]): r for r in json.load(open(sys.argv[1]))}
blocks_dir = Path(sys.argv[1]).parent
FAILS = {("initialization", 1), ("const-correctness", 3), ("virtual-dispatch", 1), ("function-templates", 0)}
UB_EXTRA = {("temporaries-dangling", 1), ("value-categories", 5), ("undefined-behavior", 1), ("sequence-containers", 2),
            ("construction-order", 0), ("threads", 1), ("legacy-refactoring", 0)}
NORUN = {("shared-ptr", 0)}
GROUP = {"pipeline-design", "pipeline-processing", "pipeline-wiring"}
EXTERNAL_RE = re.compile(r"benchmark/benchmark\.h|LLVMFuzzerTestOneInput|^\s*export module|^\s*import |^\s*module;|#include \"", re.M)
FILES_RE = re.compile(r"^// [\w./-]+\.(?:cpp|h|cppm)\b", re.M)
counts = {}
cur, order, lessons = course.load()
for lid in order:
    l = lessons[lid]
    lines = l.raw.split("\n")
    changed = False
    for idx, (start, lang, tags, body) in enumerate(course.code_blocks(l.body)):
        if lang != "cpp":
            continue
        key = (lid, idx)
        src = "\n".join(body)
        r = res.get(key)
        if lid in GROUP:
            new = ["group=pipeline"]
        elif key in FAILS:
            new = ["fails"]
        elif EXTERNAL_RE.search(src) or len(FILES_RE.findall(src)) >= 2:
            new = ["external"]
        elif r and r["ok"]:
            if r["ub_mark"] or key in UB_EXTRA:
                new = ["ub"]
            elif key in NORUN:
                new = ["complete", "norun"]
            else:
                new = ["complete"]
        else:
            new = []
        keep = [t for t in tags if t in ("c++17", "c++20")]
        tags_out = new + keep
        file_line = start - 1 + l.body_offset            # index of the fence line in the raw file
        fence = lines[file_line]
        m = re.match(r"^(\s*)(`{3,}|~{3,})cpp\b.*$", fence)
        assert m, (lid, idx, fence)
        new_fence = f"{m.group(1)}{m.group(2)}cpp" + ("".join(" " + t for t in tags_out))
        if new_fence != fence:
            lines[file_line] = new_fence
            changed = True
        k = " ".join(new) or "snippet"
        counts[k] = counts.get(k, 0) + 1
    if changed:
        l.path.write_text("\n".join(lines), encoding="utf-8")
print(counts)
