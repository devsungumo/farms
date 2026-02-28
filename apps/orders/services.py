import logging
from decimal import Decimal

from apps.cart import repositories as cart_repo
from apps.cart import services as cart_services
from apps.delivery import services as delivery_services
from .models import Order, OrderItem
from . import repositories

logger = logging.getLogger(__name__)

_VALID_TRANSITIONS = {
    Order.STATUS_PENDING:    [Order.STATUS_PAID, Order.STATUS_CANCELLED],
    Order.STATUS_PAID:       [Order.STATUS_PROCESSING, Order.STATUS_REFUNDED],
    Order.STATUS_PROCESSING: [Order.STATUS_DISPATCHED, Order.STATUS_CANCELLED],
    Order.STATUS_DISPATCHED: [Order.STATUS_DELIVERED],
    Order.STATUS_DELIVERED:  [Order.STATUS_REFUNDED],
    Order.STATUS_CANCELLED:  [],
    Order.STATUS_REFUNDED:   [],
}


def _transition(order, new_status):
    allowed = _VALID_TRANSITIONS.get(order.status, [])
    if new_status not in allowed:
        raise ValueError(f'Cannot transition order from "{order.status}" to "{new_status}".')
    repositories.update_status(order, new_status)
    logger.info('Order %s: %s → %s', order.public_id, order.status, new_status)
    return order


def create_order(user, request, zone_id, delivery_address, notes=''):
    cart = cart_services.get_cart(request)
    items = list(cart_repo.get_cart_items(cart))
    if not items:
        raise ValueError('Cart is empty.')

    delivery_info = delivery_services.calculate_fee(zone_id, items)
    subtotal = sum(Decimal(str(i.product.price)) * i.quantity for i in items)
    delivery_fee = delivery_info['delivery_fee']
    total = subtotal + delivery_fee

    order = repositories.create_order(
        user=user,
        delivery_zone=delivery_info['zone'],
        delivery_fee=delivery_fee,
        subtotal=subtotal,
        total=total,
        delivery_address=delivery_address,
        notes=notes,
    )

    order_items = [
        OrderItem(
            order=order,
            product=item.product,
            product_name=item.product.name,
            product_price=item.product.price,
            product_unit=item.product.unit,
            product_weight_kg=item.product.weight_kg,
            quantity=item.quantity,
            line_total=Decimal(str(item.product.price)) * item.quantity,
        )
        for item in items
    ]
    repositories.bulk_create_items(order_items)
    cart_services.clear_cart(request)
    return order


def mark_paid(order):
    return _transition(order, Order.STATUS_PAID)


def mark_processing(order):
    return _transition(order, Order.STATUS_PROCESSING)


def mark_dispatched(order):
    return _transition(order, Order.STATUS_DISPATCHED)


def mark_delivered(order):
    return _transition(order, Order.STATUS_DELIVERED)


def cancel_order(order):
    return _transition(order, Order.STATUS_CANCELLED)


def refund_order(order):
    return _transition(order, Order.STATUS_REFUNDED)
