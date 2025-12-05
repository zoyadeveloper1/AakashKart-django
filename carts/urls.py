from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('decrease-cart-item/<int:item_id>/', views.decrease_cart_item, name='decrease_cart_item'),
    path('remove-cart-item/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place-order'),
    

    

    

]

