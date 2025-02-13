from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Purchase, Product
from django.db import transaction
from django.conf import settings
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=Purchase)
def update_stock_on_purchase(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            try:
                instance.product.reduce_stock(instance.quantity)
            except ValueError as e:
                raise ValueError(str(e))

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)