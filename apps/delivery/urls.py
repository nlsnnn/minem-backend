from django.urls import path

from .views import DeliveryCalculateView

app_name = "delivery"

urlpatterns = [
    path("calculate/", DeliveryCalculateView.as_view(), name="calculate"),
]
