window.emitReservationCreated = function(payload){
  try{
    const evt = new CustomEvent('reservation:created', { detail: payload || {} });
    window.dispatchEvent(evt);
  }catch(_){}
};
