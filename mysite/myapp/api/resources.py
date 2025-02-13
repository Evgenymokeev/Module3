from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .permission import IsOwnerOrReadOnly
from .serializers import ProductListSerializer,PurchaseSerializer,ReturnSerializer,ProductDetailSerializer
from myapp.models import Product, Purchase, Return
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class  PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = (IsAuthenticatedOrReadOnly)

    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ReturnViewSet(viewsets.ModelViewSet):
    queryset = Return.objects.all()
    serializer_class = ReturnSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)



