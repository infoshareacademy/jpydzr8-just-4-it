(function(){
  const token = localStorage.getItem('token') || '';
  const auth = token ? { Authorization: 'Bearer '+token } : {};

  const $ = (sel)=> document.querySelector(sel);
  const tbl = $('#tbl tbody'); const stat = $('#stat');

  async function readAPI(from,to,seat){
    try{
      const url = new URL('/api/reservations', location.origin);
      if(from) url.searchParams.set('date_from', from);
      if(to) url.searchParams.set('date_to', to);
      if(seat) url.searchParams.set('seat_id', seat);
      const res = await fetch(url.toString(), { headers: auth });
      if(!res.ok) return [];
      return await res.json();
    }catch(_){ return []; }
  }

  function row(r){
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${r.id}</td><td>${r.date}</td><td>${r.seat_id}</td>
                    <td>${r.name||''}</td><td>${r.email||''}</td><td>api</td>
                    <td><button data-id="${r.id}" class="del">Delete</button></td>`;
    return tr;
  }

  function render(api){
    tbl.innerHTML='';
    api.sort((a,b)=> String(a.date).localeCompare(String(b.date)));
    for(const r of api){ tbl.appendChild(row(r)); }
    stat.textContent = `API: ${api.length}`;
  }

  async function reload(){
    const from = $('#fDateFrom').value || null;
    const to   = $('#fDateTo').value || null;
    const seat = $('#fSeat').value || null;
    const api = await readAPI(from,to,seat);
    render(api);
  }

  document.addEventListener('click', async (e)=>{
    const btn = e.target.closest('button.del');
    if(!btn) return;
    const id = btn.dataset.id;
    if(!confirm('Delete reservation '+id+'?')) return;
    const res = await fetch('/api/reservations/'+encodeURIComponent(id), { method:'DELETE', headers: auth });
    if(res.ok) reload(); else alert('Delete failed');
  });

  $('#btnAuth').addEventListener('click', reload);
  $('#btnReload').addEventListener('click', reload);
  $('#btnExport').addEventListener('click', async ()=>{
    const from = $('#fDateFrom').value || null;
    const to   = $('#fDateTo').value || null;
    const seat = $('#fSeat').value || null;
    const api = await readAPI(from,to,seat);
    const rows = [['ID','Date','Seat','Name','Email']].concat(api.map(r=>[r.id,r.date,r.seat_id,r.name||'',r.email||'']));
    const csv = rows.map(r=>r.join(',')).join('\n');
    const blob = new Blob([csv], {type:'text/csv'}); const a=document.createElement('a');
    a.href=URL.createObjectURL(blob); a.download='admin_reservations.csv'; a.click();
  });
})();
