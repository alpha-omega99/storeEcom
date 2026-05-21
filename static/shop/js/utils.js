/* ============================================================
   ChicShop — utils.js
   Utilitaires globaux : toast, CSRF, fetch helpers, wishlist

   CORRECTIONS :
   - syncWishlistServer : URL /api/v1/wishlist/ remplacée par /favoris/toggle/
     qui existe réellement dans shop/urls.py
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
    // 1. Cherche dans le formulaire Django
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    if (el) return el.value;
    // 2. Cherche dans la balise meta
    var meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content');
    // 3. Cherche dans le cookie (fallback)
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
    // Ajouter le slash final si absent (Django redirige sinon en 301)
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

/* ===== WISHLIST (localStorage) ===== */
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
    has: function(id) {
        return this.get().indexOf(Number(id)) !== -1;
    },
    add: function(id) {
        var l = this.get();
        if (l.indexOf(Number(id)) === -1) {
            l.push(Number(id));
            this.set(l);
        }
    },
    remove: function(id) {
        this.set(this.get().filter(function(x) { return x !== Number(id); }));
    },
    toggle: function(id) {
        if (this.has(id)) { this.remove(id); } else { this.add(id); }
        return this.has(id);
    },
};

/* ===== TOGGLE WISHLIST ===== */
function toggleWish(productId, btn) {
    var active = WishlistStore.toggle(productId);

    // Mettre à jour tous les boutons ♡ de ce produit
    document.querySelectorAll('.pwish').forEach(function(b) {
        if (b.getAttribute('onclick') && b.getAttribute('onclick').indexOf(String(productId)) !== -1) {
            b.classList.toggle('active', active);
        }
    });
    if (btn) btn.classList.toggle('active', active);

    showToast(active ? '❤️ Ajouté aux favoris !' : 'Retiré des favoris');

    // CORRECTION : URL correcte /favoris/toggle/ (existe dans shop/urls.py)
    syncWishlistServer(productId, active);
}

async function syncWishlistServer(productId, add) {
    try {
        await apiPost('/favoris/toggle/', {
            product_id: productId,
            action: add ? 'add' : 'remove'
        });
    } catch (e) {
        // Silencieux — localStorage fait foi en fallback
    }
}

/* ===== INIT WISHLIST AU CHARGEMENT ===== */
function initWishlistButtons() {
    var ids = WishlistStore.get();
    ids.forEach(function(id) {
        document.querySelectorAll('.pwish').forEach(function(b) {
            if (b.getAttribute('onclick') && b.getAttribute('onclick').indexOf(String(id)) !== -1) {
                b.classList.add('active');
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', initWishlistButtons);