// Session-auth login: nie zapisujemy tokenu, tylko polegamy na sesji i CSRF
(function(){
  const form = document.querySelector('.login-form');
  if(!form){ return; }

  function getCookie(name){
    return document.cookie.split('; ').find(row => row.startsWith(name + '='))?.split('=')[1];
  }

  async function doLogin(e){
    e.preventDefault();
    const emailEl = form.querySelector('#email,[name=email],[type=email]');
    const passEl  = form.querySelector('#password,[name=password],[type=password]');
    const email = emailEl?.value?.trim();
    const password = passEl?.value || '';
    if(!email || !password){ alert('Podaj e-mail i hasło.'); return; }

    // pobierz CSRF (masz też endpoint /api/auth/csrf)
    const csrftoken = getCookie('csrftoken');
    try{
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken || ''
        },
        credentials: 'same-origin',
        body: JSON.stringify({ email, password })
      });
      if(!res.ok){
        const data = await res.json().catch(()=>({}));
        alert((data && data.detail) || `Błędne dane logowania (${res.status}).`);
        return;
      }
      // sesja jest ustawiona (ciasteczko 'sessionid'), przejdź do dashboardu
      location.href = '/menu/dashboard.html';
    }catch(err){
      alert('Błąd sieci: ' + (err.message || err));
    }
  }
  form.addEventListener('submit', doLogin);
})();
