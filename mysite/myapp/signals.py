from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Purchase, Product

@receiver(post_save, sender=Purchase)
def update_stock_on_purchase(sender, instance, created, **kwargs):
    if created:
        try:
            instance.product.reduce_stock(instance.quantity)
        except ValueError as e:
            raise ValueError(str(e))
