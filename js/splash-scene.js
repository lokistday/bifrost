/* Local procedural light: no movie footage, image downloads, or rendering library. */
(() => {
  const root = document.documentElement;
  let dispose = null;
  let attempted = false;
  const observer = new MutationObserver(sync);
  observer.observe(root, { attributes: true, attributeFilter: ['class'] });
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('pagehide', stop, { once: true });
  sync();

  function stop() {
    dispose?.();
    dispose = null;
    observer.disconnect();
    document.removeEventListener('visibilitychange', sync);
  }

  function sync() {
    if (document.hidden || !root.classList.contains('splash-active')) {
      if (attempted) stop();
      return;
    }
    if (attempted || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const canvas = document.getElementById('bifrostEnergy');
    if (!canvas) return;
    attempted = true;
    dispose = paint(canvas);
  }

  function paint(canvas) {
    let gl;
    let program;
    let buffer;
    let frame;
    let ended = false;
    const shaders = [];
    const release = () => {
      if (ended) return;
      ended = true;
      if (frame !== undefined) cancelAnimationFrame(frame);
      canvas.removeEventListener('webglcontextlost', contextLost);
      window.removeEventListener('resize', resize);
      if (buffer) gl.deleteBuffer(buffer);
      if (program) gl.deleteProgram(program);
      shaders.forEach(shader => gl.deleteShader(shader));
      gl?.getExtension('WEBGL_lose_context')?.loseContext();
    };
    function contextLost(event) {
      event.preventDefault();
      canvas.dataset.renderer = 'fallback';
      canvas.style.visibility = 'hidden';
      release();
    }
    function resize() {
      const bounds = canvas.getBoundingClientRect();
      const w = Math.max(1, bounds.width);
      const h = Math.max(1, bounds.height);
      // Bound fragment work, including on Retina displays. The bloom hides upscaling.
      const scale = Math.min(window.devicePixelRatio || 1, 1.25, Math.sqrt(650000 / (w * h)));
      canvas.width = Math.round(w * scale);
      canvas.height = Math.round(h * scale);
      gl.viewport(0, 0, canvas.width, canvas.height);
    }
    try {
      gl = canvas.getContext('webgl', { alpha: false, antialias: false, depth: false, stencil: false, powerPreference: 'low-power' });
      if (!gl) throw new Error('WebGL unavailable');
      const compile = (kind, source) => {
        const shader = gl.createShader(kind);
        shaders.push(shader);
        gl.shaderSource(shader, source);
        gl.compileShader(shader);
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader));
        return shader;
      };
      const vertex = compile(gl.VERTEX_SHADER, `
        attribute vec2 position;
        void main() { gl_Position = vec4(position, 0.0, 1.0); }
      `);
      const fragment = compile(gl.FRAGMENT_SHADER, `
        precision highp float;
        uniform vec2 resolution;
        uniform float time;
        uniform float lanes[8];
        const float PI = 3.14159265;

        float hash(vec2 p) {
          return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
        }
        float noise(vec2 p) {
          vec2 i = floor(p), f = fract(p);
          f = f * f * (3.0 - 2.0 * f);
          return mix(mix(hash(i), hash(i + vec2(1., 0.)), f.x),
                     mix(hash(i + vec2(0., 1.)), hash(i + vec2(1., 1.)), f.x), f.y);
        }
        float cloud(vec2 p) {
          float n = 0.;
          float a = .55;
          for (int k = 0; k < 4; k++) {
            n += a * noise(p);
            p = mat2(1.6, 1.2, -1.2, 1.6) * p + 3.1;
            a *= .5;
          }
          return n;
        }
        vec3 prism(float phase) {
          return .55 + .45 * cos(phase + vec3(0., 2.1, 4.2));
        }
        float ring(vec2 p, float radius, float thickness) {
          return exp(-abs(length(p) - radius) / thickness);
        }
        void main() {
          vec2 uv = gl_FragCoord.xy / resolution;
          vec2 p = vec2((uv.x - .5) * resolution.x / resolution.y, 1. - uv.y);
          float t = time;
          float arrival = smoothstep(.35, 1.25, t);
          float depart = 1. - smoothstep(1.65, 2.55, t);
          float energy = smoothstep(.02, .3, t) * depart;
          float ground = .76;
          float head = mix(-.1, ground, smoothstep(.05, 1.05, t));
          float descent = 1. - smoothstep(head - .08, head + .06, p.y);
          float width = .065 + .028 * p.y;
          float warp = (cloud(vec2(p.y * 7. - t * .8, t * .6)) - .5) * .05;
          float x = p.x + warp * smoothstep(.0, .3, p.y);
          float side = abs(x) / width;
          float column = exp(-pow(side, 3.0) * 1.5) * descent;
          float turbulence = cloud(vec2(x * 30. + t * .7, p.y * 9. - t * 2.6));
          float fine = cloud(vec2(x * 140. + turbulence * 3., p.y * 25. - t * 7.));
          vec3 spectrum = prism(x / width * 2.8 + turbulence * 5. + p.y * 3. - t * .6);
          spectrum = pow(spectrum, vec3(.72));

          // Smoky depth surrounds the shaft; it is lit from within, not a flat gradient.
          float fog = cloud(vec2(p.x * 3.5 + t * .08, p.y * 4. - t * .12));
          float wisps = cloud(vec2(p.x * 7. + fog * 3., p.y * 6. + t * .1));
          float scatter = exp(-abs(x) * 3.7) * (.15 + .85 * arrival) * depart;
          vec3 color = vec3(.008, .013, .028);
          color += mix(vec3(.035, .055, .13), vec3(.16, .10, .16), wisps) * fog * scatter * 1.2;
          color += spectrum * column * (.16 + fine * .6) * energy;
          color += spectrum * exp(-side * 1.1) * .12 * energy * descent;

          // Eight irregular ribbons descend in shuffled order and wind around the core.
          for (int i = 0; i < 8; i++) {
            float f = float(i);
            float h = (t - lanes[i]) * 1.65;
            float reveal = 1. - smoothstep(h - .12, h + .02, p.y);
            float spiral = sin(p.y * (12. + f * .8) - t * (2. + f * .05) + f * 2.4);
            float branch = cos(p.y * 32. + t * 4. + f) * .008;
            float ribbonX = spiral * width * (.45 + f * .055) + branch;
            float thread = exp(-abs(x - ribbonX) / (.0015 + .003 * fine));
            vec3 hue = prism(f * .77 + .35 * p.y);
            color += hue * thread * reveal * (1.2 + fine) * energy;
            color += hue * exp(-abs(x - ribbonX) / .016) * reveal * .12 * energy;
          }

          // A hot, turbulent white center and narrow lightning-like fractures.
          float core = exp(-abs(x + (fine - .5) * .012) / .008);
          color += vec3(1., .96, .83) * core * column * arrival * 1.8 * depart;
          float fracture = abs(x + sin(p.y * 57. + turbulence * 9. - t * 4.) * width * .65);
          color += vec3(.65, .84, 1.) * exp(-fracture / .0016) * column * fine * .8 * energy;

          // The arrival seal sits in perspective on the ground: gold, radial, engraved.
          vec2 seal = vec2(p.x, (p.y - ground) * 4.0);
          float radius = length(seal);
          float angle = atan(seal.y, seal.x);
          float sealOn = smoothstep(.75, 1.25, t) * depart;
          float pattern = ring(seal, .27, .0025) + ring(seal, .30, .0014) * .7;
          pattern += ring(seal, .223, .0013) * .65;
          float etching = pow(max(0., cos(angle * 32.)), 18.);
          pattern += etching * smoothstep(.224, .23, radius) * (1. - smoothstep(.262, .267, radius)) * .7;
          float rays = pow(max(0., cos(angle * 8.)), 70.);
          pattern += rays * smoothstep(.10, .12, radius) * (1. - smoothstep(.22, .225, radius)) * .6;
          color += vec3(1., .57, .20) * pattern * sealOn;
          color += vec3(.85, .40, .12) * exp(-radius * 8.) * .4 * sealOn;
          float impact = exp(-length(vec2(p.x * 1.3, (p.y - ground) * 10.)) * 16.);
          color += vec3(1., .85, .58) * impact * arrival * 1.7 * depart;

          // Restrained lens bloom and grit; no rapid full-screen flash.
          color += vec3(.45, .56, .8) * exp(-abs(p.x) * 7.) * exp(-p.y * 7.) * .25 * energy;
          color += vec3(.45, .55, .85) * exp(-abs(p.y - ground) * 260.) * exp(-abs(p.x) * 2.5) * .12 * sealOn;
          float grain = hash(gl_FragCoord.xy + floor(t * 24.)) - .5;
          color += grain * .013;
          color *= 1. - smoothstep(.35, 1.2, length(vec2(p.x * .65, p.y - .45))) * .55;
          color = 1. - exp(-color * 1.45);
          gl_FragColor = vec4(pow(max(color, 0.), vec3(.88)), 1.);
        }
      `);
      program = gl.createProgram();
      gl.attachShader(program, vertex);
      gl.attachShader(program, fragment);
      gl.linkProgram(program);
      if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
      gl.useProgram(program);
      buffer = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);
      const position = gl.getAttribLocation(program, 'position');
      gl.enableVertexAttribArray(position);
      gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
      const size = gl.getUniformLocation(program, 'resolution');
      const time = gl.getUniformLocation(program, 'time');
      const style = getComputedStyle(root);
      gl.uniform1fv(gl.getUniformLocation(program, 'lanes[0]'), new Float32Array(Array.from({ length: 8 }, (_, i) =>
        (parseFloat(style.getPropertyValue(`--splash-lane-${i}-delay`)) || 0) / 1000)));
      resize();
      canvas.addEventListener('webglcontextlost', contextLost);
      window.addEventListener('resize', resize);
      canvas.dataset.renderer = 'webgl';
      const startedAt = performance.now();
      function draw(now) {
        if (ended) return;
        if (!canvas.isConnected || !root.classList.contains('splash-active') || document.hidden) { release(); return; }
        const elapsed = (now - startedAt) / 1000;
        if (elapsed > 3.2) { release(); return; }
        gl.uniform2f(size, canvas.width, canvas.height);
        gl.uniform1f(time, elapsed);
        gl.drawArrays(gl.TRIANGLES, 0, 6);
        frame = requestAnimationFrame(draw);
      }
      frame = requestAnimationFrame(draw);
      return release;
    } catch (error) {
      canvas.dataset.renderer = 'fallback';
      canvas.style.visibility = 'hidden';
      release();
      // Rendering is optional. The ordinary splash dismissal remains independent.
      console.warn('Bifrost light scene uses its CSS fallback:', error.message);
      return null;
    }
  }
})();
