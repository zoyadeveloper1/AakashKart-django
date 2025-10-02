# store/views.py
from django.shortcuts import render
from store.models import Product


# Home page - all available products
def home(request):
    Products = Product.objects.all().filter(is_available=True)  # correct spelling
    context ={
         'product':Products,
     }

    return render(request, 'home.html', {'Products': Products})

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
