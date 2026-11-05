/* Static, account-free study library, final projects and prerequisite bridges. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { esc, all, slug } = require('../js/learning-view.js');

module.exports = function renderStudy({ ROOT, courses, site, fill, write }) {
  const projectVersion = 'project-' + crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,'css/projects.css'))).update(fs.readFileSync(path.join(ROOT,'js/project-motion.js'))).digest('hex').slice(0,12);
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
    if (activePath) scripts += `\n<script src="../js/catalog.js?v=${esc(site.contentVersion)}" defer></script><script src="../js/learning-paths.js?v=${esc(site.contentVersion)}" defer></script><script src="../js/progress.js?v=${esc(site.contentVersion)}" defer></script><script src="../js/path-progress.js?v=${esc(site.contentVersion)}" defer></script>`;
    let html = fill(template, {TITLE:esc(`${title} · Bifrost`), DESCRIPTION:esc(description),
      CANONICAL:esc(site.url+route.replace(/index\.html$/,'')), SITE_URL:esc(site.url),
      CONTENT_VERSION:esc(site.contentVersion), CONTENT:content, SCRIPTS:scripts});
    if (activePath) html = html.replace(/(href|src)="\.\.\//g, '$1="../../')
      .replace('<body class="learning-page study-page">', `<body class="learning-page study-page" data-path="${activePath.id}">`);
    if (route === 'projects/index.html') {
      const icons = { home:'<path d="m3 10 9-7 9 7v11h-6v-7H9v7H3z"/>', paths:'<circle cx="6" cy="5" r="3"/><circle cx="18" cy="19" r="3"/><path d="M6 8v7a4 4 0 0 0 4 4h5M9 5h9"/>', projects:'<path d="m12 2 9 5v10l-9 5-9-5V7zM3 7l9 5 9-5M12 12v10M7.5 4.5l9 5"/>', exams:'<rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 4V2h6v2M8 12l3 3 5-6"/>' };
      const entries = [['home','../','홈'],['paths','../learn/','학습 경로'],['projects','./','프로젝트'],['exams','../exams/','모의고사']];
      const rail = `<aside class="project-rail" aria-label="빠른 이동"><a class="project-rail-brand" href="../" aria-label="Bifrost 홈"><img src="../assets/logo.svg?v=${esc(site.contentVersion)}" width="34" height="34" alt=""><span>BIFROST</span></a><nav aria-label="주 메뉴">${entries.map(([id,url,label])=>`<a href="${url}"${id==='projects'?' aria-current="page"':''}><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true">${icons[id]}</svg><span>${label}</span></a>`).join('')}</nav><button class="project-theme-toggle" id="themeToggle" type="button" aria-label="테마 전환" aria-pressed="false">테마 전환</button></aside>`;
      html = html.replace('class="learning-page study-page"','class="learning-page study-page project-catalog-page"').replace(/<header class="topbar">[\s\S]*?<\/header>/,rail);
    }
    write(route,html);
    pages.push(route.replace(/index\.html$/,''));
  }
  emit('learn/index.html','학습 경로', '목표에 맞는 경로를 선택하고 순서대로 학습하세요.', `
    <header class="study-hero"><div class="overline">LEARNING PATHS</div><h1>학습 경로</h1><p>목표에 맞는 경로를 고르고, 기초부터 순서대로 학습하세요.</p></header>
    <section class="study-section" id="paths"><h2>목표가 있으면, 이 순서로</h2><p>각 경로에는 필요한 선행 차시를 먼저 배치했습니다. 경로 핵심과 권장 선행을 구분하되 강의를 잠그지는 않습니다. 목표 밖의 차시는 선택해서 더 공부하세요.</p><div class="path-grid">${routes.map(route => `
      <article class="path-card" id="path-${esc(route.id)}"><span class="overline">${route.sequence.length}단계 · 종합 프로젝트</span><h3>${esc(route.title)}</h3><p>${esc(route.description)}</p><a class="learning-button small" href="../paths/${route.id}/">과정 살펴보기 →</a></article>`).join('')}</div></section>`);

  const projectPresentation = {
    foundation: ['로그 요약기', 'CSV 기록을 분석하고, 잘못된 입력의 근거까지 남기는 도구를 만드세요.'],
    web: ['안전한 예약 서비스', '세션 만료와 중복 요청을 구분하고, 재전송에도 안전한 예약을 구현하세요.'],
    forensic: ['디지털 증거 보고서', '호스트와 세션의 관계를 조사하고, 자료 위치를 추적할 수 있는 보고서를 만드세요.'],
    pwn: ['경계를 지키는 C 파서', '길이와 NUL, 잘린 입력을 구분하는 작은 레코드 파서를 구현하세요.'],
    network: ['네트워크 정책 검증', 'IPv4·IPv6 경로의 접근 정책을 검사하고 관측의 공백을 설명하세요.'],
    cloud: ['클라우드 변경 검토', '사설 경로와 긴급 권한의 경계를 확인하고 보안 승인 보고서를 작성하세요.'],
    crypto: ['암호화 레코드 검증', '문서 문맥과 재전송 상태, 키 교체를 함께 검증하는 계획을 세우세요.'],
    rev: ['프로그램 상태 복원', '입력 순서에 따라 달라지는 프로그램의 상태와 결과를 복원하세요.'],
    misc: ['제한된 변환 파이프라인', '압축 표본을 정해진 한도 안에서 풀고, 불완전한 스트림을 검증하세요.']
  };
  emit('projects/index.html','프로젝트', '분야별 종합 프로젝트로 배운 내용을 결과물로 연결하세요.', `
    <div class="project-catalog">
      <header class="project-catalog-hero"><div class="project-overline">FINAL PROJECTS</div><h1>프로젝트</h1><p>배운 내용을 결과물로.</p></header>
      <section class="project-showcase" id="projects" aria-label="분야별 종합 프로젝트">
        ${Object.entries(projectPresentation).map(([id,[title,description]],i)=>{const c=courses[id];return `<article class="project-panel" aria-labelledby="project-${id}">
          <div class="project-panel-art"><img src="../assets/projects/${id}.webp?v=${esc(site.contentVersion)}" width="960" height="640" alt="" ${i>1?'loading="lazy"':'loading="eager"'} decoding="async"></div>
          <div class="project-panel-copy"><span class="project-subject">${esc(c.label)}</span><h2 id="project-${id}">${esc(title)}</h2><p>${esc(description)}</p><div class="project-panel-meta"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/></svg><span>${c.project.minutes.join('–')}분 <span aria-hidden="true">·</span> A/B 검증</span></div><a class="project-open" href="${id}.html" aria-label="프로젝트 살펴보기 · ${esc(title)}">프로젝트 살펴보기 <span aria-hidden="true">→</span></a></div>
        </article>`;}).join('')}
      </section>
      <p class="project-catalog-note">9개 분야의 종합 과제 · 예상 시간은 설치를 제외한 저자 추정입니다.</p>
    </div>`, `<link rel="stylesheet" href="../css/projects.css?v=${projectVersion}"><script src="../js/project-motion.js?v=${projectVersion}" defer></script>`);

  for (const c of Object.values(courses)) {
    for (const activePath of [null,...routes.filter(r=>r.project===c.id)]) {
    const p = c.project;
    const lab = `../labs/${c.id}/`;
    const artifactNames = fs.readdirSync(path.join(ROOT,'scripts/lab_sources',c.id)).filter(n=>n.startsWith('project-input-')||n==='project-role.json'||n==='project-build-db.py'||n==='project-machine.c'||n==='project-parser-starter.c'||n==='project-c-tests.py');
    emit(activePath ? `paths/${activePath.id}/project.html` : `projects/${c.id}.html`,activePath ? `${p.title} — ${activePath.title}` : p.title,p.problem,`
      <nav class="breadcrumb" aria-label="현재 위치"><a href="${activePath?'../learn/':'../projects/'}">${activePath?'학습 경로':'프로젝트'}</a><span>/</span><a href="${activePath?'./':`../tracks/${c.id}/`}">${esc(activePath?activePath.title:c.title)}</a><span>/ 종합 프로젝트</span></nav>
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
      <section id="rubric" class="study-section"><h2>완주를 판단하는 기준</h2><p>항목별 0 = 근거 없음 · 1 = 설명만 가능 · 2 = 재현할 근거 있음. 8점은 자기 평가 척도이며 인증 점수가 아닙니다. 각 항목에 해당하는 파일·명령·이벤트 위치를 보고서에 연결하세요.</p>${list(p.rubric)}<details class="project-review"><summary>좋은 근거와 부족한 근거 비교</summary><p><strong>부족한 기록:</strong> “검사 PASS. 잘 동작함.” 실행한 입력·버전·실패 조건을 확인할 수 없습니다.</p><p><strong>확인 가능한 기록:</strong> “${esc(p.rubric[0])}”를 뒷받침하는 A/B 입력 이름, 실행 명령, 출력 파일, 실패 반례와 수정 전·후 차이를 붙입니다. 결과를 직접 계산한 코드 위치를 연결하고 정답을 상수로 넣지 않았는지 검토합니다.</p><ol><li>입력 값을 바꿔도 결과를 계산하는지 확인</li><li>정상·거부·경계 테스트를 각각 실행</li><li>실제 출력과 보고서 문장이 일치하는지 검토</li><li>해설 없이 새 표본의 예상 결과 설명</li></ol></details><h3>보고서에 남길 것</h3><p>범위·환경 → 예상 → 실제 관찰 → A/B 차이 → 반례와 수정 → 미확인 사항. 해시·종료 상태·테스트 결과만으로 모든 결론을 증명했다고 표현하지 마세요.</p><p>1–3일 뒤 답안 없이 B를 다시 풀거나 새 입력을 만들어 확인하세요. 설명이 막히면 해당 선행 차시로 돌아가 필요한 부분을 보충합니다.</p></section>
      <section class="study-section"><h2>실제 형식으로 연결하기</h2><p>${esc(p.bridge)}</p><h3>이 프로젝트의 범위</h3><p>${esc(p.limitations)}</p><a class="learning-button" href="${activePath?'./':'../projects/'}">${activePath?'경로 전체 돌아보기':'다른 분야 프로젝트 보기'} ↗</a></section>`,'',activePath);
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
      <nav class="breadcrumb" aria-label="현재 위치"><a href="../learn/">학습 경로</a><span>/</span><span aria-current="page">${esc(route.title)}</span></nav>
      <header class="study-hero"><div class="overline">GUIDED LEARNING PATH</div><h1>${esc(route.title)}</h1><p>${esc(route.description)}</p><div class="lesson-meta"><span>${route.sequence.length}단계 + 종합 프로젝트</span><span>${new Set(route.sequence.map(id=>lookup[id].course.id)).size}개 분야 연결</span></div></header>
      <section class="path-context-banner"><h2>이 경로의 순서로 이어서 공부하기</h2><p>차시를 열면 이 경로의 목차와 이전·다음 단계가 유지됩니다. 익숙한 선행 차시는 목차에서 건너뛰어도 됩니다.</p>${pathStats()}<a class="learning-button primary" id="continuePath" href="${route.sequence[0]}.html">첫 단계 학습하기 →</a><p class="caption">완료 기록은 같은 차시를 공유하며 이 경로에 포함된 단계만 집계합니다. 프로젝트 수행 여부는 아래 평가 기준으로 직접 확인하세요.</p></section>
      <section class="study-section" id="milestones"><h2>짧은 구간으로 나누어 완주하기</h2><p>한 구간은 최대 5차시입니다. 이미 아는 내용은 차시의 준비 진단과 독립 과제로 확인한 뒤 건너뛰세요. 시간은 설치·프로젝트를 제외한 편집자 추정입니다.</p><div class="path-grid">${route.milestones.map(stage=>`<article class="path-card"><span class="overline">구간 ${stage.number} · ${stage.lessons.length}차시 · ${stage.minutes.join('–')}분</span><h3>${esc(stage.title)}</h3><p>${esc(stage.outcome)}</p><details><summary>이 구간의 작은 결과물</summary><p>${esc(stage.artifact)}</p></details><a href="${stage.lessons[0]}.html">이 구간 시작 →</a></article>`).join('')}</div></section><section class="study-section" id="pathOutline"><h2>처음부터 마지막 결과물까지</h2>${groups.map((group,gi)=>`<details class="path-stage" ${gi===0?'open':''}><summary>${esc(group.course.title)}<span>${group.items[0].index+1}–${group.items.at(-1).index+1}단계</span></summary><ol class="path-outline">${group.items.map(({id,index})=>`<li><a href="${id}.html"><span class="path-step-number">${index+1}</span><span><small>${esc(lookup[id].course.title)} · ${route.lessons.includes(id)?'경로 핵심':'권장 선행'}</small><strong>${esc(lookup[id].lesson.title)}</strong><small>${esc(lookup[id].lesson.goal)}</small><small data-completion="${id}"></small></span><span aria-hidden="true">↗</span></a></li>`).join('')}</ol></details>`).join('')}</section>
      <section class="project-callout"><span class="overline">FINAL PROJECT</span><h2>${esc(project.title)}</h2><p>${esc(project.problem)}</p><a class="learning-button" href="project.html">이 경로의 종합 프로젝트 →</a></section>`,'',route);
  }

  return pages;
};
