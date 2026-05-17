/* ============================================================
   ChicShop — home.js
   Spécifique à la page d'accueil :
   - Timer vente flash
   - Rotation des prénoms dans le hero
   ============================================================ */

'use strict';

/* ===== FLASH SALE TIMER ===== */
(function() {
    // Fin de la vente flash : +6h à partir du chargement (peut être dynamisé via data-attr)
    const endTs = Date.now() + (5 * 3600 + 47 * 60 + 23) * 1000;

    function tick() {
        const diff = Math.max(0, Math.floor((endTs - Date.now()) / 1000));
        const h = Math.floor(diff / 3600);
        const m = Math.floor((diff % 3600) / 60);
        const s = diff % 60;
        const pad = n => String(n).padStart(2, '0');
        const elH = document.getElementById('fh');
        const elM = document.getElementById('fm');
        const elS = document.getElementById('fs');
        if (elH) elH.textContent = pad(h);
        if (elM) elM.textContent = pad(m);
        if (elS) elS.textContent = pad(s);
        if (diff === 0) clearInterval(timer);
    }
    tick();
    const timer = setInterval(tick, 1000);
})();

/* ===== ROTATION PRÉNOMS HERO ===== */
(function() {
    const heroNames = ['Fatima', 'Ibrahim', 'Maïssa', 'Aminata', 'Mohamed', 'Aïcha', 'Kadiatou'];
    let idx = 0;

    setInterval(() => {
        idx = (idx + 1) % heroNames.length;
        const el = document.getElementById('heroName');
        if (!el) return;
        el.style.opacity = '0';
        el.style.transform = 'translateY(-6px)';
        setTimeout(() => {
            el.textContent = heroNames[idx];
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 400);
    }, 3000);
})();