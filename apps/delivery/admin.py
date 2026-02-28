from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import DeliveryZone


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(ModelAdmin):
    list_display = ['name', 'base_fee', 'per_kg_rate', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    actions = ['activate_zones', 'deactivate_zones']

    @admin.action(description='Activate selected zones')
    def activate_zones(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected zones')
    def deactivate_zones(self, request, queryset):
        queryset.update(is_active=False)
