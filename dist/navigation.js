(() => {
  const menus=[...document.querySelectorAll('.desktop-nav .nav-menu')];
  const finePointer=window.matchMedia('(hover: hover) and (pointer: fine)');
  const desktop=window.matchMedia('(min-width: 1001px)');
  const controllers=menus.map(menu=>{
    const trigger=menu.querySelector('.nav-disclosure');
    const panel=menu.querySelector('.nav-panel');
    let closeTimer=0;
    let lastPointerType='mouse';
    function setOpen(open){
      clearTimeout(closeTimer);
      if(open)controllers.forEach(other=>{if(other.menu!==menu)other.setOpen(false);});
      panel.hidden=!open;
      trigger.setAttribute('aria-expanded',String(open));
    }
    trigger.addEventListener('pointerdown',event=>{lastPointerType=event.pointerType||'mouse';});
    trigger.addEventListener('click',event=>{
      const pointerType=event.pointerType||lastPointerType;
      setOpen(event.detail>0&&pointerType==='mouse'&&finePointer.matches?true:panel.hidden);
    });
    trigger.addEventListener('keydown',event=>{
      if(event.key!=='ArrowDown'&&event.key!=='ArrowUp')return;
      event.preventDefault();setOpen(true);
      const links=panel.querySelectorAll('a');
      links[event.key==='ArrowDown'?0:links.length-1]?.focus();
    });
    menu.addEventListener('pointerenter',event=>{if(event.pointerType==='mouse'&&finePointer.matches)setOpen(true);});
    menu.addEventListener('pointerleave',()=>{closeTimer=setTimeout(()=>{if(!menu.contains(document.activeElement))setOpen(false);},180);});
    menu.addEventListener('focusout',event=>{if(!menu.contains(event.relatedTarget))setOpen(false);});
    return {menu,trigger,panel,setOpen};
  });
  document.addEventListener('click',event=>controllers.forEach(item=>{if(!item.menu.contains(event.target))item.setOpen(false);}));
  document.addEventListener('keydown',event=>{
    if(event.key!=='Escape')return;
    const open=controllers.find(item=>!item.panel.hidden);
    if(open){event.preventDefault();open.setOpen(false);open.trigger.focus();}
  });
  desktop.addEventListener('change',()=>controllers.forEach(item=>item.setOpen(false)));
})();
