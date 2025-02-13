from django.test import TestCase
from myapp.models import Product, User, Purchase, Return

class UserTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')

    def test_wallet_update(self):
        self.user.update_wallet(500)
        self.assertEqual(self.user.wallet, 10500)

        self.user.update_wallet(-500)
        self.assertEqual(self.user.wallet, 10000)

        with self.assertRaises(ValueError):
            self.user.update_wallet(-20000)

class ProductTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')

    def test_reduce_stock_on_purchase(self):
        self.product.reduce_stock(2)
        self.assertEqual(self.product.quantity_in_stock, 8)

    def test_increase_stock_on_return(self):
        self.product.reduce_stock(2)
        self.product.reduce_stock(1, is_return=True)
        self.assertEqual(self.product.quantity_in_stock, 9)

class PurchaseTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.user.wallet = 1000
        self.user.save()

    def test_valid_purchase(self):
        purchase = Purchase(user=self.user, product=self.product, quantity=5)
        purchase.validate_purchase()
        self.assertEqual(purchase.user.wallet, 500)

    def test_invalid_purchase_insufficient_stock(self):
        purchase = Purchase(user=self.user, product=self.product, quantity=15)
        with self.assertRaises(ValueError):
            purchase.validate_purchase()

    def test_invalid_purchase_insufficient_funds(self):
        self.user.wallet = 400
        self.user.save()
        purchase = Purchase(user=self.user, product=self.product, quantity=5)
        with self.assertRaises(ValueError):
            purchase.validate_purchase()


class ReturnTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=5)

    def test_valid_return(self):
        return_request = Return(user=self.user, product=self.product, quantity=2, purchase=self.purchase)
        return_request.clean()

    def test_invalid_return_exceeds_purchase_quantity(self):
        return_request = Return(user=self.user, product=self.product, quantity=6, purchase=self.purchase)
        with self.assertRaises(ValueError):
            return_request.clean()

class PurchaseTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')

    def test_get_total_price(self):
        purchase = Purchase(user=self.user, product=self.product, quantity=3)
        total_price = purchase.get_total_price()
        self.assertEqual(total_price, 300)