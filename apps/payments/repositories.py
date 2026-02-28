from .models import PaymentRecord


def create_record(order, reference, amount):
    return PaymentRecord.objects.create(
        order=order,
        reference=reference,
        amount=amount,
        status=PaymentRecord.STATUS_PENDING,
    )


def get_by_reference(reference):
    try:
        return PaymentRecord.objects.select_related('order').get(reference=reference)
    except PaymentRecord.DoesNotExist:
        return None


def update_record(record, status, raw_response):
    record.status = status
    record.raw_response = raw_response
    record.save(update_fields=['status', 'raw_response', 'updated_at'])
    return record
