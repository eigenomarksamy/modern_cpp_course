// Renders modern_cpp_daily_course.md into a single static page in dist/,
// which wrangler.jsonc serves as a Cloudflare Worker with static assets.
// The Markdown file stays the source of truth; this only presents it.
import { copyFile, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { Marked } from 'marked';
import { markedHighlight } from 'marked-highlight';
import hljs from 'highlight.js/lib/core';
import bash from 'highlight.js/lib/languages/bash';
import cpp from 'highlight.js/lib/languages/cpp';
import plaintext from 'highlight.js/lib/languages/plaintext';

const SOURCE = 'modern_cpp_daily_course.md';
const OUT = 'dist';
const SITE = 'https://eigenomar.com';
const REPO = 'https://github.com/eigenomarksamy/modern_cpp_course';

hljs.registerLanguage('cpp', cpp);
hljs.registerLanguage('sh', bash);
hljs.registerLanguage('text', plaintext);

const marked = new Marked(
  markedHighlight({
    emptyLangClass: 'hljs',
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      const language = hljs.getLanguage(lang) ? lang : 'text';
      return hljs.highlight(code, { language }).value;
    },
  }),
);

const markdown = await readFile(SOURCE, 'utf8');
const title = markdown.match(/^# (.+)$/m)?.[1] ?? 'modern c++ daily course';
const body = await marked.parse(markdown);

// The checklist is plain GFM task items, which render disabled. Enable them and
// remember ticks in this browser only; the page works the same without storage.
const script = `
const KEY = 'modern-cpp-course:done';
let done = [];
try { done = JSON.parse(localStorage.getItem(KEY)) || []; } catch {}
for (const box of document.querySelectorAll('li > input[type=checkbox]')) {
  const day = box.parentElement.querySelector('a[href^="#day-"]')?.getAttribute('href');
  if (!day) continue;
  box.disabled = false;
  box.checked = done.includes(day);
  box.setAttribute('aria-label', 'done: ' + box.parentElement.textContent.trim());
  box.addEventListener('change', () => {
    done = box.checked ? [...new Set([...done, day])] : done.filter((d) => d !== day);
    try { localStorage.setItem(KEY, JSON.stringify(done)); } catch {}
  });
}`;

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<meta name="description" content="A 56-day course on modern C++17 and C++20 for working engineers, 5 to 10 minutes a day.">
<style>
:root {
  --bg: #f7f6f2;
  --surface: #efede6;
  --fg: #19191d;
  --muted: #6a6a73;
  --border: #dddbd2;
  --accent: #d2491b;
  --keyword: #a3360f;
  --string: #2f6b3a;
  --number: #7a4bb0;
  --comment: #7c7c86;
  --font-sans: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  --font-mono: ui-monospace, 'SF Mono', 'Cascadia Code', 'JetBrains Mono', Consolas, Menlo, monospace;
  --measure: 46rem;
  --gutter: clamp(1rem, 4vw, 2rem);
  --radius: 6px;
  color-scheme: light dark;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f0f12;
    --surface: #18181c;
    --fg: #ebebee;
    --muted: #9696a0;
    --border: #2a2a30;
    --accent: #ff8552;
    --keyword: #ff9d73;
    --string: #8fcf8f;
    --number: #c7a4f5;
    --comment: #8a8a94;
  }
}
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-padding-top: 4rem; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: var(--font-sans);
  font-size: 1.0625rem;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}
header {
  position: sticky;
  top: 0;
  z-index: 1;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
}
header nav {
  max-width: var(--measure);
  margin: 0 auto;
  padding: 0.75rem var(--gutter);
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 1.25rem;
  font-size: 0.9rem;
}
header nav a:first-child { margin-right: auto; }
main {
  max-width: var(--measure);
  margin: 0 auto;
  padding: 2rem var(--gutter) 4rem;
}
a { color: var(--accent); text-underline-offset: 0.15em; }
h1, h2, h3, h4, h5 { line-height: 1.25; margin: 2em 0 0.6em; }
h1 { font-size: 2rem; margin-top: 0.5em; }
h2 { font-size: 1.6rem; padding-top: 1.5rem; border-top: 1px solid var(--border); }
h3 { font-size: 1.3rem; }
h4 { font-size: 1.1rem; }
h5 { font-size: 1rem; }
code, pre { font-family: var(--font-mono); font-size: 0.875em; }
:not(pre) > code { background: var(--surface); padding: 0.1em 0.3em; border-radius: 4px; }
pre {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.9rem 1rem;
  overflow-x: auto;
  line-height: 1.45;
}
pre code { font-size: 1em; }
table { display: block; overflow-x: auto; border-collapse: collapse; margin: 1.25rem 0; font-size: 0.95rem; }
th, td { border: 1px solid var(--border); padding: 0.4rem 0.7rem; text-align: left; vertical-align: top; }
th { background: var(--surface); }
blockquote { margin: 1rem 0; padding: 0.1rem 1rem; border-left: 3px solid var(--border); color: var(--muted); }
details {
  margin: 0.75rem 0;
  padding: 0.5rem 1rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
summary { cursor: pointer; color: var(--accent); }
details[open] summary { margin-bottom: 0.5rem; }
li > input[type=checkbox] { accent-color: var(--accent); margin-right: 0.4rem; }
li:has(> input[type=checkbox]) { list-style: none; margin-left: -1.25rem; }
hr { border: 0; border-top: 1px solid var(--border); margin: 2rem 0; }
.hljs-keyword, .hljs-built_in, .hljs-type, .hljs-meta .hljs-keyword { color: var(--keyword); }
.hljs-string, .hljs-meta .hljs-string { color: var(--string); }
.hljs-number, .hljs-literal { color: var(--number); }
.hljs-comment { color: var(--comment); font-style: italic; }
.hljs-meta { color: var(--muted); }
.hljs-title { color: var(--fg); font-weight: 600; }
</style>
</head>
<body>
<header>
<nav>
<a href="${SITE}/writings">eigenomar.com</a>
<a href="#table-of-contents">contents</a>
<a href="#progress-checklist">progress</a>
<a href="/${SOURCE}" download>markdown</a>
<a href="${REPO}">source</a>
</nav>
</header>
<main>
${body}
</main>
<script>${script}</script>
</body>
</html>
`;

await rm(OUT, { recursive: true, force: true });
await mkdir(OUT, { recursive: true });
await writeFile(`${OUT}/index.html`, html);
await copyFile(SOURCE, `${OUT}/${SOURCE}`);
console.log(`built ${OUT}/index.html (${Math.round(html.length / 1024)} KiB) from ${SOURCE}`);
