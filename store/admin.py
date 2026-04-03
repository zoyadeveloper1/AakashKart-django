from django.contrib import admin
from .models import Product, Variation, ReviewRating


# ---------------- PRODUCT ADMIN ----------------

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'price',
        'old_price',
        'stock',
        'is_available',
        'created_at',
        'updated_at',
        'category'
    )
    prepopulated_fields = {'slug': ('product_name',)}
    list_filter = ('is_available', 'category')
    search_fields = ('product_name', 'description')


# ---------------- VARIATION ADMIN ----------------

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'variation_category',
        'variation_value',
        'is_active',
        'created_date',
    )
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category')
    search_fields = ('product__product_name', 'variation_value')


# ---------------- REVIEW RATING ADMIN ----------------

@admin.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'user',
        'rating',
        'status',
        'created_at'
    )
    list_editable = ('status',)
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('product__product_name', 'user__username', 'review')