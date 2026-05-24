/* ============================================================
   ChicShop — cart_page.js (NOUVEAU)
   Logique de la page panier : modifier quantité, supprimer, promo

   FONCTIONS :
   - updateCartQty(cartKey, delta) : +1 / -1 quantité
   - removeFromCart(cartKey) : supprimer un article
   - updateCartDisplay() : recalcule les totaux
   - applyPromoCode() : applique un code promo
   ============================================================ */

'use strict';

/* ===== METTRE À JOUR LA QUANTITÉ ===== */
async function updateCartQty(cartKey, delta) {
    var itemEl = document.querySelector('[data-cart-key="' + cartKey + '"]');
    if (!itemEl) return;

    var qtyEl = itemEl.querySelector('[id^="qty-"]');
    if (!qtyEl) return;

    var currentQty = parseInt(qtyEl.textContent, 10) || 1;
    var newQty = Math.max(1, Math.min(20, currentQty + delta));

    if (newQty === currentQty) return;

    // Feedback visuel immédiat
    qtyEl.style.opacity = '0.5';

    try {
        var res = await apiPost('/panier/modifier/', {
            cart_key: cartKey,
            quantity: newQty,
        });

        if (!res || res.error) {
            throw new Error(res.error || 'Erreur de mise à jour');
        }

        // Mise à jour DOM
        qtyEl.textContent = newQty;
        qtyEl.style.opacity = '1';

        // Mettre à jour le prix de la ligne
        var priceEl = itemEl.querySelector('[id^="price-"]');
        if (priceEl && res.line_total !== undefined) {
            priceEl.textContent = formatPrice(res.line_total) + ' F';
        }

        // Mettre à jour les totaux
        if (res.subtotal !== undefined) {
            updateCartTotals(res.subtotal);
        }

        updateCartBadge(res.cart_count);

    } catch (err) {
        console.error('[updateCartQty]', err);
        qtyEl.style.opacity = '1';
        showToast('❌ ' + err.message, 'error');
    }
}

/* ===== SUPPRIMER UN ARTICLE ===== */
async function removeFromCart(cartKey) {
    var itemEl = document.querySelector('[data-cart-key="' + cartKey + '"]');
    if (!itemEl) return;

    if (!confirm('Supprimer cet article du panier ?')) return;

    // Animation de suppression
    itemEl.style.transition = 'all 0.3s ease';
    itemEl.style.opacity = '0';
    itemEl.style.transform = 'translateX(-100px)';

    try {
        var res = await apiPost('/panier/supprimer/', {
            cart_key: cartKey,
        });

        if (!res || res.error) {
            throw new Error(res.error || 'Erreur de suppression');
        }

        // Supprimer du DOM après animation
        setTimeout(function() {
            itemEl.remove();

            // Vérifier si panier vide
            var remaining = document.querySelectorAll('.cart-item');
            if (remaining.length === 0) {
                location.reload(); // Recharger pour afficher le panier vide
            }
        }, 300);

        if (res.subtotal !== undefined) {
            updateCartTotals(res.subtotal);
        }

        updateCartBadge(res.cart_count);
        showToast('🗑 Article supprimé');

    } catch (err) {
        console.error('[removeFromCart]', err);
        itemEl.style.opacity = '1';
        itemEl.style.transform = 'none';
        showToast('❌ ' + err.message, 'error');
    }
}

/* ===== METTRE À JOUR LES TOTAUX ===== */
function updateCartTotals(subtotal) {
    var subtotalEl = document.getElementById('cartSubtotal');
    var totalEl = document.getElementById('cartTotal');

    var formatted = formatPrice(subtotal) + ' F CFA';

    if (subtotalEl) subtotalEl.textContent = formatted;
    if (totalEl) totalEl.textContent = formatted;

    // Animation des totaux
    [subtotalEl, totalEl].forEach(function(el) {
        if (el) {
            el.style.transition = 'color 0.3s';
            el.style.color = '#c0392b';
            setTimeout(function() {
                el.style.color = '';
            }, 500);
        }
    });

    // Désactiver le bouton commander si panier vide
    var checkoutBtn = document.querySelector('.checkout-btn');
    if (checkoutBtn && subtotal <= 0) {
        checkoutBtn.classList.add('disabled');
        checkoutBtn.style.pointerEvents = 'none';
        checkoutBtn.style.opacity = '0.5';
    }
}


/* ===== INIT : vérifier l'état du panier au chargement ===== */
document.addEventListener('DOMContentLoaded', function() {
    var items = document.querySelectorAll('.cart-item');
    var checkoutBtn = document.querySelector('.checkout-btn');

    if (items.length === 0 && checkoutBtn) {
        checkoutBtn.classList.add('disabled');
        checkoutBtn.style.pointerEvents = 'none';
        checkoutBtn.style.opacity = '0.5';
    }
});