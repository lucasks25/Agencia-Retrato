const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const vm=require('node:vm');

// Offline controller tests: graphics and DOM boundaries are explicit adapters.
// These do not open a browser or claim to verify the rendered appearance.
function scene({reduced=false,maldives=false,withoutControl=false}={}) {
  const frames=new Map(), canvases=[], draws=[],maskRects=[];
  let nextFrame=0;
  function element() {
    const listeners={},attributes={};
    return {hidden:false,dataset:{},style:{},listeners,attributes,
      addEventListener(type,fn){(listeners[type]??=[]).push(fn);},
      emit(type,event={}){for(const fn of listeners[type]||[])fn(event);},
      setAttribute(name,value){attributes[name]=String(value);},
      classList:{add(){},remove(){}},getBoundingClientRect(){return {width:1440,height:900};}};
  }
  const photograph={...element(),complete:true,naturalWidth:maldives?3840:1672,naturalHeight:maldives?2160:941,dataset:{waterScene:maldives?'maldives':''}};
  const control={...element(),hidden:true};
  const hero={...element(),querySelector(selector){return selector==='.hero-image'?photograph:selector==='.scene-motion'?(withoutControl?null:control):{};},
    insertBefore(canvas){canvas.attached=true;},append(canvas){canvas.attached=true;}};
  const preference={...element(),matches:reduced};
  const document={...element(),hidden:false,querySelector(){return hero;},createElement(tag){
    assert.equal(tag,'canvas');
    const canvas=element();
    const context={clearRect(){},save(){},restore(){},setTransform(){},
      drawImage(...args){draws.push({canvas,args});},fillRect(x,y,width,height){maskRects.push({x,y,width,height});},
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
  return {control,document,preference,frames,draws,canvases,maskRects,advance};
}

test('the sea keeps moving without a visible motion control',()=>{
  const s=scene({withoutControl:true,maldives:true});
  assert.ok(s.frames.size>0);
  s.advance(50);assert.ok(s.draws.length>0);
});

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

test('the sea mask reaches the water beside the middle coastal rocks',()=>{
  const s=scene();
  // In the source photograph, water at y=720 extends to approximately x=850.
  // With this hand-checked 1440 × 900 crop, that area extends past screen x=700.
  const band=s.maskRects.find(rect=>rect.y===690);
  assert.ok(band.width>=700,'the coastal inlet must not remain outside the animation');
  assert.ok(band.width<760,'the nearby wall and rocks must remain outside the water mask');
});

test('the sea mask retreats around the foreground rocks',()=>{
  const s=scene();
  const band=s.maskRects.find(rect=>rect.y===898);
  assert.ok(band.width<530,'foreground rocks must not be displaced as water');
});

test('the water displacement stays subtle throughout an animation cycle',()=>{
  const s=scene();
  for(let time=100;time<=8000;time+=50)s.advance(time);
  const bands=s.draws.filter(x=>x.canvas.attached&&x.args.length===9);
  assert.ok(bands.length>0);
  for(const {args} of bands){
    const sourceY=args[2],destinationY=args[6];
    const originalY=destinationY/900*941;
    assert.ok(Math.abs(sourceY-originalY)<=1.65,'water must drift less than two source pixels');
  }
});


test('the 4K Maldives scene animates open water while excluding the island',()=>{
  const s=scene({maldives:true});
  const upper=s.maskRects.find(rect=>rect.y===200);
  const island=s.maskRects.find(rect=>rect.y===850);
  assert.ok(upper.width>650,'open water in the upper half must receive movement');
  assert.ok(!island||island.width<150,'foreground island must not be displaced');
  assert.equal(s.control.hidden,false);
});
