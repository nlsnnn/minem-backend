from django.urls import path, include
from config.admin import admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
    path("api/v1/products/", include("apps.main.urls")),
    path("api/v1/orders/", include("apps.orders.urls")),
    path("api/v1/payments/", include("apps.payment.urls")),
    path("api/v1/contacts/", include("apps.contacts.urls")),
    path("api/v1/delivery/", include("apps.delivery.urls")),
]
