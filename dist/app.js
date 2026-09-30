const header = document.querySelector('.header');
const menuButton = document.querySelector('.menu-button');
const mobileNav = document.querySelector('.mobile-nav');
function setMenu(open) {
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
  mobileNav.hidden = !open;
  document.body.classList.toggle('menu-open', open);
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
function updateHeader() { header.classList.toggle('scrolled', window.scrollY > 50); }
window.addEventListener('scroll', updateHeader, {passive:true});
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
