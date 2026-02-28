from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import PaymentRecord


@admin.register(PaymentRecord)
class PaymentRecordAdmin(ModelAdmin):
    list_display = ['reference', 'order', 'amount', 'status', 'provider', 'created_at']
    list_filter = ['status', 'provider']
    search_fields = ['reference', 'order__public_id']
    date_hierarchy = 'created_at'
    readonly_fields = ['public_id', 'order', 'reference', 'amount', 'status', 'provider', 'raw_response', 'created_at', 'updated_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
