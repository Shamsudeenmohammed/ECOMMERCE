from django.shortcuts import render
from products.models import Product, Category
from django.db.utils import OperationalError

def home_view(request):
    try:
        featured_products = Product.objects.filter(
            is_featured=True,
            is_active=True
        )[:8]

        categories = Category.objects.filter(
            is_active=True,
            parent__isnull=True
        )

    except OperationalError:
        featured_products = []
        categories = []

    return render(request, 'home.html', {
        'featured_products': featured_products,
        'categories': categories,
    })
