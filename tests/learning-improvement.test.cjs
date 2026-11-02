const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {parseHTML}=require('linkedom');
const {webcrypto}=require('node:crypto');
const ROOT=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(ROOT,f),'utf8');
function load(relative,scripts,seed={}){
  const {document,Event,CustomEvent}=parseHTML(read(relative));const map=new Map(Object.entries(seed)),handlers=new Map();
  const window={crypto:webcrypto,addEventListener(t,fn){const list=handlers.get(t)||[];list.push(fn);handlers.set(t,list);},dispatchEvent(e){for(const fn of handlers.get(e.type)||[])fn(e);}};
  const localStorage={getItem:k=>map.get(k)||null,setItem:(k,v)=>map.set(k,v)};
  const context=vm.createContext({document,window,Event,CustomEvent,localStorage,Date,URL,Blob,TextEncoder,Uint8Array,setTimeout});
  for(const s of scripts)vm.runInContext(read('js/'+s),context);
  return{document,window,map,Event};
}
async function submitted(page,flag){
  page.document.getElementById('flagInput').value=flag;
  page.document.getElementById('flagForm').dispatchEvent(new page.Event('submit',{cancelable:true}));
  for(let i=0;i<100 && page.document.querySelector('#flagForm button').disabled;i++)await new Promise(resolve=>setTimeout(resolve,5));
  return page.document.getElementById('flagFeedback').textContent;
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
  const c=load('wargame/foundation-log.html',['wargames.js','wargame.js']);
  assert.match(await submitted(c,'not-a-flag'),/형식/);assert.equal(c.map.has('bifrost_wargame_v1'),false);
  assert.match(await submitted(c,'BIFROST{wrong}'),/일치하지/);
  assert.equal(JSON.parse(c.map.get('bifrost_wargame_v1')).problems['foundation-log'].solvedAt,null);
  assert.match(await submitted(c,'BIFROST{csv_records_not_commas}'),/해결/);
  const saved=c.map.get('bifrost_wargame_v1');assert.ok(JSON.parse(saved).problems['foundation-log'].solvedAt);assert.ok(!saved.includes('BIFROST{'));
  const reload=load('wargame/index.html',['wargames.js','wargame.js'],{bifrost_wargame_v1:saved});
  assert.match(reload.document.querySelector('[data-solved-label="foundation-log"]').textContent,/해결/);
  const select=reload.document.getElementById('challengeState');Object.defineProperty(select,'value',{value:'unsolved',writable:true});select.dispatchEvent(new reload.Event('change'));
  assert.ok(reload.document.querySelector('[data-challenge-card="foundation-log"]').hidden);
  const broken=load('wargame/foundation-log.html',['wargames.js','wargame.js'],{bifrost_wargame_v1:'{broken'});
  assert.match(await submitted(broken,'BIFROST{csv_records_not_commas}'),/저장에 실패/);
  assert.equal(broken.map.get('bifrost_wargame_v1'),'{broken','Corrupt records are preserved until explicit import');
  const noCrypto=load('wargame/foundation-log.html',['wargames.js','wargame.js']);noCrypto.window.crypto={};assert.match(await submitted(noCrypto,'BIFROST{test}'),/검증할 수 없습니다/);
  console.log('PASS: individualized learning plans, milestones, mastery migration/backup and real SHA-256 flag submission/reload/filter/error flows.');
})().catch(e=>{console.error(e);process.exitCode=1;});
