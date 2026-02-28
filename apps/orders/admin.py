from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from . import services
from .models import Order, OrderItem


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_price', 'product_unit', 'quantity', 'line_total']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['public_id', 'user', 'status', 'total', 'delivery_zone', 'created_at']
    list_filter = ['status', 'delivery_zone']
    search_fields = ['user__email', 'paystack_reference', 'public_id']
    date_hierarchy = 'created_at'
    readonly_fields = ['public_id', 'user', 'subtotal', 'delivery_fee', 'total', 'paystack_reference', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    actions = ['action_processing', 'action_dispatched', 'action_delivered', 'action_cancelled']
    fieldsets = (
        (None, {'fields': ('public_id', 'user', 'status')}),
        ('Delivery', {'fields': ('delivery_zone', 'delivery_address', 'delivery_fee')}),
        ('Financials', {'fields': ('subtotal', 'total')}),
        ('Payment', {'fields': ('paystack_reference',)}),
        ('Notes', {'fields': ('notes',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_readonly_fields(self, request, obj=None):
        # status is always read-only on the form; transitions happen via actions
        return self.readonly_fields + ['status']

    @admin.action(description='Mark as Processing')
    def action_processing(self, request, queryset):
        for order in queryset:
            try:
                services.mark_processing(order)
            except ValueError:
                pass

    @admin.action(description='Mark as Dispatched')
    def action_dispatched(self, request, queryset):
        for order in queryset:
            try:
                services.mark_dispatched(order)
            except ValueError:
                pass

    @admin.action(description='Mark as Delivered')
    def action_delivered(self, request, queryset):
        for order in queryset:
            try:
                services.mark_delivered(order)
            except ValueError:
                pass

    @admin.action(description='Cancel selected orders')
    def action_cancelled(self, request, queryset):
        for order in queryset:
            try:
                services.cancel_order(order)
            except ValueError:
                pass
