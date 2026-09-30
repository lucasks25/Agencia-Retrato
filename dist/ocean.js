(() => {
  const preference=window.matchMedia('(prefers-reduced-motion: reduce)');
  if(preference.matches){
    const enable=event=>{if(!event.matches){preference.removeEventListener('change',enable);initializeOcean();}};
    preference.addEventListener('change',enable);
  }else initializeOcean();
  function initializeOcean(){
  const hero=document.querySelector('.hero');
  const photograph=hero?.querySelector('.hero-image');
  const control=hero?.querySelector('.scene-motion');
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  if(!hero||!photograph||!control||reduced.matches)return;
  const canvas=document.createElement('canvas');
  canvas.className='ocean-scene';
  canvas.setAttribute('aria-hidden','true');
  const gl=canvas.getContext('webgl',{alpha:false,antialias:false,powerPreference:'low-power',depth:false,stencil:false});
  if(!gl)return;
  const vertex=`attribute vec2 a_position;varying vec2 v_uv;void main(){gl_Position=vec4(a_position,0.0,1.0);v_uv=vec2((a_position.x+1.0)*.5,(1.0-a_position.y)*.5);}`;
  const fragment=`precision mediump float;
  varying vec2 v_uv;uniform sampler2D u_image;uniform vec2 u_scale;uniform vec2 u_offset;uniform float u_time;
  void main(){
    vec2 uv=v_uv*u_scale+u_offset;
    float depth=smoothstep(.596,.67,uv.y);
    float water=depth*(1.0-smoothstep(.365,.405,uv.x));
    float near=smoothstep(.62,1.0,uv.y);
    float wave=sin(uv.y*210.0-u_time*1.35+sin(uv.x*19.0+u_time*.22)*1.6);
    float wave2=sin(uv.y*340.0+uv.x*30.0-u_time*.85);
    vec2 displacement=vec2(sin(uv.y*160.0-u_time*.8)*.00032,(wave+wave2*.45)*.00145)*water*mix(.22,1.0,near);
    vec3 color=texture2D(u_image,clamp(uv+displacement,vec2(.001),vec2(.999))).rgb;
    float shimmer=sin(uv.y*225.0-u_time*1.35+uv.x*7.0)*sin(uv.x*39.0+u_time*.2)*.006*water*near;
    gl_FragColor=vec4(color+vec3(shimmer,shimmer*.86,shimmer*.63),1.0);
  }`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){gl.deleteShader(s);return null;}return s;}
  const vs=shader(gl.VERTEX_SHADER,vertex),fs=shader(gl.FRAGMENT_SHADER,fragment);
  if(!vs||!fs)return;
  const program=gl.createProgram();gl.attachShader(program,vs);gl.attachShader(program,fs);gl.linkProgram(program);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS))return;
  gl.useProgram(program);
  const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
  const position=gl.getAttribLocation(program,'a_position');gl.enableVertexAttribArray(position);gl.vertexAttribPointer(position,2,gl.FLOAT,false,0,0);
  const scale=gl.getUniformLocation(program,'u_scale'),offset=gl.getUniformLocation(program,'u_offset'),time=gl.getUniformLocation(program,'u_time');
  const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
  let loaded=false,running=true,inView=true,frame=0,lastFrame=0,elapsed=0,lastTime=0;
  function resize(){
    if(!loaded)return;
    const r=hero.getBoundingClientRect();const dpr=Math.min(window.devicePixelRatio||1,1.35,2000/r.width);
    canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr);gl.viewport(0,0,canvas.width,canvas.height);
    const imageAspect=photograph.naturalWidth/photograph.naturalHeight,viewAspect=r.width/r.height;
    const sx=Math.min(1,viewAspect/imageAspect),sy=Math.min(1,imageAspect/viewAspect);
    const mobile=window.innerWidth<=760;
    gl.uniform2f(scale,sx,sy);gl.uniform2f(offset,(1-sx)*(mobile?.35:.5),(1-sy)*(mobile?.5:.55));
    draw();
  }
  function draw(){gl.uniform1f(time,elapsed/1000);gl.drawArrays(gl.TRIANGLES,0,6);}
  function tick(now){
    frame=0;
    if(!running||!inView||document.hidden||reduced.matches)return;
    if(lastTime)elapsed+=Math.min(now-lastTime,50);lastTime=now;
    if(now-lastFrame>=33){draw();lastFrame=now;}
    frame=requestAnimationFrame(tick);
  }
  function resume(){if(!frame&&loaded&&running&&inView&&!document.hidden&&!reduced.matches){lastTime=0;frame=requestAnimationFrame(tick);}}
  function suspend(){cancelAnimationFrame(frame);frame=0;lastTime=0;}
  function load(){
    if(loaded||!photograph.naturalWidth)return;
    try{gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,gl.RGB,gl.UNSIGNED_BYTE,photograph);}catch{return;}
    loaded=true;hero.insertBefore(canvas,hero.querySelector('.hero-shade'));hero.classList.add('has-water-motion');photograph.style.translate='0 0';
    control.hidden=false;resize();resume();
  }
  if(photograph.complete)load();else photograph.addEventListener('load',load,{once:true});
  control.addEventListener('click',()=>{running=!running;control.setAttribute('aria-pressed',String(running));control.setAttribute('aria-label',running?'Pausar o movimento do mar':'Ativar o movimento do mar');control.innerHTML=running?'<span aria-hidden="true">Ⅱ</span> Mar em movimento':'<span aria-hidden="true">▷</span> Ativar movimento';if(running)resume();else suspend();});
  new ResizeObserver(resize).observe(hero);
  new IntersectionObserver(([entry])=>{inView=entry.isIntersecting;if(inView)resume();else suspend();}).observe(hero);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)suspend();else resume();});
  reduced.addEventListener('change',event=>{if(event.matches){suspend();canvas.hidden=true;control.hidden=true;hero.classList.remove('has-water-motion');}else{canvas.hidden=false;control.hidden=false;hero.classList.add('has-water-motion');resume();}});
  canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();suspend();canvas.hidden=true;control.hidden=true;hero.classList.remove('has-water-motion');});
  }
})();
