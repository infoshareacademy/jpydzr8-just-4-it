;(() => {
  'use strict';

  const form = document.querySelector('.login-form');
  if (!form) return;

  // zawsze będziemy trzymać tutaj "najświeższy" token – z cookie lub z /api/auth/csrf
  let lastCsrfToken = '';

  function getCookie(name) {
    return document.cookie
      .split('; ')
      .find(r => r.startsWith(name + '='))
      ?.split('=')[1] || '';
  }

  async function fetchCsrfToken() {
    // 1) najpierw spróbuj z cookie
    const fromCookie = getCookie('csrftoken');
    if (fromCookie) {
      lastCsrfToken = fromCookie;
      return lastCsrfToken;
    }

    // 2) jeśli brak, poproś backend – pobierz token i cookie jednym strzałem
    //    (ważne: credentials: 'same-origin', żeby Set-Cookie zadziałało)
    let token = '';
    try {
      const res = await fetch('/api/auth/csrf', { credentials: 'same-origin' });
      // spróbuj odczytać z JSON (większość widoków zwraca {"csrfToken": "..."} )
      try {
        const data = await res.clone().json().catch(() => ({}));
        token = data.csrfToken || data.csrftoken || '';
      } catch (_) {}
      // a teraz drugi raz sprawdź cookie – po odpowiedzi powinno już być ustawione
      const fromCookie2 = getCookie('csrftoken');
      lastCsrfToken = fromCookie2 || token || '';
    } catch (_) {
      lastCsrfToken = getCookie('csrftoken') || '';
    }
    return lastCsrfToken;
  }

  // zablokuj przycisk submit do czasu gotowego CSRF (żeby uniknąć przypadkowego 403)
  const submitBtn = form.querySelector('button[type=submit], input[type=submit]');
  if (submitBtn) submitBtn.disabled = true;
  const csrfReady = (async () => {
    await fetchCsrfToken();
    if (submitBtn) submitBtn.disabled = false;
  })();

  async function postLogin(email, password) {
    // bierz najpierw z cookie, jeśli puste – użyj lastCsrfToken z /api/auth/csrf
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
      // Poczekaj aż CSRF będzie na pewno dostępny (cookie lub pamięć)
      await csrfReady;

      // Jedyny POST – bez „pustego” pierwszego i bez 403
      const res = await postLogin(email, password);

      let data = {};
      try { data = await res.clone().json(); } catch (_) {}

      if (!res.ok) {
        // pokazujemy błąd dopiero tu (bez alertów „po drodze”)
        alert((data && data.detail) || `Logowanie nieudane (${res.status})`);
        return;
      }

      // Sukces – przejście do dashboardu
      location.href = '/menu/dashboard.html';
    } catch (err) {
      alert('Błąd sieci: ' + (err?.message || err));
    }
  }

  // Nasz handler jako pierwszy
  form.addEventListener('submit', doLogin, { capture: true });
})();
