
# ===================== serializers.py =====================

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
            'included_items', 
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
