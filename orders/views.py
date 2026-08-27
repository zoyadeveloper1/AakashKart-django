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

PAYPAL_CLIENT_ID = getattr(
    settings,
    "PAYPAL_CLIENT_ID",
    ""
)

PAYPAL_SECRET = getattr(
    settings,
    "PAYPAL_SECRET",
    ""
)

PAYPAL_API = getattr(
    settings,
    "PAYPAL_BASE_URL",
    "https://api-m.sandbox.paypal.com"
).rstrip("/")


# ============================================================
# GET CLIENT IP
# ============================================================

def get_client_ip(request):

    x_forwarded_for = request.META.get(
        "HTTP_X_FORWARDED_FOR"
    )

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get(
        "REMOTE_ADDR"
    )


# ============================================================
# DECIMAL CONVERTER
# ============================================================

def to_decimal(value):

    if value is None:
        return Decimal("0.00")

    return Decimal(
        str(value)
    )


# ============================================================
# MONEY FORMAT
# ============================================================

def money(value):

    return to_decimal(value).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


# ============================================================
# GET PAYPAL ACCESS TOKEN
# ============================================================

def get_paypal_access_token():

    try:

        if not PAYPAL_CLIENT_ID:
            print("PAYPAL CLIENT ID MISSING")
            return None

        if not PAYPAL_SECRET:
            print("PAYPAL SECRET MISSING")
            return None

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
                "grant_type":
                    "client_credentials"
            },

            timeout=30,
        )

        print(
            "PAYPAL TOKEN STATUS:",
            response.status_code
        )

        if response.status_code == 200:

            data = response.json()

            token = data.get(
                "access_token"
            )

            print(
                "PAYPAL TOKEN RECEIVED:",
                bool(token)
            )

            return token

        print(
            "PAYPAL TOKEN ERROR:",
            response.text
        )

        return None

    except requests.RequestException as e:

        print(
            "PAYPAL TOKEN REQUEST ERROR:",
            repr(e)
        )

        return None

    except Exception as e:

        print(
            "PAYPAL TOKEN ERROR:",
            repr(e)
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

    total = Decimal("0.00")

    for item in cart_items:

        price = to_decimal(
            item.product.price
        )

        total += (
            price * item.quantity
        )

    total = money(total)

    # --------------------------------------------------------
    # TAX
    # --------------------------------------------------------

    tax = money(
        total * Decimal("0.05")
    )

    # --------------------------------------------------------
    # GRAND TOTAL
    # --------------------------------------------------------

    grand_total = money(
        total + tax
    )

    return render(

        request,

        "orders/checkout.html",

        {
            "cart_items":
                cart_items,

            "total":
                total,

            "tax":
                tax,

            "grand_total":
                grand_total,
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

    total = Decimal("0.00")

    for item in cart_items:

        price = to_decimal(
            item.product.price
        )

        total += (
            price * item.quantity
        )

    total = money(total)

    # --------------------------------------------------------
    # TAX
    # --------------------------------------------------------

    tax = money(
        total * Decimal("0.05")
    )

    # --------------------------------------------------------
    # GRAND TOTAL
    # --------------------------------------------------------

    grand_total = money(
        total + tax
    )

    # --------------------------------------------------------
    # CREATE ORDER
    # --------------------------------------------------------

    order = Order.objects.create(

        user=request.user,

        first_name=request.POST.get(
            "first_name",
            ""
        ),

        last_name=request.POST.get(
            "last_name",
            ""
        ),

        phone=request.POST.get(
            "phone",
            ""
        ),

        email=request.POST.get(
            "email",
            ""
        ),

        address_line_1=request.POST.get(
            "address_line_1",
            ""
        ),

        address_line_2=request.POST.get(
            "address_line_2",
            ""
        ),

        city=request.POST.get(
            "city",
            ""
        ),

        state=request.POST.get(
            "state",
            ""
        ),

        country=request.POST.get(
            "country",
            ""
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
    # ORDER PRODUCTS
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

    # --------------------------------------------------------
    # COD
    # --------------------------------------------------------

    if payment_method == "COD":

        complete_order(order)

        return redirect(
            "orders:order_complete",
            order_number=order.order_number
        )

    # --------------------------------------------------------
    # PAYPAL
    # --------------------------------------------------------

    if payment_method == "ONLINE":

        return redirect(
            "orders:paypal_checkout",
            order_id=order.id
        )

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
            "order":
                order,

            "paypal_client_id":
                PAYPAL_CLIENT_ID,
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
        # METHOD
        # ----------------------------------------------------

        if request.method != "POST":

            return JsonResponse(
                {
                    "success": False,
                    "error":
                        "POST request required"
                },
                status=405
            )

        # ----------------------------------------------------
        # REQUEST BODY
        # ----------------------------------------------------

        if not request.body:

            return JsonResponse(
                {
                    "success": False,
                    "error":
                        "Empty request body"
                },
                status=400
            )

        try:

            data = json.loads(
                request.body.decode("utf-8")
            )

        except (
            json.JSONDecodeError,
            UnicodeDecodeError
        ):

            return JsonResponse(
                {
                    "success": False,
                    "error":
                        "Invalid JSON request"
                },
                status=400
            )

        # ----------------------------------------------------
        # ORDER ID
        # ----------------------------------------------------

        order_id = data.get(
            "order_id"
        )

        if not order_id:

            return JsonResponse(
                {
                    "success": False,
                    "error":
                        "Order ID is required"
                },
                status=400
            )

        # ----------------------------------------------------
        # GET ORDER
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
            "DJANGO ORDER TOTAL:",
            order.total,
            type(order.total)
        )

        # ----------------------------------------------------
        # PAYPAL TOKEN
        # ----------------------------------------------------

        token = get_paypal_access_token()

        if not token:

            return JsonResponse(

                {
                    "success": False,
                    "error":
                        "Unable to authenticate with PayPal"
                },

                status=500
            )

        # ----------------------------------------------------
        # ORDER TOTAL
        # ----------------------------------------------------

        order_total = money(
            order.total
        )

        # ----------------------------------------------------
        # INR → USD
        # ----------------------------------------------------
        #
        # DEMO exchange rate.
        #
        # Example:
        # ₹208.95 / 83 = $2.52
        #
        # For production use a live exchange-rate service.
        # ----------------------------------------------------

        exchange_rate = Decimal(
            "83"
        )

        usd_amount = money(
            order_total /
            exchange_rate
        )

        # PayPal should not receive zero
        if usd_amount <= Decimal("0.00"):

            return JsonResponse(

                {
                    "success": False,
                    "error":
                        "Invalid payment amount"
                },

                status=400
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
        # PAYLOAD
        # ----------------------------------------------------

        payload = {

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
        }

        print(
            "PAYPAL CREATE PAYLOAD:",
            payload
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

                "Accept":
                    "application/json",

                "Prefer":
                    "return=representation",
            },

            json=payload,

            timeout=30,
        )

        print(
            "PAYPAL CREATE STATUS:",
            response.status_code
        )

        print(
            "PAYPAL CREATE RESPONSE:",
            response.text
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        try:

            paypal_data = response.json()

        except ValueError:

            return JsonResponse(

                {
                    "success": False,

                    "error":
                        "PayPal returned an invalid response",

                    "paypal_response":
                        response.text[:1000],
                },

                status=502
            )

        # ----------------------------------------------------
        # PAYPAL ERROR
        # ----------------------------------------------------

        if not response.ok:

            return JsonResponse(

                {
                    "success": False,

                    "error":
                        "PayPal order creation failed",

                    "details":
                        paypal_data,
                },

                status=response.status_code
            )

        # ----------------------------------------------------
        # ORDER ID CHECK
        # ----------------------------------------------------

        paypal_order_id = paypal_data.get(
            "id"
        )

        if not paypal_order_id:

            return JsonResponse(

                {
                    "success": False,

                    "error":
                        "PayPal order ID missing",

                    "details":
                        paypal_data,
                },

                status=502
            )

        print(
            "PAYPAL ORDER ID:",
            paypal_order_id
        )

        # ----------------------------------------------------
        # RETURN JSON
        # ----------------------------------------------------

        return JsonResponse(

            {
                "success": True,

                "id":
                    paypal_order_id,

                "status":
                    paypal_data.get(
                        "status"
                    ),

                "paypal_order":
                    paypal_data,
            }
        )

    except Exception as e:

        print(
            "PAYPAL CREATE ERROR:",
            repr(e)
        )

        return JsonResponse(

            {
                "success": False,

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
        # METHOD
        # ----------------------------------------------------

        if request.method != "POST":

            return JsonResponse(

                {
                    "success": False,

                    "error":
                        "POST request required"
                },

                status=405
            )

        # ----------------------------------------------------
        # TOKEN
        # ----------------------------------------------------

        token = get_paypal_access_token()

        if not token:

            return JsonResponse(

                {
                    "success": False,

                    "error":
                        "Unable to authenticate with PayPal"
                },

                status=500
            )

        # ----------------------------------------------------
        # CAPTURE
        # ----------------------------------------------------

        response = requests.post(

            f"{PAYPAL_API}/v2/checkout/orders/"
            f"{paypal_order_id}/capture",

            headers={

                "Authorization":
                    f"Bearer {token}",

                "Content-Type":
                    "application/json",

                "Accept":
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
        # JSON RESPONSE
        # ----------------------------------------------------

        try:

            data = response.json()

        except ValueError:

            return JsonResponse(

                {
                    "success": False,

                    "error":
                        "PayPal returned invalid capture response",

                    "paypal_response":
                        response.text[:1000],
                },

                status=502
            )

        # ----------------------------------------------------
        # PAYPAL ERROR
        # ----------------------------------------------------

        if not response.ok:

            return JsonResponse(

                {
                    "success": False,

                    "error":
                        "PayPal capture failed",

                    "details":
                        data,
                },

                status=response.status_code
            )

        # ----------------------------------------------------
        # PAYMENT STATUS
        # ----------------------------------------------------

        if data.get("status") != "COMPLETED":

            return JsonResponse(

                {
                    "success": False,

                    "error":
                        "Payment was not completed",

                    "paypal_status":
                        data.get("status"),
                },

                status=400
            )

        # ----------------------------------------------------
        # PURCHASE UNITS
        # ----------------------------------------------------

        purchase_units = data.get(
            "purchase_units",
            []
        )

        if not purchase_units:

            return JsonResponse(

                {
                    "success": False,

                    "error":
                        "Purchase information missing"
                },

                status=400
            )

        # ----------------------------------------------------
        # REFERENCE ID
        # ----------------------------------------------------

        reference_id = (
            purchase_units[0]
            .get("reference_id")
        )

        if not reference_id:

            return JsonResponse(

                {
                    "success": False,

                    "error":
                        "Order reference missing"
                },

                status=400
            )

        print(
            "PAYPAL REFERENCE ID:",
            reference_id
        )

        # ----------------------------------------------------
        # GET DJANGO ORDER
        # ----------------------------------------------------

        order = get_object_or_404(

            Order,

            order_number=reference_id,

            user=request.user,

            status="Pending"
        )

        # ----------------------------------------------------
        # DUPLICATE PAYMENT CHECK
        # ----------------------------------------------------

        existing_payment = (
            Payment.objects.filter(
                payment_id=paypal_order_id
            ).first()
        )

        if existing_payment:

            return JsonResponse(

                {
                    "success": False,

                    "error":
                        "Payment already processed"
                },

                status=400
            )

        # ----------------------------------------------------
        # PAYMENT AMOUNT
        # ----------------------------------------------------

        amount_paid = money(
            order.total
        )

        # ----------------------------------------------------
        # CREATE PAYMENT + COMPLETE ORDER
        # ----------------------------------------------------

        with transaction.atomic():

            Payment.objects.create(

                user=request.user,

                order=order,

                payment_id=
                    paypal_order_id,

                payment_method=
                    "PayPal",

                amount_paid=
                    amount_paid,

                status=
                    "Completed",
            )

            complete_order(
                order
            )

        print(
            "PAYMENT CREATED:",
            paypal_order_id
        )

        print(
            "ORDER COMPLETED:",
            order.order_number
        )

        # ----------------------------------------------------
        # SUCCESS URL
        # ----------------------------------------------------

        success_url = redirect(

            "orders:order_complete",

            order_number=
                order.order_number

        ).url

        return JsonResponse(

            {
                "success": True,

                "message":
                    "Payment completed successfully",

                "redirect_url":
                    success_url,

                "order_number":
                    order.order_number,
            }
        )

    except Exception as e:

        print(
            "PAYPAL CAPTURE ERROR:",
            repr(e)
        )

        return JsonResponse(

            {
                "success": False,

                "error":
                    str(e)
            },

            status=500
        )


# ============================================================
# COMPLETE ORDER
# ============================================================

def complete_order(order):

    order_products = (
        OrderProduct.objects.filter(
            order=order
        )
    )

    for item in order_products:

        product = item.product

        # ----------------------------------------------------
        # STOCK CHECK
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

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    send_order_confirmation_email(
        order
    )


# ============================================================
# ORDER COMPLETE
# ============================================================

@login_required
def order_complete(
    request,
    order_number
):

    order = get_object_or_404(

        Order,

        order_number=
            order_number,

        user=
            request.user
    )

    order_products = (
        OrderProduct.objects.filter(
            order=order
        )
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
# ORDER EMAIL
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

        fail_silently=True,
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

        order_number=
            order_number,

        user=
            request.user,

        status=
            "Completed"
    )

    order_products = (
        OrderProduct.objects.filter(
            order=order
        )
    )

    subtotal = Decimal("0.00")

    for item in order_products:

        subtotal += (
            to_decimal(item.price)
            * item.quantity
        )

    subtotal = money(
        subtotal
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