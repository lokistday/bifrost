/* Verify real static pages and their production scripts, without browser automation. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { parseHTML } = require('linkedom');
const ROOT = path.resolve(__dirname, '..');
const site = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/site.json'), 'utf8'));
const registry = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/lesson-ids.json'), 'utf8'));
const { create } = require('../js/learning-view.js');
let checks = 0;
const check = (value, message) => { assert.ok(value, message); checks++; };

function enhance(relative, search = '') {
  const { document, Event, CustomEvent } = parseHTML(fs.readFileSync(path.join(ROOT, relative), 'utf8'));
  const originalArticle = document.querySelector('.lesson-article');
  const saved = new Map();
  const handlers = new Map();
  const window = {
    document, matchMedia: () => ({ matches: false }),
    addEventListener(name, fn) { if (!handlers.has(name)) handlers.set(name, []); handlers.get(name).push(fn); },
    dispatchEvent(event) { for (const fn of handlers.get(event.type) || []) fn(event); }
  };
  window.parent = window;
  const localStorage = { getItem: key => saved.get(key) ?? null, setItem: (key, value) => saved.set(key, value) };
  const context = vm.createContext({ window, document, Event, CustomEvent, localStorage,
    location: { search, origin: 'https://lokistday.github.io' }, URL, URLSearchParams, Blob,
    setTimeout: () => 0, navigator: { clipboard: { writeText: async () => {} } }, console });
  for (const script of document.querySelectorAll('script[src]')) {
    const file = path.resolve(ROOT, path.dirname(relative), script.getAttribute('src').split(/[?#]/)[0]);
    vm.runInContext(fs.readFileSync(file, 'utf8'), context, { filename: file });
  }
  return { document, window, saved, originalArticle, Event };
}

const titles = new Set(), ids = [], canonicalURLs = new Set();
for (const item of site.courses) {
  const course = JSON.parse(fs.readFileSync(path.join(ROOT, `content/courses/${item.id}.json`), 'utf8'));
  for (const lesson of course.modules.flatMap(module => module.lessons)) {
    ids.push(lesson.id);
    const relative = `tracks/${course.id}/${lesson.id.split('.')[1]}.html`;
    const raw = fs.readFileSync(path.join(ROOT, relative), 'utf8');
    const doc = parseHTML(raw).document;
    const title = doc.title;
    check(!titles.has(title), `Unique server-visible title: ${lesson.id}`); titles.add(title);
    check(title.includes(lesson.title), `Server-visible title matches lesson: ${lesson.id}`);
    check(doc.querySelector('meta[name="description"]').content === lesson.goal, 'Static description');
    check(doc.querySelector('.lesson-heading h1').textContent === lesson.title, 'Article present without JS');
    check(doc.querySelector('#exampleCode').textContent === lesson.code, 'Static code is escaped faithfully');
    check(doc.querySelector('[data-visual-id]').dataset.visualId === lesson.id, 'Static diagram present');
    const canonical = doc.querySelector('link[rel="canonical"]').getAttribute('href');
    check(canonical === site.url + relative && !canonicalURLs.has(canonical), 'Unique permanent canonical route');
    canonicalURLs.add(canonical);
    check(doc.querySelector('meta[property="og:url"]').content === canonical, 'Open Graph shares canonical route');
    check(doc.querySelector('.solution') && doc.querySelectorAll('.walkthrough > li').length >= 2, 'Authored solution and steps');
    check(doc.querySelectorAll('.question-answer').length === lesson.questions.length, 'Answers readable without JS');
    check(doc.querySelector('.lesson-preparation').textContent.includes(lesson.environment.label), 'Tailored environment present');
    check(doc.querySelectorAll('.reference-panel li').length === lesson.references.length, 'Lesson-specific references');
    const names = [...doc.querySelectorAll('[id]')].map(element => element.id);
    check(new Set(names).size === names.length, 'Unique static document IDs');

    const page = enhance(relative);
    check(page.document.querySelector('.lesson-article') === page.originalArticle, 'Enhancement preserves static article and focus targets');
    check(Object.values(page.window.BifrostCourses).flatMap(c => c.modules.flatMap(m => m.lessons)).length === registry.length, 'Production catalog retains every permanent ID');
    check(!page.document.getElementById('completeLesson').hidden, 'Completion enabled only after JS');
    const savedBefore = page.saved.get('bifrost_progress_v2');
    lesson.questions.forEach((question, index) => {
      const field = page.document.querySelector(`[data-question="${index}"]`);
      const button = page.document.querySelector(`[data-check-question="${index}"]`);
      const feedback = page.document.getElementById(`questionFeedback${index}`);
      button.click();
      check(feedback.textContent.includes('하나 고른'), 'No-selection feedback');
      const radios = [...field.querySelectorAll('input')];
      const wrong = (question.answer + 1) % radios.length;
      radios[wrong].setAttribute('checked', '');
      button.click();
      check(feedback.dataset.result === 'review' && feedback.textContent.includes(question.explanation), 'Wrong answer explains reasoning');
      radios[wrong].removeAttribute('checked');
      radios[question.answer].setAttribute('checked', '');
      radios[question.answer].dispatchEvent(new page.Event('change'));
      check(feedback.textContent === '' && !feedback.hasAttribute('data-result'), 'Changing choice clears stale feedback');
      button.click();
      check(feedback.dataset.result === 'correct' && feedback.textContent.includes(question.explanation), 'Correct answer still explains reasoning');
    });
    check(page.saved.get('bifrost_progress_v2') === savedBefore, 'Self checks do not persist scores or mark completion');
    page.document.getElementById('completeLesson').click();
    check(page.window.BifrostProgress.has(lesson.id), 'Static route completion uses permanent ID');
  }
}
assert.deepEqual(ids.sort(), registry, 'No permanent IDs lost or reused');

// Query addresses still select the same article; explicit static pages ignore unrelated query IDs.
const legacy = enhance('tracks/web/lesson.html', '?id=web.sessions');
check(legacy.document.querySelector('.lesson-heading h1').textContent.includes('세션'), 'Legacy query route works');
check(legacy.document.querySelector('link[rel="canonical"]').href.endsWith('/web/sessions.html'), 'Legacy route points to static canonical');
const staticQuery = enhance('tracks/web/sessions.html', '?id=web.output');
check(staticQuery.document.body.dataset.lessonId === 'web.sessions' && staticQuery.document.querySelector('.lesson-heading h1').textContent.includes('세션'), 'Static route cannot be replaced by query ID');

// Authored strings, code examples, and question text are escaped by the shared renderer.
const attack = '<img src=x onerror=alert(1)>';
const course = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/courses/misc.json'), 'utf8'));
course.number = '03'; course.introduction = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/fields.json'), 'utf8')).misc;
const sample = course.modules[0].lessons[0];
sample.concepts[0] = attack; sample.questions[0].prompt = attack; sample.solution.approach[0] = attack;
const dataContext = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(ROOT, 'js/curriculum.js'), 'utf8'), dataContext);
const dataCourses = dataContext.window.BifrostCourses;
dataCourses.misc = course;
const markup = create(dataCourses, { renderLesson: () => '', renderCourse: () => '' }).lesson('misc', sample.id);
const doc = parseHTML(`<html><body>${markup}</body></html>`).document;
check(!doc.querySelector('[onerror], img[src="x"]') && doc.body.textContent.includes(attack), 'Content cannot create executable HTML');
console.log(`PASS: ${checks} static teaching, production hydration and self-check assertions across ${registry.length} lessons.`);
