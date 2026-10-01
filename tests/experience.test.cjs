const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
class Element {
  constructor(){this.events={};this.attrs={};this.classList={values:new Set(),add:(v)=>this.classList.values.add(v),toggle:(v,on)=>on?this.classList.values.add(v):this.classList.values.delete(v)};this.hidden=false;this.disabled=true;}
  addEventListener(event,fn){this.events[event]=fn;}
  fire(event,args={}){this.events[event]?.(args);}
  setAttribute(key,value){this.attrs[key]=value;}
  focus(){this.focused=true;this.fire('focus');}
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
  assert.equal(buttons[index].attrs['aria-selected'],'true');
  assert.equal(panels.filter(p=>!p.hidden).length,1);assert.equal(panels[index].hidden,false);
  assert.equal(photos.filter(p=>p.classList.values.has('is-active')).length,1);assert.ok(photos[index].classList.values.has('is-active'));
 }
});
test('mouse hover and keyboard focus select a detail; touch pointer entry does not',()=>{
 const {buttons}=experience();
 buttons[1].fire('pointerenter',{pointerType:'mouse'});assert.equal(buttons[1].attrs['aria-selected'],'true');
 buttons[2].fire('pointerenter',{pointerType:'touch'});assert.equal(buttons[1].attrs['aria-selected'],'true');
 buttons[3].fire('focus');assert.equal(buttons[3].attrs['aria-selected'],'true');
});
test('chapter controls support arrow keys, Home and End with roving keyboard focus',()=>{
 const {buttons}=experience();
 buttons[0].fire('keydown',{key:'ArrowRight',preventDefault(){}});
 assert.equal(buttons[1].attrs['aria-selected'],'true');assert.equal(buttons[1].tabIndex,0);assert.ok(buttons[1].focused);
 buttons[1].fire('keydown',{key:'End',preventDefault(){}});assert.equal(buttons[3].attrs['aria-selected'],'true');
 buttons[3].fire('keydown',{key:'ArrowRight',preventDefault(){}});assert.equal(buttons[0].attrs['aria-selected'],'true');
 buttons[2].fire('keydown',{key:'Home',preventDefault(){}});assert.equal(buttons[0].attrs['aria-selected'],'true');
});
function brand(internal=false){
 const intro={hidden:true,querySelector:()=>null};
 const document={body:{classList:{contains:()=>internal}},querySelector:()=>intro,addEventListener(){},removeEventListener(){}};
 const window={matchMedia:()=>({matches:false,addEventListener(){}}),addEventListener(){}};
 vm.runInNewContext(fs.readFileSync('dist/brand.js','utf8'),{document,window,setTimeout(){},clearTimeout(){}});
 return intro;
}
test('the airplane opening returns on each fresh homepage load or reload',()=>{
 assert.equal(brand().hidden,false);assert.equal(brand().hidden,false);
});
test('internal navigation opens the page without the introductory curtain',()=>{
 assert.equal(brand(true).hidden,true);
});
test('the plane crosses from outside the left edge to outside the right edge',()=>{
 const aircraft={style:{setProperty(){}}};const frame={getBoundingClientRect:()=>({width:440,height:240})};
 const intro={hidden:true,querySelector:s=>s==='.brand-flyby'?aircraft:frame,style:{setProperty(){}}};
 const document={querySelector:()=>intro,addEventListener(){},removeEventListener(){}};
 const window={innerWidth:1440,innerHeight:900,sessionStorage:{getItem(){},setItem(){}},matchMedia:()=>({matches:false,addEventListener(){}}),addEventListener(){}};
 vm.runInNewContext(fs.readFileSync('dist/brand.js','utf8'),{document,window,setTimeout(){},clearTimeout(){}});
 const path=aircraft.style.offsetPath;
 const curve=path.match(/^path\("M ([-\d.]+) ([-\d.]+) C ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"\)$/);
 assert.ok(curve,'the flight follows one continuous curve');
 const [sx,sy,c1x,c1y,c2x,c2y,ex,ey]=curve.slice(1).map(Number);
 assert.ok(sx < -window.innerWidth/2);assert.ok(ex > window.innerWidth/2);
 let previousX=sx,previousAngle;
 for(let step=0;step<=40;step++){
  const t=step/40,u=1-t;
  const x=u*u*u*sx+3*u*u*t*c1x+3*u*t*t*c2x+t*t*t*ex;
  const y=u*u*u*sy+3*u*u*t*c1y+3*u*t*t*c2y+t*t*t*ey;
  const dx=3*u*u*(c1x-sx)+6*u*t*(c2x-c1x)+3*t*t*(ex-c2x);
  const dy=3*u*u*(c1y-sy)+6*u*t*(c2y-c1y)+3*t*t*(ey-c2y);
  const angle=Math.atan2(dy,dx);
  assert.ok(x>=previousX,'the plane must never turn back');
  assert.ok(Math.abs(y)<130,'the bend must remain subtle');
  if(previousAngle!==undefined)assert.ok(Math.abs(angle-previousAngle)<.05,'heading must change gently');
  previousX=x;previousAngle=angle;
 }

});
