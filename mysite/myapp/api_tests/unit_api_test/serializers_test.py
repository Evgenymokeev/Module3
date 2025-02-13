from rest_framework.test import APITestCase
from myapp.models import Product,User, Purchase,Return
from myapp.serializers import ProductListSerializer,ProductDetailSerializer, UserSerializer,PurchaseSerializer
from myapp.serializers import ReturnSerializer


class ProductListSerializerTest(APITestCase):

    def setUp(self):
        self.product = Product.objects.create(name="Gucci", price=100.00, quantity_in_stock=10)

    def test_product_list_serializer(self):
        serializer = ProductListSerializer(self.product)
        data = serializer.data
        self.assertEqual(data['name'], 'Gucci')
        self.assertEqual(data['price'], '1000.00')
        self.assertEqual(data['quantity_in_stock'], 10)

class ProductDetailSerializerTest(APITestCase):

    def setUp(self):
        self.product = Product.objects.create(name="Gucci", price=1000.00, quantity_in_stock=10, description="A great phone.")

    def test_product_detail_serializer(self):
        serializer = ProductDetailSerializer(self.product)
        data = serializer.data
        self.assertEqual(data['name'], 'Gucci')
        self.assertEqual(data['price'], '1000.00')
        self.assertEqual(data['quantity_in_stock'], 10)
        self.assertEqual(data['description'], 'A great Gucci.')

class UserSerializerTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password")

    def test_user_serializer(self):
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')

class PurchaseSerializerTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="buyer", email="buyer@example.com", password="password", wallet=500)
        self.product = Product.objects.create(name="Gucci", price=1000.00, quantity_in_stock=10)
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=2)

    def test_purchase_serializer(self):
        serializer = PurchaseSerializer(self.purchase)
        data = serializer.data
        self.assertEqual(data['user']['username'], 'buyer')
        self.assertEqual(data['product']['name'], 'Gucci')
        self.assertEqual(data['quantity'], 2)

class ReturnSerializerTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="returner", email="returner@example.com", password="password", wallet=10000)
        self.product = Product.objects.create(name="Zara", price=1000.00, quantity_in_stock=10)
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=2)
        self.return_request = Return.objects.create(user=self.user, product=self.product, quantity=1, purchase=self.purchase)

    def test_return_serializer(self):
        serializer = ReturnSerializer(self.return_request)
        data = serializer.data
        self.assertEqual(data['purchase']['user']['username'], 'returner')
        self.assertEqual(data['purchase']['product']['name'], 'Zara')
        self.assertEqual(data['quantity'], 1)

class PurchaseSerializerValidationTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="buyer", email="buyer@example.com", password="password", wallet=10000)
        self.product = Product.objects.create(name="Zara", price=1000.00, quantity_in_stock=2)

    def test_invalid_purchase_quantity(self):
        data = {'user': self.user.id, 'product': self.product.id, 'quantity': 3}
        serializer = PurchaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_insufficient_funds(self):
        data = {'user': self.user.id, 'product': self.product.id, 'quantity': 10}
        serializer = PurchaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
