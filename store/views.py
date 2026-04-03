from django.shortcuts import render, get_object_or_404, redirect
from category.models import Category
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Variation, ReviewRating


# ==================== HOME ====================
def home(request):
    products = Product.objects.filter(is_available=True)[:6]
    return render(request, 'home.html', {'products': products})


# ==================== STORE ====================
def store(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    else:
        category = None

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(category__category_name__icontains=query)
        )

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'category': category,
        'product_count': products.count(),
        'query': query,
    }
    return render(request, 'store/store.html', context)


# ==================== PRODUCT DETAIL ====================
def product_detail(request, category_slug, product_slug):
    product = get_object_or_404(
        Product,
        slug=product_slug,
        category__slug=category_slug
    )

    reviews = ReviewRating.objects.filter(
        product=product
    ).order_by('-created_at')

    sizes = getattr(product, 'sizes', ["Small", "Medium", "Large", "X-Large"])

    context = {
        'product': product,
        'single_product': product,
        'sizes': sizes,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)


# ==================== ADD REVIEW ====================
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST" and request.user.is_authenticated:
        rating = int(request.POST.get('rating', 0))
        review_text = request.POST.get('review', '')

        # Update if already reviewed
        if ReviewRating.objects.filter(product=product, user=request.user).exists():
            review = ReviewRating.objects.get(product=product, user=request.user)
            review.rating = rating
            review.review = review_text
            review.save()
        else:
            ReviewRating.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                review=review_text
            )

    return redirect(product.get_url())

# ==================== CATEGORY VIEW ====================
def category_view(request, category_slug):
    categories = Category.objects.all()
    category = get_object_or_404(Category, slug=category_slug)

    products = Product.objects.filter(
        category=category,
        is_available=True
    )

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'category': category,
        'products': page_obj,
        'page_obj': page_obj,
        'product_count': products.count(),
    }
    return render(request, 'store/category_products.html', context)


# ==================== SEARCH ====================
def search(request):
    query = request.GET.get('keyword', '')
    products = Product.objects.filter(
        product_name__icontains=query
    ) if query else Product.objects.none()

    return render(request, 'store/store.html', {
        'query': query,
        'products': products
    })


# ==================== CATEGORY SHORTCUTS ====================
def electronics(request):
    return category_view(request, "electronics")

def fashion(request):
    return category_view(request, "fashion")

def grocery(request):
    return category_view(request, "grocery")

def books(request):
    return category_view(request, "books")

def toys(request):
    return category_view(request, "toys")

def sports(request):
    return category_view(request, "sports")

def home_appliances(request):
    return category_view(request, "home-appliances")

def personal_care(request):
    return category_view(request, "personal-care")

def light_beauty(request):
    return category_view(request, "light-beauty")