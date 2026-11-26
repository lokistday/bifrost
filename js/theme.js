/* Fixed dark appearance, including cached pages and embedded guides. */
(() => {
  const root = document.documentElement;
  root.dataset.theme = 'dark';
  root.style.colorScheme = 'dark';
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');
  if (metaThemeColor) metaThemeColor.content = root.dataset.palette === 'charcoal' ? '#181819' : '#080b17';
})();
