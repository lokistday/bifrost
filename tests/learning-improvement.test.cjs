const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {parseHTML}=require('linkedom');
const ROOT=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(ROOT,f),'utf8');
function load(relative,scripts,seed={}){
  const {document,Event,CustomEvent}=parseHTML(read(relative));const map=new Map(Object.entries(seed)),handlers=new Map();
  const window={addEventListener(t,fn){const list=handlers.get(t)||[];list.push(fn);handlers.set(t,list);},dispatchEvent(e){for(const fn of handlers.get(e.type)||[])fn(e);}};
  const localStorage={getItem:k=>map.get(k)||null,setItem:(k,v)=>map.set(k,v)};
  const context=vm.createContext({document,window,Event,CustomEvent,localStorage,Date,URL,Blob,TextEncoder,Uint8Array,setTimeout});
  for(const s of scripts)vm.runInContext(read('js/'+s),context);
  return{document,window,map,Event};
}
(async()=>{
  const p=load('tracks/foundation/environment.html',['catalog.js','progress.js']);
  const progress=p.window.BifrostProgress;
  progress.set('foundation.paths',true);progress.recordStage('foundation.paths','review');
  assert.ok(progress.has('foundation.paths'));assert.equal(progress.mastery('foundation.paths').stage,'review');
  assert.ok(progress.mastery('foundation.paths').reviewAt>Date.now());
  const backup=progress.export(),state=JSON.parse(backup);
  assert.equal(state.version,2);assert.equal(state.mastery['foundation.paths'].stage,'review');
  const other=load('tracks/foundation/environment.html',['catalog.js','progress.js']);other.window.BifrostProgress.import(backup);
  assert.equal(other.window.BifrostProgress.mastery('foundation.paths').stage,'review');
  other.window.BifrostProgress.recordStage('foundation.python-flow','independent');
  assert.equal(other.window.BifrostProgress.has('foundation.python-flow'),false,'Self-reported mastery does not auto-complete a lesson');
  const old=load('tracks/foundation/environment.html',['catalog.js','progress.js'],{bifrost_progress_v2:JSON.stringify({version:2,completed:{'foundation.paths':true}})});
  assert.ok(old.window.BifrostProgress.has('foundation.paths'));assert.equal(old.window.BifrostProgress.mastery('foundation.paths'),null);
  other.window.BifrostProgress.import(JSON.stringify({version:2,completed:{},mastery:{'web.sessions':{stage:'independent',updatedAt:1,reviewAt:-1}}}));
  assert.equal(other.window.BifrostProgress.mastery('web.sessions'),null);
  const routes=JSON.parse(read('content/generated-paths.json'));
  for(const route of routes){
    assert.deepEqual(route.milestones.flatMap(x=>x.lessons),route.sequence);
    assert.ok(route.milestones.every(x=>x.lessons.length<=5 && x.outcome && x.artifact));
  }
  const plans=JSON.parse(read('content/lesson-plans.json'));
  assert.equal(Object.keys(plans).length,153);assert.notDeepEqual(plans['foundation.environment'].minutes,plans['foundation.python-flow'].minutes);
  for(const id of Object.keys(plans)){
    const doc=parseHTML(read(`tracks/${id.replace('.','/')}.html`)).document;
    assert.ok(doc.querySelector('.written-check'));assert.ok(doc.querySelector('.troubleshooting'));assert.equal(doc.querySelectorAll('[data-mastery]').length,4);
  }
  console.log('PASS: individualized learning plans, milestones, mastery migration/backup.');
})().catch(e=>{console.error(e);process.exitCode=1;});
