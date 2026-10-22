/* Course and lesson views share content, navigation and progress. No build/runtime framework. */
(() => {
  'use strict';
  const courses = window.BifrostCourses;
  const progress = window.BifrostProgress;
  const visuals = window.BifrostVisuals;
  const key = document.body.dataset.course;
  const course = courses[key];
  const root = document.getElementById('learningContent');
  const introductionMarkup = document.getElementById('courseIntroduction')?.outerHTML || '';
  if (!course || !root) return;
  const all = c => c.modules.flatMap(m => m.lessons);
  const lessons = all(course);
  const lookup = Object.fromEntries(Object.values(courses).flatMap(c => all(c).map(l => [l.id, { course: c, lesson: l }])));
  const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const lessonHref = (id, fromKey = key) => {
    const owner = lookup[id]?.course.id;
    return owner ? `${owner === fromKey ? '' : `../${owner}/`}lesson.html?id=${encodeURIComponent(id)}` : './';
  };
  const colors = { foundation: 'cyan', web: 'blue', pwn: 'violet', rev: 'red', forensic: 'green', network: 'amber', crypto: 'pink', misc: 'orange', cloud: 'sky' };
  document.body.style.setProperty('--course-accent', `var(--map-${colors[key]})`);
  const sources = () => `<ul class="source-list">${course.sources.map(([title, url]) => `<li><a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(title)} ↗</a></li>`).join('')}</ul><p class="caption">무료로 읽을 수 있는 공식 참고 문서입니다. 영문 문서는 이 강의의 설명을 보충하는 용도로 사용하세요.</p>`;
  const stats = () => `<div class="course-stats"><span data-count="${key}"></span><div class="course-meter" role="progressbar" aria-label="${esc(course.title)} 완료 진도" aria-valuemin="0" aria-valuemax="100" data-meter="${key}"><span></span></div></div>`;
  const backup = () => `<section class="storage-panel" aria-label="브라우저 진도 저장"><strong>내 브라우저에 저장되는 학습 기록</strong><p id="storageNotice"></p><p id="legacyNotice"></p><div class="backup-actions"><button class="learning-button small" type="button" id="exportProgress">진도 백업 받기</button><label class="learning-button small import-label">백업 합쳐서 가져오기<input type="file" id="importProgress" accept="application/json,.json"></label></div><p class="caption">같은 사이트·브라우저에서 공유합니다. 다른 기기와 자동 동기화되지 않습니다. 가져오기는 완료 기록을 합치며 현재 완료 기록을 지우지 않습니다.</p><p class="feedback" role="status" id="backupFeedback"></p></section>`;
  const prereqs = () => course.prereqs.length ? `<section class="prereq-panel"><div class="overline">BEFORE YOU START</div><h2>막히면 연결해서 볼 기초</h2><p>이미 알고 있다면 바로 시작하세요. 선행 차시를 완료하지 않아도 강의를 열 수 있습니다.</p><ul>${course.prereqs.map(id => `<li><a href="${lessonHref(id)}">${esc(lookup[id].course.label)} · ${esc(lookup[id].lesson.title)} ↗</a></li>`).join('')}</ul></section>` : `<section class="prereq-panel"><div class="overline">START HERE</div><h2>처음이어도 괜찮습니다</h2><p>환경 준비부터 순서대로 진행합니다. 이미 익숙한 차시는 건너뛰고 관심 분야와 병행하세요.</p><a href="../../guides/linux.html">Windows에서 Linux 시작하기 ↗</a></section>`;
  const files = lesson => `<section id="materials" class="materials"><div><div class="overline">PRACTICE FILES</div><h2>실습 자료</h2><p>ZIP을 먼저 풀고 README를 확인하세요. 같은 폴더의 파일을 함께 유지합니다.</p></div><a class="learning-button" href="../../labs/${key}.zip" download>전체 실습 ZIP 받기 ↓</a>${lesson.files.length ? `<ul>${lesson.files.map(name => `<li><a href="../../labs/${key}/${encodeURIComponent(name)}" download>${esc(name)} ↓</a></li>`).join('')}</ul>` : '<p class="caption">이 차시는 본문의 코드·설계 예제로 진행합니다. 분야 전체 자료도 내려받을 수 있습니다.</p>'}</section>`;
  const firstIncomplete = () => lessons.find(l => !progress.has(l.id));
  function outline(current) {
    return `<aside class="course-sidebar"><a class="back-link" href="./">← ${esc(course.title)} 전체 과정</a>${stats()}<nav aria-label="차시 목차">${course.modules.map((m, mi) => `<details ${m.lessons.some(l => l.id === current) ? 'open' : ''}><summary>${esc(m.title)}<span class="caption" data-module-count="${mi}"></span></summary><ol>${m.lessons.map(l => `<li><a class="side-lesson" href="${lessonHref(l.id)}" ${current === l.id ? 'aria-current="page"' : ''}><span class="lesson-dot" data-dot="${l.id}" aria-hidden="true"></span><span>${esc(l.title)}<small class="completion-label" data-completion="${l.id}"></small></span></a></li>`).join('')}</ol></details>`).join('')}</nav><a class="back-link" href="../../index.html#mindmap">모든 분야 보기 ↗</a></aside>`;
  }
  function renderOverview() {
    root.innerHTML = `<nav class="breadcrumb" aria-label="현재 위치"><a href="../../index.html#mindmap">학습 지도</a><span aria-hidden="true">/</span><span aria-current="page">${esc(course.title)}</span></nav>
      <section class="course-hero"><div><div class="overline">${esc(document.body.dataset.courseNumber)} / LEARNING PATH</div><h1>${esc(course.title)}</h1><p class="course-lead">${esc(course.subtitle)}</p><div class="course-chips"><span>${esc(course.level)}</span><span>${course.modules.length}개 모듈 · ${lessons.length}개 차시</span><span>설명 → 실습 → 검증</span></div></div><div class="continue-panel"><div class="overline">YOUR PROGRESS</div>${stats()}<a class="learning-button primary" id="continueLearning" href="${lessonHref(lessons[0].id)}">첫 차시 시작하기 →</a><p class="caption">완료 표시는 직접 합니다. 학습 속도와 설치 시간은 환경에 따라 다릅니다.</p></div></section>
      <nav class="course-jump-links" aria-label="과정 안내 바로가기"><a href="#courseIntroduction">분야 소개 ↓</a><a href="#courseModules">강의 목차 바로 보기 ↓</a></nav>
      ${introductionMarkup}
      ${visuals?.renderCourse(key) || ''}
      <div class="overview-layout"><div><section class="outcome-panel"><div class="overline">WHAT YOU WILL BUILD</div><h2>이 과정을 마치면</h2><p>${esc(course.outcome)}</p></section><section class="module-list" id="courseModules" aria-label="모듈별 차시">${course.modules.map((m, mi) => `<section class="module-card"><div class="module-heading"><h2>${esc(m.title)}</h2><span class="caption" data-module-count="${mi}"></span></div><p>${esc(m.intro)}</p><ol>${m.lessons.map(l => `<li><a class="lesson-row" href="${lessonHref(l.id)}"><span class="lesson-dot" data-dot="${l.id}" aria-hidden="true"></span><span><strong>${esc(l.title)}</strong><small>${esc(l.goal)}</small><small class="completion-label" data-completion="${l.id}"></small></span><span aria-hidden="true">↗</span></a></li>`).join('')}</ol></section>`).join('')}</section></div><aside class="overview-aside">${prereqs()}<section class="prereq-panel"><div class="overline">OFFLINE LAB</div><h2>자료를 먼저 챙겨두기</h2><p>예제와 분석 자료는 이 사이트에서 내려받습니다. 외부 계정이나 유료 실습 서버가 필요하지 않습니다.</p><a class="learning-button" href="../../labs/${key}.zip" download>${esc(course.title)} ZIP ↓</a></section></aside></div>
      <section class="reference-panel"><h2>더 알아보기</h2>${sources()}</section>${backup()}`;
  }
  function renderLesson() {
    const id = new URLSearchParams(location.search).get('id');
    const lesson = lessons.find(l => l.id === id);
    if (!lesson) {
      document.title = '차시를 찾을 수 없습니다 — Bifrost';
      root.innerHTML = `<section class="not-found"><div class="overline">LESSON NOT FOUND</div><h1>차시를 찾을 수 없습니다</h1><p>주소의 차시 ID를 확인하거나 전체 목차에서 다시 선택하세요.</p><a class="learning-button primary" href="./">${esc(course.title)} 목차로 →</a></section>`;
      return;
    }
    const index = lessons.indexOf(lesson);
    const module = course.modules.find(m => m.lessons.includes(lesson));
    document.title = `${lesson.title} — ${course.title} · Bifrost`;
    document.querySelector('meta[name="description"]').content = lesson.goal;
    root.innerHTML = `<nav class="breadcrumb" aria-label="현재 위치"><a href="../../index.html#mindmap">학습 지도</a><span aria-hidden="true">/</span><a href="./">${esc(course.title)}</a><span aria-hidden="true">/</span><span aria-current="page">${index + 1}차시</span></nav><div class="lesson-layout">${outline(id)}<article class="lesson-article"><header class="lesson-heading"><div class="overline">${esc(module.title)} · ${index + 1} / ${lessons.length}</div><h1>${esc(lesson.title)}</h1><p class="lesson-objective">${esc(lesson.goal)}</p></header><nav class="article-steps" aria-label="본문 바로가기"><a href="#concept">01 이해</a><a href="#worked">02 따라하기</a><a href="#practice">03 직접 변경</a><a href="#verify">04 검증</a></nav>
      ${id === 'foundation.environment' ? '<p class="environment-note">Windows에 Ubuntu가 없다면 <a href="../../guides/linux.html">Linux 시작 가이드</a>부터 확인하세요. 아래 설치 명령은 Ubuntu 터미널용입니다.</p>' : ''}
      <section id="concept" class="article-section"><div class="overline">01 / UNDERSTAND</div><h2>먼저 이해하기</h2>${lesson.concepts.map((p, i) => `<p>${esc(p)}</p>${i === 0 ? (visuals?.renderLesson(id) || '') : ''}`).join('')}</section>
      ${files(lesson)}<section id="worked" class="article-section"><div class="overline">02 / WORKED EXAMPLE</div><h2>따라 하며 관찰하기</h2><p class="environment-note">Python은 Linux·WSL·macOS에서 <code>python3</code>, Windows PowerShell에서 <code>py -3</code>를 사용합니다. C·Linux 명령은 Ubuntu/WSL 기준입니다. 다운로드한 분야 폴더에서 실행하세요.</p><div class="code-shell"><div class="code-toolbar"><span>예제 · 명령 또는 관찰 절차</span><button type="button" id="copyExample">복사</button></div><pre><code id="exampleCode">${esc(lesson.code)}</code></pre></div><div class="expected-output"><h3>예상 결과와 해석</h3><pre>${esc(lesson.expected)}</pre></div></section>
      <section id="practice" class="article-section"><div class="overline">03 / TRY IT YOURSELF</div><h2>직접 바꾸고 확인하기</h2><p>${esc(lesson.task)}</p><details class="hint"><summary>막혔을 때 힌트 보기</summary><p>${esc(lesson.hint)}</p></details><p class="record-prompt">학습 기록: 사용한 환경과 명령 → 바꾸기 전 예상 → 실제 결과 → 차이의 이유를 남기세요.</p></section>
      <section id="verify" class="article-section completion-panel"><div class="overline">04 / VERIFY</div><h2>이 정도면 다음으로</h2><ul class="evidence-list">${lesson.checks.map(c => `<li>${esc(c)}</li>`).join('')}</ul><p>위 기준을 결과물로 확인한 뒤 완료로 표시하세요. 자동 채점이나 다음 차시 잠금은 없습니다.</p><button type="button" class="learning-button primary" id="completeLesson" aria-pressed="false">이 차시 완료로 표시</button><p class="feedback" role="status" id="completionFeedback"></p></section>
      <nav class="lesson-pagination" aria-label="이전·다음 차시">${index > 0 ? `<a href="${lessonHref(lessons[index - 1].id)}"><small>← 이전 차시</small>${esc(lessons[index - 1].title)}</a>` : '<a href="./"><small>← 전체 과정</small>분야 목차로</a>'}${index < lessons.length - 1 ? `<a href="${lessonHref(lessons[index + 1].id)}"><small>다음 차시 →</small>${esc(lessons[index + 1].title)}</a>` : `<a href="./"><small>과정 돌아보기 →</small>${esc(course.title)} 목차</a>`}</nav><section class="reference-panel"><h2>더 알아보기</h2>${sources()}</section>${backup()}</article></div>`;
    progress.visit(id);
    document.getElementById('completeLesson').addEventListener('click', () => {
      const done = !progress.has(id);
      progress.set(id, done);
      document.getElementById('completionFeedback').textContent = progress.available() ? (done ? '완료로 저장했습니다. 다음 차시에서 이어가세요.' : '완료 표시를 해제했습니다.') : '화면에는 반영했지만 브라우저 저장에 실패했습니다. 진도를 백업해 두세요.';
    });
    document.getElementById('copyExample').addEventListener('click', async event => {
      try { await navigator.clipboard.writeText(lesson.code); event.target.textContent = '복사됨'; }
      catch (_) { event.target.textContent = '코드를 선택해 복사하세요'; }
    });
  }
  function updateProgress() {
    document.querySelectorAll('[data-count]').forEach(el => {
      const c = courses[el.dataset.count], ls = all(c), count = progress.count(ls);
      el.textContent = `${count} / ${ls.length} 완료 · ${Math.round(count / ls.length * 100)}%`;
    });
    document.querySelectorAll('[data-meter]').forEach(el => {
      const ls = all(courses[el.dataset.meter]), percent = Math.round(progress.count(ls) / ls.length * 100);
      el.setAttribute('aria-valuenow', String(percent));
      el.firstElementChild.style.width = `${percent}%`;
    });
    document.querySelectorAll('[data-module-count]').forEach(el => {
      const ls = course.modules[Number(el.dataset.moduleCount)].lessons;
      el.textContent = `${progress.count(ls)} / ${ls.length} 완료`;
    });
    document.querySelectorAll('[data-dot]').forEach(el => el.classList.toggle('is-complete', progress.has(el.dataset.dot)));
    document.querySelectorAll('[data-completion]').forEach(el => { el.textContent = progress.has(el.dataset.completion) ? '완료' : '미완료'; });
    const continueLink = document.getElementById('continueLearning');
    if (continueLink) {
      const last = lessons.find(l => l.id === progress.last() && !progress.has(l.id));
      const next = last || firstIncomplete();
      continueLink.href = lessonHref(next ? next.id : lessons[0].id);
      continueLink.textContent = next ? `${progress.count(lessons) || last ? '이어서' : '첫 차시'} 학습하기 →` : '완료한 과정 다시 보기 →';
    }
    const complete = document.getElementById('completeLesson');
    if (complete) {
      const done = progress.has(new URLSearchParams(location.search).get('id'));
      complete.setAttribute('aria-pressed', String(done));
      complete.textContent = done ? '✓ 완료됨 · 표시 해제' : '이 차시 완료로 표시';
    }
    const storage = document.getElementById('storageNotice');
    if (storage) storage.textContent = progress.available() ? '진도는 이 브라우저의 로컬 저장소에 저장됩니다. 브라우저 데이터 삭제 전에 백업하세요.' : '브라우저 저장소를 사용할 수 없습니다. 이번 화면의 기록이 사라지기 전에 백업을 받아 두세요.';
    const legacy = document.getElementById('legacyNotice');
    if (legacy) legacy.textContent = progress.legacyCount() ? `이전 버전의 완료 기록 ${progress.legacyCount()}건을 보관했습니다. 대응되는 차시만 옮겼고, 확장·재구성된 차시는 새로 확인합니다. Crypto의 도구·문제 분류·풀이 기록은 Misc로 이동했습니다.` : '';
  }
  if (document.body.dataset.view === 'lesson') renderLesson(); else renderOverview();
  const exportButton = document.getElementById('exportProgress');
  if (exportButton) exportButton.addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([progress.export()], { type: 'application/json' }));
    const a = document.createElement('a'); a.href = url; a.download = 'bifrost-progress.json'; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    document.getElementById('backupFeedback').textContent = '진도를 JSON 파일로 내보냈습니다.';
  });
  const importInput = document.getElementById('importProgress');
  if (importInput) importInput.addEventListener('change', async () => {
    const feedback = document.getElementById('backupFeedback');
    try {
      const file = importInput.files[0];
      if (!file) return;
      if (file.size > 1000000) throw new Error('진도 파일은 1MB 이하여야 합니다.');
      progress.import(await file.text());
      feedback.textContent = progress.available() ? '완료 기록을 합쳐서 저장했습니다.' : '완료 기록을 합쳤지만 브라우저 저장에 실패했습니다. 다시 백업하세요.';
    } catch (_) { feedback.textContent = '가져올 수 없습니다. 이 사이트에서 받은 1MB 이하 진도 JSON 파일인지 확인하세요.'; }
    importInput.value = '';
  });
  window.addEventListener('bifrost-progress', updateProgress);
  updateProgress();
})();
