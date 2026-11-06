/* Module-level mock exams. Only complete, authored banks become available. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {esc, slug} = require('../js/learning-view.js');
module.exports = ({ROOT, courses, site, fill, write}) => {
  const banks = fs.readdirSync(path.join(ROOT, 'content/exams')).filter(f => f.endsWith('.json'))
    .map(f => JSON.parse(fs.readFileSync(path.join(ROOT, 'content/exams', f), 'utf8')));
  const template = fs.readFileSync(path.join(ROOT, 'templates/study.html'), 'utf8');
  const version = esc(site.contentVersion), routes = [];
  const runtimeVersion = 'exam-ui-' + crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, 'js/exam.js'))).digest('hex').slice(0,12);
  fs.mkdirSync(path.join(ROOT, 'exams'), {recursive:true});
  fs.mkdirSync(path.join(ROOT, 'js/exams'), {recursive:true});
  const lessons = Object.fromEntries(Object.values(courses).flatMap(c => c.modules.flatMap(m => m.lessons.map(l => [l.id,l]))));
  function emit(file, title, description, content, scripts = '') {
    write('exams/' + file, fill(template, {TITLE:esc(title + ' · Bifrost'), DESCRIPTION:esc(description),
      CANONICAL:esc(site.url + 'exams/' + (file === 'index.html' ? '' : file)), SITE_URL:esc(site.url),
      CONTENT_VERSION:version, CONTENT:content, SCRIPTS:`<link rel="stylesheet" href="../css/exams.css?v=${version}">\n${scripts}`}));
    routes.push('exams/' + (file === 'index.html' ? '' : file));
  }
  const total = Object.values(courses).reduce((n,c) => n + c.modules.length, 0);
  emit('index.html', '모듈별 모의고사', '분야와 모듈을 선택해 25문항을 풀고 해설과 복습할 강의를 확인하세요.', `
    <header class="study-hero exam-library-heading"><div class="overline">MY EXAMS</div><h1>모의고사</h1><p>분야와 모듈을 고르고, 배운 내용을 확인하세요.</p></header>
    <div class="exam-catalog-summary"><strong>${Object.keys(courses).length}개 분야 · ${total}개 모듈</strong><span>응시 가능 ${banks.length}개 · 준비 중 ${total-banks.length}개</span></div>
    <div class="exam-library-layout"><nav class="study-jumps exam-field-nav" aria-label="모의고사 분야">${Object.values(courses).map(c => `<a href="#exam-${c.id}">${esc(c.label)}</a>`).join('')}</nav><div class="exam-library-main">
    ${Object.values(courses).map(c => `<section class="study-section" id="exam-${c.id}"><div class="exam-course-heading"><h2>${esc(c.label)}</h2><span>${c.modules.length}개 모듈 · ${c.modules.reduce((n,m)=>n+m.lessons.length,0)}개 차시</span></div><div class="exam-module-grid">${c.modules.map((m,i) => `<article class="exam-module-card ${m.exam?'is-ready':'is-pending'}"><span class="overline">MODULE ${String(i+1).padStart(2,'0')}</span><h3>${esc(m.title.replace(/^\d+\s*·\s*/,''))}</h3><p>${m.lessons.length}개 차시 · 25문항</p><details><summary>출제 범위</summary><ul>${m.lessons.map(l => `<li><a href="../tracks/${c.id}/${slug(l.id)}.html">${esc(l.title)}</a></li>`).join('')}</ul></details>${m.exam?`<a class="learning-button primary" href="${m.exam.id}.html">모의고사 보기 →</a>`:'<p class="exam-pending">준비 중</p>'}</article>`).join('')}</div></section>`).join('')}</div></div>`, `<script src="../js/exam-catalog.js?v=${version}" defer></script>`);
  for (const bank of banks) {
    const c = courses[bank.course], m = c.modules[bank.module-1];
    const content = `<div data-exam="${bank.id}"><nav class="breadcrumb" aria-label="현재 위치"><a href="./">모의고사</a><span>/ ${esc(c.label)} / 모듈 ${bank.module}</span></nav>
      <header class="study-hero"><div class="overline">${esc(c.title)} / MODULE ${String(bank.module).padStart(2,'0')}</div><h1>${esc(bank.title)}</h1><p>25문항 · 4지선다 · 문항당 4점 · 시간 제한 없음</p></header>
      <section id="examIntro" class="study-section"><h2>응시 전 확인</h2><p>25문항을 모두 선택한 뒤 제출하면 채점합니다. 정답과 해설은 제출 후 공개되며, 시험 중 답은 바꿀 수 있습니다.</p><p>답안과 최근 결과·최고 점수는 이 브라우저에 저장됩니다. 새로고침 후에도 이어서 풀 수 있습니다. 강의 진도와 별도로 기록합니다.</p><details><summary>출제 범위 · ${m.lessons.length}개 차시</summary><ul>${m.lessons.map(l=>`<li><a href="../tracks/${c.id}/${slug(l.id)}.html">${esc(l.title)}</a></li>`).join('')}</ul></details><button class="learning-button primary js-only" hidden type="button" id="startExam">25문항 시작하기 →</button></section>
      <noscript><p>모의고사 응시·채점에는 JavaScript가 필요합니다. 출제 범위의 강의와 실습 자료는 그대로 이용할 수 있습니다.</p></noscript>
      <p id="examStorage" class="caption" role="status"></p>
      <div id="examWorkspace" hidden><aside class="exam-toolbar"><p id="examProgress" role="status" aria-live="polite"></p><a href="#examSubmit">제출 위치로 ↓</a></aside>
      <nav class="exam-question-map" aria-label="문항 바로가기">${bank.questions.map((q,i)=>`<a href="#exam-q-${q.id}" data-question-link="${q.id}" aria-label="${i+1}번 미응답">${i+1}</a>`).join('')}</nav>
      <section id="examResult" class="exam-result" hidden tabindex="-1" aria-labelledby="examResultTitle"><h2 id="examResultTitle">모의고사 결과</h2><p id="examScore" class="exam-score"></p><p id="examHistory"></p><div id="examBreakdown"></div><div class="exam-result-actions"><button type="button" class="learning-button" id="wrongOnly" aria-pressed="false">오답만 보기</button><button type="button" class="learning-button primary" id="retryExam">다시 풀기</button><a href="./">모의고사 목록 →</a></div><p>같은 25문항으로 재응시합니다. 아래 해설과 연결된 강의를 복습해 보세요.</p></section>
      <form id="examForm"><div id="examQuestions">${bank.questions.map((q,i)=>`<fieldset class="exam-question" id="exam-q-${q.id}" data-exam-question="${q.id}"><legend><span class="overline">QUESTION ${String(i+1).padStart(2,'0')}</span><span class="exam-prompt">${i+1}. ${esc(q.prompt)}</span></legend>${q.code?`<pre class="exam-code"><code>${esc(q.code)}</code></pre>`:''}${q.options.map((o,n)=>`<label class="exam-option"><input type="radio" name="${q.id}" value="${n}"><span><b>${n+1}</b> ${esc(o)}</span></label>`).join('')}<div class="exam-explanation" data-explanation="${q.id}" hidden></div></fieldset>`).join('')}</div><div id="examSubmit" class="exam-submit"><p id="examFeedback" role="status" aria-live="polite"></p><button type="submit" class="learning-button primary" id="submitExam">25문항 제출하고 채점하기</button></div></form></div></div>`;
    // Each detail page loads only its own question bank.
    write(`js/exams/${bank.id}.js`, '/* Generated from content/exams; do not edit. */\nwindow.BifrostExam = ' + JSON.stringify({...bank,lessonTitles:Object.fromEntries(m.lessons.map(l=>[l.id,l.title]))}) + ';\n');
    const bankVersion = 'exam-' + crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, `js/exams/${bank.id}.js`))).digest('hex').slice(0,12);
    emit(bank.id+'.html', bank.title+' 모의고사', `${c.label} 모듈 ${bank.module} · 25문항 모의고사`, content,
      `<script src="../js/exams/${bank.id}.js?v=${bankVersion}" defer></script>\n<script src="../js/exam.js?v=${runtimeVersion}" defer></script>`);
  }
  return routes;
};
