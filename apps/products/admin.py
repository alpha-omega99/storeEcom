# ===================== admin.py =====================
from django.contrib import admin
from django.utils import timezone
from .models import Category, Product, ProductReview, PromoCode

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
        ('Description', {'fields': ('description', 'short_description', 'included_items',)}),
        ('Tarification', {'fields': ('price', 'original_price')}),
        ('Stock & Disponibilité', {'fields': ('stock_quantity', 'is_available', 'is_active', 'is_featured')}),
        ('Personnalisation', {'fields': ('allows_embroidery', 'max_embroidery_chars', 'allows_personal_message', 'max_message_chars', 'embroidery_required')}),
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
