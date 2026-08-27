from django.urls import path
from . import views


app_name = "orders"


urlpatterns = [

    # ========================================================
    # CHECKOUT
    # ========================================================

    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),


    # ========================================================
    # PLACE ORDER
    # ========================================================

    path(
        "place-order/",
        views.place_order,
        name="place_order"
    ),


    # ========================================================
    # PAYPAL CHECKOUT PAGE
    # ========================================================

    path(
        "paypal/<int:order_id>/",
        views.paypal_checkout,
        name="paypal_checkout"
    ),


    # ========================================================
    # PAYPAL CREATE ORDER API
    # ========================================================

    path(
        "paypal/create/",
        views.create_paypal_order,
        name="create_paypal_order"
    ),


    # ========================================================
    # PAYPAL CAPTURE API
    # ========================================================

    path(
        "capture-paypal-order/<str:paypal_order_id>/",
        views.capture_paypal_order,
        name="capture_paypal_order"
    ),


    # ========================================================
    # ORDER COMPLETE
    # ========================================================

    path(
        "order-complete/<str:order_number>/",
        views.order_complete,
        name="order_complete"
    ),


    # ========================================================
    # PAYMENT SUCCESSFUL
    # ========================================================

    path(
        "payment-successful/<str:order_number>/",
        views.payment_successful,
        name="payment_successful"
    ),
]