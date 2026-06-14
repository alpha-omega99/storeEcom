/* ============================================================
   ChicShop — utils.js
   Fonctions globales partagées
   ============================================================ */

/* ---- Toast notification ---- */
function showToast(msg, type){
  var wrap = document.getElementById('toast');
  if(!wrap) return;
  var t = document.createElement('div');
  t.style.cssText = [
    'background:'+(type==='error'?'#C56F6F':'#1A3C2F'),
    'color:#fff',
    'padding:12px 20px',
    'border-radius:40px',
    'font-size:13px',
    'font-family:Outfit,sans-serif',
    'box-shadow:0 8px 24px rgba(0,0,0,.18)',
    'animation:fadeUp .3s ease',
    'max-width:320px',
    'line-height:1.4'
  ].join(';');
  t.textContent = msg;
  wrap.appendChild(t);
  setTimeout(function(){ t.style.opacity='0'; t.style.transition='opacity .3s'; setTimeout(function(){ t.remove(); }, 300); }, 3200);
}

/* ---- Format currency ---- */
function formatCFA(n){
  return Math.round(n).toLocaleString('fr-FR').replace(/,/g,' ') + ' F CFA';
}

/* ---- CSRF ---- */
function getCookie(name){
  var m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? m.pop() : '';
}

/* ---- Inject CSS keyframes if not present ---- */
(function(){
  if(document.getElementById('cs-kf')) return;
  var s = document.createElement('style');
  s.id = 'cs-kf';
  s.textContent = '@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}';
  document.head.appendChild(s);
})();
