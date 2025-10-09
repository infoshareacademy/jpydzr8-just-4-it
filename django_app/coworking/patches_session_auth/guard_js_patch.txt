// Session-auth guard: bez localStorage, polegamy na ciasteczku 'sessionid'
(async function(){
  try{
    const res = await fetch('/api/auth/me', { credentials: 'same-origin' });
    if(!res.ok){
      location.href = '/login/';
      return;
    }
    const me = await res.json();
    // opcjonalnie: pokaż imię/nazwisko itp.
    console.debug('ME', me);
  }catch(e){
    location.href = '/login/';
  }
})();
