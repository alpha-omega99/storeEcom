"""
ChicShop — Views shop
Toutes les vues liées au front : accueil, catalogue, produit,
panier (session), checkout, commande, compte, favoris...
"""
import json
import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from apps.orders.views import Order, OrderItem
from apps.products.models import Category, Product, ProductReview, PromoCode
from apps.payments.views import Payment

logger = logging.getLogger('chicshop')

# ------------------------------------------------------------------ #
#  HELPERS PANIER SESSION                                             #
# ------------------------------------------------------------------ #

CART_SESSION_KEY = 'chicshop_cart'


def get_cart(request):
    """Retourne le panier depuis la session : {product_id: {qty, size, embroidery}}"""
    return request.session.get(CART_SESSION_KEY, {})


def save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def cart_count(request):
    """Nombre total d'articles dans le panier"""
    return sum(item['qty'] for item in get_cart(request).values())


def cart_items_with_products(request):
    """Liste enrichie : [{product, quantity, size, embroidery_name, line_total}]"""
    cart = get_cart(request)
    items = []
    if not cart:
        return items, Decimal(0)

    product_ids = [int(k) for k in cart.keys()]
    products = {p.id: p for p in Product.objects.filter(id__in=product_ids, is_active=True)}

    subtotal = Decimal(0)
    for pid_str, data in cart.items():
        product = products.get(int(pid_str))
        if not product:
            continue
        qty        = data.get('qty', 1)
        line_total = product.price * qty
        subtotal  += line_total
        items.append({
            'product':        product,
            'quantity':       qty,
            'size':           data.get('size', ''),
            'embroidery_name': data.get('embroidery_name', ''),
            'line_total':     line_total,
        })
    return items, subtotal


# ------------------------------------------------------------------ #
#  CONTEXT PROCESSOR (pour le template base.html)                    #
# ------------------------------------------------------------------ #

def base_context(request):
    """Contexte commun à toutes les pages"""
    return {
        'cart_count':     cart_count(request),
        'categories':     Category.objects.filter(is_active=True).order_by('order'),
        'whatsapp_number': '22507000000',  # À configurer dans settings
    }


# ------------------------------------------------------------------ #
#  PAGE ACCUEIL                                                       #
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

    # Avis pour la page d'accueil (ou données statiques si pas d'avis)
    testimonials = ProductReview.objects.filter(
        is_approved=True
    ).select_related('product').order_by('-created_at')[:6]

    # Données format attendu par le template
    testi_data = []
    colors = [
        ('#fce8f0', '#7a1a3a'), ('#e0f0ff', '#1a3a7a'), ('#e8f5e9', '#1a6b3a'),
        ('#fff8e0', '#7a5000'), ('#f5e8ff', '#4a1a7a'), ('#e8f0ff', '#1a3a6a'),
    ]
    for i, r in enumerate(testimonials):
        bg, fg = colors[i % len(colors)]
        testi_data.append({
            'name':       r.author_name,
            'city':       r.author_city or 'Abidjan',
            'initial':    r.author_name[0].upper() if r.author_name else 'A',
            'avatar_bg':  bg,
            'avatar_color': fg,
            'rating':     r.rating,
            'comment':    r.comment,
            'time_ago':   _time_ago(r.created_at),
        })

    context = {
        **base_context(request),
        'featured_products': featured_products,
        'flash_products':    flash_products,
        'categories':        categories,
        'testimonials':      testi_data,
        'today_sales':       14,  # Peut être dynamisé depuis la DB
        'current_cat':       None,
    }
    return render(request, 'shop/home.html', context)


# ------------------------------------------------------------------ #
#  CATALOGUE                                                          #
# ------------------------------------------------------------------ #

def catalog(request, category_slug=None):
    qs = Product.objects.filter(
        is_active=True
    ).select_related('category').prefetch_related('reviews')

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        qs = qs.filter(category=current_category)

    # Filtres GET
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

    # Tri
    order = request.GET.get('order', '-sales_count')
    allowed_orders = ['price', '-price', '-sales_count', '-created_at']
    if order not in allowed_orders:
        order = '-sales_count'
    qs = qs.order_by(order)

    # Pagination
    paginator = Paginator(qs, 20)
    page_obj  = paginator.get_page(request.GET.get('page'))

    context = {
        **base_context(request),
        'products':         page_obj,
        'current_category': current_category,
        'current_cat':      category_slug,
        'max_price':        max_price or 50000,
        'search_query':     '',
        'wishlist_ids':     _get_wishlist_ids(request),
    }
    return render(request, 'shop/catalog.html', context)


def search(request):
    q   = request.GET.get('q', '').strip()
    qs  = Product.objects.none()

    if q and len(q) >= 2:
        qs = Product.objects.filter(
            is_active=True
        ).filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(color__icontains=q) |
            Q(category__name__icontains=q)
        ).select_related('category').distinct()

    context = {
        **base_context(request),
        'products':      qs,
        'search_query':  q,
        'current_cat':   None,
        'wishlist_ids':  _get_wishlist_ids(request),
    }
    return render(request, 'shop/search.html', context)


# ------------------------------------------------------------------ #
#  DÉTAIL PRODUIT                                                     #
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

    # 5 derniers avis approuvés
    recent_reviews = product.reviews.filter(is_approved=True).order_by('-created_at')[:5]

    context = {
        **base_context(request),
        'product':          product,
        'similar_products': similar,
        'wishlist_ids':     _get_wishlist_ids(request),
        'current_cat':      product.category.slug,
    }
    # Attacher les avis directement au produit pour le template
    product.recent_reviews = recent_reviews
    return render(request, 'shop/product_detail.html', context)


@require_POST
@csrf_protect
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    author_name = request.POST.get('author_name', '').strip()[:100]
    author_city = request.POST.get('author_city', '').strip()[:100]
    comment     = request.POST.get('comment', '').strip()[:1000]
    rating_str  = request.POST.get('rating', '')

    try:
        rating = int(rating_str)
        assert 1 <= rating <= 5
    except (ValueError, AssertionError):
        messages.error(request, 'Note invalide.')
        return redirect('shop:product_detail', slug=slug)

    if len(comment) < 10:
        messages.error(request, 'Votre avis doit contenir au moins 10 caractères.')
        return redirect('shop:product_detail', slug=slug)

    # Anti-doublons pour utilisateurs connectés
    if request.user.is_authenticated:
        if ProductReview.objects.filter(product=product, user=request.user).exists():
            messages.info(request, 'Vous avez déjà laissé un avis pour ce produit.')
            return redirect('shop:product_detail', slug=slug)

    # Vérifier achat vérifié
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
        is_approved=False,  # Modération obligatoire
    )
    messages.success(request, 'Merci pour votre avis ! Il sera publié après modération.')
    return redirect('shop:product_detail', slug=slug)


# ------------------------------------------------------------------ #
#  PANIER (SESSION)                                                   #
# ------------------------------------------------------------------ #

def cart_view(request):
    items, subtotal = cart_items_with_products(request)
    context = {
        **base_context(request),
        'cart_items': items,
        'subtotal':   subtotal,
    }
    return render(request, 'shop/cart.html', context)


@require_POST
def cart_add(request):
    """AJAX : Ajouter un produit au panier"""
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
    key  = str(product_id)
    if key in cart:
        cart[key]['qty'] = min(cart[key]['qty'] + quantity, 20)
    else:
        cart[key] = {'qty': quantity, 'size': size, 'embroidery_name': embroidery}

    save_cart(request, cart)

    return JsonResponse({
        'cart_count': cart_count(request),
        'message':    f'{product.name} ajouté au panier.',
    })


@require_POST
def cart_update(request):
    """AJAX : Mettre à jour la quantité"""
    try:
        body       = json.loads(request.body)
        product_id = int(body.get('product_id', 0))
        quantity   = min(max(int(body.get('quantity', 1)), 1), 20)
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Données invalides.'}, status=400)

    cart = get_cart(request)
    key  = str(product_id)
    if key not in cart:
        return JsonResponse({'error': 'Article introuvable dans le panier.'}, status=404)

    cart[key]['qty'] = quantity
    save_cart(request, cart)

    product    = get_object_or_404(Product, id=product_id)
    line_total = product.price * quantity
    _, subtotal = cart_items_with_products(request)

    return JsonResponse({
        'cart_count': cart_count(request),
        'line_total': float(line_total),
        'subtotal':   float(subtotal),
    })


@require_POST
def cart_remove(request):
    """AJAX : Supprimer un article du panier"""
    try:
        body       = json.loads(request.body)
        product_id = str(int(body.get('product_id', 0)))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Données invalides.'}, status=400)

    cart = get_cart(request)
    cart.pop(product_id, None)
    save_cart(request, cart)

    _, subtotal = cart_items_with_products(request)

    return JsonResponse({
        'cart_count': cart_count(request),
        'subtotal':   float(subtotal),
    })


def cart_count_view(request):
    """AJAX : Nombre d'articles (pour le badge JS)"""
    return JsonResponse({'cart_count': cart_count(request)})


# ------------------------------------------------------------------ #
#  CHECKOUT                                                           #
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
    context = {
        **base_context(request),
        'cart_items': items,
        'subtotal':   subtotal,
        'communes':   communes,
    }
    return render(request, 'shop/checkout.html', context)


def _process_checkout(request, items, subtotal):
    """Traiter la soumission du formulaire de commande"""
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

    # Validation basique
    if len(first_name) < 2:
        messages.error(request, 'Prénom invalide.')
        return redirect('shop:checkout')
    if not re.match(r'^\+?\d{8,15}$', phone):
        messages.error(request, 'Numéro de téléphone invalide.')
        return redirect('shop:checkout')
    if payment_meth not in ('orange_money', 'wave', 'cash'):
        payment_meth = 'cash'

    # Recalcul CÔTÉ SERVEUR
    from django.db.models import F
    discount = Decimal(0)
    promo_used = ''

    if promo_code:
        try:
            promo = PromoCode.objects.select_for_update().get(code=promo_code)
            if promo.is_valid(float(subtotal)):
                discount = round(subtotal * promo.discount_percent / 100)
                promo_used = promo_code
                PromoCode.objects.filter(pk=promo.pk).update(
                    current_uses=F('current_uses') + 1
                )
        except PromoCode.DoesNotExist:
            pass

    total = subtotal - discount

    with transaction.atomic():
        from apps.orders.views import generate_order_reference
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_first_name=first_name,
            customer_last_name=last_name,
            customer_email=email,
            customer_phone=phone,
            delivery_address=address,
            delivery_city=city,
            delivery_instructions=instructions,
            embroidery_name=embroidery,
            personal_message=pers_msg,
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
            )
            if product.stock_quantity > 0:
                Product.objects.filter(pk=product.pk).update(
                    stock_quantity=F('stock_quantity') - qty,
                    sales_count=F('sales_count') + qty,
                )

    # Vider le panier
    save_cart(request, {})

    # Notifications asynchrones
    try:
        from apps.accounts.tasks import (
            send_order_confirmation_email,
            notify_admin_new_order_whatsapp,
        )
        send_order_confirmation_email.delay(str(order.id))
        notify_admin_new_order_whatsapp.delay(str(order.id))
    except Exception as e:
        logger.error(f'Erreur envoi notifications commande {order.reference}: {e}')

    logger.info(f'Commande créée: {order.reference} — {order.total_amount} F')
    return redirect('shop:success', reference=order.reference)


# ------------------------------------------------------------------ #
#  SUCCESS                                                            #
# ------------------------------------------------------------------ #

def success_view(request, reference):
    order = get_object_or_404(Order, reference=reference)
    # Sécurité : vérifier que l'ordre appartient à l'utilisateur ou à la session
    context = {
        **base_context(request),
        'order': order,
    }
    return render(request, 'shop/success.html', context)


# ------------------------------------------------------------------ #
#  PROMOTIONS                                                         #
# ------------------------------------------------------------------ #

def promotions(request):
    promo_products = Product.objects.filter(
        is_active=True, is_available=True,
        original_price__isnull=False
    ).select_related('category').order_by('-sales_count')

    context = {
        **base_context(request),
        'promo_products': promo_products,
        'current_cat':    'promo',
        'wishlist_ids':   _get_wishlist_ids(request),
    }
    return render(request, 'shop/promotions.html', context)


# ------------------------------------------------------------------ #
#  WISHLIST (localStorage côté client + session serveur)             #
# ------------------------------------------------------------------ #

def wishlist_view(request):
    wishlist_ids = _get_wishlist_ids(request)
    wishlist_products = Product.objects.filter(
        id__in=wishlist_ids, is_active=True
    ).select_related('category') if wishlist_ids else []

    context = {
        **base_context(request),
        'wishlist_products': wishlist_products,
        'wishlist_ids':      wishlist_ids,
    }
    return render(request, 'shop/wishlist.html', context)


@require_POST
def wishlist_toggle(request):
    """AJAX : Toggle favori"""
    try:
        body       = json.loads(request.body)
        product_id = int(body.get('product_id', 0))
        action     = body.get('action', 'add')  # 'add' | 'remove'
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
#  COMPTE                                                             #
# ------------------------------------------------------------------ #

def account_view(request):
    active_tab = request.GET.get('tab', 'orders')
    orders     = []
    addresses  = []

    if request.user.is_authenticated:
        orders    = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')[:20]
        addresses = request.user.addresses.all()

    context = {
        **base_context(request),
        'active_tab': active_tab,
        'orders':     orders,
        'addresses':  addresses,
    }
    return render(request, 'shop/account.html', context)


# ------------------------------------------------------------------ #
#  HELPERS PRIVÉS                                                     #
# ------------------------------------------------------------------ #

def _get_wishlist_ids(request):
    """IDs favoris depuis la session"""
    return list(request.session.get('chicshop_wishlist', []))


def _time_ago(dt):
    """Formater une date relative simple"""
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
