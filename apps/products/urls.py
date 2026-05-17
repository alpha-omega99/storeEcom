"""ChicShop — URLs Products"""
from django.urls import path
from .views import (
    ProductListView, ProductDetailView, CategoryListView,
    ProductReviewCreateView, validate_promo_code,
)

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('promo/validate/', validate_promo_code, name='validate_promo'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('<slug:slug>/reviews/', ProductReviewCreateView.as_view(), name='product_reviews'),
]
