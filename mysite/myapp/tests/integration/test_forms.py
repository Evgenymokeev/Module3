from django.test import TestCase
from myapp.models import Product,Purchase, Return,User

from myapp.forms import ProductForm,UserCreationForm,PurchaseForm,ReturnRequestForm

class ProductFormTest(TestCase):
    def test_create_product(self):
        form_data = {
            'name': 'Test Product',
            'price': 100.0,
            'description': 'Test Description',
            'quantity_in_stock': 10,
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.first().name, 'Test Product')

    def test_invalid_price(self):
        form_data = {
            'name': 'Invalid Product',
            'price': -100.0,
            'description': 'Invalid Description',
            'quantity_in_stock': 5,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

class UserCreationFormTest(TestCase):
    def test_valid_user_creation(self):
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "securepassword123",
            "password2": "securepassword123"
        }
        form = UserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "securepassword123",
            "password2": "wrongpassword"
        }
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_missing_password(self):
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "",
            "password2": ""
        }
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

class PurchaseFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="buyer", email="buyer@example.com", wallet=50)
        self.product = Product.objects.create(name="Laptop", price=20, quantity_in_stock=5)

    def test_valid_purchase(self):
        form_data = {"quantity": 2}
        form = PurchaseForm(data=form_data, product=self.product, user=self.user)
        self.assertTrue(form.is_valid())

    def test_purchase_exceeds_stock(self):
        form_data = {"quantity": 10}
        form = PurchaseForm(data=form_data, product=self.product, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)

    def test_purchase_insufficient_wallet(self):
        form_data = {"quantity": 3}
        form = PurchaseForm(data=form_data, product=self.product, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)

class ReturnRequestFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="buyer", email="buyer@example.com", wallet=100)
        self.product = Product.objects.create(name="Zara", price=20, quantity_in_stock=5)
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=2)

    def test_valid_return(self):
        form_data = {"purchase": self.purchase.id, "quantity": 1}
        form = ReturnRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_return_exceeds_purchase(self):
        form_data = {"purchase": self.purchase.id, "quantity": 5}
        form = ReturnRequestForm(data=form_data)
        self.assertFalse(form.is_valid())