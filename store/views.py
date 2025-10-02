from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Review
from category.models import Category




def home(request):
    # Maybe show featured products only
    products = Product.objects.filter(is_available=True)[:6]  # first 6 products
    return render(request, 'home.html', {'products': products})

# ==================== STORE ====================
def store(request, category_slug=None):
    categories = Category.objects.all()   # all categories for dropdown
    products = None
    category = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
    else:
        products = Product.objects.filter(is_available=True)

    product_count = products.count()

    # Sizes for sidebar filter (sample)
    sizes = ["Small", "Medium", "Large", "X-Large"]

    return render(request, 'store/store.html', {
        'categories': categories,
        'products': products,
        'product_count': product_count,
        'category': category,
        'sizes': sizes,
    })


# ==================== PRODUCT DETAIL ====================
def product_detail(request, category_slug, product_slug):
    # Get the product by category and product slug
    product = get_object_or_404(Product, slug=product_slug, category__slug=category_slug)

    # Reviews related to this product
    reviews = product.reviews.all().order_by('-created_at')

    # Example: if you have sizes as a ManyToMany field or similar
    try:
        sizes = product.sizes.all()
    except AttributeError:
        sizes = ["Small", "Medium", "Large", "X-Large"]  # default sizes

    return render(request, 'store/product_detail.html', {
        'product': product,
        'single_product': product,   # for template compatibility
        'sizes': sizes,
        'reviews': reviews,
    })


# ==================== ADD REVIEW ====================
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')

        # Save review
        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
    return redirect(product.get_url())


# ==================== CATEGORY-SPECIFIC VIEWS ====================
def electronics(request):
    category = get_object_or_404(Category, category_name__iexact="Electronics")
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'store/category_products.html', {'category': category, 'products': products})

def fashion(request):
    category = get_object_or_404(Category, category_name__iexact="Fashion")
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'store/category_products.html', {'category': category, 'products': products})

def grocery(request):
    category = get_object_or_404(Category, category_name__iexact="Grocery")
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'store/category_products.html', {'category': category, 'products': products})

def books(request):
    category = get_object_or_404(Category, category_name__iexact="Books")
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'store/category_products.html', {'category': category, 'products': products})

def toys(request):
    category = get_object_or_404(Category, category_name__iexact="Toys")
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'store/category_products.html', {'category': category, 'products': products})

def sports(request):
    category = get_object_or_404(Category, category_name__iexact="Sports")
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'store/category_products.html', {'category': category, 'products': products})

def home_appliances(request):
    category = get_object_or_404(Category, category_name__iexact="Home Appliances")
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'store/category_products.html', {'category': category, 'products': products})

def personal_care(request):
    category = get_object_or_404(Category, category_name__iexact="Personal Care")
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'store/category_products.html', {'category': category, 'products': products})

def light_beauty(request):
    category = get_object_or_404(Category, category_name__iexact="Light & Beauty")
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'store/category_products.html', {'category': category, 'products': products})


# ==================== ADD TO CART ====================
def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)

    # Simple session cart
    cart = request.session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart

    return redirect('store')
