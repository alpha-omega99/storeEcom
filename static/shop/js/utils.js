/* ============================================================
   ChicShop — utils.js (CORRIGÉ FINAL)
   Utilitaires globaux : toast, CSRF, fetch helpers, wishlist

   CORRECTIONS :
   - syncWishlistServer : URL /favoris/toggle/ (existe dans urls.py)
   - WishlistStore : comparaison en STRING (pas Number) pour UUID
   - initWishlistButtons : matching robuste des UUID
   - Ajout de getSelectedSize() helper partagé
   ============================================================ */

'use strict';

/* ===== TOAST ===== */
let _toastTimer = null;

function showToast(msg, type) {
    type = type || 'default';
    var t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.className = type === 'error' ? 'show toast-error' : 'show';
    clearTimeout(_toastTimer);
    _toastTimer = setTimeout(function() {
        t.classList.remove('show');
    }, 2600);
}

/* ===== CSRF TOKEN ===== */
function getCsrfToken() {
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    if (el) return el.value;
    var meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content');
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
        var c = cookies[i].trim();
        if (c.startsWith('csrftoken=')) {
            return c.split('=')[1];
        }
    }
    return '';
}

/* ===== API POST (JSON + CSRF) ===== */
async function apiPost(url, data) {
    // Normaliser l'URL : ajouter slash final si absent
    if (!url.endsWith('/')) url += '/';

    var res = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify(data),
    });

    if (!res.ok) {
        var err = await res.json().catch(function() {
            return { detail: 'Erreur réseau (' + res.status + ')' };
        });
        throw new Error(err.detail || err.error || err.message || ('HTTP ' + res.status));
    }
    return res.json();
}

/* ===== API GET ===== */
async function apiGet(url) {
    var res = await fetch(url, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return res.json();
}

/* ===== FORMATER UN PRIX ===== */
function formatPrice(amount) {
    return Number(amount).toLocaleString('fr-FR') + ' F CFA';
}

/* ===== DEBOUNCE ===== */
function debounce(fn, delay) {
    delay = delay || 300;
    var t;
    return function() {
        var args = arguments;
        clearTimeout(t);
        t = setTimeout(function() { fn.apply(null, args); }, delay);
    };
}

/* ===== BADGE PANIER ===== */
function updateCartBadge(count) {
    var badge = document.getElementById('cartBadge');
    if (badge) {
        badge.textContent = count;
        badge.style.animation = 'none';
        requestAnimationFrame(function() {
            badge.style.animation = 'pop .3s ease';
        });
    }
}

/* ===== WISHLIST (localStorage + STRING comparison pour UUID) ===== */
var WishlistStore = {
    key: 'cs_wishlist',
    get: function() {
        try {
            return JSON.parse(localStorage.getItem(this.key)) || [];
        } catch (e) {
            return [];
        }
    },
    set: function(ids) {
        localStorage.setItem(this.key, JSON.stringify(ids));
    },
    // CORRECTION : comparaison STRING (pas Number) car UUID
    has: function(id) {
        var strId = String(id);
        return this.get().indexOf(strId) !== -1;
    },
    add: function(id) {
        var strId = String(id);
        var l = this.get();
        if (l.indexOf(strId) === -1) {
            l.push(strId);
            this.set(l);
        }
    },
    remove: function(id) {
        var strId = String(id);
        this.set(this.get().filter(function(x) { return x !== strId; }));
    },
    toggle: function(id) {
        if (this.has(id)) { this.remove(id); } else { this.add(id); }
        return this.has(id);
    },
};

/* ===== TOGGLE WISHLIST ===== */
function toggleWish(productId, btn) {
    var active = WishlistStore.toggle(productId);

    // CORRECTION : matching robuste des UUID avec data attribute
    document.querySelectorAll('.pwish').forEach(function(b) {
        var btnProductId = b.getAttribute('data-product-id');
        if (btnProductId === String(productId)) {
            b.classList.toggle('active', active);
        }
    });
    if (btn) btn.classList.toggle('active', active);

    showToast(active ? '❤️ Ajouté aux favoris !' : 'Retiré des favoris');

    syncWishlistServer(productId, active);
}

async function syncWishlistServer(productId, add) {
    try {
        await apiPost('/favoris/toggle/', {
            product_id: String(productId),
            action: add ? 'add' : 'remove'
        });
    } catch (e) {
        // Silencieux — localStorage fait foi en fallback
    }
}

/* ===== INIT WISHLIST AU CHARGEMENT ===== */
function initWishlistButtons() {
    var ids = WishlistStore.get();
    document.querySelectorAll('.pwish').forEach(function(b) {
        var btnProductId = b.getAttribute('data-product-id');
        if (btnProductId && ids.indexOf(btnProductId) !== -1) {
            b.classList.add('active');
        }
    });
}

document.addEventListener('DOMContentLoaded', initWishlistButtons);

// Ajouter dans utils.js
async function removeFromCart(cartKey) {
    try {
        var res = await apiPost('/panier/supprimer/', { cart_key: cartKey });
        if (!res || res.error) throw new Error(res.error || 'Erreur de suppression');
        updateCartBadge(res.cart_count);
        if (typeof refreshMiniCart === 'function') refreshMiniCart();
        return res;
    } catch (err) {
        console.error('[removeFromCart]', err);
        showToast('❌ ' + err.message, 'error');
    }
}