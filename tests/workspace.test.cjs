/* Entry routes, no-JS navigation, legacy links and preserved browser progress. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {parseHTML}=require('linkedom');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const entry=parseHTML(read('index.html')).document;
const fields=parseHTML(read('fields/index.html')).document;
assert.equal(entry.querySelectorAll('.entry-choice').length,2);
assert.match(read('css/workspace.css'),/html:not\(\.splash-active\) \.entry-choice \{ animation:entry-choice-arrive/);
assert.match(read('css/workspace.css'),/\.entry-choice::after \{ animation:entry-choice-trail/);
assert.match(read('css/workspace.css'),/\.entry-choice,\.entry-choice::after \{ animation:none!important; \}/);
assert.equal(entry.querySelector('#startFoundation').getAttribute('href'),'tracks/foundation/');
assert.equal(entry.querySelector('#chooseFields').getAttribute('href'),'fields/');
assert.equal(entry.querySelector('#entry-title').tagName,'H1');
assert.equal(entry.querySelector('.brand-wireframe,.hero-terrain'),null);
assert.equal(entry.querySelector('script[src*="wordmark-motion.js"]'),null);
assert.equal(entry.querySelector('.subject-directory,.workspace-rail,.workspace-preview,.workspace-actions'),null);
assert.equal(fields.querySelector('.workspace-rail,.workspace-preview,.workspace-actions,#homeProgressCount'),null);
assert.ok(fields.querySelector('.brand-wireframe,.hero-terrain'));
assert.ok(fields.querySelector('.fields-hero>.hero-terrain'));
assert.equal(fields.querySelector('.fields-hero>.hero-terrain').getAttribute('preserveAspectRatio'),'xMidYMid slice');
assert.equal(fields.querySelector('.guided-brand>.hero-terrain'),null);
assert.ok(fields.querySelector('script[src*="wordmark-motion.js"]'));
assert.equal(fields.querySelector('.fields-scroll-cue').getAttribute('href'),'#mindmap');
assert.match(fields.querySelector('.fields-scroll-cue').textContent,/9개 분야 보기/);
assert.equal(fields.querySelector('.entry-back').getAttribute('href'),'../');
const courses=JSON.parse(read('content/site.json')).courses;
assert.equal(fields.querySelectorAll('[data-map-track]').length,courses.length);
assert.equal(fields.querySelectorAll('.subject-card>.subject-arrow').length,courses.length);
for(const course of courses){
  const link=fields.querySelector(`[data-map-track="${course.id}"]`);
  assert.equal(link.getAttribute('href'),`../tracks/${course.id}/`);
  assert.ok(fs.existsSync(path.join(root,'tracks',course.id,'index.html')));
}
for(const [name,doc] of [['index.html',entry],['fields/index.html',fields]]){
  assert.equal(doc.querySelector('script[src*="catalog.js"],script[src*="progress.js"],script[src*="learning-paths.js"]'),null);
  assert.equal(doc.querySelector('[role="search"],#workspaceSearch,.hero-search-link'),null);
  assert.match(doc.querySelector('link[href*="workspace.css"]').getAttribute('href'),/\?v=home-[a-f0-9]{12}$/);
  for(const link of doc.querySelectorAll('a[href]')){
    const href=link.getAttribute('href');
    if(href.startsWith('#')||/^https?:/.test(href))continue;
    const url=new URL(href,'https://example.test/bifrost/'+name);
    assert.ok(url.pathname.startsWith('/bifrost/'));
    let relative=decodeURIComponent(url.pathname.slice('/bifrost/'.length));
    if(relative.endsWith('/'))relative+='index.html';
    assert.ok(fs.existsSync(path.join(root,relative)),href);
  }
}
function visit(hash,filename=''){
  let destination=null;
  vm.runInNewContext(read('js/workspace.js'),{
    URL,location:{hash,href:'https://example.test/bifrost/'+filename+hash,replace:url=>destination=url},
    localStorage:{getItem(){throw Error('Entry must not read progress');},setItem(){throw Error('Entry must not write progress');}}
  });
  return destination;
}
assert.equal(visit(''),null);
assert.equal(visit('#home'),null);
assert.equal(visit('#mindmap'),'https://example.test/bifrost/fields/');
assert.equal(visit('#fields','index.html'),'https://example.test/bifrost/fields/');
assert.ok(read('scripts/package_site.py').includes("'fields'"));
console.log('PASS: two direct entry choices, nine-field page, back link, no-JS subdirectory links, legacy bookmarks, untouched progress and scoped assets.');
