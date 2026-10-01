const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
function setup(){
 const source=fs.readFileSync('dist/app.js','utf8');
 const events={},frames=new Map(),observers=[];let id=0,reads=0,height=2400;
 const root={get scrollHeight(){reads++;return height;}};
 const progress={style:{},setAttribute(){}};
 const hero={style:{},classList:{add(){},remove(){},toggle(){}},closest:()=>null};
 const reduced={matches:false,addEventListener(event,fn){this.change=fn;}};
 const window={scrollY:0,innerHeight:800,innerWidth:1440,addEventListener(event,fn){(events[event]??=[]).push(fn);}};
 const document={documentElement:root,body:{append(){},classList:{contains:()=>false}},querySelector:()=>hero,createElement:()=>progress};
 const code=source.slice(source.indexOf('const readingProgress='),source.indexOf('const destinationSticky='));
 vm.runInNewContext(code,{document,window,reduceMotion:reduced,updateHeader(){},requestAnimationFrame(fn){frames.set(++id,fn);return id;},ResizeObserver:class{constructor(fn){observers.push(fn)}observe(){}},IntersectionObserver:class{observe(){}}});
 const initial=[...frames.values()];frames.clear();initial.forEach(fn=>fn());
 return {window,hero,progress,reduced,frames,reads:()=>reads,emit(event){for(const fn of events[event]||[])fn();},flush(){const queued=[...frames.values()];frames.clear();queued.forEach(fn=>fn());},resize(h){height=h;observers.forEach(fn=>fn());}};
}
test('rapid scroll events render once per frame without remeasuring page height',()=>{
 const s=setup(),initial=s.reads();s.window.scrollY=800;
 for(let i=0;i<60;i++)s.emit('scroll');
 assert.equal(s.frames.size,1);s.flush();assert.equal(s.reads(),initial);assert.equal(s.progress.style.transform,'scaleX(0.5)');
});
test('layout changes refresh progress bounds and clamp overscroll',()=>{
 const s=setup();s.resize(4000);s.window.scrollY=800;s.emit('scroll');s.flush();assert.equal(s.progress.style.transform,'scaleX(0.25)');
 s.window.scrollY=-50;s.emit('scroll');s.flush();assert.equal(s.progress.style.transform,'scaleX(0)');
});
test('mobile and reduced motion clear parallax immediately',()=>{
 const s=setup();s.window.scrollY=100;s.emit('scroll');s.flush();assert.notEqual(s.hero.style.translate,'0 0');
 s.window.innerWidth=390;s.emit('resize');s.flush();assert.equal(s.hero.style.translate,'0 0');
 s.window.innerWidth=1440;s.emit('resize');s.flush();s.reduced.matches=true;s.reduced.change();s.flush();assert.equal(s.hero.style.translate,'0 0');
});
