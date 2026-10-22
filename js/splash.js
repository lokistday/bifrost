/* Runs in the head so the intro is ready before the first page paint. */
(() => {
  // Keep the full intro for the first visit in this tab, including across reloads.
  // If session storage is unavailable, leave the page usable without the intro.
  try {
    const seenKey = 'bifrost_splash_seen_v1';
    if (sessionStorage.getItem(seenKey) === '1') return;
    sessionStorage.setItem(seenKey, '1');
  } catch {
    return;
  }

  const root = document.documentElement;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const startedAt = performance.now();
  const minimumDuration = reducedMotion ? 150 : 2600;
  const fadeDuration = reducedMotion ? 0 : 400;
  const background = [];
  let dismissed = false;
  let readyTimer;
  let removeTimer;

  // Assign delays before the SVG is parsed so no lanes start in unison.
  if (!reducedMotion) {
    const laneOrder = Array.from({ length: 8 }, (_, index) => index);
    const laneDuration = 900;
    const stagger = 90;
    for (let index = laneOrder.length - 1; index > 0; index--) {
      const other = Math.floor(Math.random() * (index + 1));
      [laneOrder[index], laneOrder[other]] = [laneOrder[other], laneOrder[index]];
    }
    laneOrder.forEach((lane, order) => {
      root.style.setProperty(`--splash-lane-${lane}-delay`, `${order * stagger}ms`);
    });
    root.style.setProperty('--splash-lane-duration', `${laneDuration}ms`);
    root.style.setProperty('--splash-bridge-complete', `${laneDuration + (laneOrder.length - 1) * stagger}ms`);
  }

  root.classList.add('splash-active');

  function removeSplash() {
    clearTimeout(readyTimer);
    clearTimeout(removeTimer);
    clearTimeout(safetyTimer);
    root.classList.remove('splash-active', 'splash-leaving');
    document.getElementById('startupSplash')?.remove();
    background.forEach(({ element, wasInert }) => { element.inert = wasInert; });
    document.removeEventListener('keydown', onKeyDown);
    document.removeEventListener('visibilitychange', onVisibilityChange);
    window.removeEventListener('pageshow', onPageShow);
  }

  function dismiss({ immediate = false } = {}) {
    if (immediate) {
      dismissed = true;
      removeSplash();
      return;
    }
    if (dismissed) return;
    dismissed = true;
    root.classList.add('splash-leaving');
    removeTimer = setTimeout(removeSplash, fadeDuration);
  }

  function onKeyDown(event) {
    if (event.key === 'Escape') dismiss({ immediate: true });
  }
  function onVisibilityChange() {
    if (document.hidden) dismiss({ immediate: true });
  }
  function onPageShow(event) {
    if (event.persisted) dismiss({ immediate: true });
  }

  // Never wait indefinitely for fonts, remote resources, or the page load event.
  const safetyTimer = setTimeout(() => dismiss({ immediate: true }), 4200);
  document.addEventListener('keydown', onKeyDown);
  document.addEventListener('visibilitychange', onVisibilityChange);
  window.addEventListener('pageshow', onPageShow);
  document.addEventListener('DOMContentLoaded', () => {
    if (dismissed) return;
    document.querySelectorAll('body > header, body > main, body > footer, #linuxGuideOverlay').forEach(element => {
      background.push({ element, wasInert: element.inert });
      element.inert = true;
    });
    readyTimer = setTimeout(dismiss, Math.max(0, minimumDuration - (performance.now() - startedAt)));
  }, { once: true });
})();
