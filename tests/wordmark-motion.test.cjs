const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {parseHTML}=require('linkedom');
const {document,Event}=parseHTML(fs.readFileSync('fields/index.html','utf8'));
let hidden=false,id=0,change;
Object.defineProperty(document,'hidden',{get:()=>hidden});
const queue=new Map(),motion={matches:false,addEventListener:(name,fn)=>change=fn};
const context={document,window:{matchMedia:()=>motion},requestAnimationFrame:fn=>{queue.set(++id,fn);return id;},cancelAnimationFrame:n=>queue.delete(n)};
vm.runInNewContext(fs.readFileSync('js/wordmark-motion.js','utf8'),context);
const svg=document.querySelector('.brand-wireframe'),front=document.querySelector('.brand-wire-front');
const original=front.getAttribute('d'),initial=svg.dataset.rotation;
function assertVisuallyCentered(){
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  for(const path of svg.querySelectorAll('.brand-wire-front,[data-wire-back]')){
    const coordinates=path.getAttribute('d').match(/-?\d+(?:\.\d+)?/g).map(Number);
    for(let i=0;i<coordinates.length;i+=2){
      minX=Math.min(minX,coordinates[i]);maxX=Math.max(maxX,coordinates[i]);
      minY=Math.min(minY,coordinates[i+1]);maxY=Math.max(maxY,coordinates[i+1]);
    }
  }
  assert.ok(Math.abs((minX+maxX)/2-Number(svg.dataset.brandWidth)/2)<.05,'The rotating outline stays horizontally centered');
  assert.ok(Math.abs((minY+maxY)/2-76)<.05,'The rotating outline stays vertically centered');
}
assertVisuallyCentered();
function step(t){const [key,fn]=queue.entries().next().value;queue.delete(key);fn(t);}
step(0);
let previous=Number(initial),travel=0,rearSeen=false;
const frontDeltas=[],rearDeltas=[];
for(let t=100;t<=24000;t+=100){
  const before=previous;step(t);const current=Number(svg.dataset.rotation);
  const delta=(current-before+360)%360;
  assert.ok(delta>0&&delta<=9,'Rotation always advances without a speed jump');travel+=delta;
  if(before<45||before>315)frontDeltas.push(delta);
  if(before>140&&before<220){rearDeltas.push(delta);assert.equal(document.querySelectorAll('.is-back-facing').length,8);rearSeen=true;}
  if(t%500===0)assertVisuallyCentered();
  previous=current;
}
assert.ok(travel>360,'The title keeps rotating through complete revolutions');
assert.ok(rearSeen,'Rear wireframe becomes visible');
assert.notEqual(front.getAttribute('d'),original,'Geometry changes as the word rotates');
const average=a=>a.reduce((sum,n)=>sum+n,0)/a.length;
assert.ok(average(rearDeltas)>average(frontDeltas)*3,'Rear rotates substantially faster than readable front');
hidden=true;document.dispatchEvent(new Event('visibilitychange'));assert.equal(queue.size,0);
hidden=false;document.dispatchEvent(new Event('visibilitychange'));assert.equal(queue.size,1);
motion.matches=true;change();assert.equal(queue.size,0,'Reduced motion is static');
assert.equal(document.querySelectorAll('.is-back-facing').length,0);
assert.equal(document.querySelector('.hero-copy>.workspace-eyebrow'),null);
console.log('PASS: continuous 360-degree geometry, fast rear/slow front, rear wireframe, hidden-tab pause and reduced motion.');
