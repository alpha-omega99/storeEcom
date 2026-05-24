/* ============================================================
   ChicShop — checkout.js (CORRIGÉ)
   Page checkout :
   - Sélection mode de paiement
   - Validation côté client avant soumission
   - Bouton de soumission avec état de chargement
   ============================================================ */

'use strict';

/* ===== SÉLECTION MODE PAIEMENT ===== */
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.pm-opt').forEach(function(opt) {
        opt.addEventListener('click', function() {
            document.querySelectorAll('.pm-opt').forEach(function(o) { o.classList.remove('sel'); });
            this.classList.add('sel');
            var radio = this.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });

    /* ===== VALIDATION FORMULAIRE ===== */
    var form = document.getElementById('checkoutForm');
    var submitBtn = document.getElementById('submitBtn');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        var valid = true;
        var errors = [];

        // Réinitialiser les erreurs
        document.querySelectorAll('.error').forEach(function(el) { el.classList.remove('error'); });
        document.querySelectorAll('.field-error').forEach(function(el) { el.remove(); });

        // Prénom
        var fname = document.getElementById('firstName');
        if (fname && fname.value.trim().length < 2) {
            markError(fname, 'Prénom obligatoire (min. 2 caractères)');
            valid = false;
            errors.push('Prénom');
        }

        // Nom
        var lname = document.getElementById('lastName');
        if (lname && lname.value.trim().length < 2) {
            markError(lname, 'Nom obligatoire (min. 2 caractères)');
            valid = false;
            errors.push('Nom');
        }

        // Téléphone
        var phone = document.getElementById('phone');
        if (phone) {
            var cleaned = phone.value.replace(/[\s\-\.\(\)]/g, '');
            if (!cleaned) {
                markError(phone, 'Téléphone obligatoire');
                valid = false;
                errors.push('Téléphone');
            } else if (!/^\+?\d{8,15}$/.test(cleaned)) {
                markError(phone, 'Numéro de téléphone invalide (ex: +2250700000000)');
                valid = false;
                errors.push('Téléphone');
            }
        }

        // Adresse
        var addr = document.getElementById('address');
        if (addr && addr.value.trim().length < 5) {
            markError(addr, 'Adresse complète obligatoire (min. 5 caractères)');
            valid = false;
            errors.push('Adresse');
        }

        // Commune
        var city = document.getElementById('city');
        if (city && !city.value) {
            markError(city, 'Veuillez sélectionner une commune');
            valid = false;
            errors.push('Commune');
        }

        // Prénom broderie (optionnel mais si rempli, validation)
        var emb = document.getElementById('embroideryName');
        if (emb && emb.value.trim()) {
            if (!/^[\w\s\u00C0-\u017F\-'']+$/u.test(emb.value.trim())) {
                markError(emb, 'Le prénom ne peut contenir que des lettres');
                valid = false;
                errors.push('Prénom broderie');
            }
        }

        if (!valid) {
            e.preventDefault();

            // Afficher le résumé des erreurs
            var errorBox = document.getElementById('formErrors');
            if (errorBox) {
                errorBox.style.display = 'block';
                errorBox.innerHTML = '❌ Veuillez remplir les champs suivants : <strong>' + errors.join(', ') + '</strong>';
            }

            showToast('❌ Veuillez corriger les champs en rouge', 'error');

            // Scroller vers la première erreur
            var firstErr = form.querySelector('.error');
            if (firstErr) {
                firstErr.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstErr.focus();
            }
        } else {
            // Tout est valide → désactiver le bouton pour éviter double soumission
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = '⏳ Traitement en cours...';
                submitBtn.style.opacity = '0.7';
            }
        }
    });

    /* ===== VALIDATION EN TEMPS RÉEL ===== */
    ['firstName', 'lastName', 'phone', 'address', 'city'].forEach(function(id) {
        var el = document.getElementById(id);
        if (el) {
            el.addEventListener('blur', function() {
                if (this.value.trim()) {
                    clearError(this);
                }
            });
            el.addEventListener('input', function() {
                if (this.classList.contains('error')) {
                    clearError(this);
                }
            });
        }
    });
});

function markError(el, msg) {
    el.classList.add('error');
    var hint = el.parentElement.querySelector('.field-error');
    if (!hint) {
        hint = document.createElement('span');
        hint.className = 'field-error';
        hint.style.cssText = 'font-size:11px;color:#e74c3c;display:block;margin-top:4px;font-weight:500';
        el.parentElement.appendChild(hint);
    }
    hint.textContent = msg;
}

function clearError(el) {
    el.classList.remove('error');
    var hint = el.parentElement.querySelector('.field-error');
    if (hint) hint.remove();
}