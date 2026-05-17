"""
ChicShop — URL Root
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Personnaliser l'interface admin Django (masquer des infos système)
admin.site.site_header = "ChicShop Administration"
admin.site.site_title = "ChicShop Admin"
admin.site.index_title = "Panneau de contrôle"

urlpatterns = [
    # Admin Django — URL non-standard pour éviter le scan automatique
    path('chicshop-admin/', admin.site.urls),
    path('', include('apps.shop.urls', namespace='shop')),
    path('auth/', include('apps.accounts.urls', namespace='accounts')),
    path('products/', include('apps.products.urls', namespace='products')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    

    # Documentation API (désactiver en prod si besoin)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Fichiers media en développement uniquement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
