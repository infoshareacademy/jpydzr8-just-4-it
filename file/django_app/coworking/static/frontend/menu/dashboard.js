(function(){
  const THEME_KEY = 'ui.theme';
  const DATA_KEY = 'reservations';

  const root = document.documentElement;
  const translate = window.t ? window.t : ((english, polish) => {
    const isPl = (document.documentElement.lang || '').toLowerCase().startsWith('pl');
    return isPl ? (polish ?? english) : english;
  });
  const savedTheme = localStorage.getItem(THEME_KEY) || 'light';
  root.setAttribute('data-theme', savedTheme);
  const toggleBtn = document.getElementById('themeToggle');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const cur = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', cur);
      localStorage.setItem(THEME_KEY, cur);
      toggleBtn.innerHTML = cur === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });
    toggleBtn.innerHTML = savedTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
  }

  function parseReservations(){
    try { return JSON.parse(localStorage.getItem(DATA_KEY) || '[]'); }
    catch(e){ return []; }
  }
  function toDate(d){ return new Date(d + 'T00:00:00'); }

  function renderUpcoming(){
    const today = new Date(new Date().toDateString());
    const list = parseReservations()
      .filter(r => toDate(r.date) >= today)
      .sort((a,b)=> toDate(a.date)-toDate(b.date));
    const w = document.getElementById('upcomingWidget');
    if(!w) return;
    const body = w.querySelector('.uw-body');
    if(list.length===0){
      body.classList.add('empty');
      body.textContent = translate('You have no upcoming reservations.', 'Nie masz nadchodzących rezerwacji.');
      return;
    }
    body.classList.remove('empty');
    const r = list[0];
    body.innerHTML = `<strong>${translate('Seat', 'Stanowisko')} ${r.seat}</strong> — <span>${r.date}</span><br><small>ID: ${r.id}</small>`;
  }

  function renderRecent(){
    const cont = document.getElementById('recentReservations');
    if(!cont) return;
    cont.innerHTML='';
    const list = parseReservations()
      .sort((a,b)=> new Date(b.createdAt||0) - new Date(a.createdAt||0))
      .slice(0,5);
    if(list.length===0){
      cont.innerHTML = `<div class="recent-item"><i class="fas fa-info-circle"></i><div class="recent-info">${translate('No recent reservations.', 'Brak ostatnich rezerwacji.')}</div></div>`;
      return;
    }
    list.forEach(r=>{
      const item = document.createElement('div');
      item.className='recent-item';
      item.innerHTML = `<i class="fas fa-calendar-day"></i>
        <div class="recent-info"><strong>${translate('Seat', 'Stanowisko')} ${r.seat}</strong> — <span>${r.date}</span><br><small>ID: ${r.id}</small></div>`;
      cont.appendChild(item);
    });
  }

  function exportCSV(){
    const rows = parseReservations();
    const header = ['id','seat','date','name','createdAt'];
    const csv = [header.join(',')].concat(rows.map(r=>header.map(k=>`"${(r[k]||'').toString().replace(/"/g,'""')}"`).join(','))).join('\n');
    const blob = new Blob([csv], {type:'text/csv'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'reservations.csv';
    a.click();
    setTimeout(()=>URL.revokeObjectURL(a.href), 1000);
  }
  function exportJSON(){
    const blob = new Blob([JSON.stringify(parseReservations(),null,2)], {type:'application/json'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'reservations.json';
    a.click();
    setTimeout(()=>URL.revokeObjectURL(a.href), 1000);
  }

  document.getElementById('qaCsv')?.addEventListener('click', exportCSV);
  document.getElementById('qaJson')?.addEventListener('click', exportJSON);
  document.getElementById('qaRefresh')?.addEventListener('click', ()=>{ renderUpcoming(); renderRecent(); });

  renderUpcoming(); renderRecent();
})();
