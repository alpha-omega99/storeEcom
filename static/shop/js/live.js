/* ============================================================
   ChicShop — live.js
   Popup activité temps réel, compteur de ventes animé
   ============================================================ */

'use strict';

const liveActivities = [
    { init: 'F', name: 'Fatou D.', action: 'vient de commander L\'Écrin de Sérénité', time: 'Il y a 2 min' },
    { init: 'A', name: 'Aminata B.', action: 'a ajouté L\'Héritage Royal à son panier', time: 'Il y a 5 min' },
    { init: 'M', name: 'Mamadou K.', action: 'vient de commander le Pack Mariage', time: 'Il y a 8 min' },
    { init: 'S', name: 'Salimata O.', action: 'a laissé un avis ★★★★★', time: 'Il y a 12 min' },
    { init: 'I', name: 'Ibrahim D.', action: 'vient de commander le Duo Essentiel', time: 'Il y a 15 min' },
    { init: 'K', name: 'Kadiatou M.', action: 'vient de commander le Tapis Rose Poudré', time: 'Il y a 18 min' },
];

let _laIndex = 0;

function showLiveActivity() {
    const popup = document.getElementById('livePopup');
    if (!popup) return;

    const a = liveActivities[_laIndex % liveActivities.length];
    _laIndex++;

    popup.style.display = 'flex';
    popup.innerHTML = `
    <div class="lp-avatar">${a.init}</div>
    <div class="lp-text">
      <strong>${a.name}</strong>
      ${a.action}
      <div class="lp-time">🟢 ${a.time}</div>
    </div>
  `;
    popup.classList.remove('hide');

    setTimeout(() => {
        popup.classList.add('hide');
        setTimeout(() => { popup.style.display = 'none'; }, 450);
    }, 4200);
}

/* ===== COMPTEUR DE VENTES ANIMÉ ===== */
function animateSalesCounter() {
    const el = document.getElementById('salesCpt');
    if (!el) return;
    const flash = () => {
        el.style.color = 'var(--or)';
        el.textContent = parseInt(el.textContent, 10) + 1;
        setTimeout(() => { el.style.color = ''; }, 1000);
    };
    setInterval(() => { if (Math.random() > 0.65) flash(); }, 9000);
}

/* ===== INIT ===== */
document.addEventListener('DOMContentLoaded', () => {
    // Premier popup après 3s, puis toutes les 12s
    setTimeout(showLiveActivity, 3000);
    setInterval(showLiveActivity, 12000);
    animateSalesCounter();
});