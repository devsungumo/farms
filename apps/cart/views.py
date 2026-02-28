from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.responses import ApiResponse

from . import services
from .serializers import CartSerializer


class CartView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cart = services.get_cart(request)
        serializer = CartSerializer(cart, context={'request': request})
        return ApiResponse.success(serializer.data)

    def delete(self, request):
        services.clear_cart(request)
        return ApiResponse.success({'detail': 'Cart cleared.'})


class CartItemView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        if not product_id:
            return ApiResponse.error('validation_error', 'product_id is required.')
        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except (ValueError, TypeError):
            return ApiResponse.error('validation_error', 'quantity must be a positive integer.')
        try:
            services.add_to_cart(request, product_id, quantity)
        except ValueError as exc:
            return ApiResponse.error('add_failed', str(exc))
        cart = services.get_cart(request)
        return ApiResponse.success(CartSerializer(cart, context={'request': request}).data)


class CartItemDetailView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, item_id):
        quantity = request.data.get('quantity')
        if quantity is None:
            return ApiResponse.error('validation_error', 'quantity is required.')
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return ApiResponse.error('validation_error', 'quantity must be an integer.')
        try:
            services.update_item(request, item_id, quantity)
        except ValueError as exc:
            return ApiResponse.error('update_failed', str(exc))
        cart = services.get_cart(request)
        return ApiResponse.success(CartSerializer(cart, context={'request': request}).data)

    def delete(self, request, item_id):
        try:
            services.remove_item(request, item_id)
        except ValueError as exc:
            return ApiResponse.error('remove_failed', str(exc))
        cart = services.get_cart(request)
        return ApiResponse.success(CartSerializer(cart, context={'request': request}).data)


class CartMergeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_key = request.data.get('session_key')
        if not session_key:
            return ApiResponse.error('validation_error', 'session_key is required.')
        services.merge_carts(session_key, request.user)
        cart = services.get_cart(request)
        return ApiResponse.success(CartSerializer(cart, context={'request': request}).data)
