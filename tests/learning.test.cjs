/* DOM + storage integration tests. These do not start a browser or HTTP server. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { parseHTML } = require('linkedom');
const ROOT = path.resolve(__dirname, '..');
const KEY = 'bifrost_progress_v2';
const LEGACY = 'whl_progress_v1';
let checks = 0;
function check(condition, message) { assert.ok(condition, message); checks++; }
class Storage {
  constructor(seed = {}, { denyRead = false, denyWrite = false } = {}) { this.map = new Map(Object.entries(seed)); this.denyRead = denyRead; this.denyWrite = denyWrite; }
  getItem(key) { if (this.denyRead) throw new Error('denied'); return this.map.get(key) ?? null; }
  setItem(key, value) { if (this.denyWrite) throw new Error('quota'); this.map.set(key, String(value)); }
}
function openPage(relative, search = '', storage = new Storage()) {
  const { document, Event, CustomEvent } = parseHTML(fs.readFileSync(path.join(ROOT, relative), 'utf8'));
  const handlers = new Map();
  const window = {
    document, matchMedia: () => ({ matches: false }),
    addEventListener(type, fn) { if (!handlers.has(type)) handlers.set(type, []); handlers.get(type).push(fn); },
    dispatchEvent(event) { for (const fn of handlers.get(event.type) || []) fn(event); }
  };
  window.parent = window;
  const context = vm.createContext({ window, document, localStorage: storage, location: { search, origin: 'https://example.test' }, Event, CustomEvent, URLSearchParams, URL, Blob, console, setTimeout: () => 0, navigator: { clipboard: { writeText: async () => {} } } });
  for (const file of ['theme.js', 'curriculum.js', 'progress.js', relative === 'index.html' ? 'app.js' : 'learning.js']) vm.runInContext(fs.readFileSync(path.join(ROOT, 'js', file), 'utf8'), context, { filename: file });
  return { document, window, storage, context, Event, progress: window.BifrostProgress, courses: window.BifrostCourses, relative };
}
function verifyLocalLinks(page) {
  for (const element of page.document.querySelectorAll('[href],[src]')) {
    const value = element.getAttribute('href') || element.getAttribute('src');
    if (!value || /^(https?:|data:|mailto:)/.test(value)) continue;
    const url = new URL(value, `https://example.test/bifrost/${page.relative}`);
    check(url.pathname.startsWith('/bifrost/'), `Project-relative URL: ${value}`);
    let relative = decodeURIComponent(url.pathname.slice('/bifrost/'.length));
    if (relative.endsWith('/')) relative += 'index.html';
    check(fs.existsSync(path.join(ROOT, relative)), `Missing local asset: ${relative}`);
    if (url.hash && relative === page.relative) check(!!page.document.getElementById(url.hash.slice(1)), `Missing anchor ${value}`);
    if (url.searchParams.has('id')) {
      const track = relative.split('/')[1];
      check(page.courses[track].modules.some(m => m.lessons.some(l => l.id === url.searchParams.get('id'))), `Unknown lesson link: ${value}`);
    }
  }
}
const home = openPage('index.html');
const courses = Object.values(home.courses);
check(courses.length === 9, 'Nine courses');
check(home.document.querySelectorAll('a[data-map-track]').length === 9, 'Nine semantic map links');
check(home.document.querySelectorAll('.catalog-card').length === 9, 'Nine catalogue cards');
verifyLocalLinks(home);
const ids = new Set();
let lessonCount = 0;
for (const course of courses) {
  const overview = openPage(`tracks/${course.id}/index.html`);
  check(overview.document.querySelectorAll('.module-card').length === course.modules.length, 'All modules render');
  verifyLocalLinks(overview);
  for (const lesson of course.modules.flatMap(m => m.lessons)) {
    check(!ids.has(lesson.id), `Unique ID ${lesson.id}`); ids.add(lesson.id);
    check(lesson.id.startsWith(`${course.id}.`), 'ID owns its course');
    check(lesson.concepts.length >= 2 && lesson.checks.length >= 2 && lesson.task && lesson.hint, 'Teaching + task + verification');
    const page = openPage(`tracks/${course.id}/lesson.html`, `?id=${encodeURIComponent(lesson.id)}`);
    check(page.document.querySelector('.lesson-heading h1').textContent === lesson.title, 'Deep link renders correct lesson');
    check(page.document.querySelector('#exampleCode').textContent === lesson.code, 'Code escaped without corruption');
    check(page.document.querySelectorAll('.side-lesson[aria-current="page"]').length === 1, 'Current lesson accessible');
    const elements = [...page.document.querySelectorAll('[id]')].map(el => el.id);
    check(new Set(elements).size === elements.length, 'No duplicate DOM IDs');
    verifyLocalLinks(page);
    lessonCount++;
  }
}
check(lessonCount === 62, '62 authored lessons');

// Evaluate the real desktop CSS coordinates and real SVG endpoints, not a second layout fixture.
const desktopCSS = fs.readFileSync(path.join(ROOT, 'css/mindmap.css'), 'utf8').split('@media(min-width:901px){')[1].split('\n}')[0];
const widthOfCard = 216, heightOfCard = 116;
function rectangles(width) {
  const stageWidth = Math.min(1000, width - 48);
  return Object.fromEntries(courses.map(c => {
    const rule = desktopCSS.match(new RegExp(`\\.node-${c.id}\\{([^}]+)\\}`))[1];
    const top = Number(rule.match(/top:(\d+)px/)[1]);
    let left = stageWidth / 2 - widthOfCard / 2;
    const offset = rule.match(/(left|right):calc\(50% ([+-]) (\d+)px\)/);
    if (offset) {
      const value = stageWidth / 2 + (offset[2] === '+' ? 1 : -1) * Number(offset[3]);
      left = offset[1] === 'left' ? value : stageWidth - value - widthOfCard;
    }
    return [c.id, { left, right: left + widthOfCard, top, bottom: top + heightOfCard, stageWidth }];
  }));
}
for (const width of [901, 1024, 1440, 1885]) {
  const rects = Object.values(rectangles(width));
  for (let i = 0; i < rects.length; i++) {
    const a = rects[i];
    check(a.left >= 0 && a.right <= a.stageWidth && a.bottom <= 760, `Card visible at ${width}`);
    const closestX = Math.max(a.left, Math.min(a.right, a.stageWidth / 2));
    const closestY = Math.max(a.top, Math.min(a.bottom, 380));
    check(Math.hypot(closestX - a.stageWidth / 2, closestY - 380) > 85, `Core clear at ${width}`);
    for (const b of rects.slice(i + 1)) check(a.right <= b.left || b.right <= a.left || a.bottom <= b.top || b.bottom <= a.top, `Cards do not overlap at ${width}`);
  }
}
const lineOwners = { cyan: 'foundation', blue: 'web', violet: 'pwn', red: 'rev', green: 'forensic', pink: 'crypto', orange: 'misc', amber: 'network', sky: 'cloud' };
const rects = rectangles(1048); // full 1000px stage, matching SVG viewBox
for (const line of home.document.querySelectorAll('.synapse:not(.faint)')) {
  const color = [...line.classList].find(name => lineOwners[name]);
  const coordinates = line.getAttribute('d').match(/\d+(?:\.\d+)?/g).map(Number);
  const [startX, startY] = coordinates;
  const endX = coordinates.length === 3 ? startX : coordinates.at(-2), endY = coordinates.at(-1);
  check(Math.abs(Math.hypot(startX - 500, startY - 380) - 85) < 3, 'Connector starts at core');
  const r = rects[lineOwners[color]];
  check(endX >= r.left && endX <= r.right && endY >= r.top && endY <= r.bottom && Math.min(Math.abs(endX-r.left), Math.abs(endX-r.right), Math.abs(endY-r.top), Math.abs(endY-r.bottom)) < 0.1, `Connector touches ${color} card`);
}

const store = new Storage();
const lesson = openPage('tracks/foundation/lesson.html', '?id=foundation.python-values', store);
const button = lesson.document.getElementById('completeLesson');
const hint = lesson.document.querySelector('.hint');
hint.setAttribute('open', '');
button.click();
check(button.getAttribute('aria-pressed') === 'true', 'Completion button toggles');
check(lesson.progress.has('foundation.python-values'), 'Completion stored by ID');
check(hint.hasAttribute('open') && button === lesson.document.getElementById('completeLesson'), 'Completion preserves DOM, open hints and focus target');
check(lesson.document.querySelector('[data-count]').textContent.includes('1 / 10'), 'Course total updates');
const reload = openPage('tracks/foundation/index.html', '', store);
check(reload.document.querySelector('[data-count]').textContent.includes('1 / 10'), 'Reload retains completion');
check(reload.document.querySelector('#continueLearning').getAttribute('href').includes('foundation.environment'), 'Completed last lesson does not skip first missing lesson');
const homepage = openPage('index.html', '', store);
check(homepage.document.querySelector('#catalogSummary').textContent.includes('1 / 62'), 'Homepage aggregate');

const legacyState = { foundation: [0, 1, 2, 3, 4, 5, 6, 6, 999, -1, '1'], crypto: [0, 1, 2, 3, 4, 5, 6], network: [0, 1, 2] };
const oldStore = new Storage({ [LEGACY]: JSON.stringify(legacyState) });
const migrated = openPage('tracks/crypto/index.html', '', oldStore);
check(migrated.progress.has('misc.automation') && migrated.progress.has('misc.triage') && migrated.progress.has('misc.writeup'), 'Crypto/Misc split migration');
check(!migrated.progress.has('foundation.python-values') && !migrated.progress.has('network.capstone'), 'Expanded lessons not automatically completed');
check(migrated.progress.has('network.pcap'), 'Equivalent network lesson migrated');
check(oldStore.getItem(LEGACY) === JSON.stringify(legacyState), 'Original legacy record untouched');
migrated.progress.set('misc.triage', false);
const remigrated = openPage('tracks/misc/index.html', '', oldStore);
check(!remigrated.progress.has('misc.triage'), 'Migration runs only once, unchecking persists');
remigrated.courses.misc.modules[0].lessons.reverse();
check(remigrated.progress.has('misc.automation'), 'Ordering does not change saved IDs');
check(remigrated.progress.legacyCount() === 17, 'Legacy history retained and sanitized');

const backup = lesson.progress.export();
const imported = openPage('tracks/web/index.html');
imported.progress.set('web.sql', true);
imported.progress.import(backup);
check(imported.progress.has('foundation.python-values') && imported.progress.has('web.sql'), 'Backup merges without clearing current completion');
for (const text of ['null', '{}', '{"version":1,"completed":{}}', '{"version":2,"completed":[]}', 'invalid', 'x'.repeat(1000001)]) {
  assert.throws(() => imported.progress.import(text)); checks++;
}
imported.progress.import('{"version":2,"completed":{"<script>alert(1)</script>":true,"cloud.iam":true}}');
check(imported.progress.has('cloud.iam') && !imported.progress.export().includes('<script>'), 'Imported IDs cannot inject content');

const otherTab = JSON.parse(store.getItem(KEY));
otherTab.completed['crypto.hash'] = true;
store.setItem(KEY, JSON.stringify(otherTab));
lesson.window.dispatchEvent({ type: 'storage', key: KEY, newValue: store.getItem(KEY) });
check(lesson.progress.has('crypto.hash'), 'Other tab changes loaded');
lesson.progress.set('foundation.paths', true);
check(JSON.parse(store.getItem(KEY)).completed['crypto.hash'], 'Editing one lesson preserves other tab work');
otherTab.completed['forensic.logs'] = true;
store.setItem(KEY, JSON.stringify(otherTab));
lesson.window.dispatchEvent({ type: 'pageshow', persisted: true });
check(lesson.progress.has('forensic.logs'), 'Back/forward cached page refreshes progress');

for (const failure of [{ denyRead: true }, { denyWrite: true }]) {
  const blocked = openPage('tracks/web/lesson.html', '?id=web.sql', new Storage({}, failure));
  blocked.document.getElementById('completeLesson').click();
  check(blocked.progress.has('web.sql') && !blocked.progress.available(), 'Storage failure keeps in-memory work');
  check(blocked.document.querySelector('#completionFeedback').textContent.includes('저장'), 'Storage failure shown to learner');
  check(JSON.parse(blocked.progress.export()).completed['web.sql'], 'Failed-save work can be exported');
}
const corruptStore = new Storage({ [KEY]: '{broken', [LEGACY]: '{}' });
const corrupt = openPage('tracks/web/index.html', '', corruptStore);
corrupt.progress.set('web.sql', true);
check(corruptStore.getItem(KEY) === '{broken', 'Unreadable saved data is not overwritten silently');
corrupt.progress.import(backup);
check(corrupt.progress.available() && corrupt.progress.has('foundation.python-values'), 'Explicit valid backup repairs unreadable storage');

for (const search of ['', '?id=unknown', '?id=%3Cscript%3Ealert(1)%3C/script%3E', '?id=cloud.iam']) {
  const missing = openPage('tracks/web/lesson.html', search);
  check(!!missing.document.querySelector('.not-found') && !missing.document.querySelector('script:not([src])'), 'Invalid/cross-course ID gives safe recovery');
}
const theme = openPage('tracks/cloud/index.html');
theme.document.getElementById('themeToggle').click();
check(theme.document.documentElement.dataset.theme === 'dark', 'Shared theme works on course pages');
const guide = parseHTML(fs.readFileSync(path.join(ROOT, 'guides/linux.html'), 'utf8')).document;
const returns = guide.querySelectorAll('a[href="../index.html#study"]');
check(returns.length === 2, 'Standalone Linux guide has working return links');
for (const a of returns) {
  const standalone = { window: {} }; standalone.window.parent = standalone.window;
  check(vm.runInNewContext(`(function(){${a.getAttribute('onclick')}})()`, standalone) === undefined, 'Standalone return follows its real href');
  let closed = false;
  const embedded = { window: { parent: { showMainGuide: () => { closed = true; } } } };
  check(vm.runInNewContext(`(function(){${a.getAttribute('onclick')}})()`, embedded) === false && closed, 'Embedded guide closes overlay');
}
console.log(`PASS: ${checks} checks; 9 courses and ${lessonCount} lesson deep links; migration, backup, storage failures and navigation.`);
