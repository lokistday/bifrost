/* Small enhancements for the homepage; every learning link is static. */
(() => {
  'use strict';
  const form = document.getElementById('workspaceSearch');
  const input = document.getElementById('workspaceQuery');
  form.hidden = false;
  form.addEventListener('submit', event => {
    event.preventDefault();
    const destination = new URL('learn/', location.href);
    const query = input.value.trim().slice(0,120);
    // Fragments stay in the browser: the static host never receives the query.
    destination.hash = query ? `search?q=${encodeURIComponent(query)}` : 'search';
    location.assign(destination.href);
  });
  document.addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault(); input.focus();
    }
  });
  const progress = window.BifrostProgress, route = window.BifrostPaths?.start;
  if (!progress || !route) return;
  const lessons = route.sequence.map(id=>({id}));
  function update() {
    const done = progress.count(lessons);
    const next = route.sequence.find(id=>!progress.has(id));
    document.getElementById('homeProgressCount').textContent = `${done} / ${lessons.length}`;
    document.getElementById('homeProgressNote').textContent = progress.available() ? '이 브라우저에 저장됩니다' : '진도를 저장할 수 없는 환경입니다';
    const link = document.getElementById('homeContinue');
    link.href = next ? `paths/start/${next}.html` : 'paths/start/project.html';
    link.textContent = next ? (done ? '이어서 학습하기 →' : '첫 단계 시작하기 →') : '종합 프로젝트로 →';
    document.querySelectorAll('[data-home-lesson]').forEach(row=>{
      const completed = progress.has(row.dataset.homeLesson);
      row.classList.toggle('is-complete',completed);
      row.querySelector('.lesson-state').textContent = completed ? '완료' : '미완료';
      const anchor=row.querySelector('a');
      if(row.dataset.homeLesson===next) anchor.setAttribute('aria-current','step');
      else anchor.removeAttribute('aria-current');
    });
  }
  window.addEventListener('bifrost-progress',update);
  update();
})();
