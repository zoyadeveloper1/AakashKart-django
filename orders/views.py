from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db import transaction

from decimal import Decimal, ROUND_HALF_UP
import json
import requests

from carts.models import Cart, CartItem
from .models import Order, OrderProduct, Payment


# ============================================================
# PAYPAL CONFIGURATION
# ============================================================

PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_SECRET = settings.PAYPAL_SECRET

# PayPal Sandbox API
PAYPAL_API = "https://api-m.sandbox.paypal.com"


# ============================================================
# GET CLIENT IP
# ============================================================

def get_client_ip(request):
    """
    Get visitor/client IP address.
    """

    x_forwarded_for = request.META.get(
        "HTTP_X_FORWARDED_FOR"
    )

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


# ============================================================
# CONVERT VALUE TO DECIMAL
# ============================================================

def to_decimal(value):
    """
    Safely convert float/int/string/Decimal to Decimal.

    This fixes:
    unsupported operand type(s) for /:
    'float' and 'decimal.Decimal'
    """

    return Decimal(str(value))


# ============================================================
# GET PAYPAL ACCESS TOKEN
# ============================================================

def get_paypal_access_token():

    try:

        response = requests.post(

            f"{PAYPAL_API}/v1/oauth2/token",

            auth=(
                PAYPAL_CLIENT_ID,
                PAYPAL_SECRET
            ),

            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
            },

            data={
                "grant_type": "client_credentials"
            },

            timeout=30,
        )

        print(
            "PAYPAL TOKEN STATUS:",
            response.status_code
        )

        if response.status_code == 200:

            token = response.json().get(
                "access_token"
            )

            print("PAYPAL TOKEN RECEIVED: YES")

            return token

        print(
            "PAYPAL TOKEN ERROR:",
            response.text
        )

        return None

    except requests.RequestException as e:

        print(
            "PAYPAL TOKEN REQUEST ERROR:",
            str(e)
        )

        return None


# ============================================================
# CHECKOUT
# ============================================================

@login_required
def checkout(request):

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_items = CartItem.objects.filter(
        cart=cart,
        is_active=True
    )

    if not cart_items.exists():

        return redirect(
            "carts:cart"
        )

    # --------------------------------------------------------
    # SUBTOTAL
    # --------------------------------------------------------

    total = sum(
        (
            to_decimal(item.product.price)
            * item.quantity
        )
        for item in cart_items
    )

    total = total.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    # --------------------------------------------------------
    # TAX 5%
    # --------------------------------------------------------

    tax = (
        total * Decimal("0.05")
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    # --------------------------------------------------------
    # GRAND TOTAL
    # --------------------------------------------------------

    grand_total = (
        total + tax
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    return render(
        request,
        "orders/checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
            "tax": tax,
            "grand_total": grand_total,
        }
    )


# ============================================================
# PLACE ORDER
# ============================================================

@login_required
def place_order(request):

    if request.method != "POST":

        return redirect(
            "orders:checkout"
        )

    # --------------------------------------------------------
    # GET CART
    # --------------------------------------------------------

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_items = CartItem.objects.filter(
        cart=cart,
        is_active=True
    )

    if not cart_items.exists():

        return redirect(
            "orders:checkout"
        )

    # --------------------------------------------------------
    # CALCULATE TOTAL
    # --------------------------------------------------------

    total = sum(
        (
            to_decimal(item.product.price)
            * item.quantity
        )
        for item in cart_items
    )

    total = total.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    # --------------------------------------------------------
    # TAX
    # --------------------------------------------------------

    tax = (
        total * Decimal("0.05")
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    # --------------------------------------------------------
    # GRAND TOTAL
    # --------------------------------------------------------

    grand_total = (
        total + tax
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    # --------------------------------------------------------
    # CREATE ORDER
    # --------------------------------------------------------

    order = Order.objects.create(

        user=request.user,

        first_name=request.POST.get(
            "first_name"
        ),

        last_name=request.POST.get(
            "last_name"
        ),

        phone=request.POST.get(
            "phone"
        ),

        email=request.POST.get(
            "email"
        ),

        address_line_1=request.POST.get(
            "address_line_1"
        ),

        address_line_2=request.POST.get(
            "address_line_2"
        ),

        city=request.POST.get(
            "city"
        ),

        state=request.POST.get(
            "state"
        ),

        country=request.POST.get(
            "country"
        ),

        total=grand_total,

        tax=tax,

        status="Pending",

        ip=get_client_ip(request),
    )

    print(
        "DJANGO ORDER CREATED:",
        order.order_number
    )

    print(
        "ORDER TOTAL:",
        order.total,
        type(order.total)
    )

    # --------------------------------------------------------
    # CREATE ORDER PRODUCTS
    # --------------------------------------------------------

    for item in cart_items:

        OrderProduct.objects.create(

            order=order,

            user=request.user,

            product=item.product,

            quantity=item.quantity,

            price=item.product.price,

            ordered=False,
        )

    # --------------------------------------------------------
    # PAYMENT METHOD
    # --------------------------------------------------------

    payment_method = request.POST.get(
        "payment_method"
    )

    print(
        "PAYMENT METHOD:",
        payment_method
    )

    # ========================================================
    # CASH ON DELIVERY
    # ========================================================

    if payment_method == "COD":

        complete_order(order)

        return redirect(
            "orders:order_complete",
            order_number=order.order_number
        )

    # ========================================================
    # ONLINE / PAYPAL
    # ========================================================

    elif payment_method == "ONLINE":

        return redirect(
            "orders:paypal_checkout",
            order_id=order.id
        )

    # ========================================================
    # INVALID PAYMENT METHOD
    # ========================================================

    return redirect(
        "orders:checkout"
    )


# ============================================================
# PAYPAL CHECKOUT PAGE
# ============================================================

@login_required
def paypal_checkout(request, order_id):

    order = get_object_or_404(

        Order,

        id=order_id,

        user=request.user,

        status="Pending"
    )

    return render(

        request,

        "orders/paypal.html",

        {
            "order": order,

            "paypal_client_id":
                settings.PAYPAL_CLIENT_ID,
        }
    )


# ============================================================
# CREATE PAYPAL ORDER
# ============================================================

@csrf_exempt
@login_required
def create_paypal_order(request):

    try:

        # ----------------------------------------------------
        # CHECK METHOD
        # ----------------------------------------------------

        if request.method != "POST":

            return JsonResponse(
                {
                    "error":
                        "POST request required"
                },
                status=405
            )

        # ----------------------------------------------------
        # READ JSON
        # ----------------------------------------------------

        try:

            data = json.loads(
                request.body
            )

        except json.JSONDecodeError:

            return JsonResponse(
                {
                    "error":
                        "Invalid JSON request"
                },
                status=400
            )

        # ----------------------------------------------------
        # GET ORDER ID
        # ----------------------------------------------------

        order_id = data.get(
            "order_id"
        )

        if not order_id:

            return JsonResponse(
                {
                    "error":
                        "Order ID is required"
                },
                status=400
            )

        # ----------------------------------------------------
        # GET DJANGO ORDER
        # ----------------------------------------------------

        order = get_object_or_404(

            Order,

            id=order_id,

            user=request.user,

            status="Pending"
        )

        print(
            "PAYPAL DJANGO ORDER:",
            order.order_number
        )

        print(
            "ORDER TOTAL BEFORE CONVERSION:",
            order.total,
            type(order.total)
        )

        # ----------------------------------------------------
        # GET PAYPAL TOKEN
        # ----------------------------------------------------

        token = get_paypal_access_token()

        if not token:

            return JsonResponse(
                {
                    "error":
                        "Unable to authenticate with PayPal"
                },
                status=500
            )

        # ----------------------------------------------------
        # CONVERT ORDER TOTAL TO DECIMAL
        # ----------------------------------------------------

        order_total = to_decimal(
            order.total
        )

        # ----------------------------------------------------
        # INR → USD
        # ----------------------------------------------------

        # Demo/static exchange rate.
        # Replace with live exchange rate for production.

        exchange_rate = Decimal("83")

        usd_amount = (
            order_total / exchange_rate
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        print(
            "ORDER TOTAL INR:",
            order_total
        )

        print(
            "PAYPAL AMOUNT USD:",
            usd_amount
        )

        # ----------------------------------------------------
        # CREATE PAYPAL ORDER
        # ----------------------------------------------------

        response = requests.post(

            f"{PAYPAL_API}/v2/checkout/orders",

            headers={

                "Authorization":
                    f"Bearer {token}",

                "Content-Type":
                    "application/json",

                "Prefer":
                    "return=representation",
            },

            json={

                "intent":
                    "CAPTURE",

                "purchase_units": [

                    {

                        "reference_id":
                            str(
                                order.order_number
                            ),

                        "description":
                            (
                                "AakashKart Order "
                                f"{order.order_number}"
                            ),

                        "amount": {

                            "currency_code":
                                "USD",

                            "value":
                                str(
                                    usd_amount
                                ),
                        },
                    }
                ],
            },

            timeout=30,
        )

        # ----------------------------------------------------
        # PRINT PAYPAL RESPONSE
        # ----------------------------------------------------

        print(
            "PAYPAL CREATE STATUS:",
            response.status_code
        )

        print(
            "PAYPAL CREATE RESPONSE:",
            response.text
        )

        # ----------------------------------------------------
        # HANDLE PAYPAL ERROR
        # ----------------------------------------------------

        if not response.ok:

            try:

                details = response.json()

            except ValueError:

                details = {
                    "message":
                        response.text
                }

            return JsonResponse(

                {
                    "error":
                        "PayPal order creation failed",

                    "details":
                        details,
                },

                status=response.status_code
            )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        paypal_data = response.json()

        print(
            "PAYPAL ORDER ID:",
            paypal_data.get("id")
        )

        return JsonResponse(
            paypal_data
        )

    # --------------------------------------------------------
    # GENERAL ERROR
    # --------------------------------------------------------

    except Exception as e:

        print(
            "PAYPAL CREATE ERROR:",
            repr(e)
        )

        return JsonResponse(

            {
                "error":
                    str(e)
            },

            status=500
        )


# ============================================================
# CAPTURE PAYPAL PAYMENT
# ============================================================

@csrf_exempt
@login_required
def capture_paypal_order(
    request,
    paypal_order_id
):

    try:

        # ----------------------------------------------------
        # CHECK METHOD
        # ----------------------------------------------------

        if request.method != "POST":

            return JsonResponse(

                {
                    "error":
                        "POST request required"
                },

                status=405
            )

        # ----------------------------------------------------
        # GET PAYPAL TOKEN
        # ----------------------------------------------------

        token = get_paypal_access_token()

        if not token:

            return JsonResponse(

                {
                    "error":
                        "Unable to authenticate with PayPal"
                },

                status=500
            )

        # ----------------------------------------------------
        # CAPTURE PAYMENT
        # ----------------------------------------------------

        response = requests.post(

            f"{PAYPAL_API}/v2/checkout/orders/"
            f"{paypal_order_id}/capture",

            headers={

                "Authorization":
                    f"Bearer {token}",

                "Content-Type":
                    "application/json",

                "Prefer":
                    "return=representation",
            },

            json={},

            timeout=30,
        )

        print(
            "PAYPAL CAPTURE STATUS:",
            response.status_code
        )

        print(
            "PAYPAL CAPTURE RESPONSE:",
            response.text
        )

        # ----------------------------------------------------
        # READ JSON RESPONSE
        # ----------------------------------------------------

        try:

            data = response.json()

        except ValueError:

            return JsonResponse(

                {
                    "error":
                        "Invalid response from PayPal"
                },

                status=500
            )

        # ----------------------------------------------------
        # PAYPAL ERROR
        # ----------------------------------------------------

        if not response.ok:

            return JsonResponse(

                {
                    "error":
                        "PayPal capture failed",

                    "details":
                        data,
                },

                status=response.status_code
            )

        # ----------------------------------------------------
        # CHECK COMPLETED
        # ----------------------------------------------------

        if data.get("status") != "COMPLETED":

            return JsonResponse(

                {
                    "error":
                        "Payment was not completed",

                    "paypal_status":
                        data.get("status"),
                },

                status=400
            )

        # ====================================================
        # GET PURCHASE UNIT
        # ====================================================

        purchase_units = data.get(
            "purchase_units",
            []
        )

        if not purchase_units:

            return JsonResponse(

                {
                    "error":
                        "Purchase information missing"
                },

                status=400
            )

        # ----------------------------------------------------
        # GET REFERENCE ID
        # ----------------------------------------------------

        reference_id = (

            purchase_units[0]
            .get("reference_id")
        )

        if not reference_id:

            return JsonResponse(

                {
                    "error":
                        "Order reference missing"
                },

                status=400
            )

        print(
            "PAYPAL REFERENCE ID:",
            reference_id
        )

        # ====================================================
        # FIND DJANGO ORDER
        # ====================================================

        order = get_object_or_404(

            Order,

            order_number=reference_id,

            user=request.user,

            status="Pending"
        )

        # ====================================================
        # PREVENT DUPLICATE PAYMENT
        # ====================================================

        existing_payment = Payment.objects.filter(

            payment_id=paypal_order_id

        ).first()

        if existing_payment:

            return JsonResponse(

                {
                    "error":
                        "Payment already processed"
                },

                status=400
            )

        # ====================================================
        # CREATE PAYMENT
        # ====================================================

        Payment.objects.create(

            user=request.user,

            order=order,

            payment_id=paypal_order_id,

            payment_method="PayPal",

            amount_paid=order.total,

            status="Completed",
        )

        print(
            "PAYMENT CREATED:",
            paypal_order_id
        )

        # ====================================================
        # COMPLETE ORDER
        # ====================================================

        complete_order(order)

        # ====================================================
        # SUCCESS URL
        # ====================================================

        success_url = redirect(

            "orders:order_complete",

            order_number=
                order.order_number
        ).url

        return JsonResponse(

            {

                "success":
                    True,

                "message":
                    "Payment completed successfully",

                "redirect_url":
                    success_url,
            }
        )

    # --------------------------------------------------------
    # GENERAL ERROR
    # --------------------------------------------------------

    except Exception as e:

        print(
            "PAYPAL CAPTURE ERROR:",
            repr(e)
        )

        return JsonResponse(

            {
                "error":
                    str(e)
            },

            status=500
        )


# ============================================================
# COMPLETE ORDER
# ============================================================

@transaction.atomic
def complete_order(order):

    order_products = OrderProduct.objects.filter(
        order=order
    )

    for item in order_products:

        product = item.product

        # ----------------------------------------------------
        # CHECK STOCK
        # ----------------------------------------------------

        if product.stock < item.quantity:

            raise ValueError(
                f"Insufficient stock for "
                f"{product.product_name}"
            )

        # ----------------------------------------------------
        # REDUCE STOCK
        # ----------------------------------------------------

        product.stock -= item.quantity

        product.save()

        # ----------------------------------------------------
        # MARK ORDERED
        # ----------------------------------------------------

        item.ordered = True

        item.save()

    # --------------------------------------------------------
    # CLEAR CART
    # --------------------------------------------------------

    CartItem.objects.filter(
        cart__user=order.user
    ).delete()

    # --------------------------------------------------------
    # COMPLETE ORDER
    # --------------------------------------------------------

    order.status = "Completed"

    order.save()

    print(
        "ORDER COMPLETED:",
        order.order_number
    )

    # --------------------------------------------------------
    # SEND EMAIL
    # --------------------------------------------------------

    send_order_confirmation_email(order)


# ============================================================
# ORDER COMPLETE PAGE
# ============================================================

@login_required
def order_complete(
    request,
    order_number
):

    order = get_object_or_404(

        Order,

        order_number=order_number,

        user=request.user
    )

    order_products = OrderProduct.objects.filter(

        order=order
    )

    return render(

        request,

        "orders/order_complete.html",

        {

            "order":
                order,

            "order_products":
                order_products,
        }
    )


# ============================================================
# SEND ORDER CONFIRMATION EMAIL
# ============================================================

def send_order_confirmation_email(order):

    subject = (

        f"Order Confirmed 🎉 | "
        f"Order No: {order.order_number}"
    )

    message = render_to_string(

        "orders/order_email.html",

        {

            "order":
                order,

            "user":
                order.user,
        }
    )

    send_mail(

        subject,

        message,

        settings.DEFAULT_FROM_EMAIL,

        [order.email],

        fail_silently=False,
    )


# ============================================================
# PAYMENT SUCCESSFUL
# ============================================================

@login_required
def payment_successful(
    request,
    order_number
):

    order = get_object_or_404(

        Order,

        order_number=order_number,

        user=request.user,

        status="Completed"
    )

    order_products = OrderProduct.objects.filter(

        order=order
    )

    subtotal = sum(

        (
            to_decimal(item.price)
            * item.quantity
        )

        for item in order_products
    )

    subtotal = subtotal.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    return render(

        request,

        "orders/payment_successful.html",

        {

            "order":
                order,

            "subtotal":
                subtotal,
        }
    )