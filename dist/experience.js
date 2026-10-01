/* Deliberate service choices and customer stories, with native HTML fallbacks. */
(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const track = document.querySelector('.reviews-track');
  if (track) {
    const controls = document.querySelector('.reviews-controls');
    const previous = controls.querySelector('[data-reviews-prev]');
    const next = controls.querySelector('[data-reviews-next]');
    controls.hidden = false;
    track.tabIndex = 0;
    function updateControls() {
      previous.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
    }
    function move(direction) {
      const first = track.querySelector('.review-card');
      const gap = parseFloat(getComputedStyle(track).columnGap) || 20;
      track.scrollBy({left: direction * (first.getBoundingClientRect().width + gap), behavior: reduced.matches ? 'instant' : 'smooth'});
    }
    previous.addEventListener('click', () => move(-1));
    next.addEventListener('click', () => move(1));
    track.addEventListener('scroll', updateControls, {passive:true});
    window.addEventListener('resize', updateControls, {passive:true});
    updateControls();
  }
  const dialog = document.querySelector('#review-dialog');
  if (dialog && typeof dialog.showModal === 'function') {
    let opener;
    const content = dialog.querySelector('.review-dialog-content');
    document.querySelectorAll('[data-review-open]').forEach(trigger => {
      trigger.setAttribute('aria-haspopup', 'dialog');
      trigger.addEventListener('click', event => {
        event.preventDefault();
        opener = trigger;
        const story = trigger.parentElement.querySelector('.review-full-body').cloneNode(true);
        const person = story.querySelector('.review-person h3').textContent;
        content.replaceChildren(story);
        dialog.setAttribute('aria-label', `Avaliação de ${person}`);
        dialog.showModal();
        document.body.classList.add('dialog-open');
        dialog.scrollTop = 0;
      });
    });
    dialog.querySelector('[data-review-close]').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      if (event.target === dialog) {
        const bounds = dialog.getBoundingClientRect();
        if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
      }
    });
    dialog.addEventListener('close', () => {
      if (!document.querySelector('#planner-dialog')?.open && !document.querySelector('#destination-dialog')?.open) document.body.classList.remove('dialog-open');
      opener?.focus({preventScroll:true});
    });
  }
  document.querySelectorAll('.chip-tabs').forEach(tablist => {
    const tabs = [...tablist.querySelectorAll('[role=tab]')];
    function select(tab, focus = false) {
      tabs.forEach(item => {
        const active = item === tab;
        item.setAttribute('aria-selected', String(active));
        item.tabIndex = active ? 0 : -1;
        document.getElementById(item.getAttribute('aria-controls')).hidden = !active;
      });
      if (focus) tab.focus();
    }
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => select(tab));
      tab.addEventListener('keydown', event => {
        let target;
        if (event.key === 'ArrowRight') target = tabs[(index + 1) % tabs.length];
        if (event.key === 'ArrowLeft') target = tabs[(index + tabs.length - 1) % tabs.length];
        if (event.key === 'Home') target = tabs[0];
        if (event.key === 'End') target = tabs[tabs.length - 1];
        if (target) {event.preventDefault();select(target,true);}
      });
    });
    select(tabs.find(tab => tab.getAttribute('aria-selected') === 'true') || tabs[0]);
  });
  const index = document.querySelector('.legal-index');
  if (index) {
    const mobile = window.matchMedia('(max-width: 900px)');
    index.open = !mobile.matches;
    mobile.addEventListener('change', event => {index.open = !event.matches;});
    const links = [...index.querySelectorAll('a')];
    links.forEach(link => link.addEventListener('click', () => {if (mobile.matches) index.open = false;}));
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        const visible = entries.filter(entry => entry.isIntersecting).sort((a,b) => a.boundingClientRect.top-b.boundingClientRect.top);
        if (!visible.length) return;
        const id = visible[0].target.id;
        links.forEach(link => {
          if (link.hash === `#${id}`) link.setAttribute('aria-current','location');
          else link.removeAttribute('aria-current');
        });
      }, {rootMargin:'-100px 0px -50% 0px',threshold:0});
      document.querySelectorAll('.legal-document h2[id]').forEach(heading => observer.observe(heading));
    }
  }
})();
