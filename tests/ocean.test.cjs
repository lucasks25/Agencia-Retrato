const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const vm=require('node:vm');

// Offline controller tests: graphics and DOM boundaries are explicit adapters.
// These do not open a browser or claim to verify the rendered appearance.
function scene({reduced=false}={}) {
  const frames=new Map(), canvases=[], draws=[];
  let nextFrame=0;
  function element() {
    const listeners={},attributes={};
    return {hidden:false,dataset:{},style:{},listeners,attributes,
      addEventListener(type,fn){(listeners[type]??=[]).push(fn);},
      emit(type,event={}){for(const fn of listeners[type]||[])fn(event);},
      setAttribute(name,value){attributes[name]=String(value);},
      classList:{add(){},remove(){}},getBoundingClientRect(){return {width:1440,height:900};}};
  }
  const photograph={...element(),complete:true,naturalWidth:1672,naturalHeight:941};
  const control={...element(),hidden:true};
  const hero={...element(),querySelector(selector){return selector==='.hero-image'?photograph:selector==='.scene-motion'?control:{};},
    insertBefore(canvas){canvas.attached=true;},append(canvas){canvas.attached=true;}};
  const preference={...element(),matches:reduced};
  const document={...element(),hidden:false,querySelector(){return hero;},createElement(tag){
    assert.equal(tag,'canvas');
    const canvas=element();
    const context={clearRect(){},save(){},restore(){},setTransform(){},
      drawImage(...args){draws.push({canvas,args});},fillRect(){},
      createLinearGradient(){return {addColorStop(){}};}};
    canvas.getContext=kind=>kind==='2d'?context:null;
    canvases.push(canvas);return canvas;
  }};
  const window={...element(),devicePixelRatio:1,innerWidth:1440,matchMedia(){return preference;}};
  const sandbox={document,window,Float32Array,Math,
    requestAnimationFrame(fn){frames.set(++nextFrame,fn);return nextFrame;},
    cancelAnimationFrame(id){frames.delete(id);},
    ResizeObserver:class {observe(){}},IntersectionObserver:class {observe(){}},
  };
  vm.runInNewContext(readFileSync(require.resolve('../dist/ocean.js'),'utf8'),sandbox);
  function advance(now){const queued=[...frames.values()];frames.clear();for(const fn of queued)fn(now);}
  return {control,document,preference,frames,draws,canvases,advance};
}

test('unavailable WebGL still produces animated sea frames through Canvas 2D',()=>{
  const s=scene();
  assert.equal(s.control.hidden,false,'a supported fallback must expose the motion control');
  assert.ok(s.frames.size>0,'the fallback must start the animation');
  s.advance(100);s.advance(150);
  const first=s.draws.filter(x=>x.canvas.attached).map(x=>x.args.slice(1));
  s.draws.length=0;
  s.advance(250);
  const next=s.draws.filter(x=>x.canvas.attached).map(x=>x.args.slice(1));
  assert.ok(first.length>0&&next.length>0,'both frames must render');
  assert.notDeepEqual(first.at(-20),next.at(-20),'source sampling must evolve over time');
});

test('pause stops scheduled frames and a second click resumes them',()=>{
  const s=scene();
  s.control.emit('click');
  assert.equal(s.frames.size,0);
  assert.equal(s.control.attributes['aria-pressed'],'false');
  s.control.emit('click');
  assert.ok(s.frames.size>0);
  assert.equal(s.control.attributes['aria-pressed'],'true');
});

test('reduced motion starts paused but retains an explicit opt-in',()=>{
  const s=scene({reduced:true});
  assert.equal(s.frames.size,0);
  assert.equal(s.control.hidden,false,'the visitor must be able to opt into motion');
  assert.equal(s.control.attributes['aria-pressed'],'false');
  s.control.emit('click');
  assert.ok(s.frames.size>0);
});

test('a hidden page suspends frames and visibility resumes them',()=>{
  const s=scene();
  s.document.hidden=true;s.document.emit('visibilitychange');
  assert.equal(s.frames.size,0);
  s.document.hidden=false;s.document.emit('visibilitychange');
  assert.ok(s.frames.size>0);
});
