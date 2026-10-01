const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
class Element {
  constructor(){this.events={};this.attrs={};this.hidden=true;this.links=[new ElementLink(),new ElementLink()];}
  addEventListener(type,fn){(this.events[type]??=[]).push(fn);}
  fire(type,event={}){for(const fn of this.events[type]||[])fn({target:this,...event});}
  setAttribute(k,v){this.attrs[k]=v;}
  getAttribute(k){return this.attrs[k];}
  contains(el){return el===this||el===this.trigger||el===this.panel||this.panel?.links.includes(el);}
  querySelector(s){return s==='.nav-disclosure'?this.trigger:this.panel;}
  querySelectorAll(){return this.links;}
  focus(){this.focused=true;}
}
class ElementLink {focus(){this.focused=true;}}
function setup(){
  const menus=[new Element(),new Element()];
  for(const menu of menus){menu.trigger=new Element();menu.panel=new Element();}
  const document=new Element();document.querySelectorAll=()=>menus;
  const timers=new Map();let id=0;
  const window={matchMedia:()=>({matches:true,addEventListener(){}})};
  vm.runInNewContext(fs.readFileSync('dist/navigation.js','utf8'),{document,window,setTimeout(fn){timers.set(++id,fn);return id;},clearTimeout(id){timers.delete(id);}});
  return {menus,document,flush(){for(const fn of timers.values())fn();timers.clear();}};
}
test('hover opens both navigation groups and closes the previous group',()=>{
  const {menus:[destinations,services]}=setup();
  destinations.fire('pointerenter',{pointerType:'mouse'});assert.equal(destinations.panel.hidden,false);
  services.fire('pointerenter',{pointerType:'mouse'});assert.equal(services.panel.hidden,false);assert.equal(destinations.panel.hidden,true);
});
test('keyboard arrows open the panel and Escape restores focus',()=>{
  const {menus:[menu],document}=setup();
  menu.trigger.fire('keydown',{key:'ArrowDown',preventDefault(){}});assert.ok(menu.panel.links[0].focused);
  document.fire('keydown',{key:'Escape',preventDefault(){}});assert.ok(menu.panel.hidden);assert.ok(menu.trigger.focused);
});
test('real touch clicks toggle on a hybrid device, while keyboard focus keeps the panel open',()=>{
  const {menus:[menu],document,flush}=setup();
  menu.fire('pointerenter',{pointerType:'touch'});assert.ok(menu.panel.hidden);
  menu.trigger.fire('pointerdown',{pointerType:'touch'});
  menu.trigger.fire('click',{detail:1});assert.equal(menu.panel.hidden,false);
  document.activeElement=menu.panel.links[0];menu.fire('pointerleave');flush();assert.equal(menu.panel.hidden,false);
  menu.trigger.fire('pointerdown',{pointerType:'touch'});
  menu.trigger.fire('click',{detail:1});assert.ok(menu.panel.hidden);
});
