from django.contrib import admin
from category.models import Category

# Unregister first if already registered
if Category in admin.site._registry:
    admin.site.unregister(Category)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'slug')
