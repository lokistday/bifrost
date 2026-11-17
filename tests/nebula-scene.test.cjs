/* Guard against rebuilding the whole gas volume on every animation frame. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
function create(nativeVolume) {
  const draws = [];
  const allocations = [];
  const attachedLayers = [];
  let framebuffer = null;
  let viewport = [];
  let layer = 0;
  const gl = new Proxy({
    createShader:()=>({}), createProgram:()=>({}), createBuffer:()=>({}),
    createTexture:()=>({}), createFramebuffer:()=>({}),
    getShaderParameter:()=>true, getProgramParameter:()=>true,
    getAttribLocation:()=>0, getUniformLocation:(_,name)=>name,
    getParameter:()=>2048, checkFramebufferStatus:()=> 'FRAMEBUFFER_COMPLETE',
    bindFramebuffer:(_,value)=>framebuffer=value,
    framebufferTextureLayer:(_,__,___,____,value)=>attachedLayers.push(value),
    uniform1f:(name,value)=>{if(name==='u_layer_offset') layer=value;},
    viewport:(...value)=>viewport=value,
    texImage2D:(...value)=>allocations.push(value),
    drawArrays:()=>draws.push({cached:!!framebuffer,viewport,layer}),
    texImage3D:nativeVolume ? (...value)=>allocations.push(value) : undefined
  }, {get:(target,key)=>key in target ? target[key] : /^[A-Z_0-9]+$/.test(key) ? key : ()=>{}});
  const canvas = {width:1,height:1,classList:{add(){}},getContext:name=>name==='webgl2'&&!nativeVolume ? null : gl};
  const window = {};
  vm.runInNewContext(fs.readFileSync('js/nebula-scene.js','utf8'),{window});
  const renderer = window.createBifrostNebula(canvas);
  return {canvas,renderer,draws,allocations,attachedLayers};
}
for (const nativeVolume of [true,false]) {
  const scene = create(nativeVolume);
  scene.renderer.resize(1600,900);
  assert.equal(scene.canvas.width,1440,'The entrance starts with a detailed background');
  assert.equal(scene.draws.length,0,'Allocating the renderer does not bake unseen gas');
  scene.renderer.render(0,0,0);
  const initialBakes = scene.draws.filter(draw=>draw.cached).length;
  assert.equal(initialBakes,nativeVolume ? 256 : 1);
  const allocations = scene.allocations.length;
  for(let frame=1;frame<=120;frame++) scene.renderer.render(frame/60,0,0);
  assert.equal(scene.draws.filter(draw=>draw.cached).length,initialBakes,'Nearby frames reuse the volume');
  assert.equal(scene.allocations.length,allocations,'Animation does not allocate new textures');
  const before = scene.draws.length;
  scene.renderer.render(150,0,0);
  const streamed = scene.draws.slice(before).filter(draw=>draw.cached);
  assert.equal(streamed.length,4,'Incoming gas is streamed with bounded work per frame');
  assert.ok(streamed.every(draw=>draw.viewport[2]<=320&&draw.viewport[3]<=192),'Streaming never rebuilds the full volume');
  for(let frame=0;frame<250;frame++) scene.renderer.render(150,0,0);
  assert.equal(scene.draws.filter(draw=>draw.cached).at(-1).layer,1232,'The rolling cache covers the camera after crossing a ring boundary');
  if(nativeVolume) assert.ok(scene.attachedLayers.every(value=>value>=0&&value<256),'Native texture layers wrap within the allocated volume');
  for(let frame=0;frame<160;frame++) scene.renderer.observeFrame(80);
  assert.equal(scene.canvas.width,1280,'Heavy GPU load keeps the background above the quality floor');
  for(let frame=0;frame<240;frame++) scene.renderer.observeFrame(16.7);
  assert.ok(scene.canvas.width>1280,'Detail recovers when GPU headroom returns');
}
console.log('PASS: native/fallback volume reuse, bounded streaming, texture limits and adaptive detail recovery.');
