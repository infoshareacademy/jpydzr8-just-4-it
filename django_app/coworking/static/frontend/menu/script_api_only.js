(function(){
  const API = location.origin;
  const token = localStorage.getItem('token') || '';
  const auth = token ? { Authorization: 'Bearer '+token } : {};

  const $ = (id)=> document.getElementById(id);
  const form = $('reserveForm');
  const info = $('reservationInfo');
  const seatsContainer = $('seatsContainer') || $('seatsGrid') || document.body;
  const filterDate = $('filterDate') || $('date') || $('formDate');
  const nameInput = $('formName') || $('name');
  const emailInput = $('formEmail') || $('email');
  const notesInput = $('formNotes');

  if(!window.downloadICS){
    window.downloadICS = function({title='Reservation', startDate, description='', location=''}){
      if(!startDate){ alert('No date for ICS'); return; }
      const dt = String(startDate).replace(/-/g,''); // YYYYMMDD
      const ics = [
        'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//WorkspaceBookings//EN','BEGIN:VEVENT',
        `UID:${Date.now()}@workspace`,
        `DTSTAMP:${dt}T090000Z`,
        `DTSTART;VALUE=DATE:${dt}`,
        `DTEND;VALUE=DATE:${dt}`,
        `SUMMARY:${title}`,
        `DESCRIPTION:${description}`,
        `LOCATION:${location}`,
        'END:VEVENT','END:VCALENDAR'
      ].join('\r\n');
      const blob = new Blob([ics], {type:'text/calendar'});
      const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'reservation.ics'; a.click();
    };
  }

  async function apiList(date){
    const url = new URL('/api/reservations', API);
    if(date) url.searchParams.set('date_from', date), url.searchParams.set('date_to', date);
    const res = await fetch(url.toString(), { headers: auth });
    if(!res.ok) return [];
    return await res.json();
  }
  async function apiCheck(seat_id, date){
    const res = await fetch(`/api/reservations/check/${encodeURIComponent(seat_id)}/${encodeURIComponent(date)}`, { headers: auth });
    if(!res.ok) return { reserved:false };
    return await res.json();
  }
  async function apiCreate(payload){
    const res = await fetch('/api/reservations', { method:'POST', headers:{ 'Content-Type':'application/json', ...auth }, body: JSON.stringify(payload) });
    const data = await res.json().catch(()=>null);
    if(!res.ok) throw new Error( (data && data.detail) || ('Error '+res.status) );
    return data; // {id, seat_id, date, ...}
  }
  async function apiDelete(id){
    const res = await fetch('/api/reservations/'+encodeURIComponent(id), { method:'DELETE', headers: auth });
    if(!res.ok) throw new Error('Delete failed');
    return true;
  }

  function toast(msg){ if(window.Toastify){ Toastify({ text: msg, duration: 1800, gravity:'bottom' }).showToast(); } else { console.log('[toast]', msg); } }
  function today(){ const d=new Date(); const p=n=>String(n).padStart(2,'0'); return d.getFullYear()+"-"+p(d.getMonth()+1)+"-"+p(d.getDate()); }

  const KNOWN_SEATS = (window.KNOWN_SEATS || ['A1','A2','A3','B1','B2','B3','C1','C2','C3']);
  function renderSeats(date, reservations){
    const reserved = new Set((reservations||[]).filter(r=> r.date===date).map(r=> r.seat_id));
    const wrap = seatsContainer;
    if(!wrap) return;
    wrap.innerHTML = '';
    KNOWN_SEATS.forEach(seat=>{
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'seat ' + (reserved.has(seat)? 'taken' : 'free');
      btn.textContent = seat;
      btn.dataset.seatId = seat;
      btn.disabled = reserved.has(seat);
      btn.addEventListener('click', ()=>{
        const seatInput = $('formSeat') || $('seatId');
        if(seatInput) seatInput.value = seat;
        toast(`Selected ${seat}`);
      });
      wrap.appendChild(btn);
    });
  }

  async function refreshSeats(){
    const date = (filterDate && filterDate.value) || today();
    const list = await apiList(date);
    renderSeats(date, list);
  }

  if(form){
    form.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const seat_id = (document.getElementById('formSeat')||document.getElementById('seatId'))?.value || '';
      const date = (document.getElementById('formDate')||document.getElementById('date'))?.value || '';
      const name = (nameInput && nameInput.value) || '';
      const email = (emailInput && emailInput.value) || '';
      const notes = (notesInput && notesInput.value) || '';
      if(!seat_id || !date){ toast('Uzupełnij datę i miejsce.'); return; }

      const chk = await apiCheck(seat_id, date);
      if(chk && chk.reserved){ toast('To miejsce jest już zajęte.'); await refreshSeats(); return; }

      try{
        const saved = await apiCreate({ seat_id, date, name, email, notes });
        const id = saved.id;
        window.dispatchEvent(new CustomEvent('reservation:created', { detail: { id, seat_id, date, name, email } }));
        toast('Reserved ✔');
        if(info){
          const icsId = 'reserveIcsLink';
          info.innerHTML = `Reserved ✔ — ID: <strong>${id}</strong>. <a href="#" id="${icsId}">Add to Calendar (.ics)</a>`;
          document.getElementById(icsId)?.addEventListener('click', (ev)=>{
            ev.preventDefault();
            window.downloadICS && window.downloadICS({ title: `Seat ${seat_id}`, startDate: date, description: `Reservation ${id}`, location: `Seat ${seat_id}` });
          });
        }
        await refreshSeats();
      }catch(err){
        alert(err.message || String(err));
      }
    }, { capture:true });
  }

  document.addEventListener('click', async (e)=>{
    const btn = e.target.closest('[data-cancel-id]');
    if(!btn) return;
    e.preventDefault();
    const id = btn.getAttribute('data-cancel-id');
    if(!id) return;
    if(!confirm('Cancel reservation ' + id + '?')) return;
    try{
      await apiDelete(id);
      window.dispatchEvent(new CustomEvent('reservation:deleted', { detail: { id } }));
      toast('Cancelled ✔');
      await refreshSeats();
    }catch(err){ alert(err.message||String(err)); }
  });

  if(filterDate){ if(!filterDate.value) filterDate.value = today(); filterDate.addEventListener('change', refreshSeats); }
  refreshSeats();
})();
