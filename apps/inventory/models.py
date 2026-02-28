from django.db import models


class StockRecord(models.Model):
    product = models.OneToOneField(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='stock_record',
    )
    quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.product.name} — {self.quantity}'


class StockMovement(models.Model):
    REASON_MANUAL = 'manual'
    REASON_ORDER = 'order'
    REASON_ORDER_CANCELLED = 'order_cancelled'
    REASON_RESTOCK = 'restock'
    REASON_CHOICES = [
        (REASON_MANUAL, 'Manual Adjustment'),
        (REASON_ORDER, 'Order Fulfilled'),
        (REASON_ORDER_CANCELLED, 'Order Cancelled'),
        (REASON_RESTOCK, 'Restock'),
    ]

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='stock_movements',
    )
    delta = models.IntegerField(help_text='Positive = added, negative = removed')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.delta >= 0 else ''
        return f'{self.product.name}: {sign}{self.delta} ({self.reason})'
