"""ChicShop — URLs Orders"""
from django.urls import path
from .views import OrderCreateView, OrderDetailView, MyOrdersView

app_name = 'orders'

urlpatterns = [
    path('', OrderCreateView.as_view(), name='create'),
    path('my-orders/', MyOrdersView.as_view(), name='my_orders'),
    path('<str:reference>/', OrderDetailView.as_view(), name='detail'),
]
