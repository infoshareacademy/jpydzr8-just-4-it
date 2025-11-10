(function () {

  function findSeatTiles() {
    const tiles = [];
    document.querySelectorAll('.seats-grid .seat-item-styled').forEach(el => {
      const id = el.dataset.seatId
        || (el.querySelector('.seat-label')?.textContent?.trim().split(/\s|\(/)[0])
        || '';
      if (id) tiles.push([el, id]);
    });
    return tiles;
  }

  function ensureRBadge(el) {
    let flag = el.querySelector('.seat-flag');
    if (!flag) {
      flag = document.createElement('span');
      flag.className = 'seat-flag';
      flag.textContent = 'R';
      flag.title = 'Zarezerwowane';
      flag.setAttribute('aria-label', 'Zarezerwowane');
      el.appendChild(flag);
    }
    return flag;
  }

  function setOccupied(el, occupied) {
    el.classList.toggle('seat-occupied', !!occupied);
    el.dataset.status = occupied ? 'reserved' : 'free';

    const flag = ensureRBadge(el);
    flag.style.display = occupied ? 'flex' : 'none';

    const btn = el.querySelector('.btn-reserve');
    if (btn) {
      btn.disabled = !!occupied;
      btn.title = occupied ? 'Zarezerwowane na wybraną datę' : '';
    }
  }

  async function fetchOccupied(dateStr) {
    const res = await fetch(`/api/seats/occupied?date=${encodeURIComponent(dateStr)}`, {
      credentials: 'same-origin',
      headers: { 'Accept': 'application/json' }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  async function refreshOccupied(dateStr) {
    try {
      const { occupied = [] } = await fetchOccupied(dateStr);
      const occ = new Set(occupied.map(String));
      findSeatTiles().forEach(([el, id]) => setOccupied(el, occ.has(String(id))));
    } catch (e) {
      console.warn('Nie udało się pobrać zajętości:', e);
    }
  }

  function currentDateStr() {
    const inp = document.getElementById('formDate');
    if (inp && inp.value) return inp.value;
    return new Date().toISOString().slice(0, 10);
  }

  function init() {
    const kick = () => refreshOccupied(currentDateStr());
    if (document.readyState === 'complete') setTimeout(kick, 150);
    else window.addEventListener('load', () => setTimeout(kick, 150));

    const inp = document.getElementById('formDate');
    if (inp) inp.addEventListener('change', () => refreshOccupied(inp.value || currentDateStr()));

    const mo = new MutationObserver(() => {
      clearTimeout(init._t);
      init._t = setTimeout(() => refreshOccupied(currentDateStr()), 100);
    });
    mo.observe(document.body, { childList: true, subtree: true });
  }

  init();
  window.refreshSeatsOccupied = refreshOccupied;
})();
