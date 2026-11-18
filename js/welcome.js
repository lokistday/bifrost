/* Entrance navigation, distant stars and nearby stars around the nebula. */
(() => {
  'use strict';
  const root = document.documentElement;
  if (location.hash === '#home') root.classList.add('welcome-entered');

  function setup() {
    const scene = document.getElementById('welcome');
    if (!scene) return;
    const start = document.getElementById('welcomeStart');
    const flight=window.BifrostRavenFlight;
    const canvas = document.getElementById('welcomeNebula');
    const particles = document.getElementById('welcomeParticles');
    const context = particles.getContext('2d');
    let traveler = null;
    try { traveler = window.createBifrostTraveler?.(document.getElementById('welcomeTraveler')); }
    catch (error) { console.warn('Traveler could not be initialized.',error); }
    const motion = matchMedia('(prefers-reduced-motion: reduce)');
    const pointer = { x:0, y:0, targetX:0, targetY:0 };
    let renderer = null;
    let rendererAttempted = false;
    let entering = false;
    let departure = null;
    let frame = null;
    let lastFrame = 0;
    let time = 0;
    let width = 1;
    let height = 1;
    let seed = 1937;
    let ownsAnimation = true;
    const motionChannel = typeof BroadcastChannel === 'function' ? new BroadcastChannel('bifrost-welcome-motion') : null;
    const pageId = Math.random().toString(36).slice(2);
    function claimAnimation() {
      if (document.hidden || root.classList.contains('welcome-entered')) return;
      ownsAnimation = true;
      motionChannel?.postMessage({ type:'claim', id:pageId });
      sync();
    }
    if (motionChannel) motionChannel.onmessage = event => {
      if (event.data?.type === 'claim' && event.data.id !== pageId) {
        ownsAnimation = false;
        sync();
      }
    };
    function random() {
      seed = (seed * 1664525 + 1013904223) >>> 0;
      return seed / 4294967296;
    }
    const starColors = ['#e4e8ff', '#b9d5ff', '#ffe0b5'];
    const distantStars = Array.from({ length:320 }, (_, index) => ({
      x:random(), y:random(),
      size:.35 + Math.pow(random(), 3) * .85,
      light:.18 + random() * .38,
      phase:random() * Math.PI * 2,
      color:starColors[Math.floor(random() * starColors.length)],
      bright:index % 107 === 0
    }));
    const stars = Array.from({ length:1160 }, (_, index) => ({
      along:(random() - .5) * 26,
      across:(random() + random() + random() - 1.5) * 2.8,
      z:random() * 25,
      size:.4 + random() * .8,
      phase:random() * Math.PI * 2,
      color:starColors[Math.floor(random() * starColors.length)],
      bright:index % 37 === 0
    }));
    const flightStars=Array.from({length:880},()=>({
      angle:random()*Math.PI*2,distance:random()*120,
      radius:1.5+Math.pow(random(),.7)*30,width:.6+random()*1.5,
      color:random()>.55?'159,221,255':'208,174,245'
    }));
    function revealChoices(animate = false) {
      root.classList.remove('welcome-opening');
      root.classList.add('welcome-entered');
      root.classList.toggle('welcome-flight-complete', animate);
      scene.setAttribute('aria-hidden', 'true');
      entering = false;
      departure=null;
      scene.removeAttribute('data-flight-phase');
      scene.removeAttribute('data-flight-progress');
      root.style.removeProperty('--entry-shade');
      root.style.removeProperty('--flight-nebula-opacity');
      sync();
    }
    function finishEntry(){
      history.pushState(null,'','#home');
      revealChoices(departure !== null);
      window.scrollTo(0,0);
      document.getElementById('home').focus({preventScroll:true});
    }
    function followHash() {
      if (location.hash === '#home') {
        revealChoices();
      } else if (!location.hash || location.hash === '#welcome') {
        root.classList.remove('welcome-entered', 'welcome-opening', 'welcome-flight-complete');
        scene.removeAttribute('aria-hidden');
        entering = false;
        departure=null;
        start.removeAttribute('aria-disabled');
        start.removeAttribute('tabindex');
        scene.removeAttribute('data-flight-phase');
        scene.removeAttribute('data-flight-progress');
        root.style.removeProperty('--entry-shade');
        root.style.removeProperty('--flight-nebula-opacity');
        resize();
        claimAnimation();
      }
    }
    start.addEventListener('click', event => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey ||
          event.shiftKey || event.altKey) return;
      event.preventDefault();
      if (entering) return;
      entering = true;
      start.setAttribute('aria-disabled','true');
      start.setAttribute('tabindex','-1');
      start.blur?.();
      if (motion.matches || !flight) finishEntry();
      else {
        departure={start:time};
        pointer.targetX=0;pointer.targetY=0;
        root.classList.add('welcome-opening');
        claimAnimation();
        draw();
      }
    });
    scene.addEventListener('pointermove', event => {
      pointer.targetX = event.clientX / width - .5;
      pointer.targetY = event.clientY / height - .5;
    });
    scene.addEventListener('pointerleave', () => { pointer.targetX = 0; pointer.targetY = 0; });
    scene.addEventListener('pointerenter', claimAnimation);
    window.addEventListener('focus', claimAnimation);
    function resize() {
      if (root.classList.contains('welcome-entered')) return;
      width = scene.clientWidth;
      height = scene.clientHeight;
      if (!width || !height) return;
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      particles.width = Math.round(width * ratio);
      particles.height = Math.round(height * ratio);
      context?.setTransform(ratio, 0, 0, ratio, 0, 0);
      if (!rendererAttempted) createRenderer();
      renderer?.resize(width, height);
      traveler?.resize();
      draw();
    }
    function draw() {
      const progress=departure?Math.min(1,(time-departure.start)/flight.duration):0;
      const view=departure?flight.camera(progress,height):null;
      const flightBlend=view?flight.smooth(0,.15,view.glide):0;
      if(view){
        scene.dataset.flightPhase=progress<flight.releaseAt?'rise':progress<.86?'glide':'arrive';
        scene.dataset.flightProgress=progress.toFixed(4);
        root.style.setProperty('--entry-shade',String(flight.smooth(.86,1,progress)));
        root.style.setProperty('--flight-nebula-opacity',String(1-flight.smooth(.24,.8,view.glide)*.8));
      }
      renderer?.render(time, pointer.x, pointer.y,view);
      traveler?.render(time, pointer.x, pointer.y,view);
      if (!context) return;
      context.clearRect(0, 0, width, height);
      const focal = height * 1.65 / (2 * .94);
      const travel = time * .8;
      const cameraX = Math.sin(time * .035) * .5;
      const cameraY = Math.cos(time * .027) * .35;
      for (const star of distantStars) {
        const x = ((star.x * width - pointer.x * 5) % width + width) % width;
        const y = ((star.y * height - pointer.y * 4) % height + height) % height;
        const twinkle = .82 + .18 * Math.sin(time * .45 + star.phase);
        const behindCloud = 1 - .4 * Math.exp(-Math.pow((star.y - (.65 - star.x * .3)) * 4, 2));
        context.fillStyle = star.color;
        context.globalAlpha = star.light * twinkle * behindCloud*(1-flightBlend);
        const size = star.bright ? 1.8 : star.size;
        if (star.bright) {
          context.shadowColor = star.color;
          context.shadowBlur = 10;
        }
        context.fillRect(x - size / 2, y - size / 2, size, size);
        if (star.bright) {
          context.shadowBlur = 0;
          context.globalAlpha *= .35;
          context.fillRect(x - 4, y - .35, 8, .7);
          context.fillRect(x - .35, y - 4, .7, 8);
        }
      }
      for (const star of stars) {
        const z = ((star.z - travel) % 25 + 25) % 25 + .5;
        const worldZ = 7 + travel + z;
        // Place stars along the gas ribbon in world space. The matching
        // camera projection keeps them embedded as the nebula passes by.
        const worldX = Math.sin(worldZ * .095) * 2.4 + star.along * .82 - star.across * .57;
        const worldY = Math.cos(worldZ * .07) * 1.8 + star.along * .57 + star.across * .82;
        const x = width / 2 + (worldX - cameraX) / z * focal - pointer.x * height * .15 / (2 * .94);
        const y = height / 2 - (worldY - cameraY) / z * focal - pointer.y * height * .12 / (2 * .94);
        if (x < 0 || x > width || y < 0 || y > height) continue;
        const fade = Math.min(1, z / 2) * Math.min(1, (25.5 - z) / 4);
        context.fillStyle = star.color;
        context.globalAlpha = fade * (.38 + .4 * Math.pow(.5 + Math.sin(time * .6 + star.phase) * .5, 3))*(1-flightBlend);
        const size = Math.min(2.8, star.size * (.9 + 3 / z));
        if (star.bright && z < 18) {
          context.shadowColor = star.color;
          context.shadowBlur = 9;
        }
        context.fillRect(x - size / 2, y - size / 2, size, size);
        context.shadowBlur = 0;
      }
      context.globalAlpha = 1;
      if(view){
        const shutter=.009+view.glide*.016;
        flight.paintStars(context,flightStars,view,
          flight.camera(Math.max(0,progress-shutter),height),
          flight.camera(Math.max(0,progress-shutter/2),height),width,height);
      }
    }
    function tick(now) {
      frame = requestAnimationFrame(tick);
      const elapsed = lastFrame ? now - lastFrame : 0;
      if (elapsed) {
        time += Math.min(elapsed, 100) / 1000;
        renderer?.observeFrame(elapsed);
      }
      lastFrame = now;
      const blend = 1 - Math.exp(-elapsed * .00125);
      pointer.x += (pointer.targetX - pointer.x) * blend;
      pointer.y += (pointer.targetY - pointer.y) * blend;
      draw();
      if(departure && time-departure.start>=flight.duration) finishEntry();
    }
    function sync() {
      cancelAnimationFrame(frame);
      frame = null;
      lastFrame = 0;
      const active = ownsAnimation && !document.hidden && !root.classList.contains('welcome-entered');
      if (active && !motion.matches) frame = requestAnimationFrame(tick);
      else if (active) draw();
    }
    function createRenderer() {
      rendererAttempted = true;
      try { renderer = window.createBifrostNebula(canvas); }
      catch { renderer = null; canvas.classList.remove('is-ready'); }
    }
    canvas.addEventListener('webglcontextlost', event => {
      event.preventDefault();
      renderer = null;
      canvas.classList.remove('is-ready');
    });
    canvas.addEventListener('webglcontextrestored', () => { createRenderer(); resize(); });
    window.addEventListener('hashchange', followHash);
    window.addEventListener('pageshow', followHash);
    window.addEventListener('pagehide', () => {
      cancelAnimationFrame(frame);
      frame = null;
    });
    window.addEventListener('resize', resize);
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) sync();
      else claimAnimation();
    });
    motion.addEventListener('change',()=>{
      if(motion.matches&&departure)finishEntry();
      else sync();
    });
    followHash();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setup, { once:true });
  else setup();
})();
