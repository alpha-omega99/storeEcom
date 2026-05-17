/* ============================================================
   ChicShop — cart_page.js
   Page panier :
   - Mise à jour quantité (AJAX)
   - Suppression article
   - Application code promo
   ============================================================ */

'use strict';

/* ===== MISE À JOUR QUANTITÉ ===== */
async function updateCartQty(productId, delta) {
    const qtyEl = document.getElementById(`qty-${productId}`);
    if (!qtyEl) return;

    const currentQty = parseInt(qtyEl.textContent, 10);
    const newQty = Math.max(1, currentQty + delta);

    try {
        const data = await apiPost('/shop/cart/update/', {
            product_id: productId,
            quantity: newQty,
        });

        // Mise à jour UI locale
        qtyEl.textContent = newQty;
        const priceEl = document.getElementById(`price-${productId}`);
        if (priceEl && data.line_total !== undefined) {
            priceEl.textContent = Number(data.line_total).toLocaleString('fr-FR') + ' F';
        }
        updateCartBadge(data.cart_count);
        refreshCartTotals(data.subtotal);

    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    }
}

/* ===== SUPPRESSION ===== */
async function removeFromCart(productId) {
    try {
        const data = await apiPost('/shop/cart/remove/', { product_id: productId });

        // Retirer la ligne du DOM avec animation
        const row = document.getElementById(`ci-${productId}`);
        if (row) {
            row.style.transition = 'opacity .3s, transform .3s';
            row.style.opacity = '0';
            row.style.transform = 'translateX(-20px)';
            setTimeout(() => {
                row.remove();
                // Si panier vide, recharger
                const remaining = document.querySelectorAll('.cart-item');
                if (remaining.length === 0) location.reload();
            }, 320);
        }

        updateCartBadge(data.cart_count);
        refreshCartTotals(data.subtotal);
        showToast('Article supprimé du panier');

    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    }
}

/* ===== MISE À JOUR TOTAUX ===== */
function refreshCartTotals(subtotal) {
    const fmt = Number(subtotal).toLocaleString('fr-FR') + ' F CFA';
    const sub = document.getElementById('cartSubtotal');
    const tot = document.getElementById('cartTotal');
    if (sub) sub.textContent = fmt;
    if (tot) tot.textContent = fmt;
}

/* ===== CODE PROMO ===== */
async function applyPromoCode() {
    const input = document.getElementById('promoCode');
    const msgEl = document.getElementById('promoMsg');
    if (!input || !msgEl) return;

    const code = input.value.trim().toUpperCase();
    if (!code) return;

    msgEl.className = 'promo-msg';
    msgEl.textContent = '⏳ Vérification...';

    try {
        // Récupérer le sous-total actuel
        const subText = document.getElementById('cartSubtotal') ? .textContent || '0';
        const subVal = parseInt(subText.replace(/\D/g, ''), 10) || 0;

        const data = await apiPost('/api/v1/products/promo/validate/', {
            code: code,
            order_amount: subVal,
        });

        if (data.valid) {
            msgEl.className = 'promo-msg ok';
            msgEl.textContent = `🎉 Code appliqué — -${data.discount_percent}% !`;
            const tot = document.getElementById('cartTotal');
            if (tot) tot.textContent = Number(data.new_total).toLocaleString('fr-FR') + ' F CFA';
        } else {
            msgEl.className = 'promo-msg err';
            msgEl.textContent = data.detail || 'Code invalide ou expiré.';
        }
    } catch {
        msgEl.className = 'promo-msg err';
        msgEl.textContent = 'Erreur lors de la vérification du code.';
    }
}

/* ===== ENTRÉE CLAVIER CODE PROMO ===== */
document.addEventListener('DOMContentLoaded', () => {
    const promoInput = document.getElementById('promoCode');
    if (promoInput) {
        promoInput.addEventListener('keydown', e => {
            if (e.key === 'Enter') { e.preventDefault();
                applyPromoCode(); }
        });
    }
});