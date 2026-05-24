/* ============================================================
   ChicShop — product.js (CORRIGÉ)
   Page détail produit

   MODIFICATIONS :
   - selectSize() renommé → selectRecipient()
   - _selectedSize → _selectedRecipient
   - getPersonalisationData() renvoie selected_recipient
   ============================================================ */

'use strict';

var _pdQty = 1;
var _selectedRecipient = '';

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

/* ===== SÉLECTION DESTINATAIRE (NOUVEAU) ===== */
function selectRecipient(el) {
    document.querySelectorAll('.recipient-chip').forEach(function(btn) {
        btn.classList.remove('sel');
    });
    el.classList.add('sel');
    _selectedRecipient = el.getAttribute('data-recipient') || '';

    // Feedback visuel
    var hint = document.querySelector('.recipient-hint');
    if (hint) {
        hint.textContent = 'Pour ' + _selectedRecipient + ' ✓';
        hint.style.color = '#2d6e2d';
    }
}

/* ===== QUANTITÉ (avec limite de stock) ===== */
function changeQty(delta) {
    var stockEl = document.getElementById('pdStockQty');
    var maxQty = stockEl ? parseInt(stockEl.value, 10) || 20 : 20;
    _pdQty = Math.max(1, Math.min(maxQty, _pdQty + delta));
    var el = document.getElementById('pdQty');
    if (el) el.textContent = _pdQty;
}

/* ===== APERÇU BRODERIE ===== */
function updateEmbroideryPreview(value) {
    var preview = document.getElementById('pdLiveName') || document.getElementById('pdNamePreview');
    if (!preview) return;
    preview.textContent = value.trim() || 'Votre Nom et prénom';
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
        selectedRecipient: _selectedRecipient,
    };
}

/* ===== VALIDATION DES CONDITIONS D'ACHAT ===== */
function validatePurchaseConditions() {
    var errors = [];

    // Vérifier si un destinataire est requis et sélectionné
    var recipientChips = document.querySelectorAll('.recipient-chip');
    if (recipientChips.length > 0 && !_selectedRecipient) {
        errors.push("Veuillez sélectionner à qui vous offrez ce cadeau");
        var hint = document.querySelector('.recipient-hint');
        if (hint) {
            hint.textContent = '⚠️ Veuillez choisir un destinataire';
            hint.style.color = '#c0392b';
        }
    }

    // Vérifier la broderie si le champ est visible ET requis
    var embroideryEl = document.getElementById('embroideryInput');
    if (embroideryEl && embroideryEl.hasAttribute('required') && !embroideryEl.value.trim()) {
        embroideryEl.classList.add('error');
        errors.push('Veuillez entrer un Nom ou prénom à personnaliser');
    }

    // Vérifier le stock
    var stockEl = document.getElementById('pdStockQty');
    var maxStock = stockEl ? parseInt(stockEl.value, 10) || 999 : 999;
    if (_pdQty > maxStock) {
        errors.push('Stock insuffisant. Disponible : ' + maxStock);
    }

    return errors;
}

/* ===== AJOUTER AU PANIER ===== */
async function addToCartFromDetail(productId, name, price, emoji, btn) {
    var data = getPersonalisationData();
    var originalText = btn ? btn.textContent : '🛒 Ajouter au panier';

    // Validation
    var errors = validatePurchaseConditions();
    if (errors.length > 0) {
        showToast('⚠️ ' + errors[0], 'error');
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Ajout...';
    }

    try {
        var res = await apiPost('/panier/ajouter/', {
            product_id: String(productId),
            quantity: _pdQty,
            embroidery_name: data.embroidery,
            personal_message: data.personalMessage,
        });

        if (!res || res.error) {
            throw new Error(res.error || "Erreur lors de l'ajout");
        }

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
        console.error('[addToCartFromDetail]', err);
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
    var originalText = btn ? btn.textContent : '💸 Acheter maintenant';

    // Validation des conditions AVANT tout
    var errors = validatePurchaseConditions();
    if (errors.length > 0) {
        showToast('⚠️ ' + errors[0], 'error');
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Préparation...';
    }

    try {
        var res = await apiPost('/panier/ajouter/', {
            product_id: String(productId),
            quantity: _pdQty,
            embroidery_name: data.embroidery,
            personal_message: data.personalMessage,
        });

        if (!res || res.error) {
            throw new Error(res.error || "Impossible d'ajouter au panier");
        }

        updateCartBadge(res.cart_count);
        showToast('🛒 Redirection vers la commande...');
        window.location.href = '/commander/';

    } catch (err) {
        console.error('[buyNow]', err);
        showToast('❌ ' + err.message, 'error');
        if (btn) {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    }
}

/* ===== INIT ===== */
document.addEventListener('DOMContentLoaded', function() {
    // Premier onglet actif
    var firstTab = document.querySelector('.pd-tab');
    if (firstTab) firstTab.setAttribute('aria-selected', 'true');

    // Initialiser le destinataire sélectionné si déjà présent
    var preselected = document.querySelector('.recipient-chip.sel');
    if (preselected) {
        _selectedRecipient = preselected.getAttribute('data-recipient') || '';
    }

    // Retirer l'erreur quand l'utilisateur commence à taper
    var embroideryEl = document.getElementById('embroideryInput');
    if (embroideryEl) {
        embroideryEl.addEventListener('input', function() {
            this.classList.remove('error');
        });
    }
});