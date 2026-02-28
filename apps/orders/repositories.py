from .models import Order, OrderItem


def create_order(user, delivery_zone, delivery_fee, subtotal, total, delivery_address, notes=''):
    return Order.objects.create(
        user=user,
        delivery_zone=delivery_zone,
        delivery_fee=delivery_fee,
        subtotal=subtotal,
        total=total,
        delivery_address=delivery_address,
        notes=notes,
        status=Order.STATUS_PENDING,
    )


def bulk_create_items(items_data):
    OrderItem.objects.bulk_create(items_data)


def get_order_by_public_id(public_id):
    try:
        return Order.objects.select_related('user', 'delivery_zone').prefetch_related('items').get(public_id=public_id)
    except Order.DoesNotExist:
        return None


def get_orders_for_user(user):
    return Order.objects.filter(user=user).select_related('delivery_zone')


def update_status(order, status):
    order.status = status
    order.save(update_fields=['status', 'updated_at'])
    return order


def set_paystack_reference(order, reference):
    order.paystack_reference = reference
    order.save(update_fields=['paystack_reference', 'updated_at'])
    return order


def get_order_by_reference(reference):
    try:
        return Order.objects.prefetch_related('items__product').get(paystack_reference=reference)
    except Order.DoesNotExist:
        return None
