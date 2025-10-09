(function(){
  const origFetch = window.fetch;
  window.fetch = function(input, init){
    try{
      const url = typeof input === 'string' ? input : (input && input.url) || '';
      if (/^\/api\/reservations(\?|$)/.test(url)) {
        const fixed = url.replace(/^\/api\/reservations(?!\/)/, '/api/reservations/');
        if (typeof input === 'string') input = fixed;
        else input = new Request(fixed, input);
      }
    }catch(e){}
    return origFetch.call(this, input, init);
  };
})();
