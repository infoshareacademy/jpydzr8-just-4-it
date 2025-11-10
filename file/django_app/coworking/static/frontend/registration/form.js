
(function () {
  function getCookie(name) {
    const cookie = document.cookie.split('; ').find(row => row.startsWith(name + '='));
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
  }

  async function ensureCsrf() {
    try { await fetch('/api/auth/csrf', { credentials: 'same-origin' }); } catch {}
    return getCookie('csrftoken');
  }

  function q(form, sel) { return form.querySelector(sel); }
  function txt(el) { return (el && 'value' in el) ? String(el.value || '').trim() : ''; }

  function findEmailField(form) {
    return q(form, '[name="email"]') || q(form, 'input[type="email"]') || q(form, 'input[name*="mail" i]');
  }

  function findFirstNameField(form) {
    return q(form, '[name="first_name"]') || q(form, '[name="firstName"]') || q(form, 'input[name*="first" i]');
  }

  function findLastNameField(form) {
    return q(form, '[name="last_name"]') || q(form, '[name="lastName"]') || q(form, 'input[name*="last" i], input[name*="surname" i]');
  }

  function findPasswordFields(form) {
    const p  = q(form, '[name="password"]');
    const p1 = q(form, '[name="password1"]');
    const p2 = q(form, '[name="password2"]');
    if (p) return { p };
    if (p1 || p2) return { p1, p2 };

    const pwds = Array.from(form.querySelectorAll('input[type="password"]'));
    if (pwds.length >= 2) return { p1: pwds[0], p2: pwds[1] };
    if (pwds.length === 1) return { p: pwds[0] };
    return {};
  }

  function showErrors(msgs) {
    const box = document.getElementById('regErrors');
    const arr = Array.isArray(msgs) ? msgs : (typeof msgs === 'string' ? [msgs] : []);
    const html = arr.map(m => `<div class="reg-error-item">${m}</div>`).join('');
    if (box) { box.innerHTML = html; box.style.display = html ? 'block' : 'none'; }
    else if (html) alert(arr.join('\n'));
  }

  function collectPayload(form) {
    const fEmail = findEmailField(form);
    const fFirst = findFirstNameField(form);
    const fLast  = findLastNameField(form);
    const pw = findPasswordFields(form);

    const email = txt(fEmail);
    const first = txt(fFirst);
    const last  = txt(fLast);

    if (!email) return { error: 'E-mail is required.' };

    const payload = { email };

    if (first) payload.first_name = first;
    if (last)  payload.last_name  = last;

    if (pw.p) {
      const v = txt(pw.p);
      if (!v) return { error: 'Password is required.' };
      payload.password = v;
    } else if (pw.p1 || pw.p2) {
      const v1 = txt(pw.p1);
      const v2 = txt(pw.p2);
      if (!v1 || !v2) return { error: 'Enter both password fields.' };
      if (v1 !== v2) return { error: 'The passwords are not identical.' };
      payload.password1 = v1;
      payload.password2 = v2;
    } else {
      return { error: 'Password fields not found.' };
    }

    return { payload };
  }

  async function submitRegister(e) {
    e.preventDefault();
    const form = e.currentTarget;
    showErrors([]);

    const { payload, error } = collectPayload(form);
    if (error) { showErrors(error); return; }

    const csrftoken = await ensureCsrf();

    try {
      const resp = await fetch('/api/auth/register', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(payload)
      });
      const data = await resp.json().catch(() => ({}));

      if (resp.status === 201) {
        const redirectTo = form.getAttribute('data-success-redirect') || '/login';
        window.location.assign(redirectTo);
        return;
      }

      const msgs = [];
      if (typeof data === 'object' && data) {
        for (const [k, v] of Object.entries(data)) {
          if (Array.isArray(v)) v.forEach(x => msgs.push(`${k}: ${x}`));
          else if (typeof v === 'string') msgs.push(`${k}: ${v}`);
          else msgs.push(`${k}: ${JSON.stringify(v)}`);
        }
      }
      if (!msgs.length) msgs.push('Registration failed, please try again.');
      showErrors(msgs);
    } catch (err) {
      console.error(err);
      showErrors('Network error. Please check your connection and try again.');
    }
  }

  function init() {
    const form = document.getElementById('registerForm') || document.querySelector('form');
    if (!form) return;
    form.addEventListener('submit', submitRegister);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
