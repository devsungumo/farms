from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.cart import services as cart_services
from apps.cart import repositories as cart_repo
from apps.core.responses import ApiResponse

from . import repositories, services
from .serializers import DeliveryZoneSerializer


class DeliveryZoneListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        zones = repositories.get_active_zones()
        serializer = DeliveryZoneSerializer(zones, many=True, context={'request': request})
        return ApiResponse.success(serializer.data)


class DeliveryFeeEstimateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        zone_id = request.data.get('zone_id')
        if not zone_id:
            return ApiResponse.error('validation_error', 'zone_id is required.')

        try:
            cart = cart_services.get_cart(request)
            items = list(cart_repo.get_cart_items(cart))
            if not items:
                return ApiResponse.error('empty_cart', 'Cart is empty.')
            result = services.calculate_fee(zone_id, items)
        except ValueError as exc:
            return ApiResponse.error('invalid_zone', str(exc))

        return ApiResponse.success({
            'zone': DeliveryZoneSerializer(result['zone']).data,
            'total_weight_kg': str(result['total_weight_kg']),
            'delivery_fee': str(result['delivery_fee']),
        })
