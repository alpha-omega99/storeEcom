/* ============================================================
   ChicShop — cart.js
   Gestion complète du panier (localStorage)
   ============================================================ */

var CART_KEY = 'chicshop_cart_v1';

/* ---- Lecture / écriture ---- */
function getCart(){ return JSON.parse(localStorage.getItem(CART_KEY) || '[]'); }
function saveCart(c){ localStorage.setItem(CART_KEY, JSON.stringify(c)); }

/* ---- Badge header ---- */
function updateCartBadge(count){
  var badge = document.getElementById('cartBadge');
  if(!badge) return;
  if(count > 0){
    badge.textContent = count > 99 ? '99+' : count;
    badge.style.display = 'grid';
  } else {
    badge.style.display = 'none';
  }
}

/* ---- Ajouter au panier ---- */
function addToCart(slug, qty, embroidery){
  qty = qty || 1;
  embroidery = embroidery || null;

  fetch('/api/products/' + slug + '/', {
    headers: { 'Accept': 'application/json' }
  })
  .then(function(r){ return r.ok ? r.json() : Promise.reject(r.status); })
  .then(function(product){
    var cart = getCart();
    var key  = slug + '::' + (embroidery || '');
    var idx  = cart.findIndex(function(i){ return i.product_slug+'::'+i.embroidery_name === key; });
    if(idx >= 0){
      cart[idx].quantity += qty;
    } else {
      cart.push({
        product_slug:   product.slug,
        name:           product.name,
        price:          product.price,
        image:          product.image || '',
        quantity:       qty,
        embroidery_name: embroidery
      });
    }
    saveCart(cart);
    var total = cart.reduce(function(s,i){ return s+i.quantity; }, 0);
    updateCartBadge(total);
    refreshCartDrawer();
    showToast && showToast(product.name + ' ajouté au panier ✦');
    // ouvre le tiroir
    var d = document.getElementById('cartDrawer');
    var o = document.getElementById('cartDrawerOverlay');
    if(d && !d.classList.contains('open')){
      d.classList.add('open');
      if(o) o.classList.add('open');
      d.setAttribute('aria-hidden','false');
      document.body.style.overflow = 'hidden';
    }
  })
  .catch(function(){
    // fallback : ajout sans données produit
    var cart = getCart();
    var key  = slug + '::' + (embroidery || '');
    var idx  = cart.findIndex(function(i){ return i.product_slug+'::'+i.embroidery_name === key; });
    if(idx >= 0){ cart[idx].quantity += qty; }
    else { cart.push({ product_slug:slug, name:slug, price:0, image:'', quantity:qty, embroidery_name:embroidery }); }
    saveCart(cart);
    var total = cart.reduce(function(s,i){ return s+i.quantity; }, 0);
    updateCartBadge(total);
    refreshCartDrawer();
    showToast && showToast('Produit ajouté au panier');
  });
}

/* ---- Rendu du tiroir ---- */
function refreshCartDrawer(){
  var cart    = getCart();
  var list    = document.getElementById('cdList');
  var empty   = document.getElementById('cdEmpty');
  var foot    = document.getElementById('cdFoot');
  var title   = document.getElementById('cdTitle');
  var subtEl  = document.getElementById('cdSubtotal');
  if(!list) return;

  var count = cart.reduce(function(s,i){ return s+i.quantity; }, 0);
  if(title) title.textContent = count + ' article' + (count > 1 ? 's' : '');

  if(!cart.length){
    if(empty) empty.style.display = 'block';
    list.innerHTML = '';
    if(foot) foot.style.display = 'none';
    return;
  }
  if(empty) empty.style.display = 'none';
  if(foot)  foot.style.display  = 'block';

  var sub = cart.reduce(function(s,i){ return s+i.price*i.quantity; }, 0);
  if(subtEl) subtEl.textContent = formatCFA(sub);

  list.innerHTML = cart.map(function(it, i){
    return '<li class="cd-item" data-testid="cart-item-' + i + '">'
      + '<div class="cd-item-img">'
      + (it.image ? '<img src="'+it.image+'" alt="'+it.name+'">' : '')
      + '</div>'
      + '<div class="cd-item-info">'
      + '<div class="cd-item-name">' + it.name + '</div>'
      + (it.embroidery_name ? '<div class="cd-item-opt">' + it.embroidery_name + '</div>' : '')
      + '<div class="cd-item-qty" style="display:flex;align-items:center;gap:6px;margin-top:6px">'
      + '<div style="display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:40px">'
      + '<button onclick="cartDrawerQty('+i+',-1)" style="width:26px;height:26px;border:none;background:none;cursor:pointer;font-size:14px;color:var(--emerald)" data-testid="qty-decrease-'+i+'">&#8722;</button>'
      + '<span style="padding:0 8px;font-size:12px" data-testid="qty-'+i+'">' + it.quantity + '</span>'
      + '<button onclick="cartDrawerQty('+i+',1)"  style="width:26px;height:26px;border:none;background:none;cursor:pointer;font-size:14px;color:var(--emerald)" data-testid="qty-increase-'+i+'">&#43;</button>'
      + '</div>'
      + '<span style="font-size:13px;font-weight:500;color:var(--emerald)">' + formatCFA(it.price*it.quantity) + '</span>'
      + '</div>'
      + '<button class="cd-item-remove" onclick="cartDrawerRemove('+i+')">Retirer</button>'
      + '</div>'
      + '</li>';
  }).join('');
}

function cartDrawerQty(i, d){
  var cart = getCart();
  cart[i].quantity = Math.max(1, cart[i].quantity + d);
  saveCart(cart);
  updateCartBadge(cart.reduce(function(s,it){return s+it.quantity;},0));
  refreshCartDrawer();
}
function cartDrawerRemove(i){
  var cart = getCart();
  cart.splice(i, 1);
  saveCart(cart);
  updateCartBadge(cart.reduce(function(s,it){return s+it.quantity;},0));
  refreshCartDrawer();
}

/* ---- Init au chargement ---- */
document.addEventListener('DOMContentLoaded', function(){
  var cart  = getCart();
  var total = cart.reduce(function(s,i){ return s+i.quantity; }, 0);
  updateCartBadge(total);
  refreshCartDrawer();
});
