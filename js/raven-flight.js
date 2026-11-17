/* Yggdrasil's 4.2-second rise and curved dive, mirrored for a +Z nebula.
   One camera is shared by the raven, gas and depth-projected star trails. */
(() => {
  'use strict';
  const duration=4.2,releaseAt=.18;
  const clamp=value=>Math.max(0,Math.min(1,value));
  function smooth(a,b,value){const t=clamp((value-a)/(b-a));return t*t*(3-2*t);}
  function path(distance){return [.0028*distance*distance,-.013*distance*distance,distance];}
  function normalize(v){const length=Math.hypot(...v)||1;return v.map(x=>x/length);}
  function cross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
  function camera(progress,height=900){
    const p=clamp(progress),glide=clamp((p-releaseAt)/(1-releaseAt));
    const rise=smooth(.015,.19,p),distance=Math.pow(glide,1.7)*64;
    const lead=smooth(0,.12,glide)*glide*(2-glide)*34;
    const eye=path(distance);
    eye[1]+=rise*(.25+.75*smooth(0,.18,glide));
    eye[2]-=4.35;
    const target=path(distance+lead);target[1]+=rise;
    const forward=normalize(target.map((value,index)=>value-eye[index]));
    const right=normalize(cross([0,1,0],forward));
    const up=cross(forward,right);
    const roll=.035*Math.sin(Math.PI*rise)*(1-glide)-.38*Math.sin(Math.PI*smooth(.05,.96,glide));
    const sourceHorizon=(.32+.20*rise)*(1-smooth(0,.40,glide));
    const horizon=-.04+(sourceHorizon*.6+.04)*smooth(0,.16,p);
    const focal=2.18*Math.min(.78,840/Math.max(1,height))+.48*smooth(0,.18,p);
    return {progress:p,glide,rise,distance,lead,eye,forward,right,up,roll,horizon,focal};
  }
  function project(position,view,width,height){
    const relative=position.map((value,index)=>value-view.eye[index]);
    const dot=axis=>relative.reduce((sum,value,index)=>sum+value*axis[index],0);
    const depth=dot(view.forward);
    if(depth<=.6)return null;
    const x=dot(view.right),y=dot(view.up),s=Math.sin(view.roll),c=Math.cos(view.roll);
    const scale=height*view.focal/(2*depth);
    return [width/2+(x*c-y*s)*scale,height*(.5-view.horizon/2)-(x*s+y*c)*scale,depth];
  }
  function paintStars(context,rays,view,previous,middle,width,height){
    const g=view.glide;
    const fade=smooth(0,.14,g)*(1-smooth(.86,1,view.progress));
    if(fade<=0)return;
    context.save();context.globalCompositeOperation='lighter';context.lineCap='round';
    for(const ray of rays){
      const distance=((ray.distance-view.distance+6)%120+120)%120+view.distance-6;
      const center=path(distance);center[1]+=1;
      const tangent=normalize([.0056*distance,-.026*distance,1]);
      const right=normalize(cross([0,1,0],tangent)),up=cross(tangent,right);
      const rx=Math.cos(ray.angle)*ray.radius,ry=Math.sin(ray.angle)*ray.radius;
      const position=center.map((value,index)=>value+right[index]*rx+up[index]*ry);
      const head=project(position,view,width,height),tail=project(position,previous,width,height);
      const mid=project(position,middle,width,height);
      if(!head||!tail||!mid||head[0]<-180||head[0]>width+180||head[1]<-180||head[1]>height+180)continue;
      const glow=context.createLinearGradient(tail[0],tail[1],head[0]+.001,head[1]);
      glow.addColorStop(0,`rgba(${ray.color},0)`);
      glow.addColorStop(.85,`rgba(${ray.color},.8)`);
      glow.addColorStop(1,`rgba(${ray.color},.05)`);
      context.globalAlpha=fade*(.22+Math.max(0,1-head[2]/135)*.65);
      context.strokeStyle=glow;
      context.lineWidth=Math.max(.4,ray.width*12/(head[2]+5));
      context.beginPath();context.moveTo(tail[0],tail[1]);
      context.quadraticCurveTo(mid[0],mid[1],head[0],head[1]);context.stroke();
      if(Math.hypot(head[0]-tail[0],head[1]-tail[1])<1){
        context.fillStyle=`rgba(${ray.color},.45)`;
        context.fillRect(head[0],head[1],.7,.7);
      }
    }
    context.restore();
  }
  window.BifrostRavenFlight={duration,releaseAt,smooth,path,camera,project,paintStars};
})();
