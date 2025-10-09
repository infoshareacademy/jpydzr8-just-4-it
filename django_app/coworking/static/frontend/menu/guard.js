(async function(){
  try{
    const res = await fetch('/api/auth/me', { credentials: 'same-origin' });
    if(!res.ok){
      location.href = '/login/';
      return;
    }
    const me = await res.json();

    const span = document.getElementById('userName');
    if (span) {
      let first =
        (me.first_name && String(me.first_name).trim()) ||
        (me.full_name && String(me.full_name).trim().split(/\s+/)[0]) ||
        (me.email && String(me.email).trim().split('@')[0]) ||
        'User';

      first = first.charAt(0).toUpperCase() + first.slice(1);
      span.textContent = first;
    }

    const h1 = document.querySelector('.dashboard-title');
    if (h1 && !document.getElementById('userName')) {
      h1.innerHTML = h1.innerHTML.replace(/User<\/span>|User\b/i, (m)=> (span?.textContent || first || 'User'));
    }
  }catch(e){
    location.href = '/login/';
  }
})();
