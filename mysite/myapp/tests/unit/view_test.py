from myapp.models import Product, Purchase, Return, User
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password',
                                                         email='test@example.com')
        self.client.login(username='testuser', password='password')
        self.product = Product.objects.create(name="Test Product", price=10.0, quantity_in_stock=100)

        self.purchase = Purchase.objects.create(user=self.user, product=self.product,
                                                created_at=timezone.now() - timedelta(minutes=40), quantity=1)

        self.return_obj = Return.objects.create(
            user=self.user,
            product=self.product,
            purchase=self.purchase,
            created_at=timezone.now() - timedelta(minutes=40),
            quantity=1)


    def test_profile_view_clears_old_data(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Purchase.objects.count(), 0)
        self.assertEqual(Return.objects.count(), 0)


class CustomLogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password',email='test@example.com')

    def test_logout_redirect(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('main'))


class ProductListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password',email='test@example.com')
        self.client.login(username='testuser', password='password')

    def test_product_list_view(self):
        product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')


class ProductDetailViewTest(TestCase):
    def test_product_detail_view(self):
        product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        response = self.client.get(reverse('product_detail', args=[product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')


class ReturnTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password',email='test@example.com')
        self.client.login(username='testuser', password='password')

        self.product = Product.objects.create(name="Test Product", price=100, quantity_in_stock=10)
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=1, created_at=timezone.now())

    def test_return_within_time(self):
        response = self.client.get(reverse('return_purchase', args=[self.purchase.id]))
        self.assertRedirects(response, reverse('profile'))
        self.assertTrue(Return.objects.filter(purchase=self.purchase).exists())

    def test_return_after_timeout(self):
        self.purchase.created_at = timezone.now() - timedelta(minutes=5)
        self.purchase.save()

        response = self.client.get(reverse('return_purchase', args=[self.purchase.id]))
        self.assertRedirects(response, reverse('profile'))
        self.assertFalse(Return.objects.filter(purchase=self.purchase).exists())

class UserRegisterViewTest(TestCase):
    def test_user_register(self):
        data = {'username': 'testuser', 'password1': 'password', 'password2': 'password'}
        response = self.client.post(reverse('register'), data)
        self.assertRedirects(response, reverse('profile'))
        self.assertTrue(get_user_model().objects.filter(username='testuser').exists())


class ProtectedPageAccessTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password',email='test@example.com')
        self.url = reverse('profile')

    def test_access_protected_page_logged_in(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_access_protected_page_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next=/profile/')

class ProtectedPageAccessTestNotLoggedIn(TestCase):
    def setUp(self):
        self.url = reverse('profile')

    def test_redirect_to_login_for_not_logged_in_users(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next=/profile/')


class ReturnActionTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password',email='test@example.com')
        self.client.login(username='testuser', password='password')

        self.product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=1)
        self.return_request = Return.objects.create(user=self.user, product=self.product, quantity=1, purchase=self.purchase)

    def test_approve_return(self):
        response = self.client.post(reverse('return_action'), {'return_id': self.return_request.id, 'action': 'approve'})
        self.assertRedirects(response, reverse('return_list'))


        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity_in_stock, 11)

        self.user.refresh_from_db()
        self.assertEqual(self.user.wallet, 100)

        self.assertFalse(Return.objects.filter(id=self.return_request.id).exists())

class ReturnActionRejectTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password',email='test@example.com')
        self.client.login(username='testuser', password='password')

        self.product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=1)
        self.return_request = Return.objects.create(user=self.user, product=self.product, quantity=1, purchase=self.purchase)

    def test_reject_return(self):
        response = self.client.post(reverse('return_action'), {'return_id': self.return_request.id, 'action': 'reject'})
        self.assertRedirects(response, reverse('return_list'))

        self.assertFalse(Return.objects.filter(id=self.return_request.id).exists())

class ReturnActionRejectQuantityTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password',email='test@example.com')
        self.client.login(username='testuser', password='password')


        self.product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=1)
        self.return_request = Return.objects.create(user=self.user, product=self.product, quantity=2, purchase=self.purchase)

    def test_reject_return_exceeds_quantity(self):
        response = self.client.post(reverse('return_action'), {'return_id': self.return_request.id, 'action': 'approve'})
        self.assertRedirects(response, reverse('return_list'))

        self.assertTrue(Return.objects.filter(id=self.return_request.id).exists())
        self.assertEqual(self.user.wallet, 0)

class ReturnActionRejectTooManyTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password',email='test@example.com')
        self.client.login(username='testuser', password='password')

        self.product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=1)
        self.return_request = Return.objects.create(user=self.user, product=self.product, quantity=2, purchase=self.purchase)

    def test_reject_return_exceeds_purchase(self):
        response = self.client.post(reverse('return_action'), {'return_id': self.return_request.id, 'action': 'approve'})
        self.assertRedirects(response, reverse('return_list'))

        self.assertTrue(Return.objects.filter(id=self.return_request.id).exists())
        self.assertEqual(self.product.quantity_in_stock, 10)