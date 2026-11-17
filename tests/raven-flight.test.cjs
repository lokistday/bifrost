/* The inherited camera must rise in place, then dive, without invalid bases
   or a projection jump when the small raven moves onto the full viewport. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const window={};
vm.runInNewContext(fs.readFileSync('js/raven-flight.js','utf8'),{window});
const flight=window.BifrostRavenFlight;
const dot=(a,b)=>a.reduce((sum,value,index)=>sum+value*b[index],0);
const initial=flight.camera(0,900);
const center=flight.project([0,0,0],initial,1600,900);
assert.ok(Math.abs(center[0]-800)<1e-9&&Math.abs(center[1]-468)<1e-9,'Fullscreen rendering preserves the idle raven centre');
const rise=flight.camera(.16,900),dive=flight.camera(.55,900);
assert.equal(rise.distance,0,'Takeoff rises in place instead of flying forward first');
assert.ok(rise.eye[1]>initial.eye[1]&&rise.forward[1]>0,'The camera follows the initial rise');
assert.ok(dive.distance>rise.distance&&dive.forward[1]<0,'The follow camera pitches into the dive');
for(let i=0;i<=100;i++){
  const view=flight.camera(i/100,900);
  for(const axis of [view.right,view.up,view.forward])assert.ok(Math.abs(Math.hypot(...axis)-1)<1e-9);
  assert.ok(Math.abs(dot(view.right,view.up))<1e-9&&Math.abs(dot(view.up,view.forward))<1e-9);
  assert.ok([view.roll,view.horizon,view.focal,...view.eye].every(Number.isFinite));
  const target=flight.path(view.distance+view.lead);target[1]+=view.rise;
  const projected=flight.project(target,view,1600,900);
  assert.ok(projected&&projected.every(Number.isFinite),'The camera keeps its path target in front');
}
assert.equal(flight.duration,4.2,'Keep the approved Yggdrasil flight duration');
assert.deepEqual(flight.camera(-1),flight.camera(0));
assert.deepEqual(flight.camera(2),flight.camera(1));
console.log('PASS: continuous fullscreen entry, rise before forward travel, diving camera, valid basis and target visibility.');
