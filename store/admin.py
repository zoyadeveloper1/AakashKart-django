from django.contrib import admin
from .models import Product, Variation

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name', 
        'price', 
        'old_price',    # Added old_price
        'stock',        # Added stock
        'is_available', 
        'created_at', 
        'updated_at', 
        'category'
    )

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'variation_category',
        'variation_value',
        'is_active',
        'created_date',
    )
    list_editable=('is_active',)
    list_filter = ('product','variation_category','variation_value')
    search_fields = ('product__product_name', 'variation_value')
