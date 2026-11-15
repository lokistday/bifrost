/* Preserve old subject-directory bookmarks under a subdirectory deployment. */
(() => {
  'use strict';
  if (location.hash === '#mindmap' || location.hash === '#fields') {
    location.replace(new URL('fields/', location.href).href);
  }
  if (typeof document === 'undefined') return;

  const root = document.documentElement;
  const resume = document.getElementById('resumeChoice');
  function updateResume() {
    const progress = window.BifrostProgress;
    if (!resume || !progress) return;
    const courses = Object.values(window.BifrostCourses);
    const last = progress.last();
    const course = courses.find(item => item.id === last?.split('.')[0]) ||
      courses.find(item => item.modules.some(module => progress.count(module.lessons) > 0));
    resume.hidden = !course;
    if (!course) return;
    const lessons = course.modules.flatMap(module => module.lessons);
    const next = lessons.find(lesson => lesson.id === last && !progress.has(last)) ||
      lessons.find(lesson => !progress.has(lesson.id));
    resume.querySelector('span').textContent = next ? '이어서 학습하기' : '과정 완료 · 종합 프로젝트';
    resume.querySelector('strong').textContent = next
      ? `${course.label} ${lessons.indexOf(next) + 1}차시 · ${next.title}`
      : `${course.label} 프로젝트 열기`;
    resume.href = next ? `tracks/${course.id}/${next.id.split('.')[1]}.html` : `projects/${course.id}.html`;
  }
  updateResume();
  window.addEventListener('bifrost-progress', updateResume);
  for (const link of document.querySelectorAll('.entry-choice[href]')) {
    link.addEventListener('click', event => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey ||
          event.shiftKey || event.altKey || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      root.querySelector('.entry-origin')?.classList.remove('entry-origin');
      link.classList.add('entry-origin');
      try {
        sessionStorage.setItem('bifrost-entry-route', new URL(link.href).pathname);
      } catch (_) { /* The anchor still navigates normally. */ }
    });
  }
  window.addEventListener('pageshow', () => root.querySelector('.entry-origin')?.classList.remove('entry-origin'));
  window.addEventListener('pagereveal', event => event.viewTransition?.skipTransition());
})();
