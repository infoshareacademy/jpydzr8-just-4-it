
const floors = [
  { id: 'floor-4-seats', totalSeats: 20, floor: 4 },
  { id: 'floor-5-seats', totalSeats: 30, floor: 5 },
  { id: 'floor-6-seats', totalSeats: 25, floor: 6 },
  { id: 'floor-7-seats', totalSeats: 35, floor: 7 }
];
const enhancements = ['D', 'S', 'E', 'DS', 'DSE', '0'];
const enhancementIcon = (enh) => ({
  'D':'fa-laptop-house','S':'fa-chalkboard-teacher','E':'fa-cogs','DS':'fa-laptop-code','DSE':'fa-rocket','0':'fa-desktop'
}[enh] || 'fa-desktop');


const LS_KEY = 'reservations_v1';
const getReservations = () => JSON.parse(localStorage.getItem(LS_KEY) || '[]');
const setReservations = (arr) => localStorage.setItem(LS_KEY, JSON.stringify(arr));

function genId () {
  const rnd = Math.random().toString(36).slice(2,8).toUpperCase();
  const t = Date.now().toString(36).toUpperCase();
  return `R-${t}-${rnd}`;
}

function isSeatReservedOnDate(seatId, dateStr) {
  return getReservations().some(r => r.seatId === seatId && r.date === dateStr);
}


function buildGrids() {
  floors.forEach(floor => {
    const grid = document.getElementById(floor.id);
    grid.innerHTML = '';
    for (let i = 1; i <= floor.totalSeats; i++) {
      const seat = document.createElement('div');
      seat.classList.add('seat-item-styled');
      const enhancement = enhancements[Math.floor(Math.random() * enhancements.length)];
      const seatId = `${floor.floor}-${i}`;
      seat.dataset.seatId = seatId;
      seat.dataset.feature = enhancement;
      seat.dataset.status = 'free';

      
      const preReserved = Math.random() > 0.7;
      let iconClass = enhancementIcon(enhancement);
      if (preReserved && enhancement !== '0') {
        seat.classList.add(`seat-reserved${enhancement==='0' ? '' : '-' + enhancement}`);
        seat.dataset.status = 'reserved';
        if (enhancement === '0') iconClass = 'fa-user-tie';
      } else {
        seat.classList.add('seat-unreserved');
      }

      seat.innerHTML = `<span class="seat-icon"><i class="fas ${iconClass}"></i></span><span class="seat-label">${i}(${enhancement})</span>`;
      grid.appendChild(seat);
    }
  });
}


function applyFilters() {
  const q = document.getElementById('searchSeat').value.trim().toLowerCase();
  const s = document.getElementById('filterStatus').value;
  const f = document.getElementById('filterFeature').value;
  document.querySelectorAll('.seats-grid .seat-item-styled').forEach(el => {
    const matchesQ = q === '' || (el.dataset.seatId.toLowerCase().includes(q));
    const matchesS = s === 'all' || el.dataset.status === s;
    const matchesF = f === 'all' || el.dataset.feature === f;
    el.style.display = (matchesQ && matchesS && matchesF) ? '' : 'none';
  });
}


const modal = document.getElementById('reserveModal');
const openModal = () => modal.classList.add('show');
const closeModal = () => modal.classList.remove('show');
document.querySelectorAll('[data-close]').forEach(btn => btn.addEventListener('click', closeModal));


let fp;
function initDatepicker() {
  if (fp) { fp.destroy(); }
  fp = flatpickr('#formDate', {
    dateFormat: 'Y-m-d',
    minDate: 'today',
    disableMobile: false
  });
}


let selectedSeat = null;
function attachSeatHandlers() {
  document.querySelectorAll('.seat-item-styled').forEach(seat => {
    seat.addEventListener('click', () => {
      const seatId = seat.dataset.seatId;
      selectedSeat = seatId;
      document.getElementById('formSeat').value = seatId;
      document.getElementById('formName').value = '';
      document.getElementById('formEmail').value = '';
      document.getElementById('formDate').value = '';
      document.getElementById('formNotes').value = '';
      document.getElementById('reservationInfo').textContent = 'Select a date and fill in the details';
      initDatepicker();
      openModal();
    });
  });
}

document.getElementById('reserveForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const name = document.getElementById('formName').value.trim();
  const email = document.getElementById('formEmail').value.trim();
  const date = document.getElementById('formDate').value.trim();
  const notes = document.getElementById('formNotes').value.trim();
  const seatId = selectedSeat;

  if (!seatId || !name || !email || !date) return;

  if (isSeatReservedOnDate(seatId, date)) {
    document.getElementById('reservationInfo').textContent = 'This place is already booked for this date';
    return;
  }

  const id = genId();
  const res = { id, seatId, name, email, date, notes, createdAt: new Date().toISOString() };
  const all = getReservations();
  all.push(res);
  setReservations(all);

  document.getElementById('reservationInfo').innerHTML = `Reserved ✔ — ID: <strong>${id}</strong>. Keep this ID until canceled.`;
  updateSummary();

  
  if (window.emitReservationCreated) {
    window.emitReservationCreated({
      id, seat_id: seatId, date, name, email
    });
  }

  closeModal();
});


function updateSummary() {
  const box = document.getElementById('summary');
  const all = getReservations().sort((a,b) => a.date.localeCompare(b.date));
  if (!all.length) {
    box.textContent = 'No reservations. Click on an empty spot to add a new one.';
    return;
  }
  const items = all.slice(0, 10).map(r => `<span class="badge">${r.date} • ${r.seatId} • ${r.name} • ${r.id}</span>`).join(' ');
  box.innerHTML = `<strong>Upcoming bookings:</strong><br/>${items}`;
}


const cancelDate = document.getElementById('cancelDate');
flatpickr(cancelDate, { dateFormat: 'Y-m-d' });

function renderCancelResults(list) {
  const wrap = document.getElementById('cancelResults');
  if (!list.length) { wrap.innerHTML = '<div class="tiny-note">No results found.</div>'; return; }
  wrap.innerHTML = list.map(r => `
    <div class="result-card">
      <div>
        <div><strong>${r.name}</strong> <span class="muted">(${r.email})</span></div>
        <div><span class="badge">ID: ${r.id}</span> <span class="badge">Miejsce: ${r.seatId}</span> <span class="badge">Data: ${r.date}</span></div>
      </div>
      <button class="btn" data-cancel="${r.id}"><i class="fas fa-ban"></i> Anuluj</button>
    </div>
  `).join('');
  wrap.querySelectorAll('[data-cancel]').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-cancel');
      const all = getReservations();
      const idx = all.findIndex(r => r.id === id);
      if (idx >= 0) {
        all.splice(idx,1);
        setReservations(all);
        renderCancelResults(all);
        updateSummary();
      }
    });
  });
}

document.getElementById('btnFind').addEventListener('click', () => {
  const id = document.getElementById('cancelId').value.trim();
  const date = document.getElementById('cancelDate').value.trim();
  let list = getReservations();
  if (id) list = list.filter(r => r.id.toLowerCase().includes(id.toLowerCase()));
  if (date) list = list.filter(r => r.date === date);
  renderCancelResults(list);
});
document.getElementById('btnListAll').addEventListener('click', () => renderCancelResults(getReservations()));


document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const tab = btn.dataset.tab;
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.getElementById(`tab-${tab}`).classList.add('active');
  });
});


document.addEventListener('DOMContentLoaded', () => {
  buildGrids();
  attachSeatHandlers();
  updateSummary();
  document.getElementById('searchSeat').addEventListener('input', applyFilters);
  document.getElementById('filterStatus').addEventListener('change', applyFilters);
  document.getElementById('filterFeature').addEventListener('change', applyFilters);
});



if (document.getElementById('results')) {
  flatpickr('#filterDate', { dateFormat: 'Y-m-d' });

  function exportData(format) {
    const data = getReservations();
    if (format === 'csv') {
      const header = Object.keys(data[0] || {}).join(',') + '\n';
      const rows = data.map(r => Object.values(r).join(',')).join('\n');
      const blob = new Blob([header + rows], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'rezerwacje.csv'; a.click();
      URL.revokeObjectURL(url);
    }
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'rezerwacje.json'; a.click();
      URL.revokeObjectURL(url);
    }
  }

  function renderTable(list) {
    const wrap = document.getElementById('results');
    if (!list.length) { wrap.innerHTML = '<div class="tiny-note">Brak wyników.</div>'; return; }
    wrap.innerHTML = list.map(r => `
      <div class="result-card">
        <div><strong>${r.name}</strong> (${r.email})<br/>
        <span class="badge">ID: ${r.id}</span> <span class="badge">Miejsce: ${r.seatId}</span> <span class="badge">Data: ${r.date}</span></div>
        <button class="btn" data-show="${r.id}"><i class="fas fa-eye"></i> Szczegóły</button>
      </div>`).join('');

    wrap.querySelectorAll('[data-show]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.show;
        const res = getReservations().find(x => x.id === id);
        if (!res) return;
        const details = document.getElementById('confirmDetails');
        details.innerHTML = `
          <p><strong>${res.name}</strong> (${res.email})</p>
          <p>Miejsce: ${res.seatId}</p>
          <p>Data: ${res.date}</p>
          <p>ID: ${res.id}</p>
          <div id="qr"></div>`;
        const qrDiv = document.getElementById('qr');
        qrDiv.innerHTML = '';
        new QRCode(qrDiv, window.location.origin + '/cancel.html?id=' + res.id);
        document.getElementById('btnConfirmCancel').onclick = () => {
          const all = getReservations().filter(r => r.id !== res.id);
          setReservations(all);
          document.getElementById('confirmModal').classList.remove('show');
          renderTable(all);
        };
        document.getElementById('confirmModal').classList.add('show');
      });
    });
  }

  function search() {
    const id = document.getElementById('filterId').value.trim().toLowerCase();
    const date = document.getElementById('filterDate').value.trim();
    const seat = document.getElementById('filterSeat').value.trim().toLowerCase();
    const name = document.getElementById('filterName').value.trim().toLowerCase();
    let list = getReservations();
    if (id) list = list.filter(r => r.id.toLowerCase().includes(id));
    if (date) list = list.filter(r => r.date === date);
    if (seat) list = list.filter(r => r.seatId.toLowerCase().includes(seat));
    if (name) list = list.filter(r => r.name.toLowerCase().includes(name));
    renderTable(list);
  }

  document.getElementById('btnSearch').onclick = search;
  document.getElementById('btnListAll').onclick = () => renderTable(getReservations());
  document.getElementById('btnExportCSV').onclick = () => exportData('csv');
  document.getElementById('btnExportJSON').onclick = () => exportData('json');

  document.querySelectorAll('[data-close]').forEach(btn => btn.addEventListener('click', () => {
    document.getElementById('confirmModal').classList.remove('show');
  }));

  search();
}
