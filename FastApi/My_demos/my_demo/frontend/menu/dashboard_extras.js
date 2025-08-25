
(function(){
  const API = location.origin;
  const token = localStorage.getItem('token') || '';
  const auth = token ? { Authorization: 'Bearer '+token } : {};

  const html = document.documentElement;
  function applyTheme(th){ html.setAttribute('data-theme', th === 'dark' ? 'dark' : 'light'); }
  applyTheme(localStorage.getItem('theme') || 'light');
  document.getElementById('themeToggle')?.addEventListener('click', () => {
    const cur = (html.getAttribute('data-theme') || 'light') === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', cur); applyTheme(cur);
  });

  const goLogout = (e)=>{ e?.preventDefault(); try{localStorage.removeItem('token');}catch(_){}; location.href='/logout'; };
  document.getElementById('logoutBtn')?.addEventListener('click', goLogout);
  document.getElementById('logoutTile')?.addEventListener('click', goLogout);

  if(window.Toastify && !sessionStorage.getItem('welcomed')){
    sessionStorage.setItem('welcomed', '1');
    Toastify({ text: "Welcome back! 🎉", duration: 2200, gravity: "top", position: "right", close: true }).showToast();
  }

  window.downloadICS = function({title='Reservation', startDate, description='', location=''}){
    const dt = startDate.replace(/-/g,''); 
    const ics = [
      'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-
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

  const calEl = document.getElementById('calendar');
  let calendar = null;
  if(calEl && window.FullCalendar){
    calendar = new FullCalendar.Calendar(calEl, {
      initialView: 'dayGridMonth',
      height: 'auto',
      selectable: true,
      editable: true,
      eventDurationEditable: false,
      headerToolbar: { left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek,timeGridDay' },
      events: [],
      dateClick: (info)=>{
        document.dispatchEvent(new CustomEvent('qb:open', { detail: { date: info.dateStr } }));
      },
      eventDrop: async (info)=>{
        try{
          const res = await fetch(`/api/reservations/${encodeURIComponent(info.event.id)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', ...auth },
            body: JSON.stringify({ date: info.event.startStr.slice(0,10) })
          });
          if(!res.ok){
            if(window.Toastify) Toastify({text:'Move rejected', duration:2000, gravity:'bottom'}).showToast();
            info.revert();
          }else{
            if(window.Toastify) Toastify({text:'Moved ✔', duration:1500, gravity:'bottom'}).showToast();
          }
        }catch(_){ info.revert(); }
      }
    });
    calendar.render();
  }

  async function listRange(from, to){
    try{
      const url = new URL('/api/reservations', API);
      if(from) url.searchParams.set('date_from', from);
      if(to)   url.searchParams.set('date_to', to);
      const res = await fetch(url, { headers: auth });
      if(!res.ok) return [];
      const arr = await res.json();
      return (arr||[]).map(r => ({ id: r.id, title: `${r.seat_id} – ${r.name || r.email || 'User'}`, start: r.date }));
    }catch(_){ return []; }
  }

  function dateISO(d){ const p=n=>String(n).padStart(2,'0'); return d.getFullYear()+"-"+p(d.getMonth()+1)+"-"+p(d.getDate()); }

  async function refreshCalendar(){
    if(!calendar) return;
    const now = new Date();
    const from = dateISO(new Date(now.getFullYear(), now.getMonth(), now.getDate() - 14));
    const to   = dateISO(new Date(now.getFullYear(), now.getMonth(), now.getDate() + 90));
    const events = await listRange(from,to);
    calendar.removeAllEvents(); calendar.addEventSource(events);
  }

  refreshCalendar();
  setInterval(refreshCalendar, 15000);
  document.addEventListener('visibilitychange', ()=>{ if(document.visibilityState==='visible') refreshCalendar(); });

  window.addEventListener('reservation:created', (e)=>{
    const { id, seat_id, date, name, email } = e.detail || {};
    if(calendar && id && seat_id && date){
      calendar.addEvent({ id, title: `${seat_id} – ${name || email || 'You'}`, start: date });
    }else{
      refreshCalendar();
    }
  });

  const chartEl = document.getElementById('resvChart');
  if(chartEl && window.Chart){
    const days = 14;
    const labels = Array.from({length: days}, (_,i)=>{
      const dt = new Date(); dt.setDate(dt.getDate()-(days-1-i));
      return (dt.getMonth()+1)+"/"+dt.getDate();
    });
    const data = labels.map(()=> Math.floor(Math.random()*5)+ (Math.random()<.2?5:0));
    new Chart(chartEl.getContext('2d'), {
      type: 'bar',
      data: { labels, datasets: [{ label: 'Reservations', data }]},
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
    });
  }

  (async function loadUser(){
    if(!token) return;
    try{
      const res = await fetch('/api/auth/me', { headers: auth });
      if(res.ok){ const me = await res.json(); const span = document.getElementById('userName'); if(span) span.textContent = me.full_name || me.email || 'User'; }
    }catch(_){}
  })();
})();
