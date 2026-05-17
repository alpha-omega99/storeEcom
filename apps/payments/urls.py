"""ChicShop — URLs Payments"""
from django.urls import path
from .views import initiate_payment, WebhookView

app_name = 'payments'

urlpatterns = [
    path('initiate/', initiate_payment, name='initiate'),
    path('webhook/<str:provider>/', WebhookView.as_view(), name='webhook'),
]
