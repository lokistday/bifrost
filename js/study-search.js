/* Progressive enhancement: all catalog links and paths remain usable without JS. */
(() => {
  'use strict';
  const form = document.getElementById('lessonSearch');
  if (!form) return;
  const query = document.getElementById('searchQuery');
  const course = document.getElementById('searchCourse');
  const level = document.getElementById('searchLevel');
  const results = [...document.querySelectorAll('[data-search-item]')];
  const status = document.getElementById('searchStatus');
  const empty = document.getElementById('searchEmpty');
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase().replace(/\s+/g, ' ').trim();
  function filter() {
    const words = normalize(query.value.slice(0, 120)).split(' ').filter(Boolean);
    let count = 0;
    for (const row of results) {
      const visible = (!course.value || row.dataset.course === course.value)
        && (!level.value || row.dataset.level === level.value)
        && words.every(word => normalize(row.dataset.searchItem).includes(word));
      row.hidden = !visible;
      if (visible) count++;
    }
    status.textContent = `${count}개 차시 · 제목·목표·핵심어를 검색합니다.`;
    empty.hidden = count !== 0;
    const catalog = document.getElementById('catalogResults');
    if (catalog) {
      catalog.open = Boolean(words.length || course.value || level.value);
      catalog.querySelector('summary span').textContent = `${count}개 차시`;
    }
  }
  query.value = (new URLSearchParams(location.search).get('q') || '').slice(0, 120);
  form.hidden = false;
  form.addEventListener('submit', event => { event.preventDefault(); filter(); });
  query.addEventListener('input', filter);
  course.addEventListener('change', filter);
  level.addEventListener('change', filter);
  document.getElementById('searchReset').addEventListener('click', () => {
    query.value = ''; course.value = ''; level.value = ''; filter(); query.focus();
  });
  filter();
})();
