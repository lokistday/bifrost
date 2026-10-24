/* GPU failure must never trap a visitor or leave an animation running. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../js/splash-scene.js'), 'utf8');

function visit({ active = true, reduced = false, supported = true, compiled = true } = {}) {
  const events = new Map(), frames = new Map(), deleted = [];
  let mutation, nextFrame = 0, contexts = 0, draws = 0;
  const root = { classList: { contains: () => active } };
  const gl = {
    createShader: () => ({}), createProgram: () => ({}), createBuffer: () => ({}),
    getShaderParameter: () => compiled, getShaderInfoLog: () => 'compile failed',
    getProgramParameter: () => true, getAttribLocation: () => 0, getUniformLocation: () => ({}),
    getExtension: () => ({ loseContext: () => deleted.push('context') }),
    deleteShader: () => deleted.push('shader'), deleteProgram: () => deleted.push('program'),
    deleteBuffer: () => deleted.push('buffer'), drawArrays: () => draws++
  };
  for (const name of ['shaderSource', 'compileShader', 'attachShader', 'linkProgram', 'useProgram', 'bindBuffer',
    'bufferData', 'enableVertexAttribArray', 'vertexAttribPointer', 'uniform1fv', 'viewport', 'uniform2f', 'uniform1f']) gl[name] = () => {};
  const canvas = {
    dataset: {}, style: {}, isConnected: true,
    getContext: () => { contexts++; return supported ? gl : null; },
    getBoundingClientRect: () => ({ width: 3840, height: 2160 }),
    addEventListener: (name, fn) => events.set(name, fn), removeEventListener: name => events.delete(name)
  };
  const document = {
    documentElement: root, hidden: false, getElementById: () => canvas,
    addEventListener: (name, fn) => events.set(name, fn), removeEventListener: name => events.delete(name)
  };
  vm.runInNewContext(source, {
    document, window: {
      devicePixelRatio: 2, matchMedia: () => ({ matches: reduced }),
      addEventListener: (name, fn) => events.set(name, fn), removeEventListener: name => events.delete(name)
    },
    MutationObserver: class { constructor(fn) { mutation = fn; } observe() {} disconnect() {} },
    getComputedStyle: () => ({ getPropertyValue: () => '180ms' }),
    performance: { now: () => 0 }, console: { warn() {} },
    requestAnimationFrame: fn => { frames.set(++nextFrame, fn); return nextFrame; },
    cancelAnimationFrame: id => frames.delete(id)
  });
  return { canvas, document, events, frames, deleted, contexts: () => contexts, draws: () => draws,
    deactivate: () => { active = false; mutation(); },
    draw: now => { const [id, fn] = [...frames][0]; frames.delete(id); fn(now); } };
}

for (const options of [{ active: false }, { reduced: true }]) {
  const page = visit(options);
  assert.equal(page.contexts(), 0, 'Skipped/reduced-motion intros never allocate a GPU context');
  assert.equal(page.frames.size, 0);
}
for (const options of [{ supported: false }, { compiled: false }]) {
  const page = visit(options);
  assert.equal(page.canvas.dataset.renderer, 'fallback');
  assert.equal(page.canvas.style.visibility, 'hidden');
  assert.equal(page.frames.size, 0, 'Failure uses CSS without starting an animation loop');
}
const normal = visit();
assert.equal(normal.canvas.dataset.renderer, 'webgl');
assert.ok(normal.canvas.width * normal.canvas.height < 652000, '4K screens retain a bounded rendering budget');
normal.draw(500);
assert.equal(normal.draws(), 1);
normal.deactivate();
assert.equal(normal.frames.size, 0, 'Dismissing the intro cancels the next frame');
assert.equal(normal.deleted.filter(x => x === 'shader').length, 2);
assert.ok(normal.deleted.includes('program') && normal.deleted.includes('buffer') && normal.deleted.includes('context'));
assert.equal(normal.events.has('resize'), false);
const hidden = visit();
hidden.document.hidden = true;
hidden.events.get('visibilitychange')();
assert.equal(hidden.frames.size, 0, 'Background tabs release the renderer');
const lost = visit();
lost.events.get('webglcontextlost')({ preventDefault() {} });
assert.equal(lost.canvas.dataset.renderer, 'fallback');
assert.equal(lost.frames.size, 0, 'Context loss cannot keep a stale render loop alive');
const timeout = visit();
timeout.draw(3300);
assert.equal(timeout.frames.size, 0, 'The renderer has its own finite lifetime');
console.log('PASS: light scene skip/reduced motion, GPU failure, pixel budget, dismissal, hidden tab and context-loss cleanup.');
