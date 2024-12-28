
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(blank=True, null=True, upload_to='avatars/')

    def __str__(self):
        return self.username


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/products/{self.id}"

    def get_add_to_cart_url(self):
        return f"/add-to-cart/{self.id}"

    def get_remove_from_cart_url(self):
        return f"/remove-from-cart/{self.id}"

    def get_image_url(self):
        return self.image.url if self.image else ""

    def get_price_display(self):
        return f"{self.price} BDT"

    def get_short_description(self):
        return f"{self.description[:100]}..." if self.description else ""


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.product.price


class Return(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.product.price

    class Meta:
        verbose_name_plural = "Returns"








