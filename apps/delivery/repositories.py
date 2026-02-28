from .models import DeliveryZone


def get_active_zones():
    return DeliveryZone.objects.filter(is_active=True)


def get_zone_by_id(zone_id):
    try:
        return DeliveryZone.objects.get(id=zone_id, is_active=True)
    except DeliveryZone.DoesNotExist:
        return None
