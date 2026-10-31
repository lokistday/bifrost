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
const htmlFiles = ['index.html', ...['tracks','guides','learn','projects','paths'].flatMap(folder => walk(path.join(ROOT, folder))).filter(file => file.endsWith('.html')).map(file => path.relative(ROOT, file))];
const documents = new Map(htmlFiles.map(file => [path.resolve(ROOT, file), parseHTML(fs.readFileSync(path.join(ROOT, file), 'utf8')).document]));
const illustratedAssets = new Set();
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
  for (const img of doc.querySelectorAll('img')) {
    check(img.hasAttribute('alt'), `Image has an explicit text alternative: ${file}`);
    check(Number(img.getAttribute('width')) > 0 && Number(img.getAttribute('height')) > 0, `Image reserves its layout dimensions: ${file}`);
    if (img.getAttribute('src').includes('/illustrations/')) {
      illustratedAssets.add(path.resolve(path.dirname(file), img.getAttribute('src')));
    }
  }
}
let artBytes = 0;
for (const file of illustratedAssets) {
  const bytes = fs.readFileSync(file);
  check(bytes.toString('ascii', 0, 4) === 'RIFF' && bytes.toString('ascii', 8, 12) === 'WEBP', 'Illustrations are encoded WebP assets');
  check(bytes.length < 120000, 'Each illustration stays within the web image budget');
  artBytes += bytes.length;
}
check(artBytes < 1000000, 'The complete illustration collection stays under 1 MB');
for (const file of ['main.css', 'theme.css', 'mindmap.css', 'learning.css', 'visuals.css', 'linux-guide.css', 'splash.css', 'overlays.css', 'study.css', 'workspace.css']) {
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
// Evaluate matching display declarations, including !important and specificity.
// A class-only splash test misses an overlay hidden by another stylesheet.
function displayFromStyles(element, files) {
  let winner = { important: 0, specificity: -1, order: -1, value: element.hasAttribute('hidden') ? 'none' : 'block' };
  let order = 0;
  for (const file of files) {
    const sheet = CSSOM.parse(fs.readFileSync(path.join(ROOT, file.split(/[?#]/)[0]), 'utf8'));
    for (const rule of sheet.cssRules) {
      if (!rule.selectorText || !rule.style?.getPropertyValue('display')) continue;
      for (const selector of rule.selectorText.split(',')) {
        let matches = false;
        try { matches = element.matches(selector.trim()); } catch { continue; }
        if (!matches) continue;
        const ids = (selector.match(/#[\w-]+/g) || []).length;
        const classes = (selector.match(/\.[\w-]+|\[[^\]]+\]/g) || []).length;
        const tags = selector.replace(/#[\w-]+|\.[\w-]+|\[[^\]]+\]/g, '').trim().split(/\s+/).filter(s => /^[a-z][\w-]*$/i.test(s)).length;
        const candidate = { important: Number(rule.style.getPropertyPriority('display') === 'important'),
          specificity: ids * 10000 + classes * 100 + tags, order: order++, value: rule.style.getPropertyValue('display') };
        if (candidate.important > winner.important || (candidate.important === winner.important &&
          (candidate.specificity > winner.specificity || (candidate.specificity === winner.specificity && candidate.order > winner.order)))) winner = candidate;
      }
    }
  }
  return winner.value;
}
const homeStyles = [...home.querySelectorAll('link[rel="stylesheet"]')].map(link => link.getAttribute('href'));
const splash = home.getElementById('startupSplash');
check(displayFromStyles(splash, homeStyles) === 'none', 'Skipped intro is actually hidden');
home.documentElement.classList.add('splash-active');
check(displayFromStyles(splash, homeStyles) === 'grid', 'Active intro is actually displayed by the complete homepage stylesheet stack');
check(displayFromStyles(splash, [...homeStyles, 'css/learning.css']) === 'grid', 'Course hidden rules cannot hide the homepage intro even if loaded again');
home.documentElement.classList.remove('splash-active');
const courseDocument = documents.get(path.join(ROOT, 'tracks/web/sessions.html'));
const courseStyles = [...courseDocument.querySelectorAll('link[rel="stylesheet"]')].map(link => path.join('tracks/web', link.getAttribute('href')));
check(displayFromStyles(courseDocument.getElementById('completeLesson'), courseStyles) === 'none', 'Learning controls remain hidden before JavaScript enhancement');
check(home.querySelector('meta[property="og:image"]').content.endsWith('/bifrost/og-image.png'), 'Sharing image URL matches published path');
const sitemap = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8');
const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/site.json'), 'utf8'));
const lessonRegistry = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/lesson-ids.json'), 'utf8'));
const learningPaths = JSON.parse(fs.readFileSync(path.join(ROOT,'content/generated-paths.json'),'utf8'));
check((sitemap.match(/<loc>/g) || []).length === 4 + 2 * manifest.courses.length + lessonRegistry.length + learningPaths.reduce((sum,r)=>sum+r.sequence.length+2,0), 'Sitemap includes standalone learning paths, route lessons/projects and permanent course pages');
check(!sitemap.includes('lesson.html?id='), 'Sitemap uses permanent static pages');

const workflow = fs.readFileSync(path.join(ROOT, '.github/workflows/pages.yml'), 'utf8');
check(workflow.includes('needs: verify') && workflow.includes('pnpm test') && workflow.includes('python tests/labs_test.py'), 'Deployment requires teaching and lab verification');
check(workflow.includes('path: _site') && !workflow.includes("path: '.'"), 'Deploy only packaged runtime assets');
const template = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8');
check((template.match(/\{\{MAP_NODES\}\}/g) || []).length === 1, 'Homepage has one authored map placeholder');
console.log(`PASS: ${checks} static asset, link, CSS, metadata and deployment contract checks.`);
