from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.pagination import StandardPagination
from apps.core.responses import ApiResponse

from . import repositories
from .serializers import ProductCategorySerializer, ProductDetailSerializer, ProductListSerializer


class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = repositories.get_available_products()

        category = request.query_params.get('category')
        season = request.query_params.get('season')
        is_organic = request.query_params.get('is_organic')
        is_featured = request.query_params.get('is_featured')

        if category:
            qs = qs.filter(category__slug=category)
        if season:
            qs = qs.filter(season=season)
        if is_organic is not None:
            qs = qs.filter(is_organic=is_organic.lower() in ('true', '1'))
        if is_featured is not None:
            qs = qs.filter(is_featured=is_featured.lower() in ('true', '1'))

        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ProductListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        product = repositories.get_product_by_slug(slug)
        if not product or not product.is_available:
            return ApiResponse.not_found('Product not found.')
        serializer = ProductDetailSerializer(product, context={'request': request})
        return ApiResponse.success(serializer.data)


class ProductCategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = repositories.get_all_categories()
        serializer = ProductCategorySerializer(categories, many=True, context={'request': request})
        return ApiResponse.success(serializer.data)
