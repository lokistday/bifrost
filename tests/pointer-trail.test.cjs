const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {parseHTML}=require('linkedom');
function load(finePointer=true,reduceMotion=false){
  const {document,Event}=parseHTML('<html><body class="workspace-page"><a id="link" href="learn/">Learn</a></body></html>');
  const queue=new Map(),listeners={},fine={matches:finePointer,addEventListener:(name,fn)=>listeners.fine=fn},reduced={matches:reduceMotion,addEventListener:(name,fn)=>listeners.reduced=fn};
  let now=0,id=0;
  const window={innerWidth:1000,innerHeight:800,matchMedia:q=>q.includes('reduced')?reduced:fine,addEventListener:(name,fn)=>listeners[name]=fn};
  vm.runInNewContext(fs.readFileSync('js/pointer-trail.js','utf8'),{document,window,performance:{now:()=>now},requestAnimationFrame:fn=>{queue.set(++id,fn);return id;},cancelAnimationFrame:id=>queue.delete(id)});
  function move(x,y,t,type='mouse'){now=t;const event=new Event('pointermove');Object.assign(event,{clientX:x,clientY:y,pointerType:type});document.dispatchEvent(event);}
  function tick(t){now=t;const [key,fn]=queue.entries().next().value;queue.delete(key);fn(t);}
  return{document,Event,queue,move,tick,listeners,fine,reduced};
}
assert.equal(load(false).document.querySelector('.pointer-trail'),null,'Touch-only devices do not allocate a trail');
assert.equal(load(true,true).document.querySelector('.pointer-trail'),null,'Reduced motion does not allocate a trail');
const p=load(),svg=p.document.querySelector('.pointer-trail');
assert.ok(svg.hasAttribute('hidden'));assert.equal(svg.getAttribute('aria-hidden'),'true');assert.equal(p.queue.size,0);
p.move(10,10,0,'touch');assert.equal(p.queue.size,0);
p.move(10,10,0);p.move(30,20,10);p.move(50,30,20);p.move(70,35,30);p.tick(35);
assert.ok(!svg.hasAttribute('hidden'));assert.ok(svg.querySelector('path[d*="Z"]'),'Short triangular wire details are drawn');
assert.equal(p.queue.size,1,'Only one animation loop is scheduled');
p.tick(600);assert.equal(p.queue.size,0,'The loop stops after the tail fades');assert.ok(svg.hasAttribute('hidden'));
for(let i=0;i<200;i++)p.move(i*6,i*2,700+i);
p.tick(900);assert.ok(svg.querySelectorAll('path[d]:not([d=""])').length<=36,'Trail work is bounded');
p.document.dispatchEvent(new p.Event('pointerleave'));assert.equal(p.queue.size,0);assert.ok(svg.hasAttribute('hidden'));
p.reduced.matches=true;p.listeners.reduced();assert.equal(p.document.querySelector('.pointer-trail'),null);
p.reduced.matches=false;p.listeners.reduced();assert.equal(p.document.querySelectorAll('.pointer-trail').length,1);
p.move(20,20,1000);p.listeners.scroll();assert.equal(p.queue.size,0,'Scroll clears stale positions');
const css=fs.readFileSync('css/pointer-trail.css','utf8');assert.match(css,/\.pointer-trail\s*\{[^}]*pointer-events:none/);
const source=fs.readFileSync('js/pointer-trail.js','utf8');assert.ok(!/fetch\(|localStorage|sessionStorage|sendBeacon/.test(source),'No pointer telemetry is stored or sent');
console.log('PASS: fine-pointer trail, bounded animation, fade-out/idle stop, touch/reduced-motion exclusion and cleanup.');
