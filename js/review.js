(() => {
  'use strict';
  const progress=window.BifrostProgress, courses=window.BifrostCourses;
  const lessons=Object.values(courses).flatMap(c=>c.modules.flatMap(m=>m.lessons));
  const labels={read:'읽음',guided:'따라 함',independent:'독립 해결',review:'재도전 필요'};
  const container=document.getElementById('reviewItems');
  function update(){
    const records=lessons.map(l=>({lesson:l,state:progress.mastery(l.id)})).filter(x=>x.state).sort((a,b)=>a.state.reviewAt-b.state.reviewAt);
    container.replaceChildren();
    const due=records.filter(x=>x.state.reviewAt<=Date.now());
    document.getElementById('reviewStatus').textContent=records.length ? `${records.length}개 수행 기록 · 지금 복습 ${due.length}개${progress.available()?'':' · 저장소를 사용할 수 없습니다. 백업이 필요합니다.'}` : '차시에서 읽음·따라 함·독립 해결·재도전 필요를 기록하면 이곳에 표시됩니다.';
    for(const {lesson,state} of records){
      const item=document.createElement('article');item.className='review-item';
      const anchor=document.createElement('a');anchor.href=`../tracks/${lesson.id.replace('.','/')}.html`;anchor.textContent=lesson.title;
      const info=document.createElement('p');info.textContent=`${labels[state.stage]} · ${new Date(state.reviewAt).toLocaleDateString('ko-KR')}${state.reviewAt<=Date.now()?' · 지금 복습':''}`;
      const button=document.createElement('button');button.type='button';button.className='learning-button small';button.textContent='다시 풀었음 · 7일 뒤 복습';button.addEventListener('click',()=>progress.reviewLater(lesson.id));
      item.append(anchor,info,button);container.append(item);
    }
  }
  document.querySelectorAll('.js-only').forEach(e=>e.hidden=false);
  document.getElementById('downloadLearning').addEventListener('click',()=>{
    const url=URL.createObjectURL(new Blob([progress.export()],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download='bifrost-progress.json';a.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
    document.getElementById('learningBackupFeedback').textContent='백업 파일을 내려받았습니다.';
  });
  window.addEventListener('bifrost-progress',update);update();
})();
