/* Preserve old subject-directory bookmarks under a subdirectory deployment. */
(() => {
  'use strict';
  if (location.hash === '#mindmap' || location.hash === '#fields') {
    location.replace(new URL('fields/', location.href).href);
  }
  if (typeof document === 'undefined') return;
  let navigating = false;
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
      window.setTimeout(() => window.location.assign(link.href), 480);
    });
  }
})();
