/* ============================================================
   ChicShop — catalog.js
   Page catalogue :
   - Filtres couleur interactifs
   - Range prix avec affichage dynamique
   ============================================================ */

'use strict';

document.addEventListener('DOMContentLoaded', () => {

    /* ===== FILTRES COULEUR ===== */
    document.querySelectorAll('.cf-dot').forEach(dot => {
        dot.addEventListener('click', function() {
            this.classList.toggle('sel');
        });
    });

    /* ===== RANGE PRIX ===== */
    const priceRange = document.getElementById('priceRange');
    const priceVal = document.getElementById('priceVal');
    if (priceRange && priceVal) {
        priceRange.addEventListener('input', function() {
            priceVal.textContent = Number(this.value).toLocaleString('fr-FR');
        });
    }

    /* ===== AUTO-SUBMIT SORT ===== */
    const sortForm = document.getElementById('sortForm');
    if (sortForm) {
        sortForm.querySelector('select') ? .addEventListener('change', () => sortForm.submit());
    }

});