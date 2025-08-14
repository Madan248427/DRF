# products/utils.py
from .models import Product

def get_active_products(category=None):
    queryset = Product.objects.filter(is_active=True)
    if category:
        queryset = queryset.filter(category=category)
    return queryset
