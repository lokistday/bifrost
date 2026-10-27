/* Learning-path navigation, independent practice and secure search behavior. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const { parseHTML } = require('linkedom');
const ROOT = path.resolve(__dirname,'..');
const read = name => fs.readFileSync(path.join(ROOT,name),'utf8');
let checks=0;
const check=(value,message)=>{assert.ok(value,message);checks++;};
const courses=Object.fromEntries(JSON.parse(read('content/site.json')).courses.map(({id})=>[id,JSON.parse(read(`content/courses/${id}.json`))]));
const all=Object.values(courses).flatMap(c=>c.modules.flatMap(m=>m.lessons));
const lessons=Object.fromEntries(all.map(l=>[l.id,l]));
for (const l of all) {
  const doc=parseHTML(read(`tracks/${l.id.replace('.','/')}.html`)).document;
  check(doc.querySelector('#transfer h3'),`${l.id}: independent exercise`);
  check(doc.querySelector('#transfer .hint p').textContent.length>30,`${l.id}: tailored answer`);
  check(doc.querySelectorAll('#transfer tbody tr').length===4,`${l.id}: evidence rubric`);
  check(doc.querySelector('.lesson-meta').textContent.includes('분'),`${l.id}: study time`);
  check(doc.querySelector('.readiness details').textContent.includes('보충'),`${l.id}: readiness support`);
  check(read(`tracks/${l.id.replace('.','/')}.html`).indexOf('id="exampleCode"') < read(`tracks/${l.id.replace('.','/')}.html`).indexOf('class="walkthrough"'),`${l.id}: baseline before mutations`);
}
for (const route of JSON.parse(read('content/generated-paths.json'))) {
  const seen=new Set();
  for (const id of route.sequence) {
    check(!seen.has(id) && lessons[id], 'Known, unique route lesson');
    check(lessons[id].prerequisites.every(p=>seen.has(p)), 'Prerequisites precede dependent route lesson');
    seen.add(id);
  }
  check(route.lessons.every(id=>seen.has(id)), 'No selected route lesson is omitted');
  const project=JSON.parse(read('content/projects.json'))[route.project];
  check(project.prerequisites.every(id=>seen.has(id)), 'Project prerequisites are included in its learning path');
}
for (const key of Object.keys(courses)) {
  const doc=parseHTML(read(`projects/${key}.html`)).document;
  check(doc.querySelectorAll('#rubric ol li').length===4, `${key}: project rubric`);
  check(doc.getElementById('assignment').textContent.includes('출력 계약'),`${key}: exact result contract`);
  check(doc.getElementById('check').textContent.includes('--variant b'),`${key}: transfer case required`);
  check(doc.querySelector('.project-flow').getAttribute('aria-label'),`${key}: accessible workflow`);
}

const {document,Event}=parseHTML(read('learn/index.html'));
check(document.querySelectorAll('[data-search-item]').length===all.length,'Static catalog complete without JavaScript');
check(document.getElementById('lessonSearch').hasAttribute('hidden'),'Nonfunctional search hidden before enhancement');
// linkedom select elements expose read-only value; model the DOM selection value.
for (const id of ['searchCourse','searchLevel']) Object.defineProperty(document.getElementById(id),'value',{value:'',writable:true});
vm.runInNewContext(read('js/study-search.js'),{document,URLSearchParams,location:{search:'?q='+encodeURIComponent('<img src=x onerror=alert(1)>')}});
check(document.querySelectorAll('img[onerror]').length===0,'Search input cannot become HTML');
check(!document.getElementById('searchEmpty').hidden,'Hostile/unknown query produces empty state');
const q=document.getElementById('searchQuery');
q.value='세션';q.dispatchEvent(new Event('input'));
const shown=()=>[...document.querySelectorAll('[data-search-item]')].filter(r=>!r.hidden);
check(shown().some(r=>r.dataset.course==='web'),'Korean query finds session lessons');
document.getElementById('searchCourse').value='web'; document.getElementById('searchCourse').dispatchEvent(new Event('change'));
check(shown().length>0 && shown().every(r=>r.dataset.course==='web'),'Course filter combines with query');
q.value='SQL';q.dispatchEvent(new Event('input'));
check(shown().some(r=>r.textContent.includes('SQL')),'Case-normalized English search');
document.getElementById('searchLevel').value='심화 연결';document.getElementById('searchLevel').dispatchEvent(new Event('change'));
check(shown().every(r=>r.dataset.level==='심화 연결'),'Difficulty filter');
document.getElementById('searchReset').click();
check(shown().length===all.length,'Reset restores every lesson');
check(!/innerHTML|fetch\(|eval\(|localStorage/.test(read('js/study-search.js')),'Search is text-only and does not transmit/store queries');

const html=['index.html','guides/linux.html','guides/bridges.html','learn/index.html',...Object.keys(courses).flatMap(k=>[`projects/${k}.html`,`tracks/${k}/lesson.html`]),...all.map(l=>`tracks/${l.id.replace('.','/')}.html`)];
for (const file of html) {
  const source=read(file), doc=parseHTML(source).document;
  const csp=doc.querySelector('meta[http-equiv="Content-Security-Policy"]');
  check(csp && csp.content.includes("script-src 'self';") && csp.content.includes("object-src 'none'"),`${file}: script/object policy`);
  check(csp.content.includes("base-uri 'none'") && csp.content.includes("connect-src 'none'"),`${file}: no base injection/remote data API`);
  check(!csp.content.includes('frame-ancestors'),`${file}: do not claim header-only protection via meta`);
  check(doc.querySelectorAll('script:not([src])').length===0,`${file}: no inline script`);
  check([...doc.querySelectorAll('*')].every(el=>[...el.attributes].every(a=>!/^on/i.test(a.name))),`${file}: no inline event handler`);
  check(source.indexOf('Content-Security-Policy')<source.indexOf('<script'),`${file}: policy precedes scripts`);
}
console.log(`PASS: ${checks} learning revision, static practice, search and CSP checks.`);
