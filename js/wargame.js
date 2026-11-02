/* Browser-only educational flag verification. No submissions or flags are transmitted. */
(() => {
  'use strict';
  const catalog=window.BifrostWargames, KEY='bifrost_wargame_v1';
  let writable=true, state={version:1,problems:{}};
  function sanitize(raw){
    if(!raw||raw.version!==1||!raw.problems||typeof raw.problems!=='object'||Array.isArray(raw.problems))throw Error('Invalid backup');
    const clean={version:1,problems:{}};
    for(const id of Object.keys(catalog)){
      const x=raw.problems[id];if(!x||typeof x!=='object')continue;
      clean.problems[id]={attempts:Number.isSafeInteger(x.attempts)&&x.attempts>=0?Math.min(x.attempts,1000000):0,solvedAt:Number.isSafeInteger(x.solvedAt)&&x.solvedAt>0&&x.solvedAt<=8640000000000000?x.solvedAt:null};
    }
    return clean;
  }
  function read(){
    try{const raw=localStorage.getItem(KEY);return raw?sanitize(JSON.parse(raw)):{version:1,problems:{}};}
    catch(_){writable=false;return state;}
  }
  function persist(){
    if(writable)try{localStorage.setItem(KEY,JSON.stringify(state));}catch(_){writable=false;}
    update();
  }
  function merge(a,b){
    for(const id of Object.keys(catalog)){
      const x=a.problems[id],y=b.problems[id];if(!y)continue;
      a.problems[id]={attempts:Math.max(x?.attempts||0,y.attempts),solvedAt:x?.solvedAt&&y.solvedAt?Math.min(x.solvedAt,y.solvedAt):x?.solvedAt||y.solvedAt||null};
    }
    return a;
  }
  state=read();
  const panel=document.querySelector('[data-challenge]'), id=panel?.dataset.challenge;
  const courseFilter=document.getElementById('challengeCourse'), stateFilter=document.getElementById('challengeState');
  function update(){
    document.querySelectorAll('[data-solved-label]').forEach(e=>e.textContent=state.problems[e.dataset.solvedLabel]?.solvedAt?'✓ 해결':'미해결');
    let count=0;
    document.querySelectorAll('[data-challenge-card]').forEach(card=>{
      const solved=Boolean(state.problems[card.dataset.challengeCard]?.solvedAt);
      card.hidden=Boolean(courseFilter?.value&&card.dataset.course!==courseFilter.value || stateFilter?.value==='solved'&&!solved || stateFilter?.value==='unsolved'&&solved);
      if(!card.hidden)count++;
    });
    const summary=document.getElementById('wargameSummary');
    if(summary)summary.textContent=`${Object.values(state.problems).filter(x=>x.solvedAt).length} / ${Object.keys(catalog).length} 해결${writable?'':' · 저장 실패: 기록을 백업하세요.'}`;
    const empty=document.getElementById('challengeEmpty');if(empty)empty.hidden=count!==0;
    const attempts=document.getElementById('attemptCount');if(attempts)attempts.textContent=`검증한 제출 ${state.problems[id]?.attempts||0}회${writable?'':' · 저장할 수 없어 이번 화면에만 반영됩니다.'}`;
  }
  document.querySelectorAll('.js-only').forEach(e=>e.hidden=false);
  if(courseFilter)courseFilter.addEventListener('change',update);
  if(stateFilter)stateFilter.addEventListener('change',update);
  const form=document.getElementById('flagForm');
  if(form&&catalog[id]){
    form.hidden=false;let pending=false;
    form.addEventListener('submit',async event=>{
      event.preventDefault();if(pending)return;
      const input=document.getElementById('flagInput'),feedback=document.getElementById('flagFeedback'),flag=input.value.trim();
      if(flag.length>256||!/^BIFROST\{[!-~]+\}$/.test(flag)){feedback.textContent='BIFROST{...} 형식과 공백·중괄호를 확인하세요.';return;}
      if(!window.crypto?.subtle){feedback.textContent='현재 브라우저에서는 검증할 수 없습니다. HTTPS 사이트 또는 localhost에서 열어 주세요.';return;}
      pending=true;form.querySelector('button').disabled=true;
      try{
        const digest=await window.crypto.subtle.digest('SHA-256',new TextEncoder().encode(flag));
        const actual=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
        state=merge(read(),state);
        const entry=state.problems[id]||{attempts:0,solvedAt:null};entry.attempts=Math.min(entry.attempts+1,1000000);
        const correct=actual===catalog[id].flagHash;
        if(correct&&!entry.solvedAt)entry.solvedAt=Date.now();
        state.problems[id]=entry;persist();
        feedback.textContent=correct?'정답입니다! 문제를 해결했습니다. 풀이 근거를 남기고 새 조건에서도 설명해 보세요.':'FLAG가 일치하지 않습니다. 대상 기록·순서·대소문자를 확인하고 필요한 힌트를 열어 보세요.';
        if(!writable)feedback.textContent+=' 브라우저 저장에 실패했습니다. 기록을 백업하세요.';
        if(correct)input.value='';
      }catch(_){feedback.textContent='검증 중 오류가 발생했습니다. 기록을 백업한 뒤 다시 시도하세요.';}
      finally{pending=false;form.querySelector('button').disabled=false;}
    });
  }
  const backup=document.getElementById('exportWargame');
  if(backup)backup.addEventListener('click',()=>{
    const url=URL.createObjectURL(new Blob([JSON.stringify(state,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='bifrost-wargame.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    document.getElementById('wargameBackupFeedback').textContent='해결 기록을 내보냈습니다. FLAG 원문은 저장하지 않습니다.';
  });
  document.getElementById('importWargame')?.addEventListener('change',async event=>{
    const feedback=document.getElementById('wargameBackupFeedback');
    try{const file=event.target.files[0];if(!file)return;if(file.size>1000000)throw Error();const incoming=sanitize(JSON.parse(await file.text()));state=merge(read(),state);state=merge(state,incoming);writable=true;persist();feedback.textContent=writable?'기존 해결 기록과 합쳤습니다.':'합쳤지만 저장하지 못했습니다. 다시 백업하세요.';}
    catch(_){feedback.textContent='1MB 이하의 올바른 워게임 백업 JSON을 선택하세요.';}
    event.target.value='';
  });
  window.addEventListener('storage',event=>{if(event.key===KEY||event.key===null){state=read();update();}});
  window.addEventListener('pageshow',event=>{if(event.persisted){state=read();update();}});
  update();
})();
