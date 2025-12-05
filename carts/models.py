from django.db import models
from django.conf import settings
from store.models import Product
from accounts.models import Account

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  # temporarily allow null

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE,null=True)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)


    @property
    def sub_total(self):
        return self.product.price * self.quantity


    def __str__(self):
        return f"{self.product.product_name} ({self.color}, {self.size})"