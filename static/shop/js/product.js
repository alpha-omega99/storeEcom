'use strict';

let _pdQty = 1;

async function apiPost(url, data) {
    // Va chercher le token CSRF stocké par Django dans les cookies du navigateur
    const csrfToken = document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken=')) ?
        .split('=')[1];

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Insère le token dans les headers de la requête
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Erreur (${response.status})`);
    }

    return await response.json();
}

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
    // Sélectionne l'id présent selon si c'est le placeholder ou l'aperçu sous l'input
    const preview = document.getElementById('pdLiveName') || document.getElementById('pdNamePreview');
    if (!preview) return;
    const text = value.trim() || 'Votre prénom';
    preview.textContent = text;
    preview.style.transform = 'scale(1.04)';
    setTimeout(() => { preview.style.transform = 'scale(1)'; }, 200);
}

/* ===== AJOUTER AU PANIER DEPUIS DÉTAIL ===== */
async function addToCartFromDetail(productId, name, price, emoji, btn) {
    // CORRECTION SYNTAXE : Pas d'espaces pour le ?.
    const embroidery = document.getElementById('embroideryInput') ? .value ? .trim() || '';

    // Ton HTML n'a pas de section taille active, mais on laisse la sécurité au cas où
    const sizeEl = document.querySelector('.schip.sel');
    const size = sizeEl ? (sizeEl.dataset.size || sizeEl.textContent.trim()) : '';

    // Détecte dynamiquement le texte initial du bouton cliqué
    const originalText = btn ? btn.textContent : '🛒 Ajouter au panier';

    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Ajout...';
    }

    try {
        // Envoi des données vers ton backend Django
        const data = await apiPost('/shop/cart/add/', {
            product_id: productId,
            quantity: _pdQty,
            embroidery_name: embroidery,
            selected_size: size,
        });

        // Mise à jour de l'interface (Vérifie bien que ces fonctions globales existent !)
        if (typeof updateCartBadge === 'function') updateCartBadge(data.cart_count);
        if (typeof showToast === 'function') {
            showToast(`✅ ${name} ajouté au panier !`);
        } else {
            alert(`✅ ${name} ajouté au panier !`);
        }

        if (btn) {
            btn.style.background = '#28a745';
            btn.style.color = '#ffffff';
            btn.textContent = '✅ Ajouté !';
        }

        setTimeout(() => {
            if (btn) {
                btn.style.background = '';
                btn.style.color = '';
                btn.textContent = originalText;
                btn.disabled = false;
            }
        }, 2000);

    } catch (err) {
        if (typeof showToast === 'function') {
            showToast(`❌ ${err.message}`, 'error');
        } else {
            alert(`❌ ${err.message}`);
        }

        if (btn) {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    }
}

/* ===== ACHETER MAINTENANT ===== */
async function buyNow(productId, name, price, emoji, btn) {
    const embroidery = document.getElementById('embroideryInput') ? .value ? .trim() || '';
    const sizeEl = document.querySelector('.schip.sel');
    const size = sizeEl ? (sizeEl.dataset.size || sizeEl.textContent.trim()) : '';

    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Redirection...';
    }

    try {
        await apiPost('/shop/cart/add/', {
            product_id: productId,
            quantity: _pdQty,
            embroidery_name: embroidery,
            selected_size: size,
        });

        // Redirection vers ton étape de validation de commande
        window.location.href = '/shop/checkout/';

    } catch (err) {
        if (typeof showToast === 'function') {
            showToast(`❌ ${err.message}`, 'error');
        } else {
            alert(`❌ ${err.message}`);
        }

        if (btn) {
            btn.disabled = false;
            btn.textContent = '💸 Acheter maintenant';
        }
    }
}

/* ===== INIT ===== */
document.addEventListener('DOMContentLoaded', () => {
    const firstTab = document.querySelector('.pd-tab');
    if (firstTab) firstTab.setAttribute('aria-selected', 'true');
});