

# ===================== views.py =====================
from decimal import Decimal  # <-- CORRECTION 1 : Indispensable pour la conversion du prix max
from rest_framework import generics, status
from .models import Product, Category, ProductReview, PromoCode  # <-- CORRECTION 2 & 3 : Modèles importés ici
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import ProductListSerializer, ProductDetailSerializer, CategorySerializer, ProductReviewCreateSerializer, PromoCodeValidateSerializer
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
                qs = qs.filter(price__lte=Decimal(max_price))  # <-- Utilise maintenant l'import Decimal
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
