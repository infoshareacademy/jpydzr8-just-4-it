window.toast=(m,ok=true)=>{const el=document.createElement('div');el.textContent=m;el.style.position='fixed';el.style.bottom='20px';el.style.right='20px';el.style.padding='10px 14px';el.style.borderRadius='12px';el.style.background=ok?'#16a34a':'#ef4444';el.style.color='#fff';el.style.fontSize='14px';el.style.boxShadow='0 10px 25px rgba(0,0,0,.15)';document.body.appendChild(el);setTimeout(()=>el.remove(),2200);};
document.addEventListener('htmx:afterSwap',e=>{ if(e.detail.target && e.detail.target.id==='modal-root'){ const i=e.detail.target.querySelector('input,select,textarea,button'); if(i) setTimeout(()=>i.focus(),60);} });

// Tooltip for desk markers
let tip=null; function showTip(text,x,y){ if(!tip){ tip=document.createElement('div'); tip.className='tooltip'; document.body.appendChild(tip);} tip.textContent=text; tip.style.left=x+'px'; tip.style.top=y+'px'; } function hideTip(){ if(tip){ tip.remove(); tip=null; } }
document.addEventListener('mousemove',e=>{ const hit=e.target.closest('.desk-hit'); if(hit){ const marker=hit.parentElement; const label=marker?.dataset?.id?('Stanowisko '+marker.dataset.id):''; showTip(label,e.clientX,e.clientY);} else hideTip(); });

// Position desk markers by xpct/ypct (viewBox 1200x800)
function placeDeskMarkers(){ 
  console.log('Positioning desk markers...');
  const markers=document.querySelectorAll('svg .desk-marker'); 
  console.log(`Found ${markers.length} markers`);
  markers.forEach(m=>{ 
    const xPct=parseFloat(m.dataset.xpct||'0'), yPct=parseFloat(m.dataset.ypct||'0'); 
    const x=(xPct/100)*1200, y=(yPct/100)*800; 
    console.log(`Marker ${m.dataset.id}: x_pct=${xPct}, y_pct=${yPct}, x=${x}, y=${y}`);
    m.setAttribute('transform', `translate(${x.toFixed(2)},${y.toFixed(2)})`); 
  }); 
}
document.addEventListener('DOMContentLoaded', placeDeskMarkers);

// Availability coloring for desk markers
async function updateAvailabilitySVG(){ const root=document.getElementById('floor-root'); if(!root) return; const floor=root.dataset.floor; const date=document.getElementById('pref_date')?.value||''; const from=document.getElementById('pref_from')?.value||'09:00'; const to=document.getElementById('pref_to')?.value||'17:00'; const q=new URLSearchParams({date,from,to}).toString(); const res=await fetch(`/floor/${floor}/availability/?`+q); const data=await res.json(); document.querySelectorAll('svg .desk-dot').forEach(el=>el.classList.remove('free','busy')); (data.available||[]).forEach(id=>{ const marker=document.querySelector(`[data-id="${id}"]`); const dot=marker?.querySelector('.desk-dot'); if(dot) dot.classList.add('free'); }); (data.reserved||[]).forEach(id=>{ const marker=document.querySelector(`[data-id="${id}"]`); const dot=marker?.querySelector('.desk-dot'); if(dot) dot.classList.add('busy'); }); toast && toast('Zajętość uaktualniona'); }
document.addEventListener('DOMContentLoaded',()=>{ document.getElementById('btn-availability')?.addEventListener('click', updateAvailabilitySVG); setTimeout(updateAvailabilitySVG, 300); });

// Zoom & pan for SVG
document.addEventListener('DOMContentLoaded', function() {
  const svg = document.querySelector('svg');
  if (!svg) return;
  
  let s = 1.3, tx = 0, ty = 0, drag = false, lx = 0, ly = 0;
  
  const apply = () => {
    svg.style.transform = `translate(${tx}px, ${ty}px) scale(${s})`;
    svg.style.transformOrigin = '50% 50%';
  };
  
  // Zoom in
  document.getElementById('zoom-in')?.addEventListener('click', () => {
    s = Math.min(2.5, s + 0.1);
    apply();
  });
  
  // Zoom out
  document.getElementById('zoom-out')?.addEventListener('click', () => {
    s = Math.max(1, s - 0.1);
    apply();
  });
  
  // Reset zoom
  document.getElementById('zoom-reset')?.addEventListener('click', () => {
    s = 1.3;
    tx = 0;
    ty = 0;
    apply();
  });
  
  // Mouse drag
  svg.addEventListener('mousedown', e => {
    if (e.target.classList.contains('seat-hit')) return;
    drag = true;
    lx = e.clientX;
    ly = e.clientY;
  });
  
  document.addEventListener('mousemove', e => {
    if (!drag) return;
    tx += e.clientX - lx;
    ty += e.clientY - ly;
    lx = e.clientX;
    ly = e.clientY;
    apply();
  });
  
  document.addEventListener('mouseup', () => drag = false);
  
  // Mouse wheel zoom
  svg.addEventListener('wheel', e => {
    e.preventDefault();
    s = Math.max(1, Math.min(2.5, s + (e.deltaY > 0 ? -0.1 : 0.1)));
    apply();
  }, { passive: false });
  
  // Apply initial zoom
  apply();
});
