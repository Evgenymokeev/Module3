from django.test import TestCase
from myapp.models import User,Product,Purchase,Return
from django.utils.timezone import now
from django.core.exceptions import ValidationError

class UserWalletTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password", wallet=100)

    def test_wallet_update_positive(self):
        self.user.update_wallet(50)
        self.assertEqual(self.user.wallet, 150)

    def test_wallet_update_negative(self):
        self.user.update_wallet(-30)
        self.assertEqual(self.user.wallet, 70)

    def test_wallet_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.user.update_wallet(-200)

class ProductStockTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Test Product", price=50, quantity_in_stock=10)

    def test_reduce_stock_valid(self):
        self.product.reduce_stock(3)
        self.assertEqual(self.product.quantity_in_stock, 7)

    def test_reduce_stock_insufficient(self):
        with self.assertRaises(ValueError):
            self.product.reduce_stock(15)

    def test_increase_stock_on_return(self):
        self.product.reduce_stock(3)
        self.product.reduce_stock(3, is_return=True)
        self.assertEqual(self.product.quantity_in_stock, 10)


class PurchaseTest(TestCase):
    class PurchaseTestCase(TestCase):
        def setUp(self):
            self.user = User.objects.create(username='testuser', wallet=100)
            self.product = Product.objects.create(name='Test Product', price=50, quantity_in_stock=5)

        def test_purchase_insufficient_funds(self):
            self.user.wallet = 40
            self.user.save()

            with self.assertRaises(ValueError, msg="Недостаточно средств для завершения покупки."):
                Purchase.objects.create(user=self.user, product=self.product, quantity=2)

        def test_purchase_insufficient_stock(self):
            with self.assertRaises(ValueError, msg="Недостаточно товара на складе."):
                Purchase.objects.create(user=self.user, product=self.product, quantity=10)

class ReturnTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="returner", email="returner@example.com", password="password", wallet=500)
        self.product = Product.objects.create(name="Phone", price=100, quantity_in_stock=10)
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=2, created_at=now())

    def test_successful_return(self):
        return_request = Return.objects.create(user=self.user, product=self.product, quantity=1, purchase=self.purchase)

        self.user.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(self.user.wallet, 500)
        self.assertEqual(self.product.quantity_in_stock, 10)

    def test_return_exceeds_purchase(self):
        return_request = Return(user=self.user, product=self.product, quantity=3, purchase=self.purchase)

        with self.assertRaises(ValidationError):
            return_request.full_clean()
