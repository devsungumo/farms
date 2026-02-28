from django.db import models
from django.utils.text import slugify


class DeliveryZone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    base_fee = models.DecimalField(max_digits=8, decimal_places=2)
    per_kg_rate = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
