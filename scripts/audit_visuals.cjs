/* Audit rendered SVGs with actual Korean glyph widths and theme contrast.
   Run after render_visuals.cjs; uses the same optional sharp/font environment. */
const fs = require('node:fs');
const path = require('node:path');
const { parseHTML } = require('linkedom');
const sharp = require(process.env.BIFROST_SHARP_MODULE || 'sharp');
const folder = path.resolve(process.argv[2] || path.join(require('node:os').tmpdir(), 'bifrost-visual-review'));
const manifest = JSON.parse(fs.readFileSync(path.join(folder, 'manifest.json'), 'utf8'));
const cache = new Map(), failures = [];
const esc = value => value.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const luminance = color => {
  if (!/^#[a-f\d]{6}$/i.test(color || '')) throw new Error(`Unresolved color ${color}`);
  const values = [1, 3, 5].map(i => parseInt(color.slice(i, i + 2), 16) / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4);
  return values[0] * .2126 + values[1] * .7152 + values[2] * .0722;
};
const contrast = (a, b) => { const x = luminance(a), y = luminance(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
async function widthOf(value, size, weight) {
  const key = `${size}/${weight}/${value}`;
  if (!cache.has(key)) {
    const input = { text: esc(value), font: `Malgun Gothic${Number(weight) >= 600 ? ' Bold' : ''} ${size}`, dpi: 72, rgba: true };
    if (process.env.BIFROST_KOREAN_FONT) input.fontfile = process.env.BIFROST_KOREAN_FONT;
    cache.set(key, (await sharp({ text: input }).metadata()).width);
  }
  return cache.get(key);
}
(async () => {
  let lines = 0;
  for (const item of manifest) {
    const { document } = parseHTML(`<html><body>${fs.readFileSync(item.file.replace(/\.png$/, '.svg'), 'utf8')}</body></html>`);
    const svg = document.querySelector('svg'), bboxes = [];
    for (const text of svg.querySelectorAll('text')) {
      const size = Number(text.getAttribute('font-size') || 14);
      const anchor = text.getAttribute('text-anchor') || 'start';
      const group = text.closest('g.v-tone');
      let container = group && [...group.children].find(el => el.tagName.toLowerCase() === 'rect' && ['v-node', 'v-table-cell', 'v-table-head'].some(c => el.classList.contains(c)));
      if (text.previousElementSibling?.classList.contains('v-label-bg')) container = text.previousElementSibling;
      const spans = text.querySelectorAll('tspan');
      for (const span of spans.length ? spans : [text]) {
        const value = span.textContent;
        if (!value.trim()) continue;
        const x = Number(span.getAttribute('x') ?? text.getAttribute('x'));
        const y = Number(span.getAttribute('y') ?? text.getAttribute('y'));
        const width = await widthOf(value, size, text.getAttribute('font-weight'));
        const left = x - (anchor === 'middle' ? width / 2 : anchor === 'end' ? width : 0), right = left + width;
        const location = `${item.id}/${item.theme}: ${value}`;
        if (left < -1 || right > item.width + 1 || y - size < -1 || y + size * .25 > item.height + 1) failures.push(`Canvas overflow: ${location}`);
        let background = item.theme === 'dark' ? '#151f2e' : '#ffffff';
        if (container && y >= Number(container.getAttribute('y'))) {
          const cx = Number(container.getAttribute('x')), cy = Number(container.getAttribute('y')), cw = Number(container.getAttribute('width')), ch = Number(container.getAttribute('height'));
          if (left < cx + 3 || right > cx + cw - 3 || y - size < cy + 2 || y + size * .25 > cy + ch - 2) failures.push(`Box overflow: ${location}`);
          background = container.getAttribute('fill');
        }
        const ratio = contrast(text.getAttribute('fill'), background);
        if (ratio < 4.5) failures.push(`Text contrast ${ratio.toFixed(2)}: ${location}`);
        bboxes.push({ left, right, top: y - size * .83, bottom: y + size * .15, value });
        lines++;
      }
    }
    for (let i = 0; i < bboxes.length; i++) for (const b of bboxes.slice(i + 1)) {
      const a = bboxes[i];
      if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 2 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 2) failures.push(`Text overlap ${item.id}/${item.theme}: ${a.value} / ${b.value}`);
    }
  }
  if (failures.length) throw new Error(failures.join('\n'));
  console.log(`PASS: ${manifest.length} rendered SVGs; ${lines} lines checked using actual Korean glyph widths; canvas/box bounds, text overlaps and 4.5:1 text contrast.`);
})().catch(error => { console.error(error.message); process.exitCode = 1; });
