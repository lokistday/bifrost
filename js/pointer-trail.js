/* Short-lived decorative wire trails. No pointer data is persisted or sent. */
(() => {
  'use strict';
  if(typeof window.matchMedia!=='function')return;
  const fine=window.matchMedia('(hover: hover) and (pointer: fine)');
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  const ns='http://www.w3.org/2000/svg',life=440,limit=36;
  let svg=null,paths=[],points=[],frame=null,enabled=false;
  function clear(){
    if(frame!==null){cancelAnimationFrame(frame);frame=null;}
    points=[];
    if(svg){svg.setAttribute('hidden','');paths.forEach(p=>p.setAttribute('d',''));}
  }
  function resize(){if(svg)svg.setAttribute('viewBox',`0 0 ${window.innerWidth} ${window.innerHeight}`);clear();}
  function paint(now){
    frame=null;points=points.filter(p=>now-p.t<life);
    let count=0;
    for(let i=1;i<points.length;i++){
      const a=points[i-1],b=points[i],dx=b.x-a.x,dy=b.y-a.y,length=Math.hypot(dx,dy);
      if(length<1)continue;
      const opacity=Math.pow(Math.max(0,1-(now-a.t)/life),2)*.38;
      const path=paths[count++];
      let d=`M${a.x},${a.y}L${b.x},${b.y}`;
      if(i%3===0){
        const width=2.5+Math.min(length*.08,2.5),x=(a.x+b.x)/2-dy/length*width,y=(a.y+b.y)/2+dx/length*width;
        d+=`L${x.toFixed(1)},${y.toFixed(1)}Z`;
      }
      path.setAttribute('d',d);path.setAttribute('opacity',String(opacity));
    }
    for(let i=count;i<paths.length;i++)paths[i].setAttribute('d','');
    if(count===0)svg.setAttribute('hidden','');else svg.removeAttribute('hidden');
    if(points.length)frame=requestAnimationFrame(paint);
  }
  function setup(){
    enabled=fine.matches&&!reduced.matches;
    clear();
    if(!enabled){if(svg){svg.remove();svg=null;paths=[];}return;}
    if(svg)return;
    svg=document.createElementNS(ns,'svg');svg.classList.add('pointer-trail');
    svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');svg.setAttribute('hidden','');
    for(let i=0;i<limit;i++){const path=document.createElementNS(ns,'path');svg.append(path);paths.push(path);}
    document.body.append(svg);resize();
  }
  document.addEventListener('pointermove',event=>{
    if(!enabled||document.hidden||event.pointerType!=='mouse')return;
    const now=performance.now(),previous=points.at(-1);
    if(previous&&Math.hypot(event.clientX-previous.x,event.clientY-previous.y)<3)return;
    points.push({x:event.clientX,y:event.clientY,t:now});
    if(points.length>limit)points.shift();
    if(frame===null)frame=requestAnimationFrame(paint);
  },{passive:true});
  document.addEventListener('pointerleave',clear);
  document.addEventListener('visibilitychange',clear);
  window.addEventListener('blur',clear);window.addEventListener('resize',resize);window.addEventListener('scroll',clear,{passive:true});
  fine.addEventListener?.('change',setup);reduced.addEventListener?.('change',setup);setup();
})();
