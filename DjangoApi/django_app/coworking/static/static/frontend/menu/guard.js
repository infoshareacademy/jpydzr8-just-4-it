// Simple auth guard for dashboard pages
(async function(){
  const token = localStorage.getItem('token');
  if(!token){
    location.href = '/login/';
    return;
  }
  // optionally verify token by calling /api/auth/me
  try{
    const res = await fetch('/api/auth/me', { headers: { Authorization: 'Bearer ' + token } });
    if(!res.ok){
      localStorage.removeItem('token');
      location.href = '/login/';
      return;
    }
  }catch(_){
    // if server not reachable, allow page to render but show banner
    console.warn('Cannot verify token');
  }
})();