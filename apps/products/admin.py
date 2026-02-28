from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from . import services
from .models import Category, Product, ProductImage


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'order']


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['name', 'category', 'price', 'unit', 'season', 'is_organic', 'is_available', 'is_featured', 'get_stock']
    list_filter = ['category', 'season', 'is_organic', 'is_available', 'is_featured']
    search_fields = ['name', 'description']
    inlines = [ProductImageInline]
    actions = ['mark_available', 'mark_unavailable', 'feature_selected', 'unfeature_selected']
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'category', 'description')}),
        ('Pricing & Units', {'fields': ('price', 'unit', 'weight_kg')}),
        ('Attributes', {'fields': ('season', 'is_organic', 'is_available', 'is_featured', 'cover_image')}),
    )

    @admin.display(description='Stock')
    def get_stock(self, obj):
        try:
            return obj.stock_record.quantity
        except Exception:
            return '—'

    @admin.action(description='Mark as available')
    def mark_available(self, request, queryset):
        for product in queryset:
            services.mark_available(product.id)

    @admin.action(description='Mark as unavailable')
    def mark_unavailable(self, request, queryset):
        for product in queryset:
            services.mark_unavailable(product.id)

    @admin.action(description='Feature selected products')
    def feature_selected(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description='Unfeature selected products')
    def unfeature_selected(self, request, queryset):
        queryset.update(is_featured=False)


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'product_count']
    search_fields = ['name']

    @admin.display(description='Products')
    def product_count(self, obj):
        return obj.products.count()
