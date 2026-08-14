from django.shortcuts import render
from products.models import Product

def index(models_request):
    # Fetch the 8 newest products to display on the storefront
    products = Product.objects.all()[:8]
    return render(models_request, 'core/index.html', {'products': products})
