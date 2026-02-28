from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.products.models import Product
from .models import StockRecord


@receiver(post_save, sender=Product)
def create_stock_record(sender, instance, created, **kwargs):
    if created:
        StockRecord.objects.get_or_create(product=instance, defaults={'quantity': 0})
