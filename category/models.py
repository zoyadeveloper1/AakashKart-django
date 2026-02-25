from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    category_name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def get_url(self):
        return reverse('store_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name


