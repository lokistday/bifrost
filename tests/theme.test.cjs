/* Fixed dark appearance, storage independence and readable shared colors. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { parseHTML } = require('linkedom');
const ROOT = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(ROOT, name), 'utf8');
const walk = folder => fs.readdirSync(path.join(ROOT, folder), { withFileTypes: true }).flatMap(item =>
  item.isDirectory() ? walk(`${folder}/${item.name}`) : [`${folder}/${item.name}`]);
const pages = ['index.html', ...['fields', 'tracks', 'paths', 'learn', 'projects', 'exams', 'guides'].flatMap(walk)]
  .filter(name => name.endsWith('.html'));
for (const name of pages) {
  const document = parseHTML(read(name)).document;
  assert.equal(document.documentElement.dataset.theme, 'dark', `${name}: dark before JavaScript runs`);
  assert.equal(document.querySelector('#themeToggle,.theme-toggle,.project-theme-toggle'), null, `${name}: no theme control`);
  assert.equal(document.querySelectorAll('.editorial-header .editorial-nav').length, 1, `${name}: one shared site menu`);
  assert.ok(document.querySelector('link[href*="/charcoal.css"]'), `${name}: shared palette and styling are linked`);
  const expectedColor = '#06070a';
  assert.equal(document.querySelector('meta[name="theme-color"]').getAttribute('content'), expectedColor, `${name}: browser chrome matches`);
  assert.match(document.querySelector('script[src*="/theme.js"]').getAttribute('src'), /\?v=/, `${name}: cached theme controller is replaced`);
}
for (const embedded of [false, true]) {
  // Old preferences and a light OS must never select a different palette or touch progress.
  const document = parseHTML('<html data-default-theme="light"><head><meta name="theme-color" content="#fff"></head></html>').document;
  const untouchedStorage = {
    getItem() { throw Error('Appearance must not read saved preferences or progress'); },
    setItem() { throw Error('Appearance must not write learning data'); },
    removeItem() { throw Error('Appearance must not remove learning data'); }
  };
  const handlers = {};
  const window = { matchMedia: () => ({ matches: false }), addEventListener: (type, handler) => { handlers[type] = handler; } };
  window.parent = embedded ? { postMessage() { throw Error('An embedded guide needs no theme handshake'); } } : window;
  vm.runInNewContext(read('js/theme.js'), { document, window, localStorage: untouchedStorage });
  handlers.storage?.({ key: 'bifrost_theme_v1', newValue: 'light' });
  handlers.message?.({ data: { type: 'bifrost-theme-change', theme: 'light' } });
  assert.equal(document.documentElement.dataset.theme, 'dark');
  assert.equal(document.documentElement.style.colorScheme, 'dark');
  assert.equal(document.querySelector('meta[name="theme-color"]').content, '#06070a');
}
const CSSOM = require(require.resolve('cssom', { paths: [path.dirname(require.resolve('linkedom'))] }));
const sheet = CSSOM.parse(read('css/theme.css'));
const tokens = sheet.cssRules.find(rule => rule.selectorText === ':root').style;
assert.equal(tokens.getPropertyValue('color-scheme'), 'dark');
assert.ok(!read('css/theme.css').includes('data-theme="light"'));
function luminance(hex) {
  const rgb = hex.trim().slice(1).match(/../g).map(value => parseInt(value, 16) / 255)
    .map(value => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4);
  return .2126 * rgb[0] + .7152 * rgb[1] + .0722 * rgb[2];
}
for (const foreground of ['ink', 'ink-soft', 'muted', 'teal', 'blue', 'purple', 'amber',
  ...['cyan', 'blue', 'green', 'violet', 'red', 'pink', 'amber', 'orange', 'sky'].map(name => `map-${name}`)]) {
  for (const background of ['paper', 'surface', 'surface-raised', 'surface-soft']) {
    const a = luminance(tokens.getPropertyValue(`--${foreground}`));
    const b = luminance(tokens.getPropertyValue(`--${background}`));
    assert.ok((Math.max(a, b) + .05) / (Math.min(a, b) + .05) >= 4.5, `${foreground} on ${background}: readable normal text`);
  }
}
console.log(`PASS: ${pages.length} dark-only pages, cached-light/embedded behavior, untouched storage and shared text contrast.`);
