// Tests the built site in dist/ (run `npm run build` first).
//
// 1. static checks, always: every internal link and anchor resolves, every page
//    has the landmarks and labels the reader relies on, and the routes exist;
// 2. browser checks, when Chrome or Edge is available (CHROME_PATH, or the usual
//    install locations): a headless browser driven over the DevTools protocol
//    exercises progress, v1 migration, export/import, old-link redirects, copy
//    buttons, Compiler Explorer links, search, themes, and phone-width layout.
//
// No dependencies beyond Node 22: a tiny static server emulates Cloudflare's
// static-asset routing (directory index, trailing slash, 404.html).
//
//   node scripts/test-site.mjs [--screenshots DIR] [--no-browser]
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdtemp, readFile, readdir, rm, stat, writeFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { extname, join } from 'node:path';

const DIST = 'dist';
const args = process.argv.slice(2);
const shotsDir = args.includes('--screenshots') ? args[args.indexOf('--screenshots') + 1] : null;
let failures = 0;
const results = [];
function check(name, ok, detail = '') {
  results.push({ name, ok, detail });
  if (!ok) failures++;
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${name}${detail ? `: ${detail}` : ''}`);
}

// ---------------------------------------------------------------- static checks

async function walk(dir) {
  const out = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) out.push(...await walk(p)); else out.push(p);
  }
  return out;
}

const course = JSON.parse(await readFile('site/course.json', 'utf8'));
const files = (await walk(DIST)).map((f) => f.replaceAll('\\', '/'));
const html = new Map();
for (const f of files.filter((x) => x.endsWith('.html'))) html.set(f, await readFile(f, 'utf8'));
const routeOf = (f) => f.slice(DIST.length).replace(/index\.html$/, '');
const anchorsOf = (text) => new Set([...text.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]));
const anchors = new Map([...html].map(([f, t]) => [routeOf(f), anchorsOf(t)]));

check('one page per lesson', course.lessons.every((l) => html.has(`${DIST}/day/${l.slug}/index.html`)),
      `${course.lessons.length} lessons`);
for (const p of ['/', '/full/', '/cheat-sheet/', '/references/', '/404.html']) {
  check(`route ${p} exists`, anchors.has(p));
}
check('markdown download exists', files.includes(`${DIST}/modern_cpp_daily_course.md`));
check('search index lists every lesson', JSON.parse(await readFile(`${DIST}/search-index.json`, 'utf8')).length === course.lessons.length);

let broken = [];
for (const [f, text] of html) {
  const from = routeOf(f);
  for (const m of text.matchAll(/href="([^"]+)"/g)) {
    const href = m[1].replaceAll('&amp;', '&');
    if (/^(https?:|mailto:)/.test(href)) continue;
    const [path, hash] = href.split('#');
    const target = path === '' ? from : path;
    if (!target.startsWith('/')) { broken.push(`${from} -> ${href} (relative)`); continue; }
    if (target === '/modern_cpp_daily_course.md' || target.startsWith('/assets/')) {
      if (!files.includes(`${DIST}${target}`)) broken.push(`${from} -> ${href}`);
      continue;
    }
    const page = anchors.get(target);
    if (!page) { broken.push(`${from} -> ${href} (no page)`); continue; }
    if (hash && !page.has(hash)) broken.push(`${from} -> ${href} (no anchor)`);
  }
}
check('internal links and anchors resolve', broken.length === 0, broken.slice(0, 5).join('; '));

const a11y = [];
for (const [f, text] of html) {
  if (!/<html lang="en">/.test(text)) a11y.push(`${f}: lang`);
  if ((text.match(/<h1[\s>]/g) || []).length !== 1) a11y.push(`${f}: exactly one h1`);
  if (!/<main id="main">/.test(text) || !/class="skip" href="#main"/.test(text)) a11y.push(`${f}: main landmark and skip link`);
  if (!/<title>[^<]+<\/title>/.test(text)) a11y.push(`${f}: title`);
  for (const m of text.matchAll(/<button\b[^>]*>([\s\S]*?)<\/button>/g)) {
    if (!m[1].trim() && !/aria-label=/.test(m[0])) a11y.push(`${f}: unlabelled button`);
  }
}
check('pages have lang, one h1, main landmark, skip link, labelled buttons', a11y.length === 0, a11y.slice(0, 5).join('; '));
const ceLinks = [...html.values()].join('').match(/href="https:\/\/godbolt\.org\/clientstate\/[^"]+"/g) || [];
check('compiler explorer links present', ceLinks.length > 50, `${ceLinks.length} links`);
const ceOk = ceLinks.slice(0, 200).every((l) => {
  const s = JSON.parse(Buffer.from(l.slice(l.lastIndexOf('/') + 1, -1), 'base64url').toString());
  return s.sessions[0].source.length > 0 && /-std=c\+\+(17|20)/.test(s.sessions[0].compilers[0].options);
});
check('compiler explorer links decode to source and a standard', ceOk);
check('no unresolved [[references]] in pages', ![...html.values()].some((t) => /\[\[[a-z][\w-]*\]\]/.test(t.replace(/<code[\s\S]*?<\/code>/g, ''))));

// ---------------------------------------------------------------- server

const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css',
                '.json': 'application/json', '.md': 'text/markdown; charset=utf-8' };
function serve() {
  const server = createServer(async (req, res) => {
    const url = new URL(req.url, 'http://x');
    let p = decodeURIComponent(url.pathname);
    const send = async (file, status = 200) => {
      res.writeHead(status, { 'content-type': TYPES[extname(file)] || 'application/octet-stream' });
      res.end(await readFile(file));
    };
    try {
      const file = join(DIST, p);
      const s = await stat(file).catch(() => null);
      if (s && s.isDirectory()) {
        if (!p.endsWith('/')) { res.writeHead(307, { location: `${p}/` }); res.end(); return; }
        if (existsSync(join(file, 'index.html'))) return send(join(file, 'index.html'));
      } else if (s) return send(file);
      return send(join(DIST, '404.html'), 404);
    } catch (e) { res.writeHead(500); res.end(String(e)); }
  });
  return new Promise((ok) => server.listen(0, '127.0.0.1', () => ok(server)));
}

// ---------------------------------------------------------------- browser

function findBrowser() {
  const candidates = [process.env.CHROME_PATH,
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Google/Chrome/Application/chrome.exe', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium', '/usr/bin/chromium-browser', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'];
  return candidates.find((c) => c && existsSync(c));
}

class Cdp {
  constructor(ws) { this.ws = ws; this.id = 0; this.pending = new Map(); this.waiters = [];
    ws.addEventListener('message', (e) => {
      const msg = JSON.parse(e.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { ok, fail } = this.pending.get(msg.id); this.pending.delete(msg.id);
        msg.error ? fail(new Error(msg.error.message)) : ok(msg.result);
      } else if (msg.method) {
        this.waiters = this.waiters.filter((w) => !(w.method === msg.method && w.session === msg.sessionId && (w.ok(msg.params), true)));
      }
    });
  }
  send(method, params = {}, sessionId) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params, sessionId }));
    return new Promise((ok, fail) => this.pending.set(id, { ok, fail }));
  }
  once(method, session) { return new Promise((ok) => this.waiters.push({ method, session, ok })); }
}

async function browserTests(base) {
  const exe = findBrowser();
  if (!exe || args.includes('--no-browser')) {
    console.log(exe ? 'skip browser checks (--no-browser)' : 'skip browser checks: no Chrome or Edge found (set CHROME_PATH)');
    return;
  }
  const profile = await mkdtemp(join(tmpdir(), 'cpp-course-test-'));
  const proc = spawn(exe, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
    '--no-first-run', '--no-default-browser-check', '--disable-gpu', 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
  const wsUrl = await new Promise((ok, fail) => {
    let buf = '';
    proc.stderr.on('data', (d) => { buf += d; const m = /DevTools listening on (ws:\/\/\S+)/.exec(buf); if (m) ok(m[1]); });
    setTimeout(() => fail(new Error('browser did not start')), 20000);
  });
  const ws = new WebSocket(wsUrl);
  await new Promise((ok) => ws.addEventListener('open', ok));
  const cdp = new Cdp(ws);
  try {
    await cdp.send('Browser.grantPermissions', { origin: base, permissions: ['clipboardReadWrite', 'clipboardSanitizedWrite'] }).catch(() => {});
    const { targetId } = await cdp.send('Target.createTarget', { url: 'about:blank' });
    const { sessionId: s } = await cdp.send('Target.attachToTarget', { targetId, flatten: true });
    await cdp.send('Page.enable', {}, s);
    await cdp.send('Runtime.enable', {}, s);
    const errors = [];
    ws.addEventListener('message', (e) => {
      const m = JSON.parse(e.data);
      if (m.sessionId === s && m.method === 'Runtime.exceptionThrown') errors.push(m.params.exceptionDetails.text);
    });
    const withTimeout = (promise, ms, what) => Promise.race([promise,
      new Promise((_, fail) => setTimeout(() => fail(new Error(`timed out: ${what}`)), ms))]);
    const go = async (path) => {
      if (path.includes('#')) await go('about:blank');      // a fragment-only change fires no load event
      const loaded = cdp.once('Page.loadEventFired', s);
      await cdp.send('Page.navigate', { url: path.startsWith('about:') ? path : base + path }, s);
      await withTimeout(loaded, 15000, `load ${path}`);
      await new Promise((r) => setTimeout(r, 150));
    };
    const ev = async (expr) => {
      const r = await cdp.send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }, s);
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
      return r.result.value;
    };
    const waitFor = async (expr, ms = 5000) => {
      const end = Date.now() + ms;
      while (Date.now() < end) {
        try { if (await ev(expr)) return true; } catch { /* page in transition */ }
        await new Promise((r) => setTimeout(r, 100));
      }
      return false;
    };
    const shot = async (name) => {
      if (!shotsDir) return;
      const { data } = await cdp.send('Page.captureScreenshot', { format: 'png' }, s);
      await writeFile(join(shotsDir, `${name}.png`), Buffer.from(data, 'base64'));
    };
    const total = course.lessons.length;
    const dayOf = (id) => course.lessons.find((l) => l.id === id).slug;

    // fresh visitor
    await go('/');
    check('dashboard lists every lesson', await ev(`document.querySelectorAll('.lesson-list li').length`) === total);
    check('dashboard shows zero progress', (await ev(`document.getElementById('progress-count').textContent`)) === `0 of ${total}`);
    check('continue starts at day 01', (await ev(`document.getElementById('continue').getAttribute('href')`)) === '/day/01/');
    check('the module with the next lesson is expanded', await ev(`document.getElementById('module-${course.modules[0].id}').open`));
    await shot('dashboard-light');

    // v1 migration: the old site stored ["#day-01", ...] under modern-cpp-course:done
    const v1 = ['#day-01', '#day-02', '#day-03', '#day-04', '#day-05', '#day-06', '#day-07', '#day-10'];
    await ev(`localStorage.clear(); localStorage.setItem('modern-cpp-course:done', JSON.stringify(${JSON.stringify(v1)})); true`);
    await go('/');
    const migrated = await ev(`window.courseProgress.state.done`);
    const expected = Object.entries(course.legacy.v1.complete_when)
      .filter(([, days]) => days.every((d) => [1, 2, 3, 4, 5, 6, 7, 10].includes(d))).map(([id]) => id);
    check('v1 progress migrates exactly the derived lessons',
          JSON.stringify([...migrated].sort()) === JSON.stringify([...expected].sort()), `${migrated.length} lessons`);
    check('migration leaves new material unchecked', !migrated.includes('object-layout') && !migrated.includes('review-foundations'));
    check('split lessons inherit completion', ['copy-semantics', 'move-semantics', 'noexcept-moves'].every((id) => migrated.includes(id)));
    check('v1 key is kept, not deleted', (await ev(`localStorage.getItem('modern-cpp-course:done')`)) !== null);
    check('migration note is shown', await ev(`!document.getElementById('migration-note').hidden`));
    await ev(`document.getElementById('migration-dismiss').click(); true`);
    check('migration note can be dismissed', await ev(`document.getElementById('migration-note').hidden`));

    // lesson reader: visiting is not completing
    await ev(`localStorage.clear(); true`);
    await go('/day/21/');
    const l21 = course.lessons.find((l) => l.slug === '21');
    check('lesson page shows its title', (await ev(`document.querySelector('h1').textContent`)) === l21.title);
    check('visiting does not mark complete', (await ev(`window.courseProgress.state.done.length`)) === 0);
    check('last visited is recorded', (await ev(`window.courseProgress.state.last`)) === l21.id);
    await ev(`document.querySelector('.mark-done').click(); true`);
    await go('/day/21/');
    check('completion persists across reloads', (await ev(`document.querySelector('.mark-done').getAttribute('aria-pressed')`)) === 'true');
    check('previous and next links follow the curriculum',
          (await ev(`[...document.querySelectorAll('.lesson-nav a')].map(a => a.getAttribute('href')).join(' ')`)).includes('/day/20/') &&
          (await ev(`[...document.querySelectorAll('.lesson-nav a')].map(a => a.getAttribute('href')).join(' ')`)).includes('/day/22/'));
    check('optional material is collapsed in the reader', await ev(`[...document.querySelectorAll('details.deeper')].every(d => !d.open)`));
    await shot('lesson-21');
    await ev(`document.querySelector('figure.code[data-kind="complete"], figure.code').scrollIntoView(); true`);
    await shot('code-toolbar');
    await go('/');
    check('dashboard counts the completed lesson', (await ev(`document.getElementById('progress-count').textContent`)) === `1 of ${total}`);
    check('continue recommends the next lesson', (await ev(`document.getElementById('continue').getAttribute('href')`)) === '/day/22/');

    // export and import
    const exported = JSON.parse(await ev(`window.courseProgress.exportJson()`));
    check('export has format, schema, curriculum, ids, timestamp',
          exported.format === 'modern-cpp-course-progress' && exported.schema === 2 && exported.curriculum === course.version &&
          exported.completed[0] === l21.id && !!Date.parse(exported.exported) && exported.last === l21.id);
    const importFile = join(profile, 'progress.json');
    await writeFile(importFile, JSON.stringify({ ...exported, completed: ['build-pipeline', 'not-a-lesson'] }));
    const doc = await cdp.send('DOM.getDocument', {}, s);
    const { nodeId } = await cdp.send('DOM.querySelector', { nodeId: doc.root.nodeId, selector: '#import-file' }, s);
    await cdp.send('DOM.setFileInputFiles', { files: [importFile], nodeId }, s);
    await new Promise((r) => setTimeout(r, 300));
    check('import through the page merges and reports unknown ids',
          (await ev(`window.courseProgress.state.done.join(',')`)) === `build-pipeline,${l21.id}` &&
          /1 unknown/.test(await ev(`document.getElementById('progress-status').textContent`)));
    check('import replace mode', await ev(`(() => { window.courseProgress.importText(JSON.stringify({format:'modern-cpp-course-progress',schema:2,curriculum:'2.0',completed:['raii']}), 'replace'); return window.courseProgress.state.done.join(','); })()`) === 'raii');
    check('import accepts a raw v1 day list', await ev(`window.courseProgress.parseImport('["#day-08"]').ids.join(',')`) === 'raii,scope-guards');
    check('import rejects invalid files', await ev(`(() => { try { window.courseProgress.parseImport('{"x":1}'); return false; } catch (e) { return /not a progress export/.test(e.message); } })()`));

    // old links into the single-page v1 site
    const target = course.legacy.v1.redirect['12'];
    await go('/#day-12');
    check('old #day-12 links redirect to the matching lesson', await waitFor(`location.pathname === '/day/${dayOf(target)}/'`));
    await go('/#cheat-sheet');
    check('old #cheat-sheet links redirect', await waitFor(`location.pathname === '/cheat-sheet/'`));
    await go('/day/7/');
    check('unpadded day routes redirect', await waitFor(`location.pathname === '/day/07/'`));
    await go(`/#module-${course.modules[5].id}`);
    check('module links expand their module', await waitFor(`document.getElementById('module-${course.modules[5].id}').open`));
    await go('/no/such/page/');
    check('unknown paths show the 404 page', /page not found/.test(await ev(`document.querySelector('h1').textContent`)));

    // code tools
    await go('/day/01/');
    check('copy buttons are revealed', await ev(`document.querySelectorAll('button.code-copy:not([hidden])').length > 0`));
    await ev(`document.querySelector('button.code-copy').click(); true`);
    await new Promise((r) => setTimeout(r, 200));
    check('copy gives accessible feedback', /cop/.test(await ev(`document.getElementById('live').textContent + document.querySelector('button.code-copy').textContent`)));

    // search
    await ev(`(() => { const i = document.getElementById('search-input'); i.focus(); i.value = 'move semantics'; i.dispatchEvent(new Event('input')); return true; })()`);
    await new Promise((r) => setTimeout(r, 500));
    check('search finds lessons', await ev(`document.querySelectorAll('#search-results a[href^="/day/"]').length > 0`));

    // full course
    await go('/full/');
    check('full course contains every lesson anchor', await ev(`Array.from({length: ${total}}, (_, i) => String(i + 1).padStart(2, '0')).every(n => document.getElementById('day-' + n))`));
    const withDeeper = course.lessons.filter((l) => l.deeper_topics.length).length;
    check('full course keeps every optional section', await ev(`document.querySelectorAll('details.deeper').length`) === withDeeper,
          `${withDeeper} lessons have optional material`);

    // themes and phone width
    await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'dark' }] }, s);
    await go('/');
    check('dark theme follows the system', (await ev(`getComputedStyle(document.body).backgroundColor`)) === 'rgb(15, 15, 18)');
    await shot('dashboard-dark');
    await ev(`document.querySelector('.theme-toggle').click(); true`);   // auto -> light
    check('theme toggle overrides the system', (await ev(`document.documentElement.dataset.theme`)) === 'light' &&
          (await ev(`getComputedStyle(document.body).backgroundColor`)) === 'rgb(247, 246, 242)');
    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 375, height: 800, deviceScaleFactor: 2, mobile: true }, s);
    for (const p of ['/', '/day/03/', '/day/58/', '/full/', '/references/', '/cheat-sheet/']) {
      await go(p);
      const w = await ev(`document.documentElement.scrollWidth`);
      const culprit = w <= 375 ? '' : await ev(`(() => { const el = [...document.querySelectorAll('main *')]
        .filter(e => e.getBoundingClientRect().right > 376 && !e.closest('pre, table, .code-bar'))
        .sort((a, b) => b.getBoundingClientRect().width - a.getBoundingClientRect().width).pop();
        return el ? el.tagName + '.' + el.className + ': ' + el.textContent.slice(0, 60) : '?'; })()`);
      check(`no horizontal scroll at phone width on ${p}`, w <= 375, `scrollWidth ${w} ${culprit}`);
    }
    await go('/day/21/');
    await shot('lesson-21-phone');
    check('no script errors', errors.length === 0, errors.slice(0, 3).join('; '));
  } finally {
    ws.close();
    proc.kill();
    await new Promise((r) => setTimeout(r, 500));
    await rm(profile, { recursive: true, force: true }).catch(() => {});
  }
}

const server = await serve();
const base = `http://127.0.0.1:${server.address().port}`;
try { await browserTests(base); } catch (e) { check('browser checks ran', false, e.message); }
server.close();
console.log(`\n${results.length - failures} passed, ${failures} failed`);
process.exit(failures ? 1 : 0);
