(() => {
  const intro=document.querySelector('.brand-intro');
  const preference=window.matchMedia('(prefers-reduced-motion: reduce)');
  if(!intro||preference.matches)return;
  // Replay the signature on every homepage arrival, including reloads.
  if(document.body?.classList.contains('inner-page'))return;
  let timer=0,openingTime=3850;
  function dismiss(){
    clearTimeout(timer);intro.hidden=true;
    document.removeEventListener('pointerdown',dismiss,true);
    document.removeEventListener('keydown',dismiss,true);
  }
  intro.hidden=false;
  const aircraft=intro.querySelector('.brand-flyby');
  if(aircraft){
    const startX=-window.innerWidth/2-160;
    const endX=window.innerWidth/2+160;
    const startY=30,endY=-35;
    aircraft.style.offsetPath=`path("M ${startX} ${startY} L ${endX} ${endY}")`;
    const distance=Math.hypot(endX-startX,endY-startY);
    const flightSeconds=Math.max(2.8,Math.min(4.2,distance/600));
    aircraft.style.setProperty('--brand-flight-duration',`${flightSeconds}s`);
    intro.style.setProperty('--brand-opening-duration',`${flightSeconds+.75}s`);
    openingTime=(flightSeconds+.8)*1000;
  }
  document.addEventListener('pointerdown',dismiss,true);
  document.addEventListener('keydown',dismiss,true);
  preference.addEventListener('change',dismiss);
  window.addEventListener('pageshow',event=>{if(event.persisted)dismiss();});
  timer=setTimeout(dismiss,openingTime);
})();
