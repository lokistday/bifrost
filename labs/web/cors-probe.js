'use strict';
const output=document.getElementById('result');
async function probe(path){try{const r=await fetch('http://127.0.0.1:8787'+path,{credentials:'omit'});output.textContent=`readable status=${r.status}\n`+await r.text();}catch(e){output.textContent='Browser did not expose the response. Inspect Network and Console.\n'+e;}}
document.getElementById('public').onclick=()=>probe('/api/public');
document.getElementById('private').onclick=()=>probe('/api/me');
