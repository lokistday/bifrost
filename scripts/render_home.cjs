/* Field links use the same course identifiers and lesson counts as the curriculum. */
const { esc, all } = require('../js/learning-view.js');
const drawings = {
  terminal: '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m6 8 4 4-4 4m7 0h5"/>',
  browser: '<rect x="2" y="3" width="20" height="18" rx="2"/><path d="M2 9h20M6 6h.1M9 6h.1M12 6h.1"/>',
  chip: '<rect x="5" y="5" width="14" height="14" rx="2"/><path d="M9 1v4m6-4v4M9 19v4m6-4v4M1 9h4m-4 6h4m14-6h4m-4 6h4"/><path d="M9 9h6v6H9z"/>',
  file: '<path d="M5 2h10l4 4v16H5ZM14 2v5h5M9 11h6m-6 4h6m-6 4h4"/>',
  network: '<circle cx="12" cy="4" r="3"/><circle cx="4" cy="19" r="3"/><circle cx="20" cy="19" r="3"/><path d="M12 7v5m0 0-7 4m7-4 7 4"/>',
  cloud: '<path d="M7 19a5 5 0 1 1 .2-10A7 7 0 0 1 21 11a4 4 0 0 1-1 8Z"/>',
  lock: '<rect x="4" y="10" width="16" height="12" rx="2"/><path d="M8 10V6a4 4 0 0 1 8 0v4m-4 5v3"/>',
  code: '<path d="m7 6-5 6 5 6m10-12 5 6-5 6M14 3l-4 18"/>',
  grid: '<path d="M3 3h6v6H3zm12 0h6v6h-6zM3 15h6v6H3zm12 0h6v6h-6z"/>',
  arrow: '<path d="M3 12h17m-6-6 6 6-6 6"/>'
};
const icon = (name, cls = '') => `<svg class="ui-icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${drawings[name]}</svg>`;
module.exports = function home({ courses }) {
  const data = [
    ['foundation','terminal','공통 기초','명령어를 익히고 첫 Python 예제를 실행해요.'],
    ['web','browser','웹 해킹','웹 요청과 응답 살펴보기'],
    ['pwn','chip','Pwn / 시스템','메모리와 프로그램 구조 읽기'],
    ['forensic','file','디지털 포렌식','파일에서 사건의 단서 찾기'],
    ['network','network','네트워크 보안','패킷에서 통신 흐름 읽기'],
    ['cloud','cloud','클라우드 보안','클라우드 권한과 설정 점검하기'],
    ['crypto','lock','암호학','암호화와 서명의 원리 이해하기'],
    ['rev','code','리버스 엔지니어링','프로그램의 동작 원리 추적하기'],
    ['misc','grid','문제 해결 · 자동화','반복 작업을 코드로 줄이기']
  ];
  const nodes = data.map(([id, symbol, title, description]) => {
    const featured = id === 'foundation';
    return `<a class="subject-card${featured ? ' subject-featured' : ''}" data-map-track="${id}" href="../tracks/${id}/">
      ${icon(symbol)}
      <div class="subject-copy"><h2>${esc(title)}</h2><p>${esc(description)}</p></div>
      <span class="subject-count">${all(courses[id]).length}개 차시</span>${featured ? '<span class="subject-action" aria-hidden="true">공통 기초 열기</span>' : ''}
      ${icon('arrow', 'subject-arrow')}
    </a>`;
  }).join('\n');
  return { MAP_NODES: nodes };
};
