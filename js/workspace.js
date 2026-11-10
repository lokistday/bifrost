/* Preserve old subject-directory bookmarks under a subdirectory deployment. */
(() => {
  'use strict';
  if (location.hash === '#mindmap' || location.hash === '#fields') {
    location.replace(new URL('fields/', location.href).href);
  }
  if (typeof document === 'undefined') return;
  let navigating = false;
  window.addEventListener('pageshow', event => {
    if (!event.persisted) return;
    navigating = false;
    document.documentElement.classList.remove('entry-navigating');
    document.querySelectorAll('.entry-choice.is-selected').forEach(link => link.classList.remove('is-selected'));
  });
  for (const link of document.querySelectorAll('.entry-choice[href]')) {
    link.addEventListener('click', event => {
      if (navigating) { event.preventDefault(); return; }
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey ||
          link.target && link.target !== '_self' || link.hasAttribute('download') ||
          window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      event.preventDefault();
      navigating = true;
      const bounds = link.getBoundingClientRect();
      const root = document.documentElement;
      root.style.setProperty('--entry-exit-x', `${bounds.left + bounds.width / 2}px`);
      root.style.setProperty('--entry-exit-y', `${bounds.top + bounds.height / 2}px`);
      link.classList.add('is-selected');
      root.classList.add('entry-navigating');
      window.setTimeout(() => {
        try { sessionStorage.setItem('bifrost-entry-arrival', '1'); } catch (_) { /* Navigation still works when storage is blocked. */ }
        window.location.assign(link.href);
      }, 480);
    });
  }
})();
