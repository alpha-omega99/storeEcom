// Cart functionality for ChicShop
const CART_KEY = 'chicshop_cart_v1';

function getCart() {
    try {
        return JSON.parse(localStorage.getItem(CART_KEY)) || [];
    } catch { return []; }
}

function saveCart(items) {
    localStorage.setItem(CART_KEY, JSON.stringify(items));
    updateCartUI();
}

function addToCart(slug, qty = 1, embroidery = '') {
    const cart = getCart();
    const key = slug + '::' + (embroidery || '');
    const idx = cart.findIndex(it => it.key === key);
    if (idx >= 0) {
        cart[idx].quantity += qty;
    } else {
        // Fetch product info from DOM or API
        const card = document.querySelector(`[data-testid="product-card-${slug}"]`);
        const name = card?.querySelector('.product-name')?.textContent || slug;
        const priceText = card?.querySelector('.product-price')?.textContent || '0';
        const price = parseInt(priceText.replace(/[^0-9]/g, '')) || 0;
        const img = card?.querySelector('img')?.src || '';
        cart.push({ key, product_slug: slug, name, price, image: img, quantity: qty, embroidery_name: embroidery || null });
    }
    saveCart(cart);
    showToast(`${qty > 1 ? qty + 'x ' : ''}Ajoute au panier`);
    openCart();
}

function removeFromCart(key) {
    const cart = getCart().filter(it => it.key !== key);
    saveCart(cart);
}

function updateQty(key, delta) {
    const cart = getCart();
    const idx = cart.findIndex(it => it.key === key);
    if (idx >= 0) {
        cart[idx].quantity = Math.max(1, cart[idx].quantity + delta);
        saveCart(cart);
    }
}

function clearCart() {
    localStorage.removeItem(CART_KEY);
    updateCartUI();
}

function updateCartUI() {
    const items = getCart();
    const count = items.reduce((s, it) => s + it.quantity, 0);
    const subtotal = items.reduce((s, it) => s + it.price * it.quantity, 0);

    // Update badge
    const badge = document.getElementById('cartBadge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'grid' : 'none';
    }

    // Update drawer
    const body = document.getElementById('cartBody');
    const footer = document.getElementById('cartFooter');
    const countEl = document.getElementById('cartCount');
    const subtotalEl = document.getElementById('cartSubtotal');

    if (countEl) countEl.textContent = count;
    if (subtotalEl) subtotalEl.textContent = formatCFA(subtotal);

    if (items.length === 0) {
        if (body) body.innerHTML = `
            <div class="cart-empty">
                <div class="cart-empty-icon">&#128722;</div>
                <p>Votre panier est vide pour l'instant</p>
                <a href="/catalogue/" class="btn-emerald" onclick="toggleCart()">Decouvrir nos tapis</a>
            </div>`;
        if (footer) footer.style.display = 'none';
    } else {
        if (body) {
            body.innerHTML = items.map((it, i) => `
                <div class="cart-item" data-testid="cart-item-${i}">
                    <div class="cart-item-img"><img src="${it.image || ''}" alt=""></div>
                    <div class="cart-item-info">
                        <div class="cart-item-name">${it.name}</div>
                        ${it.embroidery_name ? `<div class="cart-item-embroidery">Broderie: <span>${it.embroidery_name}</span></div>` : ''}
                        <div class="cart-item-row">
                            <div class="cart-qty">
                                <button onclick="updateQty('${it.key}', -1)">-</button>
                                <span data-testid="qty-${i}">${it.quantity}</span>
                                <button onclick="updateQty('${it.key}', 1)">+</button>
                            </div>
                            <div class="cart-item-price">${formatCFA(it.price * it.quantity)}</div>
                        </div>
                    </div>
                    <button class="cart-item-remove" onclick="removeFromCart('${it.key}')">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                    </button>
                </div>
            `).join('');
        }
        if (footer) footer.style.display = 'block';
    }
}

function toggleCart() {
    const drawer = document.getElementById('cartDrawer');
    const overlay = document.getElementById('cartOverlay');
    if (!drawer) return;
    drawer.classList.toggle('open');
    overlay.classList.toggle('open');
    document.body.style.overflow = drawer.classList.contains('open') ? 'hidden' : '';
}

function openCart() {
    const drawer = document.getElementById('cartDrawer');
    const overlay = document.getElementById('cartOverlay');
    if (drawer) drawer.classList.add('open');
    if (overlay) overlay.classList.add('open');
}

function toggleMobileMenu() {
    const nav = document.querySelector('.main-nav');
    if (nav) nav.classList.toggle('mobile-open');
}

// Initialize
document.addEventListener('DOMContentLoaded', updateCartUI);