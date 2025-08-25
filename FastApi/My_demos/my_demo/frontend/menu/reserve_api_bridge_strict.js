
(function(){
  const token = localStorage.getItem('token') || '';
  const auth = token ? { Authorization: 'Bearer '+token } : {};
  const form = document.getElementById('reserveForm');
  if(!form) return;

  const $ = (id)=> document.getElementById(id);
  let info = $('reservationInfo');
  if(!info){
    info = document.createElement('div');
    info.id = 'reservationInfo';
    form.parentNode && form.parentNode.appendChild(info);
  }

  function val(...ids){
    for(const id of ids){
      const el = document.getElementById(id);
      if(el && 'value' in el) return (el.value||'').trim();
    }
    return '';
  }

  async function apiCreate(payload){
    const res = await fetch('/api/reservations', {
      method:'POST', headers:{ 'Content-Type':'application/json', ...auth }, body: JSON.stringify(payload)
    });
    const data = await res.json().catch(()=>null);
    if(res.status === 401){
      
      try{ sessionStorage.setItem('flash_msg', 'Zaloguj się, aby rezerwować.'); }catch(_){}
      location.href = '/login/index.html';
      return Promise.reject(new Error('401 Unauthorized'));
    }
    if(!res.ok){
      const msg = (data && (data.detail || data.message)) || ('HTTP '+res.status);
      throw new Error(msg);
    }
    return data;
  }

  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    if(e.stopImmediatePropagation) e.stopImmediatePropagation();

    const seat_id = val('formSeat','seatId');
    const date    = val('formDate','date');
    const name    = val('formName','name');
    const email   = val('formEmail','email');
    const notes   = val('formNotes');

    if(!seat_id || !date){
      info.textContent = 'Uzupełnij datę i miejsce.';
      return;
    }

    try{
      const saved = await apiCreate({ seat_id, date, name, email, notes });
      const id = saved.id;
      const detail = { id, seat_id, date, name, email };
      window.dispatchEvent(new CustomEvent('reservation:created', { detail }));

      
      const linkId = 'reserveIcsLink';
      info.innerHTML = `Reserved ✔ — ID: <strong>${id}</strong>. <a href="#" id="${linkId}">Add to Calendar (.ics)</a>`;
      document.getElementById(linkId)?.addEventListener('click', (ev)=>{
        ev.preventDefault();
        if(window.downloadICS){
          window.downloadICS({ title: `Seat ${seat_id}`, startDate: date, description: `Reservation ${id}`, location: `Seat ${seat_id}` });
        } else {
          alert('Brak ics.js na tej stronie');
        }
      });

      
      try{ sessionStorage.setItem('flash_reservation', JSON.stringify(detail)); }catch(_){}
      setTimeout(()=>{ location.href = 'dashboard.html#created'; }, 900);

    }catch(err){
      info.textContent = 'Błąd: ' + (err.message || String(err));
    }
  }, { capture:true });
})();
