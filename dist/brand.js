(() => {
  const intro=document.querySelector('.brand-intro');
  const preference=window.matchMedia('(prefers-reduced-motion: reduce)');
  if(!intro||preference.matches)return;
  // Replay the signature on every homepage arrival, including reloads.
  if(document.body?.classList.contains('inner-page'))return;
  let timer=0,openingTime=4500;
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
    const startY=60,endY=-70;
    const control1X=startX*.36,control2X=endX*.28;
    aircraft.style.offsetPath=`path("M ${startX} ${startY} C ${control1X} 15 ${control2X} -110 ${endX} ${endY}")`;
    const distance=Math.hypot(endX-startX,endY-startY);
    const flightSeconds=Math.max(3.1,Math.min(4.4,distance/550));
    aircraft.style.setProperty('--brand-flight-duration',`${flightSeconds}s`);
    // Reveal begins only after the aircraft has crossed the viewport.
    const revealDelay=flightSeconds+.25,revealSeconds=1.1;
    intro.style.setProperty('--brand-reveal-delay',`${revealDelay}s`);
    intro.style.setProperty('--brand-reveal-duration',`${revealSeconds}s`);
    openingTime=(revealDelay+revealSeconds+.15)*1000;
  }
  document.addEventListener('pointerdown',dismiss,true);
  document.addEventListener('keydown',dismiss,true);
  preference.addEventListener('change',dismiss);
  window.addEventListener('pageshow',event=>{if(event.persisted)dismiss();});
  timer=setTimeout(dismiss,openingTime);
})();
