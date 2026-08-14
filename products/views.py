from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def product_detail(request, category_slug, slug):
    product = get_object_or_404(Product, category__slug=category_slug, slug=slug)
    return render(request, 'products/detail.html', {'product': product})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    return render(request, 'products/category.html', {'category': category, 'products': products})
