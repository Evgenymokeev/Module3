from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from myapp.models import User, Product, Purchase, Return

class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.product = Product.objects.create(name="Test Product", price=100.0, quantity_in_stock=10)
        self.client = APIClient()
        self.client.login(username='testuser', password='password123')

    def test_list_products(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Product', str(response.data))

    def test_create_product(self):
        data = {
            'name': 'New Product',
            'price': 150.0,
            'quantity_in_stock': 5
        }
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_update_product(self):
        data = {'price': 120.0}
        response = self.client.patch(f'/api/products/{self.product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 120.0)

    def test_delete_product(self):
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)


class PurchaseViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.product = Product.objects.create(name="Test Product", price=100.0, quantity_in_stock=10)
        self.client = APIClient()
        self.client.login(username='testuser', password='password123')

    def test_create_purchase(self):
        data = {
            'user': self.user.id,
            'product': self.product.id,
            'quantity': 2
        }
        response = self.client.post('/api/purchases/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Purchase.objects.count(), 1)

    def test_insufficient_stock(self):
        data = {'user': self.user.id, 'product': self.product.id, 'quantity': 20}
        response = self.client.post('/api/purchases/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ReturnViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.product = Product.objects.create(name="Test Product", price=100.0, quantity_in_stock=10)
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=2)
        self.client = APIClient()
        self.client.login(username='testuser', password='password123')

    def test_create_return(self):
        data = {
            'user': self.user.id,
            'product': self.product.id,
            'quantity': 1,
            'purchase': self.purchase.id
        }
        response = self.client.post('/api/returns/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Return.objects.count(), 1)

    def test_return_exceeds_purchase(self):
        data = {'user': self.user.id, 'product': self.product.id, 'quantity': 3, 'purchase': self.purchase.id}
        response = self.client.post('/api/returns/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
