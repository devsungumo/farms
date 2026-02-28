from django.contrib import admin
from unfold.admin import ModelAdmin

from . import services
from .models import Category, Post, Tag


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'published_at']
    list_filter = ['status', 'category', 'is_featured']
    search_fields = ['title', 'content', 'author__email']
    date_hierarchy = 'published_at'
    filter_horizontal = ['tags']
    readonly_fields = ['published_at', 'created_at', 'updated_at']
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'author', 'status', 'is_featured')}),
        ('Content', {'fields': ('excerpt', 'content', 'cover_image')}),
        ('Categorisation', {'fields': ('category', 'tags')}),
        ('Dates', {'fields': ('published_at', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    actions = ['publish_selected', 'unpublish_selected', 'feature_selected', 'unfeature_selected']

    @admin.action(description='Publish selected posts')
    def publish_selected(self, request, queryset):
        for post in queryset:
            services.publish_post(post.id)

    @admin.action(description='Unpublish selected posts')
    def unpublish_selected(self, request, queryset):
        for post in queryset:
            services.unpublish_post(post.id)

    @admin.action(description='Feature selected posts')
    def feature_selected(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description='Unfeature selected posts')
    def unfeature_selected(self, request, queryset):
        queryset.update(is_featured=False)


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'season', 'post_count']
    search_fields = ['name']

    @admin.display(description='Posts')
    def post_count(self, obj):
        return obj.posts.count()


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ['name', 'post_count']
    search_fields = ['name']

    @admin.display(description='Posts')
    def post_count(self, obj):
        return obj.posts.count()
