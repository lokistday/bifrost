/* Real exam pages and production events: grading, draft recovery, retry and failures. */
const assert=require('node:assert/strict'), fs=require('node:fs'), path=require('node:path'), vm=require('node:vm');
const {parseHTML}=require('linkedom');
const ROOT=path.resolve(__dirname,'..'), read=f=>fs.readFileSync(path.join(ROOT,f),'utf8');
const bank=JSON.parse(read('content/exams/foundation-01.json'));
const key=`bifrost_exam_${bank.id}_v${bank.version}`;
function load(saved={},broken=false,examId='foundation-01'){
  const {document,Event}=parseHTML(read(`exams/${examId}.html`));
  for(const e of document.querySelectorAll('input,[tabindex]'))e.focus=()=>{};
  const map=new Map(Object.entries(saved)),listeners={};
  const window={addEventListener:(t,f)=>listeners[t]=f,location:{reload(){}}};
  const localStorage={getItem:k=>map.get(k)||null,setItem:(k,v)=>{if(broken)throw Error('quota');map.set(k,v);}};
  const context=vm.createContext({window,document,localStorage});
  vm.runInContext(read(`js/exams/${examId}.js`),context);vm.runInContext(read('js/exam.js'),context);
  const click=id=>document.getElementById(id).click();
  function answer(q,n){
    const input=document.querySelector(`input[name="${q.id}"][value="${n}"]`);
    input.checked=true;input.dispatchEvent(new Event('change',{bubbles:true}));
  }
  const submit=()=>document.getElementById('examForm').dispatchEvent(new Event('submit',{cancelable:true}));
  return{document,map,click,answer,submit};
}
const catalog=parseHTML(read('exams/index.html')).document;
const examFiles=fs.readdirSync(path.join(ROOT,'content/exams')).filter(f=>f.endsWith('.json'));
assert.equal(catalog.querySelectorAll('.exam-module-card').length,49);
assert.equal(catalog.querySelectorAll('.is-ready').length,examFiles.length);
assert.equal(catalog.querySelectorAll('.is-pending').length,49-examFiles.length);
assert.equal(catalog.querySelectorAll('.is-pending .learning-button').length,0);
const {Event:CatalogEvent}=parseHTML('<html></html>');
vm.runInNewContext(read('js/exam-catalog.js'),{document:catalog,location:{hash:'#exam-web'}});
assert.equal(catalog.querySelectorAll('.exam-library-main>.study-section:not([hidden])').length,1);
assert.equal(catalog.querySelector('.exam-library-main>.study-section:not([hidden])').id,'exam-web');
catalog.querySelector('a[href="#exam-foundation"]').dispatchEvent(new CatalogEvent('click',{cancelable:true}));
assert.equal(catalog.querySelector('.exam-library-main>.study-section:not([hidden])').id,'exam-foundation');
assert.equal(bank.questions.length,25);
assert.equal(new Set(bank.questions.map(q=>q.id)).size,25);
assert.deepEqual([...new Set(bank.questions.map(q=>q.lesson))].sort(),['foundation.environment','foundation.paths']);
let p=load();
assert.ok(p.document.getElementById('examWorkspace').hidden);
assert.equal(p.document.querySelectorAll('[data-exam-question]').length,25);
assert.ok([...p.document.querySelectorAll('[data-explanation]')].every(e=>!e.textContent));
p.click('startExam');p.submit();
assert.equal(p.document.querySelectorAll('[data-exam-question]:not([hidden])').length,1);
assert.equal(p.document.getElementById('previousQuestion').disabled,true);
p.click('nextQuestion');assert.equal(p.document.getElementById('questionPosition').textContent,'2 / 25');
p.document.querySelector('[data-question-link="paths-13"]').click();
assert.equal(p.document.getElementById('questionPosition').textContent,'25 / 25');
assert.equal(p.document.getElementById('nextQuestion').disabled,true);
p.document.querySelector('[data-question-link="env-01"]').click();
assert.match(p.document.getElementById('examFeedback').textContent,/25문항/);
assert.equal(p.map.has(key),false,'Incomplete submission is not an attempt');
p.answer(bank.questions[0],bank.questions[0].answer);
const draft=p.map.get(key);
let recovered=load({[key]:draft});
assert.match(recovered.document.getElementById('startExam').textContent,/이어서/);
recovered.click('startExam');
assert.ok(recovered.document.querySelector(`input[name="${bank.questions[0].id}"][value="${bank.questions[0].answer}"]`).checked);
for(const [i,q] of bank.questions.entries()) recovered.answer(q,i<20?q.answer:(q.answer+1)%4);
recovered.submit();
assert.match(recovered.document.getElementById('examScore').textContent,/80점 · 20 \/ 25/);
assert.equal(recovered.document.querySelector('.exam-toolbar a').getAttribute('href'),'#examResult');
assert.ok([...recovered.document.querySelectorAll('#examForm input')].every(e=>e.disabled));
assert.equal(recovered.document.querySelectorAll('[data-correct="false"]').length,5);
assert.equal(recovered.document.querySelectorAll('#examBreakdown a').length,2);
assert.ok([...recovered.document.querySelectorAll('[data-explanation]')].every(e=>e.textContent.includes('정답:')&&!e.hidden));
assert.equal(JSON.parse(recovered.map.get(key)).attempts,1);
recovered.submit();assert.equal(JSON.parse(recovered.map.get(key)).attempts,1,'Double submission does not duplicate attempts');
assert.equal(recovered.map.has('bifrost_progress_v2'),false,'Exams never complete lessons');
recovered.click('wrongOnly');
assert.equal([...recovered.document.querySelectorAll('[data-exam-question]')].filter(e=>!e.hidden).length,5);
let result=load({[key]:recovered.map.get(key)});result.click('startExam');
assert.match(result.document.getElementById('examScore').textContent,/80점/);
result.click('retryExam');
assert.equal(result.document.querySelector('.exam-toolbar a').getAttribute('href'),'#examSubmit');
assert.ok(result.document.getElementById('examResult').hidden);
assert.equal(result.document.querySelectorAll('[data-exam-question][hidden]').length,24);
assert.ok([...result.document.querySelectorAll('#examForm input')].every(e=>!e.disabled&&!e.checked));
assert.ok([...result.document.querySelectorAll('[data-explanation]')].every(e=>!e.textContent));
for(const q of bank.questions)result.answer(q,q.answer);
result.submit();assert.match(result.document.getElementById('examScore').textContent,/100점/);
assert.equal(JSON.parse(result.map.get(key)).attempts,2);
result.click('wrongOnly');assert.match(result.document.getElementById('examHistory').textContent,/오답이 없습니다/);
result.click('retryExam');for(const q of bank.questions)result.answer(q,(q.answer+1)%4);result.submit();
assert.match(result.document.getElementById('examScore').textContent,/0점/);
assert.match(result.document.getElementById('examHistory').textContent,/최고 100점/);
const corrupt=load({[key]:'{broken'});corrupt.click('startExam');corrupt.answer(bank.questions[0],0);
assert.equal(corrupt.map.get(key),'{broken','Unreadable records are preserved');
assert.match(corrupt.document.getElementById('examStorage').textContent,/저장할 수 없습니다/);
const blocked=load({},true);blocked.click('startExam');for(const q of bank.questions)blocked.answer(q,q.answer);blocked.submit();
assert.match(blocked.document.getElementById('examScore').textContent,/100점/);
assert.match(blocked.document.getElementById('examStorage').textContent,/이번 화면/);
const invalid=load({[key]:JSON.stringify({answers:{'env-01':99,'env-02':'<img onerror=x>'},submitted:true})});
assert.match(invalid.document.getElementById('startExam').textContent,/시작/);
assert.equal(invalid.document.querySelectorAll('[onerror]').length,0);
for(const id of ['foundation.environment','foundation.paths']){
  for(const file of [`tracks/foundation/${id.split('.')[1]}.html`,`paths/start/${id}.html`]){
    const d=parseHTML(read(file)).document;
    assert.equal(d.querySelectorAll('[data-question]').length,0);
    assert.ok(d.querySelector('.module-exam-link a').getAttribute('href').endsWith('foundation-01.html'));
    assert.ok(d.querySelector('#materials a[download]'));assert.ok(d.querySelectorAll('.walkthrough li').length>=2);
  }
}
assert.ok(read('sitemap.xml').includes('exams/foundation-01.html'));
const foundation=JSON.parse(read('content/courses/foundation.json'));
assert.equal(examFiles.filter(f=>f.startsWith('foundation-')).length,5,'All five Foundation modules have an exam');
assert.equal(examFiles.filter(f=>f.startsWith('pwn-')).length,6,'All six System Security modules have an exam');
assert.equal(examFiles.filter(f=>f.startsWith('forensic-')).length,6,'All six Forensic modules have an exam');
const authoredIds=new Set();
for(const file of examFiles){
  const exam=JSON.parse(read('content/exams/'+file));
  assert.equal(exam.questions.length,25);
  const course=JSON.parse(read(`content/courses/${exam.course}.json`));
  const module=course.modules[exam.module-1];
  assert.deepEqual([...new Set(exam.questions.map(q=>q.lesson))].sort(),module.lessons.map(l=>l.id).sort());
  const balance=[0,0,0,0];
  for(const q of exam.questions){
    assert.ok(!authoredIds.has(q.id),'Question IDs stay globally distinct');authoredIds.add(q.id);
    assert.equal(new Set(q.options).size,4);assert.ok(q.explanation.length>20);balance[q.answer]++;
  }
  assert.ok(Math.max(...balance)<=8&&Math.min(...balance)>=4,'Answer positions are reasonably distributed');
  const newPage=load({},false,exam.id);newPage.click('startExam');
  for(const q of exam.questions)newPage.answer(q,q.answer);
  newPage.submit();assert.match(newPage.document.getElementById('examScore').textContent,/100점/);
  assert.equal(newPage.document.querySelectorAll('#examBreakdown a').length,module.lessons.length);
  const isolated=load({[key]:draft},false,exam.id);
  if(exam.id!==bank.id)assert.match(isolated.document.getElementById('startExam').textContent,/시작/,'Another exam draft never leaks into this exam');
  newPage.click('retryExam');
  for(const [i,q] of exam.questions.entries())newPage.answer(q,i<3?(q.answer+1)%4:q.answer);
  newPage.submit();assert.match(newPage.document.getElementById('examScore').textContent,/88점/);
  newPage.click('wrongOnly');
  assert.equal([...newPage.document.querySelectorAll('[data-exam-question]')].filter(f=>!f.hidden).length,3);
  for(const lesson of module.lessons){
    const doc=parseHTML(read(`tracks/${exam.course}/${lesson.id.split('.')[1]}.html`)).document;
    assert.equal(doc.querySelectorAll('[data-question]').length,0);
    assert.ok(doc.querySelector('.module-exam-link a').getAttribute('href').endsWith(exam.id+'.html'));
    assert.equal(doc.querySelector('#exampleCode').textContent,lesson.code,'Guided exercise code is preserved');
    assert.ok(doc.querySelector('#materials a[download]'));
  }
}
const previousBanks=JSON.parse(read('tests/exam-v1-options.json'));
for(const file of examFiles){
  const updated=JSON.parse(read('content/exams/'+file)), previous=previousBanks[updated.id];
  const oldKey=`bifrost_exam_${updated.id}_v1`, newKey=`bifrost_exam_${updated.id}_v2`;
  const legacyAnswers=Object.fromEntries(updated.questions.map((q,i)=>[q.id,i<20?previous[q.id].answer:(previous[q.id].answer+1)%4]));
  const legacy=JSON.stringify({answers:legacyAnswers,submitted:true,attempts:3,best:25});
  const migrated=load({[oldKey]:legacy},false,updated.id);migrated.click('startExam');
  assert.match(migrated.document.getElementById('examScore').textContent,/80점 · 20 \/ 25/);
  assert.match(migrated.document.getElementById('examHistory').textContent,/3회 · 최고 100점/);
  assert.equal(migrated.map.get(oldKey),legacy,'The original v1 record is never overwritten');
  const converted=JSON.parse(migrated.map.get(newKey));
  for(const q of updated.questions)assert.equal(converted.answers[q.id],updated.previousAnswerMap[q.id][legacyAnswers[q.id]]);
  const again=load(Object.fromEntries(migrated.map),false,updated.id);again.click('startExam');
  assert.match(again.document.getElementById('examScore').textContent,/80점/);
  assert.equal(again.map.get(newKey),migrated.map.get(newKey),'Reload must not translate the answers twice');
  const draftAnswers=Object.fromEntries(updated.questions.slice(0,3).map(q=>[q.id,previous[q.id].answer]));
  const oldDraft=JSON.stringify({answers:draftAnswers,submitted:false,attempts:1,best:10});
  const recovered=load({[oldKey]:oldDraft},false,updated.id);recovered.click('startExam');
  assert.equal([...recovered.document.querySelectorAll('input')].filter(input=>input.checked).length,3);
  for(const q of updated.questions.slice(0,3))assert.ok(recovered.document.querySelector(`input[name="${q.id}"][value="${q.answer}"]`).checked);
  const blockedMigration=load({[oldKey]:legacy},true,updated.id);blockedMigration.click('startExam');
  assert.match(blockedMigration.document.getElementById('examScore').textContent,/80점/);
  assert.equal(blockedMigration.map.has(newKey),false);
  assert.equal(blockedMigration.map.get(oldKey),legacy);
  assert.match(blockedMigration.document.getElementById('examStorage').textContent,/이번 화면/);
  const current=JSON.stringify({answers:{[updated.questions[0].id]:updated.questions[0].answer},submitted:false,attempts:1,best:2});
  const preferred=load({[oldKey]:legacy,[newKey]:current},false,updated.id);preferred.click('startExam');
  assert.ok(preferred.document.getElementById('examResult').hidden);
  assert.equal(preferred.map.get(newKey),current,'Current-version work takes priority over a legacy result');
  const invalidLegacy=load({[oldKey]:'{broken'},false,updated.id);
  assert.equal(invalidLegacy.map.has(newKey),false);
  assert.equal(invalidLegacy.map.get(oldKey),'{broken');
  const invalidCurrent=load({[oldKey]:legacy,[newKey]:'{broken'},false,updated.id);
  assert.equal(invalidCurrent.map.get(newKey),'{broken','Corrupt current work is preserved instead of silently replaced');
}
console.log('PASS: all module exams, scoring/drafts/retry, 17-bank v1 migrations, preserved legacy data, reload idempotence, quota/corrupt storage and preserved practice.');
