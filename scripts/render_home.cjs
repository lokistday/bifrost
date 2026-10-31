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
  search: '<circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/>',
  arrow: '<path d="M4 12h16m-6-6 6 6-6 6"/>',
  route: '<circle cx="5" cy="5" r="3"/><circle cx="19" cy="19" r="3"/><path d="M5 8v9a3 3 0 0 0 3 3h8M8 5h8a3 3 0 0 1 0 6H9"/>',
  moon: '<path d="M20 15A9 9 0 0 1 9 3a9 9 0 1 0 11 12Z"/>'
};
const icon = (name, cls = '') => `<svg class="ui-icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${drawings[name]}</svg>`;
module.exports = function home({ courses, paths }) {
  const data = [
    ['foundation','book','공통 기초','보안 학습을 위한 필수 개념과 도구, 환경을 익힙니다.',['Linux','Python','네트워크','명령어']],
    ['web','globe','웹 해킹','웹 서비스의 동작과 인증·권한 경계를 이해합니다.',['Web','HTTP','SQL','인증']],
    ['pwn','chip','Pwn / 시스템','메모리를 관찰하고 시스템의 경계를 검증합니다.',['Binary','Memory','GDB','Linux']],
    ['forensic','file','디지털 포렌식','디지털 증거를 분석하고 판단의 근거를 남깁니다.',['Forensic','증거 분석','타임라인']],
    ['network','network','네트워크 보안','통신 흐름을 읽고 네트워크 정책을 검증합니다.',['Network','패킷 분석','탐지']],
    ['cloud','cloud','클라우드 보안','클라우드의 신원·권한·감사·복구를 연결합니다.',['Cloud','IAM','컨테이너','복구']],
    ['crypto','lock','암호학','암호 기술의 원리와 안전한 사용 조건을 배웁니다.',['암호 이론','해시','대칭키','공개키']],
    ['rev','code','리버스 엔지니어링','프로그램의 실행 흐름과 동작을 분석합니다.',['Reverse','정적 분석','디버깅']],
    ['misc','grid','문제 해결 · 자동화','데이터에서 단서를 찾고 반복 작업을 자동화합니다.',['데이터','인코딩','자동화']]
  ];
  const nodes = data.map(([id, symbol, title, description, tags], index) => `<a class="subject-card" data-map-track="${id}" href="tracks/${id}/"><span class="subject-number">${String(index+1).padStart(2,'0')}</span>${icon(symbol)}<div class="subject-copy"><div class="subject-title"><h3>${esc(title)}</h3><span>${all(courses[id]).length}개 차시</span></div></div><span class="subject-arrow" aria-hidden="true">›</span></a>`).join('\n');
  const route = paths.find(p=>p.id==='start');
  const lookup = Object.fromEntries(Object.values(courses).flatMap(c=>all(c).map(l=>[l.id,l])));
  const lessons = route.sequence.slice(0,5).map((id,i)=>`<li data-home-lesson="${id}"><a href="paths/start/${id}.html"><span class="lesson-dot" aria-hidden="true"></span><span class="lesson-number">${String(i+1).padStart(2,'0')}</span><span>${esc(lookup[id].title)}</span><span class="lesson-state sr-only">미완료</span></a></li>`).join('');
  return { MAP_NODES:nodes, START_LESSONS:lessons, START_COUNT:route.sequence.length,
    ICON_HOME:icon('home'), ICON_BOOK:icon('book'), ICON_ROUTE:icon('route'), ICON_BOX:icon('box'), ICON_SEARCH:icon('search'), ICON_ARROW:icon('arrow'), ICON_GLOBE:icon('globe') };
};
