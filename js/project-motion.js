/* Event-driven motion; content stays readable without JavaScript. */
(() => {
  'use strict';
  const panels = [...document.querySelectorAll('.project-panel')];
  if (!panels.length || !window.matchMedia) return;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const fine = window.matchMedia('(hover: hover) and (pointer: fine)');
  let frame = 0, pending = null;
  const reset = panel => {
    panel.classList.remove('is-tracking');
    for (const key of ['--art-x','--art-y','--light-x','--light-y']) panel.style.removeProperty(key);
  };
  function cancel() {
    if (frame) cancelAnimationFrame(frame);
    frame = 0; pending = null;
    panels.forEach(reset);
  }
  function paint() {
    frame = 0;
    if (!pending || reduced.matches || !fine.matches || document.hidden) return;
    const {panel,x,y} = pending;
    panel.classList.add('is-tracking');
    panel.style.setProperty('--art-x', `${((x-.5)*12).toFixed(2)}px`);
    panel.style.setProperty('--art-y', `${((y-.5)*8).toFixed(2)}px`);
    panel.style.setProperty('--light-x', `${(x*100).toFixed(2)}%`);
    panel.style.setProperty('--light-y', `${(y*100).toFixed(2)}%`);
  }
  for (const panel of panels) {
    panel.addEventListener('pointermove', event => {
      if (event.pointerType !== 'mouse' || reduced.matches || !fine.matches || document.hidden) return;
      const box = panel.getBoundingClientRect();
      if (!box.width || !box.height) return;
      pending = {panel,x:Math.max(0,Math.min(1,(event.clientX-box.left)/box.width)),y:Math.max(0,Math.min(1,(event.clientY-box.top)/box.height))};
      if (!frame) frame = requestAnimationFrame(paint);
    }, {passive:true});
    panel.addEventListener('pointerleave', () => {
      if (pending?.panel === panel) {
        if (frame) cancelAnimationFrame(frame);
        pending = null; frame = 0;
      }
      reset(panel);
    });
  }
  let observer;
  function observe() {
    observer?.disconnect();
    panels.forEach(panel => panel.classList.remove('is-arriving'));
    if (reduced.matches || !('IntersectionObserver' in window)) return;
    observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add('is-arriving');
        observer.unobserve(entry.target);
      }
    }, {threshold:.12});
    panels.forEach(panel => observer.observe(panel));
  }
  reduced.addEventListener?.('change', () => {cancel(); observe();});
  fine.addEventListener?.('change', cancel);
  document.addEventListener('visibilitychange', () => {if (document.hidden) cancel();});
  window.addEventListener('blur', cancel);
  window.addEventListener('scroll', cancel, {passive:true});
  window.addEventListener('pagehide', () => {cancel(); observer?.disconnect();});
  window.addEventListener('pageshow', observe);
  observe();
})();
