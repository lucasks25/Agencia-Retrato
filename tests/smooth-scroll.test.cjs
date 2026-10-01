const {test}=require('node:test');const assert=require('node:assert/strict');const vm=require('node:vm');const fs=require('node:fs');
function setup({reduced=false,desktop=true,dialog=false}={}){
 const preferences=[{matches:reduced},{matches:desktop}],instances=[],events={};let mutation;
 preferences.forEach(p=>p.addEventListener=(e,fn)=>p.change=fn);
 const document={body:{classList:{contains:()=>false}},querySelector:()=>dialog?{}:null};
 const window={matchMedia:()=>preferences.shift(),addEventListener(e,fn){events[e]=fn;},Lenis:class{constructor(options){this.options=options;instances.push(this);}destroy(){this.destroyed=true;}stop(){this.stopped=true;}start(){this.stopped=false;}}};
 const saved=[...preferences];
 vm.runInNewContext(fs.readFileSync('dist/smooth-scroll.js','utf8'),{window,document,MutationObserver:class{constructor(fn){mutation=fn;}observe(){}}});
 return {instances,preferences:saved,events,setDialog(value){dialog=value;mutation();}};
}
test('desktop has gentle inertia while nested interfaces remain native',()=>{
 const s=setup();assert.equal(s.instances.length,1);const o=s.instances[0].options;
 assert.ok(o.lerp>0&&o.lerp<.1);assert.equal(o.syncTouch,false);assert.equal(o.wheelMultiplier,1);
 assert.equal(o.prevent({closest:()=>({})}),true);assert.equal(o.prevent({closest:()=>null}),false);
});
test('touch devices and reduced-motion visitors retain native scroll',()=>{
 assert.equal(setup({desktop:false}).instances.length,0);assert.equal(setup({reduced:true}).instances.length,0);
 const s=setup();s.preferences[0].matches=true;s.preferences[0].change();assert.equal(s.instances[0].destroyed,true);
});
test('modal opening stops page inertia and browser history restores one instance',()=>{
 const s=setup();s.setDialog(true);assert.equal(s.instances[0].stopped,true);s.setDialog(false);assert.equal(s.instances[0].stopped,false);
 s.events.pagehide();assert.equal(s.instances[0].destroyed,true);s.events.pageshow({persisted:true});assert.equal(s.instances.length,2);
});
