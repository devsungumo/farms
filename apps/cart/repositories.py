from .models import Cart, CartItem


def get_or_create_user_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def get_or_create_session_cart(session_key):
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


def get_cart_items(cart):
    return cart.items.select_related('product', 'product__category').all()


def get_cart_item(cart, item_id):
    try:
        return cart.items.get(id=item_id)
    except CartItem.DoesNotExist:
        return None


def add_or_update_item(cart, product, quantity):
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if created:
        item.quantity = quantity
    else:
        item.quantity += quantity
    item.save()
    return item


def update_item_quantity(item, quantity):
    item.quantity = quantity
    item.save(update_fields=['quantity'])
    return item


def delete_item(item):
    item.delete()


def clear_cart(cart):
    cart.items.all().delete()


def get_session_cart(session_key):
    try:
        return Cart.objects.get(session_key=session_key)
    except Cart.DoesNotExist:
        return None
