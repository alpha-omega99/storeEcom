/* ============================================================
   ChicShop — product.js
   Page détail produit :
   - Aperçu broderie en temps réel
   - Gestion onglets
   - Sélection taille / miniature
   - Quantité
   - Ajout au panier
   ============================================================ */

'use strict';

let _pdQty = 1;

/* ===== ONGLETS ===== */
function switchTab(el, contentId) {
    const infoBlock = el.closest('.pd-info');
    infoBlock.querySelectorAll('.pd-tab').forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
    });
    infoBlock.querySelectorAll('.pd-tab-content').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    el.setAttribute('aria-selected', 'true');
    const content = document.getElementById(contentId);
    if (content) content.classList.add('active');
}

/* ===== SÉLECTION TAILLE ===== */
function selectSize(el) {
    el.closest('.size-chips').querySelectorAll('.schip').forEach(s => s.classList.remove('sel'));
    el.classList.add('sel');
}

/* ===== SÉLECTION MINIATURE ===== */
function selectThumb(el, imgUrl) {
    document.querySelectorAll('.pd-thumb').forEach(t => t.classList.remove('sel'));
    el.classList.add('sel');
    if (imgUrl) {
        const main = document.getElementById('pdMainImgEl');
        if (main) main.src = imgUrl;
    }
}

/* ===== QUANTITÉ ===== */
function changeQty(delta) {
    _pdQty = Math.max(1, Math.min(20, _pdQty + delta));
    const el = document.getElementById('pdQty');
    if (el) el.textContent = _pdQty;
}

/* ===== APERÇU BRODERIE ===== */
function updateEmbroideryPreview(value) {
    const preview = document.getElementById('pdLiveName') || document.getElementById('pdNamePreview');
    if (!preview) return;
    const text = value.trim() || 'Votre prénom';
    preview.textContent = text;
    preview.style.transform = 'scale(1.04)';
    setTimeout(() => { preview.style.transform = 'scale(1)'; }, 200);
}

/* ===== AJOUTER AU PANIER DEPUIS DÉTAIL ===== */
async function addToCartFromDetail(productId, name, price, emoji) {
    const embroidery = document.getElementById('embroideryInput') ? .value ? .trim() || '';
    const sizeEl = document.querySelector('.schip.sel');
    const size = sizeEl ? sizeEl.dataset.size || sizeEl.textContent.trim() : '';
    const btn = document.querySelector('.btn-addcart');

    if (btn) { btn.disabled = true;
        btn.textContent = '⏳ Ajout...'; }

    try {
        const data = await apiPost('/shop/cart/add/', {
            product_id: productId,
            quantity: _pdQty,
            embroidery_name: embroidery,
            selected_size: size,
        });
        updateCartBadge(data.cart_count);
        showToast(`✅ ${name} ajouté au panier !`);
        if (btn) { btn.style.background = '#28a745';
            btn.textContent = '✅ Ajouté !'; }
        setTimeout(() => {
            if (btn) { btn.style.background = '';
                btn.textContent = '🛒 Ajouter au panier';
                btn.disabled = false; }
        }, 2000);
    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
        if (btn) { btn.disabled = false;
            btn.textContent = '🛒 Ajouter au panier'; }
    }
}

/* ===== INIT ===== */
document.addEventListener('DOMContentLoaded', () => {
    // Activer le premier onglet
    const firstTab = document.querySelector('.pd-tab');
    if (firstTab) firstTab.setAttribute('aria-selected', 'true');

    // Sélectionner la 2ème taille par défaut (comme dans l'original)
    const chips = document.querySelectorAll('.schip');
    if (chips.length >= 2) {
        chips[0].classList.remove('sel');
        chips[1].classList.add('sel');
    } else if (chips.length === 1) {
        chips[0].classList.add('sel');
    }
});