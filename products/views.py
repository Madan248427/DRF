from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer

# in views.py
class ProductList(APIView):
    def get(self, request):
        category = request.GET.get('category')
        products = Product.objects.filter(is_active=True)
        if category:
            products = products.filter(category=category)
        
        # 👇 Pass request context here
        serializer = ProductSerializer(products, many=True, context={'request': request})
        
        return Response(serializer.data)

