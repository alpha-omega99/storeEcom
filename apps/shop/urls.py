"""
ChicShop — URLs du shop (frontend)
À inclure dans config/urls.py :

    path('', include('apps.shop.urls', namespace='shop')),
"""
from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [

    # ===== PAGES PRINCIPALES =====
    path('',                    views.home,           name='home'),
    path('promotions/',         views.promotions,     name='promotions'),
    path('recherche/',          views.search,         name='search'),

    # ===== CATALOGUE =====
    path('catalogue/',                          views.catalog, name='catalog'),
    path('catalogue/<slug:category_slug>/',    views.catalog, name='catalog_category'),

    # ===== PRODUIT =====
    path('produit/<slug:slug>/',               views.product_detail, name='product_detail'),
    path('produit/<slug:slug>/avis/',          views.add_review,     name='add_review'),

    # ===== PANIER =====
    path('panier/',            views.cart_view,       name='cart'),
    path('panier/count/',      views.cart_count_view, name='cart_count'),
    path('panier/ajouter/',    views.cart_add,        name='cart_add'),
    path('panier/modifier/',   views.cart_update,     name='cart_update'),
    path('panier/supprimer/',  views.cart_remove,     name='cart_remove'),

    # ===== COMMANDE =====
    path('commander/',                          views.checkout_view, name='checkout'),
    path('confirmation/<str:reference>/',       views.success_view,  name='success'),

    # ===== FAVORIS =====
    path('favoris/',           views.wishlist_view,   name='wishlist'),
    path('favoris/toggle/',    views.wishlist_toggle, name='wishlist_toggle'),

    # ===== COMPTE =====
    
    path('compte/',            views.account_view,    name='account'),
    # Exemple dans tes urls.py — l'URL doit pointer vers une vraie JsonResponse, sans redirection !
    path('panier/mini/', views.mini_cart_api, name='mini_cart_api'),
]