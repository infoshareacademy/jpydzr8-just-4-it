// cancel_wire.js — Global: handle [data-cancel-id] or resolve via [data-cancel-seat][data-cancel-date]
(function(){
  const token = localStorage.getItem('token') || '';
  const auth = token ? { Authorization: 'Bearer '+token } : {};

  async function apiCheck(seat, date){
    const res = await fetch(`/api/reservations/check/${encodeURIComponent(seat)}/${encodeURIComponent(date)}`, { headers: auth });
    if(!res.ok) return null;
    return await res.json();
  }
  async function apiDelete(id){
    const res = await fetch('/api/reservations/'+encodeURIComponent(id), { method:'DELETE', headers: auth });
    return res.ok;
  }

  document.addEventListener('click', async (e)=>{
    const btn = e.target.closest('[data-cancel-id],[data-cancel-seat][data-cancel-date]');
    if(!btn) return;
    e.preventDefault();

    let id = btn.getAttribute('data-cancel-id');
    if(!id){
      const seat = btn.getAttribute('data-cancel-seat');
      const date = btn.getAttribute('data-cancel-date');
      if(seat && date){
        const chk = await apiCheck(seat, date);
        if(chk && chk.reserved && chk.reservation_id) id = chk.reservation_id;
      }
      if(!id){ alert('No reservations found to cancel.'); return; }
    }

    if(!confirm('Cancel your reservation '+id+'?')) return;
    const ok = await apiDelete(id);
    if(ok){
      const row = btn.closest('.cancel-row') || btn.closest('[data-reservation-row]');
      if(row) row.remove();
      window.dispatchEvent(new CustomEvent('reservation:deleted', { detail: { id } }));
    }else{
      alert('Cancellation failed.');
    }
  });
})();
