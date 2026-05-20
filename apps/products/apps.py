# apps/products/apps.py
from django.apps import AppConfig

class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'  # <--- Doit être strictement identique à ce qu'il y a dans INSTALLED_APPS