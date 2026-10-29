/* Walk every generated path using production scripts, across course boundaries. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {parseHTML} = require('linkedom');
const ROOT = path.resolve(__dirname,'..');
const read = file=>fs.readFileSync(path.join(ROOT,file),'utf8');
const routes = JSON.parse(read('content/generated-paths.json'));
let checks=0;
const check=(value,message)=>{assert.ok(value,message);checks++;};

function open(relative,store=new Map(),query='') {
  const {document,Event,CustomEvent}=parseHTML(read(relative));
  const article=document.querySelector('.lesson-article');
  const handlers=new Map();
  const window={document,matchMedia:()=>({matches:false}),
    addEventListener(type,fn){if(!handlers.has(type))handlers.set(type,[]);handlers.get(type).push(fn);},
    dispatchEvent(event){for(const fn of handlers.get(event.type)||[])fn(event);}};
  window.parent=window;
  const context=vm.createContext({document,window,Event,CustomEvent,URL,URLSearchParams,Blob,
    location:{search:query,origin:'https://example.test'},localStorage:{getItem:k=>store.get(k)??null,setItem:(k,v)=>store.set(k,v)},
    navigator:{clipboard:{writeText:async()=>{}}},setTimeout:()=>0,console});
  for(const script of document.querySelectorAll('script[src]')) {
    const file=path.resolve(ROOT,path.dirname(relative),script.getAttribute('src').split('?')[0]);
    vm.runInContext(fs.readFileSync(file,'utf8'),context,{filename:file});
  }
  return {document,window,store,article};
}

for(const route of routes) {
  const base=`paths/${route.id}/`;
  const overview=parseHTML(read(base+'index.html')).document;
  check(overview.querySelector('h1').textContent===route.title,'Path has its own overview');
  check(overview.querySelectorAll('.path-outline a').length===route.sequence.length,'Full route outline is available without JS');
  check(overview.querySelectorAll('.path-stage[open]').length===1,'Only the first stage is expanded on arrival');
  const fresh=open(base+'index.html');
  check(fresh.document.getElementById('continuePath').getAttribute('href')===route.sequence[0]+'.html','Start button enters route, not course');
  for(const [index,id] of route.sequence.entries()) {
    const relative=base+id+'.html';
    const raw=parseHTML(read(relative)).document;
    const previous=index?route.sequence[index-1]+'.html':'./';
    const next=index+1<route.sequence.length?route.sequence[index+1]+'.html':'project.html';
    const links=[...raw.querySelectorAll('.lesson-pagination a')];
    check(links[0].getAttribute('href')===previous,`${route.id}/${id}: previous is in route order`);
    check(links[1].getAttribute('href')===next,`${route.id}/${id}: next is in route order`);
    check(raw.querySelectorAll('.path-sidebar a[aria-current="page"]').length===1,'Single current route step');
    check(raw.querySelector('.path-sidebar a[aria-current="page"]').closest('details').hasAttribute('open'),'Current group expanded');
    check(raw.querySelectorAll('.path-sidebar details[open]').length===1,'Unrelated sidebar groups collapsed');
    check(raw.querySelector('.path-location').textContent.includes(`${index+1} / ${route.sequence.length}`),'Path position is visible');
    check(raw.querySelector('link[rel="canonical"]').getAttribute('href').endsWith(relative),'Share URL preserves route');
    check(raw.querySelector('.lesson-heading h1') && raw.querySelector('#exampleCode'),'Lesson readable without JS');
    const page=open(relative);
    check(page.document.querySelector('.lesson-article')===page.article,'No article replacement on hydration');
    check(page.document.querySelector('.lesson-pagination a:last-child').getAttribute('href')===next,'Hydration preserves next step');
    check(page.document.title.includes(route.title),'Runtime title retains route');
    page.document.getElementById('completeLesson').click();
    check(page.window.BifrostProgress.has(id),'Completion uses existing permanent lesson ID');
    check(page.document.querySelector('[data-path-count]').textContent.includes(`1 / ${route.sequence.length}`),'Progress counts this route');
    check(page.document.querySelector('[data-path-meter]').getAttribute('aria-valuenow')===String(Math.round(100/route.sequence.length)),'Route progress accessible value');
    const reloaded=open(relative,page.store,'?path=not-real&id=web.sql');
    check(reloaded.window.BifrostProgress.has(id),'Refresh preserves existing lesson progress');
    check(reloaded.document.body.dataset.path===route.id,'Query cannot switch a static path');
    check(reloaded.document.querySelector('.lesson-pagination a:last-child').getAttribute('href')===next,'Refresh and unrelated query retain route');
  }
  const project=open(base+'project.html');
  check(project.document.body.dataset.path===route.id,'Final project retains path');
  for(const link of project.document.querySelectorAll('#ready > ul > li > a')) {
    check(route.sequence.some(id=>link.getAttribute('href')===id+'.html'),'Project prerequisites return into route');
  }
  const complete=open(base+'index.html');
  route.sequence.forEach(id=>complete.window.BifrostProgress.set(id,true));
  check(complete.document.getElementById('continuePath').getAttribute('href')==='project.html','Completed route continues to its own project');
  const reentry=open(base+'index.html',complete.store);
  check(reentry.document.getElementById('continuePath').getAttribute('href')==='project.html','Completed route persists on reentry');
}

// Opening a course directly must not inherit a path from a prior tab or URL query.
const normal=open('tracks/web/authorization.html',new Map(),'?path=dfir');
check(!normal.document.querySelector('.path-sidebar'),'Direct course stays a course');
check(normal.document.querySelector('.lesson-pagination a:last-child').getAttribute('href')==='sql-injection.html','Normal course order preserved');
const library=parseHTML(read('learn/index.html')).document;
for(const route of routes)check(library.querySelector(`#path-${route.id} > a`).getAttribute('href')===`../paths/${route.id}/`,'Path card opens dedicated route');
check(!library.getElementById('catalogResults').hasAttribute('open'),'Full catalog collapsed by default');
check(!library.querySelector('#projects details').hasAttribute('open'),'Project collection collapsed by default');
const home=parseHTML(read('index.html')).document;
check(home.querySelector('.mindmap-stage') && !home.querySelector('.map-explorer'),'Original field map remains visible');
check(!home.querySelector('link[href*="editorial.css"]'),'Cancelled redesign is not loaded');
console.log(`PASS: ${checks} path navigation, reload, shared progress and information density checks.`);
