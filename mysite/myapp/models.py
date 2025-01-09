
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=10000)
    avatar = models.ImageField(blank=True, null=True, upload_to='avatars/')
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self):
        return self.username

    def update_wallet(self, amount):
        if self.wallet + amount < 0:
            raise ValueError("There are not enough funds in your wallet.")
        self.wallet += amount
        self.save()

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    quantity_in_stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.id})

    def reduce_stock(self, quantity):
        if self.quantity_in_stock >= quantity:
            self.quantity_in_stock -= quantity
            self.save()
        else:
            raise ValueError("Not enough stock.")


    def available_quantity(self):
        returned_quantity = Return.objects.filter(product=self).aggregate(total_returned=models.Sum('quantity'))[
                                'total_returned'] or 0
        return self.quantity_in_stock + int(returned_quantity)

    def save(self, *args, **kwargs):
        if self.quantity_in_stock < 0:
            self.quantity_in_stock = 0
        super().save(*args, **kwargs)

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    returned = models.BooleanField(default=False)

    def get_total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        if not self.pk:  # Только при создании
            if self.quantity > self.product.quantity_in_stock:
                raise ValueError("Not enough stock for this purchase.")
            self.product.reduce_stock(self.quantity)
        super().save(*args, **kwargs)

class Return(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return f"Return request by {self.purchase.user.username} for {self.purchase.product.name}"

    def get_total_refund(self):
        return self.quantity * self.product.price

    class Meta:
        verbose_name_plural = "Returns"











