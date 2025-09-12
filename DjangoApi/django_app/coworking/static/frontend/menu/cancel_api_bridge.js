// cancel_api_bridge.js — session-auth + dispatch reservation:deleted
(function(){
  function getCookie(name){ return document.cookie.split('; ').find(r => r.startsWith(name + '='))?.split('=')[1]; }
  async function apiFetch(url, opts={}){
    const csrftoken = getCookie('csrftoken') || '';
    const headers = Object.assign({ 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken }, opts.headers || {});
    const resp = await fetch(url, Object.assign({}, opts, { headers, credentials: 'same-origin' }));
    let data = null;
    try { data = await resp.json(); } catch(e){}
    if(!resp.ok){
      const msg = (data && (data.detail || data.message)) || ('HTTP ' + resp.status);
      const err = new Error(msg); err.status = resp.status; err.data = data; throw err;
    }
    return data;
  }
  const form = document.getElementById('cancelForm');
  if(!form) return;
  let info = document.getElementById('cancelInfo');
  let results = document.getElementById('cancelResults');
  if(!info){ info = document.createElement('div'); info.id='cancelInfo'; form.parentNode && form.parentNode.appendChild(info); }
  if(!results){ results = document.createElement('div'); results.id='cancelResults'; form.parentNode && form.parentNode.appendChild(results); }

  function val(id){ return (document.getElementById(id)?.value || '').trim(); }

  async function delById(id){
    await apiFetch('/api/reservations/' + encodeURIComponent(id) + '/', { method:'DELETE' });
    // notify UI for ICS cancel link
    try{ window.dispatchEvent(new CustomEvent('reservation:deleted', { detail: { id } })); }catch(_){}
    return true;
  }

  async function listByDate(date){
    return await apiFetch('/api/reservations/?date_from=' + encodeURIComponent(date) + '&date_to=' + encodeURIComponent(date), { method:'GET' });
  }

  function row(r){
    const div = document.createElement('div');
    div.className = 'cancel-row';
    div.textContent = `${r.date} — ${r.seat_id} — ${r.name} <${r.email}>`;
    const btn = document.createElement('button');
    btn.textContent = 'Cancel reservation';
    btn.addEventListener('click', async ()=>{
      try{
        await delById(r.id);
        div.remove();
        info.innerHTML = 'Deleted: ' + r.id + ` — <a href="/api/ics/reservations/${encodeURIComponent(r.id)}/cancel.ics" download>Remove from calendar (.ics)</a>`;
      }catch(err){ info.textContent = 'Error: ' + err.message; }
    });
    div.appendChild(btn);
    return div;
  }

  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    results.innerHTML = '';
    info.textContent = '';
    const id = val('cancelId') || val('reservationId') || '';
    if(id){
      try{
        await delById(id);
        info.innerHTML = 'Delete reservation: ' + id + ` — <a href="/api/ics/reservations/${encodeURIComponent(id)}/cancel.ics" download>Remove from calendar (.ics)</a>`;
      }catch(err){ info.textContent = 'Error: ' + err.message; }
      return;
    }
    const date = val('date') || val('cancelDate') || '';
    if(date){
      try{
        const items = await listByDate(date);
        if(!Array.isArray(items) || !items.length){
          info.textContent = 'No reservations for this date.';
          return;
        }
        items.forEach(r => results.appendChild(row(r)));
      }catch(err){ info.textContent = 'Error: ' + err.message; }
      return;
    }
    info.textContent = 'Please provide your booking ID or date.';
  });
})();