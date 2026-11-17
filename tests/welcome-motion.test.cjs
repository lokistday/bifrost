/* Regressions: a 60 Hz screen was capped at 30, and sidebar tabs all stayed visible. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {parseHTML} = require('linkedom');
const channels = [];
class Channel {
  constructor() { channels.push(this); }
  postMessage(data) {
    for (const other of channels) if (other !== this) other.onmessage?.({data});
  }
}
function open() {
  const {document, Event} = parseHTML(fs.readFileSync('index.html','utf8'));
  const frames = new Map();
  const timers = new Map();
  const events = {};
  const media = {matches:false, addEventListener:(_,fn)=>events.motion=fn};
  let frameId = 0;
  let hidden = false;
  let renders = 0;
  let travelerRenders = 0;
  Object.defineProperty(document,'readyState',{value:'complete'});
  Object.defineProperty(document,'hidden',{get:()=>hidden});
  const scene = document.getElementById('welcome');
  Object.defineProperty(scene,'clientWidth',{value:1600});
  Object.defineProperty(scene,'clientHeight',{value:900});
  const paint = {setTransform(){},clearRect(){},fillRect(){},save(){},restore(){},beginPath(){},
    moveTo(){},quadraticCurveTo(){},stroke(){},createLinearGradient(){return {addColorStop(){}};}};
  document.getElementById('welcomeParticles').getContext = ()=>paint;
  document.getElementById('home').focus = ()=>{};
  const location = {hash:''};
  const window = {
    devicePixelRatio:1,
    createBifrostNebula:()=>({resize(){},render(){renders++;},observeFrame(){}}),
    createBifrostTraveler:()=>({resize(){},render(){travelerRenders++;}}),
    addEventListener:(name,fn)=>events[name]=fn,
    scrollTo(){}
  };
  vm.runInNewContext(fs.readFileSync('js/raven-flight.js','utf8'),{window});
  vm.runInNewContext(fs.readFileSync('js/welcome.js','utf8'),{
    document,window,location,matchMedia:()=>media,BroadcastChannel:Channel,
    history:{pushState:(_,__,hash)=>location.hash=hash},
    requestAnimationFrame:fn=>{frames.set(++frameId,fn);return frameId;},
    cancelAnimationFrame:id=>frames.delete(id),
    setTimeout:fn=>{timers.set(++frameId,fn);return frameId;},
    clearTimeout:id=>timers.delete(id)
  });
  return {
    document,Event,frames,events,media,timers,location,
    renders:()=>renders,
    travelerRenders:()=>travelerRenders,
    setHidden:value=>{hidden=value;document.dispatchEvent(new Event('visibilitychange'));},
    step:time=>{
      const [id,fn]=frames.entries().next().value;
      frames.delete(id);
      fn(time);
    }
  };
}
const first = open();
const before = first.renders();
for(let i=0;i<=60;i++) first.step(i*1000/60);
assert.ok(first.renders()-before>=58,'Animation follows the 60 Hz display without the former 30 fps cap');
const beforeFast = first.renders();
for(let i=1;i<=120;i++) first.step(1000+i*1000/120);
assert.equal(first.renders()-beforeFast,120,'High refresh displays do not suffer an uneven fixed-rate frame gate');
assert.equal(first.travelerRenders(),first.renders(),'The traveler shares the entrance frame loop and pauses with it');
const second = open();
assert.equal(first.frames.size,0,'A second visible sidebar preview pauses the first renderer');
assert.equal(second.frames.size,1);
first.events.focus();
assert.equal(first.frames.size,1,'Returning to a preview resumes its renderer');
assert.equal(second.frames.size,0);
first.setHidden(true);
assert.equal(first.frames.size,0);
first.setHidden(false);
assert.equal(first.frames.size,1);
first.media.matches=true;
first.events.motion();
assert.equal(first.frames.size,0,'Reduced motion does not schedule frames');
first.media.matches=false;
first.events.motion();
const click = new first.Event('click',{cancelable:true});
click.button=0;
first.document.getElementById('welcomeStart').dispatchEvent(click);
assert.equal(first.location.hash,'','Clicking the raven starts flight instead of opening the next page early');
assert.equal(first.document.getElementById('welcomeStart').getAttribute('aria-disabled'),'true');
first.step(4000);
first.step(4100);
const pausedProgress=first.document.getElementById('welcome').dataset.flightProgress;
assert.ok(+pausedProgress>0&&+pausedProgress<1);
const duplicate=new first.Event('click',{cancelable:true});duplicate.button=0;
first.document.getElementById('welcomeStart').dispatchEvent(duplicate);
assert.equal(first.document.getElementById('welcome').dataset.flightProgress,pausedProgress,'Repeated activation does not restart flight');
first.setHidden(true);
assert.equal(first.frames.size,0,'A hidden flight pauses');
first.setHidden(false);
first.step(304100);
assert.equal(first.document.getElementById('welcome').dataset.flightProgress,pausedProgress,'Returning after a long pause does not skip the dive');
for(let i=1;i<=280&&first.frames.size;i++)first.step(304100+i*1000/60);
assert.equal(first.location.hash,'#home','The learning page opens only after the complete flight');
assert.equal(first.frames.size,0,'Starting learning stops entrance rendering');
first.location.hash='';first.events.hashchange();
assert.equal(first.document.getElementById('welcomeStart').getAttribute('aria-disabled'),null,'History return re-enables the raven');
assert.equal(first.frames.size,1);
const third=open();third.media.matches=true;third.events.motion();
const reducedClick=new third.Event('click',{cancelable:true});reducedClick.button=0;
third.document.getElementById('welcomeStart').dispatchEvent(reducedClick);
assert.equal(third.location.hash,'#home','Reduced motion bypasses flight immediately');
assert.equal(third.frames.size,0);
console.log('PASS: pacing, one active renderer, complete click flight, duplicate activation, hidden-flight pause, history return and reduced-motion entry.');
