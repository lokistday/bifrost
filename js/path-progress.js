/* Route state lives in the address; completed lessons keep their permanent IDs. */
(() => {
  'use strict';
  const routes = window.BifrostPaths || {};
  const key = document.body.dataset.path;
  if (!Object.prototype.hasOwnProperty.call(routes, key)) return;
  const route = routes[key], progress = window.BifrostProgress;
  const lookup = Object.fromEntries(Object.values(window.BifrostCourses).flatMap(c => c.modules.flatMap(m => m.lessons)).map(l => [l.id,l]));
  const lessons = route.sequence.map(id => lookup[id]);
  function update() {
    const done = progress.count(lessons), percent = Math.round(done / lessons.length * 100);
    document.querySelectorAll('[data-path-count]').forEach(el => { el.textContent = `${done} / ${lessons.length}단계 완료 · ${percent}%`; });
    document.querySelectorAll('[data-path-meter]').forEach(el => {
      el.setAttribute('aria-valuenow',String(percent));
      el.firstElementChild.style.width = `${percent}%`;
    });
    document.querySelectorAll('[data-completion]').forEach(el => { el.textContent = progress.has(el.dataset.completion) ? '완료' : '미완료'; });
    const link = document.getElementById('continuePath');
    if (link) {
      const next = lessons.find(l => !progress.has(l.id));
      link.href = next ? `${next.id}.html` : 'project.html';
      link.textContent = next ? `${done ? '이어서' : '첫 단계'} 학습하기 →` : '종합 프로젝트로 →';
    }
  }
  window.addEventListener('bifrost-progress',update);
  update();
})();
