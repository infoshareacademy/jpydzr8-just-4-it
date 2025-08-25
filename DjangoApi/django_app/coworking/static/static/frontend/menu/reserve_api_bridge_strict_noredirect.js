// reserve_api_bridge_strict_noredirect.js — POST to API + emit + summary (NO redirect)
(function(){
  const token = localStorage.getItem('token') || '';
  const auth = token ? { Authorization: 'Bearer '+token } : {};
  const form = document.getElementById('reserveForm');
  if(!form) return;
  const $ = (id)=> document.getElementById(id);
  let info = document.getElementById('reservationInfo');
  if(!info){ info = document.createElement('div'); info.id='reservationInfo'; form.parentNode && form.parentNode.appendChild(info); }

  async function apiCreate(payload){
    const res = await fetch('/api/reservations', { method:'POST', headers:{'Content-Type':'application/json', ...auth}, body: JSON.stringify(payload) });
    const data = await res.json().catch(()=>null);
    if(!res.ok) throw new Error((data && (data.detail||data.message)) || ('HTTP '+res.status));
    return data;
  }
  function val(...ids){ for(const id of ids){ const el = document.getElementById(id); if(el && 'value' in el) return el.value.trim(); } return ''; }

  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    if(e.stopImmediatePropagation) e.stopImmediatePropagation();
    try{
      const seat_id = val('formSeat','seatId'); const date = val('formDate','date');
      const name = val('formName','name'); const email = val('formEmail','email'); const notes = val('formNotes');
      if(!seat_id || !date) throw new Error('Uzupełnij datę i miejsce.');
      const saved = await apiCreate({ seat_id, date, name, email, notes });
      const id = saved.id;
      info.innerHTML = `Reserved ✔ — ID: <strong>${id}</strong>`;
      const detail = { id, seat_id, date, name, email };
      window.dispatchEvent(new CustomEvent('reservation:created', { detail }));
      if(typeof window.showReservationSummary === 'function'){ window.showReservationSummary(detail); }
      try{ const modal = document.getElementById('reserveModal'); if(modal){ modal.style.display='none'; modal.setAttribute('aria-hidden','true'); } }catch(_){}
    }catch(err){ alert(err.message || String(err)); }
  }, { capture:true });
})();
