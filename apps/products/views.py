"""
ChicShop — Products : Serializers + Views + URLs + Admin
"""

# ===================== serializers.py =====================
# (contenu réparti en fichiers séparés dans le vrai projet)

from decimal import Decimal
import bleach
from rest_framework import serializers
from .models import Product, Category, ProductReview, PromoCode


def sanitize(value, max_length=None):
    cleaned = bleach.clean(str(value or ''), tags=[], strip=True).strip()
    return cleaned[:max_length] if max_length else cleaned


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description', 'product_count']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True, is_available=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Sérialiseur léger pour les listes (catalogue, grille)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    discount_percent = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_name', 'category_slug',
            'price', 'original_price', 'discount_percent',
            'badge', 'emoji', 'color', 'image',
            'average_rating', 'review_count', 'is_available',
            'allows_embroidery',
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur complet pour la page produit"""
    category = CategorySerializer(read_only=True)
    discount_percent = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    recent_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category',
            'description', 'short_description',
            'price', 'original_price', 'discount_percent',
            'stock_quantity', 'is_available',
            'allows_embroidery', 'max_embroidery_chars',
            'badge', 'emoji', 'color', 'image',
            'included_items', 'available_sizes',
            'average_rating', 'review_count', 'recent_reviews',
            'created_at',
        ]

    def get_recent_reviews(self, obj):
        reviews = obj.reviews.filter(is_approved=True).order_by('-created_at')[:5]
        return ProductReviewSerializer(reviews, many=True).data


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['id', 'author_name', 'author_city', 'rating', 'comment',
                  'is_verified_purchase', 'created_at']
        read_only_fields = ['id', 'is_verified_purchase', 'created_at']


class ProductReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment', 'author_name', 'author_city']

    def validate_comment(self, value):
        cleaned = sanitize(value, max_length=1000)
        if len(cleaned) < 10:
            raise serializers.ValidationError("Le commentaire doit faire au moins 10 caractères.")
        return cleaned

    def validate_author_name(self, value):
        return sanitize(value, max_length=100)

    def validate_author_city(self, value):
        return sanitize(value, max_length=100)


class PromoCodeValidateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=30)
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=0)

    def validate_code(self, value):
        return value.upper().strip()


# ===================== views.py =====================
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q


class ProductListView(generics.ListAPIView):
    """Catalogue produits — public, avec filtres, recherche et pagination"""
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category__slug', 'badge', 'is_available', 'allows_embroidery']
    search_fields = ['name', 'description', 'color', 'category__name']
    ordering_fields = ['price', 'sales_count', 'created_at', 'average_rating']
    ordering = ['-sales_count']

    def get_queryset(self):
        qs = Product.objects.filter(
            is_active=True
        ).select_related('category').prefetch_related('reviews')

        # Filtre par catégorie slug (URL param)
        cat = self.request.query_params.get('category')
        if cat and cat != 'all':
            qs = qs.filter(
                Q(category__slug=cat) | Q(category__name__icontains=cat)
            )

        # Filtre prix max
        max_price = self.request.query_params.get('max_price')
        if max_price:
            try:
                qs = qs.filter(price__lte=Decimal(max_price))
            except Exception:
                pass  # Ignorer les valeurs invalides silencieusement

        # Uniquement les promos
        promo_only = self.request.query_params.get('promo')
        if promo_only == 'true':
            qs = qs.filter(original_price__isnull=False, badge='PROMO')

        # Uniquement les nouveautés
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            qs = qs.filter(is_featured=True)

        return qs

    # Cache 5 minutes pour les listes (évite les requêtes répétées)
    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductDetailView(generics.RetrieveAPIView):
    """Détail produit — public"""
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True
        ).select_related('category').prefetch_related('reviews')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_views()  # Compteur atomique
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryListView(generics.ListAPIView):
    """Liste des catégories — public"""
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    queryset = Category.objects.filter(is_active=True).order_by('order')

    @method_decorator(cache_page(60 * 60))  # Cache 1 heure
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductReviewCreateView(generics.CreateAPIView):
    """Déposer un avis — limité par throttle"""
    serializer_class = ProductReviewCreateSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def get_product(self):
        slug = self.kwargs.get('slug')
        try:
            return Product.objects.get(slug=slug, is_active=True)
        except Product.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Produit introuvable.")

    def perform_create(self, serializer):
        product = self.get_product()
        user = self.request.user if self.request.user.is_authenticated else None

        # Vérifier si l'utilisateur connecté a déjà laissé un avis
        if user and ProductReview.objects.filter(product=product, user=user).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Vous avez déjà laissé un avis pour ce produit.")

        # Vérifier achat vérifié
        is_verified = False
        if user:
            from apps.orders.models import OrderItem
            is_verified = OrderItem.objects.filter(
                order__user=user,
                product=product,
                order__status__in=['delivered']
            ).exists()

        serializer.save(
            product=product,
            user=user,
            is_verified_purchase=is_verified,
            is_approved=False,  # Modération obligatoire
        )

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(
            {"message": "Merci pour votre avis ! Il sera publié après modération."},
            status=status.HTTP_201_CREATED
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_promo_code(request):
    """Valider un code promo — anti-bruteforce avec throttle"""
    serializer = PromoCodeValidateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    code_str = serializer.validated_data['code']
    order_amount = float(serializer.validated_data['order_amount'])

    try:
        promo = PromoCode.objects.get(code=code_str)
        if promo.is_valid(order_amount):
            discount_amount = round(order_amount * promo.discount_percent / 100)
            return Response({
                'valid': True,
                'code': promo.code,
                'discount_percent': promo.discount_percent,
                'discount_amount': discount_amount,
                'new_total': round(order_amount - discount_amount),
            })
        else:
            return Response(
                {'valid': False, 'detail': 'Code invalide, expiré ou conditions non remplies.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except PromoCode.DoesNotExist:
        # Délai pour éviter l'énumération des codes
        import time; time.sleep(0.05)
        return Response(
            {'valid': False, 'detail': 'Code promo introuvable.'},
            status=status.HTTP_400_BAD_REQUEST
        )


# ===================== urls.py =====================
from django.urls import path

app_name = 'products'

urlpatterns_products = [
    path('', ProductListView.as_view(), name='product_list'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('promo/validate/', validate_promo_code, name='validate_promo'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('<slug:slug>/reviews/', ProductReviewCreateView.as_view(), name='product_reviews'),
]


# ===================== admin.py =====================
from django.contrib import admin
from django.utils import timezone


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'original_price', 'stock_quantity',
                    'is_available', 'is_featured', 'sales_count', 'views_count']
    list_filter = ['category', 'is_active', 'is_available', 'is_featured', 'badge']
    search_fields = ['name', 'description', 'color']
    readonly_fields = ['id', 'views_count', 'sales_count', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_available', 'is_featured', 'stock_quantity']
    fieldsets = (
        ('Général', {'fields': ('id', 'name', 'slug', 'category', 'badge', 'emoji', 'color', 'image')}),
        ('Description', {'fields': ('description', 'short_description', 'included_items', 'available_sizes')}),
        ('Tarification', {'fields': ('price', 'original_price')}),
        ('Stock & Disponibilité', {'fields': ('stock_quantity', 'is_available', 'is_active', 'is_featured')}),
        ('Personnalisation', {'fields': ('allows_embroidery', 'max_embroidery_chars')}),
        ('Statistiques', {'fields': ('views_count', 'sales_count', 'created_at', 'updated_at')}),
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'product', 'rating', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['is_approved', 'is_verified_purchase', 'rating']
    search_fields = ['author_name', 'comment', 'product__name']
    list_editable = ['is_approved']
    readonly_fields = ['id', 'created_at']
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        count = queryset.update(is_approved=True, approved_at=timezone.now())
        self.message_user(request, f"{count} avis approuvé(s).")
    approve_reviews.short_description = "✅ Approuver les avis sélectionnés"

    def reject_reviews(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f"{count} avis refusé(s).")
    reject_reviews.short_description = "❌ Refuser les avis sélectionnés"


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'current_uses', 'max_uses',
                    'is_active', 'valid_from', 'valid_until']
    list_filter = ['is_active']
    readonly_fields = ['id', 'current_uses', 'created_at']
