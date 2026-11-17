/* Existing Yggdrasil raven: shared feather texture, articulated wing stroke,
   spectral glints and afterimages. Its beak points into the nebula, away from us. */
(() => {
  'use strict';
  const source = new URL('../assets/traveler/raven.png', document.currentScript.src).href;
  window.createBifrostTraveler = canvas => {
    if (!canvas) return null;
    const gl = canvas.getContext('webgl', {
      alpha:true, premultipliedAlpha:true, antialias:false, depth:false,
      powerPreference:'high-performance'
    });
    const image = new Image();
    const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
    const flight=window.BifrostRavenFlight;
    let activeView=flight.camera(0,canvas.clientHeight||900);
    let ready = false, lost = false, replacement = null;
    let last = [0, 0, 0, null];
    let ratio = 1;
    canvas.dataset.renderer = 'yggdrasil-raven';
    if (!gl) {
      const context = canvas.getContext('2d');
      const fallback = {
        resize() {
          canvas.width = Math.max(1, canvas.clientWidth);
          canvas.height = Math.max(1, canvas.clientHeight);
          fallback.render();
        },
        render() {
          if (!ready || !context) return;
          context.clearRect(0,0,canvas.width,canvas.height);
          const width = Math.min(canvas.width*.8,canvas.height*.48,544), height = width*image.height/image.width*.6;
          context.globalAlpha = .75;
          context.drawImage(image,(canvas.width-width)/2,(canvas.height-height)/2,width,height);
          context.globalCompositeOperation = 'source-in';
          context.fillStyle = '#a4d1f4';
          context.fillRect(0,0,canvas.width,canvas.height);
          context.globalCompositeOperation = 'source-over';
          context.globalAlpha = 1;
        }
      };
      image.onload = () => { ready=true; fallback.resize(); };
      image.src = source;
      return fallback;
    }
    function program(vertex, fragment) {
      const value = gl.createProgram();
      for (const [type, code] of [[gl.VERTEX_SHADER,vertex],[gl.FRAGMENT_SHADER,fragment]]) {
        const shader = gl.createShader(type);
        gl.shaderSource(shader,code); gl.compileShader(shader);
        if (!gl.getShaderParameter(shader,gl.COMPILE_STATUS)) throw Error(gl.getShaderInfoLog(shader));
        gl.attachShader(value,shader); gl.deleteShader(shader);
      }
      gl.linkProgram(value);
      if (!gl.getProgramParameter(value,gl.LINK_STATUS)) throw Error(gl.getProgramInfoLog(value));
      return { value, uniforms:new Map() };
    }
    function uniform(material,name) {
      if (!material.uniforms.has(name)) material.uniforms.set(name,gl.getUniformLocation(material.value,name));
      return material.uniforms.get(name);
    }
    const pose = `
      uniform float u_time;
      uniform vec2 u_view;
      uniform vec2 u_pointer;
      uniform float u_dpr;
      uniform float u_departure;
      uniform vec3 u_eye;
      uniform vec3 u_right;
      uniform vec3 u_up;
      uniform vec3 u_forward;
      uniform float u_roll;
      uniform float u_horizon;
      uniform float u_focal;
      mat2 turn(float a) { float s=sin(a),c=cos(a); return mat2(c,s,-s,c); }
      float glide(float p){return clamp((p-.18)/.82,0.,1.);}
      float flightTravel(float p){return pow(glide(p),1.7)*64.;}
      float flightLead(float p){float g=glide(p);return smoothstep(0.,.12,g)*g*(2.-g)*34.;}
      vec3 path(float distance){return vec3(.0028*distance*distance,-.013*distance*distance,distance);}
      vec3 birdAt(vec3 samplePoint,float t) {
        vec2 uv=samplePoint.xy;
        vec3 p=vec3((uv.x-.5)*2.95,(.48-uv.y)*1.967,0.);
        float journey=max(0.,u_departure-max(0.,u_time-t)/4.2);
        float g=glide(journey),lift=smoothstep(.015,.19,journey);
        float fly=smoothstep(.06,.20,g),steer=smoothstep(0.,.13,g),dive=smoothstep(.18,.65,g);
        float distance=flightTravel(journey)+flightLead(journey);
        float wing=max(0.,abs(p.x)-.14);
        float beat=t*3.65;
        float flex=smoothstep(.12,.85,wing);
        float fold=.18+.74*sin(beat-wing*.36);
        fold+=.055*sin(t*1.2+sign(p.x));
        float pump=.18+.82*sin(journey*40.-wing*.4);
        fold=mix(fold,pump,smoothstep(0.,.035,journey));
        float thrust=.68-1.25*smoothstep(0.,.09,g)-wing*.1;
        float flightFold=.28+.50*sin(g*23.-wing*.65);
        flightFold=mix(flightFold,.48+.30*sin(g*23.-wing*.65),dive);
        fold=mix(fold,mix(thrust,flightFold,fly),smoothstep(0.,.025,g));
        float wingX=sign(p.x)*(.14+wing*cos(fold));
        p.x=mix(p.x,wingX,smoothstep(.10,.18,abs(p.x)));
        // The original raven camera looks from +Z. This entrance camera
        // looks from -Z: mirror depth, then pitch the head toward +Z.
        p.z=-wing*sin(fold)-.045*sin(beat-wing*1.3)*flex;
        p.y+=.07*flex*mix(sin(beat-.6),sin(g*23.+.5),fly)+.015*sin(t*2.+uv.y*8.);
        p.y-=flex*dive*.12;
        float tail=smoothstep(.57,.9,uv.y)*(1.-smoothstep(.12,.30,abs(p.x)));
        p.z+=tail*.025*sin(beat-.8);
        float preparedPitch=mix(1.02+.035*cos(t*.58),.35,lift);
        p.yz=turn(mix(preparedPitch,1.10+.88*atan(.026*distance),steer))*p.yz;
        p.xz=turn(mix(.06*sin(t*.58)+u_pointer.x*.035,-atan(.0056*distance),steer))*p.xz;
        p.xy=turn(.035*sin(t*.58+.45)*(1.-lift))*p.xy;
        p.x+=.025*sin(t*.38)-u_pointer.x*.018;
        p.y+=.035*sin(t*.82);
        p*=.82;
        p+=path(distance);
        p.y+=lift;
        return p;
      }
      vec4 project(vec3 p) {
        vec3 relative=p-u_eye;
        float depth=dot(relative,u_forward);
        if(depth<=.1)return vec4(2.,2.,2.,1.);
        vec2 screen=turn(u_roll)*vec2(dot(relative,u_right),dot(relative,u_up));
        return vec4(screen.x*u_focal*u_view.y/u_view.x,screen.y*u_focal+depth*u_horizon,0.,depth);
      }
      vec3 tint(float height,float variation) {
        float shift=.5+.5*sin(u_time*.39+height*1.8-1.6+variation*.12);
        vec3 pink=vec3(1.,.065,.48),cyan=vec3(.025,.82,1.);
        vec3 purple=vec3(.25,.095,1.);
        return mix(mix(pink,purple,smoothstep(.28,.62,shift)),cyan,smoothstep(.60,.94,shift));
      }
    `;
    const surface = program(`
      precision highp float;
      attribute vec3 a_sample;
      varying vec2 v_uv;
      varying float v_depth;
      ${pose}
      void main() {
        v_uv=a_sample.xy;
        vec3 p=birdAt(a_sample,u_time);
        v_depth=-(p.z-flightTravel(u_departure)-flightLead(u_departure))/.82;
        gl_Position=project(p);
      }
    `, `
      precision highp float;
      uniform sampler2D u_texture;
      uniform float u_echo;
      varying vec2 v_uv;
      varying float v_depth;
      ${pose}
      void main() {
        vec4 tex=texture2D(u_texture,v_uv);
        if(tex.a<.045) discard;
        float luma=dot(tex.rgb,vec3(.24,.52,.24));
        float edge=abs(luma-dot(texture2D(u_texture,v_uv+vec2(.0017,.001)).rgb,vec3(.24,.52,.24)));
        float grain=fract(sin(dot(floor(v_uv*vec2(1900.,1300.)),vec2(12.9898,78.233)))*43758.5453);
        float line=.78+.22*sin(v_uv.y*3900.);
        float scan=exp(-pow((v_uv.y-fract(u_time*.13))*14.,2.));
        float structure=pow(luma,1.45)*.48+edge*1.2;
        vec3 color=tint(v_uv.y+v_depth*.3,0.)*structure*(1.+scan*1.9)*line;
        color+=vec3(.65,.8,1.)*pow(luma,4.)*.23;
        float alpha=tex.a*smoothstep(.045,.16,luma)*(.55+grain*.45);
        float echo=mix(1.,.085,u_echo);
        gl_FragColor=vec4(color*alpha*echo,alpha*.20*echo);
      }
    `);
    const particles = program(`
      precision highp float;
      attribute vec3 a_sample;
      attribute vec4 a_detail;
      varying vec3 v_color;
      varying float v_alpha;
      varying float v_slant;
      varying float v_streak;
      ${pose}
      void main() {
        float seed=a_detail.x;
        float age=fract(u_time*(.25+seed*.18)+seed);
        float kind=a_detail.w;
        float released=step(.5,kind);
        vec3 p=birdAt(a_sample,u_time-released*age*.85);
        if(a_detail.w>1.5) {
          p.y-=age*.32;
          p.x+=sin(age*5.+seed*34.)*age*.075;
          p.z+=age*.15;
        } else if(a_detail.w>.5) {
          p.x+=(seed-.5)*age*.16;
          p.y-=age*.14;
          p.z+=age*.12;
        }
        float sparkle=.28+.72*pow(.5+.5*sin(u_time*(2.+seed*2.)+seed*150.),6.);
        v_alpha=a_detail.y*sparkle;
        v_alpha*=mix(1.,sin(age*3.14159)*.48,released);
        if(kind>1.5) v_alpha*=.3;
        float glint=pow(.5+.5*sin(u_time*2.8+seed*190.),35.);
        vec3 color=tint(a_sample.y-(p.z-flightTravel(u_departure)-flightLead(u_departure))*.3/.82,seed);
        color=mix(color,vec3(.9,.97,1.),min(.9,a_detail.y*.22+glint*.6));
        v_color=color;
        vec4 clip=project(p);
        gl_Position=clip;
        float size=.62+a_detail.z*1.8+glint*2.;
        gl_PointSize=clamp(size*u_dpr*4.4/clip.w,.7,8.*u_dpr);
        v_slant=seed*6.28318;
        v_streak=released;
      }
    `, `
      precision mediump float;
      varying vec3 v_color;
      varying float v_alpha;
      varying float v_slant;
      varying float v_streak;
      void main() {
        vec2 q=gl_PointCoord-.5;
        vec2 shape=mix(q,q*vec2(.65,1.8),v_streak);
        float core=exp(-dot(shape,shape)*24.);
        float soft=exp(-dot(q,q)*10.)*.22;
        float alpha=(core+soft)*min(1.,v_alpha);
        gl_FragColor=vec4(v_color*alpha,alpha*.45);
      }
    `);
    const screenVertex = `
      attribute vec2 a_position;
      varying vec2 v_uv;
      void main() { v_uv=a_position*.5+.5; gl_Position=vec4(a_position,0.,1.); }
    `;
    const blur = program(screenVertex,`
      precision mediump float;
      uniform sampler2D u_texture;
      uniform vec2 u_step;
      varying vec2 v_uv;
      void main() {
        vec3 c=texture2D(u_texture,v_uv).rgb*.227027;
        c+=texture2D(u_texture,v_uv+u_step*1.384615).rgb*.316216;
        c+=texture2D(u_texture,v_uv-u_step*1.384615).rgb*.316216;
        c+=texture2D(u_texture,v_uv+u_step*3.230769).rgb*.070270;
        c+=texture2D(u_texture,v_uv-u_step*3.230769).rgb*.070270;
        gl_FragColor=vec4(c,1.);
      }
    `);
    const composite = program(screenVertex,`
      precision mediump float;
      uniform sampler2D u_texture;
      uniform sampler2D u_bloom;
      uniform sampler2D u_halo;
      varying vec2 v_uv;
      void main() {
        vec4 body=texture2D(u_texture,v_uv);
        vec3 light=body.rgb+texture2D(u_bloom,v_uv).rgb*.8;
        light+=texture2D(u_halo,v_uv).rgb*.9;
        vec3 color=pow(1.-exp(-light*1.9),vec3(.86));
        float alpha=max(body.a*.48,max(color.r,max(color.g,color.b)));
        gl_FragColor=vec4(color,clamp(alpha,0.,.88));
      }
    `);
    function buffer(values) {
      const result=gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER,result);
      gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values),gl.STATIC_DRAW);
      return result;
    }
    function texture() {
      const value=gl.createTexture();
      gl.bindTexture(gl.TEXTURE_2D,value);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
      return value;
    }
    function target() {
      const value=texture(), framebuffer=gl.createFramebuffer();
      gl.bindFramebuffer(gl.FRAMEBUFFER,framebuffer);
      gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,value,0);
      return {texture:value,framebuffer,width:1,height:1};
    }
    const bodyTexture=texture();
    const scene=target(),blurA=target(),blurB=target(),haloA=target(),haloB=target();
    const screen=buffer([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]);
    let gridBuffer,pointBuffer,detailBuffer,gridCount=0,pointCount=0;
    function depth() { return 0; }
    function sizeTarget(item,width,height) {
      item.width=Math.max(1,Math.round(width)); item.height=Math.max(1,Math.round(height));
      gl.bindTexture(gl.TEXTURE_2D,item.texture);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,item.width,item.height,0,gl.RGBA,gl.UNSIGNED_BYTE,null);
    }
    function bindTarget(item) {
      gl.bindFramebuffer(gl.FRAMEBUFFER,item?.framebuffer||null);
      gl.viewport(0,0,item?.width||canvas.width,item?.height||canvas.height);
    }
    function use(material,time,x,y) {
      gl.useProgram(material.value);
      gl.uniform1f(uniform(material,'u_time'),time);
      gl.uniform2f(uniform(material,'u_view'),canvas.width,canvas.height);
      gl.uniform2f(uniform(material,'u_pointer'),x||0,y||0);
      gl.uniform1f(uniform(material,'u_dpr'),ratio);
      gl.uniform1f(uniform(material,'u_departure'),activeView.progress);
      gl.uniform3fv(uniform(material,'u_eye'),activeView.eye);
      gl.uniform3fv(uniform(material,'u_right'),activeView.right);
      gl.uniform3fv(uniform(material,'u_up'),activeView.up);
      gl.uniform3fv(uniform(material,'u_forward'),activeView.forward);
      gl.uniform1f(uniform(material,'u_roll'),activeView.roll);
      gl.uniform1f(uniform(material,'u_horizon'),activeView.horizon);
      gl.uniform1f(uniform(material,'u_focal'),activeView.focal);
    }
    function attribute(material,name,value,size) {
      const index=gl.getAttribLocation(material.value,name);
      if(index<0)return;
      gl.bindBuffer(gl.ARRAY_BUFFER,value); gl.enableVertexAttribArray(index);
      gl.vertexAttribPointer(index,size,gl.FLOAT,false,0,0);
    }
    function bindTexture(material,name,value,unit) {
      gl.activeTexture(gl.TEXTURE0+unit); gl.bindTexture(gl.TEXTURE_2D,value);
      gl.uniform1i(uniform(material,name),unit);
    }
    function blurPass(input,output,x,y) {
      bindTarget(output); use(blur,0,0,0);
      attribute(blur,'a_position',screen,2);
      bindTexture(blur,'u_texture',input.texture,0);
      gl.uniform2f(uniform(blur,'u_step'),x/input.width,y/input.height);
      gl.drawArrays(gl.TRIANGLES,0,6);
    }
    const api={
      resize() {
        if(replacement)return replacement.resize();
        if(lost)return;
        ratio=Math.min(window.devicePixelRatio||1,1.75);
        canvas.width=Math.max(1,Math.round(canvas.clientWidth*ratio));
        canvas.height=Math.max(1,Math.round(canvas.clientHeight*ratio));
        gl.activeTexture(gl.TEXTURE0);
        sizeTarget(scene,canvas.width,canvas.height);
        sizeTarget(blurA,canvas.width/2,canvas.height/2);
        sizeTarget(blurB,canvas.width/2,canvas.height/2);
        sizeTarget(haloA,canvas.width/4,canvas.height/4);
        sizeTarget(haloB,canvas.width/4,canvas.height/4);
      },
      render(time=0,x=0,y=0,view=null) {
        last=[time,x,y,view];
        if(replacement)return replacement.render(time,x,y,view);
        if(!ready||lost)return;
        activeView=view||flight.camera(0,canvas.clientHeight);
        bindTarget(scene);
        gl.clearColor(0,0,0,0); gl.clear(gl.COLOR_BUFFER_BIT);
        gl.disable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE,gl.ONE);
        use(surface,time,x,y);
        attribute(surface,'a_sample',gridBuffer,3);
        bindTexture(surface,'u_texture',bodyTexture,0);
        gl.uniform1f(uniform(surface,'u_echo'),0);
        gl.drawArrays(gl.TRIANGLES,0,gridCount);
        if(!reducedMotion.matches) {
          gl.uniform1f(uniform(surface,'u_echo'),1);
          gl.uniform1f(uniform(surface,'u_time'),time-.075);
          gl.uniform1f(uniform(surface,'u_departure'),Math.max(0,activeView.progress-.075/flight.duration));
          gl.drawArrays(gl.TRIANGLES,0,gridCount);
          gl.uniform1f(uniform(surface,'u_time'),time-.15);
          gl.uniform1f(uniform(surface,'u_departure'),Math.max(0,activeView.progress-.15/flight.duration));
          gl.drawArrays(gl.TRIANGLES,0,gridCount);
        }
        use(particles,time,x,y);
        attribute(particles,'a_sample',pointBuffer,3);
        attribute(particles,'a_detail',detailBuffer,4);
        gl.drawArrays(gl.POINTS,0,pointCount);
        gl.disable(gl.BLEND);
        blurPass(scene,blurA,1.15,0); blurPass(blurA,blurB,0,1.15);
        blurPass(blurB,haloA,1.8,0); blurPass(haloA,haloB,0,1.8);
        bindTarget(null); use(composite,0,0,0);
        attribute(composite,'a_position',screen,2);
        bindTexture(composite,'u_texture',scene.texture,0);
        bindTexture(composite,'u_bloom',blurB.texture,1);
        bindTexture(composite,'u_halo',haloB.texture,2);
        gl.drawArrays(gl.TRIANGLES,0,6);
      }
    };
    image.onload=() => {
      if(lost)return;
      gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D,bodyTexture);
      gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,image);
      const grid=[], columns=120,rows=82;
      for(let y=0;y<rows;y++)for(let x=0;x<columns;x++) {
        const u=x/columns,v=y/rows,du=1/columns,dv=1/rows;
        for(const [a,b] of [[u,v],[u+du,v],[u,v+dv],[u+du,v],[u+du,v+dv],[u,v+dv]])grid.push(a,b,depth(a,b));
      }
      gridBuffer=buffer(grid); gridCount=grid.length/3;
      const sample=document.createElement('canvas');
      sample.width=768;sample.height=512;
      const context=sample.getContext('2d',{willReadFrequently:true});
      context.drawImage(image,0,0,sample.width,sample.height);
      const pixels=context.getImageData(0,0,sample.width,sample.height).data;
      function lumaAt(x,y) {
        const i=(y*768+x)*4;
        return (pixels[i]*.24+pixels[i+1]*.52+pixels[i+2]*.24)/255;
      }
      let seed=4171;
      function random(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}
      const points=[],details=[];
      for(let i=0;i<100000;i++) {
        const x=1+Math.floor(random()*766),y=1+Math.floor(random()*510),index=(y*768+x)*4;
        const alpha=pixels[index+3]/255;
        const luma=lumaAt(x,y);
        const edge=Math.abs(luma-lumaAt(x+1,y))+Math.abs(luma-lumaAt(x,y+1));
        if(alpha<.3||luma<.08||random()>Math.min(.95,luma*.55+edge*5.))continue;
        const u=(x+random())/768,v=(y+random())/512;
        const variation=random();
        points.push(u,v,depth(u,v));
        details.push(variation,(.15+luma*1.1+edge*1.4)*alpha,random(),variation>.90?1:0);
      }
      // A short spectral wake leaves the wing tips and tail.
      const anchors=[[.10,.43],[.90,.43],[.49,.84],[.51,.84]];
      for(let i=0;i<320;i++) {
        const [u,v]=anchors[i%anchors.length];
        const a=u+(random()-.5)*.025,b=v+(random()-.5)*.025;
        points.push(a,b,depth(a,b));
        details.push(random(),.32,random(),2);
      }
      pointBuffer=buffer(points);detailBuffer=buffer(details);pointCount=points.length/3;
      ready=true;
      canvas.dataset.particles=String(pointCount);
      canvas.dataset.ready='true';
      api.render(...last);
    };
    image.onerror=() => { canvas.dataset.error='lightform-image'; };
    canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();lost=true;});
    canvas.addEventListener('webglcontextrestored',()=>{
      replacement=window.createBifrostTraveler(canvas);
      replacement?.resize();
      replacement?.render(...last);
    },{once:true});
    image.src=source;
    return api;
  };
})();
