
/**
 * registration_form.js
 * Drop-in script for Django registration.
 * - Fetches CSRF cookie
 * - Collects form values (supports snake_case and camelCase names)
 * - Accepts password OR password1/password2 (checks equality)
 * - Sends JSON to /api/auth/register with X-CSRFToken
 * - Shows human-readable errors; redirects on success
 *
 * How to use:
 * 1) Place this file at: static/frontend/registration/form.js
 * 2) In your template (templates/registration/index.html) include:
 *    <script src="{% static 'frontend/registration/form.js' %}"></script>
 * 3) Make sure your form has an id="registerForm" (or leave it, we will take the first <form>).
 * 4) Optionally add <div id="regErrors"></div> for error messages.
 */

(function () {
  function getCookie(name) {
    const cookie = document.cookie.split('; ').find(row => row.startsWith(name + '='));
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
  }

  async function ensureCsrf() {
    // Hit the CSRF endpoint to ensure csrftoken cookie is set
    try {
      await fetch('/api/auth/csrf', { credentials: 'same-origin' });
    } catch (e) {
      console.warn('CSRF prefetch failed (will try with existing cookie):', e);
    }
    return getCookie('csrftoken');
  }

  function pick(...els) {
    for (const el of els) {
      if (el) return el;
    }
    return null;
  }

  function text(el) {
    return (el && 'value' in el) ? String(el.value || '').trim() : '';
  }

  function showErrors(msgs) {
    const box = document.getElementById('regErrors');
    const asArray = Array.isArray(msgs) ? msgs : (typeof msgs === 'string' ? [msgs] : []);
    const html = asArray.map(m => `<div class="reg-error-item">${m}</div>`).join('');
    if (box) {
      box.innerHTML = html || '';
      box.style.display = html ? 'block' : 'none';
    } else if (html) {
      alert(asArray.join('\n'));
    }
  }

  function collectPayload(form) {
    // Support multiple naming conventions
    const f_first  = pick(form.querySelector('[name="first_name"]'), form.querySelector('[name="firstName"]'));
    const f_last   = pick(form.querySelector('[name="last_name"]'),  form.querySelector('[name="lastName"]'));
    const f_email  = pick(form.querySelector('[name="email"]'),      form.querySelector('[type="email"]'));
    const f_pwd    = pick(form.querySelector('[name="password"]'));
    const f_pwd1   = pick(form.querySelector('[name="password1"]'));
    const f_pwd2   = pick(form.querySelector('[name="password2"]'));

    const first_name = text(f_first);
    const last_name  = text(f_last);
    const email      = text(f_email);
    const pwd        = text(f_pwd);
    const pwd1       = text(f_pwd1);
    const pwd2       = text(f_pwd2);

    if (!email)        return { error: 'E-mail jest wymagany.' };
    if (!(pwd || (pwd1 && pwd2))) return { error: 'Podaj hasło (password) lub parę password1/password2.' };
    if (pwd1 || pwd2) {
      if (pwd1 !== pwd2) return { error: 'Hasła nie są identyczne.' };
    }

    const payload = {
      email: email
    };
    if (first_name) payload.first_name = first_name;
    if (last_name)  payload.last_name  = last_name;
    if (pwd)        payload.password   = pwd;
    else            payload.password1  = payload.password2 = pwd1; // mapped by backend

    return { payload };
  }

  async function submitRegister(e) {
    e.preventDefault();
    const form = e.currentTarget;
    showErrors([]);

    const { payload, error } = collectPayload(form);
    if (error) {
      showErrors(error);
      return;
    }

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
        // success → redirect where you want
        const redirectTo = (form.getAttribute('data-success-redirect') || '/login');
        window.location.assign(redirectTo);
        return;
      }

      // 400 with error details
      const msgs = [];
      if (typeof data === 'object' && data) {
        for (const [k, v] of Object.entries(data)) {
          if (Array.isArray(v)) {
            v.forEach(x => msgs.push(`${k}: ${x}`));
          } else if (typeof v === 'string') {
            msgs.push(`${k}: ${v}`);
          } else {
            msgs.push(`${k}: ${JSON.stringify(v)}`);
          }
        }
      }
      if (!msgs.length) msgs.push('Rejestracja nieudana. Spróbuj ponownie.');
      showErrors(msgs);
    } catch (err) {
      console.error(err);
      showErrors('Błąd sieci. Sprawdź połączenie i spróbuj ponownie.');
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
