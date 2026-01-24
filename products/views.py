from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.http import JsonResponse


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related('images'),
        slug=slug,
        is_active=True
    )

    # 🔄 AJAX request: return stock only
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'stock': product.stock,
            'is_active': product.is_active
        })

    images = product.images.all()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'images': images
    })
