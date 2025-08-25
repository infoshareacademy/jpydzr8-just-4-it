// Emit custom event after successful reservation creation
// Wywołaj emitReservationCreated({id, seat_id, date, name, email}) po udanym POST /api/reservations
window.emitReservationCreated = function(payload){
  try{
    const evt = new CustomEvent('reservation:created', { detail: payload || {} });
    window.dispatchEvent(evt);
  }catch(_){}
};
