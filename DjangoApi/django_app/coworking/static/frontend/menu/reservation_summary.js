
// reservation_summary.js (persistent, no redirect button)
(function(){
  function pad(n){ return String(n).padStart(2,'0'); }
  function nextDay(iso){ const d=new Date(iso+'T00:00:00'); d.setDate(d.getDate()+1);
    return d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate()); }
  function ymd(iso){ return String(iso).replace(/-/g,''); }

  function buildGoogleUrl({title, date, id, seat, details, location}){
    const start = ymd(date), end = ymd(nextDay(date));
    const params = new URLSearchParams({
      action:'TEMPLATE', text:title||'Reservation', dates:`${start}/${end}`,
      details: details || `Reservation ${id}`, location: location || (seat?`Seat ${seat}`:'')
    });
    return `https://calendar.google.com/calendar/render?${params.toString()}`;
  }

  function ensureICS(){
    if(window.downloadICS) return;
    window.downloadICS = function({title='Reservation', startDate, description='', location=''}){
      if(!startDate){ alert('No date for ICS'); return; }
      const dt = String(startDate).replace(/-/g,'');
      const ics = [
        'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//WorkspaceBookings//EN','BEGIN:VEVENT',
        `UID:${Date.now()}@workspace`,`DTSTAMP:${dt}T090000Z`,
        `DTSTART;VALUE=DATE:${dt}`,`DTEND;VALUE=DATE:${dt}`,
        `SUMMARY:${title}`,`DESCRIPTION:${description}`,`LOCATION:${location}`,
        'END:VEVENT','END:VCALENDAR'
      ].join('\r\n');
      const blob = new Blob([ics], {type:'text/calendar'});
      const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'reservation.ics'; a.click();
    };
  }

  function showReservationSummary({ id, seat_id, date, name, email }){
    ensureICS();
    const modal = document.createElement('div');
    modal.className = 'rs-modal';
    modal.innerHTML = `
      <div class="rs-card" role="dialog" aria-modal="true" aria-labelledby="rs-title">
        <button class="rs-close" aria-label="Close">×</button>
        <div class="rs-head">
          <div class="rs-badge">✔</div>
          <h3 class="rs-title" id="rs-title">Reservation confirmed</h3>
        </div>
        <div class="rs-row"><div class="k">Seat</div><div class="v"><strong>${seat_id||''}</strong></div></div>
        <div class="rs-row"><div class="k">Date</div><div class="v"><strong>${date||''}</strong></div></div>
        <div class="rs-row"><div class="k">ID</div><div class="v"><code>${id||''}</code></div></div>
        ${name||email?`<div class="rs-row"><div class="k">Who</div><div class="v">${name||email}</div></div>`:''}
        <div class="rs-actions">
          <a class="rs-btn primary" id="rsGoogle" target="_blank" rel="noopener">Add to Google Calendar</a>
          <button class="rs-btn" id="rsIcs">Download .ics</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    // Persistent: do NOT close on backdrop click, only via X
    modal.style.display = 'flex';
    modal.addEventListener('click', (e)=>{
      if(e.target === modal){ e.stopPropagation(); e.preventDefault(); }
    });
    modal.querySelector('.rs-close').addEventListener('click', ()=>{
      modal.style.display='none'; modal.remove();
    });

    // Buttons
    const g = modal.querySelector('#rsGoogle');
    g.href = buildGoogleUrl({ title:`Seat ${seat_id}`, date, id, seat:seat_id, details:`Reservation ${id}`, location:`Seat ${seat_id}` });
    modal.querySelector('#rsIcs').addEventListener('click', ()=>{
      window.downloadICS({ title:`Seat ${seat_id}`, startDate:date, description:`Reservation ${id}`, location:`Seat ${seat_id}` });
    });
  }

  window.showReservationSummary = showReservationSummary;
})();
