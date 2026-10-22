/* Session and dismissal checks without opening a browser. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { parseHTML } = require('linkedom');
const source = fs.readFileSync(path.join(__dirname, '../js/splash.js'), 'utf8');
const storage = () => {
  const values = new Map();
  return { getItem: key => values.get(key) ?? null, setItem: (key, value) => values.set(key, value) };
};
function visit(sessionStorage, reduced = false) {
  const { document, Event } = parseHTML('<html><body><div id="startupSplash" hidden></div><main></main></body></html>');
  const timers = new Map();
  const events = new Map();
  let nextTimer = 0;
  const window = {
    matchMedia: () => ({ matches: reduced }),
    addEventListener: (name, handler) => events.set(name, handler),
    removeEventListener: name => events.delete(name)
  };
  vm.runInNewContext(source, {
    document, window, sessionStorage, performance: { now: () => 0 },
    setTimeout: (fn, delay) => { timers.set(++nextTimer, { fn, delay }); return nextTimer; },
    clearTimeout: id => timers.delete(id)
  });
  const runAfter = delay => {
    const [id, timer] = [...timers].find(([, timer]) => timer.delay === delay);
    timers.delete(id);
    timer.fn();
  };
  return { document, Event, timers, events, runAfter, active: () => document.documentElement.classList.contains('splash-active') };
}
const session = storage();
const first = visit(session);
assert.equal(first.active(), true, 'First visit plays the intro');
first.document.dispatchEvent(new first.Event('DOMContentLoaded'));
assert.equal(first.document.querySelector('main').inert, true);
first.runAfter(2600);
first.runAfter(400);
assert.equal(first.active(), false);
assert.equal(first.document.querySelector('main').inert, undefined, 'Original interaction state is restored');
assert.equal(first.document.getElementById('startupSplash'), null);
for (const reason of ['refresh', 'return from a course']) {
  const repeat = visit(session);
  assert.equal(repeat.active(), false, reason);
  assert.equal(repeat.timers.size, 0, 'Repeated visit has no intro delay');
  assert.equal(repeat.events.size, 0);
}
assert.equal(visit(storage()).active(), true, 'A fresh tab session plays the intro');
const restored = visit(storage());
restored.events.get('pageshow')({ persisted: true });
assert.equal(restored.active(), false, 'Back/forward cache does not retain the overlay');
const reduced = visit(storage(), true);
reduced.document.dispatchEvent(new reduced.Event('DOMContentLoaded'));
reduced.runAfter(150);
reduced.runAfter(0);
assert.equal(reduced.active(), false, 'Reduced motion still dismisses correctly');
for (const sessionStorage of [
  { getItem() { throw new Error('denied'); } },
  { getItem: () => null, setItem() { throw new Error('denied'); } }
]) {
  const unavailable = visit(sessionStorage);
  assert.equal(unavailable.active(), false, 'Unavailable storage does not block the page');
  assert.equal(unavailable.timers.size, 0);
}
console.log('PASS: intro first visit, repeat visits, fresh session, back/forward cache, reduced motion and unavailable storage.');
