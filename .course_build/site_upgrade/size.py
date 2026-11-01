"""Print the reading-time estimate for v2 lessons (migration helper)."""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import readtime
L = Path(__file__).resolve().parent.parent / "lessons"
names = sys.argv[1:] or [p.stem for p in sorted(L.glob("*.md"))]
for name in names:
    text = (L / f"{name}.md").read_text(encoding="utf-8")
    fm = dict(re.findall(r"^(\w+): (.*)$", text.split("---")[1], re.M))
    body = text.split("---", 2)[2]
    e = readtime.estimate(body, fm.get("kind", "lesson"), fm.get("difficulty", 1))
    heads = [h for h in re.findall(r"^### (.+)$", body, re.M)]
    flag = "  <-- LONG" if e["core_minutes"] > 10 else ("  <-- short" if e["core_minutes"] < 4.5 else "")
    print(f"{name:32s} core {e['core_minutes']:4.1f}m deeper {e['deeper_minutes']:4.1f}m prose {e['prose_words']:4d}w code {e['code_seconds']:4d}s blocks {e['code_blocks']}{flag}")
