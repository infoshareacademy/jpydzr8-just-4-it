// static/frontend/menu/occupied.js
(function () {
  /** Znajdź wszystkie kafelki z (element, seatId) */
  function findSeatTiles() {
    const tiles = [];
    document.querySelectorAll('.seats-grid .seat-item-styled').forEach(el => {
      // preferuj data-seat-id, a jak brak – tekst z .seat-label
      const id = el.dataset.seatId
        || (el.querySelector('.seat-label')?.textContent?.trim().split(/\s|\(/)[0])
        || '';
      if (id) tiles.push([el, id]);
    });
    return tiles;
  }

  /** Upewnij się, że kafelek ma plakietkę „R” */
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

  /** Ustaw stan zajętości na podstawie prawdziwego API */
  function setOccupied(el, occupied) {
    el.classList.toggle('seat-occupied', !!occupied);
    el.dataset.status = occupied ? 'reserved' : 'free';

    // pokaż/ukryj plakietkę
    const flag = ensureRBadge(el);
    flag.style.display = occupied ? 'flex' : 'none';

    // zablokuj przycisk „Rezerwuj” (jeśli istnieje w kafelku)
    const btn = el.querySelector('.btn-reserve');
    if (btn) {
      btn.disabled = !!occupied;
      btn.title = occupied ? 'Zarezerwowane na wybraną datę' : '';
    }
  }

  /** Pobierz listę zajętych z API */
  async function fetchOccupied(dateStr) {
    const res = await fetch(`/api/seats/occupied?date=${encodeURIComponent(dateStr)}`, {
      credentials: 'same-origin',
      headers: { 'Accept': 'application/json' }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  /** Aktualizuj kafelki zgodnie z API */
  async function refreshOccupied(dateStr) {
    try {
      const { occupied = [] } = await fetchOccupied(dateStr);
      const occ = new Set(occupied.map(String));
      findSeatTiles().forEach(([el, id]) => setOccupied(el, occ.has(String(id))));
    } catch (e) {
      console.warn('Nie udało się pobrać zajętości:', e);
    }
  }

  /** Bieżąca data z #formDate (jeśli jest) albo dzisiejsza */
  function currentDateStr() {
    const inp = document.getElementById('formDate');
    if (inp && inp.value) return inp.value;
    return new Date().toISOString().slice(0, 10);
  }

  /** Podłącz pod zmianę daty + start po zbudowaniu siatki */
  function init() {
    // 1) pierwszy strzał – daj chwilę Twojemu script.js na wyrenderowanie siatek
    const kick = () => refreshOccupied(currentDateStr());
    if (document.readyState === 'complete') setTimeout(kick, 150);
    else window.addEventListener('load', () => setTimeout(kick, 150));

    // 2) reaguj na zmianę daty (formularz rezerwacji)
    const inp = document.getElementById('formDate');
    if (inp) inp.addEventListener('change', () => refreshOccupied(inp.value || currentDateStr()));

    // 3) jeżeli siatki pojawiają się dynamicznie – obserwuj zmiany DOM i odśwież
    const mo = new MutationObserver(() => {
      // krótka debouncowana aktualizacja
      clearTimeout(init._t);
      init._t = setTimeout(() => refreshOccupied(currentDateStr()), 100);
    });
    mo.observe(document.body, { childList: true, subtree: true });
  }

  init();
  // udostępnij ręczne odświeżenie
  window.refreshSeatsOccupied = refreshOccupied;
})();
