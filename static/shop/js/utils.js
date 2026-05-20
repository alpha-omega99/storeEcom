/* ============================================================
   ChicShop — utils.js
   Utilitaires globaux : toast, CSRF, helpers
   ============================================================ */

'use strict';

/* ===== TOAST ===== */
let _toastTimer = null;

function showToast(msg, type = 'default') {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.className = type === 'error' ? 'show toast-error' : 'show';
    clearTimeout(_toastTimer);
    _toastTimer = setTimeout(() => t.classList.remove('show'), 2600);
}

/* ===== CSRF TOKEN ===== */
function getCsrfToken() {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    if (el) return el.value;
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content');
    const cookie = document.cookie.split(';')
        .find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

/* ===== API HELPER (fetch JSON avec CSRF) ===== */
async function apiPost(url, data) {
    const res = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Erreur réseau' }));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

async function apiGet(url) {
    const res = await fetch(url, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

/* ===== FORMATER UN PRIX ===== */
function formatPrice(amount) {
    return Number(amount).toLocaleString('fr-FR') + ' F CFA';
}

/* ===== DEBOUNCE ===== */
function debounce(fn, delay = 300) {
    let t;
    return (...args) => { clearTimeout(t);
        t = setTimeout(() => fn(...args), delay); };
}

/* ===== BADGE PANIER ===== */
function updateCartBadge(count) {
    const badge = document.getElementById('cartBadge');
    if (badge) {
        badge.textContent = count;
        badge.style.animation = 'none';
        requestAnimationFrame(() => { badge.style.animation = 'pop .3s ease'; });
    }
}

/* ===== WISHLIST (localStorage) ===== */
const WishlistStore = {
    key: 'cs_wishlist',
    get() { try { return JSON.parse(localStorage.getItem(this.key)) || []; } catch { return []; } },
    set(ids) { localStorage.setItem(this.key, JSON.stringify(ids)); },
    has(id) { return this.get().includes(Number(id)); },
    add(id) { const l = this.get(); if (!l.includes(Number(id))) { l.push(Number(id));
            this.set(l); } },
    remove(id) { this.set(this.get().filter(x => x !== Number(id))); },
    toggle(id) { this.has(id) ? this.remove(id) : this.add(id); return this.has(id); },
};

/* ===== TOGGLE WISHLIST (appelé par tous les boutons ♡) ===== */
function toggleWish(productId, btn) {
    const active = WishlistStore.toggle(productId);
    // Mettre à jour tous les boutons avec ce product id
    document.querySelectorAll(`.pwish[onclick*="${productId}"]`).forEach(b => {
        b.classList.toggle('active', active);
    });
    if (btn) btn.classList.toggle('active', active);
    showToast(active ? '❤️ Ajouté aux favoris !' : 'Retiré des favoris');
    // Sync avec le serveur si connecté
    syncWishlistServer(productId, active);
}

async function syncWishlistServer(productId, add) {
    try {
        await apiPost('/api/v1/wishlist/', { product_id: productId, action: add ? 'add' : 'remove' });
    } catch {
        // Silencieux — le localStorage fait foi en fallback
    }
}

/* ===== INITIALISER L'ÉTAT WISHLIST AU CHARGEMENT ===== */
function initWishlistButtons() {
    const ids = WishlistStore.get();
    ids.forEach(id => {
        document.querySelectorAll(`.pwish[onclick*="${id}"]`).forEach(b => b.classList.add('active'));
    });
}
document.addEventListener('DOMContentLoaded', initWishlistButtons);