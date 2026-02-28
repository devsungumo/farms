from rest_framework import serializers

from .models import PaymentRecord


class PaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecord
        fields = ['public_id', 'reference', 'amount', 'status', 'provider', 'created_at']


class InitializePaymentSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
