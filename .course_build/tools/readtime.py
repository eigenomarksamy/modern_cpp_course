"""Approximate reading-time estimate for a lesson.

The estimate models a careful professional reader, not a skimmer:

- prose (including tables and lists) at 200 words per minute;
- code at a per-line cost that grows with the number of tokens on the line
  (1.2 s plus 0.3 s per token), plus 12 s to orient on each code block;
  program output and shell blocks count at half that cost;
- review questions add 15 s of thinking time each;
- a difficulty factor from the lesson's metadata (1, 2, or 3) scales the
  total by 1.0, 1.1, or 1.2.

Core content is everything except the "going deeper" section and, in
instructional lessons, collapsed <details> answers. Reviews count their
answers as core, because checking them is part of the review.

The numbers are deliberately simple and documented; they are meant to
compare lessons with each other and flag outliers, not to predict any one
reader's pace.
"""

import re

PROSE_WPM = 200
CODE_BLOCK_S = 12.0
CODE_LINE_S = 1.2
CODE_TOKEN_S = 0.3
QUESTION_S = 15.0
DIFFICULTY = {1: 1.0, 2: 1.1, 3: 1.2}

FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
TOKEN = re.compile(r"[A-Za-z_]\w*|\d[\w.']*|::|->|<<|>>|&&|\|\||[^\s\w]")
DEEPER = "going deeper"


def split_sections(body):
    """Return [(heading, text)] for the ### sections of a lesson body."""
    sections, current, lines, in_code = [], None, [], False
    for line in body.split("\n"):
        if FENCE.match(line):
            in_code = not in_code
        if not in_code and line.startswith("### "):
            if current is not None or lines:
                sections.append((current, "\n".join(lines)))
            current, lines = line[4:].strip(), []
        else:
            lines.append(line)
    sections.append((current, "\n".join(lines)))
    return sections


def _measure(text, strip_details):
    if strip_details:
        text = re.sub(r"<details>.*?</details>", " ", text, flags=re.S)
    prose_words, code_s, blocks = 0, 0.0, 0
    in_code, weight = False, 1.0
    for line in text.split("\n"):
        m = FENCE.match(line)
        if m:
            if not in_code:
                in_code, blocks = True, blocks + 1
                lang = m.group(2).strip().split(" ")[0]
                weight = 1.0 if lang.startswith("cpp") or lang == "cmake" else 0.5
                code_s += CODE_BLOCK_S * weight
            else:
                in_code = False
            continue
        if in_code:
            if line.strip():
                code_s += weight * (CODE_LINE_S + CODE_TOKEN_S * len(TOKEN.findall(line)))
        else:
            clean = re.sub(r"<[^>]+>|\]\([^)]*\)|[#*|>`]|^\s*[-\d.]+\s", " ", line)
            prose_words += len(clean.split())
    return prose_words, code_s, blocks


def estimate(body, kind="lesson", difficulty=1):
    """Return a dict with core and deeper minutes plus the raw measurements."""
    core_text, deeper_text, questions = [], [], 0
    for heading, text in split_sections(body):
        if heading == DEEPER:
            deeper_text.append(text)
        else:
            core_text.append(text)
            if kind == "review" and heading == "review questions":
                questions = len(re.findall(r"^\s*\d+\.\s", text, re.M))
    factor = DIFFICULTY.get(int(difficulty), 1.0)
    pw, cs, blocks = _measure("\n".join(core_text), strip_details=(kind != "review"))
    core_s = (pw / PROSE_WPM * 60 + cs + questions * QUESTION_S) * factor
    dw, ds, dblocks = _measure("\n".join(deeper_text), strip_details=False)
    deeper_s = (dw / PROSE_WPM * 60 + ds) * factor
    return {
        "core_minutes": round(core_s / 60, 1),
        "deeper_minutes": round(deeper_s / 60, 1),
        "prose_words": pw,
        "code_seconds": round(cs),
        "code_blocks": blocks,
        "questions": questions,
    }


def display_minutes(core_minutes):
    """Whole minutes for display, never below 1."""
    return max(1, int(core_minutes + 0.5))
