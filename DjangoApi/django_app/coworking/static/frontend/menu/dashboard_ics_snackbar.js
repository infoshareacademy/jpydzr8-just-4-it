// dashboard_ics_snackbar.js — ICS snackbar (server-generated .ics)
(function(){
  function ensureCSS(){
    if(document.getElementById('ics-snackbar-style')) return;
    const s = document.createElement('style'); s.id='ics-snackbar-style';
    s.textContent = [
      '.ics-snack{position:fixed;right:16px;bottom:16px;z-index:9999;background:#111;color:#fff;padding:10px 12px;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.25);display:flex;align-items:center;gap:10px;font:14px/1.3 system-ui, sans-serif}',
      '.ics-snack a{color:#93c5fd;text-decoration:underline}',
      '.ics-close{margin-left:6px;cursor:pointer;opacity:.75}',
      '.ics-actions{display:flex;gap:10px}'
    ].join(' ');
    document.head.appendChild(s);
  }
  function showICS(detail){
    ensureCSS();
    const { id, seat_id, date } = detail || {};
    if(!id || !seat_id || !date) return;
    const d = document.createElement('div');
    d.className = 'ics-snack';
    const addUrl = `/api/ics/reservations/${encodeURIComponent(id)}.ics`;
    const html = `<span>Reserved: <b>${seat_id}</b> • ${date}</span>
                  <span class="ics-actions">
                    <a href="${addUrl}" download>+ Add to Calendar (.ics)</a>
                  </span>
                  <span class="ics-close">✕</span>`;
    d.innerHTML = html;
    document.body.appendChild(d);
    d.querySelector('.ics-close').addEventListener('click', ()=> d.remove());
    setTimeout(()=>{ try{ d.remove(); }catch(_){ } }, 6000);
  }
  function showCancelICS(detail){
    ensureCSS();
    const { id, seat_id, date } = detail || {};
    if(!id) return;
    const d = document.createElement('div');
    d.className = 'ics-snack';
    const cancelUrl = `/api/ics/reservations/${encodeURIComponent(id)}/cancel.ics`;
    const html = `<span>Deleted reservation ${seat_id||''} ${date||''}</span>
                  <span class="ics-actions">
                    <a href="${cancelUrl}" download>- Remove from Calendar (.ics)</a>
                  </span>
                  <span class="ics-close">✕</span>`;
    d.innerHTML = html;
    document.body.appendChild(d);
    d.querySelector('.ics-close').addEventListener('click', ()=> d.remove());
    setTimeout(()=>{ try{ d.remove(); }catch(_){ } }, 6000);
  }
  // fire from other pages using localStorage
  try{
    const raw = localStorage.getItem('lastReservation');
    if(raw){
      const obj = JSON.parse(raw);
      if(obj && obj.id && obj.date) showICS(obj);
      localStorage.removeItem('lastReservation');
    }
  }catch(_){ }
  // also react to custom events
  window.addEventListener('reservation:created', (e)=> showICS(e.detail||{}));
  window.addEventListener('reservation:deleted', (e)=> showCancelICS(e.detail||{}));
})();