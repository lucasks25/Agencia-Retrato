(() => {
  if(typeof window.Lenis!=='function')return;
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  const desktop=window.matchMedia('(hover: hover) and (pointer: fine)');
  let motion=null,blocked=false;
  const nativeArea='dialog,.mobile-nav,.reviews-track,.legal-sidebar,.journal-toc nav,textarea,select,input,[data-lenis-prevent]';
  function syncBlocked(){
    const next=document.body.classList.contains('menu-open')||!!document.querySelector('dialog[open]');
    if(motion&&next!==blocked){if(next)motion.stop();else motion.start();}
    blocked=next;
  }
  function configure(){
    motion?.destroy();motion=null;blocked=false;
    if(reduced.matches||!desktop.matches)return;
    motion=new window.Lenis({
      autoRaf:true,lerp:.075,smoothWheel:true,syncTouch:false,
      wheelMultiplier:1,anchors:{offset:-96},
      prevent:node=>!!node.closest?.(nativeArea)
    });
    syncBlocked();
  }
  reduced.addEventListener('change',configure);
  desktop.addEventListener('change',configure);
  new MutationObserver(syncBlocked).observe(document.body,{attributes:true,subtree:true,attributeFilter:['class','open']});
  window.addEventListener('pagehide',()=>{motion?.destroy();motion=null;});
  window.addEventListener('pageshow',event=>{if(event.persisted)configure();});
  configure();
})();
