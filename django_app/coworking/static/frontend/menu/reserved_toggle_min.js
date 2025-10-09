(function(){
  const LS_KEY = 'reservedSeats';

  function loadSet(){
    try { return new Set((JSON.parse(localStorage.getItem(LS_KEY)||'[]')||[]).map(String)); }
    catch(_){ return new Set(); }
  }
  function saveSet(set){
    try { localStorage.setItem(LS_KEY, JSON.stringify(Array.from(set))); } catch(_){}
  }

  function toggleBadgeBySeatId(seatId, on){
    if(!seatId) return;
    const el = document.querySelector(`[data-seat-id="${CSS.escape(String(seatId))}"]`);
    if(!el) return;

    if(on) el.setAttribute('data-status','reserved');
    else if(el.getAttribute('data-status')==='reserved') el.removeAttribute('data-status');

    let badge = el.querySelector('.r-badge');
    if(on){
      if(!badge){
        badge = document.createElement('span');
        badge.className = 'r-badge reserved';
        badge.textContent = 'R';
        const icon = el.querySelector('.seat-icon');
        (icon?.parentElement || el).insertBefore(badge, icon || null);
      }else{
        badge.classList.add('reserved');
        badge.textContent = 'R';
      }
    }else if(badge){
      badge.remove();
    }
  }

  function renderFromStorageOnce(){
    const set = loadSet();
    if(set.size === 0) return;
    const tiles = document.querySelectorAll('.seat-item-styled,[data-seat-id]');
    if(!tiles.length) return;

    tiles.forEach(el=>{
      const sid = el.getAttribute('data-seat-id');
      if(!sid) return;
      const shouldBe = set.has(String(sid));
      if(shouldBe || el.querySelector('.r-badge') || el.getAttribute('data-status')==='reserved'){
        toggleBadgeBySeatId(sid, shouldBe);
      }
    });
  }

  window.__renderReservedBadges = renderFromStorageOnce;

  window.addEventListener('reservation:created', (e)=>{
    const d = e.detail || {};
    const seat = d.seat_id || d.seat || d.place || d.seatId || d.id_seat;
    if(!seat) return;
    const set = loadSet(); set.add(String(seat)); saveSet(set);
    toggleBadgeBySeatId(seat, true);
  });

  window.addEventListener('reservation:deleted', (e)=>{
    const d = e.detail || {};
    const seat = d.seat_id || d.seat || d.place || d.seatId || d.id_seat;
    if(!seat) return;
    const set = loadSet(); set.delete(String(seat)); saveSet(set);
    toggleBadgeBySeatId(seat, false);
  });

  function waitThenRender(tries=0){
    if (document.querySelector('.seat-item-styled,[data-seat-id]')) {
      renderFromStorageOnce(); return;
    }
    if (tries > 80) return; // ~1.3s max przy 16ms
    requestAnimationFrame(()=> waitThenRender(tries+1));
  }
  if (document.readyState === 'complete') waitThenRender();
  else window.addEventListener('load', waitThenRender);
})();
