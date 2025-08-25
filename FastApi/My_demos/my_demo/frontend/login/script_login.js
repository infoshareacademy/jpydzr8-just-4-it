
(function(){
  const form = document.querySelector('.login-form');
  if(!form){ return; }

  async function doLogin(e){
    e.preventDefault();
    const emailEl = form.querySelector('#email,[name=email],[type=email]');
    const passEl  = form.querySelector('#password,[name=password],[type=password]');
    const email = emailEl?.value?.trim();
    const password = passEl?.value || '';

    if(!email || !password){
      alert('Podaj e-mail i hasło.');
      return;
    }
    try{
      const res = await fetch('/api/auth/login', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json().catch(()=>null);
      if(!res.ok){
        alert((data && data.detail) || `Błędne dane logowania (${res.status}).`);
        return;
      }
      
      const token = data.access_token || data.token;
      localStorage.setItem('token', token);
      location.href = '/menu/dashboard.html';
    }catch(err){
      alert('Błąd sieci: ' + (err.message || err));
    }
  }

  form.addEventListener('submit', doLogin);
})();
