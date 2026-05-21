/* ============================================================
   ChicShop — cart.js
   Gestion globale du panier : badge, add to cart
   Appelé sur toutes les pages via base.html

   CORRECTIONS :
   - URLs corrigées : /shop/cart/add/ → /panier/ajouter/
   - URLs corrigées : /shop/cart/count/ → /panier/count/
   ============================================================ */

'use strict';

/* ===== ADD TO CART (depuis grille catalogue, flash sale) ===== */
async function addToCart(productId, name, price, emoji) {
    try {
        const data = await apiPost('/panier/ajouter/', {
            product_id: productId,
            quantity: 1,
        });
        updateCartBadge(data.cart_count);
        showToast(`✅ ${name} ajouté au panier !`);
    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    }
}

/* ===== CHARGER LE BADGE PANIER AU DÉMARRAGE ===== */
async function loadCartBadge() {
    try {
        const data = await apiGet('/panier/count/');
        updateCartBadge(data.cart_count);
    } catch {
        // Silencieux — le template a déjà rendu la valeur serveur
    }
}

document.addEventListener('DOMContentLoaded', loadCartBadge);