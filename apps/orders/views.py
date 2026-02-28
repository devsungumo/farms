from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.pagination import StandardPagination
from apps.core.responses import ApiResponse

from . import repositories, services
from .serializers import CreateOrderSerializer, OrderSerializer


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = repositories.get_orders_for_user(request.user)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(orders, request)
        serializer = OrderSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.error('validation_error', 'Invalid input.', details=serializer.errors)
        try:
            order = services.create_order(
                user=request.user,
                request=request,
                zone_id=serializer.validated_data['zone_id'],
                delivery_address=serializer.validated_data['delivery_address'],
                notes=serializer.validated_data.get('notes', ''),
            )
        except ValueError as exc:
            return ApiResponse.error('order_failed', str(exc))
        return ApiResponse.created(OrderSerializer(order, context={'request': request}).data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, public_id):
        order = repositories.get_order_by_public_id(public_id)
        if not order or order.user != request.user:
            return ApiResponse.not_found('Order not found.')
        serializer = OrderSerializer(order, context={'request': request})
        return ApiResponse.success(serializer.data)


class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, public_id):
        order = repositories.get_order_by_public_id(public_id)
        if not order or order.user != request.user:
            return ApiResponse.not_found('Order not found.')
        try:
            services.cancel_order(order)
        except ValueError as exc:
            return ApiResponse.error('cancel_failed', str(exc))
        return ApiResponse.success(OrderSerializer(order, context={'request': request}).data)
