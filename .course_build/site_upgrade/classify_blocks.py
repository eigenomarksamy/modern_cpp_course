"""One-time helper: compile every cpp block standalone and report the outcome."""
import concurrent.futures as cf, json, re, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import course
cur, order, lessons = course.load()
tmp = Path(sys.argv[1]); tmp.mkdir(parents=True, exist_ok=True)
jobs = []
for lid in order:
    l = lessons[lid]
    for i, (line, lang, tags, body) in enumerate(course.code_blocks(l.body)):
        if lang != "cpp": continue
        std = "c++20" if (l.standard == "C++20" or "c++20" in tags) else "c++17"
        jobs.append((lid, i, line + l.body_offset, std, "\n".join(body) + "\n"))
def run(job):
    lid, i, line, std, src = job
    f = tmp / f"{lid}-{i}.cpp"; f.write_text(src, encoding="utf-8")
    r = subprocess.run(["g++", f"-std={std}", "-fsyntax-only", "-Wall", "-Wextra", "-pedantic", str(f)],
                       capture_output=True, text=True)
    err = [l for l in r.stderr.splitlines() if "error" in l][:2]
    return {"lesson": lid, "index": i, "line": line, "std": std, "ok": r.returncode == 0,
            "has_main": bool(re.search(r"\bint\s+main\s*\(", src)),
            "ub_mark": bool(re.search(r"\bUB\b|undefined behavior", src)),
            "format": "<format>" in src, "err": err, "lines": src.count("\n")}
with cf.ThreadPoolExecutor(8) as ex:
    res = list(ex.map(run, jobs))
json.dump(res, open(tmp / "results.json", "w"), indent=1)
ok = sum(r["ok"] for r in res)
print(f"{len(res)} cpp blocks; {ok} compile standalone; {len(res)-ok} do not")
