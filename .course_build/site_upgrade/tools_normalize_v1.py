"""One-time migration step: lowercase the prose of the v1 lessons and sections.

Reads archive/v1/{lessons,sections}, writes site_upgrade/work/v1/ with the same
line structure (line numbers are preserved, recipes rely on that), and prints
a summary of what changed and what needs a human decision.
"""
import collections, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import editorial

BUILD = Path(__file__).resolve().parent.parent
src = sorted((BUILD / "archive/v1/lessons").glob("day-*.md")) + sorted((BUILD / "archive/v1/sections").glob("*.md"))
texts = {p: p.read_text(encoding="utf-8") for p in src}
ids = editorial.code_identifiers(texts.values())
out = BUILD / "site_upgrade/work/v1"
out.mkdir(parents=True, exist_ok=True)
changed = collections.Counter(); unresolved = collections.Counter()
for p, text in texts.items():
    new, bad = editorial.normalize_text(text, ids)
    for a, b in zip(text.split("\n"), new.split("\n")):
        if a != b:
            for wa, wb in zip(a.split(), b.split()):
                if wa != wb: changed[wa.strip('*_(),.:;"')] += 1
    for n, w in bad: unresolved[(p.name, w)] += 1
    (out / p.name).write_text(new, encoding="utf-8", newline="\n")
print("lowercased words:", sum(changed.values()))
print(" ".join(f"{w}:{c}" for w, c in sorted(changed.items(), key=lambda x: -x[1])))
print("\nunresolved:", " ".join(f"{f}:{w}" for (f, w), c in sorted(unresolved.items())))
leftover = []
for p in sorted(out.glob("*.md")):
    for n, msg in editorial.check_text(p.read_text(encoding="utf-8"), ids):
        leftover.append(f"{p.name}:{n}: {msg}")
print("\ncheck after normalize:", len(leftover)); print("\n".join(leftover[:60]))
