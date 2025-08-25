
// auth_ui_patch_position_fix.js
// If a dedicated container #password-strength exists, move the text there to avoid clipping
(function(){
  function moveIfContainerExists(){
    var container = document.getElementById('password-strength');
    if(!container) return;
    // find meter/text that sit right after the password input
    var pwd = document.getElementById('password') || document.querySelector('input[type="password"]');
    if(!pwd) return;
    var meter = pwd.nextElementSibling && pwd.nextElementSibling.classList && pwd.nextElementSibling.classList.contains('auth-meter')
      ? pwd.nextElementSibling : null;
    var textEl = meter && meter.nextElementSibling && meter.nextElementSibling.classList && meter.nextElementSibling.classList.contains('auth-meter-text')
      ? meter.nextElementSibling : null;
    if(textEl){
      container.innerHTML = '';
      container.appendChild(textEl);
    }
    if(meter && !meter.isConnected && container){ // if textEl moved, ensure meter stays before it
      container.insertAdjacentElement('afterbegin', meter);
    }
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', moveIfContainerExists);
  else moveIfContainerExists();
})();
