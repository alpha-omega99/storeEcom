"""
ChicShop — URL Root (CORRIGÉ)

CORRECTIONS :
- Admin URL renommée /chicshop-admin/ (sécurité — anti-scan)
- Routes API préfixées avec /api/v1/
- Routes shop sans préfixe (à la racine)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

admin.site.site_header = "ChicShop Administration"
admin.site.site_title  = "ChicShop Admin"
admin.site.index_title = "Panneau de contrôle"

urlpatterns = [
    # CORRECTION : URL admin non standard pour éviter les scans automatiques
    path('chicshop-admin/', admin.site.urls),

    # Frontend shop — à la racine
    path('', include('apps.shop.urls', namespace='shop')),

    # API REST — toutes préfixées /api/v1/
    path('api/v1/auth/',     include('apps.accounts.urls',  namespace='accounts')),
    path('api/v1/products/', include('apps.products.urls',  namespace='products')),
    path('api/v1/orders/',   include('apps.orders.urls',    namespace='orders')),
    path('api/v1/payments/', include('apps.payments.urls',  namespace='payments')),

    # Documentation API
    path('api/schema/', SpectacularAPIView.as_view(),                          name='schema'),
    path('api/docs/',   SpectacularSwaggerView.as_view(url_name='schema'),     name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
