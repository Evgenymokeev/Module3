from django.test import TestCase
from myapp.forms import UserCreationForm,PurchaseForm,ProductForm,ReturnProduct,ReturnRequestForm
from myapp.models import User,Product, Purchase, Return

class UserCreationFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            "username": "testuser",
            "password1": "StrongPassword123",
            "password2": "StrongPassword123",
        }
        form = UserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_passwords_mismatch(self):
        form_data = {
            "username": "testuser",
            "password1": "StrongPassword123",
            "password2": "WrongPassword",
        }
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_user_saved_correctly(self):
        form_data = {
            "username": "testuser",
            "password1": "StrongPassword123",
            "password2": "StrongPassword123",
        }
        form = UserCreationForm(data=form_data)
        if form.is_valid():
            user = form.save()
            self.assertIsInstance(user, User)
            self.assertTrue(user.check_password("StrongPassword123"))

class PurchaseFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password", wallet=500)
        self.product = Product.objects.create(name="Test Product", price=100, quantity_in_stock=5)

    def test_valid_purchase(self):
        form = PurchaseForm(data={"quantity": 3}, product=self.product, user=self.user)
        self.assertTrue(form.is_valid())

    def test_insufficient_stock(self):
        form = PurchaseForm(data={"quantity": 10}, product=self.product, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)

    def test_insufficient_funds(self):
        self.user.wallet = 100
        self.user.save()
        form = PurchaseForm(data={"quantity": 2}, product=self.product, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)

class ProductFormTest(TestCase):
    def test_valid_product_form(self):
        form_data = {
            "name": "Valid Product",
            "price": 100,
            "description": "A valid product description.",
            "quantity_in_stock": 10,
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_negative_price(self):
        form_data = {
            "name": "Invalid Product",
            "price": -10,
            "description": "A valid product description.",
            "quantity_in_stock": 10,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_empty_name(self):
        form_data = {
            "name": "",
            "price": 100,
            "description": "A valid product description.",
            "quantity_in_stock": 10,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

class ReturnProductFormTest(TestCase):
    def test_valid_return_request(self):
        form = ReturnProduct(data={"quantity": 2})
        self.assertTrue(form.is_valid())

    def test_return_zero_quantity(self):
        form = ReturnProduct(data={"quantity": 0})
        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)

    def test_return_negative_quantity(self):
        form = ReturnProduct(data={"quantity": -3})
        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)

class ReturnRequestFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password", email="test@example.com")
        self.product = Product.objects.create(name="Test Product", price=100, quantity_in_stock=5)
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=1)

    def test_valid_return_request(self):
        form = ReturnRequestForm(data={"purchase": self.purchase.id})
        self.assertTrue(form.is_valid())

    def test_return_without_purchase(self):
        form = ReturnRequestForm(data={"purchase": None})
        self.assertFalse(form.is_valid())
        self.assertIn("purchase", form.errors)