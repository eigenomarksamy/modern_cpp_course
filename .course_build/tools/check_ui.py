#!/usr/bin/env python3
"""Apply the editorial rules to the generated website, not just the sources.

Checks the visible text of every page in dist/ (navigation, buttons, labels,
headings, lesson prose), the user-facing attributes (title, aria-label,
placeholder, meta description), and the string literals in site/app.js
(progress and error messages). Code, preformatted text, and URLs are exempt,
as in the source checks. Run after `npm run build`:

    python .course_build/tools/check_ui.py [dist]
"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import course  # noqa: E402
import editorial  # noqa: E402

SKIP = {"code", "pre", "script", "style", "svg", "em", "cite"}   # em: italic titles, as in the sources
ATTRS = {"title", "aria-label", "placeholder", "alt"}


class TextCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth, self.chunks = 0, []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.depth += 1
        for k, v in attrs:
            if v and (k in ATTRS or (tag == "meta" and k == "content" and ("name", "description") in attrs)):
                self.chunks.append(v)

    def handle_endtag(self, tag):
        if tag in SKIP and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if not self.depth and data.strip():
            self.chunks.append(data.strip())


def main():
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else course.ROOT / "dist")
    _, _, lessons = course.load()
    ids = course.all_identifiers(lessons)
    problems = []
    for page in sorted(dist.rglob("*.html")):
        parser = TextCollector()
        parser.feed(page.read_text(encoding="utf-8"))
        seen = set()
        for chunk in parser.chunks:
            # rendered text has lost its backticks; protect what looks like code or a path
            chunk = re.sub(r"\S*(::|->|\(\)|\.cpp|\.h\b|/)\S*", " ", chunk)
            for _, msg in editorial.check_text(chunk, ids):
                key = (msg, chunk[:60])
                if key not in seen:
                    seen.add(key)
                    problems.append(f"{page.relative_to(dist)}: {msg}  [{chunk[:70]}]")
    app = (course.ROOT / "site" / "app.js").read_text(encoding="utf-8")
    for n, line in enumerate(app.split("\n"), 1):
        if line.strip().startswith("//"):
            continue
        for m in re.finditer(r"'([^'\n]*)'|`([^`\n]*)`", line):
            text = m.group(1) if m.group(1) is not None else m.group(2)
            if " " not in text or text.startswith(("/", "#", "modern-cpp", "application/")):
                continue          # identifiers, selectors, keys, and paths, not messages
            text = re.sub(r"\$\{[^}]*\}", " ", text)
            for _, msg in editorial.check_text(text, ids):
                problems.append(f"site/app.js:{n}: {msg}  [{text[:70]}]")
    for p in problems:
        print("problem:", p)
    print("ok" if not problems else f"FAILED: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
