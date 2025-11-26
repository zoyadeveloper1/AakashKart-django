from django.shortcuts import render, redirect, get_object_or_404
from carts.models import Cart, CartItem
from .models import Order, OrderProduct
import datetime
from django.contrib.auth.decorators import login_required

@login_required
def checkout(request):
    # Get the current user's cart
    cart = get_object_or_404(Cart, user=request.user)
    # Get all items in that cart
    cart_items = CartItem.objects.filter(cart=cart)

    total = 0
    for item in cart_items:
        item.total_price = item.product.price * item.quantity  # Calculate item total
        total += item.total_price

    tax = (2 * total) / 100  # 2% GST
    grand_total = total + tax

    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def place_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items:
        return redirect('store')

    total = sum(item.product.price * item.quantity for item in cart_items)
    tax = (2 * total) / 100
    grand_total = total + tax

    # Generate order number
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    order_number = f"{current_date}{request.user.id}"

    # Create order
    order = Order.objects.create(
        user=request.user,
        order_number=order_number,
        total=grand_total,
        tax=tax,
    )

    # Move cart items to OrderProduct
    for cart_item in cart_items:
        OrderProduct.objects.create(
            order=order,
            user=request.user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price,
            ordered=True,
        )

    # Clear cart
    cart_items.delete()

    return redirect('order_complete', order.id)

@login_required
def order_complete(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    ordered_products = OrderProduct.objects.filter(order=order)

    context = {
        'order': order,
        'ordered_products': ordered_products,
    }
    return render(request, 'orders/order_complete.html', context)
