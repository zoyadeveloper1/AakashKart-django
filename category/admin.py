from django.contrib import admin
from .models import Category

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    
    # Display fields in the admin list
    list_display = ('category_name', 'slug')
    
    # Make the slug editable directly in the list view
    list_editable = ('slug',)
    
    # Add search box for category_name
    search_fields = ('category_name',)
    
    # Add filter sidebar for category_name
    list_filter = ('category_name',)

admin.site.register(Category, CategoryAdmin)
