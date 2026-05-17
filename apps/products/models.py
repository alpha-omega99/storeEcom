"""
ChicShop — Modèles Produits
Catalogue complet : produits, catégories, avis, codes promo
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, blank=True, help_text="Emoji ou classe icône")
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'catégorie'
        verbose_name_plural = 'catégories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Produit ChicShop — tapis, chapelet, pack, etc."""

    class Badge(models.TextChoices):
        NEW = 'NEW', 'Nouveau'
        HOT = 'HOT', 'Populaire'
        PROMO = 'PROMO', 'Promotion'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='products'
    )
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)

    # Tarification
    price = models.DecimalField(
        max_digits=10, decimal_places=0,
        validators=[MinValueValidator(1)],
        help_text="Prix en F CFA"
    )
    original_price = models.DecimalField(
        max_digits=10, decimal_places=0,
        null=True, blank=True,
        validators=[MinValueValidator(1)],
        help_text="Prix barré (avant promotion)"
    )

    # Stock
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    # Personnalisation broderie
    allows_embroidery = models.BooleanField(default=True)
    max_embroidery_chars = models.PositiveSmallIntegerField(default=20)

    # Présentation
    badge = models.CharField(max_length=10, choices=Badge.choices, blank=True)
    emoji = models.CharField(max_length=10, blank=True)
    color = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    # Inclusions (liste d'articles dans le pack)
    included_items = models.JSONField(
        default=list, blank=True,
        help_text="Liste des articles inclus dans le pack"
    )

    # Tailles disponibles
    available_sizes = models.JSONField(
        default=list, blank=True,
        help_text="Ex: ['60×90 cm', '70×110 cm']"
    )

    # SEO & Stats
    views_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'produit'
        verbose_name_plural = 'produits'
        ordering = ['-is_featured', '-sales_count', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'is_available']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['-sales_count']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return round((1 - self.price / self.original_price) * 100)
        return None

    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(
                avg=models.Avg('rating')
            )['avg'], 1)
        return None

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

    def increment_views(self):
        """Incrémenter le compteur de vues de façon atomique"""
        Product.objects.filter(pk=self.pk).update(
            views_count=models.F('views_count') + 1
        )


class ProductReview(models.Model):
    """Avis clients — modérés avant publication"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True
    )
    # Infos client (si non connecté)
    author_name = models.CharField(max_length=100)
    author_city = models.CharField(max_length=100, blank=True)

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=1000)
    is_approved = models.BooleanField(default=False)  # Modération obligatoire
    is_verified_purchase = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'avis client'
        verbose_name_plural = 'avis clients'
        ordering = ['-created_at']
        # Un utilisateur connecté ne peut laisser qu'un avis par produit
        unique_together = [['product', 'user']]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name='rating_range'
            )
        ]
    
    def __str__(self):
        return f"{self.author_name} — {self.product.name} ({self.rating}★)"


class PromoCode(models.Model):
    """Codes promotionnels — avec validation stricte"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=30, unique=True, db_index=True)
    discount_percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(80)]
    )
    max_uses = models.PositiveIntegerField(default=100)
    current_uses = models.PositiveIntegerField(default=0)
    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=0, default=0
    )
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'code promo'
        verbose_name_plural = 'codes promo'

    def __str__(self):
        return f"{self.code} — -{self.discount_percent}%"

    def is_valid(self, order_amount=0):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active
            and self.current_uses < self.max_uses
            and self.valid_from <= now <= self.valid_until
            and order_amount >= float(self.min_order_amount)
        )
