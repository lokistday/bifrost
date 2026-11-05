'use strict';
let csrf='';
const result=document.getElementById('result');
async function request(path,body,token=true){
 const headers={};if(body!==undefined)headers['Content-Type']='application/json';
 if(token&&csrf)headers['X-CSRF-Token']=csrf;
 try{
  const r=await fetch(path,{method:body===undefined?'GET':'POST',headers,body:body===undefined?undefined:JSON.stringify(body)});
  const data=await r.json();result.textContent=`${r.status} ${path}\n`+JSON.stringify(data,null,2);return {r,data};
 }catch(e){result.textContent=String(e);return null;}
}
document.getElementById('login').addEventListener('submit',async e=>{e.preventDefault();const f=new FormData(e.target);csrf='';const v=await request('/api/login',{user:f.get('user'),password:f.get('password')});if(v?.r.ok){const m=await request('/api/me');csrf=m?.data.csrf||'';}});
document.getElementById('me').onclick=async()=>{const m=await request('/api/me');csrf=m?.data.csrf||'';};
document.getElementById('logout').onclick=async()=>{await request('/api/logout',{});csrf='';};
document.querySelectorAll('[data-note]').forEach(b=>b.onclick=()=>request('/api/notes/'+b.dataset.note));
document.getElementById('edit').onsubmit=e=>{e.preventDefault();const f=new FormData(e.target);request('/api/notes/'+f.get('id'),{text:f.get('text')});};
document.getElementById('no-token').onclick=()=>request('/api/notes/1',{text:'should not change'},false);
document.getElementById('extra-field').onclick=()=>request('/api/notes/1',{text:'should not change',role:'admin'});
document.getElementById('render').onclick=()=>{document.getElementById('safe-output').textContent=document.getElementById('sample').value;};
