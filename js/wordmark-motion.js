/* Rotate actual letter contours and depth ties; keep the rest of the hero still. */
(() => {
  'use strict';
  const svg=document.querySelector('.brand-wireframe');
  if(!svg)return;
  const width=Number(svg.dataset.brandWidth),depth=14,frontSpeed=Math.PI*2/18000;
  const glyphs=[...svg.querySelectorAll('[data-wire-glyph]')].map(group=>({
    group,offset:Number(group.dataset.offset),contours:JSON.parse(group.dataset.contours),
    front:group.querySelector('.brand-wire-front'),back:group.querySelector('[data-wire-back]'),ties:group.querySelector('[data-wire-ties]')
  }));
  const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
  let frame=null,last=null,angle=-.3,visible=true;
  function angularSpeed(a){
    // Slow on the readable front, up to 4x faster across the reversed rear.
    const rear=Math.max(0,Math.min(1,(.2-Math.cos(a))/.8));
    const blend=rear*rear*(3-2*rear);
    return frontSpeed*(1+3*blend);
  }
  function render(angle){
    const c=Math.cos(angle),s=Math.sin(angle),pitch=-.13,cp=Math.cos(pitch),sp=Math.sin(pitch);
    function project(x,y,z){
      const rx=x*c+z*s,rz=-x*s+z*c,ry=y*cp-rz*sp,zz=y*sp+rz*cp;
      const scale=1250/(1250-zz);
      return[width/2+rx*scale,82+ry*scale];
    }
    let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
    for(const g of glyphs)for(const contour of g.contours)for(const p of contour)for(const z of [-depth/2,depth/2]){
      const [x,y]=project(g.offset+p[0]-width/2,p[1]-50,z);
      minX=Math.min(minX,x);maxX=Math.max(maxX,x);
      minY=Math.min(minY,y);maxY=Math.max(maxY,y);
    }
    const shiftX=width/2-(minX+maxX)/2,shiftY=76-(minY+maxY)/2;
    function point(g,p,z){const [x,y]=project(g.offset+p[0]-width/2,p[1]-50,z);return[(x+shiftX).toFixed(2),(y+shiftY).toFixed(2)];}
    function outline(g,z){return g.contours.map(contour=>'M'+contour.map(p=>point(g,p,z).join(',')).join('L')+'Z').join('');}
    const order=[...glyphs].sort((a,b)=>(b.offset-a.offset)*s);
    for(const g of order){
      g.group.removeAttribute('transform');g.back.removeAttribute('transform');
      g.back.setAttribute('d',outline(g,-depth/2));
      let ties='';
      for(const contour of g.contours)for(let i=0;i<contour.length;i++){
        const a=contour[i],b=contour[(i+1)%contour.length],n=Math.max(1,Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/12));
        for(let k=0;k<n;k++){
          const p=[a[0]+(b[0]-a[0])*k/n,a[1]+(b[1]-a[1])*k/n];
          ties+='M'+point(g,p,-depth/2).join(',')+'L'+point(g,p,depth/2).join(',');
        }
      }
      g.ties.setAttribute('d',ties);g.front.setAttribute('d',outline(g,depth/2));
      g.front.classList.toggle('is-back-facing',c<0);
      // Back-facing wireframe stays visible through the open rear of the letters.
      svg.append(g.group);
    }
    svg.dataset.rotation=String(Math.round(((angle*180/Math.PI)%360+360)%360));
  }
  function tick(now){
    frame=null;
    if(motion.matches||document.hidden||!visible){last=null;return;}
    if(last!==null){
      const dt=Math.max(0,Math.min(now-last,100));
      // Midpoint integration keeps the acceleration smooth across frame rates.
      angle=(angle+angularSpeed(angle+angularSpeed(angle)*dt/2)*dt)%(Math.PI*2);
    }
    last=now;render(angle);frame=requestAnimationFrame(tick);
  }
  function sync(){
    if(frame!==null){cancelAnimationFrame(frame);frame=null;}
    last=null;
    if(motion.matches){render(-.3);return;}
    if(!document.hidden&&visible)frame=requestAnimationFrame(tick);
  }
  render(-.3);motion.addEventListener('change',sync);document.addEventListener('visibilitychange',sync);
  if('IntersectionObserver' in window){
    const observer=new window.IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();},{rootMargin:'80px'});
    observer.observe(svg);
  }
  sync();
})();
