// modern c++ daily course: progress, migration, import/export, search, code tools.
// Everything here is progressive enhancement: every page works without it.
(() => {
  'use strict';

  const C = window.COURSE;
  const KEY = 'modern-cpp-course:progress';      // v2 state (this file)
  const LEGACY_KEY = 'modern-cpp-course:done';   // v1: ["#day-01", ...], kept untouched
  const THEME_KEY = 'modern-cpp-course:theme';
  const FORMAT = 'modern-cpp-course-progress';
  const SCHEMA = 2;
  const MAX_IMPORT_BYTES = 256 * 1024;

  const lessons = C.lessons;
  const byId = new Map(lessons.map((l, i) => [l.id, Object.assign({ index: i }, l)]));
  const slugOf = (id) => byId.get(id).slug;
  const dayHref = (id) => `/day/${slugOf(id)}/`;

  // ------------------------------------------------------------ storage

  const store = {
    get(k) { try { return window.localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { window.localStorage.setItem(k, v); return true; } catch { return false; } },
  };

  // v1 stored "#day-07"; accept a few spellings so old exports also work.
  function v1Days(entries) {
    const days = new Set();
    for (const e of entries) {
      const m = /^#?(?:day-)?0*(\d{1,2})$/.exec(String(e).trim());
      if (m && +m[1] >= 1 && +m[1] <= 56) days.add(+m[1]);
    }
    return days;
  }

  // a v2 lesson counts as complete only if every v1 day it was derived from was complete
  function lessonsFromV1(days) {
    const out = [];
    for (const [id, required] of Object.entries(C.legacy.v1.complete_when)) {
      if (byId.has(id) && required.length && required.every((d) => days.has(d))) out.push(id);
    }
    return out;
  }

  const ordered = (set) => lessons.filter((l) => set.has(l.id)).map((l) => l.id);

  function fresh() {
    return { schema: SCHEMA, curriculum: C.version, done: [], last: null, updated: null };
  }

  function sanitize(s) {
    const out = fresh();
    if (Array.isArray(s.done)) out.done = s.done.filter((x) => typeof x === 'string' && x.length < 80);
    if (typeof s.last === 'string' && byId.has(s.last)) out.last = s.last;
    if (s.migration && typeof s.migration === 'object') out.migration = s.migration;
    if (typeof s.updated === 'string') out.updated = s.updated;
    return out;
  }

  function load() {
    const raw = store.get(KEY);
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        if (parsed && parsed.schema === SCHEMA) return sanitize(parsed);
      } catch { /* fall through */ }
      // never discard progress silently: keep the unreadable value next to the new state
      store.set(`${KEY}:unreadable-backup`, raw);
    }
    const legacyRaw = store.get(LEGACY_KEY);
    if (legacyRaw) {
      try {
        const old = JSON.parse(legacyRaw);
        if (Array.isArray(old)) {
          const days = v1Days(old);
          const done = lessonsFromV1(days);
          const s = fresh();
          s.done = ordered(new Set(done));
          s.migration = { from: 'curriculum 1.0', at: new Date().toISOString(), oldDays: days.size,
                          newLessons: s.done.length, acknowledged: false };
          save(s);
          return s;
        }
      } catch { /* an unreadable v1 value is left alone */ }
    }
    return fresh();
  }

  function save(s) {
    s.updated = new Date().toISOString();
    return store.set(KEY, JSON.stringify(s));
  }

  let state = load();
  const doneSet = () => new Set(state.done);
  const isDone = (id) => state.done.includes(id);

  function setDone(id, value) {
    const set = doneSet();
    if (value) set.add(id); else set.delete(id);
    // keep ids from other curriculum versions; count only the current ones
    const unknown = state.done.filter((x) => !byId.has(x));
    state.done = ordered(set).concat(unknown);
    save(state);
  }

  function nextLesson() {
    const set = doneSet();
    if (state.last && byId.has(state.last) && !set.has(state.last)) return state.last;
    const start = state.last && byId.has(state.last) ? byId.get(state.last).index + 1 : 0;
    for (let i = start; i < lessons.length; i++) if (!set.has(lessons[i].id)) return lessons[i].id;
    for (let i = 0; i < start; i++) if (!set.has(lessons[i].id)) return lessons[i].id;
    return null;
  }

  // ------------------------------------------------------------ export / import

  function exportJson() {
    return JSON.stringify({
      format: FORMAT, schema: SCHEMA, curriculum: C.version,
      exported: new Date().toISOString(),
      completed: ordered(doneSet()),
      last: state.last,
    }, null, 2);
  }

  // returns { ids: [...], unknown: n, source: '...' } or throws Error with a readable message
  function parseImport(text) {
    let data;
    try { data = JSON.parse(text); } catch { throw new Error('the file is not valid JSON'); }
    if (Array.isArray(data)) {                               // a raw v1 localStorage value
      return { ids: lessonsFromV1(v1Days(data)), unknown: 0, last: null, source: 'curriculum 1.0 (day list)' };
    }
    if (!data || typeof data !== 'object') throw new Error('the file does not contain a progress object');
    if (data.format !== FORMAT) throw new Error('this is not a progress export from this course');
    if (!Array.isArray(data.completed)) throw new Error('the export has no list of completed lessons');
    if (data.schema === 1 || String(data.curriculum).startsWith('1')) {
      return { ids: lessonsFromV1(v1Days(data.completed)), unknown: 0, last: null, source: 'curriculum 1.0' };
    }
    if (data.schema !== SCHEMA) throw new Error(`unsupported export schema ${data.schema}`);
    const ids = data.completed.filter((x) => typeof x === 'string' && byId.has(x));
    return { ids, unknown: data.completed.length - ids.length,
             last: typeof data.last === 'string' && byId.has(data.last) ? data.last : null,
             source: `curriculum ${data.curriculum}` };
  }

  function applyImport(result, mode) {
    const set = mode === 'replace' ? new Set() : doneSet();
    result.ids.forEach((id) => set.add(id));
    state.done = ordered(set);
    if (result.last && (mode === 'replace' || !state.last)) state.last = result.last;
    save(state);
  }

  // ------------------------------------------------------------ shared ui

  function setupTheme() {
    const button = document.querySelector('.theme-toggle');
    if (!button) return;
    const order = ['auto', 'light', 'dark'];
    const apply = (t) => {
      if (t === 'auto') delete document.documentElement.dataset.theme;
      else document.documentElement.dataset.theme = t;
      button.textContent = `theme: ${t}`;
      button.setAttribute('aria-label', `color theme: ${t}. activate to change`);
    };
    let current = store.get(THEME_KEY) || 'auto';
    apply(current);
    button.addEventListener('click', () => {
      current = order[(order.indexOf(current) + 1) % order.length];
      store.set(THEME_KEY, current);
      apply(current);
    });
  }

  function announce(text) {
    const live = document.getElementById('live');
    if (live) { live.textContent = ''; window.setTimeout(() => { live.textContent = text; }, 30); }
  }

  function setupCopy() {
    document.querySelectorAll('button.code-copy').forEach((button) => {
      button.hidden = false;
      button.addEventListener('click', async () => {
        const code = button.closest('figure.code').querySelector('pre code').innerText;
        let ok = false;
        try { await navigator.clipboard.writeText(code); ok = true; } catch {
          const area = document.createElement('textarea');
          area.value = code; area.setAttribute('readonly', ''); area.style.position = 'fixed'; area.style.opacity = '0';
          document.body.appendChild(area); area.select();
          try { ok = document.execCommand('copy'); } catch { ok = false; }
          area.remove();
        }
        button.textContent = ok ? 'copied' : 'copy failed';
        announce(ok ? 'code copied to the clipboard' : 'could not copy the code');
        window.setTimeout(() => { button.textContent = 'copy'; }, 1600);
      });
    });
  }

  function setupSearch() {
    const input = document.getElementById('search-input');
    const list = document.getElementById('search-results');
    if (!input || !list) return;
    let index = null;
    const load = () => index || (index = fetch('/search-index.json').then((r) => r.json()).catch(() => []));
    const close = () => { list.hidden = true; input.setAttribute('aria-expanded', 'false'); };
    const render = async () => {
      const q = input.value.trim().toLowerCase();
      if (q.length < 2) { close(); return; }
      const terms = q.split(/\s+/);
      const items = (await load()).map((it) => {
        let score = 0;
        for (const t of terms) {
          const inTitle = it.title.toLowerCase().includes(t);
          const inRest = it.text.includes(t);
          if (!inTitle && !inRest) return null;
          score += inTitle ? 3 : 1;
        }
        return { it, score };
      }).filter(Boolean).sort((a, b) => b.score - a.score || a.it.day - b.it.day).slice(0, 10);
      list.innerHTML = '';
      if (!items.length) {
        const li = document.createElement('li');
        li.className = 'empty'; li.textContent = 'no matching lessons';
        list.appendChild(li);
      }
      for (const { it } of items) {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = `/day/${it.slug}/`;
        const day = document.createElement('span'); day.className = 'day'; day.textContent = `day ${it.slug}`;
        a.append(day, document.createTextNode(it.title));
        li.appendChild(a);
        list.appendChild(li);
      }
      list.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    };
    input.addEventListener('focus', load);
    input.addEventListener('input', render);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { close(); input.blur(); }
      if (e.key === 'ArrowDown') { const a = list.querySelector('a'); if (a) { e.preventDefault(); a.focus(); } }
      if (e.key === 'Enter') { const a = list.querySelector('a'); if (a) { e.preventDefault(); window.location.href = a.href; } }
    });
    list.addEventListener('keydown', (e) => {
      const links = [...list.querySelectorAll('a')];
      const i = links.indexOf(document.activeElement);
      if (e.key === 'ArrowDown' && i < links.length - 1) { e.preventDefault(); links[i + 1].focus(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); (i > 0 ? links[i - 1] : input).focus(); }
      if (e.key === 'Escape') { close(); input.focus(); }
    });
    document.addEventListener('click', (e) => { if (!e.target.closest('.search')) close(); });
  }

  // ------------------------------------------------------------ dashboard

  // links into the old single-page site (cpp.eigenomar.com/#day-12) land here
  function legacyRedirect() {
    const h = window.location.hash;
    let m = /^#day-(\d{2})$/.exec(h);
    if (m && C.legacy.v1.redirect[m[1]]) return dayHref(C.legacy.v1.redirect[m[1]]);
    m = /^#week-([1-8])$/.exec(h);
    if (m) {
      const first = String((+m[1] - 1) * 7 + 1).padStart(2, '0');
      const id = C.legacy.v1.redirect[first];
      return id ? `/#module-${byId.get(id).module}` : null;
    }
    const pages = { '#cheat-sheet': '/cheat-sheet/', '#references': '/references/', '#introduction': '/full/#introduction',
                    '#course-overview': '/full/#course-overview', '#table-of-contents': '/full/#table-of-contents',
                    '#progress-checklist': '/#curriculum' };
    return pages[h] || null;
  }

  function renderDashboard() {
    const set = doneSet();
    const total = lessons.length;
    const count = lessons.filter((l) => set.has(l.id)).length;
    const pct = total ? Math.round((count / total) * 100) : 0;
    const q = (sel) => document.querySelector(sel);
    q('#progress-count').textContent = `${count} of ${total}`;
    q('#progress-pct').textContent = `${pct}%`;
    q('#progress-bar').style.width = `${pct}%`;
    const bar = q('#progress-bar').parentElement;
    bar.setAttribute('aria-valuenow', String(pct));

    const next = nextLesson();
    const cont = q('#continue');
    if (next) {
      const l = byId.get(next);
      cont.href = dayHref(next);
      const verb = count === 0 && !state.last ? 'start with' : 'continue with';
      cont.textContent = `${verb} day ${l.slug}: ${l.title}`;
    } else {
      cont.href = '/full/';
      cont.textContent = 'every lesson is complete: browse the full course';
    }
    const last = q('#last-visited');
    if (state.last && byId.has(state.last)) {
      const l = byId.get(state.last);
      last.innerHTML = '';
      last.append('last visited: ');
      const a = document.createElement('a'); a.href = dayHref(l.id); a.textContent = `day ${l.slug}: ${l.title}`;
      last.appendChild(a);
      last.hidden = false;
    } else last.hidden = true;

    document.querySelectorAll('.lesson-list li[data-id]').forEach((li) => {
      const done = set.has(li.dataset.id);
      li.classList.toggle('done', done);
      const s = li.querySelector('.status');
      s.textContent = done ? '✓' : '·';
      s.setAttribute('aria-label', done ? 'completed' : 'not completed');
    });
    document.querySelectorAll('.module[data-module]').forEach((mod) => {
      const ids = C.modules.find((m) => m.id === mod.dataset.module).lessons;
      const n = ids.filter((id) => set.has(id)).length;
      mod.querySelector('.count').textContent = `${n} / ${ids.length}`;
      mod.querySelector('.bar > span').style.width = `${Math.round((n / ids.length) * 100)}%`;
    });

    const note = q('#migration-note');
    if (state.migration && !state.migration.acknowledged) {
      q('#migration-text').textContent =
        `your progress from the original 56-day course was carried over: ${state.migration.oldDays} completed days ` +
        `became ${state.migration.newLessons} completed lessons. lessons with substantially new material, ` +
        'including the new reviews, start unchecked.';
      note.hidden = false;
    } else note.hidden = true;
  }

  function setupDashboard() {
    const target = legacyRedirect();
    if (target) { window.location.replace(target); return; }
    renderDashboard();

    // expand the module someone linked to, or else the one holding the next lesson
    const openModule = (id) => { const d = document.getElementById(`module-${id}`); if (d) d.open = true; };
    const fromHash = () => { if (/^#module-/.test(window.location.hash)) openModule(window.location.hash.slice(8)); };
    const next = nextLesson();
    if (/^#module-/.test(window.location.hash)) fromHash();
    else if (next) openModule(byId.get(next).module);
    window.addEventListener('hashchange', fromHash);

    document.getElementById('migration-dismiss').addEventListener('click', () => {
      state.migration.acknowledged = true; save(state); renderDashboard();
    });

    const status = document.getElementById('progress-status');
    const say = (text, error = false) => { status.textContent = text; status.classList.toggle('error', error); };

    document.getElementById('export-progress').addEventListener('click', () => {
      const blob = new Blob([exportJson()], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `modern-cpp-course-progress-${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a); a.click(); a.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      say(`exported ${state.done.filter((id) => byId.has(id)).length} completed lessons`);
    });

    const file = document.getElementById('import-file');
    document.getElementById('import-progress').addEventListener('click', () => file.click());
    file.addEventListener('change', async () => {
      const f = file.files && file.files[0];
      file.value = '';
      if (!f) return;
      if (f.size > MAX_IMPORT_BYTES) { say('that file is too large to be a progress export', true); return; }
      try {
        const result = parseImport(await f.text());
        const mode = document.querySelector('input[name="import-mode"]:checked').value;
        applyImport(result, mode);
        renderDashboard();
        const extra = result.unknown ? `; ${result.unknown} unknown lesson ids were ignored` : '';
        say(`imported ${result.ids.length} completed lessons from ${result.source} (${mode})${extra}`);
      } catch (err) {
        say(`import failed: ${err.message}`, true);
      }
    });

    document.getElementById('reset-progress').addEventListener('click', () => {
      if (!window.confirm('clear all progress in this browser? export it first if you may want it back.')) return;
      const migration = state.migration;
      state = fresh();
      if (migration) state.migration = Object.assign({}, migration, { acknowledged: true });
      save(state);
      renderDashboard();
      say('progress cleared');
    });
  }

  // ------------------------------------------------------------ lesson reader

  function setupLesson(id) {
    state.last = id;          // opening a lesson records the visit, never completion
    save(state);
    const button = document.querySelector('.mark-done');
    if (!button) return;
    const render = () => {
      const done = isDone(id);
      button.setAttribute('aria-pressed', String(done));
      button.textContent = done ? 'completed ✓ (undo)' : 'mark as completed';
    };
    button.hidden = false;
    render();
    button.addEventListener('click', () => {
      setDone(id, !isDone(id));
      render();
      announce(isDone(id) ? 'lesson marked as completed' : 'lesson marked as not completed');
    });
  }

  // ------------------------------------------------------------ full course

  function setupFull() {
    const set = doneSet();
    document.querySelectorAll('.toc li[data-id]').forEach((li) => {
      if (set.has(li.dataset.id)) li.insertAdjacentText('beforeend', ' ✓');
    });
    const expand = document.getElementById('expand-deeper');
    if (expand) {
      expand.hidden = false;
      expand.addEventListener('click', () => {
        const all = [...document.querySelectorAll('details.deeper')];
        const open = !all.every((d) => d.open);
        all.forEach((d) => { d.open = open; });
        expand.textContent = open ? 'collapse optional sections' : 'expand optional sections';
      });
    }
  }

  // ------------------------------------------------------------ start

  setupTheme();
  setupCopy();
  setupSearch();
  const page = document.body.dataset.page;
  if (page === 'dashboard') setupDashboard();
  if (page === 'lesson') setupLesson(document.body.dataset.lesson);
  if (page === 'full') setupFull();

  // exposed for tests and for debugging from the console
  window.courseProgress = {
    load, exportJson, parseImport, lessonsFromV1, v1Days, nextLesson,
    importText(text, mode) { const r = parseImport(text); applyImport(r, mode); return r; },
    get state() { return state; },
  };
})();
