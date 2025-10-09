window.downloadICS = function({title='Reservation', startDate, description='', location=''}){
  if(!startDate){ alert('No date for ICS'); return; }
  const dt = String(startDate).replace(/-/g,''); // YYYYMMDD
  const ics = [
    'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//WorkspaceBookings//EN','BEGIN:VEVENT',
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
