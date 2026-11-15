/* Homepage display data comes from the same curriculum and paths as lessons. */
const { esc, all } = require('../js/learning-view.js');
const drawings = {
  home: '<path d="m3 11 9-8 9 8v10h-6v-7H9v7H3Z"/>',
  book: '<path d="M12 5v16M12 5C9 2 5 3 2 4v15c4-1 7-1 10 2 3-3 6-3 10-2V4c-3-1-7-2-10 1Z"/>',
  globe: '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M5 6h14M5 18h14"/>',
  chip: '<rect x="5" y="5" width="14" height="14" rx="2"/><path d="M9 1v4m6-4v4M9 19v4m6-4v4M1 9h4m-4 6h4m14-6h4m-4 6h4"/><path d="M9 9h6v6H9z"/>',
  file: '<path d="M5 2h10l4 4v16H5ZM14 2v5h5M9 11h6m-6 4h6m-6 4h4"/>',
  network: '<circle cx="12" cy="4" r="3"/><circle cx="4" cy="19" r="3"/><circle cx="20" cy="19" r="3"/><path d="M12 7v5m0 0-7 4m7-4 7 4"/>',
  cloud: '<path d="M7 19a5 5 0 1 1 .2-10A7 7 0 0 1 21 11a4 4 0 0 1-1 8Z"/>',
  lock: '<rect x="4" y="10" width="16" height="12" rx="2"/><path d="M8 10V6a4 4 0 0 1 8 0v4m-4 5v3"/>',
  code: '<path d="m7 6-5 6 5 6m10-12 5 6-5 6M14 3l-4 18"/>',
  grid: '<path d="M3 3h6v6H3zm12 0h6v6h-6zM3 15h6v6H3zm12 0h6v6h-6z"/>',
  box: '<path d="m12 2 10 5v10l-10 5-10-5V7Zm0 10v10M2 7l10 5 10-5M7 4.5l10 5V15"/>',
  arrow: '<path d="M4 12h16m-6-6 6 6-6 6"/>',
  route: '<circle cx="5" cy="5" r="3"/><circle cx="19" cy="19" r="3"/><path d="M5 8v9a3 3 0 0 0 3 3h8M8 5h8a3 3 0 0 1 0 6H9"/>',
  exam: '<rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 2h6v4H9zM8 12l2 2 5-5M9 18h6"/>',
  flag: '<path d="M5 22V3m0 1c5-4 9 4 14 0v10c-5 4-9-4-14 0"/>',
  review: '<path d="M3 11a9 9 0 1 1 2 7M3 4v7h7m2-4v6l4 2"/>',
  moon: '<path d="M20 15A9 9 0 0 1 9 3a9 9 0 1 0 11 12Z"/>'
};
const icon = (name, cls = '') => `<svg class="ui-icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${drawings[name]}</svg>`;
module.exports = function home({ courses, paths }) {
  const order = ['foundation', 'web', 'pwn', 'forensic', 'network', 'cloud', 'crypto', 'rev', 'misc'];
  const nodes = order.map(id => `<a class="subject-card" data-map-track="${id}" href="../tracks/${id}/"><img src="../assets/illustrations/${id}.webp" alt="" width="64" height="64"><div class="subject-copy"><div class="subject-title"><h3>${esc(courses[id].label)}</h3><span>${all(courses[id]).length}개 차시</span></div><p>${esc(courses[id].introduction.question)}</p></div>${icon('arrow','subject-arrow')}</a>`).join('\n');
  return { MAP_NODES:nodes,
    BRAND_WIREFRAME:require('./render_wordmark.cjs')(),
    BRAND_BACKDROP:require('./render_backdrop.cjs')(),
    ICON_HOME:icon('home'), ICON_BOOK:icon('book'), ICON_ROUTE:icon('route'), ICON_BOX:icon('box'), ICON_ARROW:icon('arrow'), ICON_GLOBE:icon('globe'), ICON_EXAM:icon('exam'), ICON_FLAG:icon('flag'), ICON_REVIEW:icon('review') };
};
