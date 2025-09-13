
// reservation_table.js — table + Edit modal (session auth, CSRF)
(function(){
  function getCookie(name){
    return document.cookie.split('; ').find(row => row.startsWith(name + '='))?.split('=')[1];
  }
  async function apiFetch(url, opts={}){
    const csrftoken = getCookie('csrftoken') || '';
    const headers = Object.assign({ 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken }, opts.headers || {});
    const res = await fetch(url, Object.assign({}, opts, { headers, credentials: 'same-origin' }));
    let data = null; try{ data = await res.json(); } catch(e){}
    if(!res.ok){ throw new Error((data && (data.detail||data.message)) || ('HTTP '+res.status)); }
    return data;
  }
  function el(tag, attrs={}, ...children){
    const e = document.createElement(tag);
    Object.entries(attrs).forEach(([k,v])=>{
      if(k==='class') e.className = v;
      else if(k==='html') e.innerHTML = v;
      else e.setAttribute(k, v);
    });
    children.forEach(c=>{ if(c!==null && c!==undefined) e.appendChild(typeof c==='string'?document.createTextNode(c):c); });
    return e;
  }
  function ensureModal(){
    if(document.getElementById('resvEditModal')) return document.getElementById('resvEditModal');
    const modal = el('div', {id:'resvEditModal', class:'resv-modal hide'},
      el('div', {class:'resv-modal-backdrop'}),
      el('div', {class:'resv-modal-dialog'},
        el('div', {class:'resv-modal-header'},
          el('h3', {class:'resv-modal-title', html:'Edit reservation'}),
          el('button', {class:'resv-close', id:'resvCloseBtn', 'aria-label':'Close'}, '×')
        ),
        el('div', {class:'resv-modal-body'},
          el('form', {id:'resvEditForm'},
            el('input', {type:'hidden', id:'resvId'}),
            el('div', {class:'row'},
              el('label', {for:'resvDate'}, 'Date'),
              el('input', {id:'resvDate', type:'text', disabled:'disabled'})
            ),
            el('div', {class:'row'},
              el('label', {for:'resvSeat'}, 'Seat'),
              el('input', {id:'resvSeat', type:'text', disabled:'disabled'})
            ),
            el('div', {class:'row'},
              el('label', {for:'resvName'}, 'Name'),
              el('input', {id:'resvName', type:'text'})
            ),
            el('div', {class:'row'},
              el('label', {for:'resvEmail'}, 'Email'),
              el('input', {id:'resvEmail', type:'email'})
            ),
            el('div', {class:'row'},
              el('label', {for:'resvNotes'}, 'Notes'),
              el('textarea', {id:'resvNotes', rows:'3'})
            ),
            el('div', {class:'row right'},
              el('button', {type:'button', class:'btn btn-muted', id:'resvCancel'}, 'Cancel'),
              el('button', {type:'submit', class:'btn btn-primary', id:'resvSave'}, 'Save')
            )
          ),
          el('div', {id:'resvEditInfo', class:'muted', style:'margin-top:6px'})
        )
      )
    );
    document.body.appendChild(modal);
    // close interactions
    modal.querySelector('#resvCloseBtn').addEventListener('click', ()=>modal.classList.add('hide'));
    modal.querySelector('#resvCancel').addEventListener('click', ()=>modal.classList.add('hide'));
    modal.querySelector('.resv-modal-backdrop').addEventListener('click', ()=>modal.classList.add('hide'));
    // submit handler
    modal.querySelector('#resvEditForm').addEventListener('submit', async (e)=>{
      e.preventDefault();
      const info = document.getElementById('resvEditInfo'); info.textContent = 'Saving...';
      const id = document.getElementById('resvId').value;
      const payload = {
        name: document.getElementById('resvName').value.trim(),
        email: document.getElementById('resvEmail').value.trim(),
        notes: document.getElementById('resvNotes').value.trim(),
      };
      try{
        await apiFetch(`/api/reservations/${encodeURIComponent(id)}/`, { method:'PATCH', body: JSON.stringify(payload) });
        info.textContent = 'Saved ✔';
        // refresh table row in-place:
        const row = document.querySelector(`tr[data-resv-id="${CSS.escape(id)}"]`);
        if(row){
          row.querySelector('.c-name').textContent = payload.name || '—';
          row.querySelector('.c-email').textContent = payload.email || '—';
          row.querySelector('.c-notes') && (row.querySelector('.c-notes').textContent = payload.notes || '—');
        }
        setTimeout(()=> modal.classList.add('hide'), 500);
      }catch(err){
        info.textContent = 'Error: ' + (err.message || String(err));
      }
    });
    return modal;
  }
  function openEditModal(r){
    const m = ensureModal();
    m.classList.remove('hide');
    document.getElementById('resvEditInfo').textContent = '';
    document.getElementById('resvId').value = r.id || '';
    document.getElementById('resvDate').value = r.date || '';
    document.getElementById('resvSeat').value = r.seat_id || '';
    document.getElementById('resvName').value = r.name || '';
    document.getElementById('resvEmail').value = r.email || '';
    document.getElementById('resvNotes').value = r.notes || '';
  }
  async function run(){
    const wrap = document.getElementById('resvTableWrap');
    if(!wrap) return;
    const today = new Date();
    const to = new Date(today); to.setDate(to.getDate()+30);
    const df = today.toISOString().slice(0,10);
    const dt = to.toISOString().slice(0,10);
    try{
      const items = await apiFetch(`/api/reservations/?date_from=${df}&date_to=${dt}`);
      if(!Array.isArray(items) || !items.length){ wrap.innerHTML = '<em>No upcoming reservations.</em>'; return; }
      const table = el('table', {class:'resv-table'});
      const thead = el('thead', {}, el('tr', {},
        el('th',{html:'Date'}), el('th',{html:'Seat'}), el('th',{html:'Name'}), el('th',{html:'Email'}), el('th',{html:'Actions'})
      ));
      const tbody = el('tbody');
      items.forEach(r=>{
        const btnEdit = el('button', {class:'btn btn-primary btn-sm'}, 'Edit');
        btnEdit.addEventListener('click', ()=> openEditModal(r));
        const btnDel = el('button', {class:'btn btn-muted btn-sm'}, 'Delete');
        btnDel.addEventListener('click', async ()=>{
          btnDel.disabled = true;
          try{ await apiFetch(`/api/reservations/${encodeURIComponent(r.id)}/`, { method:'DELETE' }); tr.remove(); }
          catch(err){ alert('Delete failed: ' + err.message); btnDel.disabled=false; }
        });
        const tr = el('tr', {'data-resv-id': r.id || ''},
          el('td',{html: r.date || '—'}),
          el('td',{html: r.seat_id || '—'}),
          el('td',{class:'c-name', html: r.name || '—'}),
          el('td',{class:'c-email', html: r.email || '—'}),
          el('td',{}, el('div', {}, btnEdit, document.createTextNode(' '), btnDel))
        );
        tbody.appendChild(tr);
      });
      table.appendChild(thead); table.appendChild(tbody);
      wrap.innerHTML = ''; wrap.appendChild(table);
    }catch(err){
      wrap.innerHTML = '<em>Error: '+(err.message||String(err))+'</em>';
    }
  }
  document.addEventListener('DOMContentLoaded', run);
})();
