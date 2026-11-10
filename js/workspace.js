/* Preserve old subject-directory bookmarks under a subdirectory deployment. */
(() => {
  'use strict';
  if (location.hash === '#mindmap' || location.hash === '#fields') {
    location.replace(new URL('fields/', location.href).href);
  }
  if (typeof document === 'undefined') return;

  const root = document.documentElement;
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
