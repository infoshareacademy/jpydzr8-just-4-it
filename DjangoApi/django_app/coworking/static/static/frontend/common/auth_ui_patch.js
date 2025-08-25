// auth_ui_patch.js
// Drop-in enhancements for login + registration pages:
// - Show/Hide password (auto-injected eye button if missing)
// - Password strength meter on registration (password + confirm match)
// - Working Back/Cancel buttons

(function(){
  const $ = (sel, root=document) => root.querySelector(sel);
  const $$ = (sel, root=document) => Array.from(root.querySelectorAll(sel));

  // ---------- Eye toggle (password visibility) ----------
  function ensureToggleFor(input){
    if(!input || input.dataset.hasToggle) return;
    input.dataset.hasToggle = '1';
    // Wrap
    const wrap = document.createElement('div');
    wrap.className = 'auth-field';
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    // Button
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'auth-toggle';
    btn.title = 'Show/Hide password';
    btn.setAttribute('aria-label','Show or hide password');
    btn.innerHTML = '👁️';
    btn.addEventListener('click', ()=>{
      input.type = input.type === 'password' ? 'text' : 'password';
    });
    wrap.appendChild(btn);
  }

  function initVisibilityToggles(){
    // Common ids / names
    const candidates = [
      '#password', '#pass', 'input[type="password"]',
      '#newPassword', '#registerPassword', '#regPassword', '#pwd', '#confirmPassword', '#passwordConfirm'
    ];
    const seen = new Set();
    for(const sel of candidates){
      $$(sel).forEach(inp=>{
        if(seen.has(inp)) return;
        seen.add(inp);
        ensureToggleFor(inp);
      });
    }
    // explicit toggle buttons, if present
    $$('[data-password-toggle]').forEach(btn=>{
      const targetSel = btn.getAttribute('data-password-toggle') || '#password';
      const inp = $(targetSel) || $('input[type="password"]');
      if(inp){
        btn.addEventListener('click', ()=>{
          inp.type = inp.type === 'password' ? 'text' : 'password';
        });
      }
    });
  }

  // ---------- Strength meter (registration) ----------
  function scorePassword(pw){
    if(!pw) return 0;
    let s = 0;
    const len = pw.length;
    if(len >= 8) s += 1;
    if(len >= 12) s += 1;
    if(/[a-z]/.test(pw)) s += 1;
    if(/[A-Z]/.test(pw)) s += 1;
    if(/[0-9]/.test(pw)) s += 1;
    if(/[^A-Za-z0-9]/.test(pw)) s += 1;
    // penalize common
    const common = ['password','qwerty','123456','abc123','admin','letmein','iloveyou'];
    if(common.some(c => pw.toLowerCase().includes(c))) s = Math.max(0, s-3);
    return Math.min(s, 6);
  }
  function labelFor(score){
    if(score <= 2) return {text:'Weak', cls:'weak', pct: 33};
    if(score <= 4) return {text:'Medium', cls:'medium', pct: 66};
    return {text:'Strong', cls:'strong', pct: 100};
  }

  function attachStrengthMeter(passwordInput, confirmInput){
    if(!passwordInput || passwordInput.dataset.hasMeter) return;
    passwordInput.dataset.hasMeter = '1';

    const meter = document.createElement('div');
    meter.className = 'auth-meter';
    const fill = document.createElement('div');
    fill.className = 'auth-meter-fill';
    meter.appendChild(fill);
    const txt = document.createElement('div');
    txt.className = 'auth-meter-text';
    passwordInput.parentNode.insertBefore(meter, passwordInput.nextSibling);
    passwordInput.parentNode.insertBefore(txt, meter.nextSibling);

    function refresh(){
      const s = scorePassword(passwordInput.value);
      const m = labelFor(s);
      fill.style.width = m.pct + '%';
      txt.textContent = 'Strength: ' + m.text;
    }
    passwordInput.addEventListener('input', refresh);
    refresh();

    if(confirmInput){
      const confirmTxt = document.createElement('div');
      confirmTxt.className = 'auth-meter-text';
      confirmTxt.style.marginTop = '2px';
      confirmTxt.style.color = 'var(--danger, #dc2626)';
      confirmInput.addEventListener('input', ()=>{
        confirmTxt.textContent = (confirmInput.value && confirmInput.value !== passwordInput.value)
          ? 'Passwords do not match'
          : '';
      });
      confirmInput.parentNode.insertBefore(confirmTxt, confirmInput.nextSibling);
    }
  }

  function initStrengthOnRegistration(){
    // Try common selectors
    const pw = $('#registerPassword') || $('#password') || $('#newPassword') || $('input[type="password"]');
    // Confirm: not the same as pw
    let confirm = $('#confirmPassword') || $('#passwordConfirm') || null;
    if(confirm === pw) confirm = null;
    attachStrengthMeter(pw, confirm);
  }

  // ---------- Back/Cancel buttons ----------
  function initBackCancel(){
    const goBack = (href)=>{
      if(href) { location.href = href; return; }
      if(document.referrer) { history.back(); return; }
      // fallback: go to root or welcome
      location.href = 'welcome/index.html';
    };
    // by id
    const ids = ['btnBack','btnCancel','cancelBtn','backBtn'];
    ids.forEach(id=>{
      const el = document.getElementById(id);
      if(el && !el.dataset.backBound){
        el.dataset.backBound = '1';
        el.addEventListener('click', (e)=>{ e.preventDefault(); goBack(el.getAttribute('data-href')); });
      }
    });
    // by attribute
    $$('[data-action="back"],[data-action="cancel"]').forEach(el=>{
      if(el.dataset.backBound) return;
      el.dataset.backBound = '1';
      el.addEventListener('click', (e)=>{ e.preventDefault(); goBack(el.getAttribute('data-href')); });
    });
    // auto-inject back link if none on page
    if(!$('#btnBack') && !$('#btnCancel') && !$('[data-action="back"]')){
      const a = document.createElement('button');
      a.className = 'auth-back';
      a.textContent = '← Back';
      a.addEventListener('click', ()=> goBack());
      const host = $('main') || document.body;
      host.insertBefore(a, host.firstChild);
    }
  }

  // ---------- Boot ----------
  function boot(){
    initVisibilityToggles();
    initStrengthOnRegistration();
    initBackCancel();
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
