import logging

from apps.products import repositories as product_repo
from . import repositories

logger = logging.getLogger(__name__)


def adjust_stock(product_id, delta, reason, note=''):
    record = repositories.get_or_create_stock_record(product_id)
    previous_quantity = record.quantity
    new_quantity = max(0, previous_quantity + delta)

    repositories.update_quantity(record, new_quantity)
    repositories.create_movement(product_id, delta, reason, note)

    if new_quantity == 0:
        product_repo.set_availability(product_id, False)
    elif previous_quantity == 0 and new_quantity > 0:
        product_repo.set_availability(product_id, True)

    logger.info(
        'Stock adjusted: product=%s delta=%s reason=%s qty=%s→%s',
        product_id, delta, reason, previous_quantity, new_quantity,
    )
    return record
