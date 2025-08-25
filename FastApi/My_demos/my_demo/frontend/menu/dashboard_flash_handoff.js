
(function(){
  try{
    const raw = sessionStorage.getItem('flash_reservation');
    if(!raw) return;
    sessionStorage.removeItem('flash_reservation');
    const d = JSON.parse(raw);
    window.dispatchEvent(new CustomEvent('reservation:created', { detail: d }));
  }catch(_){}
})();
