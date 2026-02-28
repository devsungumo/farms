from django.urls import path

from .views import DeliveryFeeEstimateView, DeliveryZoneListView

urlpatterns = [
    path('zones/', DeliveryZoneListView.as_view(), name='delivery-zone-list'),
    path('estimate/', DeliveryFeeEstimateView.as_view(), name='delivery-fee-estimate'),
]
