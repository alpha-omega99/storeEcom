"""
ChicShop — Views shop (COMPLET + CORRIGÉ)

CORRECTIONS :
- Panier : clé composite (product_id:size:embroidery) pour gérer les variantes
- cart_update / cart_remove : acceptent cart_key au lieu de product_id
- checkout : panier vidé SEULEMENT après création commande réussie
- require_POST importé correctement
"""

import json
import logging
from decimal import Decimal

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.orders.views import Order, OrderItem, generate_order_reference
from apps.products.models import Category, Product, ProductReview, PromoCode

logger = logging.getLogger('chicshop')


# ------------------------------------------------------------------ #
#  HELPERS PANIER SESSION (CORRIGÉS)
# ------------------------------------------------------------------ #

CART_SESSION_KEY = 'chicshop_cart'


def get_cart(request):
    return request.session.get(CART_SESSION_KEY, {})


def save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def cart_count(request):
    return sum(item.get('qty', 1) for item in get_cart(request).values())


def _make_cart_key(product_id, size, embroidery):
    """Crée une clé unique pour chaque variante de produit."""
    return f"{product_id}:{size or 'default'}:{embroidery or 'none'}"


def cart_items_with_products(request):
    cart = get_cart(request)
    items = []
    if not cart:
        return items, Decimal(0)

    # Extraire les product_ids des clés composites
    product_ids = []
    for key in cart.keys():
        try:
            pid = int(key.split(':')[0])
            product_ids.append(pid)
        except (ValueError, IndexError):
            continue

    products = {
        str(p.id): p
        for p in Product.objects.filter(id__in=product_ids, is_active=True)
    }

    subtotal = Decimal(0)
    for key, data in cart.items():
        try:
            pid = int(key.split(':')[0])
        except (ValueError, IndexError):
            continue

        product = products.get(str(pid))
        if not product:
            continue
        qty = data.get('qty', 1)
        line_total = product.price * qty
        subtotal += line_total
        items.append({
            'cart_key':        key,
            'product':         product,
            'quantity':        qty,
            'size':            data.get('size', ''),
            'embroidery_name': data.get('embroidery_name', ''),
            'line_total':      line_total,
        })
    return items, subtotal


# ------------------------------------------------------------------ #
#  PAGE ACCUEIL
# ------------------------------------------------------------------ #

def home(request):
    featured_products = Product.objects.filter(
        is_active=True, is_available=True
    ).select_related('category').prefetch_related('reviews').order_by('-sales_count')[:8]

    flash_products = Product.objects.filter(
        is_active=True, is_available=True, original_price__isnull=False
    ).order_by('-sales_count')[:6]

    categories = Category.objects.filter(is_active=True).order_by('order')
    for cat in categories:
        cat.product_count = cat.products.filter(is_active=True, is_available=True).count()

    testimonials = ProductReview.objects.filter(
        is_approved=True
    ).select_related('product').order_by('-created_at')[:6]

    colors = [
        ('#fce8f0', '#7a1a3a'), ('#e0f0ff', '#1a3a7a'), ('#e8f5e9', '#1a6b3a'),
        ('#fff8e0', '#7a5000'), ('#f5e8ff', '#4a1a7a'), ('#e8f0ff', '#1a3a6a'),
    ]
    testi_data = []
    for i, r in enumerate(testimonials):
        bg, fg = colors[i % len(colors)]
        testi_data.append({
            'name':         r.author_name,
            'city':         r.author_city or 'Abidjan',
            'initial':      r.author_name[0].upper() if r.author_name else 'A',
            'avatar_bg':    bg,
            'avatar_color': fg,
            'rating':       r.rating,
            'comment':      r.comment,
            'time_ago':     _time_ago(r.created_at),
        })

    return render(request, 'shop/home.html', {
        'featured_products': featured_products,
        'flash_products':    flash_products,
        'categories':        categories,
        'testimonials':      testi_data,
        'today_sales':       14,
        'current_cat':       None,
    })


# ------------------------------------------------------------------ #
#  CATALOGUE
# ------------------------------------------------------------------ #

def catalog(request, category_slug=None):
    qs = Product.objects.filter(
        is_active=True
    ).select_related('category').prefetch_related('reviews')

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        qs = qs.filter(category=current_category)

    max_price = request.GET.get('max_price')
    if max_price:
        try:
            qs = qs.filter(price__lte=Decimal(max_price))
        except Exception:
            pass

    if request.GET.get('available'):
        qs = qs.filter(is_available=True)
    if request.GET.get('promo'):
        qs = qs.filter(original_price__isnull=False, badge='PROMO')
    if request.GET.get('new'):
        qs = qs.filter(badge='NEW')
    if request.GET.get('embroidery'):
        qs = qs.filter(allows_embroidery=True)

    order = request.GET.get('order', '-sales_count')
    if order not in ['price', '-price', '-sales_count', '-created_at']:
        order = '-sales_count'
    qs = qs.order_by(order)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'shop/catalog.html', {
        'products':         page_obj,
        'current_category': current_category,
        'current_cat':      category_slug,
        'max_price':        max_price or 50000,
        'search_query':     '',
        'wishlist_ids':     _get_wishlist_ids(request),
    })


def search(request):
    q = request.GET.get('q', '').strip()
    qs = Product.objects.none()

    if q and len(q) >= 2:
        qs = Product.objects.filter(is_active=True).filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(color__icontains=q) |
            Q(category__name__icontains=q)
        ).select_related('category').distinct()

    return render(request, 'shop/search.html', {
        'products':     qs,
        'search_query': q,
        'current_cat':  None,
        'wishlist_ids': _get_wishlist_ids(request),
    })


# ------------------------------------------------------------------ #
#  DÉTAIL PRODUIT
# ------------------------------------------------------------------ #

def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('reviews'),
        slug=slug, is_active=True
    )
    product.increment_views()

    similar = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk).order_by('-sales_count')[:4]

    product.recent_reviews = product.reviews.filter(is_approved=True).order_by('-created_at')[:5]

    return render(request, 'shop/product_detail.html', {
        'product':          product,
        'similar_products': similar,
        'wishlist_ids':     _get_wishlist_ids(request),
        'current_cat':      product.category.slug,
    })


@require_POST
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    author_name = request.POST.get('author_name', '').strip()[:100]
    author_city = request.POST.get('author_city', '').strip()[:100]
    comment     = request.POST.get('comment', '').strip()[:1000]

    try:
        rating = int(request.POST.get('rating', ''))
        assert 1 <= rating <= 5
    except (ValueError, AssertionError):
        messages.error(request, 'Note invalide.')
        return redirect('shop:product_detail', slug=slug)

    if len(comment) < 10:
        messages.error(request, 'Votre avis doit contenir au moins 10 caractères.')
        return redirect('shop:product_detail', slug=slug)

    if request.user.is_authenticated:
        if ProductReview.objects.filter(product=product, user=request.user).exists():
            messages.info(request, 'Vous avez déjà laissé un avis pour ce produit.')
            return redirect('shop:product_detail', slug=slug)

    is_verified = False
    if request.user.is_authenticated:
        is_verified = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status='delivered',
        ).exists()

    import bleach
    ProductReview.objects.create(
        product=product,
        user=request.user if request.user.is_authenticated else None,
        author_name=bleach.clean(author_name, tags=[], strip=True),
        author_city=bleach.clean(author_city, tags=[], strip=True),
        comment=bleach.clean(comment, tags=[], strip=True),
        rating=rating,
        is_verified_purchase=is_verified,
        is_approved=False,
    )
    messages.success(request, 'Merci pour votre avis ! Il sera publié après modération.')
    return redirect('shop:product_detail', slug=slug)


# ------------------------------------------------------------------ #
#  PANIER (SESSION) — CORRIGÉ
# ------------------------------------------------------------------ #

def cart_view(request):
    items, subtotal = cart_items_with_products(request)
    return render(request, 'shop/cart.html', {
        'cart_items': items,
        'subtotal':   subtotal,
    })


@require_POST
def cart_add(request):
    """AJAX — Ajouter au panier (clé composite pour variantes)"""
    try:
        body       = json.loads(request.body)
        product_id = int(body.get('product_id', 0))
        quantity   = min(int(body.get('quantity', 1)), 20)
        size       = str(body.get('selected_size', ''))[:50]
        embroidery = str(body.get('embroidery_name', ''))[:20]
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Données invalides.'}, status=400)

    product = get_object_or_404(Product, id=product_id, is_active=True, is_available=True)

    cart = get_cart(request)
    key  = _make_cart_key(product_id, size, embroidery)

    if key in cart:
        cart[key]['qty'] = min(cart[key]['qty'] + quantity, 20)
    else:
        cart[key] = {
            'qty': quantity,
            'size': size,
            'embroidery_name': embroidery,
            'product_id': product_id,
        }

    save_cart(request, cart)

    return JsonResponse({
        'success': True,
        'cart_count': cart_count(request),
        'message': f'{product.name} ajouté au panier.',
    })


@require_POST
def cart_update(request):
    """AJAX — Mettre à jour la quantité (clé composite)"""
    try:
        body       = json.loads(request.body)
        cart_key   = str(body.get('cart_key', ''))
        quantity   = min(max(int(body.get('quantity', 1)), 1), 20)
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Données invalides.'}, status=400)

    cart = get_cart(request)
    if cart_key not in cart:
        return JsonResponse({'error': 'Article introuvable dans le panier.'}, status=404)

    cart[cart_key]['qty'] = quantity
    save_cart(request, cart)

    # Extraire product_id de la clé composite
    try:
        product_id = int(cart_key.split(':')[0])
    except (ValueError, IndexError):
        return JsonResponse({'error': 'Clé panier invalide.'}, status=400)

    product    = get_object_or_404(Product, id=product_id)
    line_total = product.price * quantity
    _, subtotal = cart_items_with_products(request)

    return JsonResponse({
        'success': True,
        'cart_count': cart_count(request),
        'line_total': float(line_total),
        'subtotal':   float(subtotal),
    })


@require_POST
def cart_remove(request):
    """AJAX — Supprimer un article (clé composite)"""
    try:
        body       = json.loads(request.body)
        cart_key   = str(body.get('cart_key', ''))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Données invalides.'}, status=400)

    cart = get_cart(request)
    if cart_key in cart:
        del cart[cart_key]
        save_cart(request, cart)

    _, subtotal = cart_items_with_products(request)

    return JsonResponse({
        'success': True,
        'cart_count': cart_count(request),
        'subtotal':   float(subtotal),
    })


def cart_count_view(request):
    """AJAX — Badge panier (GET autorisé)"""
    return JsonResponse({'cart_count': cart_count(request)})


# ------------------------------------------------------------------ #
#  CHECKOUT — CORRIGÉ
# ------------------------------------------------------------------ #

def checkout_view(request):
    items, subtotal = cart_items_with_products(request)
    if not items:
        messages.warning(request, 'Votre panier est vide.')
        return redirect('shop:cart')

    if request.method == 'POST':
        return _process_checkout(request, items, subtotal)

    communes = [
        'Cocody', 'Yopougon', 'Plateau', 'Marcory', 'Abobo',
        'Adjamé', 'Treichville', 'Koumassi', 'Bingerville',
        'Attécoubé', 'Port-Bouët', 'Songon',
    ]
    return render(request, 'shop/checkout.html', {
        'cart_items': items,
        'subtotal':   subtotal,
        'communes':   communes,
    })


def _process_checkout(request, items, subtotal):
    import re, bleach
    from django.db import transaction

    def clean(val, max_len=200):
        return bleach.clean(str(val or '').strip(), tags=[], strip=True)[:max_len]

    first_name   = clean(request.POST.get('customer_first_name'), 50)
    last_name    = clean(request.POST.get('customer_last_name'), 50)
    phone        = re.sub(r'[\s\-\.\(\)]', '', request.POST.get('customer_phone', ''))
    email        = request.POST.get('customer_email', '').strip().lower()[:254]
    city         = clean(request.POST.get('delivery_city'), 100)
    address      = clean(request.POST.get('delivery_address'), 500)
    instructions = clean(request.POST.get('delivery_instructions'), 300)
    payment_meth = request.POST.get('payment_method', 'cash')
    embroidery   = clean(request.POST.get('embroidery_name'), 20)
    pers_msg     = clean(request.POST.get('personal_message'), 200)
    promo_code   = request.POST.get('promo_code', '').upper().strip()[:30]

    if len(first_name) < 2:
        messages.error(request, 'Prénom invalide.')
        return redirect('shop:checkout')
    if not re.match(r'^\+?\d{8,15}$', phone):
        messages.error(request, 'Numéro de téléphone invalide.')
        return redirect('shop:checkout')
    if payment_meth not in ('orange_money', 'wave', 'cash'):
        payment_meth = 'cash'

    discount   = Decimal(0)
    promo_used = ''

    if promo_code:
        try:
            promo = PromoCode.objects.select_for_update().get(code=promo_code)
            if promo.is_valid(float(subtotal)):
                discount   = round(subtotal * promo.discount_percent / 100)
                promo_used = promo_code
                PromoCode.objects.filter(pk=promo.pk).update(current_uses=F('current_uses') + 1)
        except PromoCode.DoesNotExist:
            pass

    total = subtotal - discount

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_first_name=first_name,
            customer_last_name=last_name,
            customer_email=email,
            customer_phone=phone,
            delivery_address=address,
            delivery_city=city,
            delivery_instructions=instructions,
            payment_method=payment_meth,
            subtotal=subtotal,
            discount_amount=discount,
            total_amount=total,
            promo_code=promo_used,
        )
        for item in items:
            product = item['product']
            qty     = item['quantity']
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                unit_price=product.price,
                quantity=qty,
                selected_size=item.get('size', ''),
                embroidery_name=item.get('embroidery_name', ''),
            )
            if product.stock_quantity > 0:
                Product.objects.filter(pk=product.pk).update(
                    stock_quantity=F('stock_quantity') - qty,
                    sales_count=F('sales_count') + qty,
                )

    # CORRECTION : vider le panier SEULEMENT après création réussie
    save_cart(request, {})

    try:
        from apps.accounts.tasks import (
            send_order_confirmation_email,
            notify_admin_new_order_whatsapp,
        )
        send_order_confirmation_email.delay(str(order.id))
        notify_admin_new_order_whatsapp.delay(str(order.id))
    except Exception as e:
        logger.error(f'Notifications commande {order.reference}: {e}')

    logger.info(f'Commande créée: {order.reference} — {order.total_amount} F')
    return redirect('shop:success', reference=order.reference)


# ------------------------------------------------------------------ #
#  SUCCESS
# ------------------------------------------------------------------ #

def success_view(request, reference):
    order = get_object_or_404(Order, reference=reference)
    return render(request, 'shop/succes.html', {'order': order})


# ------------------------------------------------------------------ #
#  PROMOTIONS
# ------------------------------------------------------------------ #

def promotions(request):
    promo_products = Product.objects.filter(
        is_active=True, is_available=True, original_price__isnull=False
    ).select_related('category').order_by('-sales_count')

    return render(request, 'shop/promotions.html', {
        'promo_products': promo_products,
        'current_cat':    'promo',
        'wishlist_ids':   _get_wishlist_ids(request),
    })


# ------------------------------------------------------------------ #
#  WISHLIST
# ------------------------------------------------------------------ #

def wishlist_view(request):
    wishlist_ids      = _get_wishlist_ids(request)
    wishlist_products = Product.objects.filter(
        id__in=wishlist_ids, is_active=True
    ).select_related('category') if wishlist_ids else []

    return render(request, 'shop/wishlist.html', {
        'wishlist_products': wishlist_products,
        'wishlist_ids':      wishlist_ids,
    })


@require_POST
def wishlist_toggle(request):
    """AJAX — Toggle favori"""
    try:
        body       = json.loads(request.body)
        product_id = int(body.get('product_id', 0))
        action     = body.get('action', 'add')
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Données invalides.'}, status=400)

    wishlist = set(request.session.get('chicshop_wishlist', []))
    if action == 'add':
        wishlist.add(product_id)
    else:
        wishlist.discard(product_id)

    request.session['chicshop_wishlist'] = list(wishlist)
    request.session.modified = True
    return JsonResponse({'wishlist_count': len(wishlist)})


# ------------------------------------------------------------------ #
#  COMPTE
# ------------------------------------------------------------------ #

def account_view(request):
    active_tab = request.GET.get('tab', 'orders')
    orders     = []
    addresses  = []

    if request.user.is_authenticated:
        orders    = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')[:20]
        addresses = request.user.addresses.all()

    return render(request, 'shop/account.html', {
        'active_tab': active_tab,
        'orders':     orders,
        'addresses':  addresses,
    })


# ------------------------------------------------------------------ #
#  HELPERS PRIVÉS
# ------------------------------------------------------------------ #

def _get_wishlist_ids(request):
    return list(request.session.get('chicshop_wishlist', []))


def _time_ago(dt):
    from django.utils import timezone
    diff = timezone.now() - dt
    days = diff.days
    if days == 0:
        return "Aujourd'hui"
    if days == 1:
        return "Hier"
    if days < 7:
        return f"Il y a {days} jours"
    if days < 30:
        return f"Il y a {days // 7} semaine(s)"
    return f"Il y a {days // 30} mois"