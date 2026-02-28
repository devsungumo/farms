from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.responses import ApiResponse

from . import services
from .serializers import InitializePaymentSerializer, PaymentRecordSerializer


class InitializePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InitializePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.error('validation_error', 'Invalid input.', details=serializer.errors)
        try:
            result = services.initialize(serializer.validated_data['order_id'])
        except ValueError as exc:
            return ApiResponse.error('payment_failed', str(exc))
        except Exception:
            return ApiResponse.error('payment_error', 'Could not initialize payment. Try again.', status_code=502)
        return ApiResponse.success(result)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, reference):
        try:
            record = services.verify(reference)
        except ValueError as exc:
            return ApiResponse.error('verify_failed', str(exc))
        except Exception:
            return ApiResponse.error('verify_error', 'Could not verify payment. Try again.', status_code=502)
        return ApiResponse.success(PaymentRecordSerializer(record).data)


class PaystackWebhookView(APIView):
    permission_classes = [AllowAny]
    # Paystack sends raw bytes; CSRF exemption not needed for API views

    def post(self, request):
        signature = request.headers.get('X-Paystack-Signature', '')
        body = request.body
        try:
            ok = services.handle_webhook(body, signature)
        except Exception:
            return ApiResponse.error('webhook_error', 'Webhook processing failed.')
        if not ok:
            return ApiResponse.error('invalid_signature', 'Webhook signature mismatch.', status_code=401)
        return ApiResponse.success({'detail': 'Webhook received.'})
