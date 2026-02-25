from django.urls import path
from . import views

app_name = "carts"

urlpatterns = [
    # -------------------------------
    # CART ACTIONS
    # -------------------------------
    path('add/<int:product_id>/', views.add_cart, name='add_cart'),  # Add item
    path('decrease/<int:item_id>/', views.decrease_cart_item, name='decrease_cart_item'),  # Decrease quantity
    path('remove-cart-item/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/', views.cart_view, name='cart'),  # View cart
    # urls.py
    

    # -------------------------------
    # CHECKOUT & ORDERS
    # -------------------------------
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-complete/', views.order_complete, name='order_complete'),

    # -------------------------------
    # PAYMENT
    # -------------------------------
    path('payment/', views.payment, name='payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('payment/complete/', views.payment_complete, name='payment_complete'),
]
