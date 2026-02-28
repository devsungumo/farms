from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.inventory import services
from .models import StockMovement, StockRecord


@admin.register(StockRecord)
class StockRecordAdmin(ModelAdmin):
    list_display = ['product', 'quantity', 'updated_at']
    search_fields = ['product__name']
    readonly_fields = ['product', 'updated_at']
    actions = ['restock_ten']

    def has_add_permission(self, request):
        return False  # auto-created on product save

    @admin.action(description='Add 10 units to selected products')
    def restock_ten(self, request, queryset):
        for record in queryset:
            services.adjust_stock(record.product_id, 10, 'restock', 'Bulk restock via admin')


@admin.register(StockMovement)
class StockMovementAdmin(ModelAdmin):
    list_display = ['product', 'delta', 'reason', 'note', 'created_at']
    list_filter = ['reason']
    search_fields = ['product__name']
    date_hierarchy = 'created_at'
    readonly_fields = ['product', 'delta', 'reason', 'note', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
