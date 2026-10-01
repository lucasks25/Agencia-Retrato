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
  const aircraft=intro.querySelector('.brand-flyby');
  const frame=intro.querySelector('.brand-intro-frame');
  if(aircraft&&frame){
    const rect=frame.getBoundingClientRect();
    const rx=Math.min(rect.width/2+35,window.innerWidth/2-55);
    const ry=rect.height/2+30,k=.55228475;
    const endX=window.innerWidth/2+180,endY=-window.innerHeight/2-150;
    const path=`M 0 ${-ry} C ${rx*k} ${-ry} ${rx} ${-ry*k} ${rx} 0 C ${rx} ${ry*k} ${rx*k} ${ry} 0 ${ry} C ${-rx*k} ${ry} ${-rx} ${ry*k} ${-rx} 0 C ${-rx} ${-ry*k} ${-rx*k} ${-ry} 0 ${-ry} C ${rx*.8} ${-ry} ${endX*.7} ${endY*.8} ${endX} ${endY}`;
    aircraft.style.offsetPath=`path("${path}")`;
    const h=((rx-ry)/(rx+ry))**2;
    const orbit=Math.PI*(rx+ry)*(1+3*h/(10+Math.sqrt(4-3*h)));
    let departure=0,previous={x:0,y:-ry};
    for(let i=1;i<=40;i++){
      const t=i/40,u=1-t;
      const point={x:3*u*u*t*rx*.8+3*u*t*t*endX*.7+t*t*t*endX,y:-u*u*u*ry-3*u*u*t*ry+3*u*t*t*endY*.8+t*t*t*endY};
      departure+=Math.hypot(point.x-previous.x,point.y-previous.y);previous=point;
    }
    aircraft.style.setProperty('--brand-orbit-end',`${orbit/(orbit+departure)*100}%`);
  }
  document.addEventListener('pointerdown',dismiss,true);
  document.addEventListener('keydown',dismiss,true);
  preference.addEventListener('change',dismiss);
  window.addEventListener('pageshow',event=>{if(event.persisted)dismiss();});
  timer=setTimeout(dismiss,3450);
})();
