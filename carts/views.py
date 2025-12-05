# carts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from store.models import Product
from .models import Cart, CartItem
from decimal import Decimal

# ---------------------------------------------------
# ADD TO CART
# ---------------------------------------------------
def add_cart(request, product_id):

    # User login check
    if not request.user.is_authenticated:
        return redirect('login')

    # Get product
    product = get_object_or_404(Product, id=product_id)

    # POST values
    color = request.POST.get('color')
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))

    # Get user cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if item already exists with SAME color & size
    existing_item = CartItem.objects.filter(
        cart=cart,
        product=product,
        color=color,
        size=size
    ).first()

    if existing_item:
        # If same item exists → increase quantity
        existing_item.quantity += quantity
        existing_item.save()
    else:
        # Otherwise → create new item
        CartItem.objects.create(
            cart=cart,
            product=product,
            color=color,
            size=size,
            quantity=quantity
        )

    return redirect('cart')


# ---------------------------------------------------
# DECREASE CART ITEM
# ---------------------------------------------------
def decrease_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')


# ---------------------------------------------------
# REMOVE ITEM COMPLETELY
# ---------------------------------------------------
def remove_cart_item(request, cart_item_id):
    if not request.user.is_authenticated:
        return redirect('login')

    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    cart_item.delete()

    return redirect('cart')


# ---------------------------------------------------
# CART VIEW
# ---------------------------------------------------
def cart_view(request):

    if not request.user.is_authenticated:
        return redirect('login')

    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    total = sum(item.sub_total for item in cart_items)
    tax_rate = Decimal('0.05')  # 5%
    tax = total * tax_rate
    grand_total = total + tax

    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)


# ---------------------------------------------------
# CHECKOUT
# ---------------------------------------------------
def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'store/checkout.html')


# ---------------------------------------------------
# PLACE ORDER
# ---------------------------------------------------
def place_order(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return HttpResponse("Order placed!")
