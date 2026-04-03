from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [

    # ==============================
    # CHECKOUT & PLACE ORDER
    # ==============================
    path("checkout/", views.checkout, name="checkout"),
    path("place-order/", views.place_order, name="place_order"),

    # ==============================
    # PAYPAL PAGE
    # ==============================
    path(
        "paypal/<int:order_id>/",
        views.paypal_checkout,
        name="paypal_checkout"
    ),

    # ==============================
    # PAYPAL AJAX APIs
    # ==============================
    path(
        "paypal/create/",
        views.create_paypal_order,
        name="create_paypal_order"
    ),

    path(
        "capture-paypal-order/<str:paypal_order_id>/",
        views.capture_paypal_order,
        name="capture_paypal_order"
    ),

    # ==============================
    # ORDER SUCCESS PAGES
    # ==============================
    path(
        "order-complete/<str:order_number>/",
        views.order_complete,
        name="order_complete"
    ),

    path(
        "payment-successful/<str:order_number>/",
        views.payment_successful,
        name="payment_successful"
    ),
]