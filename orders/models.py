from django.db import models
from django.conf import settings
from store.models import Product
import uuid
from accounts.models import Account
from django.utils import timezone

# ------------------------
# Helper function
# ------------------------
def generate_order_number():
    """Auto-generate a unique order number"""
    return str(uuid.uuid4()).replace('-', '')[:20]

# ------------------------
# Order model
# ------------------------
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    first_name = models.CharField(max_length=50, default="Unknown")
    last_name = models.CharField(max_length=50, default="Unknown")
    phone = models.CharField(max_length=15, default="0000000000")
    email = models.EmailField(default="example@example.com")
    address_line_1 = models.CharField(max_length=255, default="Unknown Address")
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, default="Unknown City")
    state = models.CharField(max_length=100, default="Unknown State")
    country = models.CharField(max_length=100, default="Unknown Country")
    order_note = models.TextField(blank=True, null=True)
    order_number = models.CharField(max_length=20, unique=True, blank=True)  # Auto-generate
    total = models.FloatField(default=0)
    tax = models.FloatField(default=0)
    ip = models.GenericIPAddressField(blank=True, null=True)  # Store customer IP
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"


# ------------------------
# Payment model
# ------------------------
class Payment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=50, default="COD")
    amount_paid = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_id} - {self.user.username}"


# ------------------------
# OrderProduct model
# ------------------------
class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(default=0)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.product_name} ({self.quantity})"
