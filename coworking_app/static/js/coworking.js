/* coworking.js - English, Django-ready frontend logic (localStorage demo) */

(function(){
const STORAGE_KEY = 'coworking_reservations_v1';
const FEATURES_KEY = 'coworking_seat_features_v1';
const CONFIG = { tooltipDelay:150 };

const FEATURE_MAP = {
    '': { name: 'None', cls: '', icon: 'fa-desktop', color: '#4CAF50' },
    'D': { name: 'Docking station', cls: 'seat-reserved-D', icon: 'fa-laptop-house', color:'#FFC107' },
    'S': { name: 'Two screens', cls: 'seat-reserved-S', icon: 'fa-chalkboard-teacher', color:'#03A9F4' },
    'E': { name: 'Electric desk adjustment', cls: 'seat-reserved-E', icon: 'fa-cogs', color:'#9C27B0' },
    'DS': { name: 'Dock & 2 screens', cls: 'seat-reserved-DS', icon: 'fa-laptop-code', color:'#2196F3' },
    'DSE': { name: 'Full equipment', cls: 'seat-reserved-DSE', icon: 'fa-rocket', color:'#FF5722' },
    'X': { name: 'Reserved (seed)', cls: 'seat-reserved', icon:'fa-user-tie', color:'#F44336' }
};

function uid(prefix='r'){ return prefix + '-' + Math.random().toString(36).slice(2,9); }
function mockDelay(ms=300){ return new Promise(r=>setTimeout(r, ms)); }
async function saveReservationToServer(res){ await mockDelay(250); return { ok:true, id:res.id }; }
async function deleteReservationFromServer(id){ await mockDelay(200); return { ok:true }; }
function showToast(msg, timeout=3200){ const t = document.createElement('div'); t.className='toast'; t.innerHTML = msg; document.getElementById('toast-container').appendChild(t); setTimeout(()=>{ t.style.opacity='0'; setTimeout(()=>t.remove(),320); }, timeout); }
function nowISO(){ return new Date().toISOString(); }
function combineDateTime(dateStr, timeStr){ const [y,m,d]=dateStr.split('-').map(Number); const [hh,mm]=timeStr.split(':').map(Number); return new Date(y,m-1,d,hh,mm,0,0).toISOString(); }
function overlaps(aStart,aEnd,bStart,bEnd){ return (new Date(aStart) < new Date(bEnd)) && (new Date(bStart) < new Date(aEnd)); }
function niceDateRange(sISO,eISO){ const s=new Date(sISO), e=new Date(eISO); const opts={ day:'2-digit', month:'2-digit', hour:'2-digit', minute:'2-digit' }; return s.toLocaleString('en-GB',opts) + ' — ' + e.toLocaleString('en-GB',opts); }
function toLocalDateISO(d){ const dt = new Date(d); return dt.toISOString().slice(0,10); }

function loadReservations(){ try{ const j=localStorage.getItem(STORAGE_KEY); return j?JSON.parse(j):[] }catch(e){console.error(e); return []} }
function saveReservations(arr){ localStorage.setItem(STORAGE_KEY, JSON.stringify(arr)); }
function loadFeatures(){ try{ const j=localStorage.getItem(FEATURES_KEY); return j?JSON.parse(j):null }catch(e){return null} }
function saveFeatures(obj){ localStorage.setItem(FEATURES_KEY, JSON.stringify(obj)); }

const floors = [
    { id: 'floor-4-seats', totalSeats: 20 },
    { id: 'floor-5-seats', totalSeats: 30 },
    { id: 'floor-6-seats', totalSeats: 25 },
    { id: 'floor-7-seats', totalSeats: 35 }
];
const possible = ['', 'D','S','E','DS','DSE'];
function pickRandomFeature(){ return possible[Math.floor(Math.random()*possible.length)]; }

function ensureFeatures(){
    let f = loadFeatures();
    if(f) return f;
    f = {};
    floors.forEach(floor=>{
        for(let i=1;i<=floor.totalSeats;i++){
            const id = `${floor.id.split('-')[1]}-${i}`;
            const isReservedVisual = Math.random() > 0.7 ? (Math.random()>0.5 ? 'X' : pickRandomFeature()) : pickRandomFeature();
            f[id] = isReservedVisual;
        }
    });
    saveFeatures(f);
    return f;
}

// legend (feature filters)
const legendRoot = document.getElementById('legend-root');
let activeFeatureFilter = null; // null = no feature filter
let statusFilter = 'all'; // 'all' | 'available' | 'occupied'

function renderLegend(){
    const feats = ensureFeatures();
    legendRoot.innerHTML = '';
    // Build unique feature list from FEATURE_MAP (exclude X)
    const keys = ['', 'D','S','E','DS','DSE'];
    keys.forEach(k=>{
        const fm = FEATURE_MAP[k] || FEATURE_MAP[''];
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.dataset.feat = k;
        item.innerHTML = `<span class="seat-symbol ${fm.cls.replace('seat-','reserved-')||''}"><i class="fas ${fm.icon}"></i></span><span>${fm.name}</span>`;
        item.addEventListener('click', ()=>{
            // toggle feature filter
            if(activeFeatureFilter === k) activeFeatureFilter = null; else activeFeatureFilter = k;
            document.querySelectorAll('.legend-item').forEach(el=> el.classList.remove('active'));
            if(activeFeatureFilter !== null){
                const sel = document.querySelector(`.legend-item[data-feat="${activeFeatureFilter}"]`);
                if(sel) sel.classList.add('active');
            }
            applyFilters();
        });
        legendRoot.appendChild(item);
    });
}

// status filters (All / Available / Occupied)
document.addEventListener('click', (e)=>{
    const sbtn = e.target.closest('#status-filter .filter-btn');
    if(sbtn){
        document.querySelectorAll('#status-filter .filter-btn').forEach(b=>b.classList.remove('active'));
        sbtn.classList.add('active');
        statusFilter = sbtn.dataset.status;
        applyFilters();
    }
});

function buildSeats(){
    const feats = ensureFeatures();
    floors.forEach(floor=>{
        const grid = document.getElementById(floor.id);
        grid.innerHTML = '';
        for(let i=1;i<=floor.totalSeats;i++){
            const seatId = `${floor.id.split('-')[1]}-${i}`;
            const feat = feats[seatId] || '';
            const el = document.createElement('div');
            el.className = 'seat-item-styled';
            const featureKey = feat === 'X' ? 'X' : feat;
            const fm = FEATURE_MAP[featureKey] || FEATURE_MAP[''];
            if(fm.cls) el.classList.add(fm.cls);
            if(featureKey === '') el.classList.add('seat-unreserved');
            const iconClass = fm.icon || 'fa-desktop';
            el.innerHTML = `<span class="seat-icon"><i class="fas ${iconClass}"></i></span><span class="seat-label">${i}(${featureKey || 0})</span>`;
            el.setAttribute('data-seat-id', seatId);
            el.setAttribute('tabindex','0');
            attachSeatHandlers(el, seatId, featureKey);
            grid.appendChild(el);
        }
    });
}

let tooltipTimer = null;
const tooltipEl = document.getElementById('tooltip');
function showTooltipFor(el, content, clientX, clientY){
    tooltipEl.innerHTML = content;
    tooltipEl.style.left = (clientX + 14) + 'px';
    tooltipEl.style.top = (clientY - 8) + 'px';
    tooltipEl.style.opacity = '1';
    tooltipEl.style.transform = 'translateY(0)';
}
function hideTooltip(){ tooltipEl.style.opacity = '0'; tooltipEl.style.transform = 'translateY(-6px)'; }

function attachSeatHandlers(el, seatId, featureKey){
    el.addEventListener('mouseenter', (ev)=>{
        tooltipTimer = setTimeout(()=>{
            const status = isSeatCurrentlyOccupied(seatId) ? 'Occupied' : 'Available';
            const featName = FEATURE_MAP[featureKey] ? FEATURE_MAP[featureKey].name : 'None';
            const content = `<strong>${seatId}</strong><div style="font-size:0.9rem;margin-top:4px">${featName} — ${status}</div>`;
            showTooltipFor(el, content, ev.clientX, ev.clientY);
        }, CONFIG.tooltipDelay);
    });
    el.addEventListener('mousemove', (ev)=>{
        if(tooltipEl.style.opacity === '1'){ tooltipEl.style.left = (ev.clientX + 14) + 'px'; tooltipEl.style.top = (ev.clientY - 8) + 'px'; }
    });
    el.addEventListener('mouseleave', ()=>{ clearTimeout(tooltipTimer); hideTooltip(); });

    el.addEventListener('click', (e)=>{
        const isShift = e.shiftKey;
        if(isShift){ quickReserveToday(seatId, featureKey); }
        else { openSeatModal(seatId, featureKey); }
    });
    el.addEventListener('keydown', (e)=>{ if(e.key==='Enter') openSeatModal(seatId, featureKey); if(e.key===' '){ e.preventDefault(); openSeatModal(seatId, featureKey); } });
}

function isSeatCurrentlyOccupied(seatId){
    const all = loadReservations();
    const now = new Date();
    return all.some(r => r.seatId === seatId && new Date(r.end) > now);
}

function applyFilters(){
    const allSeats = document.querySelectorAll('.seat-item-styled');
    allSeats.forEach(s => s.style.opacity = '0.35');
    allSeats.forEach(s=>{
        const id = s.getAttribute('data-seat-id');
        const feats = ensureFeatures();
        const f = feats[id] || '';
        const occupied = isSeatCurrentlyOccupied(id);
        // check status filter
        let statusOk = true;
        if(statusFilter === 'available' && occupied) statusOk = false;
        if(statusFilter === 'occupied' && !occupied) statusOk = false;
        // check feature filter
        let featureOk = true;
        if(activeFeatureFilter !== null){
            featureOk = (f === activeFeatureFilter);
        }
        if(statusOk && featureOk) s.style.opacity = '1';
    });
}

function renderReservationsList(){
    const root = document.getElementById('reservations-list'); root.innerHTML = '';
    const all = loadReservations().slice();
    if(all.length === 0){ root.innerHTML = '<div class="small muted">No reservations yet.</div>'; }
    else {
        all.sort((a,b)=> new Date(a.start) - new Date(b.start));
        all.forEach(res => {
            const item = document.createElement('div'); item.className='reservation-item';
            const meta = document.createElement('div'); meta.className='reservation-meta';
            meta.innerHTML = `<strong>Seat ${res.seatId}</strong><div class="small">${niceDateRange(res.start, res.end)}</div>`;
            const actions = document.createElement('div');
            const cancelBtn = document.createElement('button'); cancelBtn.className='btn btn-ghost'; cancelBtn.innerHTML='<i class="fas fa-times"></i>'; cancelBtn.title='Cancel';
            cancelBtn.addEventListener('click', ()=> cancelReservationWithUndo(res.id));
            actions.appendChild(cancelBtn);
            item.appendChild(meta); item.appendChild(actions);
            root.appendChild(item);
        });
    }
    refreshAllSeatsFromReservations();
    updateStats();
}

function refreshAllSeatsFromReservations(){
    const feats = ensureFeatures();
    document.querySelectorAll('.seat-item-styled').forEach(el=>{
        const id = el.getAttribute('data-seat-id');
        el.classList.remove('seat-reserved','seat-reserved-D','seat-reserved-S','seat-reserved-E','seat-reserved-DS','seat-reserved-DSE');
        const f = feats[id] || '';
        const fm = FEATURE_MAP[f === 'X' ? 'X' : f] || FEATURE_MAP[''];
        if(fm && fm.cls) el.classList.add(fm.cls);
        if(isSeatCurrentlyOccupied(id)){
            if(!el.classList.contains('seat-reserved')) el.classList.add('seat-reserved');
        } else {
            if(f === '') { el.classList.add('seat-unreserved'); }
        }
    });
    applyFilters();
}

function cancelReservationWithUndo(resId){
    const before = loadReservations();
    const idx = before.findIndex(r=> r.id === resId);
    if(idx === -1) return;
    const removed = before.splice(idx,1)[0];
    saveReservations(before);
    renderReservationsList();
    const undoToast = document.createElement('div'); undoToast.className='toast';
    undoToast.innerHTML = `Reservation for ${removed.seatId} cancelled. <button id="undo-btn" class="btn btn-ghost" style="margin-left:8px;">Undo</button>`;
    document.getElementById('toast-container').appendChild(undoToast);
    let undone=false;
    const undoBtn = undoToast.querySelector('#undo-btn');
    const t = setTimeout(async ()=>{ if(!undone){ await deleteReservationFromServer(resId); undoToast.style.opacity='0'; setTimeout(()=>undoToast.remove(),300); showToast('Reservation permanently removed.'); refreshAllSeatsFromReservations(); } },6000);
    undoBtn.addEventListener('click', ()=>{ undone=true; clearTimeout(t); const now = loadReservations(); now.push(removed); saveReservations(now); renderReservationsList(); undoToast.style.opacity='0'; setTimeout(()=>undoToast.remove(),220); showToast('Reservation restored.'); });
}

function openSeatModal(seatId, featureKey){
    const root = document.getElementById('modal-root'); root.innerHTML=''; root.style.display='block';
    const bg = document.createElement('div'); bg.className='modal-backdrop';
    const modal = document.createElement('div'); modal.className='modal';
    const feat = FEATURE_MAP[featureKey] || FEATURE_MAP[''];
    const all = loadReservations();
    const upcoming = all.filter(r=> r.seatId === seatId && new Date(r.end) > new Date()).sort((a,b)=> new Date(a.start)-new Date(b.start));
    let upcomingHtml = '<div class="small muted">No upcoming reservations.</div>';
    if(upcoming.length){ upcomingHtml = '<ul style="margin:6px 0 0 16px;">' + upcoming.map(u=> `<li class="small">${niceDateRange(u.start,u.end)}</li>`).join('') + '</ul>'; }
    modal.innerHTML = `
        <h4>Seat ${seatId}</h4>
        <div class="small muted">Amenity: <strong>${feat.name}</strong></div>
        <div style="height:10px"></div>
        <div class="small muted">Upcoming reservations for this seat:</div>
        <div style="margin-top:6px">${upcomingHtml}</div>
        <hr style="margin:12px 0;border:none;border-top:1px solid #eef4fb;" />
        <div class="form-row">
            <div class="col"><label class="small">Date</label><input type="date" id="res-date" class="input" value="${toLocalDateISO(new Date())}"></div>
            <div class="col"><label class="small">Start</label><input type="time" id="res-start" class="input" value="09:00"></div>
        </div>
        <div class="form-row">
            <div class="col"><label class="small">End</label><input type="time" id="res-end" class="input" value="11:00"></div>
            <div class="col"><div class="small muted">Amenity (assigned): <strong>${feat.name}</strong></div></div>
        </div>
        <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:12px;">
            <button class="btn btn-ghost" id="cancel-modal">Cancel</button>
            <button class="btn btn-primary" id="confirm-res">Reserve</button>
        </div>
    `;
    bg.appendChild(modal); root.appendChild(bg);
    document.getElementById('cancel-modal').addEventListener('click', closeModal);
    bg.addEventListener('click', (e)=> { if(e.target===bg) closeModal(); });
    document.getElementById('confirm-res').addEventListener('click', async ()=>{
        const date = document.getElementById('res-date').value;
        const startT = document.getElementById('res-start').value;
        const endT = document.getElementById('res-end').value;
        if(!date || !startT || !endT){ showToast('Please provide date and times.'); return; }
        const startISO = combineDateTime(date, startT);
        const endISO = combineDateTime(date, endT);
        if(new Date(startISO) >= new Date(endISO)){ showToast('End time must be after start time.'); return; }
        const all = loadReservations();
        const conflict = all.find(r=> r.seatId === seatId && overlaps(startISO, endISO, r.start, r.end));
        if(conflict){ showToast('This seat is already reserved for the selected time range.'); return; }
        const reservation = { id: uid('res'), seatId, start: startISO, end: endISO, option: featureKey, createdAt: nowISO() };
        all.push(reservation); saveReservations(all); renderReservationsList(); closeModal(); markSeatReserved(seatId); showToast('Reservation created.'); const resp = await saveReservationToServer(reservation); if(!resp || !resp.ok) showToast('Warning: server save failed (mock).');
    });
}
function closeModal(){ const root=document.getElementById('modal-root'); root.innerHTML=''; root.style.display='none'; }

function markSeatReserved(seatId){ const el = document.querySelector(`[data-seat-id="${seatId}"]`); if(!el) return; el.classList.remove('seat-unreserved'); if(!el.classList.contains('seat-reserved')) el.classList.add('seat-reserved'); }

async function quickReserveToday(seatId, featureKey){
    if(isSeatCurrentlyOccupied(seatId)){ showToast('This seat is already occupied.'); return; }
    const today = new Date(); const dateStr = toLocalDateISO(today);
    const startISO = combineDateTime(dateStr, '09:00'); const endISO = combineDateTime(dateStr, '17:00');
    const reservation = { id: uid('res'), seatId, start: startISO, end: endISO, option: featureKey, createdAt: nowISO() };
    const all = loadReservations(); all.push(reservation); saveReservations(all); renderReservationsList(); markSeatReserved(seatId); showToast('Quick reservation created.'); const resp = await saveReservationToServer(reservation); if(!resp || !resp.ok) showToast('Warning: server save failed (mock).');
}

document.addEventListener('click', (e)=>{
    if(e.target.closest('#export-json')){
        const data = loadReservations(); const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }); const url = URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='reservations.json'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url); showToast('Reservations exported.');
    } else if(e.target.closest('#import-json')){
        const input=document.createElement('input'); input.type='file'; input.accept='application/json'; input.onchange = (ev)=>{ const f = ev.target.files[0]; if(!f) return; const rd = new FileReader(); rd.onload = ()=>{ try{ const parsed = JSON.parse(rd.result); if(!Array.isArray(parsed)) throw new Error('Invalid'); saveReservations(parsed); renderReservationsList(); showToast('Reservations imported.'); }catch(err){ showToast('Import error: invalid file.'); } }; rd.readAsText(f); }; input.click();
    } else if(e.target.closest('#clear-all')){
        if(!confirm('Are you sure you want to remove all reservations?')) return; localStorage.removeItem(STORAGE_KEY); renderReservationsList(); showToast('Reservations cleared.');
    }
});

function updateStats(){
    const allSeats = document.querySelectorAll('.seat-item-styled');
    const totalSeats = allSeats.length;
    const all = loadReservations();
    let occupiedCount = 0;
    allSeats.forEach(s=>{ const id = s.getAttribute('data-seat-id'); if(isSeatCurrentlyOccupied(id)) occupiedCount++; });
    const freeCount = totalSeats - occupiedCount;
    document.getElementById('stat-free').textContent = freeCount;
    document.getElementById('stat-occupied').textContent = occupiedCount;
    const todayISO = toLocalDateISO(new Date());
    const startOfDay = new Date(todayISO + 'T00:00:00').toISOString();
    const endOfDay = new Date(todayISO + 'T23:59:59').toISOString();
    const todayCount = all.filter(r=> overlaps(r.start, r.end, startOfDay, endOfDay)).length;
    document.getElementById('stat-today').textContent = todayCount;
    const feats = ensureFeatures();
    const counts = {}; Object.keys(FEATURE_MAP).forEach(k=> counts[k]=0);
    Object.keys(feats).forEach(id=>{ const f = feats[id] || ''; counts[f || ''] = (counts[f || ''] || 0) + 1; });
    const fcRoot = document.getElementById('feature-counts'); fcRoot.innerHTML = '';
    const displayOrder = ['', 'D','S','E','DS','DSE'];
    displayOrder.forEach(k=>{
        const fm = FEATURE_MAP[k] || FEATURE_MAP[''];
        const row = document.createElement('div'); row.className='stat-row';
        const left = document.createElement('div'); left.className='stat-left';
        const icon = document.createElement('span'); icon.className='small-icon'; icon.style.background = fm.color; icon.innerHTML = `<i class="fas ${fm.icon}"></i>`;
        left.appendChild(icon);
        const label = document.createElement('div'); label.innerHTML = `<div style="font-weight:600">${fm.name}</div>`;
        left.appendChild(label);
        const cnt = document.createElement('div'); cnt.textContent = counts[k] || 0;
        row.appendChild(left); row.appendChild(cnt);
        fcRoot.appendChild(row);
    });
}

function markAllReservedFromStored(){
    document.querySelectorAll('.seat-item-styled').forEach(el=> el.classList.remove('seat-unreserved'));
    const all = loadReservations(); all.forEach(r=>{ const el = document.querySelector(`[data-seat-id="${r.seatId}"]`); if(el) el.classList.add('seat-reserved'); });
}

function generateSeedReservations(){
    const now = new Date();
    function addDays(n){ const d = new Date(now); d.setDate(d.getDate()+n); return d; }
    const examples = [ { seat:'4-3', date:addDays(0) }, { seat:'5-10', date:addDays(1) }, { seat:'6-7', date:addDays(2) }, { seat:'7-15', date:addDays(0) } ];
    return examples.map((ex, idx)=>{ const start = new Date(ex.date); start.setHours(9+idx,0,0,0); const end = new Date(ex.date); end.setHours(11+idx,0,0,0); return { id: uid('seed'), seatId: ex.seat, start: start.toISOString(), end: end.toISOString(), createdAt: nowISO(), meta:{ note:'seed' } }; });
}

document.addEventListener('DOMContentLoaded', ()=>{
    renderLegend();
    buildSeats();
    if(!localStorage.getItem(STORAGE_KEY)){ saveReservations(generateSeedReservations()); }
    renderReservationsList();
    markAllReservedFromStored();
    updateStats();
});

window.addEventListener('scroll', ()=> hideTooltip());
window.addEventListener('resize', ()=> hideTooltip());

window.__coworking = { loadReservations, saveReservations, ensureFeatures, rebuild: ()=>{ renderLegend(); buildSeats(); renderReservationsList(); updateStats(); } };
})();