# carts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from store.models import Product
from .models import Cart, CartItem
from decimal import Decimal


def add_cart(request, product_id):
    """Add product to user's cart or increase quantity if exists"""
    # ✅ Get color, size, and quantity safely from POST
    color = request.POST.get('color')
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))

    # For debugging (optional)
    # return HttpResponse(f"Color: {color}, Size: {size}, Quantity: {quantity}")

    # ✅ Redirect unauthenticated users to login
    if not request.user.is_authenticated:
        return redirect('login')

    # ✅ Get the product and user's cart
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # ✅ Check if item already exists with same color & size
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        color=color,
        size=size,
        defaults={'quantity': quantity}
    )

    # ✅ If item exists, just update quantity
    if not item_created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect('cart')  # redirect to cart view


def decrease_cart_item(request, item_id):
    """Decrease quantity of a specific cart item by 1"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()  # remove if quantity becomes 0

    return redirect('cart')



def remove_cart_item(request, cart_item_id):
    """Remove a specific CartItem from user's cart"""
    if not request.user.is_authenticated:
        return redirect('login')

    # ✅ Get the specific cart item (not just product)
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart')


def cart_view(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    total = sum([item.sub_total for item in cart_items])  # total of items
    tax_rate = Decimal('0.05')  # 5% tax as Decimal
    tax = total * tax_rate
    grand_total = total + tax

    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    return render(request, 'carts/checkout.html')
