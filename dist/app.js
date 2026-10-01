const header = document.querySelector('.header');
const menuButton = document.querySelector('.menu-button');
const mobileNav = document.querySelector('.mobile-nav');
function setMenu(open) {
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
  mobileNav.hidden = !open;
  document.body.classList.toggle('menu-open', open);
  document.querySelector('main').inert = open;
  document.querySelector('footer').inert = open;
  const floatingContact = document.querySelector('.contact-float');
  if (floatingContact) floatingContact.inert = open;
  if(!open){const destinations=mobileNav.querySelector('.mobile-destinations');if(destinations)destinations.open=false;}
}
menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
mobileNav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
    setMenu(false);
    menuButton.focus();
  }
});
const desktopWidth = window.matchMedia('(min-width: 1001px)');
desktopWidth.addEventListener('change', event => { if (event.matches) setMenu(false); });
let headerScrolled;
function updateHeader(y=window.scrollY) {
  const scrolled=(document.body.classList.contains('inner-page') && !document.body.classList.contains('photo-page')) || y > 50;
  if(scrolled!==headerScrolled){header.classList.toggle('scrolled',scrolled);headerScrolled=scrolled;}
}
updateHeader();
const cards = [...document.querySelectorAll('.destination-card')];
document.querySelectorAll('.filter').forEach(button => button.addEventListener('click', () => {
  const selected = button.dataset.filter;
  document.querySelectorAll('.filter').forEach(filter => {
    const active = filter === button;
    filter.classList.toggle('active', active);
    filter.setAttribute('aria-pressed', String(active));
  });
  cards.forEach(card => { card.hidden = selected !== 'todos' && card.dataset.region !== selected; });
  const count = cards.filter(card => !card.hidden).length;
  const labels = {brasil:'inspirações brasileiras', mundo:'inspirações pelo mundo', todos:'inspirações para sua próxima viagem'};
  document.querySelector('#destination-count').textContent = `${count} ${labels[selected]}`;
}));

const detailDialog = document.querySelector('#destination-dialog');
const plannerDialog = document.querySelector('#planner-dialog');
const tripDestination = document.querySelector('#trip-destination');
let plannerStep = 0;
let lastTrigger = null;
let selectedDestination = '';
const destinationDetails = [
  {name:'Milagres', choice:'Milagres, Alagoas', location:'ALAGOAS · BRASIL', description:'A Praia do Marceneiro, na Costa dos Corais, é o cenário do NANNAI Milagres. Uma inspiração para combinar dias de praia, hospedagem e celebração.', facts:[['Um lugar','Praia do Marceneiro, Alagoas'],['Uma inspiração','NANNAI Milagres'],['Planejamento','Datas, hospedagem e deslocamentos sob consulta']]},
  {name:'Praia do Preá', choice:'Praia do Preá, Ceará', location:'CEARÁ · BRASIL', description:'O Casana Hotel reúne sete bangalôs na Praia do Preá. Privacidade e hospitalidade em pequena escala, com praia, bem-estar e kitesurf como parte da experiência.', facts:[['Um lugar','Praia do Preá, próximo a Jericoacoara'],['Uma inspiração','Casana Hotel'],['Seu ritmo','Descanso, gastronomia e atividades no mar']]},
  {name:'Rio de Janeiro', choice:'Rio de Janeiro', location:'RIO DE JANEIRO · BRASIL', description:'Descubra o Rio também pelos restaurantes e bares que ajudam a contar sua história. A curadoria da Retrato reúne endereços para incluir a gastronomia no desenho da viagem.', facts:[['Um lugar','Rio de Janeiro'],['Uma inspiração','Restaurantes e bares selecionados pela Retrato'],['Seu ritmo','Gastronomia, cultura e descobertas urbanas']]},
  {name:'Maldivas', choice:'Maldivas', location:'OCEANO ÍNDICO', description:'Nas Maldivas, a ilha escolhida define o estilo da viagem. Resort, tipo de villa, regime de refeições e traslados precisam conversar com o seu perfil.', facts:[['Um lugar','Arquipélago das Maldivas'],['Uma inspiração','Villas na praia ou sobre a água'],['Planejamento','Ilha, hospedagem e traslados escolhidos em conjunto']]},
  {name:'Roma', choice:'Roma, Itália', location:'ITÁLIA', description:'O Anantara Palazzo Naiadi é uma inspiração para viver Roma a partir da Piazza della Repubblica. História e hospitalidade encontram a cidade em um endereço central.', facts:[['Um lugar','Roma, Itália'],['Uma inspiração','Anantara Palazzo Naiadi'],['Seu ritmo','História, arquitetura e gastronomia']]}
];
function unlockPage() {
  if (!detailDialog.open && !plannerDialog.open) document.body.classList.remove('dialog-open');
}
function closeDestination() { detailDialog.close(); }
cards.forEach((card,index) => {
  if(!card.hasAttribute('data-destination-page'))card.setAttribute('aria-haspopup','dialog');
  card.addEventListener('click',event => {
    if(card.hasAttribute('data-destination-page'))return;
    if(event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const detail=destinationDetails[index];
    selectedDestination=detail.choice;
    lastTrigger=card;
    const img=card.querySelector('img');
    document.querySelector('#detail-image').src=img.getAttribute('src');
    document.querySelector('#detail-image').alt=img.alt;
    document.querySelector('#detail-title').textContent=detail.name;
    document.querySelector('#detail-location').textContent=detail.location;
    document.querySelector('#detail-description').textContent=detail.description;
    const facts=document.querySelector('#detail-facts');
    facts.replaceChildren();
    detail.facts.forEach(([label,value])=>{const row=document.createElement('div');const dt=document.createElement('dt');const dd=document.createElement('dd');dt.textContent=label;dd.textContent=value;row.append(dt,dd);facts.append(row);});
    document.querySelector('#detail-source').href=card.href;
    document.body.classList.add('dialog-open');
    detailDialog.showModal();
  });
});
detailDialog.querySelector('.dialog-close').addEventListener('click',closeDestination);
detailDialog.addEventListener('close',()=>{unlockPage();if(!plannerDialog.open) lastTrigger?.focus();});
function renderPlanner() {
  document.querySelectorAll('.planner-step').forEach(step=>{step.hidden=Number(step.dataset.step)!==plannerStep;});
  document.querySelectorAll('[data-progress]').forEach(step=>{step.classList.toggle('current',Number(step.dataset.progress)===plannerStep);});
  document.querySelector('#planner-back').hidden=plannerStep===0;
  document.querySelector('#planner-next').hidden=plannerStep===2;
  if(plannerStep===2) {
    const summary=document.querySelector('#trip-summary');
    summary.textContent=makeTripSummary();
    document.querySelector('.whatsapp-action').href='https://wa.me/551132880015?text='+encodeURIComponent(makeTripSummary());
    summary.setAttribute('tabindex','0');
    document.querySelector('#copy-status').textContent='';
  }
  plannerDialog.querySelector('.planner-body').scrollTop=0;
}
function openPlanner(destination='') {
  if(detailDialog.open) detailDialog.close();
  if(destination) tripDestination.value=destination;
  document.querySelector('#other-destination-field').hidden=tripDestination.value!=='Outro destino';
  plannerStep=0;
  renderPlanner();
  document.body.classList.add('dialog-open');
  plannerDialog.showModal();
  document.querySelector('#trip-destination').focus();
}
document.querySelectorAll('a[href="https://wa.me/551132880015"]').forEach(link=>{
  if(link.classList.contains('contact-float') || link.classList.contains('whatsapp-action') || link.hasAttribute('data-direct-contact')) return;
  link.setAttribute('aria-haspopup','dialog');
  link.addEventListener('click',event=>{
    if(event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();lastTrigger=mobileNav.contains(link)?menuButton:link;setMenu(false);openPlanner();
  });
});
document.querySelector('#detail-plan').addEventListener('click',()=>openPlanner(selectedDestination));
plannerDialog.querySelector('.dialog-close').addEventListener('click',()=>plannerDialog.close());
plannerDialog.addEventListener('close',()=>{unlockPage();lastTrigger?.focus();});
document.querySelector('#planner-next').addEventListener('click',()=>{
  plannerStep=Math.min(2,plannerStep+1);renderPlanner();
  plannerDialog.querySelector(`[data-step="${plannerStep}"] h3`).setAttribute('tabindex','-1');
  plannerDialog.querySelector(`[data-step="${plannerStep}"] h3`).focus();
});
document.querySelector('#planner-back').addEventListener('click',()=>{plannerStep=Math.max(0,plannerStep-1);renderPlanner();plannerDialog.querySelector(`[data-step="${plannerStep}"] h3`).setAttribute('tabindex','-1');plannerDialog.querySelector(`[data-step="${plannerStep}"] h3`).focus();});
tripDestination.addEventListener('change',()=>{document.querySelector('#other-destination-field').hidden=tripDestination.value!=='Outro destino';});
document.querySelector('#planner-form').addEventListener('submit',event=>event.preventDefault());
function makeTripSummary() {
  const destination=tripDestination.value==='Outro destino' ? document.querySelector('#trip-other').value.trim()||'Outro destino a definir' : tripDestination.value;
  const vibe=document.querySelector('input[name="vibe"]:checked').value;
  const period=document.querySelector('#trip-period').value.trim()||'Datas a definir';
  const travelers=document.querySelector('#trip-travelers').value;
  const notes=document.querySelector('#trip-notes').value.trim();
  return `Olá, Retrato! Gostaria de conversar sobre uma viagem sob medida.\n\nDestino: ${destination}\nExperiência: ${vibe}\nPeríodo: ${period}\nViajantes: ${travelers}${notes?'\nO que não pode faltar: '+notes:''}`;
}
document.querySelector('#copy-summary').addEventListener('click',async()=>{
  try {await navigator.clipboard.writeText(makeTripSummary());document.querySelector('#copy-status').textContent='Resumo copiado. Cole na conversa com a Retrato.';}
  catch {document.querySelector('#copy-status').textContent='Não foi possível copiar automaticamente. Selecione o resumo acima e copie para levar à conversa.';}
});
[detailDialog,plannerDialog].forEach(dialog=>dialog.addEventListener('click',event=>{if(event.target!==dialog)return;const r=dialog.getBoundingClientRect();if(event.clientX<r.left || event.clientX>r.right || event.clientY<r.top || event.clientY>r.bottom)dialog.close();}));
document.querySelectorAll('[data-plan-destination]').forEach(button=>button.addEventListener('click',()=>{lastTrigger=button;openPlanner(button.dataset.planDestination||'');}));
document.querySelectorAll('[data-plan-vibe]').forEach(button=>button.addEventListener('click',()=>{
  const value=button.dataset.planVibe;
  document.querySelectorAll('input[name="vibe"]').forEach(input=>{input.checked=input.value===value;});
  lastTrigger=button;openPlanner();
}));
document.querySelectorAll('[data-plan-service]').forEach(button=>button.addEventListener('click',()=>{
  lastTrigger=button;openPlanner();
  document.querySelector('#trip-notes').value='Gostaria de informações sobre '+button.dataset.planService+'.';
}));
document.querySelectorAll('a[data-local]').forEach(link=>link.removeAttribute('target'));
document.querySelectorAll('.desktop-nav>a,.nav-panel a,.mobile-nav a').forEach(link=>{
  if(new URL(link.href,location.href).pathname.replace(/\/$/,'')===location.pathname.replace(/\/$/,''))link.setAttribute('aria-current','page');
});
const archive=document.querySelector('.archive');
if(archive){
  const search=document.querySelector('#journal-search');
  const items=[...document.querySelectorAll('.archive .archive-card')];
  let category=archive.dataset.initialCategory||'';
  let visibleLimit=9;
  function normalizeSearch(value){return value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim();}
  function updateArchive(){
    const query=normalizeSearch(search.value);
    const matches=items.filter(card=>(!category||card.dataset.category===category)&&query.split(/\s+/).every(term=>(card.dataset.search||'').includes(term)));
    const visible=new Set(matches.slice(0,visibleLimit));
    items.forEach(card=>{card.hidden=!visible.has(card);});
    document.querySelectorAll('[data-journal-category]').forEach(button=>{button.setAttribute('aria-pressed',String(button.dataset.journalCategory===category));});
    document.querySelector('#journal-count').textContent=matches.length===1?'1 história encontrada':`${matches.length} histórias encontradas`;
    document.querySelector('#journal-more').hidden=visibleLimit>=matches.length;
    document.querySelector('#journal-empty').hidden=matches.length>0;
    document.querySelector('#journal-clear').hidden=!category&&!query;
  }
  search.addEventListener('input',()=>{visibleLimit=9;updateArchive();});
  document.querySelectorAll('[data-journal-category]').forEach(button=>button.addEventListener('click',()=>{category=button.dataset.journalCategory;visibleLimit=9;updateArchive();}));
  document.querySelector('#journal-clear').addEventListener('click',()=>{category='';search.value='';visibleLimit=9;updateArchive();search.focus();});
  document.querySelector('#journal-more').addEventListener('click',()=>{
    const previousVisible=items.filter(item=>!item.hidden);
    visibleLimit+=9;updateArchive();
    const firstNew=items.find(item=>!item.hidden&&!previousVisible.includes(item));
    firstNew?.focus({preventScroll:true});
  });
  updateArchive();
}

// Motion supports the content; it never blocks navigation or waits for a preload.
const reduceMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
const revealTargets=document.querySelectorAll('.intro-copy,.intro-mosaic,.section-heading,.experience-heading,.benefits article,.journey-heading,.journey-photo,.steps article,.journal-card,.page-heading h1,.page-intro,.split-editorial>div,.service-grid article,.intent-card,.article-body>.article-lead,.destination-editorial>div,.destination-stay>div,.destination-highlights article');
if(!reduceMotion.matches && 'IntersectionObserver' in window){
  const observer=new IntersectionObserver(entries=>{
    entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target);}});
  },{threshold:.08,rootMargin:'0px 0px -25px 0px'});
  revealTargets.forEach((element,index)=>{element.classList.add('reveal');element.style.setProperty('--reveal-delay',`${Math.min(index%3,2)*75}ms`);observer.observe(element);});
  reduceMotion.addEventListener('change',event=>{if(event.matches){revealTargets.forEach(element=>element.classList.add('is-visible'));observer.disconnect();}});
}
const readingProgress=document.createElement('div');readingProgress.className='reading-progress';readingProgress.setAttribute('aria-hidden','true');document.body.append(readingProgress);
const heroImage=document.querySelector('.hero-image,.destination-hero>img,.photo-heading>img');
let scrollFrame=0,scrollMax=0,viewportHeight=0,viewportWidth=0,heroInView=true,lastProgress=-1,lastParallax;
function measureMotion(){
  viewportHeight=window.innerHeight;viewportWidth=window.innerWidth;
  scrollMax=Math.max(0,document.documentElement.scrollHeight-viewportHeight);
  scheduleMotion();
}
function updateMotion(){
  scrollFrame=0;
  const y=Math.max(0,window.scrollY);
  const progress=scrollMax>0?Math.min(1,y/scrollMax):0;
  if(progress!==lastProgress){readingProgress.style.transform=`scaleX(${progress})`;lastProgress=progress;}
  updateHeader(y);
  if(heroImage){
    const parallax=!heroImage.closest('.has-water-motion')&&!reduceMotion.matches&&viewportWidth>760;
    if(parallax!==lastParallax){heroImage.classList.toggle('has-scroll-parallax',parallax);lastParallax=parallax;}
    if(parallax&&heroInView)heroImage.style.translate=`0 ${Math.min(y*.035,24)}px`;
    else if(!parallax)heroImage.style.translate='0 0';
  }
}
function scheduleMotion(){if(!scrollFrame)scrollFrame=requestAnimationFrame(updateMotion);}
window.addEventListener('scroll',scheduleMotion,{passive:true});
window.addEventListener('resize',measureMotion,{passive:true});
window.addEventListener('pageshow',measureMotion);
reduceMotion.addEventListener('change',scheduleMotion);
if(typeof ResizeObserver!=='undefined')new ResizeObserver(measureMotion).observe(document.body);
else window.addEventListener('load',measureMotion,{once:true});
if(heroImage&&'IntersectionObserver' in window)new IntersectionObserver(([entry])=>{heroInView=entry.isIntersecting;scheduleMotion();}).observe(heroImage);
measureMotion();
const destinationSticky=document.querySelector('.destination-sticky');
if(destinationSticky && 'IntersectionObserver' in window){
  const hero=document.querySelector('.destination-hero');
  const footer=document.querySelector('.footer');
  let belowHero=false;let atFooter=false;
  function setSticky(){destinationSticky.classList.toggle('shown',belowHero&&!atFooter);destinationSticky.inert=!belowHero||atFooter;}
  const heroObserver=new IntersectionObserver(([entry])=>{belowHero=!entry.isIntersecting;setSticky();},{threshold:0});heroObserver.observe(hero);
  const footerObserver=new IntersectionObserver(([entry])=>{atFooter=entry.isIntersecting;setSticky();},{threshold:0});footerObserver.observe(footer);
}
