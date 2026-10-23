/* Coverage, accessibility, geometry and lesson-specific facts; no browser needed. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const { parseHTML } = require('linkedom');
const ROOT = path.resolve(__dirname, '..');
const context = { window: {} };
for (const file of ['curriculum.js', 'visual-data.js', 'visuals.js']) vm.runInNewContext(fs.readFileSync(path.join(ROOT, 'js', file), 'utf8'), context, { filename: file });
const courses = context.window.BifrostCourses;
const data = context.window.BifrostVisualData;
const renderer = context.window.BifrostVisuals;
let checks = 0;
const check = (condition, message) => { assert.ok(condition, message); checks++; };
const lessonIDs = Object.values(courses).flatMap(c => c.modules.flatMap(m => m.lessons.map(l => l.id)));
assert.deepEqual(Object.keys(data.lessons).sort(), lessonIDs.sort());
assert.deepEqual(Object.keys(data.courses).sort(), Object.keys(courses).sort());
assert.deepEqual(JSON.parse(JSON.stringify(data)), JSON.parse(fs.readFileSync(path.join(ROOT, 'content/visuals.json'), 'utf8')), 'Generated bundle matches authored source');

function samples(d) {
  const tokens = d.match(/[MLCHVQmlchvq]|-?\d+(?:\.\d+)?/g);
  let i = 0, x = 0, y = 0, command;
  const points = [];
  const number = () => Number(tokens[i++]);
  while (i < tokens.length) {
    if (/^[a-z]$/i.test(tokens[i])) command = tokens[i++];
    const relative = command === command.toLowerCase();
    const c = command.toUpperCase(), ox = x, oy = y;
    if (c === 'M') { x = number() + (relative ? ox : 0); y = number() + (relative ? oy : 0); points.push([x, y]); }
    else if (c === 'C') {
      const a = [number(), number()], b = [number(), number()], end = [number(), number()];
      if (relative) for (const p of [a, b, end]) { p[0] += ox; p[1] += oy; }
      for (let step = 1; step <= 80; step++) {
        const t = step / 80, s = 1 - t;
        points.push([s ** 3 * ox + 3 * s ** 2 * t * a[0] + 3 * s * t ** 2 * b[0] + t ** 3 * end[0], s ** 3 * oy + 3 * s ** 2 * t * a[1] + 3 * s * t ** 2 * b[1] + t ** 3 * end[1]]);
      }
      [x, y] = end;
    } else {
      if (c === 'L') { x = number() + (relative ? ox : 0); y = number() + (relative ? oy : 0); }
      else if (c === 'H') x = number() + (relative ? ox : 0);
      else if (c === 'V') y = number() + (relative ? oy : 0);
      else throw new Error(`Unsupported command ${c}`);
      for (let step = 1; step <= 40; step++) points.push([ox + (x - ox) * step / 40, oy + (y - oy) * step / 40]);
    }
  }
  return points;
}
const inside = ([x, y], n) => x > n[1] + 1 && x < n[1] + n[3] - 1 && y > n[2] + 1 && y < n[2] + n[4] - 1;
const boundary = ([x, y], n) => x >= n[1] - .1 && x <= n[1] + n[3] + .1 && y >= n[2] - .1 && y <= n[2] + n[4] + .1 && Math.min(Math.abs(x - n[1]), Math.abs(x - n[1] - n[3]), Math.abs(y - n[2]), Math.abs(y - n[2] - n[4])) < .1;
for (const [collection, course] of [[data.lessons, false], [data.courses, true]]) {
  for (const [id, visual] of Object.entries(collection)) {
    const html = course ? renderer.renderCourse(id) : renderer.renderLesson(id);
    const { document } = parseHTML(`<html><body>${html}</body></html>`);
    const svg = document.querySelector('svg');
    check(document.querySelectorAll('figure').length === 1, `${id}: one authored figure`);
    check(svg?.getAttribute('role') === 'img', `${id}: accessible graphic`);
    check(svg.querySelector('title').textContent === visual.title && svg.querySelector('desc').textContent === visual.description, `${id}: complete text alternative`);
    check(document.querySelector('.visual-description p').textContent === visual.description, `${id}: visible alternative available`);
    check(document.querySelector('figcaption').textContent.includes(visual.takeaway), `${id}: teaching takeaway`);
    check(document.querySelector('.visual-viewport').getAttribute('tabindex') === '0', `${id}: keyboard scrolling`);
    check(!document.querySelector('script,img,iframe,foreignObject,a'), `${id}: no active or external content`);
    const ids = [...document.querySelectorAll('[id]')].map(el => el.id);
    check(ids.length === new Set(ids).size, `${id}: unique IDs`);
    for (const ref of svg.getAttribute('aria-labelledby').split(' ')) check(!!document.getElementById(ref), `${id}: resolved accessibility reference`);
    for (const p of svg.querySelectorAll('[marker-end]')) check(!!document.getElementById(p.getAttribute('marker-end').slice(5, -1)), `${id}: resolved arrow marker`);
    const [,, width, height] = svg.getAttribute('viewBox').split(' ').map(Number);
    for (const span of svg.querySelectorAll('tspan')) {
      const x = Number(span.getAttribute('x')), y = Number(span.getAttribute('y'));
      check(x >= 0 && x <= width && y >= 10 && y < height, `${id}: text baseline inside canvas`);
    }
    if (visual.type === 'table') check(!visual.widths || visual.widths.reduce((a, b) => a + b) === 704, `${id}: table fits canvas`);
    if (visual.type === 'map') {
      for (let i = 0; i < visual.nodes.length; i++) {
        const a = visual.nodes[i];
        check(a[1] >= 16 && a[1] + a[3] <= width - 16 && a[2] >= 16 && a[2] + a[4] <= height - 16, `${id}: node within canvas`);
        for (const b of visual.nodes.slice(i + 1)) check(a[1] + a[3] <= b[1] || b[1] + b[3] <= a[1] || a[2] + a[4] <= b[2] || b[2] + b[4] <= a[2], `${id}: nodes do not overlap`);
      }
      for (const p of svg.querySelectorAll('.v-edge')) {
        const points = samples(p.getAttribute('d'));
        check(visual.nodes.some(n => boundary(points[0], n)), `${id}: connector leaves node boundary`);
        check(visual.nodes.some(n => boundary(points.at(-1), n)), `${id}: connector reaches node boundary`);
        check(!points.some(point => visual.nodes.some(n => inside(point, n))), `${id}: connector does not pass through a node`);
      }
    }
  }
}
check(new Set(Object.values(data.lessons).map(v => v.title)).size === lessonIDs.length, 'Every lesson has its own graphic title');
check(renderer.renderLesson('unknown') === '' && renderer.renderCourse('unknown') === '', 'Unknown IDs do not break lesson rendering');

// Facts tied to the bundled labs, rather than generic placeholder labels.
const flat = id => JSON.stringify(data.lessons[id]);
const digest = value => crypto.createHash('sha256').update(value).digest('hex');
check(flat('crypto.hash').includes(digest('Bifrost')) && flat('crypto.hash').includes(digest('Bifrost!')), 'SHA-256 diagrams contain actual digests');
const payload = Buffer.from(Buffer.from('Bifrost').toString('base64')).toString('base64');
check(flat('misc.pipeline').includes(payload) && flat('misc.writeup').includes(payload), 'Pipeline and inverse match the real fixture');
const auth = fs.readFileSync(path.join(ROOT, 'labs/forensic/auth.csv'), 'utf8');
check(auth.includes('09:00:00+09:00') && flat('forensic.timeline').includes('00:00 UTC'), 'Forensic offset conversion matches the fixture');
check(data.lessons['network.transport'].messages.length === 8 && data.lessons['network.pcap'].rows[0].values.length === 8, 'Packet diagrams cover the eight-frame fixture');
check(flat('network.policy').includes('DENY · MISMATCH') && flat('network.policy').includes('N06'), 'Missing egress rule is visibly distinguished');
check(flat('pwn.bounds').includes('index 3 · 금지') && data.lessons['pwn.bounds'].rows[0].validCount === 3, 'Invalid element is outside the valid array range');
check(flat('network.tls').includes('15프레임') && flat('network.tls').includes('레코드 9개') && flat('network.tls').includes('tls13.pcap'), 'TLS visual names the actual separate encrypted fixture');
check(flat('crypto.symmetric').includes('aead.py') && !flat('crypto.symmetric').includes('실행하지 않습니다'), 'AEAD visual matches the executable authenticated encryption lab');
check(flat('crypto.public-key').includes('Ed25519') && flat('cloud.capstone').includes('INVALID'), 'Signature and cloud visual notes match improved labs');

const originalTitle = data.lessons['web.flow'].title;
data.lessons['web.flow'].title = '<img src=x onerror=alert(1)> & "test"';
const malicious = parseHTML(`<html><body>${renderer.renderLesson('web.flow')}</body></html>`).document;
check(!malicious.querySelector('img,[onerror]') && malicious.querySelector('h3').textContent === data.lessons['web.flow'].title, 'Diagram content is escaped');
data.lessons['web.flow'].title = originalTitle;
console.log(`PASS: ${checks} visual checks; 62 lesson and 9 course diagrams, text alternatives, routing, canvas bounds and lab facts.`);
