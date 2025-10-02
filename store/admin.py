from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_available', 'created_date', 'modified_date')
    list_filter = ('category', 'is_available')  # Optional: filter sidebar
    search_fields = ('name', 'category__category_name')  # Optional: search by name or category
    list_editable = ('price', 'stock', 'is_available')  # Make price and stock editable directly

admin.site.register(Product, ProductAdmin)
