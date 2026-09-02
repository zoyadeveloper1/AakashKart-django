# store/views.py

from django.shortcuts import render
from store.models import Product
from category.models import Category


# Home page
def home(request):
    # Get all available products
    products = Product.objects.filter(is_available=True)

    # Get all categories
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
    }

    return render(request, 'home.html', context)


# Category pages
def electronics(request):
    return render(request, 'categories/electronics.html')


def fashion(request):
    return render(request, 'categories/fashion.html')


def grocery(request):
    return render(request, 'categories/grocery.html')


def books(request):
    return render(request, 'categories/books.html')


def toys(request):
    return render(request, 'categories/toys.html')


def sports(request):
    return render(request, 'categories/sports.html')