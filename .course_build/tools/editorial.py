"""Editorial rules for the course: lowercase prose and no em dashes.

Prose is lowercase, including the start of every sentence. Capitals are allowed
only for acronyms (RAII, UB), C++ and its versions, proper names and products
(Linux, GitHub, CMake), and exact identifiers. Code blocks, inline code, URLs,
HTML tags, cross references, quotations ("..."), and italic titles (*...*) are
protected and never checked or changed.

check_text() reports suspicious words with line numbers. normalize_text()
lowercases ordinary capitalized words and leaves everything protected alone;
it never touches mixed-case words it does not recognize, it only reports them.
"""

import re

# Proper names, products, tools, units, and other words that keep their capitals.
ALLOWLIST = set("""
AArch64 Abrahams Acton AddressSanitizer Amdahl AMD Anthony AoS Apple Asio
Baker Bazel Bjarne Bloaty Boost Cachegrind Carruth Catch2 Chandler Chrome Clang
Cloudflare CMake Conan CppCon Dave Debian Dekker DoF Doppler Doxygen Drepper Edge
Feathers Fedor GiB GitHub GoingNative Godbolt Google GoogleTest Gruber Herb Hyrum
Hz Iglberger Intel Itanium Java JavaScript Josuttis KiB Klaus kHz dB Lewis Linux
Liskov macOS Markdown MiB MinGW Meyers Michael Mike MSan MSYS2 NaN NaNs Nicolai
Ninja Node Parent Perfetto Pikus Python Qt Rust Scott Sean Smalltalk SoA
Stroustrup Sutter ThreadSanitizer Tracy TSan Tuesday UBSan Ubuntu Ulrich
Valgrind VTune Williams Win32 Windows libFuzzer oneTBB Wrangler ASan Instruments
""".split())

# Multi-word names whose ordinary words keep their capitals only in this phrase.
PHRASES = [
    "Compiler Explorer", "C++ Insights", "Quick C++ Benchmark", "Google Benchmark",
    "Core Guidelines", "Standard C++ Foundation", "Visual Studio", "Guru of the Week",
    "Asymmetric Transfer", "GitHub Actions", "Workers Builds", "Node.js",
    "Static Assets", "Boost.Filesystem", "C++ and Beyond",
]

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
WORD = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:\+\+\d*)?(?:['’][A-Za-z]+)?")
ACRONYM = re.compile(r"[A-Z][A-Z0-9]+(?:\+\+)?\d*s?|C\+\+\d*|[A-Z]")
EM_DASH = "\u2014"

# Spans that are never checked: inline code, link targets, autolinks, raw URLs,
# HTML tags and entities, cross references, quotations, italic titles, phrases.
PROTECT = re.compile(
    r"`[^`]*`"
    r"|\]\([^)]*\)"
    r"|<https?://[^>]*>|https?://\S+"
    r"|</?[A-Za-z][^>]*>|&[a-z]+;"
    r"|\[\[[^\]]*\]\]"
    r"|\"[^\"\n]*\"|“[^”\n]*”"
    r"|(?<![*\w])\*(?![\s*])[^*`\n]*?(?<![\s*])\*(?![*\w])"
    r"|" + "|".join(re.escape(p) for p in PHRASES)
)

CODE_COMMENT = re.compile(r"//.*$|/\*.*?\*/")
CODE_STRING = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')


def code_identifiers(texts):
    """Identifiers used in C++ code blocks (comments and strings excluded)."""
    ids = set()
    for text in texts:
        in_code = is_cpp = False
        for line in text.splitlines():
            if FENCE.match(line):
                in_code = not in_code
                is_cpp = in_code and line.strip().lstrip("`~").startswith("cpp")
                continue
            if in_code and is_cpp:
                line = CODE_STRING.sub(" ", CODE_COMMENT.sub(" ", line))
                ids.update(re.findall(r"[A-Za-z_]\w*", line))
    return ids


def allowed(word, identifiers, sentence_start=False):
    """Is this capitalized word legitimate here?

    Identifiers from code count only mid-sentence: at a sentence start a
    capital is far more likely to be an ordinary word ("The", "Signed").
    """
    base = re.sub(r"['’][A-Za-z]+$", "", word)
    if base == base.lower() and word == word.lower():
        return True
    if base in ALLOWLIST:
        return True
    if base in identifiers and not (sentence_start and re.fullmatch(r"[A-Z][a-z]+", base)):
        return True
    if base == "A":
        return False  # the article, not a name
    return bool(ACRONYM.fullmatch(base))


SENTENCE_END = re.compile(r"(?:^|[.!?:]|^\s*(?:[-+]|\d+\.|>|\|)|\|)[\s*_(\[]*$")


def _sentence_start(line, pos):
    """True when the word at pos begins a sentence, list item, or table cell."""
    return bool(SENTENCE_END.search(line[:pos]))


def prose_lines(text):
    """Yield (line_number, line) for lines outside fenced code blocks."""
    in_code = False
    for n, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_code = not in_code
            continue
        if not in_code:
            yield n, line


def _segments(line):
    """Split a line into (start, text, protected) segments."""
    out, pos = [], 0
    for m in PROTECT.finditer(line):
        if m.start() > pos:
            out.append((pos, line[pos:m.start()], False))
        out.append((m.start(), m.group(0), True))
        pos = m.end()
    if pos < len(line):
        out.append((pos, line[pos:], False))
    return out


def check_text(text, identifiers=frozenset()):
    """Return a list of (line_number, message) for editorial problems."""
    problems = []
    for n, line in prose_lines(text):
        if EM_DASH in line:
            problems.append((n, "em dash in prose"))
        bad = []
        for start, seg, protected in _segments(line):
            if protected:
                continue
            for m in WORD.finditer(seg):
                if not allowed(m.group(0), identifiers, _sentence_start(line, start + m.start())):
                    bad.append(m.group(0))
        if bad:
            problems.append((n, "unexpected capitals: " + ", ".join(dict.fromkeys(bad))))
    # Em dashes inside code are fine; only prose is checked above.
    return problems


def normalize_line(line, identifiers):
    """Lowercase ordinary capitalized words; return (line, unresolved_words)."""
    out, unresolved = [], []
    for start, seg, protected in _segments(line):
        if protected:
            out.append(seg)
            continue

        def fix(m, start=start):
            w = m.group(0)
            if allowed(w, identifiers, _sentence_start(line, start + m.start())):
                return w
            base = re.sub(r"['’][A-Za-z]+$", "", w)
            if re.fullmatch(r"[A-Z][a-z0-9]*", base) or base == "A":
                return w[0].lower() + w[1:]
            unresolved.append(w)
            return w

        out.append(WORD.sub(fix, seg))
    return "".join(out), unresolved


def normalize_text(text, identifiers=frozenset()):
    lines, unresolved, in_code = [], [], False
    for n, line in enumerate(text.split("\n"), 1):
        if FENCE.match(line):
            in_code = not in_code
            lines.append(line)
            continue
        if in_code:
            lines.append(line)
            continue
        new, bad = normalize_line(line, identifiers)
        lines.append(new)
        unresolved += [(n, w) for w in bad]
    return "\n".join(lines), unresolved
