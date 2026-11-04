// Renders the course into a static site in dist/, served by a Cloudflare Worker
// with static assets (wrangler.jsonc). The only input is site/course.json, which
// `python .course_build/tools/course.py assemble` generates from the lesson
// sources together with modern_cpp_daily_course.md, so every view shows the same
// content. Routes:
//   /                      dashboard: progress, continue, curriculum, tools
//   /day/NN/               one lesson per page
//   /full/                 the whole course on one page
//   /cheat-sheet/, /references/
//   /modern_cpp_daily_course.md, /search-index.json, /404.html
import { copyFile, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { Marked } from 'marked';
import hljs from 'highlight.js/lib/core';
import bash from 'highlight.js/lib/languages/bash';
import cmake from 'highlight.js/lib/languages/cmake';
import cpp from 'highlight.js/lib/languages/cpp';
import json from 'highlight.js/lib/languages/json';
import plaintext from 'highlight.js/lib/languages/plaintext';

const OUT = 'dist';
const MARKDOWN = 'modern_cpp_daily_course.md';
const SITE = 'https://cpp.eigenomar.com';
const HOME = 'https://eigenomar.com';
const REPO = 'https://github.com/eigenomarksamy/modern_cpp_course';
const CE_COMPILER = { id: 'g141', name: 'GCC 14.1' };   // Compiler Explorer compiler id

hljs.registerLanguage('cpp', cpp);
hljs.registerLanguage('sh', bash);
hljs.registerLanguage('cmake', cmake);
hljs.registerLanguage('json', json);
hljs.registerLanguage('text', plaintext);

const course = JSON.parse(await readFile('site/course.json', 'utf8'));
const lessons = course.lessons;
const byId = new Map(lessons.map((l) => [l.id, l]));
const modules = new Map(course.modules.map((m) => [m.id, m]));

const escapeHtml = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// ---------------------------------------------------------------- code blocks

// Programs split across blocks (```cpp group=NAME) are numbered in course order
// and linked to Compiler Explorer as one concatenated translation unit.
const groups = new Map();
for (const l of lessons) {
  for (const m of l.body.matchAll(/^```cpp([^\n]*)\n([\s\S]*?)^```$/gm)) {
    const g = /group=(\S+)/.exec(m[1]);
    if (!g) continue;
    if (!groups.has(g[1])) groups.set(g[1], []);
    groups.get(g[1]).push(m[2]);
  }
}

function compilerExplorerUrl(source, std) {
  const state = {
    sessions: [{
      id: 1, language: 'c++', source,
      compilers: [{ id: CE_COMPILER.id, options: `-std=${std} -O2 -Wall -Wextra -pedantic` }],
    }],
  };
  return `https://godbolt.org/clientstate/${Buffer.from(JSON.stringify(state)).toString('base64url')}`;
}

const KIND_LABEL = {
  complete: 'complete example',
  snippet: 'snippet',
  fails: 'does not compile, on purpose',
  ub: 'undefined behavior: read it, do not run it',
  external: 'needs other files or libraries',
};
const LANG_LABEL = { text: 'text', sh: 'shell', cmake: 'cmake', json: 'json' };

let context = { standard: 'C++17' };

function renderCode({ text, lang }) {
  const info = (lang || '').trim().split(/\s+/);
  const language = info[0] || 'text';
  const tags = info.slice(1);
  const highlighted = hljs.highlight(text, { language: hljs.getLanguage(language) ? language : 'text' }).value;
  let kind = 'other';
  let label = escapeHtml(LANG_LABEL[language] || language);
  let link = '';
  if (language === 'cpp') {
    const std = (tags.find((t) => t === 'c++17' || t === 'c++20') || context.standard.toLowerCase());
    const group = tags.find((t) => t.startsWith('group='));
    kind = group ? 'group' : (['complete', 'fails', 'ub', 'external'].find((t) => tags.includes(t)) || 'snippet');
    let tag = KIND_LABEL[kind];
    let source = text;
    if (group) {
      const parts = groups.get(group.slice(6));
      tag = `part ${parts.indexOf(text) + 1} of ${parts.length} of one program`;
      source = parts.join('\n');
    }
    label = `${std.replace('c++', 'C++')} <span class="tag">${escapeHtml(tag)}</span>`;
    if (['complete', 'fails', 'ub', 'group'].includes(kind)) {
      const title = `open in Compiler Explorer (${CE_COMPILER.name}, -std=${std})` +
        (kind === 'group' ? ': all parts of the program' : '');
      link = `<a class="code-ce" href="${compilerExplorerUrl(source, std)}" target="_blank" rel="noopener" title="${escapeHtml(title)}">Compiler Explorer</a>`;
    }
  }
  return `<figure class="code" data-kind="${kind}"><div class="code-bar"><span class="code-label">${label}</span>` +
    `<span class="code-actions">${link}<button type="button" class="code-copy" hidden>copy</button></span></div>` +
    `<pre><code class="hljs language-${escapeHtml(language)}">${highlighted}</code></pre></figure>\n`;
}

const marked = new Marked({ gfm: true, renderer: { code: renderCode } });
const md = (text, ctx = {}) => { context = { standard: 'C++17', ...ctx }; return marked.parse(text); };
const inline = (text) => marked.parseInline(text);

// lessons store sections at ### and topics at ####; shift them for each page's outline
function shiftHeadings(text, delta) {
  let inCode = false;
  return text.split('\n').map((line) => {
    if (/^\s*(```|~~~)/.test(line)) inCode = !inCode;
    if (inCode) return line;
    const m = /^(#{1,6}) (.*)$/.exec(line);
    return m ? `${'#'.repeat(Math.min(6, Math.max(1, m[1].length + delta)))} ${m[2]}` : line;
  }).join('\n');
}

function splitDeeper(body) {
  const i = body.search(/^### going deeper\s*$/m);
  return i < 0 ? [body, ''] : [body.slice(0, i), body.slice(i).replace(/^### going deeper\s*\n/, '')];
}

// links are written for the one-page document (#day-12); the multi-page site has routes
function routeLinks(html) {
  return html
    .replace(/href="#day-(\d+)"/g, 'href="/day/$1/"')
    .replace(/href="#module-([\w-]+)"/g, 'href="/#module-$1"')
    .replace(/href="#cheat-sheet"/g, 'href="/cheat-sheet/"')
    .replace(/href="#references"/g, 'href="/references/"')
    .replace(/href="#curriculum"/g, 'href="/#curriculum"')
    .replace(/href="#(introduction|course-overview|table-of-contents|progress-checklist)"/g, 'href="/full/#$1"');
}

function lessonHtml(lesson, shift) {
  const [core, deeper] = splitDeeper(lesson.body);
  const ctx = { standard: lesson.standard };
  let html = md(shiftHeadings(core, shift), ctx);
  if (deeper) {
    const topics = lesson.deeper_topics.length ? `: <span class="topics">${escapeHtml(lesson.deeper_topics.join('; '))}</span>` : '';
    html += `<details class="deeper"><summary>going deeper (optional)${topics}</summary>\n${md(shiftHeadings(deeper, shift), ctx)}</details>\n`;
  }
  return html;
}

// ---------------------------------------------------------------- page shell

function page({ title, description, pageType, lessonId = '', path, body }) {
  const nav = [
    ['/#curriculum', 'curriculum'], ['/full/', 'full course'], ['/cheat-sheet/', 'cheat sheet'], ['/references/', 'references'],
  ].map(([href, text]) => `<a href="${href}"${href === path ? ' aria-current="page"' : ''}>${text}</a>`).join('\n');
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(title)}</title>
<meta name="description" content="${escapeHtml(description)}">
<link rel="canonical" href="${SITE}${path}">
<link rel="stylesheet" href="/assets/style.css">
<script>try{var t=localStorage.getItem('modern-cpp-course:theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t;}catch(e){}</script>
<script src="/assets/course-data.js" defer></script>
<script src="/assets/app.js" defer></script>
</head>
<body data-page="${pageType}"${lessonId ? ` data-lesson="${lessonId}"` : ''}>
<a class="skip" href="#main">skip to content</a>
<header class="site-header">
<nav aria-label="site">
<a class="home" href="/">modern c++ daily course</a>
${nav}
<span class="header-tools">
<span class="search" role="search">
<label class="visually-hidden" for="search-input">search lessons</label>
<input id="search-input" type="search" placeholder="search lessons" autocomplete="off" aria-controls="search-results" aria-expanded="false">
<ul id="search-results" class="search-results" hidden></ul>
</span>
<button type="button" class="theme-toggle" aria-label="color theme">theme</button>
</span>
</nav>
</header>
<main id="main">
${body}
</main>
<footer class="site-footer">
<a class="button" href="${HOME}">eigenomar.com</a>
</footer>
<div id="live" class="visually-hidden" aria-live="polite"></div>
</body>
</html>
`;
}

// ---------------------------------------------------------------- pages

const counts = course.counts;

// the checkboxes stay disabled until app.js has loaded the progress they show
function lessonListItem(l) {
  return `<li data-id="${l.id}"${l.kind === 'review' ? ' class="review"' : ''}>` +
    `<input type="checkbox" class="status" aria-label="day ${l.slug} completed" disabled><span class="day">${l.slug}</span>` +
    `<a href="/day/${l.slug}/">${inline(l.title)}</a><span class="minutes">${l.minutes} min</span></li>`;
}

// option text cannot hold markup, so titles lose their backticks
const throughOptions = () => course.modules.map((m) => `<optgroup label="module ${m.n}: ${escapeHtml(m.title)}">
${m.lessons.map((id) => { const l = byId.get(id); return `<option value="${l.id}">day ${l.slug}: ${escapeHtml(l.title.replaceAll('`', ''))}</option>`; }).join('\n')}
</optgroup>`).join('\n');

function dashboard() {
  const mods = course.modules.map((m) => {
    const items = m.lessons.map((id) => lessonListItem(byId.get(id))).join('\n');
    const first = byId.get(m.lessons[0]).slug;
    const last = byId.get(m.lessons[m.lessons.length - 1]).slug;
    return `<details class="module" id="module-${m.id}" data-module="${m.id}">
<summary><span class="title">module ${m.n}: ${escapeHtml(m.title)}</span><span class="count">${m.lessons.length} days</span>
<span class="blurb">days ${first} to ${last}. ${inline(m.blurb)}</span>
<span class="bar" aria-hidden="true"><span></span></span></summary>
<ol class="lesson-list">
${items}
</ol>
</details>`;
  }).join('\n');
  const body = `<h1>${escapeHtml(course.title)}</h1>
<p class="lede">${escapeHtml(course.tagline)}. ${counts.lesson_count} days in ${counts.module_count} modules: ${counts.instructional_count} short lessons, each with one objective, and ${counts.review_count} reviews. read one a day, in order or wherever your work takes you.</p>
<p><a href="/full/#introduction">how the course works</a> · <a href="/full/#course-overview">course overview</a></p>

<section class="progress-summary" aria-labelledby="progress-heading">
<h2 id="progress-heading" class="visually-hidden">your progress</h2>
<p id="migration-note" hidden><span id="migration-text"></span> <button type="button" id="migration-dismiss">ok</button></p>
<p class="progress-line"><strong id="progress-pct">0%</strong> complete · <span id="progress-count">0 of ${counts.lesson_count}</span> days</p>
<div class="bar" role="progressbar" aria-label="course progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span id="progress-bar"></span></div>
<p><a id="continue" class="button primary" href="/day/${lessons[0].slug}/">start with day ${lessons[0].slug}: ${inline(lessons[0].title)}</a></p>
<p id="last-visited" class="muted" hidden></p>
</section>

<section id="curriculum" aria-labelledby="curriculum-heading">
<h2 id="curriculum-heading">curriculum</h2>
<p class="muted">every day lists its approximate reading time; tick a day to mark it as completed, or untick it to undo. reviews close each module; no lesson is locked.</p>
${mods}
</section>

<section class="resources">
<h2>the whole course</h2>
<ul>
<li><a href="/full/">the full course on one page</a>, with every lesson, review, and optional section</li>
<li><a href="/cheat-sheet/">modern C++17/20 cheat sheet</a></li>
<li><a href="/references/">references for deeper study</a></li>
<li><a href="/${MARKDOWN}" download>download the course as Markdown</a></li>
<li><a href="${REPO}">source on GitHub</a></li>
</ul>
</section>

<section class="progress-tools" aria-labelledby="tools-heading">
<h2 id="tools-heading">your progress data</h2>
<p class="muted">progress is stored only in this browser. export it to keep a copy or move it to another browser; importing accepts exports from this course, including exports and saved data from the original 56-day version.</p>
<div class="set-progress">
<label for="set-progress-through">completed through</label>
<select id="set-progress-through" aria-describedby="set-progress-help">
${throughOptions()}
</select>
<button type="button" id="set-progress">set progress</button>
</div>
<p id="set-progress-help" class="muted">marks every day up to the one you choose as completed, and every later day as not completed.</p>
<fieldset>
<legend>when importing</legend>
<label><input type="radio" name="import-mode" value="merge" checked> merge with this browser's progress</label>
<label><input type="radio" name="import-mode" value="replace"> replace this browser's progress</label>
</fieldset>
<p><button type="button" id="export-progress">export progress</button>
<button type="button" id="import-progress">import progress</button>
<input type="file" id="import-file" accept="application/json,.json" hidden>
<button type="button" id="reset-progress">reset progress</button></p>
<p id="progress-status" class="status-message" role="status"></p>
</section>`;
  return page({ title: course.title, description: `${course.tagline}: ${counts.lesson_count} short daily lessons.`,
                pageType: 'dashboard', path: '/', body });
}

function lessonLink(l, cls = '') {
  return `<a${cls ? ` class="${cls}"` : ''} href="/day/${l.slug}/">day ${l.slug}: ${inline(l.title)}</a>`;
}

function lessonPage(l, i) {
  const mod = modules.get(l.module);
  const prev = lessons[i - 1];
  const next = lessons[i + 1];
  const builds = l.prerequisites.map((id) => byId.get(id)).filter(Boolean);
  const later = l.used_by.map((id) => byId.get(id)).filter(Boolean).slice(0, 6);
  const buildsLabel = l.kind === 'review' ? 'covers' : 'builds on';
  const body = `<p class="crumbs"><a href="/#module-${mod.id}">module ${mod.n}: ${escapeHtml(mod.title)}</a> · day ${l.slug} of ${lessons.length}</p>
<h1>${inline(l.title)}</h1>
<p class="lesson-meta"><span>about ${l.minutes} minutes</span><span>${l.standard}</span>${l.kind === 'review' ? '<span>review</span>' : ''}${l.deeper_topics.length ? `<span>+ optional deeper material</span>` : ''}</p>
<p class="objective"><strong>objective:</strong> ${inline(l.objective)}</p>
${builds.length ? `<p class="builds-on">${buildsLabel}: ${builds.map((b) => lessonLink(b)).join(', ')}</p>` : ''}
<div class="lesson-actions"><button type="button" class="mark-done" aria-pressed="false" hidden>mark as completed</button><a href="/full/#day-${l.slug}">read in the full course</a></div>
<article class="lesson-body">
${routeLinks(lessonHtml(l, -1))}
</article>
${later.length ? `<p class="related">used later in: ${later.map((b) => lessonLink(b)).join(', ')}</p>` : ''}
<nav class="lesson-nav" aria-label="lesson navigation">
<div class="prev">${prev ? `<span class="label">previous</span>${lessonLink(prev)}` : ''}</div>
<div class="middle"><a href="/#module-${mod.id}">module ${mod.n}</a></div>
<div class="next">${next ? `<span class="label">next</span>${lessonLink(next)}` : '<span class="label">the end</span><a href="/">back to the dashboard</a>'}</div>
</nav>`;
  return page({ title: `day ${l.slug}: ${l.title} · ${course.title}`, description: l.objective,
                pageType: 'lesson', lessonId: l.id, path: `/day/${l.slug}/`, body });
}

function fullPage() {
  const toc = course.modules.map((m) => `<li><details><summary><a href="#module-${m.id}">module ${m.n}: ${escapeHtml(m.title)}</a></summary><ol>
${m.lessons.map((id) => { const l = byId.get(id); return `<li data-id="${l.id}"><a href="#day-${l.slug}">day ${l.slug}: ${inline(l.title)}</a></li>`; }).join('\n')}
</ol></details></li>`).join('\n');
  const mods = course.modules.map((m) => {
    const ls = m.lessons.map((id) => {
      const l = byId.get(id);
      const pre = l.prerequisites.map((p) => byId.get(p)).filter(Boolean)
        .map((b) => `<a href="#day-${b.slug}">day ${b.slug}</a>`).join(', ');
      return `<article class="full-lesson"><a id="day-${l.slug}"></a>
<h3>day ${l.slug}: ${inline(l.title)}</h3>
<p class="lesson-meta"><span>about ${l.minutes} minutes</span><span>${l.standard}</span><span><a href="/day/${l.slug}/">open as a single page</a></span></p>
<p class="objective"><strong>objective:</strong> ${inline(l.objective)}</p>
${pre ? `<p class="builds-on">${l.kind === 'review' ? 'covers' : 'builds on'}: ${pre}</p>` : ''}
${lessonHtml(l, 1)}
</article>`;
    }).join('\n');
    return `<section class="full-module"><a id="module-${m.id}"></a><h2>module ${m.n}: ${escapeHtml(m.title)}</h2>
<p>${inline(m.blurb)}</p>
${ls}
</section>`;
  }).join('\n');
  const s = course.sections;
  const body = `<h1>${escapeHtml(course.title)}: the full course</h1>
<p>every lesson, review, and optional section on one page, in course order. the same content as the <a href="/">daily reader</a> and the <a href="/${MARKDOWN}" download>Markdown download</a>.</p>
<div class="full-tools"><a class="button" href="/${MARKDOWN}" download>download Markdown</a><button type="button" id="expand-deeper" hidden>expand optional sections</button></div>
<nav class="toc" id="table-of-contents" aria-labelledby="toc-heading"><h2 id="toc-heading">contents</h2>
<ul>
<li><a href="#introduction">introduction and learning philosophy</a></li>
<li><a href="#course-overview">course overview</a></li>
<li><a href="#curriculum">curriculum map</a></li>
${toc}
<li><a href="#cheat-sheet">modern C++17/20 cheat sheet</a></li>
<li><a href="#references">references for deeper study</a></li>
</ul></nav>
${md(s.introduction)}
${md(s.overview)}
${md(s.curriculum)}
${mods}
${md(s.cheat_sheet)}
${md(s.references)}`;
  return page({ title: `the full course · ${course.title}`, description: 'every lesson of the course on one page.',
                pageType: 'full', path: '/full/', body });
}

function sectionPage(key, path, title) {
  const html = routeLinks(md(shiftHeadings(course.sections[key], -1)));
  return page({ title: `${title} · ${course.title}`, description: title, pageType: 'page', path, body: html });
}

function notFound() {
  const body = `<h1>page not found</h1>
<p>this address is not part of the course. the <a href="/">dashboard</a> lists every lesson, and the search box above finds them by topic.</p>
<script>
(function () {
  var m = /^\\/day\\/(\\d{1,3})\\/?$/.exec(location.pathname);
  if (m) { var n = String(+m[1]).padStart(2, '0'); if (n !== m[1]) location.replace('/day/' + n + '/'); }
})();
</script>`;
  return page({ title: `page not found · ${course.title}`, description: 'page not found', pageType: 'page', path: '/404.html', body });
}

// ---------------------------------------------------------------- write

const courseData = {
  version: course.version,
  lessons: lessons.map((l) => ({ id: l.id, slug: l.slug, title: l.title, module: l.module, kind: l.kind, minutes: l.minutes })),
  modules: course.modules.map((m) => ({ id: m.id, n: m.n, title: m.title, lessons: m.lessons })),
  legacy: course.legacy,
};
const searchIndex = lessons.map((l) => ({
  id: l.id, slug: l.slug, day: l.day, title: l.title,
  text: [l.id.replaceAll('-', ' '), l.objective, modules.get(l.module).title, ...l.deeper_topics,
         ...[...l.body.matchAll(/^#### (.+)$/gm)].map((m) => m[1])].join(' ').toLowerCase(),
}));

await rm(OUT, { recursive: true, force: true });
await mkdir(`${OUT}/assets`, { recursive: true });
const files = new Map([
  ['index.html', dashboard()],
  ['full/index.html', fullPage()],
  ['cheat-sheet/index.html', sectionPage('cheat_sheet', '/cheat-sheet/', 'cheat sheet')],
  ['references/index.html', sectionPage('references', '/references/', 'references')],
  ['404.html', notFound()],
  ['assets/course-data.js', `window.COURSE = ${JSON.stringify(courseData)};\n`],
  ['search-index.json', JSON.stringify(searchIndex)],
]);
lessons.forEach((l, i) => files.set(`day/${l.slug}/index.html`, lessonPage(l, i)));
for (const [name, content] of files) {
  await mkdir(`${OUT}/${name.split('/').slice(0, -1).join('/')}`, { recursive: true });
  await writeFile(`${OUT}/${name}`, content);
}
await copyFile('site/style.css', `${OUT}/assets/style.css`);
await copyFile('site/app.js', `${OUT}/assets/app.js`);
await copyFile(MARKDOWN, `${OUT}/${MARKDOWN}`);
const bytes = [...files.values()].reduce((n, s) => n + Buffer.byteLength(s), 0);
console.log(`built ${files.size + 3} files in ${OUT}/ (${Math.round(bytes / 1024)} KiB of HTML/JSON): ` +
            `${lessons.length} lesson pages, dashboard, full course, cheat sheet, references`);
