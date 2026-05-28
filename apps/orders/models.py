"""ChicShop — Orders app files"""
# Ce fichier est un placeholder — les modèles, vues, admin sont dans views.py (all-in-one)
# Dans un vrai projet de taille importante, séparer en models.py / serializers.py / views.py / admin.py

# models.py — importer depuis views.py pour l'admin
import uuid
import re
import bleach
from decimal import Decimal

from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings

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
    embroidery_name = models.CharField(max_length=20, blank=True)
    personal_message = models.CharField(max_length=200, blank=True)
    class Meta:
        verbose_name = "ligne de commande"

    def __str__(self):
        return f"{self.product_name} ×{self.quantity}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity