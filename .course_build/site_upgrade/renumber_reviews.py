"""Renumber review questions 1..n and label answers "answer k: ..." in order.

Idempotent. Strips v1 "from week N" prefixes, which no longer mean anything.
"""
import re, sys
from pathlib import Path

def fix(path):
    text = Path(path).read_text(encoding="utf-8")
    lines = text.split("\n")
    section, q, a, out = None, 0, 0, []
    for line in lines:
        if line.startswith("### "):
            section = line[4:].strip()
        if section == "review questions":
            m = re.match(r"^(\d+)\. (.*)$", line)
            if m:
                q += 1
                body = re.sub(r"^\*\*from week \d\.\*\* ", "", m.group(2))
                line = f"{q}. {body}"
        if section == "answers":
            m = re.match(r"^<summary>(?:answer \d+: |\d+\. )?(.*)</summary>$", line)
            if m and not m.group(1).startswith("mini exercise"):
                a += 1
                title = re.sub(r"^from week \d: ", "", m.group(1))
                line = f"<summary>answer {a}: {title}</summary>"
            elif m:
                line = "<summary>mini exercise answer</summary>"
        out.append(line)
    if q != a:
        print(f"{path}: {q} questions but {a} answers")
    Path(path).write_text("\n".join(out), encoding="utf-8")

for p in sys.argv[1:]:
    fix(p)
