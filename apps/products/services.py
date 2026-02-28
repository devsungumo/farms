from . import repositories


def mark_available(product_id):
    repositories.set_availability(product_id, True)


def mark_unavailable(product_id):
    repositories.set_availability(product_id, False)


def feature_product(product_id):
    product = repositories.get_product_by_id(product_id)
    if product:
        product.is_featured = True
        repositories.save_product(product)
    return product


def unfeature_product(product_id):
    product = repositories.get_product_by_id(product_id)
    if product:
        product.is_featured = False
        repositories.save_product(product)
    return product
