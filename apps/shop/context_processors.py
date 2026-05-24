"""
ChicShop — Context Processors
Injecte automatiquement dans tous les templates :
- cart_count
- categories
- whatsapp_number
"""
from django.conf import settings
from django.db import connection
from apps.products.models import Category


def shop_context(request):
    """Contexte global disponible dans tous les templates"""

    # 1. Nombre d'articles dans le panier (session)
    cart = request.session.get('chicshop_cart', {})
    cart_count = 0
    if isinstance(cart, dict):
        cart_count = sum(item.get('qty', 1) for item in cart.values() if isinstance(item, dict))

    # 2. Catégories sécurisées contre la récursion
    categories = []
    
    # On vérifie d'abord que la table existe dans MySQL avant de faire le filter()
    # Cela évite de faire crasher le processeur pendant les migrations ou un bug DB
    if "products_category" in connection.introspection.table_names():
        try:
            categories = list(Category.objects.filter(is_active=True).order_by('order'))
        except Exception:
            categories = []

    # 3. Récupération du numéro WhatsApp
    whatsapp = getattr(settings, 'WHATSAPP_ADMIN_NUMBER', '2250103976779')
    whatsapp_cleaned = str(whatsapp).replace('+', '').replace(' ', '')

    return {
        'cart_count':      cart_count,
        'categories':      categories,
        'whatsapp_number': whatsapp_cleaned,
        'current_year':    2026,  # Fixé directement sur l'année en cours
    }