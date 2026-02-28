from rest_framework import serializers

from .models import Category, Product, ProductImage


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'order']


class ProductListSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    stock_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'unit', 'season',
            'is_organic', 'is_available', 'is_featured',
            'cover_image', 'category', 'stock_quantity',
        ]

    def get_stock_quantity(self, obj):
        try:
            return obj.stock_record.quantity
        except Exception:
            return 0


class ProductDetailSerializer(ProductListSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            'description', 'weight_kg', 'images', 'created_at',
        ]
