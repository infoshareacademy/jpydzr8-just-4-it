// modal_stay_guard.js — keep the reservation summary on screen by blocking auto-redirects temporarily
(function(){
  // How long to block redirects after the summary appears (ms)
  const BLOCK_MS = 8000;

  let unblockTimer = null;
  let blocked = false;
  let origAssign = null, origReplace = null, origHrefDesc = null;

  function blockRedirects(){
    if(blocked) return;
    blocked = true;

    // Patch location.assign/replace
    origAssign = window.location.assign.bind(window.location);
    origReplace = window.location.replace.bind(window.location);

    window.location.assign = function(url){
      console.warn('[modal_stay_guard] Blocked location.assign to', url);
    };
    window.location.replace = function(url){
      console.warn('[modal_stay_guard] Blocked location.replace to', url);
    };

    // Patch setting location.href
    try{
      origHrefDesc = Object.getOwnPropertyDescriptor(Location.prototype, 'href');
      Object.defineProperty(window.location.__proto__, 'href', {
        configurable: true,
        enumerable: true,
        set: function(v){ console.warn('[modal_stay_guard] Blocked location.href =', v); },
        get: function(){ return origHrefDesc.get.call(window.location); }
      });
    }catch(_){ /* some browsers may not allow redefining */ }

    // Block beforeunload navigations (form submits triggering reloads)
    window.addEventListener('beforeunload', onBeforeUnload);
  }

  function unblockRedirects(){
    if(!blocked) return;
    blocked = false;

    if(origAssign) window.location.assign = origAssign;
    if(origReplace) window.location.replace = origReplace;
    if(origHrefDesc){
      try{
        Object.defineProperty(window.location.__proto__, 'href', origHrefDesc);
      }catch(_){}
    }
    window.removeEventListener('beforeunload', onBeforeUnload);
    origAssign = origReplace = origHrefDesc = null;
  }

  function onBeforeUnload(e){
    // While summary is up, prevent accidental unloads
    e.preventDefault();
    e.returnValue = '';
    return '';
  }

  // Tie the guard to the reservation summary lifecycle
  window.addEventListener('reservation:created', ()=>{
    blockRedirects();
    clearTimeout(unblockTimer);
    unblockTimer = setTimeout(unblockRedirects, BLOCK_MS);
  });

  // If reservation summary provides a global close, listen and unblock immediately
  window.addEventListener('reservation:summary:closed', ()=>{
    unblockRedirects();
    clearTimeout(unblockTimer);
  });

  // Also, if the modal is inserted, extend the block until user closes it
  const observer = new MutationObserver((mutations)=>{
    for(const m of mutations){
      for(const node of m.addedNodes){
        if(node && node.nodeType === 1 && node.classList && node.classList.contains('rs-modal')){
          blockRedirects();
          clearTimeout(unblockTimer);
        }
      }
      for(const node of m.removedNodes){
        if(node && node.nodeType === 1 && node.classList && node.classList.contains('rs-modal')){
          window.dispatchEvent(new Event('reservation:summary:closed'));
        }
      }
    }
  });
  observer.observe(document.documentElement, { childList:true, subtree:true });

  // Expose manual controls for debugging
  window.__modal_guard_block__ = blockRedirects;
  window.__modal_guard_unblock__ = unblockRedirects;
})();
