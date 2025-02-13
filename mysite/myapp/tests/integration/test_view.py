from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from myapp.models import User, Product,Purchase,Return
from django.contrib.messages import get_messages
from django.utils.timezone import now
from datetime import timedelta


class UserRegistrationTest(TestCase):
    def test_user_registration_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        })
        self.assertRedirects(response, reverse('profile'))
        user = get_user_model().objects.get(username='testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('TestPassword123'))

    def test_user_registration_failure(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'TestPassword123',
            'password2': 'DifferentPassword123',
        })

        form = response.context['form']

        self.assertTrue(form.errors)

        self.assertEqual(form.errors['password2'], ["The two password fields didn't match."])

class ProductPurchaseTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', email='test@example.com', password='TestPassword123')
        self.product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        self.client.login(username='testuser', password='TestPassword123')

    def test_successful_purchase(self):
        response = self.client.post(reverse('product_detail', kwargs={'pk': self.product.id}), {'quantity': 2})
        self.product.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(self.product.quantity_in_stock, 8)
        self.assertEqual(self.user.wallet, 9800)
        self.assertRedirects(response, reverse('profile'))

    def test_insufficient_funds(self):
        self.user.wallet = 150
        self.user.save()

        # Активируем сессию вручную
        session = self.client.session
        session.save()

        response = self.client.post(
            reverse('product_detail', kwargs={'pk': self.product.id}),
            {'quantity': 2},
            follow=True
        )

        messages = list(get_messages(response.wsgi_request))


        self.assertIn('Произошла ошибка при оформлении покупки.', [msg.message for msg in messages])

    def test_insufficient_stock(self):
        response = self.client.post(reverse('product_detail', kwargs={'pk': self.product.id}), {'quantity': 20},
                                    follow=True)

        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Произошла ошибка при оформлении покупки.', [msg.message for msg in messages])


class ProductReturnTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', email='test@example.com', password='TestPassword123')
        self.product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        self.purchase = Purchase.objects.create(user=self.user, product=self.product, quantity=2)
        self.client.login(username='testuser', password='TestPassword123')

    def test_successful_return_within_time(self):
        self.purchase.created_at = now() - timedelta(minutes=2)
        self.purchase.save()
        response = self.client.post(reverse('return_purchase', kwargs={'purchase_id': self.purchase.id}))
        self.assertRedirects(response, reverse('profile'))
        self.purchase.refresh_from_db()  # Обновить объект из базы данных
        self.assertEqual(Return.objects.count(), 1)
        self.assertEqual(self.purchase.returned, True)


    def test_already_returned_product(self):
        self.purchase.returned = True
        self.purchase.save()
        response = self.client.post(reverse('return_purchase', kwargs={'purchase_id': self.purchase.id}))

        self.assertRedirects(response, reverse('profile'))

        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Этот товар уже был возвращен.")


def test_return_outside_time_limit(self):
    self.purchase.created_at = now() - timedelta(minutes=10)
    self.purchase.save()

    response = self.client.post(reverse('return_purchase', kwargs={'purchase_id': self.purchase.id}))

    self.assertRedirects(response, reverse('profile'))

    profile_response = self.client.get(reverse('profile'))

    self.assertContains(profile_response, "Возврат невозможен, так как прошло более 3 минут с момента покупки.")


class ReturnListViewTest(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(username='admin', email='admin@example.com', password='adminpassword')
        self.normal_user = get_user_model().objects.create_user(username='user', email='user@example.com', password='userpassword')
        self.product = Product.objects.create(name='Test Product', price=100, quantity_in_stock=10)
        self.purchase = Purchase.objects.create(user=self.normal_user, product=self.product, quantity=2)
        self.purchase.returned = True
        self.purchase.save()
        self.client.login(username='admin', password='adminpassword')

    def test_return_list_view(self):
        return_request = Return.objects.create(user=self.normal_user, product=self.product, quantity=1,
                                               purchase=self.purchase)

        response = self.client.get(reverse('return_list'))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.purchase.product.name)

    def test_non_admin_cannot_view_return_list(self):
        self.client.login(username='user', password='userpassword')
        response = self.client.get(reverse('return_list'))
        self.assertEqual(response.status_code, 403)

    def test_approve_return(self):
        return_request = Return.objects.create(user=self.normal_user, product=self.product, quantity=1,
                                               purchase=self.purchase)
        response = self.client.post(reverse('return_list'), {'return_id': return_request.id, 'action': 'approve'})

        self.product.refresh_from_db()

        self.assertRedirects(response, reverse('return_list'))

        self.assertEqual(self.product.quantity_in_stock, 11)

        self.assertEqual(self.normal_user.wallet, 10000)

