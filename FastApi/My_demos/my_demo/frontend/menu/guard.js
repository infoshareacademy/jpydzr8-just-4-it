
(async function(){
  const token = localStorage.getItem('token');
  if(!token){
    location.href = '/login/';
    return;
  }
  
  try{
    const res = await fetch('/api/auth/me', { headers: { Authorization: 'Bearer ' + token } });
    if(!res.ok){
      localStorage.removeItem('token');
      location.href = '/login/';
      return;
    }
  }catch(_){
    
    console.warn('Cannot verify token');
  }
})();