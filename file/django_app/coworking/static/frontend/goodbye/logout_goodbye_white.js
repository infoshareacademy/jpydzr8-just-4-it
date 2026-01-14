(function () {
  const body = document.body;
  const intro = document.querySelector('.goodbye-intro');
  const app = document.querySelector('.goodbye-app');
  const target = document.getElementById('gbText');
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const WORD = (target?.dataset.text || 'Goodbye!').trim();

  function splitToLetters(text){
    return text.split('').map((ch, i) => {
      const span = document.createElement('span');
      span.className = 'letter';
      span.dataset.i = String(i);
      span.textContent = ch === ' ' ? '\u00A0' : ch;
      const angle = Math.random() * Math.PI * 2;
      const distance = 60 + Math.random() * 80;
      const x = Math.cos(angle) * distance;
      const y = Math.sin(angle) * distance;
      const rot = (Math.random() * 960 - 480).toFixed(2) + 'deg';
      const delay = 80 + i * 35 + Math.random() * 120;
      span.style.setProperty('--x', x.toFixed(2) + 'px');
      span.style.setProperty('--y', y.toFixed(2) + 'px');
      span.style.setProperty('--r', rot);
      span.style.setProperty('--delay', delay + 'ms');
      return span;
    });
  }

  function buildWord(){
    if (!target) return;
    target.innerHTML = '';
    const frag = document.createDocumentFragment();
    splitToLetters(WORD).forEach(n => frag.appendChild(n));
    target.appendChild(frag);
  }

  function showCard(){
    body.classList.add('gb-ready');
    setTimeout(() => { if (intro) intro.style.display = 'none'; }, 900);
  }

  function startSequence(){
    if (prefersReduced){
      buildWord();
      if (app) { app.style.opacity = '1'; app.style.transform = 'none'; }
      showCard();
      return;
    }
    buildWord();
    setTimeout(() => {
      intro?.classList.add('exploding');
      const total = 1700;
      setTimeout(() => {
        if (app) app.style.opacity = '1';
        showCard();
      }, total);
    }, 550);
  }

  startSequence();
})();
