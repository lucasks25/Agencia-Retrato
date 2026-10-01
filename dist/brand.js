(() => {
  const intro=document.querySelector('.brand-intro');
  const preference=window.matchMedia('(prefers-reduced-motion: reduce)');
  if(!intro||preference.matches)return;
  let timer=0;
  function dismiss(){
    clearTimeout(timer);intro.hidden=true;
    document.removeEventListener('pointerdown',dismiss,true);
    document.removeEventListener('keydown',dismiss,true);
  }
  intro.hidden=false;
  document.addEventListener('pointerdown',dismiss,true);
  document.addEventListener('keydown',dismiss,true);
  preference.addEventListener('change',dismiss);
  window.addEventListener('pageshow',event=>{if(event.persisted)dismiss();});
  timer=setTimeout(dismiss,2700);
})();
