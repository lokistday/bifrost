/* Troubleshooting tools. */
const fs=require('node:fs');
const path=require('node:path');
const {esc}=require('../js/learning-view.js');
module.exports=({ROOT,courses,site,fill,write})=>{
  const template=fs.readFileSync(path.join(ROOT,'templates/study.html'),'utf8');
  const paths=[];
  function emit(route,title,content,scripts='') {
    fs.mkdirSync(path.dirname(path.join(ROOT,route)),{recursive:true});
    write(route,fill(template,{TITLE:esc(title+' · Bifrost'),DESCRIPTION:esc(title),CANONICAL:esc(site.url+route.replace(/index\.html$/,'')),SITE_URL:esc(site.url),CONTENT_VERSION:esc(site.contentVersion),CONTENT:content,SCRIPTS:scripts}));
    paths.push(route.replace(/index\.html$/,''));
  }
  emit('guides/troubleshooting.html','막혔을 때 확인 순서',`<header class="study-hero"><div class="overline">FIND THE BLOCKER</div><h1>막힌 지점부터 구분하세요.</h1><p>재설치하기 전에 오류 메시지와 실행한 위치를 기록합니다.</p></header>${[
    ['명령을 찾을 수 없음','command not found, python3 또는 gcc를 인식할 수 없음','자신의 OS와 셸을 확인하고 버전 명령부터 실행하세요. Windows Python은 py -3 --version, Linux/macOS는 python3 --version입니다. 설치 후 터미널을 다시 열고 필요한 도구만 설치합니다.'],
    ['입력 파일을 찾을 수 없음',"No such file, can’t open file",'현재 폴더의 파일 목록을 봅니다. PowerShell: Get-Location / Get-ChildItem. Linux/macOS: pwd / ls. ZIP 안에서 직접 실행하지 말고 압축을 푼 작업 사본으로 이동합니다.'],
    ['문법·들여쓰기 오류','SyntaxError, IndentationError, 컴파일 오류','오류 줄과 바로 앞 줄의 괄호·따옴표·들여쓰기를 확인합니다. 셸 명령을 Python에 넣거나 C 조각을 터미널에 넣지 않았는지 코드 상자의 실행 문맥을 확인합니다.'],
    ['실행은 되지만 결과가 다름','출력이 예전과 같음, 행 수가 다름','파일을 저장했는지, 같은 경로를 편집·실행했는지 확인합니다. C는 다시 컴파일합니다. 원본 결과를 먼저 확인한 후 입력 하나만 바꾸고 예상·실제를 나란히 기록합니다.'],
    ['동작은 재현했지만 이유를 설명하지 못함','해설을 보면 알겠지만 혼자 시작하지 못함','한 번에 한 조건만 예측합니다. 차시의 준비 진단과 선행 차시로 돌아가고, 빈 파일에서 작은 예제를 만든 뒤 독립 과제를 다시 풉니다. 수행 수준은 따라 함 또는 재도전 필요로 기록합니다.'],
  ].map(([title,symptom,check])=>`<section class="bridge-card"><h2>${esc(title)}</h2><p><strong>증상:</strong> ${esc(symptom)}</p><p><strong>다음 확인:</strong> ${esc(check)}</p></section>`).join('')}<a href="../learn/">학습으로 돌아가기 →</a>`);
  return paths;
};
