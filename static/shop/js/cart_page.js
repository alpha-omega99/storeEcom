/* ============================================================
   ChicShop — cart_page.js (CORRIGÉ)
   Page panier : mise à jour quantité, suppression, promo

   CORRECTIONS :
   - updateCartQty : envoie cart_key (pas product_id)
   - removeFromCart : envoie cart_key (pas product_id)
   - Mise à jour DOM par index de ligne (pas product.id)
   ============================================================ */

'use strict';

/* ===== METTRE À JOUR LA QUANTITÉ ===== */
async function updateCartQty(cartKey, delta) {
    // Trouver la ligne dans le DOM
    var itemEl = document.querySelector('[data-cart-key="' + cartKey + '"]');
    if (!itemEl) return;

    var qtyEl = itemEl.querySelector('.ci-qty span');
    var currentQty = parseInt(qtyEl.textContent, 10);
    var newQty = Math.max(1, Math.min(20, currentQty + delta));

    if (newQty === currentQty) return;

    try {
        // CORRECTION : envoie cart_key au lieu de product_id
        var data = await apiPost('/panier/modifier/', {
            cart_key: cartKey,
            quantity: newQty,
        });

        if (!data || data.error) {
            throw new Error(data.error || 'Erreur de mise à jour');
        }

        // Mise à jour du DOM
        qtyEl.textContent = newQty;

        // Mettre à jour le prix de la ligne
        var priceEl = itemEl.querySelector('.ci-price');
        if (priceEl && data.line_total !== undefined) {
            priceEl.textContent = formatPrice(data.line_total);
        }

        // Mettre à jour les totaux
        if (data.subtotal !== undefined) {
            updateTotals(data.subtotal);
        }

        updateCartBadge(data.cart_count);

    } catch (err) {
        showToast('❌ ' + err.message, 'error');
    }
}

/* ===== SUPPRIMER UN ARTICLE ===== */
async function removeFromCart(cartKey) {
    var itemEl = document.querySelector('[data-cart-key="' + cartKey + '"]');
    if (!itemEl) return;

    if (!confirm('Retirer cet article du panier ?')) return;

    try {
        // CORRECTION : envoie cart_key au lieu de product_id
        var data = await apiPost('/panier/supprimer/', {
            cart_key: cartKey,
        });

        if (!data || data.error) {
            throw new Error(data.error || 'Erreur de suppression');
        }

        // Animation de suppression
        itemEl.style.transition = 'all .3s ease';
        itemEl.style.opacity = '0';
        itemEl.style.transform = 'translateX(-20px)';

        setTimeout(function() {
            itemEl.remove();

            // Vérifier si le panier est vide
            var remaining = document.querySelectorAll('.cart-item');
            if (remaining.length === 0) {
                location.reload(); // Recharger pour afficher le panier vide
            }
        }, 300);

        // Mettre à jour les totaux
        if (data.subtotal !== undefined) {
            updateTotals(data.subtotal);
        }

        updateCartBadge(data.cart_count);
        showToast('🗑 Article retiré');

    } catch (err) {
        showToast('❌ ' + err.message, 'error');
    }
}

/* ===== METTRE À JOUR LES TOTAUX ===== */
function updateTotals(subtotal) {
    var subtotalEl = document.getElementById('cartSubtotal');
    var totalEl = document.getElementById('cartTotal');

    if (subtotalEl) subtotalEl.textContent = formatPrice(subtotal);
    if (totalEl) totalEl.textContent = formatPrice(subtotal);
}

/* ===== APPLIQUER UN CODE PROMO ===== */
async function applyPromoCode() {
    var input = document.getElementById('promoCode');
    var msg = document.getElementById('promoMsg');
    var code = input.value.trim().toUpperCase();

    if (!code) {
        msg.textContent = 'Veuillez entrer un code promo';
        msg.className = 'promo-msg error';
        return;
    }

    try {
        var data = await apiPost('/produits/promo/valider/', { code: code });

        if (data.valid) {
            msg.textContent = '✅ Code promo appliqué : -' + data.discount_percent + '%';
            msg.className = 'promo-msg success';
            // TODO: recalculer le total avec la remise
        } else {
            msg.textContent = '❌ ' + (data.error || 'Code promo invalide');
            msg.className = 'promo-msg error';
        }
    } catch (err) {
        msg.textContent = '❌ ' + err.message;
        msg.className = 'promo-msg error';
    }
}