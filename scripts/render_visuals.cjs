/* Render the actual inline SVG assets for local visual review, without a browser.
   Optional dependency: sharp (or set BIFROST_SHARP_MODULE to its module path). */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { parseHTML } = require('linkedom');
const sharp = require(process.env.BIFROST_SHARP_MODULE || 'sharp');
const ROOT = path.resolve(__dirname, '..');
const out = path.resolve(process.argv[2] || path.join(require('node:os').tmpdir(), 'bifrost-visual-review'));
const context = { window: {} };
for (const file of ['visual-data.js', 'visuals.js']) vm.runInNewContext(fs.readFileSync(path.join(ROOT, 'js', file), 'utf8'), context, { filename: file });
const data = context.window.BifrostVisualData, renderer = context.window.BifrostVisuals;
const css = ['theme.css', 'learning.css', 'visuals.css'].map(file => fs.readFileSync(path.join(ROOT, 'css', file), 'utf8').split('@media print')[0]).join('\n');
// Use the same course accent mapping as the actual lesson page.
const site = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/site.json'), 'utf8'));
const colors = Object.fromEntries(site.courses.map(course => [course.id, course.accent]));
const rules = [...css.matchAll(/([^{}]+)\{([^{}]*)\}/g)].map(m => ({
  selector: m[1].replace(/\/\*[\s\S]*?\*\//g, '').trim(),
  declarations: [...m[2].matchAll(/([\w-]+)\s*:\s*([^;]+)(?:;|$)/g)].map(m => [m[1], m[2].trim()])
})).filter(r => r.selector && !r.selector.startsWith('@'));
const attrs = new Set(['fill', 'fill-opacity', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-linecap', 'stroke-linejoin', 'font-family', 'font-size', 'font-weight', 'text-anchor']);
function resolve(value, vars) {
  for (let i = 0; i < 12 && value.includes('var('); i++) value = value.replace(/var\((--[\w-]+)(?:,\s*([^()]*))?\)/g, (_, key, fallback) => vars[key] ?? fallback ?? '');
  return value;
}
function standalone(html, theme) {
  const { document } = parseHTML(`<html data-theme="${theme}"><body>${html}</body></html>`);
  const styles = new Map();
  for (const rule of rules) {
    let elements;
    try { elements = document.querySelectorAll(rule.selector); } catch { continue; }
    for (const element of elements) {
      if (!styles.has(element)) styles.set(element, {});
      Object.assign(styles.get(element), Object.fromEntries(rule.declarations));
    }
  }
  const course = document.querySelector('figure').getAttribute('data-visual-id').split('.')[0];
  styles.set(document.body, { ...(styles.get(document.body) || {}), '--course-accent': `var(--map-${colors[course]})` });
  function visit(element, inherited = {}) {
    const style = styles.get(element) || {};
    const vars = { ...inherited, ...Object.fromEntries(Object.entries(style).filter(([key]) => key.startsWith('--'))) };
    for (const [name, value] of Object.entries(style)) if (attrs.has(name)) element.setAttribute(name, resolve(value, vars));
    for (const child of element.children) visit(child, vars);
  }
  visit(document.documentElement);
  const svg = document.querySelector('svg');
  svg.setAttribute('style', '');
  // A concrete canvas color also makes contrast visible outside the lesson page.
  svg.insertAdjacentHTML('afterbegin', `<rect x="0" y="0" width="100%" height="100%" fill="${theme === 'dark' ? '#151f2e' : '#ffffff'}"/>`);
  return svg.outerHTML;
}
(async () => {
  fs.mkdirSync(out, { recursive: true });
  // Register the Korean font with Pango/fontconfig before librsvg renders SVGs.
  if (process.env.BIFROST_KOREAN_FONT) await sharp({ text: { text: '학습', font: 'Malgun Gothic 14', fontfile: process.env.BIFROST_KOREAN_FONT, rgba: true } }).png().toBuffer();
  const entries = [
    ...Object.keys(data.courses).map(id => [`course-${id}`, renderer.renderCourse(id)]),
    ...Object.keys(data.lessons).map(id => [id, renderer.renderLesson(id)])
  ];
  const manifest = [];
  for (const theme of ['light', 'dark']) {
    const folder = path.join(out, theme); fs.mkdirSync(folder, { recursive: true });
    for (const [id, html] of entries) {
      const svg = standalone(html, theme), file = path.join(folder, `${id}.png`);
      fs.writeFileSync(path.join(folder, `${id}.svg`), svg);
      const info = await sharp(Buffer.from(svg)).png().toFile(file);
      manifest.push({ id, theme, file, width: info.width, height: info.height });
    }
    // Small review sheets expose inconsistent padding, clipped rows and crossings.
    for (const course of Object.keys(data.courses)) {
      const items = manifest.filter(item => item.theme === theme && (item.id === `course-${course}` || item.id.startsWith(`${course}.`)));
      const cellW = 560, titleH = 32, gap = 20;
      const rowHeights = Array.from({ length: Math.ceil(items.length / 2) }, (_, row) => Math.max(...items.slice(row * 2, row * 2 + 2).map(i => Math.round(i.height * cellW / i.width))) + titleH + gap);
      const height = rowHeights.reduce((a, b) => a + b, 0) + gap;
      let top = gap;
      const layers = [];
      for (let i = 0; i < items.length; i++) {
        if (i && i % 2 === 0) top += rowHeights[i / 2 - 1];
        const left = gap + (i % 2) * (cellW + gap), item = items[i];
        const title = `<svg width="${cellW}" height="${titleH}" xmlns="http://www.w3.org/2000/svg"><text x="3" y="22" font-family="sans-serif" font-size="16" fill="${theme === 'dark' ? '#e7edf7' : '#172235'}">${item.id}</text></svg>`;
        layers.push({ input: Buffer.from(title), left, top });
        layers.push({ input: await sharp(item.file).resize({ width: cellW }).toBuffer(), left, top: top + titleH });
      }
      await sharp({ create: { width: cellW * 2 + gap * 3, height, channels: 4, background: theme === 'dark' ? '#0b1220' : '#f0f4f8' } }).composite(layers).png().toFile(path.join(out, `${course}-${theme}.png`));
    }
  }
  fs.writeFileSync(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 2));
  console.log(`Rendered ${manifest.length} diagrams and 18 review sheets to ${out}`);
})().catch(error => { console.error(error); process.exitCode = 1; });
