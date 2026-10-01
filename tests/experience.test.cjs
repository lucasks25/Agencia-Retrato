const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
class Element {
  constructor(){this.events={};this.attrs={};this.classList={values:new Set(),add:(v)=>this.classList.values.add(v),toggle:(v,on)=>on?this.classList.values.add(v):this.classList.values.delete(v)};this.hidden=false;this.disabled=true;}
  addEventListener(event,fn){this.events[event]=fn;}
  fire(event,args={}){this.events[event]?.(args);}
  setAttribute(key,value){this.attrs[key]=value;}
}
function experience(){
  const buttons=Array.from({length:4},()=>new Element());
  const panels=Array.from({length:4},()=>new Element());
  const photos=Array.from({length:4},()=>new Element());
  const section=new Element();section.querySelectorAll=s=>s==='[data-experience-choice]'?buttons:s==='[data-experience-copy]'?panels:s==='[data-experience-photo]'?photos:[];
  const document={querySelector:s=>s==='[data-experience-gallery]'?section:null,querySelectorAll:()=>[]};
  vm.runInNewContext(fs.readFileSync('dist/experience.js','utf8'),{document,window:{matchMedia:()=>({matches:false})}});
  return {buttons,panels,photos};
}
test('each travel detail selects its corresponding image and description on click',()=>{
 const {buttons,panels,photos}=experience();
 for(let index=0;index<4;index++){
  buttons[index].fire('click');
  assert.equal(buttons[index].attrs['aria-expanded'],'true');
  assert.equal(panels.filter(p=>!p.hidden).length,1);assert.equal(panels[index].hidden,false);
  assert.equal(photos.filter(p=>p.classList.values.has('is-active')).length,1);assert.ok(photos[index].classList.values.has('is-active'));
 }
});
test('mouse hover and keyboard focus select a detail; touch pointer entry does not',()=>{
 const {buttons}=experience();
 buttons[1].fire('pointerenter',{pointerType:'mouse'});assert.equal(buttons[1].attrs['aria-expanded'],'true');
 buttons[2].fire('pointerenter',{pointerType:'touch'});assert.equal(buttons[1].attrs['aria-expanded'],'true');
 buttons[3].fire('focus');assert.equal(buttons[3].attrs['aria-expanded'],'true');
});
function brand(storage){
 const intro={hidden:true,querySelector:()=>null};
 const document={querySelector:()=>intro,addEventListener(){},removeEventListener(){}};
 const window={sessionStorage:storage,matchMedia:()=>({matches:false,addEventListener(){}}),addEventListener(){}};
 vm.runInNewContext(fs.readFileSync('dist/brand.js','utf8'),{document,window,setTimeout(){},clearTimeout(){}});
 return intro;
}
test('the airplane opening is shown once per session across page loads',()=>{
 const values=new Map();const storage={getItem:k=>values.get(k),setItem:(k,v)=>values.set(k,v)};
 assert.equal(brand(storage).hidden,false);assert.equal(brand(storage).hidden,true);
});
test('unavailable session storage does not break the page',()=>{
 const storage={getItem(){throw Error('blocked');},setItem(){throw Error('blocked');}};
 assert.doesNotThrow(()=>brand(storage));
});
test('the plane crosses from outside the left edge to outside the right edge',()=>{
 const aircraft={style:{setProperty(){}}};const frame={getBoundingClientRect:()=>({width:440,height:240})};
 const intro={hidden:true,querySelector:s=>s==='.brand-flyby'?aircraft:frame,style:{setProperty(){}}};
 const document={querySelector:()=>intro,addEventListener(){},removeEventListener(){}};
 const window={innerWidth:1440,innerHeight:900,sessionStorage:{getItem(){},setItem(){}},matchMedia:()=>({matches:false,addEventListener(){}}),addEventListener(){}};
 vm.runInNewContext(fs.readFileSync('dist/brand.js','utf8'),{document,window,setTimeout(){},clearTimeout(){}});
 const path=aircraft.style.offsetPath;
 const straight=path.match(/^path\("M ([-\d.]+) ([-\d.]+) L ([-\d.]+) ([-\d.]+)"\)$/);
 assert.ok(straight,'a single uninterrupted flight replaces the loop');
 assert.ok(Number(straight[1]) < -window.innerWidth/2);assert.ok(Number(straight[3]) > window.innerWidth/2);
});
