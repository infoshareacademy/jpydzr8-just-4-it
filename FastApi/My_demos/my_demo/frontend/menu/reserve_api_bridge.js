
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

  async function createReservation(seat_id, date, name, email, notes){
    const res = await fetch('/api/reservations', {
      method:'POST', headers:{ 'Content-Type':'application/json', ...auth },
      body: JSON.stringify({ seat_id, date, name, email, notes })
    });
    const data = await res.json().catch(()=>null);
    if(!res.ok) throw new Error((data && data.detail) || ('Error '+res.status));
    return data;
  }

  form.addEventListener('submit', async (e)=>{
    
    e.preventDefault();
    
    if(e.stopImmediatePropagation) e.stopImmediatePropagation();

    try{
      const seat_id = ($('formSeat')?.value) || ($('seatId')?.value) || '';
      const date    = ($('formDate')?.value) || ($('date')?.value) || '';
      const name    = ($('formName')?.value) || ($('name')?.value) || '';
      const email   = ($('formEmail')?.value) || ($('email')?.value) || '';
      const notes   = ($('formNotes')?.value) || '';

      if(!seat_id || !date) throw new Error('Uzupełnij datę i miejsce.');

      const saved = await createReservation(seat_id, date, name, email, notes);
      const id = saved.id;

      
      window.dispatchEvent(new CustomEvent('reservation:created', { detail: { id, seat_id, date, name, email } }));

      
      const linkId = 'reserveIcsLink';
      info.innerHTML = `Reserved ✔ — ID: <strong>${id}</strong>. <a href="#" id="${linkId}">Add to Calendar (.ics)</a>`;
      document.getElementById(linkId)?.addEventListener('click', (ev)=>{
        ev.preventDefault();
        if(window.downloadICS){
          window.downloadICS({ title: \`Seat \${seat_id}\`, startDate: date, description: \`Reservation \${id}\`, location: \`Seat \${seat_id}\` });
        } else {
          alert('ICS helper missing (ics.js)');
        }
      });

      
      try{
        const modal = document.getElementById('reserveModal');
        if(modal){ modal.classList.remove('show'); modal.setAttribute('aria-hidden','true'); modal.style.display='none'; }
      }catch(_){}
    }catch(err){
      alert(err.message || String(err));
    }
  }, { capture: true });
})();
