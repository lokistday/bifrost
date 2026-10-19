/* Shared theme controller for every Bifrost page and embedded guide. */
(() => {
  const STORAGE_KEY = 'bifrost_theme_v1';
  const root = document.documentElement;
  const button = document.getElementById('themeToggle');
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');

  function readSavedTheme() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === 'dark' || saved === 'light') return saved;
    } catch (_) { /* Storage can be disabled; use system preference instead. */ }
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function updateTheme(theme, { persist = false, notifyParent = false } = {}) {
    const selected = theme === 'dark' ? 'dark' : 'light';
    root.dataset.theme = selected;
    root.style.colorScheme = selected;
    if (button) {
      const dark = selected === 'dark';
      button.setAttribute('aria-pressed', String(dark));
      button.setAttribute('aria-label', dark ? '라이트 모드로 전환' : '다크 모드로 전환');
      button.innerHTML = dark
        ? '<span class="theme-icon" aria-hidden="true">☀</span><span class="theme-label">라이트 모드</span>'
        : '<span class="theme-icon" aria-hidden="true">☾</span><span class="theme-label">다크 모드</span>';
    }
    if (metaThemeColor) metaThemeColor.content = selected === 'dark' ? '#0b1220' : '#101a30';
    if (persist) {
      try { localStorage.setItem(STORAGE_KEY, selected); } catch (_) { /* Theme still applies for this visit. */ }
    }
    if (notifyParent) {
      const frame = document.getElementById('linuxGuideFrame');
      if (frame && frame.contentWindow) {
        frame.contentWindow.postMessage({ type: 'bifrost-theme-change', theme: selected }, location.origin);
      }
    }
  }

  updateTheme(readSavedTheme());

  if (button) button.addEventListener('click', () => {
    updateTheme(root.dataset.theme === 'dark' ? 'light' : 'dark', { persist: true, notifyParent: true });
  });

  /* Keep a page or iframe in sync if another same-origin Bifrost page changes the saved preference. */
  window.addEventListener('storage', event => {
    if (event.key === STORAGE_KEY && (event.newValue === 'dark' || event.newValue === 'light')) {
      updateTheme(event.newValue, { notifyParent: true });
    }
  });

  window.addEventListener('message', event => {
    if (event.origin !== location.origin || !event.data || event.data.type !== 'bifrost-theme-change') return;
    if (event.data.theme === 'dark' || event.data.theme === 'light') updateTheme(event.data.theme);
  });

  /* Parent can read the current preference after an iframe finishes loading. */
  if (window.parent !== window) {
    try { window.parent.postMessage({ type: 'bifrost-theme-ready', theme: root.dataset.theme }, location.origin); } catch (_) { /* No-op for standalone contexts. */ }
  }
  window.addEventListener('message', event => {
    if (event.origin !== location.origin || !event.data || event.data.type !== 'bifrost-theme-ready') return;
    const frame = document.getElementById('linuxGuideFrame');
    if (frame && frame.contentWindow) frame.contentWindow.postMessage({ type: 'bifrost-theme-change', theme: root.dataset.theme || 'light' }, location.origin);
  });
})();
