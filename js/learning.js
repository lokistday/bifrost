/* Enhance generated pages; retain support for permanent lesson.html?id= links. */
(() => {
  'use strict';
  const courses = window.BifrostCourses;
  const progress = window.BifrostProgress;
  const { all } = window.BifrostLearningView;
  const key = document.body.dataset.course;
  const course = courses[key];
  const root = document.getElementById('learningContent');
  if (!course || !root) return;
  const lessons = all(course);
  const paths = window.BifrostPaths || {};
  const pathId = document.body.dataset.path;
  const route = Object.prototype.hasOwnProperty.call(paths, pathId) ? paths[pathId] : null;
  const view = window.BifrostLearningView.create(courses, window.BifrostVisuals, route);
  const lessonHref = id => view.lessonHref(id, key);
  const firstIncomplete = () => lessons.find(lesson => !progress.has(lesson.id));
  const isLesson = document.body.dataset.view === 'lesson';
  const queryId = new URLSearchParams(location.search).get('id');
  const currentId = document.body.dataset.lessonId || queryId;
  const lesson = lessons.find(item => item.id === currentId);

  // Normal pages already contain the complete article. Query URLs need client-side selection.
  if (isLesson && root.dataset.rendered !== currentId) {
    root.innerHTML = view.lesson(key, currentId);
  } else if (!isLesson && root.dataset.rendered !== 'course') {
    root.innerHTML = view.overview(key);
  }
  if (isLesson) {
    document.title = lesson ? `${lesson.title} — ${route ? route.title : course.title} · Bifrost` : '차시를 찾을 수 없습니다 — Bifrost';
    if (lesson) {
      document.querySelector('meta[name="description"]').content = lesson.goal;
      const canonical = document.querySelector('link[rel="canonical"]');
      if (canonical) canonical.href = new URL(lessonHref(currentId), canonical.href).href;
      progress.visit(currentId);
      document.getElementById('completeLesson').addEventListener('click', () => {
        const done = !progress.has(currentId);
        progress.set(currentId, done);
        document.getElementById('completionFeedback').textContent = progress.available()
          ? (done ? '완료로 저장했습니다. 다음 차시에서 이어가세요.' : '완료 표시를 해제했습니다.')
          : '화면에는 반영했지만 브라우저 저장에 실패했습니다. 진도를 백업해 두세요.';
      });
      document.getElementById('copyExample').addEventListener('click', async event => {
        try { await navigator.clipboard.writeText(lesson.code); event.target.textContent = '복사됨'; }
        catch (_) { event.target.textContent = '코드를 선택해 복사하세요'; }
      });
      document.querySelectorAll('[data-check-question]').forEach(button => {
        const index = Number(button.dataset.checkQuestion);
        const question = lesson.questions[index];
        const field = document.querySelector(`[data-question="${index}"]`);
        const feedback = document.getElementById(`questionFeedback${index}`);
        button.addEventListener('click', () => {
          const selected = field.querySelector('input:checked');
          if (!selected) {
            feedback.textContent = '보기를 하나 고른 뒤 확인하세요.';
            feedback.removeAttribute('data-result');
            return;
          }
          const correct = Number(selected.value) === question.answer;
          feedback.dataset.result = correct ? 'correct' : 'review';
          feedback.textContent = `${correct ? '맞았습니다.' : '다시 살펴보세요.'} ${question.explanation}`;
        });
        field.querySelectorAll('input').forEach(input => input.addEventListener('change', () => {
          feedback.textContent = '';
          feedback.removeAttribute('data-result');
        }));
      });
    }
  }
  root.querySelectorAll('.js-only').forEach(element => { element.hidden = false; });
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
      const done = progress.has(currentId);
      complete.setAttribute('aria-pressed', String(done));
      complete.textContent = done ? '✓ 완료됨 · 표시 해제' : '이 차시 완료로 표시';
    }
    const storage = document.getElementById('storageNotice');
    if (storage) storage.textContent = progress.available() ? '진도는 이 브라우저의 로컬 저장소에 저장됩니다. 브라우저 데이터 삭제 전에 백업하세요.' : '브라우저 저장소를 사용할 수 없습니다. 이번 화면의 기록이 사라지기 전에 백업을 받아 두세요.';
    const legacy = document.getElementById('legacyNotice');
    if (legacy) legacy.textContent = progress.legacyCount() ? `이전 버전의 완료 기록 ${progress.legacyCount()}건을 보관했습니다. 대응되는 차시만 옮겼고, 확장·재구성된 차시는 새로 확인합니다. Crypto의 도구·문제 분류·풀이 기록은 Misc로 이동했습니다.` : '';
  }
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
