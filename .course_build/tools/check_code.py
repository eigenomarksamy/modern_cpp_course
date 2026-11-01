#!/usr/bin/env python3
"""Compile-check the course's C++ examples, as labelled by their fence tags.

    ```cpp complete         a standalone translation unit: must compile; run if it has main()
    ```cpp complete norun   must compile; never run (it leaks, loops, or waits on purpose)
    ```cpp ub               compiles, contains undefined behavior on purpose: compiled, never run
    ```cpp fails            ill-formed on purpose: must fail to compile
    ```cpp group=NAME       part of a program split across blocks (in course order): the parts
                            are concatenated, compiled, and run as one translation unit
    ```cpp external         needs several files, modules support, or a third-party library: skipped
    ```cpp                  a snippet (fragment of a larger program): skipped
    a trailing c++17 or c++20 tag overrides the lesson's standard for that block.

Usage:
    python check_code.py [--cxx g++ --cxx clang++] [--run] [--sanitize] [--jobs N] [--only ID ...]
                         [--report .course_build/checks/code_report]

Every compiler is checked with -std=<standard> -Wall -Wextra -pedantic. Blocks that include
<format> are reported as skipped (not failed) on a compiler whose library lacks it, so the
report says exactly what was and was not verified. --sanitize adds AddressSanitizer and
UndefinedBehaviorSanitizer to runs (GCC/Clang on Linux or macOS). Nothing tagged ub is ever run.
"""

import argparse
import concurrent.futures as cf
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import course  # noqa: E402

MAIN = re.compile(r"\bint\s+main\s*\(")


def collect(only=None):
    """Return the list of checkable units: dicts with id, tags, standard, source."""
    cur, order, lessons = course.load()
    units, groups = [], {}
    for lid in order:
        l = lessons[lid]
        for idx, (line, lang, tags, body) in enumerate(course.code_blocks(l.body)):
            if lang != "cpp":
                continue
            std = next((t for t in tags if t in ("c++17", "c++20")), l.standard.lower())
            where = f".course_build/lessons/{lid}.md:{line + l.body_offset}"
            src = "\n".join(body) + "\n"
            group = next((t.split("=", 1)[1] for t in tags if t.startswith("group=")), None)
            if group:
                g = groups.setdefault(group, {"id": f"group:{group}", "where": [], "std": std,
                                              "kind": "group", "norun": False, "src": [], "lessons": set()})
                g["where"].append(where)
                g["src"].append(src)
                g["lessons"].add(lid)
                if std == "c++20":
                    g["std"] = "c++20"
                continue
            kind = ("fails" if "fails" in tags else "ub" if "ub" in tags else
                    "complete" if "complete" in tags else "external" if "external" in tags else "snippet")
            if only and lid not in only:
                continue
            units.append({"id": f"{lid}#{idx}", "where": where, "std": std, "kind": kind,
                          "norun": "norun" in tags, "src": src, "lesson": lid})
    for g in groups.values():
        if only and not (g["lessons"] & set(only)):
            continue
        units.append({"id": g["id"], "where": ", ".join(g["where"]), "std": g["std"], "kind": "group",
                      "norun": False, "src": "".join(g["src"]), "lesson": ",".join(sorted(g["lessons"]))})
    return units


def probe_format(cxx, workdir):
    f = Path(workdir) / "probe_format.cpp"
    f.write_text("#include <format>\nint main() { return std::format(\"{}\", 1).size() == 1 ? 0 : 1; }\n")
    r = subprocess.run([cxx, "-std=c++20", "-fsyntax-only", str(f)], capture_output=True, text=True)
    return r.returncode == 0


def check_unit(unit, cxx, workdir, run, sanitize, has_format):
    result = {"id": unit["id"], "where": unit["where"], "kind": unit["kind"], "std": unit["std"], "compiler": cxx}
    if unit["kind"] in ("snippet", "external"):
        result["status"] = "skipped"
        result["reason"] = "snippet" if unit["kind"] == "snippet" else "needs other files, modules, or a library"
        return result
    if "<format>" in unit["src"] and not has_format:
        result["status"] = "skipped"
        result["reason"] = "the standard library has no <format>"
        return result
    safe = re.sub(r"[^\w]+", "_", unit["id"])
    src = Path(workdir) / f"{safe}.cpp"
    src.write_text(unit["src"], encoding="utf-8")
    flags = [f"-std={unit['std']}", "-Wall", "-Wextra", "-pedantic", "-pthread"]
    has_main = bool(MAIN.search(unit["src"]))
    want_run = run and has_main and unit["kind"] in ("complete", "group") and not unit["norun"]
    if want_run:
        exe = Path(workdir) / (safe + (".exe" if os.name == "nt" else ""))
        extra = ["-g", "-O1", "-fsanitize=address,undefined", "-fno-sanitize-recover=undefined"] if sanitize else ["-O1"]
        cmd = [cxx, *flags, *extra, str(src), "-o", str(exe)]
    else:
        cmd = [cxx, *flags, "-fsyntax-only", str(src)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    compiled = r.returncode == 0
    diag = [l for l in r.stderr.splitlines() if "error" in l or "warning" in l][:4]
    if unit["kind"] == "fails":
        result["status"] = "ok" if not compiled else "FAILED"
        result["detail"] = "rejected as intended" if not compiled else "compiled, but is labelled as ill-formed"
        result["diagnostics"] = diag[:2]
        return result
    if not compiled:
        result["status"] = "FAILED"
        result["detail"] = "did not compile"
        result["diagnostics"] = diag
        return result
    result["warnings"] = [d for d in diag if "warning" in d]
    if not want_run:
        result["status"] = "ok"
        result["detail"] = "compiled" + (" (undefined behavior: not run)" if unit["kind"] == "ub" else "")
        return result
    try:
        p = subprocess.run([str(exe)], capture_output=True, text=True, timeout=30)
        ok = p.returncode == 0
        result["status"] = "ok" if ok else "FAILED"
        result["detail"] = "compiled and ran" + (" under ASan+UBSan" if sanitize else "") + \
            ("" if ok else f", exit code {p.returncode}")
        result["output"] = p.stdout[-400:]
        if not ok:
            result["stderr"] = p.stderr[-800:]
    except subprocess.TimeoutExpired:
        result["status"] = "FAILED"
        result["detail"] = "timed out after 30 s"
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cxx", action="append", help="compiler to use (repeatable); default: g++ and clang++ if found")
    ap.add_argument("--run", action="store_true", help="link and run complete examples that have main()")
    ap.add_argument("--sanitize", action="store_true", help="run with -fsanitize=address,undefined")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--only", nargs="*", help="lesson ids to check")
    ap.add_argument("--report", default=str(course.BUILD / "checks" / "code_report"),
                    help="path prefix for the .json and .md reports")
    args = ap.parse_args()

    compilers = args.cxx or [c for c in ("g++", "clang++") if shutil.which(c)]
    if not compilers:
        print("no C++ compiler found")
        return 2
    units = collect(set(args.only) if args.only else None)
    results, failures = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        for cxx in compilers:
            version = subprocess.run([cxx, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
            has_format = probe_format(cxx, tmp)
            work = Path(tmp) / re.sub(r"\W+", "_", cxx)
            work.mkdir()
            with cf.ThreadPoolExecutor(args.jobs) as ex:
                rs = list(ex.map(lambda u: check_unit(u, cxx, work, args.run, args.sanitize, has_format), units))
            for r in rs:
                r["compiler_version"] = version
            results += rs
            summary = {}
            for r in rs:
                summary[r["status"]] = summary.get(r["status"], 0) + 1
            failures += summary.get("FAILED", 0)
            print(f"{version}: " + ", ".join(f"{k} {v}" for k, v in sorted(summary.items())))
            for r in rs:
                if r["status"] == "FAILED":
                    print(f"  FAILED {r['id']} ({r['where']}): {r['detail']}")
                    for d in r.get("diagnostics", [])[:2]:
                        print(f"      {d[-160:]}")
                    if r.get("stderr"):
                        print("      " + r["stderr"].strip().splitlines()[-1][:160])

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    meta = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "platform": sys.platform, "run": args.run, "sanitize": args.sanitize, "compilers": compilers}
    report.with_suffix(".json").write_text(json.dumps({"meta": meta, "results": results}, indent=1) + "\n",
                                           encoding="utf-8")
    lines = [f"# code check report", "", f"generated {meta['generated']} on `{sys.platform}`; "
             f"run: {args.run}; sanitizers: {args.sanitize}.", "",
             "| example | kind | standard | compiler | status | detail |", "| --- | --- | --- | --- | --- | --- |"]
    for r in results:
        if r["status"] == "skipped" and r.get("reason") == "snippet":
            continue
        lines.append(f"| `{r['id']}` | {r['kind']} | {r['std']} | {r['compiler_version'][:40]} | {r['status']} | "
                     f"{r.get('detail') or r.get('reason', '')} |")
    snippets = sum(1 for r in results if r.get("reason") == "snippet")
    lines += ["", f"{snippets} snippet checks skipped (fragments are not standalone programs)."]
    report.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
