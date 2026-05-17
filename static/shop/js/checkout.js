/* ============================================================
   ChicShop — checkout.js
   Page checkout :
   - Sélection mode de paiement
   - Validation côté client avant soumission
   ============================================================ */

'use strict';

/* ===== SÉLECTION MODE PAIEMENT ===== */
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.pm-opt').forEach(opt => {
        opt.addEventListener('click', function() {
            document.querySelectorAll('.pm-opt').forEach(o => o.classList.remove('sel'));
            this.classList.add('sel');
            // Cocher le radio caché
            const radio = this.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });

    /* ===== VALIDATION FORMULAIRE ===== */
    const form = document.getElementById('checkoutForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        let valid = true;

        // Prénom
        const fname = document.getElementById('firstName');
        if (fname && fname.value.trim().length < 2) {
            markError(fname, 'Prénom obligatoire (min. 2 caractères)');
            valid = false;
        } else if (fname) clearError(fname);

        // Téléphone
        const phone = document.getElementById('phone');
        if (phone) {
            const cleaned = phone.value.replace(/[\s\-\.\(\)]/g, '');
            if (!/^\+?\d{8,15}$/.test(cleaned)) {
                markError(phone, 'Numéro de téléphone invalide');
                valid = false;
            } else clearError(phone);
        }

        // Adresse
        const addr = document.getElementById('address');
        if (addr && addr.value.trim().length < 5) {
            markError(addr, 'Adresse complète obligatoire');
            valid = false;
        } else if (addr) clearError(addr);

        // Prénom broderie
        const emb = document.getElementById('embroideryName');
        if (emb && emb.value.trim()) {
            if (!/^[\w\sÀ-ÿ\-']+$/u.test(emb.value.trim())) {
                markError(emb, 'Le prénom brodé ne peut contenir que des lettres');
                valid = false;
            } else clearError(emb);
        }

        if (!valid) {
            e.preventDefault();
            showToast('❌ Veuillez corriger les champs en rouge', 'error');
            // Scroller vers la première erreur
            const firstErr = form.querySelector('.error');
            if (firstErr) firstErr.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });
});

function markError(el, msg) {
    el.classList.add('error');
    let hint = el.parentElement.querySelector('.field-error');
    if (!hint) {
        hint = document.createElement('span');
        hint.className = 'field-error';
        hint.style.cssText = 'font-size:10px;color:#ff4444;display:block;margin-top:3px';
        el.parentElement.appendChild(hint);
    }
    hint.textContent = msg;
}

function clearError(el) {
    el.classList.remove('error');
    const hint = el.parentElement.querySelector('.field-error');
    if (hint) hint.remove();
}