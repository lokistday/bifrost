/* Match the selected pictogram to the destination heading for this navigation. */
(() => {
  'use strict';
  const root = document.documentElement;
  let selected = false;
  try {
    selected = sessionStorage.getItem('bifrost-entry-route') === location.pathname;
    sessionStorage.removeItem('bifrost-entry-route');
  } catch (_) { /* Direct visits render normally. */ }
  if (selected && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    root.classList.add('entry-destination');
  }
  window.addEventListener('pagereveal', event => {
    const transition = event.viewTransition;
    if (!transition) return;
    if (!root.classList.contains('entry-destination')) {
      transition.skipTransition();
      return;
    }
    root.classList.add('entry-morph');
    transition.finished.finally(() => root.classList.remove('entry-morph', 'entry-destination'));
  });
  window.addEventListener('pagehide', () => root.classList.remove('entry-destination', 'entry-morph'));
})();
