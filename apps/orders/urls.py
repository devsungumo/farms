from django.urls import path

from .views import OrderCancelView, OrderDetailView, OrderListView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('<uuid:public_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('<uuid:public_id>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
]
