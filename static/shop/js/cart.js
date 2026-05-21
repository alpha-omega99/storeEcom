/* ============================================================
   ChicShop — cart.js (CORRIGÉ)
   Gestion globale du panier : badge, add to cart
   Appelé sur toutes les pages via base.html

   CORRECTIONS :
   - addToCart : envoie aussi selected_size et embroidery_name
   - addToCart : vérifie la réponse avant toast
   ============================================================ */

'use strict';

/* ===== ADD TO CART (depuis grille catalogue, flash sale) ===== */
async function addToCart(productId, name, price, emoji) {
    try {
        var data = await apiPost('/panier/ajouter/', {
            product_id: productId,
            quantity: 1,
            selected_size: '',
            embroidery_name: '',
        });

        // VÉRIFICATION : s'assurer que l'ajout a fonctionné
        if (!data || data.error) {
            throw new Error(data.error || "Erreur lors de l'ajout au panier ");
        }

        updateCartBadge(data.cart_count);
        showToast('✅ ' + name + ' ajouté au panier !');
    } catch (err) {
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
    } catch {
        // Silencieux — le template a déjà rendu la valeur serveur
    }
}

document.addEventListener('DOMContentLoaded', loadCartBadge);