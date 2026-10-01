(() => {
  const hero=document.querySelector('.hero');
  const photograph=hero?.querySelector('.hero-image');
  const control=hero?.querySelector('.scene-motion');
  if(!hero||!photograph||!control)return;
  const preference=window.matchMedia('(prefers-reduced-motion: reduce)');
  let renderer=null,frame=0,lastTime=0,lastDraw=0,elapsed=0,inView=true,userChoice=null;
  const smooth=(a,b,x)=>{const t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t);};
  // Trace the actual water/rock boundary in the unchanged 1672 × 941 photograph.
  const shoreline=[[557,800],[582,774],[604,761],[620,727],[640,675],[649,653],[666,686],[681,691],[689,735],[701,866],[723,858],[738,830],[753,809],[771,813],[790,784],[807,750],[826,740],[842,724],[866,706],[890,682],[914,651],[930,627],[941,594]].map(([y,x])=>[y/941,x/1672]);
  function coast(y){
    for(let i=1;i<shoreline.length;i++){
      if(y<=shoreline[i][0]){const [a,x]=shoreline[i-1],[b,z]=shoreline[i];return x+(z-x)*Math.max(0,Math.min(1,(y-a)/(b-a)));}
    }
    return shoreline.at(-1)[1];
  }
  const glNumber=value=>value.toFixed(8);
  const coastShader=`float coastAt(float y){float x=${glNumber(shoreline[0][1])};`+shoreline.slice(1).map(([y,x],i)=>`x=mix(x,${glNumber(x)},clamp((y-${glNumber(shoreline[i][0])})/${glNumber(y-shoreline[i][0])},0.0,1.0));`).join('')+'return x;}';
  function crop(width,height){
    const imageAspect=photograph.naturalWidth/photograph.naturalHeight,viewAspect=width/height;
    const sx=Math.min(1,viewAspect/imageAspect),sy=Math.min(1,imageAspect/viewAspect);
    const mobile=window.innerWidth<=760;
    return {sx,sy,ox:(1-sx)*(mobile?.35:.5),oy:(1-sy)*(mobile?.5:.55)};
  }
  function webglRenderer(){
    const canvas=document.createElement('canvas');
    const gl=canvas.getContext('webgl',{alpha:false,antialias:false,powerPreference:'low-power',depth:false,stencil:false});
    if(!gl)return null;
    const vertex=`attribute vec2 a_position;varying vec2 v_uv;void main(){gl_Position=vec4(a_position,0.0,1.0);v_uv=vec2((a_position.x+1.0)*.5,(1.0-a_position.y)*.5);}`;
    const fragment=`precision mediump float;
    varying vec2 v_uv;uniform sampler2D u_image;uniform vec2 u_scale;uniform vec2 u_offset;uniform float u_time;
    ${coastShader}
    void main(){
      vec2 uv=v_uv*u_scale+u_offset;
      float depth=smoothstep(.594,.625,uv.y);
      float coast=coastAt(uv.y);
      float water=depth*(1.0-smoothstep(coast-.0045,coast,uv.x));
      float near=smoothstep(.61,1.0,uv.y);
      float phase=uv.y*185.0-u_time*.62+sin(uv.x*14.0+u_time*.09)*.65;
      float swell=sin(phase)+sin(uv.y*310.0+uv.x*23.0-u_time*.41)*.36;
      vec2 drift=vec2(sin(uv.y*130.0-u_time*.35)*.00028,swell*.0012)*water*mix(.25,1.0,near);
      vec3 color=texture2D(u_image,clamp(uv+drift,vec2(.001),vec2(.999))).rgb;
      float light=sin(phase+1.15)*sin(uv.x*33.0+u_time*.1)*.003*water*near;
      gl_FragColor=vec4(color+vec3(light,light*.84,light*.6),1.0);
    }`;
    function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){gl.deleteShader(s);return null;}return s;}
    const vs=shader(gl.VERTEX_SHADER,vertex),fs=shader(gl.FRAGMENT_SHADER,fragment);
    if(!vs||!fs)return null;
    const program=gl.createProgram();gl.attachShader(program,vs);gl.attachShader(program,fs);gl.linkProgram(program);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS))return null;
    gl.useProgram(program);
    const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
    const position=gl.getAttribLocation(program,'a_position');gl.enableVertexAttribArray(position);gl.vertexAttribPointer(position,2,gl.FLOAT,false,0,0);
    const scale=gl.getUniformLocation(program,'u_scale'),offset=gl.getUniformLocation(program,'u_offset'),time=gl.getUniformLocation(program,'u_time');
    const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,gl.RGB,gl.UNSIGNED_BYTE,photograph);
    canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();switchToCanvas();});
    return {canvas,resize(width,height){
      canvas.width=width;canvas.height=height;gl.viewport(0,0,width,height);
      const c=crop(width,height);gl.uniform2f(scale,c.sx,c.sy);gl.uniform2f(offset,c.ox,c.oy);
    },draw(seconds){gl.uniform1f(time,seconds);gl.drawArrays(gl.TRIANGLES,0,6);}};
  }
  function canvasRenderer(){
    const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d',{alpha:true});
    if(!ctx)return null;
    const mask=document.createElement('canvas'),maskCtx=mask.getContext('2d');
    if(!maskCtx)return null;
    let c,width,height;
    return {canvas,resize(w,h){
      width=canvas.width=mask.width=w;height=canvas.height=mask.height=h;c=crop(w,h);
      maskCtx.clearRect(0,0,w,h);
      for(let y=0;y<h;y+=2){
        const uvY=y/h*c.sy+c.oy,depth=smooth(.594,.625,uvY);
        if(!depth)continue;
        const edge=(coast(uvY)-c.ox)/c.sx*w,soft=.0045/c.sx*w;
        if(edge<=0)continue;
        const gradient=maskCtx.createLinearGradient(edge-soft,0,edge,0);
        gradient.addColorStop(0,`rgba(255,255,255,${depth})`);gradient.addColorStop(1,'rgba(255,255,255,0)');
        maskCtx.fillStyle=gradient;maskCtx.fillRect(0,y,Math.min(w,edge),2);
      }
    },draw(seconds){
      ctx.globalCompositeOperation='source-over';ctx.clearRect(0,0,width,height);
      const iw=photograph.naturalWidth,ih=photograph.naturalHeight;
      const sourceWidth=c.sx*iw,sourceBand=c.sy/height*ih*2;
      for(let y=0;y<height;y+=2){
        const uvY=y/height*c.sy+c.oy,depth=smooth(.594,.625,uvY);
        if(!depth)continue;
        const near=smooth(.61,1,uvY),strength=depth*(.25+.75*near);
        const swell=Math.sin(uvY*185-seconds*.62)+Math.sin(uvY*310-seconds*.41)*.36;
        const dy=swell*.0012*strength,dx=Math.sin(uvY*130-seconds*.35)*.00028*strength;
        const sourceX=Math.max(0,Math.min(iw-sourceWidth,(c.ox+dx)*iw));
        const sourceY=Math.max(0,Math.min(ih-sourceBand,(uvY+dy)*ih));
        ctx.drawImage(photograph,sourceX,sourceY,sourceWidth,sourceBand,0,y,width,2);
      }
      ctx.globalCompositeOperation='destination-in';ctx.drawImage(mask,0,0);
      ctx.globalCompositeOperation='source-over';
    }};
  }
  const playing=()=>userChoice===null?!preference.matches:userChoice;
  function suspend(){cancelAnimationFrame(frame);frame=0;lastTime=0;}
  function tick(now){
    frame=0;
    if(!renderer||!playing()||!inView||document.hidden)return;
    if(lastTime)elapsed+=Math.min(now-lastTime,50);lastTime=now;
    if(now-lastDraw>=33){renderer.draw(elapsed/1000);lastDraw=now;}
    frame=requestAnimationFrame(tick);
  }
  function resume(){if(renderer&&!frame&&playing()&&inView&&!document.hidden){lastTime=0;frame=requestAnimationFrame(tick);}}
  function updateControl(){
    if(!renderer)return;
    const active=playing();
    control.hidden=false;control.setAttribute('aria-pressed',String(active));
    control.setAttribute('aria-label',active?'Pausar o movimento do mar':'Ativar o movimento do mar');
    control.innerHTML=active?'<span aria-hidden="true">Ⅱ</span> Pausar o mar':'<span aria-hidden="true">▷</span> Ativar o mar';
    renderer.canvas.hidden=preference.matches&&userChoice===null;
    if(active)resume();else suspend();
  }
  function resize(){
    if(!renderer)return;
    const r=hero.getBoundingClientRect();if(!r.width||!r.height)return;
    const dpr=Math.min(window.devicePixelRatio||1,1.25,1600/r.width);
    renderer.resize(Math.round(r.width*dpr),Math.round(r.height*dpr));renderer.draw(elapsed/1000);
  }
  function attach(){
    renderer.canvas.className='ocean-scene';renderer.canvas.setAttribute('aria-hidden','true');
    hero.insertBefore(renderer.canvas,hero.querySelector('.hero-shade'));
    hero.classList.add('has-water-motion');photograph.style.translate='0 0';resize();updateControl();
  }
  function switchToCanvas(){
    suspend();const previous=renderer;
    renderer=canvasRenderer();previous?.canvas.remove();
    if(renderer)attach();else{hero.classList.remove('has-water-motion');control.hidden=true;}
  }
  function load(){
    if(renderer||!photograph.naturalWidth)return;
    try{renderer=webglRenderer();}catch{renderer=null;}
    if(!renderer)renderer=canvasRenderer();
    if(renderer)attach();
  }
  control.addEventListener('click',()=>{userChoice=!playing();updateControl();});
  preference.addEventListener('change',()=>{userChoice=null;updateControl();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)suspend();else resume();});
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(resize).observe(hero);
  else window.addEventListener('resize',resize,{passive:true});
  if(typeof IntersectionObserver!=='undefined')new IntersectionObserver(([entry])=>{inView=entry.isIntersecting;if(inView)resume();else suspend();}).observe(hero);
  if(photograph.complete)load();else photograph.addEventListener('load',load,{once:true});
})();
