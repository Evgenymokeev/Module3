
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.urls import reverse

class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=10000)
    avatar = models.ImageField(blank=True, null=True, upload_to='avatars/')

    def __str__(self):
        return self.username




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

    def save(self, *args, **kwargs):
        if self.quantity_in_stock < 0:
            self.quantity_in_stock = 0
        super().save(*args, **kwargs)

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.quantity > self.product.quantity_in_stock:
                raise ValueError("Not enough stock for this purchase.")
            self.product.reduce_stock(self.quantity)
        super().save(*args, **kwargs)


class Return(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE,null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return request by {self.purchase.user.username} for {self.purchase.product.name}"

    class Meta:
        verbose_name_plural = "Returns"











