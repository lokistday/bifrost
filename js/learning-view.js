/* Pure HTML views: shared by the static build and browser's legacy URL support. */
((host) => {
  'use strict';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const all = course => course.modules.flatMap(module => module.lessons);
  const slug = id => id.slice(id.indexOf('.') + 1);

  function create(courses, visuals) {
    const lookup = Object.fromEntries(Object.values(courses).flatMap(course =>
      all(course).map(lesson => [lesson.id, { course, lesson }])));

    function lessonHref(id, fromKey) {
      const owner = lookup[id]?.course.id;
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
      return `<section class="storage-panel js-only" hidden aria-label="브라우저 진도 저장">
        <strong>내 브라우저에 저장되는 학습 기록</strong><p id="storageNotice"></p><p id="legacyNotice"></p>
        <div class="backup-actions"><button class="learning-button small" type="button" id="exportProgress">진도 백업 받기</button>
          <label class="learning-button small import-label">백업 합쳐서 가져오기<input type="file" id="importProgress" accept="application/json,.json"></label></div>
        <p class="caption">같은 사이트·브라우저에서 공유합니다. 다른 기기와 자동 동기화되지 않습니다. 가져오기는 완료 기록을 합치며 현재 완료 기록을 지우지 않습니다.</p>
        <p class="feedback" role="status" id="backupFeedback"></p></section>`;
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
        <div class="overview-layout"><div>
          <section class="outcome-panel"><div class="overline">WHAT YOU WILL BUILD</div><h2>이 과정을 마치면</h2><p>${esc(course.outcome)}</p></section>
          <section class="module-list" id="courseModules" aria-label="모듈별 차시">${course.modules.map((module, index) => `
            <section class="module-card"><div class="module-heading"><h2>${esc(module.title)}</h2><span class="caption" data-module-count="${index}"></span></div><p>${esc(module.intro)}</p>
              <ol>${module.lessons.map(lesson => `<li><a class="lesson-row" href="${lessonHref(lesson.id, key)}"><span class="lesson-dot" data-dot="${lesson.id}" aria-hidden="true"></span>
                <span><strong>${esc(lesson.title)}</strong><small>${esc(lesson.goal)}</small><small class="completion-label" data-completion="${lesson.id}"></small></span><span aria-hidden="true">↗</span></a></li>`).join('')}</ol>
            </section>`).join('')}</section></div>
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
        ${step.code ? codeBlock(step.code, '', '작게 나눠 확인하기') : ''}${step.expected ? `<div class="step-observation"><strong>관찰할 결과</strong><pre>${esc(step.expected)}</pre></div>` : ''}</li>`).join('')}</ol>`;
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
      const course = courses[key], lessons = all(course), lesson = lessons.find(item => item.id === id);
      if (!lesson) return `<section class="not-found"><div class="overline">LESSON NOT FOUND</div><h1>차시를 찾을 수 없습니다</h1><p>주소의 차시 ID를 확인하거나 전체 목차에서 다시 선택하세요.</p><a class="learning-button primary" href="./">${esc(course.title)} 목차로 →</a></section>`;
      const index = lessons.indexOf(lesson), module = course.modules.find(item => item.lessons.includes(lesson));
      return `<nav class="breadcrumb" aria-label="현재 위치"><a href="../../index.html#mindmap">학습 지도</a><span aria-hidden="true">/</span><a href="./">${esc(course.title)}</a><span aria-hidden="true">/</span><span aria-current="page">${index + 1}차시</span></nav>
        <div class="lesson-layout">${outline(course, id)}<article class="lesson-article">
          <header class="lesson-heading"><img class="lesson-field-art" src="../../assets/illustrations/${key}.webp" width="480" height="480" alt="" decoding="async"><div class="lesson-heading-copy"><div class="overline">${esc(module.title)} · ${index + 1} / ${lessons.length}</div><h1>${esc(lesson.title)}</h1><p class="lesson-objective">${esc(lesson.goal)}</p></div></header>
          <nav class="article-steps" aria-label="본문 바로가기"><a href="#concept">01 이해</a><a href="#worked">02 따라하기</a><a href="#practice">03 직접 변경</a><a href="#verify">04 검증</a></nav>
          ${lesson.environment ? `<section class="lesson-preparation" aria-label="이 차시 준비"><h2>준비와 연결</h2><p><strong>${esc(lesson.environment.label)}</strong></p><ul>${lesson.environment.details.map(detail => `<li>${esc(detail)}</li>`).join('')}</ul>${prerequisites(lesson.prerequisites || [], key, true)}
            ${id === 'foundation.environment' ? '<a href="../../guides/linux.html">Windows에서 Linux 시작하기 ↗</a>' : ''}</section>` : ''}
          <section id="concept" class="article-section"><div class="overline">01 / UNDERSTAND</div><h2>먼저 이해하기</h2>${lesson.concepts.map((paragraph, i) => `<p>${esc(paragraph)}</p>${i === 0 ? visuals.renderLesson(id) : ''}`).join('')}
            ${lesson.pitfalls?.length ? `<aside class="misconceptions"><h3>자주 헷갈리는 지점</h3><dl>${lesson.pitfalls.map(pitfall => `<dt>${esc(pitfall.mistake)}</dt><dd>${esc(pitfall.correction)}</dd>`).join('')}</dl></aside>` : ''}</section>
          ${files(course, lesson)}
          <section id="worked" class="article-section"><div class="overline">02 / WORKED EXAMPLE</div><h2>따라 하며 관찰하기</h2>${walkthrough(lesson)}
            <h3>전체 예제 연결하기</h3>${codeBlock(lesson.code, 'exampleCode', undefined, true)}<div class="expected-output"><h3>예상 결과와 해석</h3><pre>${esc(lesson.expected)}</pre></div></section>
          <section id="practice" class="article-section"><div class="overline">03 / TRY IT YOURSELF</div><h2>직접 바꾸고 확인하기</h2><p>${esc(lesson.task)}</p>
            <details class="hint"><summary>막혔을 때 힌트 보기</summary><p>${esc(lesson.hint)}</p></details>${solution(lesson)}<p class="record-prompt">학습 기록: 사용한 환경과 명령 → 바꾸기 전 예상 → 실제 결과 → 차이의 이유를 남기세요.</p></section>
          <section id="verify" class="article-section completion-panel"><div class="overline">04 / VERIFY</div><h2>이 정도면 다음으로</h2>${questions(lesson)}
            <h3>내 결과물 확인하기</h3><ul class="evidence-list">${lesson.checks.map(check => `<li>${esc(check)}</li>`).join('')}</ul>
            <p>위 기준을 결과물로 확인한 뒤 완료로 표시하세요. 다음 차시를 잠그지 않습니다.</p><button type="button" class="learning-button primary js-only" hidden id="completeLesson" aria-pressed="false">이 차시 완료로 표시</button><p class="feedback" role="status" id="completionFeedback"></p></section>
          <nav class="lesson-pagination" aria-label="이전·다음 차시">${index > 0 ? `<a href="${lessonHref(lessons[index - 1].id, key)}"><small>← 이전 차시</small>${esc(lessons[index - 1].title)}</a>` : '<a href="./"><small>← 전체 과정</small>분야 목차로</a>'}
            ${index < lessons.length - 1 ? `<a href="${lessonHref(lessons[index + 1].id, key)}"><small>다음 차시 →</small>${esc(lessons[index + 1].title)}</a>` : `<a href="./"><small>과정 돌아보기 →</small>${esc(course.title)} 목차</a>`}</nav>
          <section class="reference-panel"><h2>이 차시의 참고 문서</h2>${sources(lesson.references || course.sources)}</section>${backup()}
        </article></div>`;
    }

    return Object.freeze({ overview, lesson: lessonView, lessonHref });
  }

  const api = Object.freeze({ create, esc, all, slug });
  if (typeof module === 'object' && module.exports) module.exports = api;
  else host.BifrostLearningView = api;
})(typeof window === 'object' ? window : globalThis);
