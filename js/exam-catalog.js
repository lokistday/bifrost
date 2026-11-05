/* Field navigation keeps the exam library compact without hiding links from no-JS readers. */
(() => {
  'use strict';
  const nav=document.querySelector('[aria-label="모의고사 분야"]');
  if(!nav)return;
  const links=[...nav.querySelectorAll('a')];
  const sections=links.map(a=>document.getElementById(a.getAttribute('href').slice(1)));
  function select(index){
    links.forEach((a,i)=>{if(i===index)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');});
    sections.forEach((section,i)=>section.hidden=i!==index);
  }
  links.forEach((a,i)=>a.addEventListener('click',event=>{event.preventDefault();select(i);}));
  const initial=links.findIndex(a=>a.getAttribute('href')===location.hash);
  select(initial<0?0:initial);
})();
