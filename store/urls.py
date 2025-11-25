from django.urls import path
from . import views

urlpatterns = [
    # Main Store
    path('', views.store, name='store'),

    # Category-wise
    path('category/<slug:category_slug>/', views.category_view, name='category-store'),

    # Product Details
    path('product/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),

    # Reviews
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),

    # Search
    path('search/', views.search, name='search'),

    # Category Shortcuts
    path('electronics/', views.electronics, name='electronics'),
    path('fashion/', views.fashion, name='fashion'),
    path('grocery/', views.grocery, name='grocery'),
    path('books/', views.books, name='books'),
    path('toys/', views.toys, name='toys'),
    path('sports/', views.sports, name='sports'),
    path('home-appliances/', views.home_appliances, name='home_appliances'),
    path('personal-care/', views.personal_care, name='personal_care'),
    path('light-beauty/', views.light_beauty, name='light_beauty'),
]
