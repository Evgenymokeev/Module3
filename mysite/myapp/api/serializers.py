from rest_framework import serializers

from myapp.models import Product, Purchase, Return,User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response



class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price','quantity_in_stock']

class ProductDetailSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']




class PurchaseSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    product = ProductListSerializer()

    class Meta:
        model = Purchase
        fields = '__all__'


class ReturnSerializer(serializers.ModelSerializer):
    purchase = PurchaseSerializer()

    class Meta:
        model = Return
        fields = '__all__'


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk
        })
