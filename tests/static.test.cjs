/* Build output, project-relative navigation, CSS and sharing assets. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { parseHTML } = require('linkedom');
const ROOT = path.resolve(__dirname, '..');
const CSSOM = require(require.resolve('cssom', { paths: [path.dirname(require.resolve('linkedom'))] }));
let checks = 0;
const check = (value, message) => { assert.ok(value, message); checks++; };
const walk = directory => fs.readdirSync(directory, { withFileTypes: true }).flatMap(item =>
  item.isDirectory() ? walk(path.join(directory, item.name)) : [path.join(directory, item.name)]);
const htmlFiles = ['index.html', ...walk(path.join(ROOT, 'tracks')).filter(file => file.endsWith('.html')).map(file => path.relative(ROOT, file)), 'guides/linux.html'];
const documents = new Map(htmlFiles.map(file => [path.resolve(ROOT, file), parseHTML(fs.readFileSync(path.join(ROOT, file), 'utf8')).document]));
for (const [file, doc] of documents) {
  for (const element of doc.querySelectorAll('[href],[src]')) {
    const value = element.getAttribute('href') || element.getAttribute('src');
    if (!value || /^(https?:|data:|mailto:)/.test(value)) continue;
    const url = new URL(value, `https://example.test/bifrost/${path.relative(ROOT, file).replaceAll('\\', '/')}`);
    check(url.pathname.startsWith('/bifrost/'), `Link stays inside project: ${value}`);
    let name = decodeURIComponent(url.pathname.slice('/bifrost/'.length));
    if (name.endsWith('/')) name += 'index.html';
    const target = path.resolve(ROOT, name);
    check(fs.existsSync(target), `Static link exists: ${value} in ${file}`);
    if (url.hash && documents.has(target)) {
      check(documents.get(target).getElementById(decodeURIComponent(url.hash.slice(1))), `Static anchor exists: ${value} in ${file}`);
    }
  }
}
for (const file of ['main.css', 'theme.css', 'mindmap.css', 'learning.css', 'visuals.css', 'linux-guide.css', 'splash.css', 'overlays.css']) {
  const source = fs.readFileSync(path.join(ROOT, 'css', file), 'utf8');
  check(!/var\([^)]*\)[\da-f]{2,}/i.test(source), `No malformed color suffix: ${file}`);
  check(CSSOM.parse(source).cssRules.length > 0, `Stylesheet parses: ${file}`);
}
const main = fs.readFileSync(path.join(ROOT, 'css/main.css'), 'utf8');
check(!/\.(?:phase|track-button|track-detail|lesson-plan|field-choice)\b/.test(main), 'Retired homepage component rules removed');
check(!/html\[data-theme/.test(main), 'Theme overrides centralized');
const map = CSSOM.parse(fs.readFileSync(path.join(ROOT, 'css/mindmap.css'), 'utf8'));
const rootSelectors = map.cssRules.filter(rule => rule.selectorText).map(rule => rule.selectorText);
check(new Set(rootSelectors).size === rootSelectors.length, 'Mindmap root selectors have one definition');

const png = fs.readFileSync(path.join(ROOT, 'og-image.png'));
check(png.subarray(0, 8).equals(Buffer.from([137,80,78,71,13,10,26,10])), 'Sharing image is a PNG');
check(png.readUInt32BE(16) === 1200 && png.readUInt32BE(20) === 630, 'Sharing image has promised dimensions');
const home = documents.get(path.join(ROOT, 'index.html'));
check(home.querySelector('meta[property="og:image"]').content.endsWith('/bifrost/og-image.png'), 'Sharing image URL matches published path');
const sitemap = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8');
check((sitemap.match(/<loc>/g) || []).length === 73, 'Sitemap includes home, Linux guide, 9 courses and 62 lessons');
check(!sitemap.includes('lesson.html?id='), 'Sitemap uses permanent static pages');

const workflow = fs.readFileSync(path.join(ROOT, '.github/workflows/pages.yml'), 'utf8');
check(workflow.includes('needs: verify') && workflow.includes('pnpm test') && workflow.includes('python tests/labs_test.py'), 'Deployment requires teaching and lab verification');
check(workflow.includes('path: _site') && !workflow.includes("path: '.'"), 'Deploy only packaged runtime assets');
const template = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8');
check((template.match(/\{\{MAP_NODES\}\}/g) || []).length === 1, 'Homepage has one authored map placeholder');
console.log(`PASS: ${checks} static asset, link, CSS, metadata and deployment contract checks.`);
