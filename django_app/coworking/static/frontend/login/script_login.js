;(() => {
  'use strict';

  const form = document.querySelector('.login-form');
  if (!form) return;

  let lastCsrfToken = '';

  function getCookie(name) {
    return document.cookie
      .split('; ')
      .find(r => r.startsWith(name + '='))
      ?.split('=')[1] || '';
  }

  async function fetchCsrfToken() {
    const fromCookie = getCookie('csrftoken');
    if (fromCookie) {
      lastCsrfToken = fromCookie;
      return lastCsrfToken;
    }

    let token = '';
    try {
      const res = await fetch('/api/auth/csrf', { credentials: 'same-origin' });
      try {
        const data = await res.clone().json().catch(() => ({}));
        token = data.csrfToken || data.csrftoken || '';
      } catch (_) {}
      const fromCookie2 = getCookie('csrftoken');
      lastCsrfToken = fromCookie2 || token || '';
    } catch (_) {
      lastCsrfToken = getCookie('csrftoken') || '';
    }
    return lastCsrfToken;
  }

  const submitBtn = form.querySelector('button[type=submit], input[type=submit]');
  if (submitBtn) submitBtn.disabled = true;
  const csrfReady = (async () => {
    await fetchCsrfToken();
    if (submitBtn) submitBtn.disabled = false;
  })();

  async function postLogin(email, password) {
    const headerToken = getCookie('csrftoken') || lastCsrfToken || '';
    if (!headerToken) throw new Error('Brak CSRF tokenu — odśwież stronę i spróbuj ponownie.');

    return fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': headerToken
      },
      credentials: 'same-origin',
      body: JSON.stringify({ email, password })
    });
  }

  async function doLogin(e) {
    e?.preventDefault();
    if (e && typeof e.stopImmediatePropagation === 'function') e.stopImmediatePropagation();

    const emailEl = form.querySelector('#email,[name=email],[type=email]');
    const passEl  = form.querySelector('#password,[name=password],[type=password]');
    const email = (emailEl?.value || '').trim().toLowerCase();
    const password = passEl?.value || '';

    if (!email || !password) { alert('Podaj e-mail i hasło.'); return; }

    try {
      await csrfReady;

      const res = await postLogin(email, password);

      let data = {};
      try { data = await res.clone().json(); } catch (_) {}

      if (!res.ok) {
        alert((data && data.detail) || `Logowanie nieudane (${res.status})`);
        return;
      }

      location.href = '/menu/dashboard.html';
    } catch (err) {
      alert('Błąd sieci: ' + (err?.message || err));
    }
  }

  form.addEventListener('submit', doLogin, { capture: true });
})();
