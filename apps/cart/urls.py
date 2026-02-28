from django.urls import path

from .views import CartItemDetailView, CartItemView, CartMergeView, CartView

urlpatterns = [
    path('', CartView.as_view(), name='cart-detail'),
    path('items/', CartItemView.as_view(), name='cart-item-add'),
    path('items/<int:item_id>/', CartItemDetailView.as_view(), name='cart-item-detail'),
    path('merge/', CartMergeView.as_view(), name='cart-merge'),
]
