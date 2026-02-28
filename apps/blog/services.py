from django.utils import timezone

from .models import Post
from . import repositories


def publish_post(post_id):
    post = repositories.get_post_by_id(post_id)
    if post and post.status != Post.STATUS_PUBLISHED:
        post.status = Post.STATUS_PUBLISHED
        post.published_at = post.published_at or timezone.now()
        repositories.save_post(post)
    return post


def unpublish_post(post_id):
    post = repositories.get_post_by_id(post_id)
    if post:
        post.status = Post.STATUS_DRAFT
        repositories.save_post(post)
    return post
