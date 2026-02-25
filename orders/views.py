from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from decimal import Decimal
import uuid, json, requests

from carts.models import Cart, CartItem
from store.models import Product
from .models import Order, OrderProduct, Payment
from django.core.mail import send_mail
from django.template.loader import render_to_string



# ==================================================
# PAYPAL CONFIG
# ==================================================
PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_SECRET = settings.PAYPAL_SECRET
PAYPAL_API = "https://api-m.sandbox.paypal.com"


# ==================================================
# PAYPAL TOKEN
# ==================================================
def get_paypal_access_token():
    response = requests.post(
        f"{PAYPAL_API}/v1/oauth2/token",
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        data={"grant_type": "client_credentials"},
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    return None


# ==================================================
# CLIENT IP
# ==================================================
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")


# ==================================================
# CHECKOUT
# ==================================================
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    if not cart_items.exists():
        return redirect("carts:cart")

    total = sum(item.product.price * item.quantity for item in cart_items)
    tax = round(total * Decimal("0.05"), 2)
    grand_total = total + tax

    return render(request, "orders/checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "tax": tax,
        "grand_total": grand_total,
    })


# ==================================================
# PLACE ORDER
# ==================================================
@login_required
def place_order(request):
    if request.method != "POST":
        return redirect("orders:checkout")

    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    if not cart_items.exists():
        return redirect("orders:checkout")

    total = sum(item.product.price * item.quantity for item in cart_items)
    tax = round(total * Decimal("0.05"), 2)
    grand_total = total + tax

    order = Order.objects.create(
        user=request.user,
        first_name=request.POST.get("first_name"),
        last_name=request.POST.get("last_name"),
        phone=request.POST.get("phone"),
        email=request.POST.get("email"),
        address_line_1=request.POST.get("address_line_1"),
        address_line_2=request.POST.get("address_line_2"),
        city=request.POST.get("city"),
        state=request.POST.get("state"),
        country=request.POST.get("country"),
        total=grand_total,
        tax=tax,
        status="Pending",
        ip=get_client_ip(request),
        order_number=str(uuid.uuid4()).replace("-", "")[:10],
    )

    for item in cart_items:
        OrderProduct.objects.create(
            order=order,
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
            ordered=False,
        )

    payment_method = request.POST.get("payment_method")

    if payment_method == "COD":
        complete_order(order)
        return redirect("orders:order_complete", order_number=order.order_number)

    return redirect("orders:paypal_checkout", order_id=order.id)


# ==================================================
# PAYPAL PAGE
# ==================================================
@login_required
def paypal_checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/paypal.html", {"order": order})


# ==================================================
# CREATE PAYPAL ORDER
# ==================================================
@csrf_exempt
@login_required
def create_paypal_order(request):
    data = json.loads(request.body)
    order = get_object_or_404(Order, id=data["order_id"], user=request.user)

    token = get_paypal_access_token()
    usd_amount = round(order.total / Decimal("83"), 2)

    response = requests.post(
        f"{PAYPAL_API}/v2/checkout/orders",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": "USD",
                    "value": str(usd_amount)
                }
            }],
        },
    )
    return JsonResponse(response.json())


# ==================================================
# CAPTURE PAYPAL PAYMENT (FIXED)
# ==================================================
@csrf_exempt
@login_required
def capture_paypal_order(request, paypal_order_id):
    token = get_paypal_access_token()

    response = requests.post(
        f"{PAYPAL_API}/v2/checkout/orders/{paypal_order_id}/capture",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()

    if data.get("status") == "COMPLETED":
        order = get_object_or_404(Order, user=request.user, status="Pending")

        Payment.objects.create(
            user=request.user,
            order=order,
            payment_id=paypal_order_id,
            payment_method="PayPal",
            amount_paid=order.total,
            status="Completed",
        )

        complete_order(order)

        # 🔥 THIS is what sends user to Payment Successful page
        return JsonResponse({
            "redirect_url": redirect(
                "orders:order_complete",
                order_number=order.order_number
            ).url
        })

    return JsonResponse({"error": "Payment failed"})

# ==================================================
# COMPLETE ORDER (FINAL FIX 🔥)
# ==================================================
def complete_order(order):
    order_products = OrderProduct.objects.filter(order=order)

    for item in order_products:
        product = item.product
        product.stock -= item.quantity
        product.save()

        item.ordered = True
        item.save()

    CartItem.objects.filter(cart__user=order.user).delete()

    order.status = "Completed"
    order.save()

    # ✅ SEND EMAIL HERE
    send_order_confirmation_email(order)

# ==================================================
# ORDER COMPLETE PAGE
# ==================================================
@login_required
def order_complete(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_products = OrderProduct.objects.filter(order=order)

    return render(request, "orders/order_complete.html", {
        "order": order,
        "order_products": order_products,
    })

def send_order_confirmation_email(order):
    subject = f"Order Confirmed 🎉 | Order No: {order.order_number}"

    message = render_to_string("orders/order_email.html", {
        "order": order,
        "user": order.user,
    })

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
    )

@login_required
def payment_successful(request, order_number):
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user,
        status="Completed"
    )

    order_products = OrderProduct.objects.filter(order=order)
    subtotal = sum(i.price * i.quantity for i in order_products)

    return render(request, "orders/payment_successful.html", {
        "order": order,
        "subtotal": subtotal,
    })
