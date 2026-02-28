from rest_framework import serializers

from apps.delivery.serializers import DeliveryZoneSerializer

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_price', 'product_unit', 'quantity', 'line_total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_zone = DeliveryZoneSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'public_id', 'status', 'delivery_zone', 'delivery_address',
            'delivery_fee', 'subtotal', 'total', 'notes',
            'paystack_reference', 'items', 'created_at', 'updated_at',
        ]


class CreateOrderSerializer(serializers.Serializer):
    zone_id = serializers.IntegerField()
    delivery_address = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True, default='')
