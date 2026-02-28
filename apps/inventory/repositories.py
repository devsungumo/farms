from .models import StockMovement, StockRecord


def get_or_create_stock_record(product_id):
    record, _ = StockRecord.objects.get_or_create(
        product_id=product_id,
        defaults={'quantity': 0},
    )
    return record


def update_quantity(stock_record, new_quantity):
    stock_record.quantity = new_quantity
    stock_record.save(update_fields=['quantity', 'updated_at'])
    return stock_record


def create_movement(product_id, delta, reason, note=''):
    return StockMovement.objects.create(
        product_id=product_id,
        delta=delta,
        reason=reason,
        note=note,
    )


def get_movements(product_id=None):
    qs = StockMovement.objects.select_related('product')
    if product_id:
        qs = qs.filter(product_id=product_id)
    return qs
