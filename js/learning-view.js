/* Pure HTML views: shared by the static build and browser's legacy URL support. */
((host) => {
  'use strict';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const all = course => course.modules.flatMap(module => module.lessons);
  const slug = id => id.slice(id.indexOf('.') + 1);

  function create(courses, visuals, route = null) {
    const lookup = Object.fromEntries(Object.values(courses).flatMap(course =>
      all(course).map(lesson => [lesson.id, { course, lesson }])));

    function lessonHref(id, fromKey) {
      const owner = lookup[id]?.course.id;
      if (route) return route.sequence.includes(id) ? `${id}.html` : `../../tracks/${owner}/${slug(id)}.html`;
      return owner ? `${owner === fromKey ? '' : `../${owner}/`}${slug(id)}.html` : './';
    }

    function sources(references) {
      return `<ul class="source-list">${references.map(([title, url]) => `
        <li><a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(title)} ↗</a></li>`).join('')}
      </ul><p class="caption">무료로 읽는 공식 참고 문서입니다. 필요한 절을 찾아 본문의 설명과 함께 확인하세요.</p>`;
    }

    function stats(course) {
      return `<div class="course-stats"><span data-count="${course.id}"></span>
        <div class="course-meter" role="progressbar" aria-label="${esc(course.title)} 완료 진도" aria-valuemin="0" aria-valuemax="100" data-meter="${course.id}"><span></span></div>
      </div>`;
    }

    function backup() {
      return `<details class="storage-panel js-only" hidden aria-label="브라우저 진도 저장"><summary>학습 기록 · 백업과 가져오기</summary>
        <strong>내 브라우저에 저장되는 학습 기록</strong><p id="storageNotice"></p><p id="legacyNotice"></p>
        <div class="backup-actions"><button class="learning-button small" type="button" id="exportProgress">진도 백업 받기</button>
          <label class="learning-button small import-label">백업 합쳐서 가져오기<input type="file" id="importProgress" accept="application/json,.json"></label></div>
        <p class="caption">같은 사이트·브라우저에서 공유합니다. 다른 기기와 자동 동기화되지 않습니다. 가져오기는 완료 기록을 합치며 현재 완료 기록을 지우지 않습니다.</p>
        <p class="feedback" role="status" id="backupFeedback"></p></details>`;
    }

    function prerequisites(ids, key, lesson = false) {
      if (!ids.length) return `<p class="caption">${lesson ? '별도 선행 차시 없이 시작할 수 있습니다.' : '환경 준비부터 시작합니다. 익숙한 차시는 건너뛰어도 됩니다.'}</p>`;
      return `<p class="caption">막히는 개념만 연결해서 복습하세요. 선행 차시 완료 여부로 강의를 잠그지 않습니다.</p>
        <ul>${ids.map(id => `<li><a href="${lessonHref(id, key)}">${esc(lookup[id].course.label)} · ${esc(lookup[id].lesson.title)} ↗</a></li>`).join('')}</ul>`;
    }

    function introduction(course) {
      const field = course.introduction;
      return `<section class="course-introduction" id="courseIntroduction" aria-label="분야 소개">
        <div class="field-guide-card"><div class="field-guide-top"><span class="field-index">${course.number}</span><h2>${esc(course.title)}</h2></div>
          <p class="field-question">${esc(field.question)}</p><dl>${field.items.map(item => `<dt>${esc(item.label)}</dt><dd>${esc(item.text)}</dd>`).join('')}</dl>
          <div class="field-path"><b>학습 경로</b> ${esc(field.path)}</div>
        </div></section>`;
    }

    function files(course, lesson) {
      return `<section id="materials" class="materials">
        <div><div class="overline">PRACTICE FILES</div><h2>실습 자료</h2><p>ZIP을 먼저 풀고 README를 확인하세요. 같은 폴더의 파일을 함께 유지합니다.</p></div>
        <a class="learning-button" href="../../labs/${course.id}.zip" download>전체 실습 ZIP 받기 ↓</a>
        ${lesson.files.length ? `<ul>${lesson.files.map(name => `<li><a href="../../labs/${course.id}/${encodeURIComponent(name)}" download>${esc(name)} ↓</a></li>`).join('')}</ul>` : '<p class="caption">이 차시는 본문의 코드·설계 예제로 진행합니다.</p>'}
      </section>`;
    }

    function outline(course, current) {
      const groups = [];
      if (route) route.sequence.forEach((id,index)=>{
        const owner=lookup[id].course;
        if (groups.at(-1)?.course!==owner) groups.push({course:owner,items:[]});
        groups.at(-1).items.push({id,index});
      });
      if (route) return `<aside class="course-sidebar path-sidebar"><a class="back-link" href="./">← ${esc(route.title)} 목차</a>
        <div class="course-stats"><span data-path-count></span><div class="course-meter" role="progressbar" aria-label="${esc(route.title)} 차시 완료 진도" aria-valuemin="0" aria-valuemax="100" data-path-meter><span></span></div></div>
        <nav aria-label="${esc(route.title)} 경로 목차">${groups.map(group=>`<details ${group.items.some(item=>item.id===current)?'open':''}><summary>${esc(group.course.title)}<span class="caption">${group.items[0].index+1}–${group.items.at(-1).index+1}단계</span></summary><ol>${group.items.map(({id,index})=>`<li><a class="side-lesson" href="${lessonHref(id)}" ${current===id?'aria-current="page"':''}>
          <span class="path-step-number">${index+1}</span><span><small>${esc(lookup[id].course.label)} · ${route.lessons.includes(id)?'경로 핵심':'권장 선행'}</small>${esc(lookup[id].lesson.title)}<small class="completion-label" data-completion="${id}"></small></span></a></li>`).join('')}
          </ol></details>`).join('')}<a class="side-lesson path-project-link" href="project.html"><span class="path-step-number">✦</span><span>마지막 · 종합 프로젝트</span></a></nav>
        <a class="back-link" href="../../learn/#paths">다른 학습 경로 보기 ↗</a></aside>`;
      return `<aside class="course-sidebar"><a class="back-link" href="./">← ${esc(course.title)} 전체 과정</a>${stats(course)}
        <nav aria-label="차시 목차">${course.modules.map((module, index) => `
          <details ${module.lessons.some(lesson => lesson.id === current) ? 'open' : ''}>
            <summary>${esc(module.title)}<span class="caption" data-module-count="${index}"></span></summary>
            <ol>${module.lessons.map(lesson => `<li><a class="side-lesson" href="${lessonHref(lesson.id, course.id)}" ${current === lesson.id ? 'aria-current="page"' : ''}>
              <span class="lesson-dot" data-dot="${lesson.id}" aria-hidden="true"></span><span>${esc(lesson.title)}<small class="completion-label" data-completion="${lesson.id}"></small></span></a></li>`).join('')}</ol>
          </details>`).join('')}</nav><a class="back-link" href="../../index.html#mindmap">모든 분야 보기 ↗</a>
      </aside>`;
    }

    function overview(key) {
      const course = courses[key], lessons = all(course);
      return `<nav class="breadcrumb" aria-label="현재 위치"><a href="../../index.html#mindmap">학습 지도</a><span aria-hidden="true">/</span><span aria-current="page">${esc(course.title)}</span></nav>
        <section class="course-hero"><div class="course-hero-intro"><div class="course-hero-copy"><div class="overline">${course.number} / LEARNING PATH</div><h1>${esc(course.title)}</h1>
          <p class="course-lead">${esc(course.subtitle)}</p><div class="course-chips"><span>${esc(course.level)}</span><span>${course.modules.length}개 모듈 · ${lessons.length}개 차시</span><span>설명 → 실습 → 검증</span></div></div><img class="course-hero-art" src="../../assets/illustrations/${key}.webp" width="480" height="480" alt="" decoding="async"></div>
          <div class="continue-panel"><div class="overline">YOUR PROGRESS</div>${stats(course)}<a class="learning-button primary" id="continueLearning" href="${lessonHref(lessons[0].id, key)}">첫 차시 시작하기 →</a><p class="caption">완료 표시는 직접 합니다. 학습 속도와 설치 시간은 환경에 따라 다릅니다.</p></div>
        </section>
        <nav class="course-jump-links" aria-label="과정 안내 바로가기"><a href="#courseIntroduction">분야 소개 ↓</a><a href="#courseModules">강의 목차 바로 보기 ↓</a></nav>
        ${introduction(course)}${visuals.renderCourse(key)}
        <section class="learning-path-panel"><div><span class="overline">LEARN → APPLY → EXPLAIN</span><h2>이 과정의 완주 기준</h2><p>차시별 독립 과제에서 조건을 바꿔 보고, 마지막에는 두 표본을 분석한 결과와 근거 보고서를 완성합니다.</p></div><a class="learning-button" href="../../learn/">차시 검색 · 목표별 경로 ↗</a></section>
        <div class="overview-layout"><div>
          <section class="outcome-panel"><div class="overline">WHAT YOU WILL BUILD</div><h2>이 과정을 마치면</h2><p>${esc(course.outcome)}</p></section>
          <section class="module-list" id="courseModules" aria-label="모듈별 차시">${course.modules.map((module, index) => `
            <section class="module-card"><div class="module-heading"><h2>${esc(module.title)}</h2><span class="caption" data-module-count="${index}"></span></div><p>${esc(module.intro)}</p>
              <ol>${module.lessons.map(lesson => `<li><a class="lesson-row" href="${lessonHref(lesson.id, key)}"><span class="lesson-dot" data-dot="${lesson.id}" aria-hidden="true"></span>
                <span><strong>${esc(lesson.title)}</strong><small>${esc(lesson.goal)}</small><small class="completion-label" data-completion="${lesson.id}"></small></span><span aria-hidden="true">↗</span></a></li>`).join('')}</ol>
            </section>`).join('')}</section>
          ${course.project ? `<section class="project-callout" id="finalProject"><span class="overline">FINAL PROJECT</span><h2>${esc(course.project.title)}</h2><p>${esc(course.project.problem)}</p><p class="caption">${course.project.minutes.join('–')}분 · 설치 제외 저자 추정 · A/B 표본 + 결과 검사 + 보고서 평가</p><a class="learning-button primary" href="../../projects/${key}.html">종합 프로젝트 시작하기 →</a></section>` : ''}</div>
          <aside class="overview-aside"><section class="prereq-panel"><div class="overline">BEFORE YOU START</div><h2>막히면 연결해서 볼 기초</h2>${prerequisites(course.prereqs, key)}
            ${key === 'foundation' ? '<a href="../../guides/linux.html">Windows에서 Linux 시작하기 ↗</a>' : ''}</section>
            <section class="prereq-panel"><div class="overline">OFFLINE LAB</div><h2>자료를 먼저 챙겨두기</h2><p>예제와 분석 자료는 이 사이트에서 내려받습니다. 외부 계정이나 유료 실습 서버가 필요하지 않습니다.</p><a class="learning-button" href="../../labs/${key}.zip" download>${esc(course.title)} ZIP ↓</a></section>
          </aside></div>
        <section class="reference-panel"><h2>더 알아보기</h2>${sources(course.sources)}</section>${backup()}`;
    }

    function codeBlock(code, id, label = '예제 · 명령 또는 관찰 절차', copy = false) {
      return `<div class="code-shell"><div class="code-toolbar"><span>${esc(label)}</span>${copy ? '<button class="js-only" hidden type="button" id="copyExample">복사</button>' : ''}</div><pre><code${id ? ` id="${id}"` : ''}>${esc(code)}</code></pre></div>`;
    }

    function walkthrough(lesson) {
      if (!lesson.walkthrough?.length) return '';
      return `<ol class="walkthrough">${lesson.walkthrough.map(step => `<li><h3>${esc(step.title.replace(/^\d+[.)]\s*/, ''))}</h3><p>${esc(step.explanation)}</p>
        ${step.code ? codeBlock(step.code, '', step.context || `부분 예제 · ${lesson.environment.label} · 앞 단계의 변수·폴더 유지`) : ''}${step.expected ? `<div class="step-observation"><strong>관찰할 결과</strong><pre>${esc(step.expected)}</pre></div>` : ''}</li>`).join('')}</ol>`;
    }

    function learningPlan(lesson) {
      const plan = lesson.learning;
      if (!plan) return '';
      return `<div class="lesson-meta"><span>${esc(plan.level)}</span><span>학습 ${plan.minutes.join('–')}분</span><span>처음 준비 ${plan.setup.join('–')}분</span></div>
        <p class="caption">시간은 설치 경험에 따라 달라지는 저자 추정입니다. 목표별 경로에서 핵심 차시를 고르거나 이 분야를 순서대로 진행하세요.</p>
        <details class="readiness"><summary>시작 전, 내 준비 상태 확인하기</summary><p>${esc(plan.readiness)}</p><details><summary>판단 기준과 보충 자료</summary><p>${esc(plan.readinessAnswer)}</p><a href="../../guides/bridges.html#${esc(plan.bridge)}">막힌 기초를 짧게 연결하기 ↗</a></details></details>`;
    }

    function transfer(lesson) {
      if (!lesson.learning) return '';
      const plan = lesson.learning;
      return `<section class="transfer-panel" id="transfer"><div class="overline">INDEPENDENT PRACTICE</div><h3>도움 없이, 조건을 바꿔 보기</h3>
        <p>${esc(plan.challenge)}</p><ol><li>위 해설을 닫고 예상 결과와 근거를 먼저 적습니다.</li><li>코드·원시 자료·문서 근거로 확인하고 예상과 실제 차이를 설명합니다.</li><li>새 반례 하나를 만들고 무엇까지 확인했는지 기록합니다.</li></ol>
        <details class="hint"><summary>시도한 뒤 판단 기준 읽기</summary><p>${esc(plan.answer)}</p></details>
        <div class="rubric-table-wrap"><table class="rubric-table"><caption>이 차시의 자기 평가 · 체크 여부는 실력 인증이 아닙니다</caption><thead><tr><th scope="col">확인할 역량</th><th scope="col">남길 근거</th></tr></thead><tbody>
          <tr><th scope="row">개념</th><td>${esc(lesson.checks[0])} — 자기 말로 설명</td></tr>
          <tr><th scope="row">실행·관찰</th><td>${esc(lesson.checks[1])} — 명령·입력·출력 또는 자료 위치</td></tr>
          <tr><th scope="row">조건 변경</th><td>독립 과제의 예상과 결과, 판단 기준과 다른 점</td></tr>
          <tr><th scope="row">한계·전이</th><td>새 반례, 확정할 수 없는 결론, 다음 확인 자료</td></tr></tbody></table></div>
        <p class="caption">각 항목: 0 근거 없음 · 1 설명만 가능 · 2 재현 근거 있음. 모든 항목의 근거를 갖추는 것을 목표로 하세요. 1–3일 뒤 예제를 닫고 다시 풀어보세요.</p>
        <a href="../../labs/${lesson.id.split('.')[0]}/lesson-workbook.md" download>이 분야의 과제 기록 양식 받기 ↓</a></section>`;
    }

    function questions(lesson) {
      return `<div class="self-check"><h3>이해한 내용을 점검하기</h3><p>답을 고른 뒤 이유까지 확인하세요. 점수는 저장하지 않습니다.</p>
        ${(lesson.questions || []).map((question, index) => `<fieldset class="question" data-question="${index}">
          <legend>${index + 1}. ${esc(question.prompt)}</legend>
          ${question.options.map((option, n) => `<label class="question-option"><input type="radio" name="question-${index}" value="${n}"><span>${esc(option)}</span></label>`).join('')}
          <button class="learning-button small js-only" hidden type="button" data-check-question="${index}">답 확인</button>
          <p class="question-feedback feedback" role="status" id="questionFeedback${index}"></p>
          <details class="question-answer"><summary>정답과 이유 읽기</summary><p><strong>정답: ${esc(question.options[question.answer])}</strong></p><p>${esc(question.explanation)}</p></details>
        </fieldset>`).join('')}</div>`;
    }

    function solution(lesson) {
      if (!lesson.solution) return '';
      return `<details class="solution"><summary>과제 해설과 예시 답안 보기</summary><div class="solution-body">
        <ol>${lesson.solution.approach.map(step => `<li>${esc(step)}</li>`).join('')}</ol>
        ${lesson.solution.code ? codeBlock(lesson.solution.code, '', '예시 답안') : ''}
        <h3>결과를 판단하는 기준</h3><pre>${esc(lesson.solution.expected)}</pre>
      </div></details>`;
    }

    function lessonView(key, id) {
      const course = courses[key], lessons = route ? route.sequence.map(item=>lookup[item].lesson) : all(course), lesson = all(course).find(item => item.id === id);
      if (!lesson) return `<section class="not-found"><div class="overline">LESSON NOT FOUND</div><h1>차시를 찾을 수 없습니다</h1><p>주소의 차시 ID를 확인하거나 전체 목차에서 다시 선택하세요.</p><a class="learning-button primary" href="./">${esc(course.title)} 목차로 →</a></section>`;
      const index = lessons.indexOf(lesson), module = course.modules.find(item => item.lessons.includes(lesson));
      if (route && index<0) throw new Error('Lesson does not belong to this learning path');
      return `<nav class="breadcrumb" aria-label="현재 위치"><a href="../../${route?'learn/':'index.html#mindmap'}">${route?'학습 경로':'학습 지도'}</a><span aria-hidden="true">/</span><a href="./">${esc(route?route.title:course.title)}</a><span aria-hidden="true">/</span><span aria-current="page">${index + 1}${route?'단계':'차시'}</span></nav>
        <div class="lesson-layout">${outline(course, id)}<article class="lesson-article">
          ${route?`<nav class="path-location" aria-label="현재 학습 경로"><a href="./">${esc(route.label)}</a><strong>${index+1} / ${lessons.length}단계</strong><a href="./#pathOutline">경로 목차 ↗</a></nav>`:''}
          <header class="lesson-heading"><img class="lesson-field-art" src="../../assets/illustrations/${key}.webp" width="480" height="480" alt="" decoding="async"><div class="lesson-heading-copy"><div class="overline">${esc(route?course.title+' · '+module.title:module.title)} · ${index + 1} / ${lessons.length}</div><h1>${esc(lesson.title)}</h1><p class="lesson-objective">${esc(lesson.goal)}</p></div></header>
          ${learningPlan(lesson)}
          <nav class="article-steps" aria-label="본문 바로가기"><a href="#concept">01 이해</a><a href="#worked">02 따라하기</a><a href="#practice">03 직접 변경</a><a href="#transfer">04 독립 과제</a><a href="#verify">05 검증</a></nav>
          ${lesson.environment ? `<details class="lesson-preparation" aria-label="이 차시 준비" ${id==='foundation.environment'?'open':''}><summary>준비 환경과 선행 학습 확인</summary><p><strong>${esc(lesson.environment.label)}</strong></p><ul>${lesson.environment.details.map(detail => `<li>${esc(detail)}</li>`).join('')}</ul>${prerequisites(lesson.prerequisites || [], key, true)}
            ${id === 'foundation.environment' ? '<a href="../../guides/linux.html">Windows에서 Linux 시작하기 ↗</a>' : ''}</details>` : ''}
          <section id="concept" class="article-section"><div class="overline">01 / UNDERSTAND</div><h2>먼저 이해하기</h2>${lesson.concepts.map((paragraph, i) => `<p>${esc(paragraph)}</p>${i === 0 ? visuals.renderLesson(id) : ''}`).join('')}
            ${lesson.pitfalls?.length ? `<aside class="misconceptions"><h3>자주 헷갈리는 지점</h3><dl>${lesson.pitfalls.map(pitfall => `<dt>${esc(pitfall.mistake)}</dt><dd>${esc(pitfall.correction)}</dd>`).join('')}</dl></aside>` : ''}</section>
          ${files(course, lesson)}
          <section id="worked" class="article-section"><div class="overline">02 / WORKED EXAMPLE</div><h2>따라 하며 관찰하기</h2>
            <p class="baseline-note">먼저 수정하지 않은 원본으로 아래 기준 예제를 확인하세요. 원본 폴더를 보관하고 전체 폴더의 작업 사본에서 다음 변경 단계를 진행합니다. 아래 예상 결과는 변경 전 기준입니다.</p>
            <h3>처음 상태의 전체 예제</h3>${codeBlock(lesson.code, 'exampleCode', lesson.learning?.codeContext || lesson.environment.label, true)}<div class="expected-output"><h3>변경 전 예상 결과와 해석</h3><pre>${esc(lesson.expected)}</pre></div>
            <h3>이제 단계별로 바꾸고 관찰하기</h3>${walkthrough(lesson)}</section>
          <section id="practice" class="article-section"><div class="overline">03 / TRY IT YOURSELF</div><h2>직접 바꾸고 확인하기</h2><p>${esc(lesson.task)}</p>
            <details class="hint"><summary>막혔을 때 힌트 보기</summary><p>${esc(lesson.hint)}</p></details>${solution(lesson)}<p class="record-prompt">학습 기록: 사용한 환경과 명령 → 바꾸기 전 예상 → 실제 결과 → 차이의 이유를 남기세요.</p>${transfer(lesson)}</section>
          <section id="verify" class="article-section completion-panel"><div class="overline">05 / VERIFY</div><h2>이 정도면 다음으로</h2>${questions(lesson)}
            <h3>내 결과물 확인하기</h3><ul class="evidence-list">${lesson.checks.map(check => `<li>${esc(check)}</li>`).join('')}</ul>
            <p>위 기준을 결과물로 확인한 뒤 완료로 표시하세요. 다음 차시를 잠그지 않습니다.</p><button type="button" class="learning-button primary js-only" hidden id="completeLesson" aria-pressed="false">이 차시 완료로 표시</button><p class="feedback" role="status" id="completionFeedback"></p></section>
          <nav class="lesson-pagination" aria-label="${route?'경로의 이전·다음 단계':'이전·다음 차시'}">${index > 0 ? `<a href="${lessonHref(lessons[index - 1].id, key)}"><small>← 이전 ${route?'단계':'차시'}</small>${esc(lessons[index - 1].title)}</a>` : `<a href="./"><small>← ${route?'학습 경로':'전체 과정'}</small>${route?'경로':'분야'} 목차로</a>`}
            ${index < lessons.length - 1 ? `<a href="${lessonHref(lessons[index + 1].id, key)}"><small>다음 ${route?'단계':'차시'} →</small>${esc(lessons[index + 1].title)}</a>` : `<a href="${route?'project.html':`../../projects/${key}.html`}"><small>다음 단계 →</small>${route?'경로':'분야'} 종합 프로젝트</a>`}</nav>
          ${route?`<p class="caption"><a href="../../tracks/${key}/${slug(id)}.html">이 차시를 ${esc(course.title)} 분야 과정으로 보기 ↗</a></p>`:''}
          <section class="reference-panel"><h2>이 차시의 참고 문서</h2>${sources(lesson.references || course.sources)}</section>${backup()}
        </article></div>`;
    }

    return Object.freeze({ overview, lesson: lessonView, lessonHref });
  }

  const api = Object.freeze({ create, esc, all, slug });
  if (typeof module === 'object' && module.exports) module.exports = api;
  else host.BifrostLearningView = api;
})(typeof window === 'object' ? window : globalThis);
