from apps.products.repositories import get_product_by_id
from .models import CartItem
from . import repositories


def get_cart(request):
    if request.user.is_authenticated:
        return repositories.get_or_create_user_cart(request.user)
    if not request.session.session_key:
        request.session.create()
    return repositories.get_or_create_session_cart(request.session.session_key)


def add_to_cart(request, product_id, quantity):
    product = get_product_by_id(product_id)
    if not product:
        raise ValueError('Product not found.')
    if not product.is_available:
        raise ValueError('Product is not available.')
    cart = get_cart(request)
    return repositories.add_or_update_item(cart, product, quantity)


def update_item(request, item_id, quantity):
    cart = get_cart(request)
    item = repositories.get_cart_item(cart, item_id)
    if not item:
        raise ValueError('Cart item not found.')
    if quantity <= 0:
        repositories.delete_item(item)
        return None
    return repositories.update_item_quantity(item, quantity)


def remove_item(request, item_id):
    cart = get_cart(request)
    item = repositories.get_cart_item(cart, item_id)
    if not item:
        raise ValueError('Cart item not found.')
    repositories.delete_item(item)


def clear_cart(request):
    cart = get_cart(request)
    repositories.clear_cart(cart)


def merge_carts(session_key, user):
    anon_cart = repositories.get_session_cart(session_key)
    if not anon_cart:
        return
    user_cart = repositories.get_or_create_user_cart(user)
    for anon_item in anon_cart.items.select_related('product').all():
        existing = CartItem.objects.filter(cart=user_cart, product=anon_item.product).first()
        if existing:
            existing.quantity += anon_item.quantity
            existing.save(update_fields=['quantity'])
        else:
            CartItem.objects.create(
                cart=user_cart,
                product=anon_item.product,
                quantity=anon_item.quantity,
            )
    anon_cart.delete()


def get_cart_total(cart):
    items = repositories.get_cart_items(cart)
    return sum(item.product.price * item.quantity for item in items)
