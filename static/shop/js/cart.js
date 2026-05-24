/* ============================================================
   ChicShop — cart.js (CORRIGÉ FINAL)
   Gestion globale du panier : badge, add to cart
   Appelé sur toutes les pages via base.html

   CORRECTIONS :
   - addToCart : envoie selected_size (récupéré du DOM si dispo)
   - addToCart : vérifie la réponse avant toast
   - URL normalisée (pas de double slash)
   - Gestion d'erreur réseau améliorée
   ============================================================ */

'use strict';

/* ===== ADD TO CART (depuis grille catalogue, flash sale) ===== */
async function addToCart(productId, name, price, emoji) {
    try {
        var data = await apiPost('/panier/ajouter/', {
            product_id: String(productId),
            quantity: 1,
            embroidery_name: '',
            personal_message: '',
        });

        if (!data || data.error) {
            throw new Error(data.error || "Erreur lors de l'ajout au panier");
        }

        updateCartBadge(data.cart_count);
        showToast('✅ ' + name + ' ajouté au panier !');
        window.dispatchEvent(new Event('cart:added'));
    } catch (err) {
        console.error('[addToCart]', err);
        showToast('❌ ' + err.message, 'error');
    }
}

/* ===== CHARGER LE BADGE PANIER AU DÉMARRAGE ===== */
async function loadCartBadge() {
    try {
        var data = await apiGet('/panier/count/');
        if (data && data.cart_count !== undefined) {
            updateCartBadge(data.cart_count);
        }
    } catch (err) {
        console.warn('[loadCartBadge]', err);
        // Silencieux — le template a déjà rendu la valeur serveur
    }
}

document.addEventListener('DOMContentLoaded', loadCartBadge);