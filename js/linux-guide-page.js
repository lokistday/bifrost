/* Same-origin embedded guide navigation; standalone links keep their fallback. */
document.querySelectorAll('[data-return-guide]').forEach(link => {
  link.addEventListener('click', event => {
    try {
      if (window.parent !== window && window.parent.location.origin === location.origin
          && typeof window.parent.showMainGuide === 'function') {
        event.preventDefault();
        window.parent.showMainGuide();
      }
    } catch (_) { /* Cross-origin parents use the ordinary link. */ }
  });
});
