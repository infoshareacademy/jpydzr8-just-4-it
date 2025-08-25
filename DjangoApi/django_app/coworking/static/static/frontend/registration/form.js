// Registration with auto-login
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("regForm") || document.querySelector(".registration-form");
  if(!form){ return; }

  async function autoLogin(email, password){
    const res = await fetch('/api/auth/login', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ email, password })
    });
    const data = await res.json().catch(()=>null);
    if(!res.ok){
      throw new Error((data && data.detail) || ('Login failed ' + res.status));
    }
    const token = data.access_token || data.token;
    if(!token){ throw new Error('Brak tokenu w odpowiedzi logowania'); }
    localStorage.setItem('token', token);
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = (form.querySelector('#email,[name=email]')?.value || '').trim();
    const password = form.querySelector('#password,[name=password]')?.value || '';
    const full_name = (form.querySelector('#fullName,[name=full_name]')?.value || '').trim();

    if(!email || !password){
      alert('Podaj e-mail i hasło.');
      return;
    }

    try{
      // 1) Register
      const reg = await fetch('/api/auth/register', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ email, password, full_name })
      });
      const regData = await reg.json().catch(()=>null);
      if(!reg.ok){
        alert((regData && regData.detail) || `Rejestracja nieudana (${reg.status}).`);
        return;
      }

      // 2) Auto-login
      await autoLogin(email, password);

      // 3) Redirect to dashboard
      location.href = '/menu/dashboard.html';
    }catch(err){
      console.error(err);
      alert('Błąd: ' + (err.message || err));
    }
  });
});
