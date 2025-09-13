(function(){
  function getCookie(name){
    return document.cookie.split('; ').find(x => x.startsWith(name+'='))?.split('=')[1] || '';
  }
  function val(...ids){
    for(const id of ids){
      const el = document.getElementById(id);
      if(el && typeof el.value !== 'undefined' && String(el.value).trim() !== ''){
        return String(el.value).trim();
      }
    }
    return '';
  }
  function ensureTrailingSlash(url){
    const [path, qs] = url.split('?');
    return (path.endsWith('/') ? path : path + '/') + (qs ? ('?'+qs) : '');
  }

  // Fix GETy tabeli/kal
  window.API_RES_LIST = function(qs){
    const base = '/api/reservations';
    const url = ensureTrailingSlash(base) + (qs ? ('?'+qs) : '');
    return fetch(url, { credentials: 'same-origin' }).then(r => r.json());
  };

  const form = document.getElementById('reserveForm');
  if(!form) return;
  const info = document.getElementById('reservationInfo') || (function(){ const d=document.createElement('div'); d.id='reservationInfo'; form.appendChild(d); return d; })();

  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const seat_id = val('formSeat','seat','seatId','seat_id');
    const date    = val('formDate','date','reserveDate','dateStr');
    const name    = val('formName','name','fullName');
    const email   = val('formEmail','email','mail');
    const notes   = val('formNotes','notes');

    if(!seat_id || !date || !name || !email){
      info.textContent = 'Required: seat, date, name, email.';
      return;
    }

    const body = { seat_id, date, name, email, notes };
    try{
      info.textContent = 'Saving...';
      const res = await fetch('/api/reservations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'same-origin',
        body: JSON.stringify(body)
      });
      const data = await res.json().catch(()=> ({}));
      if(!res.ok){
        const first = data?.detail || Object.entries(data)[0]?.join(': ') || ('HTTP '+res.status);
        throw new Error(first);
      }
      info.textContent = 'Reservation saved.';
      try{
        localStorage.setItem('lastReservation', JSON.stringify(data));
        window.dispatchEvent(new CustomEvent('reservation:created', { detail: data }));
      }catch(e){}
      setTimeout(()=> location.href='/dashboard#created', 500);
    }catch(err){
      info.textContent = 'Error: ' + (err.message || String(err));
    }
  }, { capture: true });
})();