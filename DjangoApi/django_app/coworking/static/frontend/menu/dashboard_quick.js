// Quick-book modal using API (POST /api/reservations) + ICS + ticket link
(function(){
  function getCookie(name){return document.cookie.split('; ').find(r=>r.startsWith(name+'='))?.split('=')[1];}

  const m = document.getElementById('qbModal');
  const openBtn = document.getElementById('quickBookBtn');
  const btnCancel = document.getElementById('qbCancel');
  const btnCreate = document.getElementById('qbCreate');
  const fDate = document.getElementById('qbDate');
  const fSeat = document.getElementById('qbSeat');
  const fName = document.getElementById('qbName');
  const fEmail = document.getElementById('qbEmail');
  const info = document.getElementById('qbInfo');

  function openModal(pref={}){
    m.style.display='flex'; m.setAttribute('aria-hidden','false');
    if(pref.date) fDate.value = pref.date;
    setTimeout(()=> fSeat.focus(), 0);
  }
  function closeModal(){ m.style.display='none'; m.setAttribute('aria-hidden','true'); info.textContent=''; }

  openBtn?.addEventListener('click', ()=> openModal({ date: new Date().toISOString().slice(0,10) }));
  btnCancel?.addEventListener('click', closeModal);
  document.addEventListener('qb:open', (e)=> openModal(e.detail||{}));
  m.addEventListener('click', (e)=>{ if(e.target === m) closeModal(); });

  btnCreate?.addEventListener('click', async ()=>{
    const date = fDate.value.trim();
    const seat_id = fSeat.value.trim();
    const name = fName.value.trim() || 'You';
    const email = fEmail.value.trim() || '';
    if(!date || !seat_id){ info.textContent='Fill date and seat.'; return; }

    try{
      const res = await fetch('/api/reservations/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': (getCookie('csrftoken')||'') },
        body: JSON.stringify({ seat_id, date, name, email, notes: '' })
      });
      const data = await res.json().catch(()=>null);
      if(!res.ok){
        info.textContent = (data && data.detail) ? data.detail : `Error ${res.status}`;
        return;
      }
      const id = data.id;
      if(window.emitReservationCreated){
        window.emitReservationCreated({ id, seat_id, date, name, email });
      } else {
        const evt = new CustomEvent('reservation:created', { detail: { id, seat_id, date, name, email } });
        window.dispatchEvent(evt);
      }
      info.innerHTML = `Created ✔ ID <b>${id}</b> — <a href="#" id="dlICS">Add to Calendar (.ics)</a>`;
      document.getElementById('dlICS')?.addEventListener('click', (e)=>{
        e.preventDefault();
        if(window.downloadICS){
          window.downloadICS({ title: `Seat ${seat_id}`, startDate: date, description: `Reservation ${id}`, location: `Seat ${seat_id}` });
        }
      });
    }catch(err){
      info.textContent = err.message || String(err);
    }
  });
})();
