from django.urls import path

from .views import CategoryListView, PostDetailView, PostListView, TagListView

urlpatterns = [
    path('posts/', PostListView.as_view(), name='blog-post-list'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='blog-post-detail'),
    path('categories/', CategoryListView.as_view(), name='blog-category-list'),
    path('tags/', TagListView.as_view(), name='blog-tag-list'),
]
