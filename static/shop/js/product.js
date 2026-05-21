/* ============================================================
   ChicShop — product.js (CORRIGÉ)
   Page détail produit

   CORRECTIONS :
   - buyNow() : vérification de la réponse avant redirection
   - buyNow() : vérification taille sélectionnée obligatoire
   - buyNow() : mise à jour badge panier avant redirection
   - addToCartFromDetail() : vérification taille + gestion erreur améliorée
   - Sélection taille par défaut au DOMContentLoaded
   ============================================================ */

'use strict';

let _pdQty = 1;

/* ===== GESTION DES ONGLETS ===== */
function switchTab(el, contentId) {
    const infoBlock = el.closest('.pd-info');
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

/* ===== SÉLECTION MINIATURE ===== */
function selectThumb(el, imgUrl) {
    document.querySelectorAll('.pd-thumb').forEach(function(t) {
        t.classList.remove('sel');
    });
    el.classList.add('sel');
    if (imgUrl) {
        var main = document.getElementById('pdMainImgEl');
        if (main) main.src = imgUrl;
    }
}

/* ===== SÉLECTION TAILLE ===== */
function selectSize(el) {
    var parent = el.closest('.size-chips');
    if (parent) {
        parent.querySelectorAll('.schip').forEach(function(s) {
            s.classList.remove('sel');
        });
    }
    el.classList.add('sel');
}

/* ===== QUANTITÉ ===== */
function changeQty(delta) {
    _pdQty = Math.max(1, Math.min(20, _pdQty + delta));
    var el = document.getElementById('pdQty');
    if (el) el.textContent = _pdQty;
}

/* ===== APERÇU BRODERIE EN TEMPS RÉEL ===== */
function updateEmbroideryPreview(value) {
    var preview = document.getElementById('pdLiveName') || document.getElementById('pdNamePreview');
    if (!preview) return;
    var text = value.trim() || 'Votre prénom';
    preview.textContent = text;
    preview.style.transform = 'scale(1.04)';
    setTimeout(function() {
        preview.style.transform = 'scale(1)';
    }, 200);
}

/* ===== VÉRIFICATION TAILLE ===== */
function _getSelectedSize() {
    var sizeEl = document.querySelector('.schip.sel');
    return sizeEl ? (sizeEl.dataset.size || sizeEl.textContent.trim()) : '';
}

function _hasSizesAvailable() {
    return document.querySelectorAll('.schip').length > 0;
}

function _validateSize() {
    if (_hasSizesAvailable() && !_getSelectedSize()) {
        showToast('❌ Veuillez sélectionner une taille', 'error');
        return false;
    }
    return true;
}

/* ===== AJOUTER AU PANIER DEPUIS LA PAGE DÉTAIL ===== */
async function addToCartFromDetail(productId, name, price, emoji, btn) {
    if (!_validateSize()) return;

    var embroideryEl = document.getElementById('embroideryInput');
    var embroidery = embroideryEl ? embroideryEl.value.trim() : '';
    var size = _getSelectedSize();
    var originalText = btn ? btn.textContent : '🛒 Ajouter au panier';

    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Ajout...';
    }

    try {
        var data = await apiPost('/panier/ajouter/', {
            product_id: productId,
            quantity: _pdQty,
            embroidery_name: embroidery,
            selected_size: size,
        });

        // VÉRIFICATION : s'assurer que l'ajout a bien fonctionné
        if (!data || data.error) {
            throw new Error(data.error || 'Erreur lors de l'
                ajout au panier ');
            }

            updateCartBadge(data.cart_count);
            showToast('✅ ' + name + ' ajouté au panier !');

            if (btn) {
                btn.style.background = '#28a745';
                btn.style.color = '#ffffff';
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
        if (!_validateSize()) return;

        var embroideryEl = document.getElementById('embroideryInput');
        var embroidery = embroideryEl ? embroideryEl.value.trim() : '';
        var size = _getSelectedSize();

        if (btn) {
            btn.disabled = true;
            btn.textContent = '⏳ Ajout...';
        }

        try {
            var data = await apiPost('/panier/ajouter/', {
                product_id: productId,
                quantity: _pdQty,
                embroidery_name: embroidery,
                selected_size: size,
            });

            // VÉRIFICATION CRITIQUE : s'assurer que l'ajout a fonctionné
            if (!data || data.error) {
                throw new Error(data.error || 'Erreur lors de l'
                    ajout au panier ');
                }

                // Mettre à jour le badge AVANT de rediriger
                if (data.cart_count !== undefined) {
                    updateCartBadge(data.cart_count);
                }

                // Redirection SEULEMENT si succès confirmé
                window.location.href = '/commander/';

            } catch (err) {
                showToast('❌ ' + err.message, 'error');
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = '💸 Acheter maintenant';
                }
            }
        }

        /* ===== INIT PAGE DÉTAIL ===== */
        document.addEventListener('DOMContentLoaded', function() {
            // Activer aria-selected sur le premier onglet
            var firstTab = document.querySelector('.pd-tab');
            if (firstTab) firstTab.setAttribute('aria-selected', 'true');

            // Sélectionner la première taille disponible par défaut
            var chips = document.querySelectorAll('.schip');
            if (chips.length > 0) {
                chips[0].classList.add('sel');
            }
        });