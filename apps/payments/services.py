import hashlib
import hmac
import logging

import requests as http_client
from django.conf import settings

from apps.inventory.services import adjust_stock
from apps.inventory.models import StockMovement
from apps.orders import repositories as order_repo
from apps.orders import services as order_services
from .models import PaymentRecord
from . import repositories

logger = logging.getLogger(__name__)

PAYSTACK_BASE = 'https://api.paystack.co'


def _headers():
    return {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }


def initialize(order_id):
    order = order_repo.get_order_by_public_id(order_id)
    if not order:
        raise ValueError('Order not found.')
    if order.status != 'pending':
        raise ValueError('Order is not in pending state.')

    amount_kobo = int(order.total * 100)
    payload = {
        'email': order.user.email,
        'amount': amount_kobo,
    }
    response = http_client.post(f'{PAYSTACK_BASE}/transaction/initialize', json=payload, headers=_headers(), timeout=30)
    response.raise_for_status()
    data = response.json()['data']

    reference = data['reference']
    repositories.create_record(order, reference, order.total)
    order_repo.set_paystack_reference(order, reference)

    logger.info('Payment initialized: order=%s reference=%s', order.public_id, reference)
    return {'authorization_url': data['authorization_url'], 'reference': reference}


def verify(reference):
    record = repositories.get_by_reference(reference)
    if not record:
        raise ValueError('Payment record not found.')

    # Idempotency — already confirmed
    if record.status == PaymentRecord.STATUS_SUCCESS:
        logger.info('Payment already verified (idempotent): reference=%s', reference)
        return record

    response = http_client.get(f'{PAYSTACK_BASE}/transaction/verify/{reference}', headers=_headers(), timeout=30)
    response.raise_for_status()
    raw = response.json()
    paystack_status = raw.get('data', {}).get('status')

    if paystack_status == 'success':
        repositories.update_record(record, PaymentRecord.STATUS_SUCCESS, raw)
        order = record.order
        order_services.mark_paid(order)
        for item in order.items.all():
            if item.product_id:
                adjust_stock(item.product_id, -item.quantity, StockMovement.REASON_ORDER)
        logger.info('Payment verified: reference=%s order=%s', reference, order.public_id)
    else:
        repositories.update_record(record, PaymentRecord.STATUS_FAILED, raw)
        logger.warning('Payment failed: reference=%s status=%s', reference, paystack_status)

    return record


def handle_webhook(body, signature):
    secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
    expected = hmac.new(secret, body, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(expected, signature):
        logger.warning('Webhook signature mismatch.')
        return False

    import json
    payload = json.loads(body)
    event = payload.get('event')
    if event == 'charge.success':
        reference = payload['data']['reference']
        verify(reference)
    return True
