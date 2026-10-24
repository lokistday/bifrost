/* Start first visits before paint; inspect completed resource timing for cache-bypass reloads. */
(() => {
  const seenKey = 'bifrost_splash_seen_v1';
  const replayKey = 'bifrost_splash_replay_v1';
  const pageKey = () => location.pathname + location.search;
  const scriptURL = document.currentScript?.src;
  const root = document.documentElement;
  let started = false;

  // Key events are an optional signal: browser-level reload shortcuts may bypass the page.
  document.addEventListener('keydown', event => {
    if (!event.isTrusted || event.defaultPrevented || event.repeat || event.altKey) return;
    const key = event.key.toLowerCase();
    const hardReload = (key === 'f5' && (event.ctrlKey || event.shiftKey)) ||
      (key === 'r' && event.shiftKey && (event.ctrlKey || event.metaKey));
    const normalReload = key === 'f5' || (key === 'r' && (event.ctrlKey || event.metaKey));
    try {
      if (hardReload) sessionStorage.setItem(replayKey, JSON.stringify({ at: Date.now(), page: pageKey() }));
      else if (normalReload) sessionStorage.removeItem(replayKey);
    } catch { /* Never interfere with the browser's native refresh. */ }
  }, { capture: true });

  const navigation = () => {
    try { return performance.getEntriesByType?.('navigation')?.[0]; }
    catch { return undefined; }
  };

  // A direct replay link is deterministic even when the browser owns the shortcut.
  let explicitReplay = false;
  try {
    const url = new URL(location.href);
    if (url.searchParams.get('intro') === '1') {
      url.searchParams.delete('intro');
      history.replaceState(history.state, '', url.pathname + url.search + url.hash);
      explicitReplay = true;
    }
  } catch { /* No URL/history support: leave the normal page usable. */ }

  let seen = true;
  let replay = false;
  let storageAvailable = false;
  try {
    const saved = sessionStorage.getItem(replayKey);
    if (saved !== null) sessionStorage.removeItem(replayKey);
    if (saved !== null) {
      try {
        const request = JSON.parse(saved);
        const age = Date.now() - request?.at;
        const type = navigation()?.type;
        replay = typeof request?.at === 'number' && request.page === pageKey() &&
          Number.isFinite(age) && age >= 0 && age <= 30000 && (!type || type === 'reload');
      } catch { /* Ignore malformed or stale requests. */ }
    }
    seen = sessionStorage.getItem(seenKey) === '1';
    storageAvailable = true;
  } catch { /* Automatic intros remain off when storage is unavailable. */ }

  function play(reason) {
    if (started) return;
    try { sessionStorage.setItem(seenKey, '1'); }
    catch { if (!explicitReplay) return; }
    started = true;
    root.dataset.introReason = reason;
    document.removeEventListener('DOMContentLoaded', checkNetworkReload);
    window.removeEventListener('load', finishNetworkCheck);
    startIntro();
  }

  // Full response bodies for both HTML and this script are consistent with cache bypass.
  // This is a cache signal, not proof of a particular key: a completely cold normal
  // reload or freshly changed files may also replay once. Cached/304 reloads do not.
  const fullTransfer = entry => entry && entry.responseEnd > 0 && entry.encodedBodySize > 0 &&
    entry.transferSize > 300 && entry.transferSize > entry.encodedBodySize &&
    entry.deliveryType !== 'cache' && entry.responseStatus !== 304 && !(entry.workerStart > 0);

  function checkNetworkReload() {
    if (started || !storageAvailable || !scriptURL) return;
    try {
      const nav = navigation();
      const resource = performance.getEntriesByName?.(scriptURL, 'resource')?.[0];
      if (nav?.type === 'reload' && fullTransfer(nav) && fullTransfer(resource)) play('network-reload');
    } catch { /* Timing unsupported or incomplete: keep the page interactive. */ }
  }
  function finishNetworkCheck() {
    checkNetworkReload();
    document.removeEventListener('DOMContentLoaded', checkNetworkReload);
    window.removeEventListener('load', finishNetworkCheck);
  }

  if (explicitReplay) play('replay-link');
  else if (storageAvailable && !seen) play('first-visit');
  else if (storageAvailable && replay) play('reload-shortcut');
  else if (storageAvailable && (!navigation()?.type || navigation()?.type === 'reload')) {
    // At head-script time the current resource may not yet be in the timeline.
    // Recheck without blocking rendering, creating a timer, or adding an overlay.
    checkNetworkReload();
    if (!started) {
      document.addEventListener('DOMContentLoaded', checkNetworkReload, { once: true });
      window.addEventListener('load', finishNetworkCheck, { once: true });
    }
  }

  function startIntro() {
    const root = document.documentElement;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const startedAt = performance.now();
    const minimumDuration = reducedMotion ? 150 : 1400;
    const fadeDuration = reducedMotion ? 0 : 600;
    const background = [];
    let dismissed = false;
    let readyTimer;
    let removeTimer;
  
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
    function makeReady() {
      if (dismissed) return;
      document.querySelectorAll('body > header, body > main, body > footer, #linuxGuideOverlay').forEach(element => {
        background.push({ element, wasInert: element.inert });
        element.inert = true;
      });
      readyTimer = setTimeout(dismiss, Math.max(0, minimumDuration - (performance.now() - startedAt)));
    }
    if (document.readyState === 'loading' || !document.readyState) document.addEventListener('DOMContentLoaded', makeReady, { once: true });
    else makeReady();
  }
})();
