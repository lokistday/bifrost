/* Build complete HTML with the same pure view functions used for legacy URLs. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ROOT = path.resolve(__dirname, '..');
const { create, esc, all, slug } = require('../js/learning-view.js');
const site = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/site.json'), 'utf8'));
site.contentVersion = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/site-metrics.json'), 'utf8')).contentVersion;
const { protect } = require('./site_security.cjs');
const read = name => fs.readFileSync(path.join(ROOT, name), 'utf8');
const write = (name, value) => fs.writeFileSync(path.join(ROOT, name), (name.endsWith('.html') ? protect(value) : value).replace(/\r\n/g, '\n'));
const context = { window: {} };
for (const file of ['curriculum.js', 'visual-data.js', 'visuals.js']) {
  vm.runInNewContext(read(`js/${file}`), context, { filename: file });
}
const courses = context.window.BifrostCourses;
const contentVersion = esc(site.contentVersion);
const view = create(courses, context.window.BifrostVisuals);
const star = '<svg class="bifrost-star" viewBox="0 0 40 40" aria-hidden="true"><path d="M20 3 24 15 36 20 24 24 20 36 16 24 4 20 16 15Z" fill="currentColor"/><path d="M31 5 32.4 9.2 36.6 10.6 32.4 12 31 16.2 29.6 12 25.4 10.6 29.6 9.2Z" fill="#d3e3ff"/></svg>';
const template = read('templates/learning.html');
function fill(source, values) {
  return source.replace(/\{\{([A-Z_]+)\}\}/g, (_, key) => {
    if (!(key in values)) throw new Error(`Missing template field: ${key}`);
    return values[key];
  });
}
function page(course, lesson, legacy = false) {
  const title = lesson ? `${lesson.title} — ${course.title} · Bifrost` : `${course.title} — Bifrost`;
  const route = `tracks/${course.id}/${lesson ? `${slug(lesson.id)}.html` : ''}`;
  const content = lesson ? view.lesson(course.id, lesson.id) : view.overview(course.id);
  const note = legacy
    ? '<noscript><p class="environment-note">이전 형식의 차시 주소입니다. 아래 목차에서 차시를 선택하면 JavaScript 없이도 본문을 읽을 수 있습니다.</p></noscript>'
    : '<noscript><p class="environment-note">본문·도식·해설은 그대로 읽을 수 있습니다. 진도 표시와 복사·답 확인 버튼에는 JavaScript가 필요합니다. 문제의 정답과 이유는 펼쳐서 읽으세요.</p></noscript>';
  return fill(template, {
    TITLE: esc(title), DESCRIPTION: esc(lesson ? lesson.goal : course.subtitle),
    CANONICAL: esc(site.url + route), SITE_URL: esc(site.url), CONTENT_VERSION: contentVersion,
    COURSE: course.id, NUMBER: course.number, VIEW: lesson || legacy ? 'lesson' : 'course',
    LESSON_ID: lesson?.id || '', ACCENT: course.accent, LABEL: esc(course.label), STAR: star,
    RENDERED: legacy ? 'legacy' : lesson?.id || 'course', CONTENT: note + content,
    VISUAL_SCRIPTS: legacy ? `<script src="../../js/visual-data.js?v=${contentVersion}" defer></script>\n<script src="../../js/visuals.js?v=${contentVersion}" defer></script>` : ''
  });
}
const routes = ['', 'guides/linux.html'];
routes.push(...require('./render_study.cjs')({ ROOT, courses, site, fill, write }));
let count = 0;
for (const course of Object.values(courses)) {
  fs.mkdirSync(path.join(ROOT, 'tracks', course.id), { recursive: true });
  write(`tracks/${course.id}/index.html`, page(course));
  write(`tracks/${course.id}/lesson.html`, page(course, null, true));
  routes.push(`tracks/${course.id}/`);
  for (const lesson of all(course)) {
    const route = `tracks/${course.id}/${slug(lesson.id)}.html`;
    write(route, page(course, lesson));
    routes.push(route);
    count++;
  }
}
const nodes = site.courses.map(item => {
  const course = courses[item.id];
  return `      <a class="map-node node-${course.id}" data-map-track="${course.id}" href="tracks/${course.id}/"><img class="node-art" src="assets/illustrations/${course.id}.webp" width="480" height="480" alt="" decoding="async"><span class="node-copy"><span class="node-number">${course.number} / ${item.mapLabel}</span><strong>${esc(course.title)}</strong><small>${esc(course.label)}</small><i>${esc(item.teaser)}</i></span><span class="node-arrow" aria-hidden="true">↗</span></a>`;
}).join('\n');
write('index.html', fill(read('templates/index.html'), {
  MAP_NODES: nodes, SITE_URL: esc(site.url), COURSE_COUNT: Object.keys(courses).length,
  LESSON_COUNT: count, CONTENT_VERSION: contentVersion
}));
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
  routes.map(route => `  <url><loc>${esc(site.url + route)}</loc></url>`).join('\n') + '\n</urlset>\n');
console.log(`Generated ${count} complete lesson pages, 9 course pages, 9 compatible query entries and homepage.`);
