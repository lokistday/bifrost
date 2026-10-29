/* Static, account-free study library, final projects and prerequisite bridges. */
const fs = require('node:fs');
const path = require('node:path');
const { esc, all, slug } = require('../js/learning-view.js');

module.exports = function renderStudy({ ROOT, courses, site, fill, write }) {
  const template = fs.readFileSync(path.join(ROOT, 'templates/study.html'), 'utf8');
  const routes = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/generated-paths.json'), 'utf8'));
  const lookup = Object.fromEntries(Object.values(courses).flatMap(c => all(c).map(l => [l.id, { course:c, lesson:l }])));
  const href = id => `../tracks/${lookup[id].course.id}/${slug(id)}.html`;
  const lessonLink = (id, route = null) => `<a href="${route && route.sequence.includes(id) ? `${id}.html` : href(id)}">${esc(lookup[id].lesson.title)}</a>`;
  const pathStats = () => '<div class="course-stats"><span data-path-count></span><div class="course-meter" role="progressbar" aria-label="경로 차시 완료 진도" aria-valuemin="0" aria-valuemax="100" data-path-meter><span></span></div></div>';
  const list = values => `<ol>${values.map(v => `<li>${esc(v)}</li>`).join('')}</ol>`;
  const code = text => `<div class="code-shell"><pre><code>${esc(text)}</code></pre></div>`;
  const pages = [];
  function emit(route, title, description, content, scripts='', activePath=null) {
    fs.mkdirSync(path.dirname(path.join(ROOT, route)), {recursive:true});
    if (activePath) scripts += `\n<script src="../js/catalog.js?v=${esc(site.contentVersion)}" defer></script><script src="../js/learning-paths.js?v=${esc(site.contentVersion)}" defer></script><script src="../js/progress.js" defer></script><script src="../js/path-progress.js?v=${esc(site.contentVersion)}" defer></script>`;
    let html = fill(template, {TITLE:esc(`${title} · Bifrost`), DESCRIPTION:esc(description),
      CANONICAL:esc(site.url+route.replace(/index\.html$/,'')), SITE_URL:esc(site.url),
      CONTENT_VERSION:esc(site.contentVersion), CONTENT:content, SCRIPTS:scripts});
    if (activePath) html = html.replace(/(href|src)="\.\.\//g, '$1="../../')
      .replace('<body class="learning-page study-page">', `<body class="learning-page study-page" data-path="${activePath.id}">`);
    write(route,html);
    pages.push(route.replace(/index\.html$/,''));
  }
  const allLessons = Object.values(courses).flatMap(c => all(c).map(l => ({course:c,lesson:l})));
  emit('learn/index.html','검색과 목표별 학습 경로', '차시를 찾고, 준비 상태를 확인하고, 분야별 프로젝트로 배운 내용을 검증하세요.', `
    <header class="study-hero"><div class="overline">YOUR NEXT STEP</div><h1>배우는 순서부터<br>스스로 푸는 순간까지.</h1><p>${allLessons.length}개 차시를 검색하거나 목표별 경로를 선택하세요. 기초가 막히면 짧게 보충하고, 독립 과제와 종합 프로젝트로 이해를 확인합니다.</p></header>
    <nav class="study-jumps" aria-label="학습 도구"><a href="#paths">목표별 경로 ↓</a><a href="#search">전체 차시 검색 ↓</a><a href="#projects">종합 프로젝트 ↓</a><a href="../guides/bridges.html">기초 연결 ↗</a></nav>
    <section class="study-section" id="paths"><h2>목표가 있으면, 이 순서로</h2><p>각 경로에는 필요한 선행 차시를 먼저 배치했습니다. 경로 핵심과 권장 선행을 구분하되 강의를 잠그지는 않습니다. 목표 밖의 차시는 선택해서 더 공부하세요.</p><div class="path-grid">${routes.map(route => `
      <article class="path-card" id="path-${esc(route.id)}"><span class="overline">${route.sequence.length}단계 · 종합 프로젝트</span><h3>${esc(route.title)}</h3><p>${esc(route.description)}</p><a class="learning-button small" href="../paths/${route.id}/">과정 살펴보기 →</a></article>`).join('')}</div></section>
    <section class="study-section" id="search"><h2>지금 필요한 개념 찾기</h2><noscript><p>아래 전체 차시와 경로는 그대로 사용할 수 있습니다. 브라우저의 찾기(Ctrl+F)로 제목을 찾으세요.</p></noscript>
      <form class="search-form" id="lessonSearch" role="search" hidden><label for="searchQuery">제목 · 목표 · 핵심어<input id="searchQuery" type="search" maxlength="120" placeholder="예: 세션, 로그, DNS, 키" autocomplete="off"></label><label for="searchCourse">분야<select id="searchCourse"><option value="">모든 분야</option>${Object.values(courses).map(c=>`<option value="${c.id}">${esc(c.title)}</option>`).join('')}</select></label><label for="searchLevel">난이도<select id="searchLevel"><option value="">모든 난이도</option><option>기초</option><option>응용</option><option>심화 연결</option></select></label><button id="searchReset" class="learning-button small" type="button">초기화</button></form>
      <p id="searchStatus" class="search-status" role="status" aria-live="polite">전체 ${allLessons.length}개 차시</p><p id="searchEmpty" hidden>일치하는 차시가 없습니다. 검색어를 줄이거나 분야·난이도 필터를 초기화하세요.</p>
      <details class="catalog-disclosure" id="catalogResults"><summary>차시 목록 펼치기 <span>${allLessons.length}개 차시</span></summary><ul class="search-results">${allLessons.map(({course:c,lesson:l})=>`<li data-course="${c.id}" data-level="${esc(l.learning.level)}" data-search-item="${esc([c.title,c.label,l.title,l.goal,...l.learning.tags].join(' '))}"><a href="${href(l.id)}"><small>${esc(c.title)} · ${esc(l.learning.level)} · ${l.learning.minutes.join('–')}분</small><strong>${esc(l.title)}</strong><small>${esc(l.goal)}</small></a></li>`).join('')}</ul></details><p class="caption">학습 시간은 설치를 제외한 저자 추정입니다. 검색어·검색 결과를 서버로 전송하지 않습니다.</p></section>
    <section class="study-section" id="projects"><h2>배운 내용을 결과물로.</h2><p>차시를 마쳤다면 두 가지 표본을 풀고 근거를 정리해 보세요.</p><details class="catalog-disclosure"><summary>분야별 종합 프로젝트 보기 <span>9개 프로젝트</span></summary><div class="path-grid">${Object.values(courses).map(c=>`<article class="path-card"><span class="overline">${esc(c.title)}</span><h3>${esc(c.project.title)}</h3><p>${esc(c.project.problem)}</p><a href="../projects/${c.id}.html">과제·자료·평가 기준 보기 →</a></article>`).join('')}</div></details></section>`,
    `<script src="../js/study-search.js?v=${esc(site.contentVersion)}" defer></script>`);

  for (const c of Object.values(courses)) {
    for (const activePath of [null,...routes.filter(r=>r.project===c.id)]) {
    const p = c.project;
    const lab = `../labs/${c.id}/`;
    const artifactNames = fs.readdirSync(path.join(ROOT,'scripts/lab_sources',c.id)).filter(n=>n.startsWith('project-input-')||n==='project-role.json'||n==='project-build-db.py'||n==='project-machine.c'||n==='project-parser-starter.c'||n==='project-c-tests.py');
    emit(activePath ? `paths/${activePath.id}/project.html` : `projects/${c.id}.html`,activePath ? `${p.title} — ${activePath.title}` : p.title,p.problem,`
      <nav class="breadcrumb" aria-label="현재 위치"><a href="../learn/">학습 경로</a><span>/</span><a href="${activePath?'./':`../tracks/${c.id}/`}">${esc(activePath?activePath.title:c.title)}</a><span>/ 종합 프로젝트</span></nav>
      ${activePath?`<section class="path-context-banner"><a href="./">${esc(activePath.title)}</a><strong>마지막 단계 · 종합 프로젝트</strong><p>이 경로에서 배운 내용을 근거와 결과물로 연결합니다.</p>${pathStats()}<a href="${activePath.sequence.at(-1)}.html">← 마지막 차시 돌아보기</a></section>`:''}
      <header class="study-hero"><div class="overline">${esc(c.title)} / FINAL PROJECT</div><h1>${esc(p.title)}</h1><p>${esc(p.problem)}</p><div class="lesson-meta"><span>${p.minutes.join('–')}분 · 설치 제외 저자 추정</span><span>로컬 표본 · 계정 불필요</span><span>A/B 변형 + 근거 보고서</span></div></header>
      <ol class="project-flow" aria-label="프로젝트 진행 흐름"><li><b>01 · PREDICT</b><span>자료와 계약 읽기<br>실행 전 예상</span></li><li><b>02 · BUILD</b><span>A 표본 독립 풀이<br>정상·거부 검사</span></li><li><b>03 · TRANSFER</b><span>B 표본 재검증<br>새 반례 추가</span></li><li><b>04 · EXPLAIN</b><span>근거 보고서<br>루브릭 검토</span></li></ol>
      <nav class="study-jumps" aria-label="프로젝트 항목"><a href="#ready">준비 ↓</a><a href="#assignment">과제 ↓</a><a href="#check">검사 ↓</a><a href="#rubric">평가 ↓</a></nav>
      <section id="ready" class="study-section"><h2>먼저 준비할 것</h2><p>ZIP 전체를 풀고 원본을 보관하세요. 폴더 전체의 작업 사본에서 진행합니다. 모든 자료는 직접 만든 교육용 표본이며 외부 서비스에 접속할 필요가 없습니다.</p><ul>${p.prerequisites.map(id=>`<li>${lessonLink(id,activePath)}</li>`).join('')}</ul><div class="project-files"><a class="learning-button primary" href="../labs/${c.id}.zip" download>실습과 프로젝트 ZIP ↓</a><a class="learning-button" href="${lab}project-brief.md" download>과제 안내 ↓</a><a class="learning-button" href="${lab}project-report.md" download>보고서 양식 ↓</a></div><details><summary>표본·보조 파일 목록</summary><ul>${artifactNames.map(n=>`<li><a href="${lab}${encodeURIComponent(n)}" download>${esc(n)} ↓</a></li>`).join('')}</ul><p>각 파일을 따로 받으면 의존 파일이 빠질 수 있습니다. 실행할 때는 ZIP 전체를 사용하세요.</p></details></section>
      <section id="assignment" class="study-section"><h2>수행할 과제</h2>${list(p.tasks)}<div class="baseline-note"><h3>출력 계약</h3><p>${esc(p.contract)}</p><p>project-answer-template.json의 필드와 타입은 유지하고 직접 계산한 결과를 새 answers-a.json·answers-b.json에 넣습니다. 빈 목록과 0은 자리표시자입니다.</p></div></section>
      <section id="check" class="study-section"><h2>결과를 확인하는 방법</h2><p>각 분야 작업 폴더의 터미널에서 실행합니다. Linux/WSL/macOS는 python3, Windows PowerShell은 py -3를 사용하세요. Crypto는 가상 환경에 requirements.txt 설치가 필요합니다.</p>${code('python3 project.py check answers-a.json --variant a\npython3 project.py check answers-b.json --variant b')}
      ${c.id==='pwn' ? `<p>C 과제는 직접 작성한 소스를 로컬에서 컴파일·실행하는 별도 검사를 제공합니다. 격리된 테스트 환경에서 실행하세요. 처음 제공된 starter는 미완성이므로 검사가 실패해야 정상입니다.</p>${code('python3 project-c-tests.py --source project-parser-starter.c --sanitize')}` : ''}
      ${c.id==='forensic' ? `<p>SQLite 파일은 새 이름으로만 생성합니다. 이미 있으면 덮어쓰지 않고 멈춥니다.</p>${code('python3 project-build-db.py --variant a\npython3 project-build-db.py --variant b')}` : ''}
      <p>결과 검사기는 답안 JSON만 읽습니다. 코드를 실행하거나 서버로 제출하지 않습니다. 결과 일치(0)·불일치(1)·답안 입력 오류(2)를 구분합니다. 코드 품질과 보고서의 사실성은 아래 기준으로 별도 검토하세요.</p><details class="solution"><summary>독립 시도 후, 참고 결과와 풀이 읽기</summary><p>공개된 참조 구현입니다. 답을 본 뒤에는 새로운 반례를 직접 만들어 설명할 수 있는지 확인하세요.</p>${code('python3 project.py example --variant a\npython3 project.py example --variant b')}<a href="${lab}project_reference.py" download>참조 구현 읽기 ↓</a></details></section>
      <section id="rubric" class="study-section"><h2>완주를 판단하는 기준</h2><p>항목별 0 = 근거 없음 · 1 = 설명만 가능 · 2 = 재현할 근거 있음. 8점은 자기 평가 척도이며 인증 점수가 아닙니다. 각 항목에 해당하는 파일·명령·이벤트 위치를 보고서에 연결하세요.</p>${list(p.rubric)}<h3>보고서에 남길 것</h3><p>범위·환경 → 예상 → 실제 관찰 → A/B 차이 → 반례와 수정 → 미확인 사항. 해시·종료 상태·테스트 결과만으로 모든 결론을 증명했다고 표현하지 마세요.</p><p>1–3일 뒤 답안 없이 B를 다시 풀거나 새 입력을 만들어 확인하세요. 설명이 막히면 해당 선행 차시로 돌아가 필요한 부분을 보충합니다.</p></section>
      <section class="study-section"><h2>실제 형식으로 연결하기</h2><p>${esc(p.bridge)}</p><h3>이 프로젝트의 범위</h3><p>${esc(p.limitations)}</p><a class="learning-button" href="${activePath?'./':'../learn/#projects'}">${activePath?'경로 전체 돌아보기':'다른 분야 프로젝트 보기'} ↗</a></section>`,'',activePath);
    }
  }

  for (const route of routes) {
    const project = courses[route.project].project;
    const groups = [];
    route.sequence.forEach((id,index)=>{
      const course = lookup[id].course;
      if (groups.at(-1)?.course!==course) groups.push({course,items:[]});
      groups.at(-1).items.push({id,index});
    });
    emit(`paths/${route.id}/index.html`,route.title,route.description,`
      <nav class="breadcrumb" aria-label="현재 위치"><a href="../learn/#paths">학습 경로</a><span>/</span><span aria-current="page">${esc(route.title)}</span></nav>
      <header class="study-hero"><div class="overline">GUIDED LEARNING PATH</div><h1>${esc(route.title)}</h1><p>${esc(route.description)}</p><div class="lesson-meta"><span>${route.sequence.length}단계 + 종합 프로젝트</span><span>${new Set(route.sequence.map(id=>lookup[id].course.id)).size}개 분야 연결</span></div></header>
      <section class="path-context-banner"><h2>이 경로의 순서로 이어서 공부하기</h2><p>차시를 열면 이 경로의 목차와 이전·다음 단계가 유지됩니다. 익숙한 선행 차시는 목차에서 건너뛰어도 됩니다.</p>${pathStats()}<a class="learning-button primary" id="continuePath" href="${route.sequence[0]}.html">첫 단계 학습하기 →</a><p class="caption">완료 기록은 같은 차시를 공유하며 이 경로에 포함된 단계만 집계합니다. 프로젝트 수행 여부는 아래 평가 기준으로 직접 확인하세요.</p></section>
      <section class="study-section" id="pathOutline"><h2>처음부터 마지막 결과물까지</h2>${groups.map((group,gi)=>`<details class="path-stage" ${gi===0?'open':''}><summary>${esc(group.course.title)}<span>${group.items[0].index+1}–${group.items.at(-1).index+1}단계</span></summary><ol class="path-outline">${group.items.map(({id,index})=>`<li><a href="${id}.html"><span class="path-step-number">${index+1}</span><span><small>${esc(lookup[id].course.title)} · ${route.lessons.includes(id)?'경로 핵심':'권장 선행'}</small><strong>${esc(lookup[id].lesson.title)}</strong><small>${esc(lookup[id].lesson.goal)}</small><small data-completion="${id}"></small></span><span aria-hidden="true">↗</span></a></li>`).join('')}</ol></details>`).join('')}</section>
      <section class="project-callout"><span class="overline">FINAL PROJECT</span><h2>${esc(project.title)}</h2><p>${esc(project.problem)}</p><a class="learning-button" href="project.html">이 경로의 종합 프로젝트 →</a></section>`,'',route);
  }

  const bridges = [
    ['python','Python 객체와 자료 계약','목록은 값의 순서를, 딕셔너리는 키와 값의 관계를 표현합니다. 변수가 같은 변경 가능한 객체를 가리키는지와 값이 같은지를 구분하세요. JSON의 true는 Python bool로 읽힙니다.',
     'a = [{"count": 1}]\nb = a.copy()\nb[0]["count"] = 2\nprint(a[0]["count"])\nprint(type(True) is int)',
     '2와 False입니다. 바깥 목록을 복사해도 안쪽 딕셔너리는 공유됩니다. 정수 계약에 bool을 받지 않으려면 타입을 구분합니다.',
     '딕셔너리 안에 목록을 넣고 얕은/깊은 복사 후 원본을 비교하세요.', ['foundation.mutable-data','foundation.structured-data']],
    ['c','C의 객체·구조체·파일 디스크립터','포인터는 객체의 주소를 담으며 객체의 수명을 늘려 주지 않습니다. 구조체는 필드를 묶지만 패딩 때문에 sizeof가 필드 크기 합과 다를 수 있습니다. 파일 디스크립터는 바이트 버퍼 주소가 아니라 프로세스의 열린 파일 참조 번호입니다.',
     '#include <stdio.h>\nstruct pair { char kind; int count; };\nint main(void) {\n    struct pair p = {\'A\', 3};\n    struct pair *q = &p;\n    q->count = 4;\n    printf("count=%d size=%zu\\n", p.count, sizeof p);\n    return 0;\n}',
     'bridge.c에 저장하고 gcc -std=c11 -Wall -Wextra bridge.c -o bridge && ./bridge로 실행합니다. count=4이고 size는 ABI에 따라 달라질 수 있습니다. q->count와 p.count는 같은 객체의 필드입니다.',
     'p를 직렬화할 때 메모리를 통째로 복사하지 않고 필드 폭과 순서를 정해야 하는 이유를 쓰세요.', ['foundation.c-memory','pwn.struct-layout','pwn.file-descriptors']],
    ['bytes','문자·바이트·엔디언','화면 글자 수·문자열 길이·바이트 길이를 혼동하지 않습니다. 숫자 바이트에는 폭과 순서를 명시하고, 같은 바이트의 signed/unsigned 해석을 구별하세요.',
     'raw = bytes.fromhex("0100")\nprint(int.from_bytes(raw, "big"))\nprint(int.from_bytes(raw, "little"))\nprint(len("가"), len("가".encode("utf-8")))',
     '256, 1, 그리고 1 3입니다. 숫자 폭·바이트 순서·텍스트 인코딩은 별도 계약입니다.',
     '00ff를 big/little-endian으로 예측하고 중간 NUL이 있는 문자열과 이진 데이터도 비교하세요.', ['foundation.text-bytes','rev.byte-order','pwn.binary-strings']],
    ['web','요청과 인증·인가의 경계','브라우저가 보내는 값은 요청입니다. 요청자의 신원은 신뢰한 세션 검증으로 정하고, 소유자와 권한은 서버가 가진 상태를 기준으로 확인해야 합니다. HTML 해석·CORS·CSRF는 각각 다른 경계입니다.',
     '주체 확인 → 대상 조회 → 행동 권한 확인 → 입력 계약 확인 → 상태 변경 → 응답\n실패한 요청 → 상태 유지 + 필요한 최소 오류 정보',
     '클라이언트의 owner=alice 값을 신뢰해 권한을 정하면 안 됩니다. 세션이 유효하다는 사실만으로 다른 사용자의 자원 수정이 허용되지 않습니다.',
     '정상 주체·타인 자원·알 수 없는 필드를 조합한 4칸 시험표를 쓰세요.', ['web.sessions','web.authorization','web.mass-assignment']],
    ['evidence','관찰·추론·미확인을 분리하기','원시 자료에서 읽은 필드와 그 필드로 세운 가설은 다른 종류의 문장입니다. 시간 순서는 인과가 아니며 로그가 없다는 사실도 수집 범위를 확인하기 전에는 행위 부재의 증명이 아닙니다.',
     '관찰: E3에 session=S7, event=read가 기록됨\n추론: 같은 호스트의 로그인과 연결될 가능성\n미확인: 실제 사용자 의도·파일 외부 반출\n추가 자료: 세션 발급 이력·파일 내용·송신 기록',
     '모든 결론에 자료 위치를 붙이고 가능한 대안 가설을 하나 이상 남깁니다. ±5초인 두 이벤트의 구간이 겹치면 순서를 확정하지 않습니다.',
     '실패 로그인 뒤 성공 로그를 보고 사실 2개·가설 2개·추가 자료 2개를 작성하세요.', ['forensic.logs','forensic.log-correlation','forensic.evidence-coverage']],
    ['network','도달·권한·관측을 따로 보기','DNS로 목적지를 찾는 일, 경로로 도달하는 일, 요청 권한을 허용하는 일, 그 사건을 로그에서 보는 일은 서로 다릅니다. IPv4/IPv6와 왕복 경로도 따로 확인해야 합니다.',
     '이름 해석 → 라우팅/연결 → 프로토콜 처리 → 신원/권한 → 업무 결과\n센서·로그 수집은 각 단계에서 실제 관측 범위를 확인',
     '사설 IP만으로 권한이 생기지 않고, 감사 enabled=true만으로 끝까지 전달됐음을 증명할 수 없습니다. 한 단계의 실패를 모든 단계의 실패로 뭉뚱그리지 않습니다.',
     'DNS 성공·TCP 시간 초과·HTTP 403·감사 로그 누락을 각 단계와 추가 확인 자료로 분류하세요.', ['foundation.network','network.routing','cloud.private-endpoint-paths']]
  ];
  emit('guides/bridges.html','막힌 기초를 연결하는 짧은 연습','객체·C·바이트·웹·증거·네트워크를 짧은 확인 문제로 연결합니다.', `
    <header class="study-hero"><div class="overline">BRIDGE THE GAP</div><h1>막힌 개념만 짧게 연결하세요.</h1><p>본 차시로 돌아가기 전에 10–20분 정도 확인하는 보충 연습입니다. 계산 예측 → 실행 또는 근거 확인 → 자기 설명 순서로 진행합니다.</p></header><nav class="study-jumps" aria-label="기초 보충 주제">${bridges.map(b=>`<a href="#${b[0]}">${esc(b[1])} ↓</a>`).join('')}</nav>${bridges.map(([id,title,description,example,answer,task,refs])=>`<section class="bridge-card" id="${id}"><h2>${esc(title)}</h2><p>${esc(description)}</p>${code(example)}<p><strong>직접 확인:</strong> ${esc(task)}</p><details><summary>판단 기준과 실행 안내</summary><p>${esc(answer)}</p></details><p>이어지는 차시: ${refs.map(id=>lessonLink(id)).join(' · ')}</p></section>`).join('')}<a class="learning-button" href="../learn/">학습 경로로 돌아가기 →</a>`);
  return pages;
};
