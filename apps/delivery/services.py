from decimal import Decimal

from . import repositories


def calculate_fee(zone_id, cart_items):
    """
    cart_items: iterable of objects with .product.weight_kg and .quantity
    Returns dict with delivery_fee, total_weight_kg, zone.
    """
    zone = repositories.get_zone_by_id(zone_id)
    if not zone:
        raise ValueError(f'Delivery zone {zone_id} not found or inactive.')

    total_weight = sum(
        Decimal(str(item.product.weight_kg)) * item.quantity
        for item in cart_items
    )
    fee = zone.base_fee + (total_weight * zone.per_kg_rate)

    return {
        'delivery_fee': fee.quantize(Decimal('0.01')),
        'total_weight_kg': total_weight,
        'zone': zone,
    }
