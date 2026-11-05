/* Personal study exams: answers stay local; scoring never changes lesson progress. */
(() => {
  'use strict';
  const bank = window.BifrostExam, root = document.querySelector('[data-exam]');
  if (!bank || root?.dataset.exam !== bank.id) return;
  const key = `bifrost_exam_${bank.id}_v${bank.version}`;
  const byId = id => document.getElementById(id);
  const fields = [...document.querySelectorAll('[data-exam-question]')];
  let writable = true, started = false, wrongOnly = false, current = 0;
  // ESSENTIAL-style workspace: one question, previous/next, and an answer sheet.
  const layout=document.createElement('div');layout.className='exam-solving-layout';
  const pane=document.createElement('div');pane.className='exam-question-pane';
  const sheet=document.createElement('aside');sheet.className='exam-answer-sheet';sheet.setAttribute('aria-label','나의 답안');
  const sheetTitle=document.createElement('h2');sheetTitle.textContent='나의 답안';sheet.append(sheetTitle);
  const controls=document.createElement('nav');controls.className='exam-pagination';controls.setAttribute('aria-label','이전·다음 문제');
  const prev=document.createElement('button');prev.type='button';prev.textContent='← 이전 문제';prev.id='previousQuestion';
  const position=document.createElement('span');position.id='questionPosition';position.setAttribute('aria-live','polite');
  const next=document.createElement('button');next.type='button';next.textContent='다음 문제 →';next.id='nextQuestion';
  controls.append(prev,position,next);
  byId('examQuestions').after(controls);
  byId('submitExam').setAttribute('form','examForm');
  sheet.append(document.querySelector('.exam-toolbar'),document.querySelector('.exam-question-map'),byId('examSubmit'));
  pane.append(byId('examForm'));layout.append(pane,sheet);byId('examWorkspace').append(layout);
  function showQuestion(index,focus=false) {
    current=Math.max(0,Math.min(bank.questions.length-1,index));
    fields.forEach((field,i)=>field.hidden=!state.submitted&&i!==current);
    prev.disabled=current===0;next.disabled=current===fields.length-1;
    position.textContent=`${current+1} / ${fields.length}`;
    document.querySelectorAll('[data-question-link]').forEach((a,i)=>{if(i===current)a.setAttribute('aria-current','step');else a.removeAttribute('aria-current');});
    if(focus){fields[current].querySelector('input').focus();layout.scrollIntoView?.({block:'start',behavior:'instant'});}
  }
  prev.addEventListener('click',()=>showQuestion(current-1,true));
  next.addEventListener('click',()=>showQuestion(current+1,true));
  document.querySelectorAll('[data-question-link]').forEach((a,i)=>a.addEventListener('click',event=>{if(!state.submitted){event.preventDefault();showQuestion(i,true);}}));
  let state = {answers:{}, submitted:false, attempts:0, best:0};
  function sanitize(raw) {
    if (!raw || typeof raw !== 'object' || !raw.answers || typeof raw.answers !== 'object' || Array.isArray(raw.answers)) throw Error('Invalid answers');
    const clean = {answers:{}, submitted:raw.submitted===true, attempts:Number.isSafeInteger(raw.attempts)&&raw.attempts>=0?raw.attempts:0, best:Number.isInteger(raw.best)&&raw.best>=0&&raw.best<=25?raw.best:0};
    for (const q of bank.questions) {
      const a = raw.answers[q.id];
      if (Number.isInteger(a) && a>=0 && a<q.options.length) clean.answers[q.id]=a;
    }
    if (Object.keys(clean.answers).length!==25) clean.submitted=false;
    return clean;
  }
  try { const raw=localStorage.getItem(key); if(raw) state=sanitize(JSON.parse(raw)); }
  catch (_) { writable=false; }
  function notice() { byId('examStorage').textContent=writable?'답안과 결과는 이 브라우저에만 저장됩니다.':'브라우저 기록을 읽거나 저장할 수 없습니다. 이번 화면에서만 응시할 수 있으며 창을 닫으면 새 답안이 사라집니다.'; }
  function save() { if(writable) try { localStorage.setItem(key,JSON.stringify(state)); } catch(_){writable=false;} notice(); }
  function correctCount() { return bank.questions.filter(q=>state.answers[q.id]===q.answer).length; }
  function progress() {
    const n=Object.keys(state.answers).length;
    byId('examProgress').textContent=state.submitted?`채점 완료 · ${correctCount()} / 25 정답`:`${n} / 25 응답 · ${25-n}문항 남음`;
    const action=document.querySelector('.exam-toolbar a');action.href=state.submitted?'#examResult':'#examSubmit';action.textContent=state.submitted?'결과로 ↑':'제출 위치로 ↓';
    document.querySelectorAll('[data-question-link]').forEach((a,i)=>{
      const answered=Number.isInteger(state.answers[a.dataset.questionLink]);
      a.classList.toggle('is-answered',answered);
      a.setAttribute('aria-label',`${i+1}번 ${answered?'응답 완료':'미응답'}`);
    });
  }
  function text(tag, content) { const e=document.createElement(tag); e.textContent=content; return e; }
  function showResult() { byId('examResult').focus();byId('examResult').scrollIntoView?.({block:'start',behavior:'instant'}); }
  function results() {
    const score=correctCount();
    byId('examScore').textContent=`${score*4}점 · ${score} / 25 정답`;
    byId('examHistory').textContent=`완료한 응시 ${state.attempts}회 · 최고 ${state.best*4}점`;
    const breakdown=byId('examBreakdown');breakdown.replaceChildren();
    for(const [lesson,title] of Object.entries(bank.lessonTitles)) {
      const questions=bank.questions.filter(q=>q.lesson===lesson), right=questions.filter(q=>state.answers[q.id]===q.answer).length;
      const row=text('p',`${title}: ${right} / ${questions.length} 정답 `), a=text('a','강의 복습 →');
      a.href=`../tracks/${lesson.replace('.','/')}.html`;row.append(a);breakdown.append(row);
    }
    for(const field of fields) {
      const q=bank.questions.find(q=>q.id===field.dataset.examQuestion), correct=state.answers[q.id]===q.answer;
      field.dataset.correct=String(correct);
      const explanation=field.querySelector('[data-explanation]');
      const status=text('strong',correct?'정답':'오답');status.className=correct?'exam-correct':'exam-incorrect';
      const chosen=text('p',`내 답: ${state.answers[q.id]+1}. ${q.options[state.answers[q.id]]}`);
      const answer=text('p',`정답: ${q.answer+1}. ${q.options[q.answer]}`);
      const a=text('a',`${bank.lessonTitles[q.lesson]} 복습 →`);a.href=`../tracks/${q.lesson.replace('.','/')}.html`;
      explanation.replaceChildren(status,chosen,answer,text('p',q.explanation),a);explanation.hidden=false;
    }
    byId('examResult').hidden=false;byId('examSubmit').hidden=true;
    root.classList.add('is-review');controls.hidden=true;fields.forEach(field=>field.hidden=false);
    document.querySelectorAll('#examForm input').forEach(input=>input.disabled=true);
  }
  function start() {
    started=true;byId('examIntro').hidden=true;byId('examWorkspace').hidden=false;
    for(const field of fields) for(const input of field.querySelectorAll('input')) input.checked=state.answers[field.dataset.examQuestion]===Number(input.value);
    if(state.submitted) results();else showQuestion(bank.questions.findIndex(q=>!Number.isInteger(state.answers[q.id]))<0?0:bank.questions.findIndex(q=>!Number.isInteger(state.answers[q.id])));progress();notice();
  }
  byId('startExam').hidden=false;
  byId('startExam').textContent=state.submitted?'최근 결과 보기 →':Object.keys(state.answers).length?'이어서 풀기 →':'25문항 시작하기 →';
  byId('startExam').addEventListener('click',()=>{start(); if(state.submitted) showResult(); else fields[0].querySelector('input').focus();});
  byId('examForm').addEventListener('change',event=>{
    if(state.submitted || !event.target.matches('input[type="radio"]'))return;
    state.answers[event.target.name]=Number(event.target.value);byId('examFeedback').textContent='';save();progress();
  });
  byId('examForm').addEventListener('submit',event=>{
    event.preventDefault();if(state.submitted)return;
    const missing=bank.questions.find(q=>!Number.isInteger(state.answers[q.id]));
    if(missing){byId('examFeedback').textContent=`아직 ${25-Object.keys(state.answers).length}문항을 선택하지 않았습니다. 모든 문항에 답한 뒤 제출하세요.`;showQuestion(bank.questions.indexOf(missing),true);return;}
    state.submitted=true;state.attempts++;state.best=Math.max(state.best,correctCount());save();results();progress();showResult();
  });
  byId('wrongOnly').addEventListener('click',()=>{
    wrongOnly=!wrongOnly;fields.forEach(field=>field.hidden=wrongOnly&&field.dataset.correct==='true');
    byId('wrongOnly').setAttribute('aria-pressed',String(wrongOnly));byId('wrongOnly').textContent=wrongOnly?'전체 문항 보기':'오답만 보기';
    byId('examHistory').textContent=wrongOnly&&correctCount()===25?'모든 문항을 맞혔습니다. 다시 확인할 오답이 없습니다.':`완료한 응시 ${state.attempts}회 · 최고 ${state.best*4}점`;
    document.querySelector('.exam-question-map').hidden=wrongOnly;
  });
  byId('retryExam').addEventListener('click',()=>{
    state.answers={};state.submitted=false;wrongOnly=false;
    root.classList.remove('is-review');controls.hidden=false;
    fields.forEach(field=>{field.hidden=false;delete field.dataset.correct;field.querySelector('[data-explanation]').hidden=true;field.querySelector('[data-explanation]').replaceChildren();});
    document.querySelectorAll('#examForm input').forEach(input=>{input.checked=false;input.disabled=false;});
    byId('examResult').hidden=true;byId('examSubmit').hidden=false;byId('examFeedback').textContent='';
    byId('wrongOnly').setAttribute('aria-pressed','false');byId('wrongOnly').textContent='오답만 보기';document.querySelector('.exam-question-map').hidden=false;
    save();progress();showQuestion(0,true);
  });
  // Do not overwrite another tab's newer answers from a stale exam screen.
  window.addEventListener('storage',event=>{if(event.key===key || event.key===null){
    try { const raw=localStorage.getItem(key);state=raw?sanitize(JSON.parse(raw)):{answers:{},submitted:false,attempts:0,best:0}; }
    catch(_){writable=false;notice();return;}
    if(started) window.location.reload();
  }});
  notice();
})();
