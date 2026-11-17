/* Cache procedural gas in a rolling volume, then ray-march that volume. */
(() => {
  'use strict';
  window.createBifrostNebula = canvas => {
    const forwardSpeed = .8;
    const options = { alpha:false, antialias:false, depth:false, powerPreference:'high-performance' };
    const gl = canvas.getContext('webgl2', options) || canvas.getContext('webgl', options);
    if (!gl) return null;
    const nativeVolume = typeof gl.texImage3D === 'function';
    function compile(type, source) {
      if (nativeVolume) {
        source = '#version 300 es\n' + source
          .replace(/\battribute\b/g, 'in')
          .replace(/\bvarying\b/g, type === gl.VERTEX_SHADER ? 'out' : 'in')
          .replace(/\btexture2D\b/g, 'texture')
          .replace(/\bgl_FragColor\b/g, 'fragmentColor');
        if (type === gl.FRAGMENT_SHADER) source = source.replace('precision highp float;', 'precision highp float;\nout vec4 fragmentColor;');
      }
      const shader = gl.createShader(type);
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        const message = gl.getShaderInfoLog(shader);
        gl.deleteShader(shader);
        throw new Error(message);
      }
      return shader;
    }
    const vertex = compile(gl.VERTEX_SHADER, `
      attribute vec2 a_position;
      varying vec2 v_uv;
      void main() {
        v_uv = a_position;
        gl_Position = vec4(a_position, 0.0, 1.0);
      }
    `);
    const noiseSource = `
      uniform sampler2D u_noise;
      float noise3(vec3 p) {
        vec3 cell = floor(p);
        vec3 f = fract(p);
        f = f * f * (3.0 - 2.0 * f);
        vec2 uv = cell.xy + vec2(37.0, 17.0) * cell.z + f.xy;
        vec2 slices = texture2D(u_noise, (uv + 0.5) / 256.0).rg;
        return mix(slices.r, slices.g, f.z);
      }
    `;
    const gasSource = `
      precision highp float;
      ${noiseSource}
      const mat3 rotation = mat3(
        0.00, 0.80, 0.60,
        -0.80, 0.36, -0.48,
        -0.60, -0.48, 0.64
      );
      float turbulence(vec3 p) {
        float value = noise3(p) * 0.5;
        p = rotation * p * 2.03 + 13.7;
        value += noise3(p) * 0.25;
        p = rotation * p * 2.01 + 9.2;
        value += noise3(p) * 0.125;
        p = rotation * p * 2.02;
        value += noise3(p) * 0.0625;
        p = rotation * p * 2.03;
        value += noise3(p) * 0.03125;
        p = rotation * p * 2.01;
        return value + noise3(p) * 0.015625;
      }
      vec4 gasAt(vec3 p) {
          vec3 q = p * 0.82;
          float broad = noise3(p * 0.17 + vec3(8.0, 5.0, 0.0));
          q += vec3(broad, noise3(p * 0.19 + 17.0), broad * 0.7) * 1.3;
          float field = turbulence(q);
          // One connected, warped cloud bank with darker space around it.
          // Fine turbulence belongs inside this structure instead of filling
          // every direction with disconnected patches of fog.
          vec2 spine = p.xy - vec2(sin(p.z * 0.095) * 2.4, cos(p.z * 0.07) * 1.8);
          float across = spine.y * 0.82 - spine.x * 0.57;
          float warp = (broad - 0.5) * 3.6 + (noise3(p * 0.11 + 29.0) - 0.5) * 1.4;
          float ribbon = exp(-pow((across + warp) / 3.1, 2.0));
          float core = exp(-dot(spine * vec2(0.16, 0.2), spine * vec2(0.16, 0.2)));
          float cloud = clamp(ribbon * 0.86 + core * 0.42, 0.0, 1.0);
          vec2 corridor = p.xy - vec2(sin(p.z * 0.23) * 1.2, cos(p.z * 0.17) * 0.8);
          float opening = exp(-dot(corridor, corridor) * 0.55) * 0.055;
          float density = pow(max(field - (0.575 - cloud * 0.055) - opening, 0.0), 1.25)
            * 4.1 * cloud * smoothstep(0.2, 0.68, broad);
          if (density > 0.001) {
            float heat = noise3(p * 0.21 + vec3(13.5, 4.0, 5.0));
            vec3 violet = vec3(0.16, 0.10, 0.32);
            vec3 crimson = vec3(0.9, 0.13, 0.065);
            vec3 gasColor = mix(violet, crimson, smoothstep(0.25, 0.78, heat));
            float lightField = noise3(p * 0.34 + vec3(-7.0, 13.0, 8.0));
            float edgeLight = clamp((field - turbulence(q + vec3(0.15, 0.2, -0.12))) * 8.0 + 0.35, 0.0, 1.0);
            float illumination = 0.09 + lightField * lightField * 3.0;
            vec3 scattered = gasColor * illumination * (0.5 + edgeLight * 1.6);
            scattered += vec3(0.9, 0.65, 0.83) * pow(edgeLight, 3.0) * pow(lightField, 2.0) * 0.9;
            float dust = smoothstep(0.48, 0.7, broad) * 0.8;
            scattered *= 1.0 - dust;
            float alpha = 1.0 - exp(-density * (0.4 + dust * 0.5));
            // Premultiply before storing so interpolation preserves thin gas.
            return vec4(sqrt(clamp(scattered * alpha * 0.25, 0.0, 1.0)), alpha);
          }
          return vec4(0.0);
      }
    `;
    const bakeFragment = compile(gl.FRAGMENT_SHADER, gasSource + `
      uniform vec2 u_slice_size;
      uniform float u_layer_offset;
      uniform float u_spacing;
      void main() {
        ${nativeVolume ? `
        vec3 p = vec3((gl_FragCoord.xy / u_slice_size - 0.5) * vec2(56.0, 32.0), (u_layer_offset + 0.5) * u_spacing);
        ` : `
        vec2 tile = floor(gl_FragCoord.xy / u_slice_size);
        vec2 voxel = mod(gl_FragCoord.xy, u_slice_size);
        float slot = tile.y * 16.0 + tile.x;
        float layer = mod(slot - u_layer_offset, 256.0) + u_layer_offset;
        vec3 p = vec3((voxel / u_slice_size - 0.5) * vec2(56.0, 32.0), (layer + 0.5) * u_spacing);
        `}
        gl_FragColor = gasAt(p);
      }
    `);
    const fragment = compile(gl.FRAGMENT_SHADER, `
      precision highp float;
      ${noiseSource}
      uniform vec2 u_size;
      uniform vec2 u_pointer;
      uniform float u_time;
      uniform float u_forward_speed;
      uniform vec3 u_camera_origin;
      uniform vec3 u_camera_right;
      uniform vec3 u_camera_up;
      uniform vec3 u_camera_forward;
      uniform float u_camera_roll;
      uniform float u_camera_horizon;
      uniform float u_camera_focal;
      uniform float u_camera_active;
      uniform vec2 u_slice_size;
      uniform vec2 u_atlas_size;
      uniform float u_spacing;
      varying vec2 v_uv;
      ${nativeVolume ? `
      uniform highp sampler3D u_volume;
      vec4 volumeAt(vec3 p) {
        vec4 gas = texture(u_volume, vec3(p.xy / vec2(56.0, 32.0) + 0.5, p.z / (u_spacing * 256.0)));
        gas.rgb = gas.rgb * gas.rgb * 4.0;
        return gas;
      }
      ` : `
      uniform sampler2D u_volume;
      vec4 sliceAt(vec2 xy, float layer) {
        float slot = mod(layer, 256.0);
        vec2 tile = vec2(mod(slot, 16.0), floor(slot / 16.0));
        vec2 texel = clamp(xy * u_slice_size, vec2(0.5), u_slice_size - 0.5);
        return texture2D(u_volume, (tile * u_slice_size + texel) / u_atlas_size);
      }
      vec4 volumeAt(vec3 p) {
        vec2 xy = p.xy / vec2(56.0, 32.0) + 0.5;
        float z = p.z / u_spacing - 0.5;
        float layer = floor(z);
        vec4 a = sliceAt(xy, layer);
        vec4 b = sliceAt(xy, layer + 1.0);
        a.rgb = a.rgb * a.rgb * 4.0;
        b.rgb = b.rgb * b.rgb * 4.0;
        return mix(a, b, fract(z));
      }
      `}
      void main() {
        vec2 uv = v_uv;
        uv.x *= u_size.x / u_size.y;
        vec3 origin = vec3(sin(u_time * 0.035) * 0.5, cos(u_time * 0.027) * 0.35, 7.0 + u_time * u_forward_speed);
        vec3 direction = normalize(vec3(uv * 0.94 + u_pointer * vec2(0.15, -0.12), 1.65));
        if(u_camera_active>.5) {
          origin=u_camera_origin;
          vec2 screen=vec2(uv.x,v_uv.y-u_camera_horizon);
          float s=sin(-u_camera_roll),c=cos(-u_camera_roll);
          screen=mat2(c,s,-s,c)*screen;
          direction=normalize(u_camera_right*screen.x+u_camera_up*screen.y+u_camera_forward*u_camera_focal);
        }
        vec3 accumulated = vec3(0.0);
        vec3 weightedPosition = vec3(0.0);
        float transmission = 1.0;
        float distance = 0.4;
        float jitter = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898,78.233))) * 43758.5453);
        distance += jitter * 0.025;
        for (int step = 0; step < 40; step++) {
          vec3 samplePosition = origin + direction * distance;
          vec4 gas = volumeAt(samplePosition);
          // Match optical thickness when traversing the same distance in fewer steps.
          float alpha = 1.0 - pow(1.0 - gas.a, 1.2);
          weightedPosition += samplePosition * transmission * alpha;
          accumulated += transmission * gas.rgb * (alpha / max(gas.a, 0.0001));
          transmission *= 1.0 - alpha;
          if (transmission < 0.025) break;
          distance += 0.624;
        }
        // Resolve small filaments at the final image resolution. Keeping this
        // work outside the ray loop restores detail without repeating all gas
        // and lighting calculations at every depth sample.
        float coverage = 1.0 - transmission;
        if (coverage > 0.01) {
          vec3 detailPosition = weightedPosition / max(coverage, 0.001);
          float fold = noise3(detailPosition * 0.75 + 31.0);
          float strand = noise3(detailPosition * 3.8 + fold * 1.7);
          float fine = noise3(detailPosition * 9.0 + vec3(7.0, 19.0, 3.0));
          float ridge = 1.0 - abs(strand * 2.0 - 1.0);
          accumulated *= 0.72 + strand * 0.38 + fine * 0.22;
          accumulated += vec3(0.09, 0.045, 0.12) * pow(ridge, 6.0)
            * smoothstep(0.04, 0.5, coverage) * (1.0 - coverage) * 0.25;
        }
        vec3 color = accumulated + vec3(0.006, 0.003, 0.014) * transmission;
        color = 1.0 - exp(-color * 1.45);
        color = pow(color, vec3(1.05));
        gl_FragColor = vec4(color, 1.0);
      }
    `);
    function link(fragmentShader) {
      const result = gl.createProgram();
      gl.attachShader(result, vertex);
      gl.attachShader(result, fragmentShader);
      gl.bindAttribLocation(result, 0, 'a_position');
      gl.linkProgram(result);
      if (!gl.getProgramParameter(result, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(result));
      return result;
    }
    const program = link(fragment);
    const bakeProgram = link(bakeFragment);
    gl.deleteShader(vertex);
    gl.deleteShader(fragment);
    gl.deleteShader(bakeFragment);
    gl.useProgram(program);
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
    const position = gl.getAttribLocation(program, 'a_position');
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
    let seed = 90317;
    const samples = new Uint8Array(256 * 256);
    for (let i = 0; i < samples.length; i++) {
      seed = (seed * 1664525 + 1013904223) >>> 0;
      samples[i] = seed >>> 24;
    }
    const pixels = new Uint8Array(256 * 256 * 4);
    for (let y = 0; y < 256; y++) {
      for (let x = 0; x < 256; x++) {
        const index = (y * 256 + x) * 4;
        pixels[index] = samples[y * 256 + x];
        pixels[index + 1] = samples[((y + 17) % 256) * 256 + (x + 37) % 256];
        pixels[index + 3] = 255;
      }
    }
    const noiseTexture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, noiseTexture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.REPEAT);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 256, 256, 0, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
    // A 256-slice ring covers the camera's full ray distance. Only the next
    // incoming slice is rebuilt as the camera advances, rather than the scene.
    const largeAtlas = gl.getParameter(gl.MAX_TEXTURE_SIZE) >= 4096;
    const detailedVolume = nativeVolume && gl.getParameter(gl.MAX_3D_TEXTURE_SIZE) >= 512;
    const sliceWidth = nativeVolume ? (detailedVolume ? 320 : 256) : (largeAtlas ? 224 : 128);
    const sliceHeight = nativeVolume ? (detailedVolume ? 192 : 160) : (largeAtlas ? 128 : 80);
    const atlasWidth = sliceWidth * 16;
    const atlasHeight = sliceHeight * 16;
    const spacing = .125;
    const volumeTexture = gl.createTexture();
    const volumeTarget = nativeVolume ? gl.TEXTURE_3D : gl.TEXTURE_2D;
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(volumeTarget, volumeTexture);
    gl.texParameteri(volumeTarget, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(volumeTarget, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(volumeTarget, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(volumeTarget, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    if (nativeVolume) {
      gl.texParameteri(volumeTarget, gl.TEXTURE_WRAP_R, gl.REPEAT);
      gl.texImage3D(volumeTarget, 0, gl.RGBA8, sliceWidth, sliceHeight, 256, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
    } else gl.texImage2D(volumeTarget, 0, gl.RGBA, atlasWidth, atlasHeight, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
    const framebuffer = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, framebuffer);
    if (nativeVolume) gl.framebufferTextureLayer(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, volumeTexture, 0, 0);
    else gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, volumeTexture, 0);
    if (gl.checkFramebufferStatus(gl.FRAMEBUFFER) !== gl.FRAMEBUFFER_COMPLETE) throw new Error('Nebula volume unavailable');
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.useProgram(bakeProgram);
    gl.uniform2f(gl.getUniformLocation(bakeProgram, 'u_slice_size'), sliceWidth, sliceHeight);
    gl.uniform1f(gl.getUniformLocation(bakeProgram, 'u_spacing'), spacing);
    const layerOffsetUniform = gl.getUniformLocation(bakeProgram, 'u_layer_offset');
    gl.useProgram(program);
    gl.uniform1i(gl.getUniformLocation(program, 'u_volume'), 1);
    gl.uniform2f(gl.getUniformLocation(program, 'u_slice_size'), sliceWidth, sliceHeight);
    gl.uniform2f(gl.getUniformLocation(program, 'u_atlas_size'), atlasWidth, atlasHeight);
    gl.uniform1f(gl.getUniformLocation(program, 'u_spacing'), spacing);
    gl.uniform1f(gl.getUniformLocation(program, 'u_forward_speed'), forwardSpeed);
    const sizeUniform = gl.getUniformLocation(program, 'u_size');
    const timeUniform = gl.getUniformLocation(program, 'u_time');
    const pointerUniform = gl.getUniformLocation(program, 'u_pointer');
    const cameraUniforms=Object.fromEntries(['origin','right','up','forward','roll','horizon','focal','active']
      .map(name=>[name,gl.getUniformLocation(program,'u_camera_'+name)]));
    let viewportWidth = 1;
    let viewportHeight = 1;
    let qualityWidth = 1440;
    let frameTotal = 0;
    let frameCount = 0;
    let headroomWindows = 0;
    let smoothedFrameMs = 16.7;
    let ready = false;
    let cachedThrough = 255;
    function refreshVolume(time) {
      const requiredLayer = Math.ceil((7 + time * forwardSpeed + 27) / spacing);
      // History navigation can return from a completed flight to idle cruise.
      // Rebuild once when that older position has left the rolling cache.
      if(ready && Math.floor((7+time*forwardSpeed)/spacing)<cachedThrough-255) ready=false;
      if (ready && requiredLayer <= cachedThrough) return;
      gl.bindFramebuffer(gl.FRAMEBUFFER, framebuffer);
      gl.useProgram(bakeProgram);
      if (!ready) {
        const firstLayer = Math.max(0, Math.floor((7 + time * forwardSpeed) / spacing) - 2);
        cachedThrough = firstLayer + 255;
        if (nativeVolume) {
          gl.viewport(0, 0, sliceWidth, sliceHeight);
          for (let layer = firstLayer; layer <= cachedThrough; layer++) {
            gl.framebufferTextureLayer(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, volumeTexture, 0, layer % 256);
            gl.uniform1f(layerOffsetUniform, layer);
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
          }
        } else {
          gl.uniform1f(layerOffsetUniform, firstLayer);
          gl.viewport(0, 0, atlasWidth, atlasHeight);
          gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        }
      } else {
        // Normal motion streams a few small slices per second. Bound work
        // per frame even if a caller jumps forward in time.
        for (let count = 0; count < 4 && cachedThrough < requiredLayer; count++) {
          const layer = ++cachedThrough;
          const slot = layer % 256;
          gl.uniform1f(layerOffsetUniform, layer);
          if (nativeVolume) {
            gl.framebufferTextureLayer(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, volumeTexture, 0, slot);
            gl.viewport(0, 0, sliceWidth, sliceHeight);
          } else gl.viewport((slot % 16) * sliceWidth, Math.floor(slot / 16) * sliceHeight, sliceWidth, sliceHeight);
          gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        }
      }
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      gl.useProgram(program);
      gl.viewport(0, 0, canvas.width, canvas.height);
    }
    function updateResolution() {
      const pixelBudget = qualityWidth * qualityWidth * 9 / 16;
      const scale = Math.min(1, Math.sqrt(pixelBudget / (viewportWidth * viewportHeight)));
      const width = Math.max(1, Math.round(viewportWidth * scale));
      const height = Math.max(1, Math.round(viewportHeight * scale));
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
        gl.viewport(0, 0, width, height);
      }
      gl.uniform2f(sizeUniform, viewportWidth, viewportHeight);
    }
    return {
      resize(width, height) {
        viewportWidth = width;
        viewportHeight = height;
        updateResolution();
      },
      observeFrame(milliseconds) {
        if (milliseconds < 4 || milliseconds > 500) return;
        milliseconds = Math.min(milliseconds, 150);
        smoothedFrameMs += (milliseconds - smoothedFrameMs) * .08;
        frameTotal += milliseconds;
        frameCount++;
        if (frameCount < 40) return;
        const average = frameTotal / frameCount;
        frameCount = 0;
        frameTotal = 0;
        if (average > 21 && qualityWidth > 1280) {
          qualityWidth = Math.max(1280, Math.round(qualityWidth * Math.max(.8, Math.sqrt(17 / average))));
          headroomWindows = 0;
          updateResolution();
        } else {
          headroomWindows = average < 18.2 ? headroomWindows + 1 : 0;
          if (headroomWindows >= 6 && qualityWidth < 1920) {
            qualityWidth = Math.min(1920, Math.round(qualityWidth * 1.08));
            headroomWindows = 0;
            updateResolution();
          }
        }
      },
      performance() {
        return { fps:1000 / smoothedFrameMs, renderWidth:canvas.width, renderHeight:canvas.height, mode:nativeVolume ? '3d-cache' : 'atlas-cache' };
      },
      render(time, x, y, flight=null) {
        const volumeTime=time+(flight?.distance||0)/forwardSpeed;
        refreshVolume(volumeTime);
        gl.uniform1f(timeUniform, time);
        gl.uniform2f(pointerUniform, x, y);
        gl.uniform1f(cameraUniforms.active,flight?1:0);
        if(flight) {
          const origin=[Math.sin(time*.035)*.5+flight.eye[0]*.2,
            Math.cos(time*.027)*.35+flight.eye[1]*.2,7+time*forwardSpeed+flight.distance];
          gl.uniform3fv(cameraUniforms.origin,origin);
          gl.uniform3fv(cameraUniforms.right,flight.right);
          gl.uniform3fv(cameraUniforms.up,flight.up);
          gl.uniform3fv(cameraUniforms.forward,flight.forward);
          gl.uniform1f(cameraUniforms.roll,flight.roll);
          gl.uniform1f(cameraUniforms.horizon,flight.horizon);
          gl.uniform1f(cameraUniforms.focal,flight.focal);
        }
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        if (!ready) {
          ready = true;
          canvas.classList.add('is-ready');
        }
      }
    };
  };
})();
