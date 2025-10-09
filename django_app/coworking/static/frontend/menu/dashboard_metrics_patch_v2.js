
(function(){
  const token = localStorage.getItem('token') || '';
  const auth = token ? { Authorization: 'Bearer '+token } : {};

  const elNext  = document.getElementById('sumNext');
  const elLast  = document.getElementById('sumLast');
  const elCount = document.getElementById('sumCount');
  const elIcs   = document.getElementById('sumIcs');

  const chartCanvas =
      document.getElementById('resvChart')
   || document.querySelector('canvas#reservationsLast14')
   || document.querySelector('canvas[data-chart="last14"]');

  const myList =
      document.getElementById('myReservationsList')
   || document.getElementById('myReservations')
   || document.getElementById('sumList')
   || document.querySelector('[data-list="my-reservations"]');

  const p2 = n => String(n).padStart(2,'0');
  const iso = d => d.getFullYear() + '-' + p2(d.getMonth()+1) + '-' + p2(d.getDate());
  const add = (d, days) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + days);
  const today = () => { const d = new Date(); return new Date(d.getFullYear(), d.getMonth(), d.getDate()); };

  async function apiList({from, to}){
    const url = new URL('/api/reservations', location.origin);
    if(from) url.searchParams.set('date_from', from);
    if(to)   url.searchParams.set('date_to', to);
    const res = await fetch(url, { headers: auth });
    if(!res.ok) { console.warn('[metrics_v2] apiList failed', res.status); return []; }
    return await res.json();
  }

  async function refreshSummary(items){
    try{
      const now = today();
      const nowIso = iso(now);
      let next = null, last = null, upcoming = 0;

      for(const r of items){
        if(!r.date) continue;
        if(r.date >= nowIso){
          if(!next || r.date < next.date) next = r;
          if(r.date <= iso(add(now, 30))) upcoming++;
        }else{
          if(!last || r.date > last.date) last = r;
        }
      }

      if(elNext)  elNext.textContent  = next ? `${next.date} (seat ${next.seat_id})` : '—';
      if(elLast)  elLast.textContent  = last ? `${last.date} (seat ${last.seat_id})` : '—';
      if(elCount) elCount.textContent = String(upcoming);

      if(elIcs){
        elIcs.onclick = (e)=>{
          e.preventDefault();
          if(!next){ return; }
          const dt = String(next.date).replace(/-/g,'');
          const ics = [
            'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//WorkspaceBookings//EN','BEGIN:VEVENT',
            `UID:${Date.now()}@workspace`,
            `DTSTAMP:${dt}T090000Z`,
            `DTSTART;VALUE=DATE:${dt}`,
            `DTEND;VALUE=DATE:${dt}`,
            `SUMMARY:Seat ${next.seat_id}`,
            `DESCRIPTION:Reservation ${next.id}`,
            `LOCATION:Seat ${next.seat_id}`,
            'END:VEVENT','END:VCALENDAR'
          ].join('\r\n');
          const blob = new Blob([ics], {type:'text/calendar'});
          const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'reservation.ics'; a.click();
        };
      }
    }catch(err){
      console.error('[metrics_v2] summary error', err);
    }
  }

  function renderMyReservations(items){
    if(!myList) return;
    const nowIso = iso(today());
    const upcoming = items.filter(r => r.date >= nowIso).sort((a,b)=> a.date.localeCompare(b.date));
    const past = items.filter(r => r.date < nowIso).sort((a,b)=> b.date.localeCompare(a.date));
    const rows = [...upcoming, ...past].slice(0, 12);

    myList.innerHTML = '';
    if(!rows.length){
      myList.innerHTML = '<li class="muted">No reservations yet.</li>';
      return;
    }
    for(const r of rows){
      const li = document.createElement('li');
      li.setAttribute('data-reservation-row','');
      li.innerHTML = `<span>${r.date}</span> • <strong>${r.seat_id}</strong> <small>(id ${r.id})</small>
                      <button class="mini-cancel" data-cancel-id="${r.id}" style="margin-left:8px">Cancel</button>`;
      myList.appendChild(li);
    }
  }

  let chart = null;
  function renderChart(items){
    if(!chartCanvas || typeof Chart === 'undefined') return;
    try{
      const now = today();
      const labels = [];
      const counts = [];
      const map = {};
      for(let i=13; i>=0; i--){
        const d = iso(add(now, -i));
        labels.push(d);
        map[d] = 0;
      }
      for(const r of items){
        if(r.date && (r.date in map)) map[r.date]++;
      }
      for(const d of labels) counts.push(map[d]);

      if(!chart){
        chart = new Chart(chartCanvas.getContext('2d'), {
          type: 'bar',
          data: { labels, datasets: [{ label: 'Reservations', data: counts }] },
          options: {
            responsive: true,
            animation: false,
            scales: { y: { beginAtZero: true, precision: 0 } },
            plugins: { legend: { display:false } }
          }
        });
      }else{
        chart.data.labels = labels;
        chart.data.datasets[0].data = counts;
        chart.update();
      }
    }catch(err){
      console.error('[metrics_v2] chart error', err);
    }
  }

  async function fullRefresh(){
    const now = today();
    const from = iso(add(now, -60));
    const to   = iso(add(now,  60));
    const items = await apiList({ from, to });
    renderChart(items);        // last 14 days
    renderMyReservations(items);
    refreshSummary(items);
  }

  const debounced = (()=>{
    let t=null; return ()=>{ clearTimeout(t); t=setTimeout(fullRefresh, 120); };
  })();
  window.addEventListener('reservation:created', debounced);
  window.addEventListener('reservation:deleted', debounced);
  window.addEventListener('reservation:updated', debounced);

  setInterval(fullRefresh, 15000);

  fullRefresh();
})();
