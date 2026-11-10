/* Continue the guided entry transition after the destination document loads. */
(() => {
  'use strict';
  try {
    if (sessionStorage.getItem('bifrost-entry-arrival') !== '1') return;
    sessionStorage.removeItem('bifrost-entry-arrival');
  } catch (_) { return; }
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const root = document.documentElement;
  root.classList.add('entry-arriving');
  window.setTimeout(() => root.classList.remove('entry-arriving'), 850);
})();
