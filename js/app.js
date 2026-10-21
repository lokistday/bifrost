/* Homepage catalogue: detailed teaching lives in dedicated course/lesson pages. */
(() => {
  'use strict';
  const courses = window.BifrostCourses, progress = window.BifrostProgress;
  const catalogue = document.getElementById('courseCatalog');
  if (!catalogue) return;
  const all = c => c.modules.flatMap(m => m.lessons);
  const colors = { foundation: 'cyan', web: 'blue', pwn: 'violet', rev: 'red', forensic: 'green', network: 'amber', crypto: 'pink', misc: 'orange', cloud: 'sky' };
  catalogue.innerHTML = Object.values(courses).map((c, i) => `<article class="catalog-card" style="--course-accent:var(--map-${colors[c.id]})"><div class="overline">${String(i).padStart(2, '0')} / ${c.label}</div><h3>${c.title}</h3><p>${c.subtitle}</p><small class="caption">${c.level} · ${c.modules.length}개 모듈 · ${all(c).length}개 차시</small><div class="course-stats"><span data-home-count="${c.id}"></span><div class="course-meter" role="progressbar" aria-label="${c.title} 완료 진도" aria-valuemin="0" aria-valuemax="100" data-home-meter="${c.id}"><span></span></div></div><a href="tracks/${c.id}/">목차와 강의 열기 ↗</a></article>`).join('');
  function update() {
    const lessons = Object.values(courses).flatMap(all), done = progress.count(lessons);
    document.querySelectorAll('[data-home-count]').forEach(el => {
      const ls = all(courses[el.dataset.homeCount]);
      el.textContent = `${progress.count(ls)} / ${ls.length} 완료`;
    });
    document.querySelectorAll('[data-home-meter]').forEach(el => {
      const ls = all(courses[el.dataset.homeMeter]), value = Math.round(progress.count(ls) / ls.length * 100);
      el.setAttribute('aria-valuenow', String(value));
      el.firstElementChild.style.width = `${value}%`;
    });
    const last = lessons.find(l => l.id === progress.last());
    const owner = last && Object.values(courses).find(c => all(c).includes(last));
    document.getElementById('catalogSummary').innerHTML = `<div><strong>공통 기초 + 8개 전문 분야 · ${done} / ${lessons.length}차시 완료</strong>${owner ? `최근 학습: ${owner.title} · ${last.title}` : '처음이라면 공통 기초에서 환경을 준비하세요.'}</div><a class="learning-button" href="${owner ? `tracks/${owner.id}/` : 'tracks/foundation/'}">${owner ? '최근 과정 이어가기' : '공통 기초 시작하기'} →</a>`;
    if (!progress.available()) document.getElementById('homeStorageNotice').textContent = '브라우저 저장소를 사용할 수 없습니다. 분야 페이지에서 현재 기록을 백업하세요. 저장소를 허용하지 않으면 페이지 이동 시 기록이 유지되지 않을 수 있습니다.';
  }
  window.addEventListener('bifrost-progress', update);
  update();
})();
