/* Session and dismissal checks without opening a browser. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { parseHTML } = require('linkedom');
const source = fs.readFileSync(path.join(__dirname, '../js/splash.js'), 'utf8');
const storage = () => {
  const values = new Map();
  return { getItem: key => values.get(key) ?? null, setItem: (key, value) => values.set(key, value), removeItem: key => values.delete(key) };
};
function visit(sessionStorage, reduced = false, { navigation = 'navigate', now = 100000, pathname = '/bifrost/', search = '' } = {}) {
  const { document, Event } = parseHTML('<html><body><div id="startupSplash" hidden></div><main></main></body></html>');
  const timers = new Map();
  const events = new Map();
  const shortcuts = [];
  const addEventListener = document.addEventListener.bind(document);
  document.addEventListener = (name, fn, options) => {
    if (name === 'keydown' && options?.capture) shortcuts.push(fn);
    addEventListener(name, fn, options);
  };
  let nextTimer = 0;
  const window = {
    matchMedia: () => ({ matches: reduced }),
    addEventListener: (name, handler) => events.set(name, handler),
    removeEventListener: name => events.delete(name)
  };
  vm.runInNewContext(source, {
    document, window, sessionStorage, location: { pathname, search }, Date: { now: () => now },
    performance: { now: () => 0, getEntriesByType: () => [{ type: navigation }] },
    setTimeout: (fn, delay) => { timers.set(++nextTimer, { fn, delay }); return nextTimer; },
    clearTimeout: id => timers.delete(id)
  });
  const runAfter = delay => {
    const [id, timer] = [...timers].find(([, timer]) => timer.delay === delay);
    timers.delete(id);
    timer.fn();
  };
  // Trusted keyboard input is simulated at the registered handler boundary; no browser is launched.
  const keydown = overrides => {
    const event = { key: 'F5', ctrlKey: false, shiftKey: false, metaKey: false, altKey: false,
      isTrusted: true, defaultPrevented: false, repeat: false, ...overrides };
    shortcuts.forEach(fn => fn(event));
    return event;
  };
  return { document, Event, timers, events, runAfter, keydown, active: () => document.documentElement.classList.contains('splash-active') };
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
  assert.doesNotThrow(() => unavailable.keydown({ ctrlKey: true }), 'Storage errors never interfere with native refresh');
}
console.log('PASS: intro first visit, repeat visits, fresh session, back/forward cache, reduced motion and unavailable storage.');

const replayKey = 'bifrost_splash_replay_v1';
first.keydown({ ctrlKey: true });
assert.equal(visit(session, false, { navigation: 'reload', now: 101000 }).active(), true,
  'Shortcut listener remains installed after the finished intro removes its dismissal listeners');
for (const shortcut of [
  { ctrlKey: true }, { shiftKey: true }, { ctrlKey: true, shiftKey: true },
  { key: 'R', ctrlKey: true, shiftKey: true }, { key: 'r', metaKey: true, shiftKey: true }
]) {
  const data = storage();
  visit(data);
  const page = visit(data);
  assert.equal(page.active(), false, 'Previously seen intro stays skipped before the shortcut');
  const event = page.keydown(shortcut);
  assert.equal(event.defaultPrevented, false, 'Native hard reload is not intercepted');
  assert.ok(data.getItem(replayKey), 'Replay is armed even after the session guard skipped the intro');
  const replay = visit(data, false, { navigation: 'reload', now: 101000 });
  assert.equal(replay.active(), true, 'Hard-reload shortcut replays the intro');
  assert.equal(data.getItem(replayKey), null, 'Replay request is consumed once');
  assert.equal(visit(data, false, { navigation: 'reload' }).active(), false, 'Following normal reload skips again');
}
for (const key of [{}, { key: 'r', ctrlKey: true }, { key: 'r', metaKey: true }]) {
  const data = storage(); visit(data); visit(data).keydown(key);
  assert.equal(visit(data, false, { navigation: 'reload' }).active(), false, 'Normal F5/Ctrl+R does not replay');
}
for (const override of [{ isTrusted: false }, { defaultPrevented: true }, { repeat: true }, { altKey: true }]) {
  const data = storage(); visit(data); visit(data).keydown({ ctrlKey: true, ...override });
  assert.equal(data.getItem(replayKey), null, 'Synthetic, cancelled, repeated or unrelated shortcut does not arm replay');
}
for (const options of [
  { navigation: 'navigate' }, { navigation: 'back_forward' },
  { navigation: 'reload', pathname: '/bifrost/index.html' },
  { navigation: 'reload', now: 131000 }, { navigation: 'reload', now: 99000 }
]) {
  const data = storage(); visit(data); visit(data).keydown({ ctrlKey: true });
  assert.equal(visit(data, false, options).active(), false, 'Stale, different-page or non-reload requests are ignored');
  assert.equal(data.getItem(replayKey), null);
}
const cancelledReplay = storage(); visit(cancelledReplay);
const page = visit(cancelledReplay);
page.keydown({ ctrlKey: true });
page.keydown({});
assert.equal(cancelledReplay.getItem(replayKey), null, 'Normal refresh cancels a pending shortcut marker');
const brokenReplay = storage(); visit(brokenReplay); brokenReplay.setItem(replayKey, '{broken');
assert.equal(visit(brokenReplay, false, { navigation: 'reload' }).active(), false, 'Corrupt replay data is harmless');
const reducedReplay = storage(); visit(reducedReplay); visit(reducedReplay).keydown({ ctrlKey: true });
const reducedHard = visit(reducedReplay, true, { navigation: 'reload' });
assert.equal(reducedHard.active(), true);
reducedHard.document.dispatchEvent(new reducedHard.Event('DOMContentLoaded'));
reducedHard.runAfter(150); reducedHard.runAfter(0);
assert.equal(reducedHard.active(), false, 'Replayed intro respects reduced motion');
console.log('PASS: trusted hard-reload shortcuts, one-shot replay, normal refresh, invalid/stale markers and reduced motion.');
