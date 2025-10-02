from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('add-to-cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),


    # Category and Product Detail
    path('<slug:category_slug>/', views.store, name='products_by_category'),
    path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    

    

    # Static category pages (if you still want them separately)
    path('electronics/', views.electronics, name='electronics'),
    path('fashion/', views.fashion, name='fashion'),
    path('grocery/', views.grocery, name='grocery'),
    path('books/', views.books, name='books'),
    path('toys/', views.toys, name='toys'),
    path('sports/', views.sports, name='sports'),
    path('home_appliances/', views.home_appliances, name='home_appliances'),
    path('personal_care/', views.personal_care, name='personal_care'),
    path('light_beauty/', views.light_beauty, name='light_beauty'),
]
