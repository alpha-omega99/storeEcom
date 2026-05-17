"""
ChicShop — App Orders
Commandes : modèles, serializers, vues, URLs, admin
"""
import uuid
import re
import bleach
from decimal import Decimal

from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings

from rest_framework import serializers, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.urls import path


# ============================================================
# MODELS
# ============================================================

def generate_order_reference():
    """Générer une référence de commande unique non prévisible"""
    import secrets, string
    prefix = settings.CHICSHOP.get('ORDER_REF_PREFIX', 'CS')
    suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    return f"{prefix}-{suffix}"


class Order(models.Model):
    """Commande ChicShop"""

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        CONFIRMED = 'confirmed', 'Confirmée'
        IN_EMBROIDERY = 'in_embroidery', 'En personnalisation'
        PACKAGING = 'packaging', 'En emballage'
        SHIPPED = 'shipped', 'Expédiée'
        DELIVERED = 'delivered', 'Livrée'
        CANCELLED = 'cancelled', 'Annulée'
        REFUNDED = 'refunded', 'Remboursée'

    class PaymentMethod(models.TextChoices):
        ORANGE_MONEY = 'orange_money', 'Orange Money'
        WAVE = 'wave', 'Wave'
        CASH = 'cash', 'Cash à la livraison'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(
        max_length=20, unique=True, db_index=True,
        default=generate_order_reference
    )

    # Utilisateur — nullable (commandes invités)
    user = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders'
    )

    # Informations client (copiées au moment de la commande — immuables)
    customer_first_name = models.CharField(max_length=50)
    customer_last_name = models.CharField(max_length=50)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)

    # Livraison
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=100)
    delivery_instructions = models.TextField(blank=True)

    # Personnalisation broderie
    embroidery_name = models.CharField(max_length=20, blank=True)
    personal_message = models.CharField(max_length=200, blank=True)

    # Tarification (snapshot au moment de la commande)
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)
    promo_code = models.CharField(max_length=30, blank=True)

    # Paiement
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'En attente'), ('paid', 'Payée'), ('failed', 'Échec'), ('refunded', 'Remboursée')],
        default='pending'
    )

    # Statut
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    # Notes internes (admin seulement — jamais exposées à l'utilisateur)
    admin_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'commande'
        verbose_name_plural = 'commandes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['customer_email']),
            models.Index(fields=['reference']),
        ]

    def __str__(self):
        return f"#{self.reference} — {self.customer_first_name} {self.customer_last_name}"

    def update_status(self, new_status):
        """Changer le statut et déclencher les actions associées"""
        self.status = new_status
        if new_status == 'confirmed':
            self.confirmed_at = timezone.now()
        elif new_status == 'delivered':
            self.delivered_at = timezone.now()
        self.save()
        # Notifier le client (asynchrone)
        from apps.accounts.tasks import send_order_status_update
        send_order_status_update.delay(str(self.id), new_status)


class OrderItem(models.Model):
    """Ligne de commande — snapshot produit au moment de la commande"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'products.Product', on_delete=models.PROTECT, related_name='order_items'
    )
    # Snapshot pour historique (même si le produit est modifié plus tard)
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    selected_size = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "ligne de commande"

    def __str__(self):
        return f"{self.product_name} ×{self.quantity}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity


# ============================================================
# SERIALIZERS
# ============================================================

def sanitize(value, max_length=None):
    cleaned = bleach.clean(str(value or ''), tags=[], strip=True).strip()
    return cleaned[:max_length] if max_length else cleaned


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, max_value=20)
    selected_size = serializers.CharField(max_length=50, required=False, default='')


class OrderCreateSerializer(serializers.Serializer):
    """Création de commande — validation complète côté serveur"""
    # Infos client
    customer_first_name = serializers.CharField(max_length=50)
    customer_last_name = serializers.CharField(max_length=50)
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=20)

    # Livraison
    delivery_address = serializers.CharField(max_length=500)
    delivery_city = serializers.CharField(max_length=100)
    delivery_instructions = serializers.CharField(max_length=300, required=False, default='')

    # Personnalisation
    embroidery_name = serializers.CharField(max_length=20, required=False, default='', allow_blank=True)
    personal_message = serializers.CharField(max_length=200, required=False, default='', allow_blank=True)

    # Paiement
    payment_method = serializers.ChoiceField(choices=['orange_money', 'wave', 'cash'])

    # Panier
    items = serializers.ListField(
        child=OrderItemCreateSerializer(),
        min_length=1, max_length=20
    )

    # Code promo
    promo_code = serializers.CharField(max_length=30, required=False, default='', allow_blank=True)

    def validate_customer_first_name(self, v):
        v = sanitize(v, 50)
        if len(v) < 2:
            raise serializers.ValidationError("Prénom trop court.")
        if not re.match(r"^[\w\sÀ-ÿ\-']+$", v):
            raise serializers.ValidationError("Prénom invalide.")
        return v

    def validate_customer_last_name(self, v):
        v = sanitize(v, 50)
        if len(v) < 2:
            raise serializers.ValidationError("Nom trop court.")
        return v

    def validate_customer_email(self, v):
        return v.lower().strip()

    def validate_customer_phone(self, v):
        cleaned = re.sub(r'[\s\-\.\(\)]', '', v)
        if not re.match(r'^\+?[\d]{8,15}$', cleaned):
            raise serializers.ValidationError("Numéro de téléphone invalide.")
        return cleaned

    def validate_embroidery_name(self, v):
        v = sanitize(v, 20)
        if v and not re.match(r"^[\w\sÀ-ÿ\-']+$", v):
            raise serializers.ValidationError(
                "Le prénom brodé ne peut contenir que des lettres."
            )
        return v

    def validate_personal_message(self, v):
        return sanitize(v, 200)

    def validate_delivery_address(self, v):
        return sanitize(v, 500)

    def validate_delivery_city(self, v):
        return sanitize(v, 100)

    def validate_delivery_instructions(self, v):
        return sanitize(v, 300)

    def validate_promo_code(self, v):
        return v.upper().strip()


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'unit_price', 'quantity',
                  'selected_size', 'line_total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(
        source='get_payment_method_display', read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'reference', 'status', 'status_display',
            'customer_first_name', 'customer_last_name', 'customer_email', 'customer_phone',
            'delivery_address', 'delivery_city', 'delivery_instructions',
            'embroidery_name', 'personal_message',
            'subtotal', 'discount_amount', 'total_amount', 'promo_code',
            'payment_method', 'payment_method_display', 'payment_status',
            'items', 'created_at', 'confirmed_at', 'delivered_at',
        ]
        # Ne jamais exposer les notes admin à l'utilisateur
        read_only_fields = fields


# ============================================================
# VIEWS
# ============================================================

class OrderCreateRateThrottle(AnonRateThrottle):
    scope = 'order'


class OrderCreateView(generics.GenericAPIView):
    """
    Créer une commande.
    - Authentification optionnelle (commandes invités)
    - Recalcul des prix côté serveur (jamais faire confiance au client)
    - Transaction atomique
    """
    serializer_class = OrderCreateSerializer
    permission_classes = [AllowAny]
    throttle_classes = [OrderCreateRateThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        from apps.products.models import Product, PromoCode
        import logging
        logger = logging.getLogger('chicshop')

        with transaction.atomic():
            # ---- 1. Recalculer les prix côté serveur ----
            items_data = data['items']
            subtotal = Decimal(0)
            order_items_to_create = []

            max_cart = settings.CHICSHOP.get('MAX_CART_ITEMS', 20)
            if len(items_data) > max_cart:
                return Response(
                    {'detail': f"Maximum {max_cart} articles par commande."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for item_data in items_data:
                try:
                    product = Product.objects.select_for_update().get(
                        id=item_data['product_id'],
                        is_active=True,
                        is_available=True
                    )
                except Product.DoesNotExist:
                    return Response(
                        {'detail': f"Produit introuvable ou indisponible."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Vérifier le stock
                qty = item_data['quantity']
                if product.stock_quantity > 0 and product.stock_quantity < qty:
                    return Response(
                        {'detail': f"Stock insuffisant pour '{product.name}' (disponible: {product.stock_quantity})."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                line_total = product.price * qty
                subtotal += line_total
                order_items_to_create.append({
                    'product': product,
                    'product_name': product.name,
                    'unit_price': product.price,
                    'quantity': qty,
                    'selected_size': item_data.get('selected_size', ''),
                })

            # ---- 2. Valider le montant minimum ----
            min_amount = settings.CHICSHOP.get('MIN_ORDER_AMOUNT', 1000)
            if subtotal < min_amount:
                return Response(
                    {'detail': f"Montant minimum de commande : {min_amount:,.0f} F CFA."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ---- 3. Appliquer le code promo (si fourni) ----
            discount = Decimal(0)
            promo_code_str = data.get('promo_code', '')
            if promo_code_str:
                try:
                    promo = PromoCode.objects.select_for_update().get(code=promo_code_str)
                    if promo.is_valid(float(subtotal)):
                        discount = round(subtotal * promo.discount_percent / 100)
                        # Incrémenter l'utilisation du code
                        PromoCode.objects.filter(pk=promo.pk).update(
                            current_uses=models.F('current_uses') + 1
                        )
                    else:
                        promo_code_str = ''  # Code invalide, ignorer
                except PromoCode.DoesNotExist:
                    promo_code_str = ''

            total = subtotal - discount

            # ---- 4. Créer la commande ----
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_first_name=data['customer_first_name'],
                customer_last_name=data['customer_last_name'],
                customer_email=data['customer_email'],
                customer_phone=data['customer_phone'],
                delivery_address=data['delivery_address'],
                delivery_city=data['delivery_city'],
                delivery_instructions=data.get('delivery_instructions', ''),
                embroidery_name=data.get('embroidery_name', ''),
                personal_message=data.get('personal_message', ''),
                payment_method=data['payment_method'],
                subtotal=subtotal,
                discount_amount=discount,
                total_amount=total,
                promo_code=promo_code_str,
            )

            # ---- 5. Créer les lignes de commande ----
            OrderItem.objects.bulk_create([
                OrderItem(order=order, **item)
                for item in order_items_to_create
            ])

            # ---- 6. Décrémenter le stock ----
            for item in order_items_to_create:
                if item['product'].stock_quantity > 0:
                    Product.objects.filter(pk=item['product'].pk).update(
                        stock_quantity=models.F('stock_quantity') - item['quantity'],
                        sales_count=models.F('sales_count') + item['quantity'],
                    )

        # Notifications asynchrones (hors transaction)
        from apps.accounts.tasks import (
            send_order_confirmation_email,
            notify_admin_new_order_whatsapp
        )
        send_order_confirmation_email.delay(str(order.id))
        notify_admin_new_order_whatsapp.delay(str(order.id))

        logger.info(
            f"Nouvelle commande — ref={order.reference} "
            f"total={order.total_amount} méthode={order.payment_method}"
        )

        return Response(
            {
                "message": "Commande passée avec succès 🌸 Aminata vous contactera dans 5 minutes !",
                "order": OrderSerializer(order).data,
            },
            status=status.HTTP_201_CREATED
        )


class OrderDetailView(generics.RetrieveAPIView):
    """Détail d'une commande par référence — accès par email de commande ou user connecté"""
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        reference = self.kwargs.get('reference')
        # IDOR protection stricte
        try:
            order = Order.objects.prefetch_related('items__product').get(reference=reference)
        except Order.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Commande introuvable.")

        # Vérifier l'autorisation
        user = self.request.user
        if user.is_authenticated:
            if order.user == user or user.is_staff:
                return order
        # Pour les invités : vérifier via email (passé en query param)
        email = self.request.query_params.get('email', '').lower().strip()
        if email and order.customer_email == email:
            return order

        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("Vous n'avez pas accès à cette commande.")


class MyOrdersView(generics.ListAPIView):
    """Historique commandes de l'utilisateur connecté"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items').order_by('-created_at')


# ============================================================
# URLS
# ============================================================
app_name = 'orders'

urlpatterns = [
    path('', OrderCreateView.as_view(), name='create'),
    path('my-orders/', MyOrdersView.as_view(), name='my_orders'),
    path('<str:reference>/', OrderDetailView.as_view(), name='detail'),
]


# ============================================================
# ADMIN
# ============================================================
from django.contrib import admin


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product', 'product_name', 'unit_price', 'quantity',
                       'selected_size', 'line_total']
    extra = 0
    can_delete = False

    def line_total(self, obj):
        return f"{obj.line_total:,.0f} F CFA"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['reference', 'customer_first_name', 'customer_last_name',
                    'customer_phone', 'delivery_city', 'status', 'payment_method',
                    'total_amount', 'created_at']
    list_filter = ['status', 'payment_method', 'payment_status', 'delivery_city', 'created_at']
    search_fields = ['reference', 'customer_first_name', 'customer_last_name',
                     'customer_email', 'customer_phone', 'embroidery_name']
    readonly_fields = ['id', 'reference', 'user', 'subtotal', 'discount_amount',
                       'total_amount', 'created_at', 'updated_at', 'confirmed_at', 'delivered_at']
    inlines = [OrderItemInline]
    list_editable = ['status']
    ordering = ['-created_at']

    fieldsets = (
        ('Référence', {'fields': ('id', 'reference', 'user', 'status')}),
        ('Client', {'fields': ('customer_first_name', 'customer_last_name',
                                'customer_email', 'customer_phone')}),
        ('Livraison', {'fields': ('delivery_address', 'delivery_city', 'delivery_instructions')}),
        ('Personnalisation', {'fields': ('embroidery_name', 'personal_message')}),
        ('Paiement', {'fields': ('payment_method', 'payment_status', 'subtotal',
                                  'discount_amount', 'promo_code', 'total_amount')}),
        ('Notes admin', {'fields': ('admin_notes',)}),
        ('Dates', {'fields': ('created_at', 'updated_at', 'confirmed_at', 'delivered_at')}),
    )

    actions = ['mark_confirmed', 'mark_in_embroidery', 'mark_shipped', 'mark_delivered']

    def mark_confirmed(self, request, queryset):
        for order in queryset:
            order.update_status('confirmed')
        self.message_user(request, f"{queryset.count()} commande(s) confirmée(s).")
    mark_confirmed.short_description = "✅ Confirmer les commandes"

    def mark_in_embroidery(self, request, queryset):
        for order in queryset:
            order.update_status('in_embroidery')
        self.message_user(request, f"{queryset.count()} commande(s) en personnalisation.")
    mark_in_embroidery.short_description = "🎨 Mettre en personnalisation"

    def mark_shipped(self, request, queryset):
        for order in queryset:
            order.update_status('shipped')
        self.message_user(request, f"{queryset.count()} commande(s) expédiée(s).")
    mark_shipped.short_description = "🚚 Marquer comme expédiée"

    def mark_delivered(self, request, queryset):
        for order in queryset:
            order.update_status('delivered')
        self.message_user(request, f"{queryset.count()} commande(s) livrée(s).")
    mark_delivered.short_description = "📦 Marquer comme livrée"
