"""
ChicShop — Context Processors
Injecte automatiquement dans tous les templates :
- cart_count
- categories
- whatsapp_number

Ajouter dans settings/base.py > TEMPLATES > OPTIONS > context_processors :
    'apps.shop.context_processors.shop_context',
"""
from django.conf import settings
from apps.products.models import Category


def shop_context(request):
    """Contexte global disponible dans tous les templates"""

    # Nombre d'articles dans le panier (session)
    cart = request.session.get('chicshop_cart', {})
    cart_count = sum(item.get('qty', 1) for item in cart.values())

    # Catégories pour la nav (mise en cache possible)
    try:
        categories = list(Category.objects.filter(is_active=True).order_by('order'))
    except Exception:
        categories = []

    return {
        'cart_count':      cart_count,
        'categories':      categories,
        'whatsapp_number': getattr(settings, 'WHATSAPP_ADMIN_NUMBER', '2250103976779').replace('+', '').replace(' ', ''),
        'current_year':    __import__('datetime').date.today().year,
    }
