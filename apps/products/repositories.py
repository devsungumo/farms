from .models import Category, Product


def get_available_products(**filters):
    return (
        Product.objects.filter(is_available=True, **filters)
        .select_related('category')
        .prefetch_related('images')
    )


def get_product_by_slug(slug):
    try:
        return (
            Product.objects.select_related('category')
            .prefetch_related('images')
            .get(slug=slug)
        )
    except Product.DoesNotExist:
        return None


def get_product_by_id(product_id):
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None


def set_availability(product_id, is_available):
    Product.objects.filter(id=product_id).update(is_available=is_available)


def save_product(product):
    product.save()
    return product


def get_all_categories():
    return Category.objects.all()
