from .models import Category, Post, Tag


def get_published_posts(**filters):
    return (
        Post.objects.filter(status=Post.STATUS_PUBLISHED, **filters)
        .select_related('author', 'category')
        .prefetch_related('tags')
        .order_by('-published_at')
    )


def get_post_by_slug(slug):
    try:
        return (
            Post.objects.select_related('author', 'category')
            .prefetch_related('tags')
            .get(slug=slug, status=Post.STATUS_PUBLISHED)
        )
    except Post.DoesNotExist:
        return None


def get_post_by_id(post_id):
    try:
        return Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return None


def save_post(post):
    post.save()
    return post


def get_all_categories():
    return Category.objects.all()


def get_all_tags():
    return Tag.objects.all()
