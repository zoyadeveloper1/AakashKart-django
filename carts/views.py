from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal

from store.models import Product
from carts.models import Cart, CartItem



# ---------------------------------------------------
# ADD TO CART
# ---------------------------------------------------
@login_required
def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    color = request.POST.get('color')
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item = CartItem.objects.filter(
        cart=cart,
        product=product,
        color=color,
        size=size
    ).first()

    if cart_item:
        cart_item.quantity += quantity
        cart_item.save()
    else:
        CartItem.objects.create(
            cart=cart,
            product=product,
            color=color,
            size=size,
            quantity=quantity
        )

    return redirect("carts:cart")


# ---------------------------------------------------
# DECREASE CART ITEM
# ---------------------------------------------------
@login_required
def decrease_cart_item(request, item_id):
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect("carts:cart")


# ---------------------------------------------------
# REMOVE CART ITEM
# ---------------------------------------------------


@login_required
def remove_cart_item(request, cart_item_id):
    cart = get_object_or_404(Cart, user=request.user)

    cart_item = get_object_or_404(
        CartItem,
        id=cart_item_id,
        cart=cart
    )

    cart_item.delete()
    return redirect("carts:cart")


# ---------------------------------------------------
# CART VIEW
# ---------------------------------------------------
@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    total = sum(
        (item.product.price * item.quantity) for item in cart_items
    ) or Decimal("0.00")

    tax = (total * Decimal("0.05")).quantize(Decimal("0.01"))
    grand_total = total + tax

    context = {
        "cart_items": cart_items,
        "total": total,
        "tax": tax,
        "grand_total": grand_total,
    }

    return render(request, "store/cart.html", context)


# ---------------------------------------------------
# CHECKOUT
# ---------------------------------------------------
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    if not cart_items.exists():
        return redirect("carts:cart")

    total = sum(
        (item.product.price * item.quantity) for item in cart_items
    ) or Decimal("0.00")

    tax = (total * Decimal("0.05")).quantize(Decimal("0.01"))
    grand_total = total + tax

    context = {
        "cart_items": cart_items,
        "total": total,
        "tax": tax,
        "grand_total": grand_total,
    }

    return render(request, "orders/checkout.html", context)


# ---------------------------------------------------
# PLACE ORDER
# ---------------------------------------------------
@login_required
def place_order(request):
    # Later: create Order + OrderItem here
    return redirect("orders:order_complete")


# ---------------------------------------------------
# ORDER COMPLETE
# ---------------------------------------------------
@login_required
def order_complete(request):
    return render(request, "orders/order_complete.html")


# ---------------------------------------------------
# PAYMENT (TEMP / TEST)
# ---------------------------------------------------
@login_required
def payment(request):
    return HttpResponse("Payment processing...")


@login_required
def payment_success(request):
    return HttpResponse("Payment successful!")


@login_required
def payment_cancel(request):
    return HttpResponse("Payment cancelled.")


@login_required
def payment_failed(request):
    return HttpResponse("Payment failed.")


@login_required
def payment_complete(request):
    return HttpResponse("Payment complete.")

def complete_order(order):
    # Clear user's cart after order
    CartItem.objects.filter(cart__user=order.user).delete()

    # Optional: deactivate cart instead of deleting
    # Cart.objects.filter(user=order.user).update(is_active=False)
    pass
