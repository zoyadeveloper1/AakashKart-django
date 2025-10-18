from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),  # all products / search
    path('category/<slug:category_slug>/', views.category_view, name='category-store'),
    path('product/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),

    # Category shortcuts (optional)
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
