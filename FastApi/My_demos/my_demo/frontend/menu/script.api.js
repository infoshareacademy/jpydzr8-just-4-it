
(function() {
  const API_BASE = (() => {
    if (window.API_BASE_URL) return window.API_BASE_URL.replace(/\/+$/,'');
    const meta = document.querySelector('meta[name="api-base-url"]');
    return (meta?.content || 'http://localhost:3000').replace(/\/+$/,'');
  })();

  const endpoints = {
    search: (params) => API_BASE + '/reservations' + toQuery(params),
    cancel: (id) => API_BASE + '/reservations/' + encodeURIComponent(id)
  };

  function toQuery(obj) {
    const p = new URLSearchParams();
    Object.entries(obj).forEach(([k,v]) => {
      if (v != null && String(v).trim() !== '') p.append(k, String(v).trim());
    });
    const qs = p.toString();
    return qs ? ('?' + qs) : '';
  }

  function showError(msg, detail) {
    const box = document.getElementById('feedback');
    box.innerHTML = `<div class="error"><strong>Błąd:</strong> ${msg}${detail ? `<div class="muted" style="margin-top:6px;">${detail}</div>` : ''}</div>`;
  }
  function clearError() { document.getElementById('feedback').innerHTML = ''; }
  function showLoading(target) {
    target.innerHTML = `<div class="empty"><span class="inline-spinner"><span class="spinner"></span> Ładowanie...</span></div>`;
  }

  async function fetchJSON(url, opts = {}) {
    const res = await fetch(url, {
      headers: { 'Accept': 'application/json', ...(opts.headers || {}) },
      ...opts
    });
    if (!res.ok) {
      const text = await res.text().catch(()=>'');
      throw new Error(`HTTP ${res.status} ${res.statusText} ${text ? '- ' + text : ''}`);
    }
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) return res.json();
    const text = await res.text();
    try { return JSON.parse(text); } catch { return text; }
  }

  function render(list) {
    const wrap = document.getElementById('results');
    wrap.innerHTML = '';
    if (!list || !list.length) {
      wrap.innerHTML = '<div class="empty"><i class="fas fa-inbox"></i> Brak wyników</div>';
      return;
    }
    list.forEach(item => {
      const row = document.createElement('div');
      row.className = 'row';
      row.dataset.id = item.id;
      row.innerHTML = `
        <div><strong>${escapeHtml(item.id)}</strong></div>
        <div>${escapeHtml(item.date || '')}</div>
        <div>${escapeHtml(item.seat || '')}</div>
        <div>
          ${escapeHtml(item.name || '')}
          <div class="muted" style="font-size:12px;">${escapeHtml(item.email || '')}</div>
        </div>
        <div class="actions">
          <button class="btn" data-action="qr"><i class="fas fa-qrcode"></i> QR</button>
          <button class="btn primary" data-action="cancel"><i class="fas fa-ban"></i> Anuluj</button>
        </div>
      `;
      wrap.appendChild(row);
    });
  }

  function escapeHtml(s) {
    return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',\"'\":'&#39;'}[c]));
  }

  function exportJSON(list) {
    const blob = new Blob([JSON.stringify(list, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = Object.assign(document.createElement('a'), { href: url, download: 'reservations.json' });
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  function exportCSV(list) {
    const header = ['id','date','seat','name','email','notes'];
    const lines = [header.join(',')];
    (list || []).forEach(r => {
      const row = [r.id, r.date, r.seat, r.name, r.email, r.notes]
        .map(v => `\"${(v ?? '').toString().replace(/\"/g,'\"\"')}\"`);
      lines.push(row.join(','));
    });
    const blob = new Blob([lines.join('\\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = Object.assign(document.createElement('a'), { href: url, download: 'reservations.csv' });
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  function openModal(detailsHtml, onConfirm) {
    const modal = document.getElementById('confirmModal');
    const details = document.getElementById('confirmDetails');
    details.innerHTML = detailsHtml || '';
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');

    function close() {
      modal.classList.remove('open');
      modal.setAttribute('aria-hidden', 'true');
      details.innerHTML = '';
    }
    modal.querySelectorAll('[data-close]').forEach(el => el.addEventListener('click', close, { once: true }));

    const btnConfirm = document.getElementById('btnConfirmCancel');
    const cloned = btnConfirm.cloneNode(true);
    btnConfirm.replaceWith(cloned);
    cloned.addEventListener('click', () => { try { onConfirm && onConfirm(); } finally { close(); } }, { once: true });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const $ = (sel) => document.querySelector(sel);
    const results = $('#results');

    const inputs = { id: $('#filterId'), date: $('#filterDate'), seat: $('#filterSeat'), name: $('#filterName') };

    async function runSearch() {
      clearError();
      showLoading(results);
      try {
        const url = endpoints.search({ id: inputs.id.value, date: inputs.date.value, seat: inputs.seat.value, name: inputs.name.value });
        const data = await fetchJSON(url);
        render(Array.isArray(data) ? data : (data.items || []));
      } catch (e) {
        render([]);
        showError('Nie udało się pobrać listy rezerwacji.', e.message);
      }
    }

    $('#btnSearch').addEventListener('click', runSearch);
    $('#btnListAll').addEventListener('click', async () => {
      inputs.id.value = inputs.date.value = inputs.seat.value = inputs.name.value = '';
      await runSearch();
    });
    $('#btnExportJSON').addEventListener('click', async () => {
      try {
        const url = endpoints.search({ id: inputs.id.value, date: inputs.date.value, seat: inputs.seat.value, name: inputs.name.value });
        const data = await fetchJSON(url);
        exportJSON(Array.isArray(data) ? data : (data.items || []));
      } catch(e) { showError('Eksport JSON nieudany.', e.message); }
    });
    $('#btnExportCSV').addEventListener('click', async () => {
      try {
        const url = endpoints.search({ id: inputs.id.value, date: inputs.date.value, seat: inputs.seat.value, name: inputs.name.value });
        const data = await fetchJSON(url);
        exportCSV(Array.isArray(data) ? data : (data.items || []));
      } catch(e) { showError('Eksport CSV nieudany.', e.message); }
    });

    results.addEventListener('click', async (e) => {
      const row = e.target.closest('.row');
      if (!row) return;
      const id = row.dataset.id;
      const actionBtn = e.target.closest('button');
      if (!actionBtn) return;
      const action = actionBtn.dataset.action;

      if (action === 'cancel') {
        openModal(`Anulować rezerwację <strong>${id}</strong>?`, async () => {
          try {
            await fetchJSON(endpoints.cancel(id), { method: 'DELETE' });
            await runSearch();
          } catch (e) {
            showError('Nie udało się anulować rezerwacji.', e.message);
          }
        });
      } else if (action === 'qr') {
        const divId = 'qr-' + Math.random().toString(36).slice(2,8);
        openModal(`<div class="muted" style="margin-bottom:8px;">Zeskanuj QR, aby pobrać szczegóły.</div><div id="${divId}" style="display:flex;justify-content:center;"></div>`, () => {});
        const el = document.getElementById(divId);
        if (el && window.QRCode) {
          new QRCode(el, { text: JSON.stringify({ id }), width: 200, height: 200 });
        } else if (el) {
          el.textContent = 'Biblioteka QRCode niedostępna.';
        }
      }
    });

    const params = new URLSearchParams(window.location.search);
    if (params.has('id')) inputs.id.value = params.get('id');

    if (window.flatpickr) {
      flatpickr('#filterDate', { dateFormat: 'Y-m-d', allowInput: true });
    }

    runSearch();
  });
})();