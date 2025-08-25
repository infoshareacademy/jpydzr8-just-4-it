
(function(){
  const token = localStorage.getItem('token') || '';
  const auth = token ? { Authorization: 'Bearer '+token } : {};

  const $ = (id)=> document.getElementById(id);
  const form = $('cancelForm') || document.querySelector('form#cancelForm') || document.querySelector('form[action*="cancel"]') || document.querySelector('form');
  let info = $('cancelInfo');
  if(!info){
    info = document.createElement('div');
    info.id = 'cancelInfo';
    (form && form.parentNode) ? form.parentNode.appendChild(info) : document.body.appendChild(info);
  }
  let results = $('cancelResults');
  if(!results){
    results = document.createElement('div');
    results.id = 'cancelResults';
    results.style.marginTop = '8px';
    (form && form.parentNode) ? form.parentNode.appendChild(results) : document.body.appendChild(results);
  }

  async function apiCheck(seat, date){
    const res = await fetch(`/api/reservations/check/${encodeURIComponent(seat)}/${encodeURIComponent(date)}`, { headers: auth });
    if(!res.ok) return null;
    return await res.json(); 
  }
  async function apiList(params={}){
    const url = new URL('/api/reservations', location.origin);
    Object.entries(params).forEach(([k,v])=>{ if(v!=null && v!=='') url.searchParams.set(k,v); });
    const res = await fetch(url, { headers: auth });
    if(!res.ok) return [];
    return await res.json();
  }
  async function apiDelete(id){
    const res = await fetch('/api/reservations/'+encodeURIComponent(id), { method:'DELETE', headers: auth });
    return res.ok;
  }

  function val(...ids){
    for(const id of ids){
      const el = document.getElementById(id);
      if(el && 'value' in el) return el.value.trim();
    }
    return '';
  }

  function row(r){
    const div = document.createElement('div');
    div.className = 'cancel-row';
    div.style.cssText = 'display:flex;gap:8px;align-items:center;border:1px solid #ddd;padding:8px;border-radius:8px;margin:6px 0;';
    div.innerHTML = `<span><strong>${r.date}</strong> • seat <strong>${r.seat_id}</strong> • id <code>${r.id}</code></span>
                     <span style="flex:1"></span>
                     <button class="btn-cancel" data-cancel-id="${r.id}">Cancel</button>`;
    return div;
  }

  async function searchAndRender(){
    results.innerHTML = '';
    const id = val('cancelId','reservationId');
    const seat = val('cancelSeat','formSeat','seatId');
    const date = val('cancelDate','formDate','date');

    if(id){
      
      const items = await apiList({ date_from: date||null, date_to: date||null, seat_id: null });
      const found = items.find(x => String(x.id) === String(id));
      if(found){ results.appendChild(row(found)); }
      else { info.textContent = 'Nie znaleziono rezerwacji o podanym ID (spróbuj podać też datę).'; }
      return;
    }

    if(seat && date){
      const chk = await apiCheck(seat, date);
      if(chk && chk.reserved && chk.reservation_id){
        const items = await apiList({ date_from: date, date_to: date, seat_id: seat });
        if(items.length){
          items.forEach(r => results.appendChild(row(r)));
        }else{
          
          results.appendChild(row({ id: chk.reservation_id, date, seat_id: seat }));
        }
      }else{
        info.textContent = 'Brak rezerwacji dla tego miejsca i daty.';
      }
      return;
    }

    
    if(date && !seat){
      const items = await apiList({ date_from: date, date_to: date });
      if(items.length){ items.forEach(r => results.appendChild(row(r))); }
      else { info.textContent = 'Brak rezerwacji na wybraną datę.'; }
      return;
    }

    
    if(seat && !date){
      const now = new Date();
      const p = n => String(n).padStart(2,'0');
      const from = `${now.getFullYear()}-${p(now.getMonth()+1)}-${p(now.getDate()-30)}`;
      const to   = `${now.getFullYear()}-${p(now.getMonth()+1)}-${p(now.getDate()+30)}`;
      const items = await apiList({ seat_id: seat, date_from: from, date_to: to });
      if(items.length){ items.forEach(r => results.appendChild(row(r))); }
      else { info.textContent = 'Brak rezerwacji dla tego miejsca w ostatnich/zbliżających się 30 dniach.'; }
      return;
    }

    info.textContent = 'Podaj ID rezerwacji lub (Miejsce + Data), albo samą datę aby wyświetlić listę.';
  }

  
  form && form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    if(e.stopImmediatePropagation) e.stopImmediatePropagation();
    info.textContent = ''; results.innerHTML = '';

    const id = val('cancelId','reservationId');
    const seat = val('cancelSeat','formSeat','seatId');
    const date = val('cancelDate','formDate','date');

    let targetId = id || '';

    try{
      if(!targetId){
        if(seat && date){
          const chk = await apiCheck(seat, date);
          if(chk && chk.reserved && chk.reservation_id){ targetId = chk.reservation_id; }
          else { info.textContent = 'Nie znaleziono rezerwacji dla podanego miejsca i daty.'; return; }
        }else{
          
          await searchAndRender();
          return;
        }
      }

      const ok = await apiDelete(targetId);
      if(ok){
        info.textContent = 'Anulowano ✔';
        
        window.dispatchEvent(new CustomEvent('reservation:deleted', { detail: { id: targetId } }));
      }else{
        info.textContent = 'Nie udało się anulować.';
      }
    }catch(err){
      info.textContent = 'Błąd: ' + (err.message || String(err));
    }
  }, { capture:true });

  
  document.addEventListener('click', async (e)=>{
    const btn = e.target.closest('button.btn-cancel,[data-cancel-id]');
    if(!btn) return;
    e.preventDefault();
    const idAttr = btn.getAttribute('data-cancel-id');
    let targetId = idAttr || '';

    if(!targetId){
      const seat = btn.getAttribute('data-cancel-seat');
      const date = btn.getAttribute('data-cancel-date');
      if(seat && date){
        const chk = await apiCheck(seat, date);
        if(chk && chk.reserved && chk.reservation_id){
          targetId = chk.reservation_id;
          btn.setAttribute('data-cancel-id', targetId);
        }else{
          alert('Nie znaleziono rezerwacji do anulowania.');
          return;
        }
      }else{
        return;
      }
    }

    if(!confirm('Anulować rezerwację '+targetId+'?')) return;
    const ok = await apiDelete(targetId);
    if(ok){
      (btn.closest('.cancel-row') || btn).remove();
      info.textContent = 'Anulowano ✔';
      window.dispatchEvent(new CustomEvent('reservation:deleted', { detail: { id: targetId } }));
    }else{
      alert('Nie udało się anulować.');
    }
  });

  
  const btnFind = document.getElementById('btnFind');
  btnFind && btnFind.addEventListener('click', async (e)=>{ e.preventDefault(); info.textContent=''; await searchAndRender(); });
})();
