async function api(path, method='GET', body=null){
  const token = localStorage.getItem('token');
  const headers = {'Content-Type':'application/json'};
  if (token) headers['Authorization'] = 'Bearer ' + token;
  const r = await fetch(path, { method, headers, body: body ? JSON.stringify(body) : null });
  let data = {};
  try { data = await r.json(); } catch(_) {}
  if(!r.ok){ throw new Error((data && data.detail) || r.statusText); }
  return data;
}

async function isSeatReservedOnDate(seatId, dateStr){
  const res = await api(`/api/reservations/seat/${encodeURIComponent(seatId)}?date=${encodeURIComponent(dateStr)}`);
  return res.reserved;
}

async function createReservation({seatId, date, name, email, notes}){
  return await api('/api/reservations', 'POST', { seat_id: seatId, date, name, email, notes });
}

async function cancelReservation(reservationId){
  return await api(`/api/reservations/${encodeURIComponent(reservationId)}`, 'DELETE');
}

async function listReservations(date){
  const url = date ? `/api/reservations?date=${encodeURIComponent(date)}` : '/api/reservations';
  return await api(url);
}
