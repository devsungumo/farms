from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.pagination import StandardPagination
from apps.core.responses import ApiResponse

from . import repositories
from .serializers import CategorySerializer, PostDetailSerializer, PostListSerializer, TagSerializer


class PostListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        posts = repositories.get_published_posts()
        paginator = StandardPagination()
        page = paginator.paginate_queryset(posts, request)
        serializer = PostListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class PostDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        post = repositories.get_post_by_slug(slug)
        if not post or not post.is_published:
            return ApiResponse.not_found('Post not found.')
        serializer = PostDetailSerializer(post, context={'request': request})
        return ApiResponse.success(serializer.data)


class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = repositories.get_all_categories()
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return ApiResponse.success(serializer.data)


class TagListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tags = repositories.get_all_tags()
        serializer = TagSerializer(tags, many=True, context={'request': request})
        return ApiResponse.success(serializer.data)
