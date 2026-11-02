/* Static problem statements, progressive hints, and a private review dashboard. */
const fs=require('node:fs');
const path=require('node:path');
const {esc,all,slug}=require('../js/learning-view.js');
module.exports=({ROOT,courses,site,fill,write})=>{
  const template=fs.readFileSync(path.join(ROOT,'templates/study.html'),'utf8');
  const challenges=JSON.parse(fs.readFileSync(path.join(ROOT,'content/wargames.json'),'utf8'));
  const lookup=Object.fromEntries(Object.values(courses).flatMap(c=>all(c).map(l=>[l.id,l])));
  const paths=[];
  function emit(route,title,content,scripts='') {
    fs.mkdirSync(path.dirname(path.join(ROOT,route)),{recursive:true});
    write(route,fill(template,{TITLE:esc(title+' · Bifrost'),DESCRIPTION:esc(title),CANONICAL:esc(site.url+route.replace(/index\.html$/,'')),SITE_URL:esc(site.url),CONTENT_VERSION:esc(site.contentVersion),CONTENT:content,SCRIPTS:scripts}));
    paths.push(route.replace(/index\.html$/,''));
  }
  const script=name=>`<script src="../js/${name}?v=${esc(site.contentVersion)}" defer></script>`;
  const badge='<p class="caption">개인 학습용 문제입니다. 해결 기록은 이 브라우저에 저장됩니다. FLAG 일치와 독립 풀이 능력은 별도로 확인하세요.</p>';
  const disclosure='<details class="practice-limits"><summary>채점과 기록의 범위</summary><p>정적 사이트의 브라우저 검증이므로 자료·검증 정보는 공개되어 있으며 우회가 가능합니다. 공개 경쟁·실력 인증용 채점이 아닙니다. 계정 동기화는 없고 브라우저 데이터 삭제 전 기록을 백업하세요.</p></details>';
  emit('wargame/index.html','실습으로 푸는 워게임',`
    <header class="study-hero"><div class="overline">PRACTICE → FIND FLAG → SUBMIT</div><h1>직접 풀고, FLAG로 확인하세요.</h1><p>문제를 고르고 실습 자료를 내려받으세요. 관찰·분석으로 FLAG를 얻어 제출하면 해결 기록이 남습니다.</p></header>
    <ol class="project-flow"><li><b>01 문제 읽기</b><span>목표·준비 지식 확인</span></li><li><b>02 실습하기</b><span>자료 분석 또는 로컬 실행</span></li><li><b>03 FLAG 제출</b><span>BIFROST{...} 입력</span></li><li><b>04 다시 설명하기</b><span>풀이와 새 반례 기록</span></li></ol>
    ${badge}<p id="wargameSummary" role="status"></p><div class="challenge-filters js-only" hidden><label>분야 <select id="challengeCourse"><option value="">모든 분야</option>${Object.values(courses).map(c=>`<option value="${c.id}">${esc(c.title)}</option>`).join('')}</select></label><label>해결 상태 <select id="challengeState"><option value="">전체</option><option value="unsolved">미해결</option><option value="solved">해결</option></select></label></div>
    <div class="path-grid">${challenges.map(c=>`<article class="path-card challenge-card" data-challenge-card="${c.id}" data-course="${c.course}"><span class="overline">${esc(courses[c.course].title)} · ${esc(c.level)}</span><h2><a href="${c.id}.html">${esc(c.title)}</a></h2><p>${esc(c.objective)}</p><span data-solved-label="${c.id}">미해결</span><a class="learning-button small" href="${c.id}.html">문제 풀기 →</a></article>`).join('')}</div><p id="challengeEmpty" hidden>조건에 맞는 문제가 없습니다.</p>${disclosure}
    <details><summary>워게임 기록 백업</summary><button class="learning-button small js-only" hidden id="exportWargame" type="button">해결 기록 내보내기</button><label class="learning-button small js-only" hidden>기록 합치기<input id="importWargame" type="file" accept="application/json,.json"></label><p id="wargameBackupFeedback" role="status"></p></details>`,script('wargames.js')+script('wargame.js'));
  for(const c of challenges)emit(`wargame/${c.id}.html`,c.title,`
    <nav class="breadcrumb"><a href="./">워게임</a><span>/ ${esc(courses[c.course].title)}</span><span>/ ${esc(c.level)}</span></nav>
    <header class="study-hero"><div class="overline">${esc(courses[c.course].title)} / ${esc(c.level)}</div><h1>${esc(c.title)}</h1><p>${esc(c.description)}</p></header>
    <section class="study-section"><h2>해결 목표</h2><p>${esc(c.objective)}</p><p>FLAG 형식은 <code>BIFROST{...}</code>입니다. 대소문자와 중괄호를 그대로 입력하세요.</p><a class="learning-button primary" href="files/${c.archive}" download>문제 자료 ZIP ↓</a><details><summary>다운로드 무결성 확인</summary><p class="artifact-hash">SHA-256: ${esc(c.sha256)}</p></details></section>
    <section class="study-section"><h2>막히면 먼저 볼 차시</h2><ul>${c.lessons.map(id=>`<li><a href="../tracks/${id.split('.')[0]}/${slug(id)}.html">${esc(lookup[id].title)} ↗</a></li>`).join('')}</ul><p><a href="../guides/troubleshooting.html">실행 환경·파일·출력이 예상과 다를 때 ↗</a></p></section>
    <section class="flag-panel" data-challenge="${c.id}"><h2>FLAG 제출</h2><span data-solved-label="${c.id}">미해결</span><form id="flagForm" hidden><label for="flagInput">찾은 FLAG<input id="flagInput" type="text" autocomplete="off" spellcheck="false" maxlength="256" placeholder="BIFROST{...}" required></label><button class="learning-button primary" type="submit">제출하기</button></form><noscript><p>FLAG 검증과 해결 기록에는 JavaScript가 필요합니다. 문제와 자료는 그대로 읽고 내려받을 수 있습니다.</p></noscript><p id="flagFeedback" role="status" aria-live="polite"></p><p id="attemptCount" class="caption"></p>${badge}</section>
    <section class="study-section"><h2>단계별 힌트</h2><p>먼저 시도한 내용과 막힌 위치를 적고 필요한 힌트만 여세요.</p>${c.hints.map((hint,i)=>`<details class="challenge-hint"><summary>힌트 ${i+1}</summary><p>${esc(hint)}</p></details>`).join('')}<details class="challenge-solution"><summary>시도 후 풀이 확인</summary><p>${esc(c.solution)}</p><p>풀이를 읽었다면 새 입력으로 재현한 뒤 관련 차시에 독립 수행 여부를 기록하세요.</p></details></section>${disclosure}`,script('wargames.js')+script('wargame.js'));

  emit('learn/review.html','내 학습과 복습',`<header class="study-hero"><div class="overline">RECALL → RETRY → EXPLAIN</div><h1>지금 다시 풀어 볼 것.</h1><p>차시에서 기록한 수행 수준을 바탕으로 복습할 대상을 보여 줍니다. 완료 표시와 독립 해결 기록은 서로 다릅니다.</p></header><section class="study-section"><h2>내 복습 목록</h2><p>재도전 필요는 다음 날, 독립 해결은 3일 뒤, 읽음·따라 함은 2일 뒤에 다시 확인합니다. 복습했다면 7일 뒤로 미룰 수 있습니다.</p><p id="reviewStatus" role="status"></p><div id="reviewItems"></div><noscript><p>이 브라우저의 기록을 읽으려면 JavaScript가 필요합니다.</p></noscript><a href="./">학습 경로 선택하기 ↗</a></section><section class="study-section"><h2>기록 백업</h2><button id="downloadLearning" class="learning-button js-only" hidden type="button">진도·수행 수준 백업 받기</button><p id="learningBackupFeedback" role="status"></p><p>가져오기는 강의 하단의 ‘학습 기록 · 백업과 가져오기’에서 할 수 있습니다.</p><a href="../wargame/">워게임 해결 기록 보기 ↗</a></section>`,script('catalog.js')+script('progress.js')+script('review.js'));

  emit('guides/troubleshooting.html','막혔을 때 확인 순서',`<header class="study-hero"><div class="overline">FIND THE BLOCKER</div><h1>막힌 지점부터 구분하세요.</h1><p>재설치하기 전에 오류 메시지와 실행한 위치를 기록합니다.</p></header>${[
    ['명령을 찾을 수 없음','command not found, python3 또는 gcc를 인식할 수 없음','자신의 OS와 셸을 확인하고 버전 명령부터 실행하세요. Windows Python은 py -3 --version, Linux/macOS는 python3 --version입니다. 설치 후 터미널을 다시 열고 필요한 도구만 설치합니다.'],
    ['입력 파일을 찾을 수 없음',"No such file, can’t open file",'현재 폴더의 파일 목록을 봅니다. PowerShell: Get-Location / Get-ChildItem. Linux/macOS: pwd / ls. ZIP 안에서 직접 실행하지 말고 압축을 푼 작업 사본으로 이동합니다.'],
    ['문법·들여쓰기 오류','SyntaxError, IndentationError, 컴파일 오류','오류 줄과 바로 앞 줄의 괄호·따옴표·들여쓰기를 확인합니다. 셸 명령을 Python에 넣거나 C 조각을 터미널에 넣지 않았는지 코드 상자의 실행 문맥을 확인합니다.'],
    ['실행은 되지만 결과가 다름','출력이 예전과 같음, 행 수가 다름','파일을 저장했는지, 같은 경로를 편집·실행했는지 확인합니다. C는 다시 컴파일합니다. 원본 결과를 먼저 확인한 후 입력 하나만 바꾸고 예상·실제를 나란히 기록합니다.'],
    ['동작은 재현했지만 이유를 설명하지 못함','해설을 보면 알겠지만 혼자 시작하지 못함','한 번에 한 조건만 예측합니다. 차시의 준비 진단과 선행 차시로 돌아가고, 빈 파일에서 작은 예제를 만든 뒤 독립 과제를 다시 풉니다. 수행 수준은 따라 함 또는 재도전 필요로 기록합니다.'],
    ['워게임 서버가 시작되지 않음','Address already in use, 연결 거부','기존 로컬 실습 서버를 Ctrl+C로 종료합니다. web-notes의 주소와 포트가 127.0.0.1:8899인지 확인하고 서버가 실행 중인 터미널을 유지하세요. 다른 서비스의 포트를 스캔할 필요는 없습니다.']
  ].map(([title,symptom,check])=>`<section class="bridge-card"><h2>${esc(title)}</h2><p><strong>증상:</strong> ${esc(symptom)}</p><p><strong>다음 확인:</strong> ${esc(check)}</p></section>`).join('')}<a href="../learn/">학습으로 돌아가기 →</a>`);
  return paths;
};
