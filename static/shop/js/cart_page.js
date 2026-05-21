/* ============================================================
   ChicShop — cart_page.js
   Page panier : quantité, suppression, code promo

   CORRECTIONS :
   - URLs corrigées : /shop/cart/update/ → /panier/modifier/
   - URLs corrigées : /shop/cart/remove/ → /panier/supprimer/
   - Promo code : URL /api/v1/products/promo/validate/ → /products/promo/validate/
   ============================================================ */

'use strict';

/* ===== MISE À JOUR QUANTITÉ ===== */
async function updateCartQty(productId, delta) {
    var qtyEl = document.getElementById('qty-' + productId);
    if (!qtyEl) return;

    var currentQty = parseInt(qtyEl.textContent, 10);
    var newQty = Math.max(1, currentQty + delta);

    try {
        // CORRECTION : URL /panier/modifier/
        var data = await apiPost('/panier/modifier/', {
            product_id: productId,
            quantity: newQty,
        });

        qtyEl.textContent = newQty;

        var priceEl = document.getElementById('price-' + productId);
        if (priceEl && data.line_total !== undefined) {
            priceEl.textContent = Number(data.line_total).toLocaleString('fr-FR') + ' F';
        }

        updateCartBadge(data.cart_count);
        refreshCartTotals(data.subtotal);

    } catch (err) {
        showToast('❌ ' + err.message, 'error');
    }
}

/* ===== SUPPRESSION D'UN ARTICLE ===== */
async function removeFromCart(productId) {
    try {
        // CORRECTION : URL /panier/supprimer/
        var data = await apiPost('/panier/supprimer/', {
            product_id: productId
        });

        var row = document.getElementById('ci-' + productId);
        if (row) {
            row.style.transition = 'opacity .3s, transform .3s';
            row.style.opacity = '0';
            row.style.transform = 'translateX(-20px)';
            setTimeout(function() {
                row.remove();
                var remaining = document.querySelectorAll('.cart-item');
                if (remaining.length === 0) location.reload();
            }, 320);
        }

        updateCartBadge(data.cart_count);
        refreshCartTotals(data.subtotal);
        showToast('Article supprimé du panier');

    } catch (err) {
        showToast('❌ ' + err.message, 'error');
    }
}

/* ===== MISE À JOUR DES TOTAUX ===== */
function refreshCartTotals(subtotal) {
    var fmt = Number(subtotal).toLocaleString('fr-FR') + ' F CFA';
    var sub = document.getElementById('cartSubtotal');
    var tot = document.getElementById('cartTotal');
    if (sub) sub.textContent = fmt;
    if (tot) tot.textContent = fmt;
}

/* ===== APPLICATION DU CODE PROMO ===== */
async function applyPromoCode() {
    var input = document.getElementById('promoCode');
    var msgEl = document.getElementById('promoMsg');
    if (!input || !msgEl) return;

    var code = input.value.trim().toUpperCase();
    if (!code) {
        showToast('Entrez un code promo', 'error');
        return;
    }

    msgEl.className = 'promo-msg';
    msgEl.textContent = '⏳ Vérification...';

    try {
        var subText = document.getElementById('cartSubtotal');
        var subVal = subText ? parseInt(subText.textContent.replace(/\D/g, ''), 10) : 0;

        // CORRECTION : URL /products/promo/validate/ (sans /api/v1/ — selon config/urls.py)
        var data = await apiPost('/products/promo/validate/', {
            code: code,
            order_amount: subVal,
        });

        if (data.valid) {
            msgEl.className = 'promo-msg ok';
            msgEl.textContent = '🎉 Code appliqué — -' + data.discount_percent + '% !';
            var tot = document.getElementById('cartTotal');
            if (tot) tot.textContent = Number(data.new_total).toLocaleString('fr-FR') + ' F CFA';
        } else {
            msgEl.className = 'promo-msg err';
            msgEl.textContent = data.detail || 'Code invalide ou expiré.';
        }
    } catch (e) {
        msgEl.className = 'promo-msg err';
        msgEl.textContent = 'Erreur lors de la vérification.';
    }
}

/* ===== ENTRÉE CLAVIER CODE PROMO ===== */
document.addEventListener('DOMContentLoaded', function() {
    var promoInput = document.getElementById('promoCode');
    if (promoInput) {
        promoInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                applyPromoCode();
            }
        });
    }
});