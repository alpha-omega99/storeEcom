/* ============================================================
   ChicShop — product.js
   Page détail produit

   CORRECTIONS FINALES :
   1. getCsrfToken() vient de utils.js — pas redéfini ici
   2. personal_message inclus dans addToCartFromDetail et buyNow
   3. UUID passé comme string (pas int)
   4. Validation prénom obligatoire si allows_embroidery
   ============================================================ */

'use strict';

var _pdQty = 1;

/* ===== ONGLETS ===== */
function switchTab(el, contentId) {
    var infoBlock = el.closest('.pd-info');
    if (!infoBlock) return;
    infoBlock.querySelectorAll('.pd-tab').forEach(function(t) {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
    });
    infoBlock.querySelectorAll('.pd-tab-content').forEach(function(c) {
        c.classList.remove('active');
    });
    el.classList.add('active');
    el.setAttribute('aria-selected', 'true');
    var content = document.getElementById(contentId);
    if (content) content.classList.add('active');
}

/* ===== MINIATURE ===== */
function selectThumb(el, imgUrl) {
    document.querySelectorAll('.pd-thumb').forEach(function(t) { t.classList.remove('sel'); });
    el.classList.add('sel');
    if (imgUrl) {
        var main = document.getElementById('pdMainImgEl');
        if (main) main.src = imgUrl;
    }
}


/* ===== QUANTITÉ ===== */
function changeQty(delta) {
    _pdQty = Math.max(1, Math.min(20, _pdQty + delta));
    var el = document.getElementById('pdQty');
    if (el) el.textContent = _pdQty;
}

/* ===== APERÇU BRODERIE ===== */
function updateEmbroideryPreview(value) {
    var preview = document.getElementById('pdLiveName') || document.getElementById('pdNamePreview');
    if (!preview) return;
    preview.textContent = value.trim() || 'Votre prénom';
    preview.style.transform = 'scale(1.04)';
    setTimeout(function() { preview.style.transform = 'scale(1)'; }, 200);
}

/* ===== RÉCUPÉRER LES CHAMPS DE PERSONNALISATION ===== */
function getPersonalisationData() {
    var embroideryEl = document.getElementById('embroideryInput');
    var personalMsgEl = document.getElementById('personalMsgInput');

    return {
        embroidery: embroideryEl ? embroideryEl.value.trim() : '',
        personalMessage: personalMsgEl ? personalMsgEl.value.trim() : '',
    };
}

/* ===== AJOUTER AU PANIER ===== */
async function addToCartFromDetail(productId, name, price, emoji, btn) {
    var data = getPersonalisationData();
    var originalText = btn ? btn.textContent : '🛒 Ajouter au panier';

    // Validation : prénom obligatoire si le champ existe
    var embroideryEl = document.getElementById('embroideryInput');
    if (embroideryEl && !data.embroidery) {
        embroideryEl.classList.add('error');
        showToast('⚠️ Veuillez entrer un prénom à personnaliser', 'error');
        embroideryEl.focus();
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Ajout...';
    }

    try {
        var res = await apiPost('/panier/ajouter/', {
            product_id: productId, // UUID string
            quantity: _pdQty,
            embroidery_name: data.embroidery,
            personal_message: data.personalMessage,
        });

        updateCartBadge(res.cart_count);
        showToast('✅ ' + name + ' ajouté au panier !');

        if (btn) {
            btn.style.background = '#28a745';
            btn.style.color = '#fff';
            btn.textContent = '✅ Ajouté !';
        }
        setTimeout(function() {
            if (btn) {
                btn.style.background = '';
                btn.style.color = '';
                btn.textContent = originalText;
                btn.disabled = false;
            }
        }, 2000);

    } catch (err) {
        showToast('❌ ' + err.message, 'error');
        if (btn) {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    }
}

/* ===== ACHETER MAINTENANT ===== */
async function buyNow(productId, name, price, emoji, btn) {
    var data = getPersonalisationData();

    // Validation : prénom obligatoire si le champ existe
    var embroideryEl = document.getElementById('embroideryInput');
    if (embroideryEl && !data.embroidery) {
        embroideryEl.classList.add('error');
        showToast('⚠️ Veuillez entrer un prénom à personnaliser', 'error');
        embroideryEl.focus();
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Préparation...';
    }

    try {
        var res = await apiPost('/panier/ajouter/', {
            product_id: productId, // UUID string
            quantity: _pdQty,
            embroidery_name: data.embroidery,
            personal_message: data.personalMessage,
        });

        updateCartBadge(res.cart_count);
        // Redirection seulement si succès
        window.location.href = '/commander/';

    } catch (err) {
        showToast('❌ ' + err.message, 'error');
        if (btn) {
            btn.disabled = false;
            btn.textContent = '💸 Acheter maintenant';
        }
    }
}

/* ===== INIT ===== */
document.addEventListener('DOMContentLoaded', function() {
    // Premier onglet actif
    var firstTab = document.querySelector('.pd-tab');
    if (firstTab) firstTab.setAttribute('aria-selected', 'true');

    // Retirer l'erreur quand l'utilisateur commence à taper
    var embroideryEl = document.getElementById('embroideryInput');
    if (embroideryEl) {
        embroideryEl.addEventListener('input', function() {
            this.classList.remove('error');
        });
    }
});