
// reservation_summary_hook.js
(function(){
  if(window.__RS_HOOKED__) return; window.__RS_HOOKED__ = true;
  window.addEventListener('reservation:created', (e)=>{
    try{
      const d = e.detail || {};
      if(!d || !d.id || window.__RS_LAST_ID === d.id) return;
      window.__RS_LAST_ID = d.id;
      if(typeof window.showReservationSummary === 'function'){
        window.showReservationSummary(d);
      }
    }catch(_){}
  });
})();
