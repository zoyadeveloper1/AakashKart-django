from django.db import models
from category.models import Category
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


# ---------------- PRODUCT MODEL ---------------- #

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    image = models.ImageField(upload_to='products/', blank=True, null=True)

    slug = models.SlugField(unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    # 🔥 AUTO SLUG GENERATE
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.product_name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    # ✅ FIXED URL METHOD
    def get_url(self):
        return reverse('store:product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name


# ---------------- REVIEW MODEL ---------------- #

class ReviewRating(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    review = models.TextField(max_length=500, blank=True)

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} ({self.rating}⭐)"


# ---------------- VARIATION MODEL ---------------- #

VARIATION_CATEGORY_CHOICES = (
    ('color', 'Color'),
    ('size', 'Size'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    variation_category = models.CharField(max_length=100, choices=VARIATION_CATEGORY_CHOICES)
    variation_value = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)

    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.variation_category}: {self.variation_value}"