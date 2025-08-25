
(function(){
  function ensureCSS(){
    if(document.getElementById('ics-snackbar-style')) return;
    const s = document.createElement('style'); s.id='ics-snackbar-style';
    s.textContent = '.ics-snack{position:fixed;right:16px;bottom:16px;background:var(--card-bg,#111);color:#fff;padding:12px 14px;border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.2);display:flex;gap:10px;align-items:center;z-index:99999} .ics-snack a{color:#0ff;text-decoration:underline} .ics-close{margin-left:8px;cursor:pointer;opacity:.7}';
    document.head.appendChild(s);
  }
  function showICS(detail){
    ensureCSS();
    const { id, seat_id, date } = detail || {};
    if(!id || !seat_id || !date) return;
    const d = document.createElement('div');
    d.className = 'ics-snack';
    d.innerHTML = `<span>Reserved: <b>${seat_id}</b> • ${date}</span> <a href="#" class="ics-link">Add to Calendar</a> <span class="ics-close">✕</span>`;
    document.body.appendChild(d);
    d.querySelector('.ics-link').addEventListener('click', (e)=>{
      e.preventDefault();
      if(window.downloadICS){
        window.downloadICS({ title: 'Seat '+seat_id, startDate: date, description: 'Reservation '+id, location: 'Seat '+seat_id });
      }else{ alert('Brak ics.js'); }
    });
    d.querySelector('.ics-close').addEventListener('click', ()=> d.remove());
    setTimeout(()=>{ try{ d.remove(); }catch(_){ } }, 5000);
  }
  window.addEventListener('reservation:created', (e)=> showICS(e.detail||{}));
})();
